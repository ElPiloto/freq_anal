
from pydub import AudioSegment
import os
import sys

# python example.py one two three
#>>> print(sys.argv)
#['example.py', 'one', 'two', 'three']

args = sys.argv[1:] # get rid of script name


FFMPEG_TEMPLATE = "ffmpeg -ss {start_time} -t {duration} -i {in_file} {out_file}"

mp3_files = ["./mp3s/Sung-Thunder_Love.mp3", "./mp3s/VHS_Dreams-Nightdrive.mp3"]


def make_out_filename(in_file, start_time, end_time, idx=-1):
  if idx < 0:
    idx = ""
  else:
    idx = "{}_".format(idx)
  time_description = "_start_{}_end_{}".format(start_time, end_time)

  path, filename = os.path.split(in_file)
  #path = os.path.abspath(in_file)
  new_filename = idx + filename.replace(".mp3","") + time_description + ".mp3"
  out_file = os.path.join(path, new_filename)
  return out_file

START = 0
DURATION = 5
OFFSET = 30
NUM_CLIPS = 4

for f in mp3_files:
  current_time = START
  for clip_idx in range(NUM_CLIPS):
    end_time = current_time + DURATION

    in_file = f
    out_file = make_out_filename(in_file, current_time, end_time, idx=clip_idx)
    cmd = FFMPEG_TEMPLATE.format(start_time=current_time, duration=DURATION, in_file=in_file, out_file=out_file)
    print(cmd)
    os.system(cmd)
    current_time += OFFSET

  
