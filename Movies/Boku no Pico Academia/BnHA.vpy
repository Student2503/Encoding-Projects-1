import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
import havsfunc as haf
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 8096

# Source
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# Rescaling

planes = split(src)
descaled = core.descale.Debicubic(planes[0], 1280, 720, 0, 1/2)

resized = core.resize.Bicubic(src, 1280, 720)
replanes = split(resized)

merged = join([descaled,replanes[1],replanes[2]])
merged = depth(merged, 16)

upscaled = core.placebo.Shader(merged, shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
upscaled = core.fmtc.resample(upscaled, css = 420)

#masking

mask = core.std.Sobel(depth(src, 16), 0)
luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
mask_outer = iterate(luma, core.std.Maximum, 2)
mask_inner = iterate(mask_outer, core.std.Minimum, 3)
halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
halos = iterate(halos, core.std.Minimum, 1)

# Filtering

denoise = core.knlm.KNLMeansCL(depth(upscaled, 16),h=0.6, d=2, a=3)

dehalo = haf.YAHR(denoise, blur=1, depth=32)
dehalo = stf.dehalo(dehalo)
masked_dehalo = core.std.MaskedMerge(denoise, dehalo, halos)

deband = stf.masked_deband(masked_dehalo)

aa = taa(deband, aatype = 'Nnedi3', cycle = 2)

grain = kgf.adaptive_grain(aa, 0.25, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()