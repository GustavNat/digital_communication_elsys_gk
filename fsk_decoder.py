import sys
import numpy as np
from scipy.signal import butter, filtfilt
from raspi_import import raspi_import


def bandpass(signal, sample_rate, f0, f1):
    # Removes frequencies around f0 and f1
    # Uses a Butterworth bandpass filter
    f_low, f_high = min(f0, f1), max(f0, f1)
    margin = (f_high - f_low) / 2
    nyq = sample_rate / 2
    b, a = butter(4, [(f_low - margin) / nyq, (f_high + margin) / nyq], btype='band')
    return filtfilt(b, a, signal)


def find_start_sample(signal, sample_rate, f0, f1, bit_time, start_signal):
    # Searches the recording for start_signal to find where the message begins
    # It does this in two stages: a fast coarse scan first, then a slow fine scan around the best candidates
    # Returns the sample index right after the start_signal ends
    n = int(round(bit_time * sample_rate))
    t = np.arange(n) / sample_rate
    ref0 = np.hanning(n) * np.exp(-2j * np.pi * f0 * t)
    ref1 = np.hanning(n) * np.exp(-2j * np.pi * f1 * t)
    expected = (np.array(start_signal) * 2 - 1).astype(float)
    bit_offsets = np.arange(len(start_signal)) * n

    def ratio(starts):
        c = signal[starts[:, None] + np.arange(n)[None, :]]
        c = c - c.mean(axis=1, keepdims=True)
        e0 = np.abs(c @ ref0) ** 2
        e1 = np.abs(c @ ref1) ** 2
        return (e1 / (e0 + e1 + 1e-10)) * 2 - 1

    # Stage 1: coarse scan
    coarse_step = max(1, n // 2)
    coarse_starts = np.arange(0, len(signal) - n + 1, coarse_step)
    coarse_expected = np.repeat(expected, n // coarse_step)
    coarse_corr = np.correlate(ratio(coarse_starts), coarse_expected, mode='valid')
    top3 = np.argsort(coarse_corr)[-3:][::-1]

    # Stage 2: fine scan
    fine_step = max(1, n // 124)
    fine_offsets = np.arange(-n // 2, n // 2 + 1, fine_step)
    best_score, best_sample = -np.inf, 0

    for coarse_peak in top3:
        coarse_sample = int(coarse_peak) * coarse_step
        all_starts = np.clip(
            (coarse_sample + fine_offsets[:, None] + bit_offsets[None, :]).flatten(),
            0, len(signal) - n
        )
        scores = ratio(all_starts).reshape(len(fine_offsets), len(start_signal)) @ expected
        idx = int(np.argmax(scores))
        if scores[idx] > best_score:
            best_score = scores[idx]
            best_sample = coarse_sample + fine_offsets[idx]

    return int(best_sample) + len(start_signal) * n


def decode_bits(signal, sample_rate, f0, f1, bit_time):
    # Splits the signal into fixed-length chunks, one chunk per bit period.
    # For each chunk it measures how much energy is at f0 vs f1 — whichever is stronger decides if the bit is 0 or 1.
    # Returns a list of integers (0s and 1s) representing the decoded bits.
    n = int(round(bit_time * sample_rate))
    t = np.arange(n) / sample_rate
    window = np.hanning(n)
    ref0 = window * np.exp(-2j * np.pi * f0 * t)
    ref1 = window * np.exp(-2j * np.pi * f1 * t)

    total = (len(signal) // n) * n
    chunks = signal[:total].reshape(-1, n)
    chunks = chunks - chunks.mean(axis=1, keepdims=True)

    e0 = np.abs(chunks @ ref0) ** 2
    e1 = np.abs(chunks @ ref1) ** 2
    return (e1 > e0).astype(int).tolist()


def find_stop(bits, stop_signal, bits_per_symbol):
    # Scans through the decoded bits looking for the known stop sequence.
    # Only checks at symbol-aligned positions
    # Returns the index where the stop sequence starts, or the total length if it is never found.
    n = len(stop_signal)
    for i in range(0, len(bits) - n + 1, bits_per_symbol):
        errors = sum(a != b for a, b in zip(bits[i:i+n], stop_signal))
        if errors < 1:
            return i
    return len(bits)


def fsk_decoder(path, f0, f1, bit_time, bits_per_symbol,
                start_signal=None, stop_signal=None, channels=1, channel=0):
    """
    Decode an FSK recording and return a list of bits.

    path:         Path to the .dat file recorded by adc_sampler.
    f0:           Frequency (Hz) used for bit 0 by the transmitter.
    f1:           Frequency (Hz) used for bit 1 by the transmitter.
    bit_time:     How long one bit lasts in seconds.
    bits_per_symbol: Number of bits per symbol.
    start_signal: Known bit sequence marking the start of the message.
                  If not given, decoding starts from the beginning of the file.
    stop_signal:  Known bit sequence marking the end of the message.
                  If not given, decoding continues to the end of the file.
    channel:      Which ADC channel to decode (default 0).
    """
    sample_period, data = raspi_import(path, channels=channels)
    sample_rate = 1.0 / sample_period
    signal = data[:, channel]

    signal = bandpass(signal - np.mean(signal), sample_rate, f0, f1)

    if start_signal is not None:
        payload_sample = find_start_sample(signal, sample_rate, f0, f1, bit_time, start_signal)
        bits = decode_bits(signal[payload_sample:], sample_rate, f0, f1, bit_time)
    else:
        bits = decode_bits(signal, sample_rate, f0, f1, bit_time)

    if stop_signal is not None:
        stop_idx = find_stop(bits, stop_signal, bits_per_symbol)
        bits = bits[:stop_idx]

    return bits