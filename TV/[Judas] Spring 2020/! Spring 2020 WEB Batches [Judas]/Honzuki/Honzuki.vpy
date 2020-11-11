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

# Source
# src = lvf.src(r'Z:\Downloads\! Nyaa\[Erai-raws] Honzuki no Gekokujou - Shisho ni Naru Tame ni wa Shudan wo Erandeiraremasen 2nd Season - 12 END [1080p][Multiple Subtitle].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)
planes = split(depth(src, 32))
descaled = kgf.inverse_scale(planes[0], height=812,kernel='bicubic', b=0, c=1/2,mask_detail=True)
ch1 = core.resize.Bicubic(planes[1], height = 812, width = 1444)
ch2 = core.resize.Bicubic(planes[2], height = 812, width = 1444)

merged = kgf.join([descaled, ch1, ch2])
rescaled =  core.placebo.Shader(depth(merged, 16), shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
rescaled = core.fmtc.resample(rescaled, css = 420)

# dehalo masking
# mask = core.std.Sobel(src, 0)
# luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
# mask_outer = iterate(luma, core.std.Maximum, 2)
# mask_inner = iterate(mask_outer, core.std.Minimum, 3)
# halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
# halos = iterate(halos, core.std.Minimum, 1)

# Filtering
denoise = mvf.BM3D(rescaled, sigma = 1)

# dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
# dehalo = stf.dehalo(dehalo)
# masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), depth(dehalo, 16), depth(halos, 16))

aa = taa(depth(denoise, 16), 3)

deband = stf.masked_deband(depth(aa, 32))

grain = kgf.adaptive_grain(depth(deband, 16), 0.4, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()