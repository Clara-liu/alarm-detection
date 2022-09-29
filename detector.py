import time
import logging
import argparse
import pyaudio
import numpy as np
from scipy import fft


alarm_freq = 3000
bandwidth = 50
volume_gate = .5
alert_window = 8


sr = 44100
n_samples = 4096


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
    :type dur: int
    :return: sine wave
    :rtype: numpy array
    """
    x = np.linspace(0, dur, sr * dur, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = np.sin((2 * np.pi) * frequencies)
    return y