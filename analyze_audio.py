from __future__ import division
import time
from pydub import AudioSegment
import numpy as np
import skvideo.io
import matplotlib.mlab as mlab
import matplotlib.pylab as plt
import os

mp3_files = ['./mp3s/pure_sine_single_segment.mp3', './mp3s/Sung-Thunder_Love.mp3', './mp3s/VHS_Dreams-Nightdrive.mp3']

IN_FILE = mp3_files[0]
OUT_FILE = IN_FILE.replace('.mp3','.mp4')

song = AudioSegment.from_mp3(IN_FILE)
sampling_rate = song.frame_rate # 44100 or 48000
bytes_per_sample = song.sample_width
# frame contains a sample for each channel
bytes_per_frame = song.frame_width

total_bytes = song.duration_seconds * sampling_rate
total_bytes *= song.channels # num_channel samples / frame
total_bytes *= song.sample_width
print(total_bytes)

# TODO(piloto): Figure out if np.int16 is because the sample_width(bytes_per_sample) = 2 and whether or not we should have a mapping here in case that value is different
# assert bytes_per_sample == 2
data = np.fromstring(song._data, np.int16)

channels = []
for c in xrange(song.channels):
  channels.append(data[::song.channels])
 
# FFT the signal and extract frequency components

#wsize = 4096
wsize = 4900
wratio = 0

# spectrum is freqs by time
spectrum, freqs, times = mlab.specgram(channels[0], NFFT=wsize, Fs=sampling_rate, window=mlab.window_hanning, noverlap=int(wsize * wratio))

# preprocess spectrum
spectrum = 10 * np.log10(spectrum)
spectrum[spectrum == -np.inf] = 0
spectrum = spectrum ** 2 # get power

# finally normalize
for f in range(spectrum.shape[0]):
  #spectrum = spectrum/np.max(spectrum)
  #spectrum[f,:] /= np.max(spectrum[f,:])
  pass



def animate_spectrum(spectrum, freqs, times, yield_canvas=False, colormap_name='rainbow'):
  num_freqs = len(freqs)
  num_bars = num_freqs # TODO(piloto): Implement binning
  bars = plt.bar(range(num_bars), range(num_bars))
  colormap = getattr(plt.cm, colormap_name)
  color_list = colormap(np.linspace(0,1,len(freqs)))
  for b,c in zip(bars,color_list):
    b.set_color(c)
  max_height = np.max(spectrum)
  plt.ylim( (0, max_height))
  plt.ylim( (0, 1))
  plt.xlim( (0, num_freqs))


  # now iterate throught frames
  for time_idx, time in enumerate(times):
    freq_sum = np.sum(spectrum[:, time_idx])
    if freq_sum > 0.000001:
      plt.ylim((0, np.max(spectrum[:,time_idx]/freq_sum)))
    for bar, height in zip(bars, spectrum[:,time_idx]):
      if freq_sum > 0.000001:
        bar.set_height(height/freq_sum)
      else:
        bar.set_height(0)
    plt.draw()
    if yield_canvas:
      arr = fig_to_array()
      yield arr

def fig_to_array():
  fig=plt.gcf()
  data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
  data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
  return data

def spectrum_to_video(spectrum, freqs, times):

  #frames_per_second = 60./times[-1]/len(times)
  frames_per_second = 1./(times[2]-times[1])
  #writer = skvideo.io.FFmpegWriter('test_v1.mp4', inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
  writer = skvideo.io.FFmpegWriter(OUT_FILE, inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
  for idx, img in enumerate(animate_spectrum(spectrum, freqs, times, yield_canvas=True)):
    if img is not None:
      writer.writeFrame(img)
  writer.close()

def combine_video_and_audio(video, audio):
  video = video.replace(".mp4","_combined.mp4")
  cmd = "ffmpeg -i {} -i {} -codec copy -shortest {}".format(video, audio, video)
  print(cmd)
  os.system(cmd)

if True:
  plt.rcParams['axes.facecolor'] = 'black'
  plt.ion()
  #animate_spectrum(spectrum, freqs, times)
  spectrum_to_video(spectrum, freqs, times)
  combine_video_and_audio(OUT_FILE, IN_FILE)
