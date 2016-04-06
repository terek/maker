# -*- coding: utf-8 -*-

import argparse

import generator
import renderer
import sox

from functools import partial
from functools import reduce

from commands import *
from functors import *

parser = argparse.ArgumentParser(description='Video maker.')
parser.add_argument('--absolute_working_directory', required = True)
parser.add_argument('--audio_directory', required = True)
parser.add_argument('--bpm', type=int, default=120)
parser.add_argument('--cleanup', action='store_true')
parser.add_argument('--generate', required = True)
parser.add_argument('--fps', required = True, type=float)
parser.add_argument('--master_audio', required = True)
parser.add_argument('--video_directory', required = True)
args = vars(parser.parse_args())

TW=1280
TH=720
DIM = '%dx%d' % (TW, TH)

def compose(*functions):
  def compose2(f, g):
    return lambda x: f(g(x))
  return reduce(compose2, functions)

ZONGORA_TRACK_L = 't8_03_01.wav'
ZONGORA_TRACK_R = 't8_04_01.wav'
ENEK_TRACK = 't7_07_06.wav'
BAR = args['bpm'] / 60.

enek_mono = sox.Filter(
    args['audio_directory'] + ENEK_TRACK,
    'compand 0.1,0.3 -60,-60,-30,-15,-20,-12,-4,-8,-2,-7 -14 ' +
    'treble 2 2k ' +
    'equalizer 1.1k 1q -3')
enek = sox.Filter(
    sox.MonoToStereo(enek_mono, enek_mono),
    'vol 0.2')

zongora = sox.Filter(
    args['audio_directory'] + 's8_0304_1.wav',
    #sox.MonoToStereo(args['audio_directory'] + ZONGORA_TRACK_L,
    #                 args['audio_directory'] + ZONGORA_TRACK_R),
    'vol 0.1')
    
master_audio = sox.Filter(
  sox.Trim(sox.Mix(zongora, enek), 1 * BAR, 62 * BAR),
  'fade h 0 0 8 pad 0 4')

# Given a list of images, make it count long by sampling or duplicating frames
# proportionally.
def Resample(count, images):
  assert images
  int_count = int(round(count))
  assert int_count > 1
  if len(images) == int_count:
    return images
  new_images = []
  for i in range(int_count):
    r = float(i) / (int_count - 1)
    new_images.append(images[int(round(float(len(images) - 1) * r))])
  return new_images

g = renderer.Renderer(args)

def ProcessFrames(processors, frames):
  return (
    map(compose(*processors), frames) if type(processors) == list
    else map(processors, frames) if hasattr(processors, '__call__')
    else frames)

def Process(duration, processors, frames):
  sampled = Resample(duration * args['fps'], frames)
  processed = ProcessFrames(processors, sampled)
  g.Add(duration, processed)


STREAM_FPS=29.97
STREAM_LEN=132
main_stream = {}
for i in [47,48,49,50]:
  main_stream[i] = [
      VideoToImages(
          args['video_directory'] + 'DSC_00%s.MOV' % i,
          STREAM_FPS, 0, STREAM_LEN),
      None]
main_stream[47][1] = 4.4
main_stream[48][1] = 7.10
main_stream[49][1] = 7.2
main_stream[50][1] = 4.92

kezek_stream = (
    VideoToImages(
        args['video_directory'] + 'DSC_0051.MOV', STREAM_FPS, 0, STREAM_LEN),
    3.05)

kozel_stream = (
    VideoToImages(
        args['video_directory'] + 'DSC_0056.MOV', STREAM_FPS, 0, STREAM_LEN),
    3.12)

OKOL_CUT_LEN = 5
okol_stream = (
    VideoToImages(
        VideoCutSegment(
            args['video_directory'] + 'DSC_0061.MOV', 3, OKOL_CUT_LEN),
        STREAM_FPS, 0, OKOL_CUT_LEN),
    1.52)

INTRO_CUT_LEN = 5
intro_stream = (
    VideoToImages(
        VideoCutSegment(
            args['video_directory'] + 'DSC_0059.MOV', 27, INTRO_CUT_LEN),
        STREAM_FPS, 0, INTRO_CUT_LEN),
    1.6)

