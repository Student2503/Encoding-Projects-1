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
# src = lvf.src(r'src/[Erai-raws] Noblesse - 01 [1080p][Multiple Subtitle].mkv')

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, d=3, a=2, s=6, h=0.6)

aa = taa(denoise, 3)

deband = join([
             core.placebo.Deband(plane(aa, 0), grain=0, threshold=2.8, radius=16),
             core.placebo.Deband(plane(aa, 1), grain=0, threshold=3.2, radius=20),
             core.placebo.Deband(plane(aa, 2), grain=0, threshold=3.2, radius=20)
                ])    

dehalo = stf.dehalo(deband) 

grain = kgf.adaptive_grain(dehalo, .45, luma_scaling=8)

# # Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output(1)
# src.set_output(2)
