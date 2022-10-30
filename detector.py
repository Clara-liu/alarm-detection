import logging
import argparse
import pyaudio
import sys
import numpy as np
from scipy import fft
from os import path
from time import sleep
from utils import telegram_bot


def _fft(signal, sr):
    yf = fft.fft(signal)
    n = len(signal) 
    yf = 2/n * np.abs(yf[0:n//2])
    xf = fft.fftfreq(n, 1/sr)[0:n//2]
    result = dict(
        loudest_freq = xf[np.argmax(yf)],
        loudest_intensity = yf.max(),
        intensity = yf,
        freq = xf
    )
    return result


def _generate_sine(freq, sr, dur):
    """generate sine wave for testing

    :param freq: frequency in Hz of sine wave
    :type freq: int or float
    :param sr: sample per second
    :type sr: int
    :param dur: duration in seconds
    :type dur: float
    :return: sine wave
    :rtype: numpy array
    """
    # 2pi because np.sin takes radians
    y = (np.sin(2 * np.pi * np.arange(sr * dur) * freq / sr))
    return y


class Detector:
    def __init__(self, alarm_freq, bw, vol_gate, alert_win, sr, n_samples, verbose=True):
        self.sr = sr
        self.n = n_samples
        self.alert_tolerance = alert_win
        self.bw = bw
        self.alarm_freq = alarm_freq
        self.gate = vol_gate
        self.alarm_record = []
        self.beeped = False
        self.verbose = verbose

    def reset(self):
        self.alarm_record = []
    
    def detect(self, sig):
        fft_result = _fft(sig, self.sr)
        within_bw = (fft_result['loudest_freq'] < (self.alarm_freq + self.bw)) and (fft_result['loudest_freq'] > (self.alarm_freq - self.bw))
        above_gate = fft_result['loudest_intensity'] > self.gate
        if within_bw and above_gate:
            self.alarm_record.append('Beep')
            self.beeped = True
        else:
            self.beeped = False
        if self.verbose:
            logging.info(f'Loudness {fft_result["loudest_intensity"]} at {fft_result["loudest_freq"]} Hz.')
    
    def alarm(self):
        if self.beeped and len(self.alarm_record) >= self.alert_tolerance:
            logging.info('Alarm detected!')
            self.reset()
            logging.info('Alarm has been reset after positive alarm.')
            return True
        elif self.beeped and len(self.alarm_record) < self.alert_tolerance:
            logging.info(f'Alarm going off after {self.alert_tolerance - len(self.alarm_record)} more beeps!')
            return False
        else:
            self.reset()
            logging.info('Alarm has been reset after no beep.')
            return False


def _args():
    parser = argparse.ArgumentParser(
        description = 'Audio alarm detection'
    )

    parser.add_argument(
        '--alarm-freq',
        type=int,
        help='Frequency of the alarm to detect',
        required=True
    )

    parser.add_argument(
        '--band-width',
        type=int,
        help='Error margin is equal to the alarm freq plus and minus band width',
        default=50
    )

    parser.add_argument(
        '--volume-gate',
        type=float,
        help='Alarm is detected when the loudest frequency is louder than this threshold.',
        default=.1
    )

    parser.add_argument(
        '--alert-win',
        type=int,
        help='How many beeps before alerting.',
        default=5
    )

    parser.add_argument(
        '--mic-id',
        type=int,
        help='The device ID of the USB microphone.',
        required=True
    )

    parser.add_argument(
        '--test-mode',
        help='whether to use testing mode.',
        action='store_true'
    )

    parser.add_argument(
        '--verbose',
        help='Whether to log each detection.',
        action='store_true'
    )

    parser.add_argument(
        '--telegram-file',
        type=str,
        required=True,
        help='Path to file containing info on telegram bot.'
    )

    args = parser.parse_args()
    return args



if __name__ == '__main__':
    listen_dur = 0.1

    sr = 44100
    n_samples = 4096
    args = _args()
    if not path.exists(args.telegram_file):
        sys.exit('Cannot find yaml file for telegram.')

    logging.basicConfig(level=logging.INFO)

    detector = Detector(args.alarm_freq, args.band_width, args.volume_gate, args.alert_win, sr, n_samples, verbose=args.verbose)

    if not args.test_mode:
        p = pyaudio.PyAudio()
        _stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sr,
            input=True,
            frames_per_buffer=n_samples,
            input_device_index=args.mic_id
        )
    else:
        logging.info('Entering testing mode')
    while True:
        if not args.test_mode:
            _stream.start_stream()
            raw_sig = []
            for i in range(0, int((sr/n_samples)*listen_dur)):
                data = np.frombuffer(_stream.read(n_samples, exception_on_overflow=False), dtype=np.float32)
                raw_sig =+ data
            detector.detect(raw_sig)
            _stream.stop_stream()
        ####### testing block ########
        else:
            trigger_beep = np.random.choice(2, 1, p=[0.3, 0.7]).item()
            if trigger_beep:
                freq = args.alarm_freq
            else:
                freq = 2000
            logging.info(f'trigger: {trigger_beep}')
            sig =_generate_sine(freq, sr, listen_dur)
            detector.detect(sig)
        text_alarm = detector.alarm()
        if text_alarm:
            logging.info('Text for positive alarm detection!')
            telegram_bot.text_telegram(args.telegram_file)
            sleep(300)
            ########################## text ##########################
        sleep(0.9)