LABAK_CUT_LEN = 5
labak_stream = (
    VideoToImages(
        VideoCutSegment(
            args['video_directory'] + 'DSC_0053.MOV', 150, INTRO_CUT_LEN),
        STREAM_FPS, 0, LABAK_CUT_LEN),
    1.6)

ARANY_CUT_LEN = 8
arany_stream = (
    VideoToImages(
        VideoCutSegment(
            args['video_directory'] + 'DSC_0148.MOV', 27, ARANY_CUT_LEN),
        STREAM_FPS, 0, ARANY_CUT_LEN),
    0)

def GetStreamBars(stream, start, len):
  s_frame = (stream[1] + start * BAR) * STREAM_FPS
  e_frame = (stream[1] + (start + len) * BAR) * STREAM_FPS
  return stream[0][int(round(s_frame)) : int(round(e_frame))]

def ProcessStreamBars(num_bars, processors, stream, offset_bar = 0):
  curr_bar = g.CurrTime() / BAR
  Process(num_bars * BAR, processors,
          GetStreamBars(stream, curr_bar + offset_bar, num_bars))

def FredsEffect(effect, params, image):
  command = '../fred/%s %s %s OUTPUT.png' % (effect, params, image)
  return generator.RegisterCommand(
      generator.CreateBaseName(command) + '.png', [image], command, command)

def FramesApply(frames, start, duration, transformer):
  start_frame = int(round(start * args['fps']))
  end_frame = start_frame + int(round(duration * args['fps']))
  transformed = transformer(frames[start_frame : end_frame])
  assert len(transformed) == end_frame - start_frame
  frames[start_frame : end_frame] = transformed
  #return frames[:start_frame] + transformed + frames[end_frame:] = transformed

def Combinator(args_list):
  args_list_lens = [len(x) for x in args_list if type(x) == list]
  num_items = 1
  if args_list_lens:
    if max(args_list_lens) != min(args_list_lens):
      raise Exception('lists should be of identical length: %s %s' % (
        str(args_list_lens), str(args_list)))
    num_items = args_list_lens[0]
  items = []
  for i in range(num_items):
    t = float(i) / (num_items - 1) if num_items > 1 else 0
    item = map(
        lambda arg: (arg(t) if hasattr(arg, '__call__') else
                     arg[i] if type(arg) == list else
                     arg),
        args_list)
    items.append(item)
  return items

def FadeOut(images):
  return map(lambda a : Fade(*a), Combinator([identity, images]))

def FadeIn(images):
  return map(lambda a : Fade(*a), Combinator([inverter(identity), images]))

def VidaBlur(image):
  mask = SimpleImage(
    '-size %s xc: -draw \'circle 660,200 640,80\' -negate' % DIM)
  return MaskedConvert(mask, '-blur 0x8', image)


defproc = [
    partial(FredsEffect, 'lucisarteffect', '-g 0.3 -s 100'),
    #partial(SimpleResize, 50)
    ]

# INTRO
INTRO_START=5
INTRO_END=28.6
INTRO_MAX=30
INTRO_DURATION = INTRO_END - INTRO_START
intro_original = VideoToImages(
    VideoCutSegment(
        args['video_directory'] + 'DSC_0059.MOV', 0, INTRO_MAX),
    STREAM_FPS, 0, INTRO_MAX)
intro_frames = ProcessFrames(
    defproc,
    Resample(INTRO_DURATION * args['fps'],
             intro_original[int(INTRO_START * STREAM_FPS) :
                            int(INTRO_END * STREAM_FPS)]))
FramesApply(intro_frames, 0 * BAR, 1 * BAR, FadeIn)
intro_vid = VideoFromImages(intro_frames, args['fps'])
intro_aud = sox.Trim(
    args['video_directory'] + 'intro_cleaned.wav',
    INTRO_START,
    INTRO_DURATION)
intro_master = MergeVideoAndAudio(intro_vid, intro_aud)

