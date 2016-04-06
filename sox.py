import generator

def Trim(audio, start, duration):
  command = 'sox %s OUTPUT.wav trim %.2f =%.2f' % (
      audio, start, start + duration)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      [audio],
      command,
      'Trimming audio %s (%.2f, %.2f)' % (audio, start, duration))

def MonoToStereo(audio_left, audio_right):
  command = 'sox -M %s %s OUTPUT.wav' % (audio_left, audio_right)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      [audio_left, audio_right],
      command,
      'Mergin mono files to stereo %s & %s' % (audio_left, audio_right))

def MonoToLeftRight(mono, left, right):
  command = 'sox %s OUTPUT.wav remix 1v%.2f 1v%.2f' % (mono, left, right)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      [mono],
      command,
      'Stereo file from mono with shift %s (%.2f, %.2f)' % (
          mono, left, right))

def Filter(audio, filter):
  command = 'sox %s OUTPUT.wav %s' % (audio, filter)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      [audio],
      command,
      'Applying filter to %s (%s)' % (audio, filter))

def Mix(*audios):
  command = 'sox --norm=0 -m %s OUTPUT.wav' % (' '.join(audios))
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      audios,
      command,
      'Mixing songs %s' % str(audios))

def Concat(*audios):
  command = 'sox %s OUTPUT.wav' % (' '.join(audios))
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      audios,
      command,
      'Concatenating files %s' % str(audios))

def Silence(audio, *start_durations):
  pads = ['%.2f@%.2f' % (d, s) for (s, d) in start_durations]
  trims = ['trim 0 %.2f 0 %.2f %.2f' % (s, d, d) for (s, d) in start_durations]
  command = 'sox %s OUTPUT.wav pad %s %s' % (audio, ' '.join(pads), ' '.join(trims))
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.wav',
      [audio],
      command,
      'Silencing audio %s @ %s' % (str(audio), str(start_durations)))
