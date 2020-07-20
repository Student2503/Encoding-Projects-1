import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
from vsutil import *
import sys
core.max_cache_size = 8096

# Source
src = lvf.src(r'Z:\Anime\BNA - Brand New Animal\Season 1\[Asenshi] Brand New Animal (BNA) - 01 [B92208CE].mkv')
# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.2, d=2, a = 3)
dering = haf.HQDeringmod(denoise)
deband = stf.masked_deband(dering)
aa = lvf.aa.nneedi3_clamp(deband)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.35, luma_scaling=8)

# Output
final = depth(grain, 10)
src.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()