# These cannot contain / because that would confuse the temp rename substitution.
# TODO: better renaming.
PREFIX = 'gen'
TMP_PREFIX = 'tmp'

# A command has multiple input_filenames and one target". A target produces
# files, most of the time one (target=filename). An exception is when a single
# command produces multiple output files, then the target is the first filename.
# We keep a map for all targets that describes what's needed and how to create.
#   map : target -> ([input_filenames], command, comment)
TARGET_BUILD_MAP = {}
# If a filename is created by a multi-output command, and it's not a target
# (ie not the first filename), it is listed in this map.
# map : filename -> target
FILENAME_TARGET_MAP = {}

def FileExtension(filename):
  idx = filename.rfind('.')
  assert idx != -1
  return filename[idx + 1:]

def FileBaseName(filename):
  idx = filename.rfind('.')
  assert idx != -1
  return filename[idx + 1:]

def GroupBaseName(filename):
  idx = filename.rfind('-00001.')
  assert idx != -1
  return filename[:idx]

def IsGroup(filename):
  return filename.rfind('-00001.') != -1

def CreateBaseName(command):
  return '%s-%016x' % (PREFIX, abs(hash(command)))

# Output can be a single file or a list of multiple files.
def RegisterCommand(output, inputs, command, comment):
  assert type(inputs) is list or type(inputs) is tuple
  target = output[0] if type(output) is list else output
  if target not in TARGET_BUILD_MAP:
    TARGET_BUILD_MAP[target] = (inputs, command, comment)
  else:
    if TARGET_BUILD_MAP[target] != (inputs, command, comment):
      raise Exception(
        'build map already contains %s with different command' % target)
  return target

# Do not call directly.
def GenerateLinks(filenames):
  assert len(filenames) > 0
  input_basename = FileBaseName(filenames[0])
  basename = CreateBaseName(''.join(filenames))
  ext = FileExtension(filenames[0])
  commands = []
  links = []
  for i in range(len(filenames)):
    link = '%s-%05d.%s' % (basename, i + 1, ext)
    commands.append('ln -sf %s %s' % (filenames[i], link))
    links.append(link)
  commands.reverse()
  commands.insert(0, 'rm -f %s-?????.%s' % (basename, ext))
  target = links[0]
  RegisterCommand(
      links,
      filenames,
      '\n  '.join(commands),
      'Linking %s-?????.%s <- %s-?????.%s (%d files).' % (
          input_basename, ext, basename, ext, len(filenames)))
  return links

def GenerateName(target, name):
  print 'ln -sf %s %s' % (target, name)

def GenerateCommands(target, command, comment):
  ext = FileExtension(target)
  i = target.rfind('-00001.') if IsGroup(target) else target.rfind('.')
  suffix = target[i:]
  basename = target[:i]
  tmp_basename = '%s-%016x' % (TMP_PREFIX, abs(hash(command)))
  tmp_filename = '%s%s' % (tmp_basename, suffix)
  process = command.replace('OUTPUT', tmp_basename)
  postprocess = (
    '  for output in %s*.%s; do mv ${output} ${output/%s/%s}; done\n' % (
        tmp_basename, ext, tmp_basename, basename) if process != command
    else '')
  return (
    'if [ ! -e %s ]\nthen\n  echo "%s"\n  %s\n%sfi' % (
      target, comment.replace('"', '\\"'), process, postprocess))

def GenerateScript(working_directory, filenames):
  done_targets = set()
  script = [
    '# !/bin/bash',
    '# Abort script on error.',
    'set -e',
    '# Switch to working directory.',
    'cd %s' % working_directory,
    'rm -f OUTPUT*',
    ]

  def Generate(filename):
    target = (FILENAME_TARGET_MAP[filename]
              if filename in FILENAME_TARGET_MAP
              else filename)
    if target not in done_targets:
      # Check if there is a rule to create; otherwise it must exist.
      if target in TARGET_BUILD_MAP:
        (input_filenames, command, comment) = TARGET_BUILD_MAP[target]
        for f in input_filenames: Generate(f)
        script.append(GenerateCommands(target, command, comment))
        done_targets.add(target)

  for f in filenames: Generate(f)
  print '\n'.join(script)

def GenerateCleanupScript(working_directory, filenames):
  done_files = set()
  script = [
    '# !/bin/bash',
    '# Switch to working directory.',
    'cd %s' % working_directory,
    'mkdir saved',
    ]

  files = []
  for f in FILENAME_TARGET_MAP:
    if f not in done_files:
      files.append(f)
      done_files.add(f)
  for target in TARGET_BUILD_MAP:
    if target not in done_files:
      files.append(target)
      done_files.add(target)
    input_filenames = TARGET_BUILD_MAP[target][0]
    for f in input_filenames:
      if f not in done_files:
        files.append(f)
        done_files.add(f)

  script.extend(
      ['mv "%s" saved' % f for f in files if f.find('/') == -1])
  print '\n'.join(script)
