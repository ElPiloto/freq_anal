from __future__ import division
import time
from pydub import AudioSegment
import numpy as np
import skvideo.io
import matplotlib.mlab as mlab
import matplotlib.pylab as plt
import os

plt.ion()

N = 128             # Must be a power of two
T = 1.               # Set sampling rate to 1
A = 1.               # Sinusoidal amplitude
phi = 0.             # Sinusoidal phase
f = 0.1            # Frequency (cycles/sample)
n = np.array(range(N))        # Discrete time axis
x = A*np.cos(2*np.pi*n*f*T+phi) # Sampled sinusoid

#N = 600
## sample spacing
#T = 1.0 / 800.0
#x = np.linspace(0.0, N*T, N)
#y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
#y = np.sin(50.0 * 2.0*np.pi*x)# + 0.5*np.sin(80.0 * 2.0*np.pi*x)
#X = np.fft.rfft(y)
X = np.fft.rfft(x)
#plt.plot(freqs, X.real, freqs, X.imag)
freqs = np.fft.rfftfreq(x.shape[-1],d=T)
print("signal has length = {}, freqs has len = {}".format(len(x),len(freqs)))
plt.plot(freqs, X.real)
plt.show()

if False:
  import scipy.fftpack

  # Number of samplepoints
  N = 600
  # sample spacing
  T = 1.0 / 800.0
  x = np.linspace(0.0, N*T, N)
  y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
  yf = scipy.fftpack.fft(y)
  xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

  ax = plt.subplot(2,1,1)
  ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
  ax = plt.subplot(2,1,2)
  ax.plot(x, y)
  plt.show()
  plt.figure()

  sampling_rate = T
  wsize=32

  #wsize = 4096
  #wsize = 4900
  #wsize=int(44100/8)
  #wsize=int(48000/8)
  wratio = 0

  # spectrum is freqs by time
  spectrum, freqs, times = mlab.specgram(x, NFFT=wsize, Fs=sampling_rate, window=mlab.window_none, noverlap=int(wsize * wratio), scale_by_freq=True)

  IN_FILE = 'synthetic_sine.mp3'

  OUT_FILE = IN_FILE.replace('.mp3','.mp4')

  # preprocess spectrum
  #spectrum = 10 * np.log10(spectrum)
  #spectrum[spectrum == -np.inf] = 0
  spectrum = spectrum ** 2 # get power

  # finally normalize
  for f in range(spectrum.shape[0]):
    #spectrum = spectrum/np.max(spectrum)
    #spectrum[f,:] /= np.max(spectrum[f,:])
    pass

  SHOULD_NORM = False


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
    if SHOULD_NORM:
      plt.ylim( (0, 1))
    #plt.xlim( (0, 512))
    #plt.xlim( (0, num_freqs))


    # now iterate throught frames
    for time_idx, time in enumerate(times):
      if SHOULD_NORM:
        freq_sum = np.sum(spectrum[:, time_idx])
        if freq_sum > 0.000001:
          plt.ylim((0, np.max(spectrum[:,time_idx]/freq_sum)))

      for bar, height in zip(bars, spectrum[:,time_idx]):
        if SHOULD_NORM:
          if freq_sum > 0.000001:
            bar.set_height(height/freq_sum)
          else:
            bar.set_height(0)
        else:
          bar.set_height(height)
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
    frames_per_second = 1./(times[1]-times[0])
    #writer = skvideo.io.FFmpegWriter('test_v1.mp4', inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
    writer = skvideo.io.FFmpegWriter(OUT_FILE, inputdict={'-framerate': '{0:.5g}'.format(frames_per_second)}, outputdict={'-r': '60'})
    for idx, img in enumerate(animate_spectrum(spectrum, freqs, times, yield_canvas=True)):
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
    plt.ion()
    #animate_spectrum(spectrum, freqs, times)
    spectrum_to_video(spectrum, freqs, times)
    #combine_video_and_audio(OUT_FILE, IN_FILE)
