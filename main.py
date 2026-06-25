from lib.adc_sampler import record
from lib.fsk_decoder import fsk_decoder

F0 = 1200           # Hz – frequency for bit 0
F1 = 2200           # Hz – frequency for bit 1
BIT_TIME = 0.5     # s  – duration of one bit

START_SIGNAL = [1, 1, 1, 0, 1]

DURATION    = 10      # seconds
OUTPUT_FILE = 'recording.bin'

# Record
record(DURATION, OUTPUT_FILE)

# Decode
bits = fsk_decoder(OUTPUT_FILE, F0, F1, BIT_TIME, start_signal=START_SIGNAL)


print(bits)
