from enum import Enum
import struct

LITTLE_ENDIAN_INT = struct.Struct('<I')
LITTLE_ENDIAN_SIGNED_SHORT = struct.Struct('<h')
CHUNK_SIZE_OFFSET = 4
DATA_SUB_CHUNK_SIZE_SIZE_OFFSET = 40
WAV_SAMPLE_MIN = -32768
WAV_SAMPLE_MAX = 32767
class WaveWriter(object):
  '''
  WaveWriter writes a single channel 16-bit wave file into the parameter fout with a sample rate set by sample_rate
  '''
  def __init__(self, fout, sample_rate):
    self.sample_count = 0
    self.sample_rate = sample_rate
    self.fout = fout
    self._write_header()

  def _write_header(self):
    self.fout.write(b'RIFF')
    self.fout.write(b'\xFF\xFF\xFF\xFF') # Place holder for chunk size
    self.fout.write(b'WAVE')
    self.fout.write(b'fmt ')
    self.fout.write(b'\x10\x00\x00\x00') # Sub chunk size, little endian 16
    self.fout.write(b'\x01\x00') # audio format, always little endian 1
    self.fout.write(b'\x01\x00') # number of channels, always 1
    self.fout.write(LITTLE_ENDIAN_INT.pack(self.sample_rate)) # sample rate
    self.fout.write(LITTLE_ENDIAN_INT.pack(self.sample_rate * 2)) # bytes per sample
    self.fout.write(b'\x02\x00') # block alignment
    self.fout.write(b'\x10\x00') # bits per sample
    self.fout.write(b'data')
    self.fout.write(b'\xFF\xFF\xFF\xFF') # place holder for sub chunk size

  def write_samples(self, samples):
    '''
    Writes an iterable of integers in the range  [-32768, 32767] out as audio samples
    '''
    self.sample_count += len(samples)
    for v in samples:
      self.fout.write(LITTLE_ENDIAN_SIGNED_SHORT.pack(v))

  def write_sample(self, sample):
    '''
    Write a single integer as an audio sample
    '''
    self.write_samples((sample,))

  def _pad_output_to_even(self):
    if self.fout.tell() % 2 == 0:
      return
    self.fout.write(b'\x00')

  def finish(self, metadata = None):
    '''
    Finishes writing the file, but does not close the file.
    Optional metadata may be passed in as an iterable of tuples. The first item in each tuple
    should be an enumeration from WavMetadataIdentifier. The second item should be a string.
    '''
    if metadata is not None:
      list_chunk_start = self.fout.tell()
      self.fout.write(b'LIST')
      list_chunk_size_offset = self.fout.tell()
      self.fout.write(b'\xFF\xFF\xFF\xFF')  # Place holder for chunk size
      self.fout.write(b'INFO')

      for identifier_enum, value in metadata:
        self.fout.write(identifier_enum.value)
        self.fout.write(LITTLE_ENDIAN_INT.pack(len(value) + 1))
        self.fout.write(value.encode())
        self.fout.write(b'\x00')
        self._pad_output_to_even()

      end_of_list = self.fout.tell()
      self._pad_output_to_even()
      self.fout.seek(list_chunk_start + 4)
      self.fout.write(LITTLE_ENDIAN_INT.pack(end_of_list - list_chunk_start - 8))

    v = self.fout.tell() - 8
    self.fout.seek(CHUNK_SIZE_OFFSET)
    self.fout.write(LITTLE_ENDIAN_INT.pack(v))

    self.fout.seek(DATA_SUB_CHUNK_SIZE_SIZE_OFFSET)
    v = 2 * self.sample_count
    self.fout.write(LITTLE_ENDIAN_INT.pack(v))

class WavMetadataIdentifier(Enum):
  TRACK_TITLE = b'INAM'
  ALBUM_TITLE = b'IPRD'
  ARTIST = b'IART'
  CREATION_DATE = b'ICRD'
  TRACK_NUMBER = b'ITRK'
  COMMENT = b'ICMT'
  KEYWORDS = b'IKEY'
  CREATING_SOFTWARE = b'ISFT'
  ENGINEER = b'IENG'
  TECHNICIAN = b'ITCH'
  GENRE = b'IGNR'
  COPYRIGHT = b'ICOP'
  SUBJECT = b'ISBJ'
  CREATOR_NAME = b'ISRC'