import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 16384

# Source
# src = lvf.src(r"Z:\Downloads\! Sonarr\imported-sonarr/[Erai-raws] Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 02 [1080p][Multiple Subtitle].mkv")
# old_Judas= lvf.src(r'Z:/Downloads/[Judas] Re.Zero kara Hajimeru Isekai Seikatsu - S02E01.mkv')
# new_Judas= lvf.src(r'C:/Users/Joel/Downloads/[Erai-raws] Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 02 [1080p][Multiple Subtitle].mkv')
# anitime = lvf.src(r'Z:/Downloads/[Anime Time] Re Zero kara Hajimeru Isekai Seikatsu S2 - 02 [1080p][HEVC 10bit x265][Multi Sub][AAC].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
# src = depth(src, 16)
# Scaling
src32 = depth(src, 32)
planes = split(src32)
descaled = core.descale.Debicubic(planes[0], 1280, 720, 0, 1/2)

resized = core.resize.Bicubic(src32, 1280, 720)
replanes = split(resized)

merged = join([descaled,replanes[1],replanes[2]])
merged = depth(merged, 16)

upscaled = core.placebo.Shader(merged, shader=r"FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "ewa_lanczos")
upscaled = core.fmtc.resample(upscaled, css = 420)
# Filtering
# dm = lvf.denoise.adaptive_mask(upscaled, luma_scaling = 10)
denoise = core.knlm.KNLMeansCL(upscaled,h=0.4, d=2, a=3)
# denoise = core.std.MaskedMerge(denoise, upscaled, dm)

deband = stf.masked_deband(denoise, iterations = 1, threshold = 3.5, radius = 20, grain = 0)
aa = lvf.aa.nneedi3_clamp(deband)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(src, 10)]).set_output()