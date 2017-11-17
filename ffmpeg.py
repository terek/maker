import generator

FFMPEG="ffmpeg"

def VideoToImages(video, fps, start, duration):
  assert fps > 0
  num_frames = int(round(fps * duration))
  command = (
      '%s -i %s -r %.2f -ss %.2f -t %.2f -f image2 OUTPUT-%%05d.png') % (
          FFMPEG, video, fps, start, duration)
  basename = generator.CreateBaseName(command)
  filenames = ['%s-%05d.png' % (basename, x) for x in range(1, num_frames + 1)]
  target = generator.RegisterCommand(
      filenames,
      [video],
      command,
      command)
  for f in filenames[1:]:
    generator.FILENAME_TARGET_MAP[f] = target
  return filenames

def VideoFromImages(fps, filenames):
  links = generator.GenerateLinks(filenames)
  assert len(links) > 0
  command = (
      '%s -f image2 -r %.2f -i %s -r %.2f -c:v libx264 -pix_fmt yuv420p ' +
      '-f mp4 OUTPUT.mp4') % (
          FFMPEG, fps, generator.GroupBaseName(links[0]) + '-%05d.png', fps)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.mp4',
      links,
      command,
      command)

def VideoCutSegment(video, start, duration):
  command = (
      '%s -i %s  -ss %s -t %s -an -c:v libx264 OUTPUT.mp4') % (
          FFMPEG, video, start, duration)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.mp4',
      [video],
      command,
      'Cutting video segment (%s, %s) %s' % (start, duration, video))

def MergeVideos(absolute_path, videos):
  command = (
      '%s -f concat -i <(echo "%s") -strict -2 OUTPUT.mp4' % (
          FFMPEG, ''.join(["file '%s/%s'\n" % (absolute_path, x) for x in videos])))
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.mp4',
      videos,
      command,
      'Merging %d videos' % len(videos))

def MergeVideoAndAudio(video, audio):
  command = (
      '%s -i %s  -i %s -map 0:v:0 -map 1:a:0 -shortest -c:v copy ' +
      '-c:a aac -strict experimental OUTPUT.mp4') % (
          FFMPEG, video, audio)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.mp4',
      [video, audio],
      command,
      'Merging video & audio (%s + %s)' % (video, audio))
