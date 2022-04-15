from simplewave import *
import math
import sys

sample_rate = int(sys.argv[1])
sweep_start_hz = int(sys.argv[2])
sweep_end_hz = int(sys.argv[3])
duration_seconds = float(sys.argv[4])
output_file = sys.argv[5]

number_of_samples = math.ceil(duration_seconds * sample_rate)
delta_hz = sweep_end_hz - sweep_start_hz

metadata = (
  (WavMetadataIdentifier.CREATING_SOFTWARE, 'simplewave'),
  (WavMetadataIdentifier.COMMENT, "sweep from %d Hz to %d Hz" % (sweep_start_hz, sweep_end_hz,)),
)

with open(output_file, 'wb') as fout:
  wav_writer = WaveWriter(fout, sample_rate)
  for i in range(number_of_samples):
    i_hz = delta_hz * (i/number_of_samples)
    v = math.sin(2 * math.pi * i * (sweep_start_hz + i_hz) / sample_rate) * 0.99
    v *= (2**15 - 1)
    v = int(v)
    wav_writer.write_sample(v)
  wav_writer.finish(metadata)