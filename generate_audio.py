from pydub.generators import Sine, Square, Pulse, WhiteNoise, SignalGenerator
from pydub import AudioSegment
import pdb

silence = lambda duration: AudioSegment.silent(duration=duration)

FREQS = [125, 250, 500, 1000, 2000]
DURATIONS = [500, 500, 1000., 1000., 1000.]
#FREQS = [500]
#DURATIONS = [5000.]
#WAVE_TYPES = [WhiteNoise, Sine, Square]
WAVE_TYPES = [Sine, silence, Sine, silence, Sine, silence]

# OSCILLATION
NUM_CYCLES = 10
FREQS = [250, 0] * NUM_CYCLES
DURATIONS = [500, 500] * NUM_CYCLES
WAVE_TYPES = [Sine, silence] * NUM_CYCLES

# SINGLE SINE - MULTI SEG
NUM_CYCLES = 3
FREQS = [250] * NUM_CYCLES
DURATIONS = [500] * NUM_CYCLES
WAVE_TYPES = [Sine] * NUM_CYCLES

# SINGLE SINE - SINGLE SEG
NUM_CYCLES = 1
FREQS = [3000]
DURATIONS = [4000]
WAVE_TYPES = [Sine]
OUT_NAME = "pure_sine_single_segment.mp3"

def islambda(v):
  LAMBDA = lambda:0
  return isinstance(v, type(LAMBDA))

def make_audio_segment(wave_form, duration, freq):
  if islambda(wave_form):
    return  wave_form(duration)
  #if issubclass(wave_form, SignalGenerator):
  else:
    return  wave_form(freq).to_audio_segment(duration)

complete_signal = None
for f, d, w in zip(FREQS, DURATIONS, WAVE_TYPES):
  #tmp_signal = w(f).to_audio_segment(d)
  tmp_signal = make_audio_segment(w,d,f)
  if complete_signal is None:
    complete_signal = tmp_signal
  else:
    complete_signal = complete_signal.append(tmp_signal,crossfade=0)

complete_signal.export("./mp3s/{}".format(OUT_NAME), format="mp3", bitrate="192k")

