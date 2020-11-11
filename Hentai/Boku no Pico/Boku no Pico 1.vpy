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
shader  = r"Z:/Misc stuff/FSRCNNX_x2_16-0-4-1.glsl"

# Input
src = lvf.src(r'Z:/Encoding-Projects/Hentai/Boku no Pico/Sources/Remuxed disc 1/title_t01.mkv')
src = depth(src, 8)
cropped = core.std.Crop(src, top = 66, bottom = 70)

decomb = lvf.deinterlace.decomb(cropped, TFF = False, decimate = False, vinv = True)
vdecimate = core.vivtc.VDecimate(decomb)
dec = core.std.AddBorders(vdecimate, top = 66, bottom = 70)
fix = core.edgefixer.ContinuityFixer(vdecimate, [2,0,0], [0,0,0], [2,0,0], [0,0,0], [5,0,0])
fix = core.std.AddBorders(fix, top = 66, bottom = 70)

denoise = core.knlm.KNLMeansCL(depth(fix, 16), a=3, h=0.3, d=2)
deband = stf.masked_deband(denoise, grain = 0) 

awarpsharp = core.warp.AWarpSharp2(depth(deband, 16), depth=12, planes=[1,2])
warped = core.std.ShufflePlanes([deband, awarpsharp, awarpsharp], [0,1,2], colorfamily=src.format.color_family)

grain = kgf.adaptive_grain(warped, 0.15, luma_scaling=10)
edge = core.std.Crop(grain, top = 66, bottom = 72)
edge = core.std.AddBorders(edge, top = 66, bottom = 72)

final = depth(edge, 10)
final.set_output()
# core.std.Interleave([depth(dec, 10),depth(fcb, 10)]).set_output()
# 19059
# 47246