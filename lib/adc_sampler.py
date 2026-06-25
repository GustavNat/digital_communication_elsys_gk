import subprocess

SAMPLE_RATE = 31250  # Hz, set by REPEAT_MICROS in adc_sampler.c


def record(duration, output_file):
    num_samples = int(duration * SAMPLE_RATE)
    subprocess.run(['sudo', './c/adc_sampler', str(num_samples), output_file], check=True)
