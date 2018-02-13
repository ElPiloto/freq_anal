from __future__ import division
import time
from pydub import AudioSegment
import numpy as np
import skvideo.io

# TODO(piloto): Check to see if we're on OS X before we import tkagg
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#import matplotlib.pylab as plt
import matplotlib.mlab as mlab
import os

import onset_detection_lib as od

mp3_files = ['./media/pure_sine_single_segment.mp3', './media/Sung-Thunder_Love.mp3', './media/VHS_Dreams-Nightdrive.mp3']

IN_FILE = mp3_files[1]
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

wsize = 4096
# in the paper they use 2048 a.k.a. 46ms
#wsize = 4900
wratio = 0
# in the paper they use 78.5% overlap, a.k.a. hop size of 441 a.k.a. 10ms


# spectrum is freqs by time
spectrum, freqs, times = mlab.specgram(channels[0], NFFT=wsize, Fs=sampling_rate, window=mlab.window_hanning, noverlap=int(wsize * wratio))

onsets = od.spectral_flux(spectrum)

# preprocess spectrum
spectrum = 10 * np.log10(spectrum)
spectrum[spectrum == -np.inf] = 0
spectrum = spectrum ** 2 # get power

# finally normalize
for f in range(spectrum.shape[0]):
  #spectrum = spectrum/np.max(spectrum)
  #spectrum[f,:] /= np.max(spectrum[f,:])
  pass



def animate_spectrum(spectrum, freqs, times, yield_canvas=False, colormap_name='rainbow', onset=None):
  if onset is not None:

    #plt.ioff()
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
      #plt.ion()
      plt.draw()
      if yield_canvas:
        arr = fig_to_array()
        yield arr

  else:
    bars = plt.bar(0,0)
    colormap = getattr(plt.cm, colormap_name)
    color_list = colormap([0])
    for b,c in zip(bars,color_list):
      b.set_color(c)
    max_height = np.max(onset)
    plt.ylim( (0, max_height))
    #plt.ylim( (0, 1))
    #plt.xlim( (0, num_freqs))


    # now iterate throught frames
    for time_idx, time in enumerate(times):
      bars[0].set_height(onset[time_idx])
      #freq_sum = np.sum(spectrum[:, time_idx])
      #if freq_sum > 0.000001:
        #plt.ylim((0, np.max(spectrum[:,time_idx]/freq_sum)))
      #for bar, height in zip(bars, spectrum[:,time_idx]):
        #if freq_sum > 0.000001:
          #bar.set_height(height/freq_sum)
        #else:
          #bar.set_height(0)
      #plt.ion()
      plt.draw()
      if yield_canvas:
        arr = fig_to_array()
        yield arr

def fig_to_array():
  fig=plt.gcf()
  # IF ON OSX, we need to do:
  try:
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
  except Exception, e:
    data = np.fromstring(fig.canvas.get_renderer().tostring_rgb(), dtype=np.uint8, sep='')
  data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
  return data

def spectrum_to_video(spectrum, freqs, times, onset=None):

  #frames_per_second = 60./times[-1]/len(times)
  frames_per_second = 1./(times[2]-times[1])
  #writer = skvideo.io.FFmpegWriter('test_v1.mp4', inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
  writer = skvideo.io.FFmpegWriter(OUT_FILE, inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
  for idx, img in enumerate(animate_spectrum(spectrum, freqs, times, yield_canvas=True, onset=onset)):
    if img is not None:
      writer.writeFrame(img)
  writer.close()

def combine_video_and_audio(video, audio):
  out_video = video.replace(".mp4","_combined.mp4")
  cmd = "ffmpeg -i {} -i {} -codec copy -shortest {}".format(video, audio, out_video)
  print(cmd)
  os.system(cmd)

if True:
  plt.rcParams['axes.facecolor'] = 'black'
  #plt.ion()
  #animate_spectrum(spectrum, freqs, times, onset=onsets)
  spectrum_to_video(spectrum, freqs, times, onset=onsets)
  combine_video_and_audio(OUT_FILE, IN_FILE)
