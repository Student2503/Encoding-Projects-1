import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
import os

core.max_cache_size = 16*1024

# Source
# src = lvf.src(r'Z:/Downloads/! Sonarr/imported-sonarr/[Erai-raws] Maou Gakuin no Futekigousha - 12 [1080p][Multiple Subtitle].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, h=0.4, d=2, a=3)
aa = lvf.aa.nneedi3_clamp(denoise)
deband = stf.masked_deband(aa, iterations=1, threshold = 2.8, radius = 18, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)
grain = kgf.adaptive_grain(deband, 0.30, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(src, 10)]).set_output()