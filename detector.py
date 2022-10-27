import time
import logging
import argparse
import pyaudio
import numpy as np
from scipy import fft
from time import sleep


def _fft(signal, sr, normalise=True):
    # scale to between 0 and 1 if signal is 16 bit numbers
    norm_sig = (signal/32768.0) if normalise else signal
    yf = fft.rfft(norm_sig)
    xf = fft.rfftfreq(len(norm_sig), 1/sr)
    result = dict(
        loudest_freq = xf[np.argmax(np.abs(yf))],
        loudest_intensity = np.abs(yf).max(),
        intensity = yf,
        freq = xf
    )
    return result


def _generate_sine(freq, sr, dur):
    """generate sine wave for testing

    :param freq: frequency in Hz of sine wave
    :type freq: int or float
    :param sr: sampling rate
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
    def __init__(self, alarm_freq, bw, vol_gate, alert_win, sr, n_samples):
        self.sr = sr
        self.n = n_samples
        self.alert_tolerance = alert_win
        self.bw = bw
        self.alarm_freq = alarm_freq
        self.gate = vol_gate
        self.alarm_record = []
        self.beeped = False

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


if __name__ == '__main__':
    alarm_freq = 3000
    bandwidth = 80
    volume_gate = .1
    alert_window = 5
    listen_dur = 0.1

    device_id = 1

    sr = 44100
    n_samples = 4096
    test = False

    logging.basicConfig(level=logging.INFO)
    detector = Detector(alarm_freq, bandwidth, volume_gate, alert_window, sr, n_samples)
    if not test:
        p = pyaudio.PyAudio()
        _stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sr,
            input=True,
            frames_per_buffer=n_samples,
            input_device_index=device_id
        )
    else:
        logging.info('Entering testing mode')
    while True:
        if not test:
            _stream.start_stream()
            raw_sig = []
            for i in range(0, int((sr/n_samples)*listen_dur)):
                data = np.frombuffer(_stream.read(n_samples, exception_on_overflow=False), dtype=np.float32)
                raw_sig =+ data
            detector.detect(raw_sig)
            _stream.stop_stream()
        ####### testing ########
        else:
            trigger_beep = np.random.choice(2, 1, p=[0.3, 0.7]).item()
            if trigger_beep:
                freq = alarm_freq
            else:
                freq = 2000
            logging.info(f'trigger: {trigger_beep}')
            sig =_generate_sine(freq, sr, n_samples/sr)*5
            detector.detect(sig)
        text_alarm = detector.alarm()
        if text_alarm:
            logging.info('Text for positive alarm detection!')
            ########################## text ##########################
        sleep(0.99)