#ProcessStreamBars(1, defproc, intro_stream)
Process(1 * BAR, defproc, GetStreamBars(labak_stream, 0, 1))
#ProcessStreamBars(1, defproc, kezek_stream)
#ProcessStreamBars(1, defproc, main_stream[50])
ProcessStreamBars(1, defproc, kozel_stream)
#  2- 6 Nem ez a szakmám,
ProcessStreamBars(4, defproc, main_stream[50])
#  6-10 Elmagyarázom,
ProcessStreamBars(2, defproc, kozel_stream)
ProcessStreamBars(2, defproc, main_stream[50])
# 10-14 A szervezetetednél
ProcessStreamBars(4, defproc + [VidaBlur], main_stream[50])
# 14-18 Egy alapos belső vizsgálat helyett
ProcessStreamBars(2, defproc, kozel_stream)
ProcessStreamBars(1, defproc, main_stream[47])
# 18-20 ököl!
# 20-22
Process(1.5 * BAR, defproc, GetStreamBars(okol_stream, 0, 1.5))
ProcessStreamBars(3.5, defproc, main_stream[49])
# 22-26 A koleszos haverok alatt
ProcessStreamBars(2, defproc, kozel_stream)
ProcessStreamBars(2, defproc, main_stream[50])
# 26-30 Az akciós gáznak ára van
ProcessStreamBars(2, defproc, main_stream[50])
ProcessStreamBars(2, defproc, kozel_stream)
# 30-34 S noha nedvesen a sár jól kenhető
ProcessStreamBars(2, defproc, main_stream[49])
ProcessStreamBars(2, defproc, kozel_stream)
# 34-36 szakad!
# 36-40 Nem mehettek Amerikába,
ProcessStreamBars(4, defproc, kozel_stream)
ProcessStreamBars(1.5, defproc, main_stream[49])
# 40-44 De ha az ostoba taktikázás miatt
ProcessStreamBars(3, defproc, kezek_stream)
ProcessStreamBars(1.0, defproc, kozel_stream)
# 44-48 Mert ahol hiányoznak az ellensúlyok
#ProcessStreamBars(2, defproc, main_stream[48])
ProcessStreamBars(2, defproc, kezek_stream)
ProcessStreamBars(2.5, defproc, kozel_stream)
# 48-   wc keféket!
Process(4 * BAR, defproc, GetStreamBars(arany_stream, 0, 4))
#ProcessStreamBars(2, defproc, kozel_stream)
# 50-54
#ProcessStreamBars(2, defproc, main_stream[50])
ProcessStreamBars(2, defproc, kezek_stream)
# 54-58
ProcessStreamBars(4, defproc, main_stream[49])
# 58-62
ProcessStreamBars(4, defproc, main_stream[49])

black = SimpleImage('-size %s xc:black -depth 8 -type TrueColorMatte' % DIM)
Process(2 * BAR, defproc, [black])

g.Apply(58 * BAR, 4.1 * BAR, FadeOut)


gen = args['generate']
gen_all = gen == 'all'

(vid_start, vid_duration, vid) = g.Render(
    0 * BAR, 64 * BAR,
    prefix_videos = [intro_vid] if gen_all else [])
#(vid_start, vid_duration, vid) = g.Render(52 * BAR, 8 * BAR)
aud = sox.Trim(master_audio, vid_start, vid_duration)
if gen_all:
  aud = sox.Concat(intro_aud, aud)

clip_master = MergeVideoAndAudio(vid, aud)



final = (master_audio if args['generate'] == 'music' else
         intro_master if args['generate'] == 'intro' else
         clip_master if args['generate'] == 'clip' else
         clip_master)

if args['cleanup']:
  generator.GenerateCleanupScript(
      args['absolute_working_directory'], [master_audio])
else:
  generator.GenerateScript(args['absolute_working_directory'], [final])
  #generator.GenerateScript(args['absolute_working_directory'], [master_audio])

generator.GenerateName(master_audio, args['master_audio'])
generator.GenerateName(final, 'final.mp4')
