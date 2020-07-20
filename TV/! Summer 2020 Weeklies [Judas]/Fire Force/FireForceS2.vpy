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

core.max_cache_size = 16384

# Source
# src = lvf.src(r'Z:\Downloads\[HorribleSubs] Enen no Shouboutai S2 - 02 [1080p].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# scaling
planes = split(src)
y = core.descale.Debicubic(planes[0], 1600, 900, 0, 1/2 )
resized = core.resize.Bicubic(src, 1600, 900)
replanes = split(resized)

joined = join([y,replanes[1],replanes[2]])
joined = depth(joined, 16)

upscaled = core.placebo.Shader(joined, shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "ewa_lanczos")
upscaled = core.fmtc.resample(upscaled, css = 420)


# Filtering
denoise = core.knlm.KNLMeansCL(upscaled,h=0.4, d=2, a=4)
deband = stf.masked_deband(denoise, grain = 0)
aa = taa(deband, 3)
dehalo =  stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.15, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()