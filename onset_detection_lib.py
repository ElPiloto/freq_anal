from __future__ import division

import numpy as np
import pdb

# only keeps positive parts
def halfwave_rectifier(x):
  return (np.abs(x) + x)/2

def spectral_flux(freqs_by_time):
  num_freqs = freqs_by_time.shape[0]
  num_times = freqs_by_time.shape[1]
  print(num_freqs, num_times)
  diff = halfwave_rectifier(np.diff(np.abs(freqs_by_time), axis=0))
  sum_diff_per_timept = np.sum(diff, axis=0) # sum over frequencies
  return np.pad(sum_diff_per_timept, ((1,0)), mode='constant') # add an extra 0 in the beginning so we have the original length

def phase_deviation(phases_by_time):
  # tmp is the second derivative
  tmp = np.diff(np.diff(phases_by_time, axis=0), axis=0)
  pd = np.mean(tmp, axis=0, keepdims=True)
  pd = np.pad(pd, ((0,2)), mode='constant') # add an extra 0 in the beginning so we have the original length
  print("phase deviation output has shape = {}".format(pd.shape))
  return pd
  


