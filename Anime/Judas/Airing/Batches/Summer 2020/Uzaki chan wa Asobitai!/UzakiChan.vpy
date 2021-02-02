import vapoursynth as vs
core = vs.core

import os
from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
from vsutil import *
import sys

core.max_cache_size = 16*1024

# Source
# src = lvf.src(r'E:/Anime/TV/Uzaki-chan Wants to Hang Out!/Season 1/Uzaki-chan Wants to Hang Out! - 1x03 - The Asai Family Wants to Look Out for Us! [WEB-1080p x264 AAC] [Erai-raws].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.5, d=2, a=3, s=4)
aa = lvf.aa.nneedi3_clamp(denoise)
dehalo = stf.dehalo(aa)
deband = stf.masked_deband(dehalo, iterations=1, threshold = 2.8, radius = 24, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)
grain = kgf.adaptive_grain(deband, 0.30, luma_scaling=6)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(src, 10)]).set_output()