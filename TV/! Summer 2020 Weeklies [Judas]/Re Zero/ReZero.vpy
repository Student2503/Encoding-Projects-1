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

core.max_cache_size = 16 * 1024

# Source
# src = lvf.src(r"Z:\Downloads\! Sonarr\imported-sonarr/[Erai-raws] Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 02 [1080p][Multiple Subtitle].mkv")
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.4, d=2, a=3)
deband = stf.masked_deband(denoise, iterations = 1, threshold = 3.2, radius = 18, grain = 0)
aa = taa(deband, 3, cycles = 2)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.20, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()