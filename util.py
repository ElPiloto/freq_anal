from __future__ import division
import numpy as np

def aggregate_rows_regular(data, num_rows_collapse=2, aggregate_fn=np.mean, uneven_rows_method='graceful'):
  # could be either graceful or error
  num_rows, num_cols = data.shape
  num_output_rows = int(np.ceil(num_rows/num_rows_collapse))
  if int(num_output_rows) != num_output_rows:
    if uneven_rows_method != 'graceful':
      raise ValueError('data has {} rows and want to collapse every {} rows, but this does not divide evenly.'.format(num_rows, num_rows_collapse))

  output = np.full(shape=(num_output_rows, num_cols), dtype=data.dtype, fill_value=np.nan)
  aggregated_row_idx = 0
  for i in range(num_output_rows):
    start_row = i * num_rows_collapse
    end_row = (i+1) * num_rows_collapse
    if end_row > num_rows:
      end_row = num_rows
    output[aggregated_row_idx,:] = aggregate_fn(data[start_row:end_row,:],axis=0, keepdims=True)
    aggregated_row_idx += 1
  return output

