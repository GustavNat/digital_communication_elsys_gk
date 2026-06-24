import subprocess
from fsk_decoder import fsk_decoder

F0 = 1500           # Hz – frequency for bit 0
F1 = 1820           # Hz – frequency for bit 1
BIT_TIME = 0.05     # s  – duration of one bit

START_SIGNAL = [1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1]
STOP_SIGNAL  = [1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1]
BITS_PER_SYMBOL   = 5    # number of bits per symbol

NUM_SAMPLES  = 31250    # 31250 = 1 second
OUTPUT_FILE  = 'recording.bin'

# Record
subprocess.run(['sudo', './adc_sampler', str(NUM_SAMPLES), OUTPUT_FILE], check=True)

# Decode
bits = fsk_decoder(OUTPUT_FILE, F0, F1, BIT_TIME, BITS_PER_SYMBOL,
                   start_signal=START_SIGNAL,
                   stop_signal=STOP_SIGNAL,
                   )

print(bits)
