import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
from typing import Optional
from vsutil import *
import sys
import nnedi3_rpow2
import mvsfunc as mvf
# import muvsfunc as muf
# import adjust
# import havsfunc as haf
core.max_cache_size = 8096
shader  = r"C:/FSRCNNX_x2_16-0-4-1.glsl"

# Input
dvd = lvf.src(r'src/Disc 1/title_t01.mkv')
remastered = lvf.src(r'src/Remastered/Boku no Pico - 1.mkv')
# remastered = core.vivtc.VDecimate(remastered)

src = dvd

decomb = lvf.deinterlace.decomb(src, TFF = True, decimate = False, vinv = True)
decimated = core.vivtc.VDecimate(decomb).fmtc.resample(css=444)[220:]
deblended = lvf.deinterlace.deblend(remastered, 5)

cropped = core.std.Crop(decimated, top = 67, bottom = 70)
fix = core.edgefixer.ContinuityFixer(cropped,left=0,right=3,top=[0,2,2],bottom=[0,1,1],radius=[2,2,2])
fix = core.std.AddBorders(fix, top = 1, bottom = 1)
resized = core.resize.Spline36(fix, 1920, 1080)

# fix = core.std.AddBorders(fix, top = 67, bottom = 70)

# denoise = core.knlm.KNLMeansCL(depth(fix, 16), a=3, h=0.3, d=2)
# deband = stf.masked_deband(denoise, grain = 0) 

# awarpsharp = core.warp.AWarpSharp2(depth(deband, 16), depth=12, planes=[1,2])
# warped = core.std.ShufflePlanes([deband, awarpsharp, awarpsharp], [0,1,2], colorfamily=src.format.color_family)

# grain = kgf.adaptive_grain(warped, 0.15, luma_scaling=10)
# edge = core.std.Crop(grain, top = 66, bottom = 72)
# edge = core.std.AddBorders(edge, top = 66, bottom = 72)

final = depth(fix, 8)
resized.set_output(0)
remastered.set_output(1)
# core.std.Interleave([depth(dec, 10),depth(fcb, 10)]).set_output()
# 19059
# 47246