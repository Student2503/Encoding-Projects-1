import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
from vsutil import *
import sys
core.max_cache_size = 16384

# Source
src = lvf.src(r'Z:\Downloads\[Erai-raws] Peter Grill to Kenja no Jikan - 01 [1080p][Multiple Subtitle].mkv')
src = core.std.Trim(src, first = 15)

atx = lvf.src(r'Z:\Downloads\[Ohys-Raws] Peter Grill to Kenja no Jikan - 01 (AT-X 1920x1080 x264 AAC).mp4')
atx = core.resize.Bicubic(atx,1916,1080)
atx = core.std.AddBorders(atx, left=2,right=2)

#  srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
src = depth(src, 16)
atx = depth(atx, 16)

ohysmask = core.std.BlankClip(width=1916, height=1080, format=vs.YUV420P8, length=1, color=[0, 0, 0])
ohysmask = core.std.AddBorders(ohysmask, 2, 2, 0, 0, color=[255, 255, 255])
ohysmask = core.resize.Point(ohysmask, format=vs.YUV420P16)

# Decensoring

# Adding in card after OP
intro_erai = core.std.Trim(src, first = 0, last = 4171)
OP_card_ohys = core.std.Trim(atx, first = 4172, last = 4291)
rest_of_erai = core.std.Trim(src, first = 4172)
decensored = intro_erai+OP_card_ohys+rest_of_erai

#light bar decensors
ohys1 = atx[12094:12154]
erai1 = decensored[12094:12154]
decensored_scene1 = core.std.MaskedMerge(ohys1, erai1, ohysmask)
ep1 = core.std.Trim(decensored, last = 12093)
ep_after_censor1 = core.std.Trim(decensored, first = 12154)
decensored = ep1+decensored_scene1+ep_after_censor1

ohys2 = atx[13076:13249]
erai2 = decensored[13076:13249]
decensored_scene2 = core.std.MaskedMerge(ohys2, erai2, ohysmask)
ep2 = core.std.Trim(decensored, last = 13075)
ep_after_censor2 = core.std.Trim(decensored, first = 13249)
decensored = ep2+decensored_scene2+ep_after_censor2

ohys3 = atx[13680:13783]
erai3 = decensored[13680:13783]
decensored_scene3 = core.std.MaskedMerge(ohys3, erai3, ohysmask)
ep3 = core.std.Trim(decensored, last = 13679)
ep_after_censor3 = core.std.Trim(decensored, first = 13783)
decensored = ep3+decensored_scene3+ep_after_censor3

ohys4 = atx[14829:14996]
erai4 = decensored[14829:14996]
decensored_scene4 = core.std.MaskedMerge(ohys4, erai4, ohysmask)
ep4 = core.std.Trim(decensored, last = 14828)
ep_after_censor4 = core.std.Trim(decensored, first = 14996)
decensored = ep4+decensored_scene4+ep_after_censor4

# Rescaling Erai
src32 = depth(decensored, 32)
planes = split(src32)
descaled = core.descale.Debicubic(planes[0], 1440, 810, 0, 1/2)

resized = core.resize.Bicubic(src32, 1440, 810)
replanes = split(resized)

merged = join([descaled,replanes[1],replanes[2]])
merged = depth(merged, 16)

upscaled = core.placebo.Shader(merged, shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "ewa_lanczos")
upscaled = core.fmtc.resample(upscaled, css = 420)

# Filtering Erai
denoise = core.knlm.KNLMeansCL(upscaled,h=0.4, d=2, a = 3)
dering = haf.HQDeringmod(denoise)
deband = stf.masked_deband(dering)
aa = lvf.aa.nneedi3_clamp(deband)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.20, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(atx, 10),depth(decensored, 10)]).set_output()
# comp = lvf.scomp(depth(decensored,10), depth(final,10),make_diff=True).set_output()

