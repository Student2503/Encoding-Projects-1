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
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src,16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, d=2, a=3, s=6, h=1.0, channels="UV")
aa = taa(denoise, 3)

deband = join([
             core.placebo.Deband(plane(aa, 0), grain=0, threshold=2.8, radius=16),
             core.placebo.Deband(plane(aa, 1), grain=0, threshold=3.6, radius=20),
             core.placebo.Deband(plane(aa, 2), grain=0, threshold=3.6, radius=20)
                ])     
grain = kgf.adaptive_grain(deband, 0.25, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()