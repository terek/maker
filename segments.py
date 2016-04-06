import math

from commands import *

class Segments:
  fps = None

  # pairs of frame ids
  segments = []
  start_times = [0.]

  frames = []

  def __init__(self, fps):
    self.fps = fps
    assert 0 < self.fps <= 30

  def NearestSegmentIdx(self, start):
    start_idx = 0
    while (start_idx < len(self.start_times) - 1 and
           self.start_times[start_idx] < start - 0.1): # rounding error
      start_idx += 1
    return start_idx

  def CurrTime(self):
    return self.start_times[-1]

  # Generates points uniformly sampled for the next `duration' seconds. Returns
  # relative positions [0, 1].
  def GenerateSamples(self, duration):
    start_time = self.CurrTime()
    end_time = start_time + duration
    begin_sec = int(math.floor(start_time))
    end_sec = int(math.ceil(end_time))
    wide_samples = [(begin_sec + float(x) / self.fps)
                    for x in range(int((end_sec - begin_sec) * self.fps))]
    ticks = [t for t in wide_samples if start_time <= t < end_time]
    current_time = end_time
    return [(t - start_time) / duration for t in ticks]

  def Add(self, t, images):
    assert len(self.start_times) == len(self.segments) + 1

    start_frame = len(self.frames)
    end_frame = len(self.frames) + len(images)
    self.frames += images

    # Add a new video segment.
    self.segments.append((start_frame, end_frame))

    # Advance
    self.start_times.append(self.start_times[-1] + t)

    # Make sure there is no missing frame due to accumulated rounding errors.
    assert len(self.frames) + 1 > self.fps * self.start_times[-1]

  def ApplyFull(self, transformer):
    self.ApplyFrameRange(0, len(self.frames), transformer)

  def ApplyFrameRange(self, start_frame, end_frame, transformer):
    transformed = transformer(self.frames[start_frame : end_frame])
    assert len(transformed) == end_frame - start_frame
    self.frames[start_frame : end_frame] = transformed


  def Render(self, start, duration):
    assert len(self.start_times) == len(self.segments) + 1
    start_idx = self.NearestSegmentIdx(start)
    end_idx = self.NearestSegmentIdx(start + duration)
    exact_start = self.start_times[start_idx]
    exact_duration = self.start_times[end_idx] - exact_start
    segment_list = [
        self.frames[start_frame : end_frame]
        for (start_frame, end_frame) in self.segments[start_idx : end_idx]]
    return (exact_start, exact_duration, segment_list)
