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
# src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Weekly batches\[HorribleSubs] Nami yo Kiitekure - 12 [1080p].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# dehalo masking
mask = core.std.Sobel(src, 0)
luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
mask_outer = iterate(luma, core.std.Maximum, 2)
mask_inner = iterate(mask_outer, core.std.Minimum, 3)
halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
halos = iterate(halos, core.std.Minimum, 1)

# Filtering
denoise = mvf.BM3D(src, sigma = 1)

dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
dehalo = stf.dehalo(dehalo)
masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), depth(dehalo, 16), depth(halos, 16))

aa = taa(depth(masked_dehalo, 16), 3)

deband = stf.masked_deband(depth(aa, 32))

grain = kgf.adaptive_grain(depth(deband, 16), 0.3, luma_scaling=10)
grain = depth(grain, 10)
# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([fvf.Depth(src, 10),final]).set_output()