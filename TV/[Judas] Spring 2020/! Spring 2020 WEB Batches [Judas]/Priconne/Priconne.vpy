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
core.max_cache_size = 16384

# Source
# src = lvf.src(r'Z:\Downloads\! Nyaa\[Erai-raws] Princess Connect! Re-Dive - 02 [1080p][Multiple Subtitle].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# Masking
mask = core.std.Sobel(src, 0)
luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
mask_outer = iterate(luma, core.std.Maximum, 2)
mask_inner = iterate(mask_outer, core.std.Minimum, 3)
halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
halos = iterate(halos, core.std.Minimum, 1)

# Filtering
denoise = mvf.BM3D(src, sigma = 1)

# dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
dehalo = stf.dehalo(depth(denoise, 16))
masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), depth(dehalo, 16), depth(halos, 16))

aa = taa(masked_dehalo, aatype = "Nnedi3")

upscaled = core.placebo.Shader(depth(aa, 16), shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 3840, height = 2160, filter = "haasnsoft")
supersampled = core.resize.Spline36(upscaled, width = 1920, height = 1080)
supersampled = core.resize.Bicubic(supersampled, format=vs.YUV420P16)

deband = stf.masked_deband(supersampled)
grain = kgf.adaptive_grain(depth(deband, 16), 0.6, luma_scaling=10)

# Output
final = fvf.Depth(grain, 10)
final.set_output()
# core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(supersampled, 10)]).set_output()