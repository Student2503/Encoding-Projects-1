import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
import havsfunc as haf
from typing import Optional
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2
import sys
core.max_cache_size = 4096

# Source
# src = lvf.src(r'Z:\Encoding\Testing_Area\Kakushigoto\Kakushigoto - 01x12 - Hidden Truths [WEB-1080p x264 AAC] [Erai-raws].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# scaling
planes = split(src)
y = core.descale.Debicubic(planes[0], 1444, 812, 0, 1/2)
resized = core.resize.Bicubic(src, 1444, 812)
replanes = split(resized)

joined = join([y,replanes[1],replanes[2]])
joined = depth(joined, 16)

upscaled = core.placebo.Shader(joined, shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
upscaled = core.fmtc.resample(upscaled, css = 420)

# Filtering
denoise = core.knlm.KNLMeansCL(upscaled, a=2, h=1.00, d=3) 
aa = taa(denoise, aatype = "Nnedi3", cycle = 3)
deband = stf.masked_deband(aa)
grain = kgf.adaptive_grain(deband, 0.8, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(final, 10)]).set_output()