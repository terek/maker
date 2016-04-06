import generator

# No dependence on other generated images.
def SimpleImage(args,
                command = 'convert', output_format = 'png32:'):
  command = '%s %s %sOUTPUT.png' % (command, args, output_format)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.png', [], command, command)

# Dependence on 1 generated image.
def SimpleConvert(args, image,
                  command = 'convert', output_format = 'png32:'):
  command = '%s %s %sOUTPUT.png' % (command, args % image, output_format)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.png', [image], command, command)

# Dependence on multiple generated image.
def MultiConvert(args, images,
                 command = 'convert', output_format = 'png32:'):
  command = '%s %s %sOUTPUT.png' % (
      command, args % tuple(images), output_format)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.png', images, command, command)

#def MaskedConvert(mask, args, image,
#                  command = 'convert', output_format = 'png32:'):
#  command = '%s %s -mask %s %s +mask %sOUTPUT.png' % (
#      command, image, mask, args, output_format)
#  return generator.RegisterCommand(
#    generator.CreateBaseName(command) + '.png', [image, mask], command, command)

# Make sure colors are not stored as palette indices.
#def FixColorType(image):
#  command = 'convert %s -define png:color-type=2 OUTPUT.png' % image
#  return generator.RegisterCommand(
#    generator.CreateBaseName(command) + '.png', [image], command, command)

# Resize image to fit widthxheight, cropping to completely fill or adding black
# bands as needed.
#def Resize(fill, width, height, image, gravity = 'center'):
#  dim = '%dx%d' % (width, height)
#  command = (
#    'convert -size %s xc:black  %s -resize %s%s -gravity %s -composite ' +
#    '%sOUTPUT.png') % (dim, image, dim, '^' if fill else '', gravity,
#                       output_format)
#  return generator.RegisterCommand(
#    generator.CreateBaseName(command) + '.png', [image], command, command)

def SimpleResize(percent, image, output_format = 'png32:'):
  command = (
    'convert %s -resize %s%% %sOUTPUT.png') % (image, percent, output_format)
  return generator.RegisterCommand(
    generator.CreateBaseName(command) + '.png', [image], command, command)


#def Crop(image, top = 0, bottom = 0, left = 0, right = 0):
#  command = (
#      'convert %s ' +
#      '-gravity NorthWest -crop 0x0+%d+%d +repage ' +
#      '-gravity SouthEast -crop 0x0+%d+%d ' +
#      'png24:OUTPUT.png') % (
#          image, left, top, right, bottom)
#  return generator.RegisterCommand(
#      generator.CreateBaseName(command) + '.png', [image], command, command)

#def Fade(ratio, image):
#  assert 0 <= ratio <= 1
#  command = (
#    'convert %s -fill black -colorize %.2f -define png:color-type=2 ' +
#    'png24:OUTPUT.png') % (
#      image, 100 * ratio)
#  return generator.RegisterCommand(
#      generator.CreateBaseName(command) + '.png', [image], command, command)
#
#def Blend(ratio, src_image, dst_image):
#  assert 0 <= ratio <= 1
#  command = (
#      'convert %s %s -compose blend -define compose:args=%.2f -composite ' +
#      '-depth 8 -define png:color-type=2 png24:OUTPUT.png') % (
#          src_image, dst_image, 100 * ratio)
#  return generator.RegisterCommand(
#      generator.CreateBaseName(command) + '.png',
#      [src_image, dst_image],
#      command, command)

def Composite(*images, **kwargs):
  output_format = ('png24:' if 'output_format' not in kwargs
                   else kwargs['output_format'])
  assert len(images) > 0
  if len(images) == 1:
    return images[0]
  command = (
      'convert %s %s %sOUTPUT.png' % (
          images[0],
          ' '.join(map(lambda f: '%s -composite' % f, images[1:])),
          output_format))
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.png',
      images,
      command,
      'Compositing %d images: %s' % (len(images), str(images)))