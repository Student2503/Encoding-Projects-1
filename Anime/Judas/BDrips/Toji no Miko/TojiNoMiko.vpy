import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
import havsfunc as haf
from typing import Optional
from vsutil import *
import sys
import os

core.max_cache_size = 16 * 1024

# Source
# src = lvf.src(r'src/[Beatrice-Raws] Toji no Miko 10 [BDRip 1920x1080 HEVC FLAC].mkv')

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
aa = taa(src, 3)

deband = stf.masked_deband(aa, iterations=1, threshold = 2.4, radius = 16, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)

dehalo = stf.dehalo(deband) 
grain = kgf.adaptive_grain(dehalo, 0.30, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output(1)
# src.set_output(2)