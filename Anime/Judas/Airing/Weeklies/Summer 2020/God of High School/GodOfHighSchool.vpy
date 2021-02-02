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
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.3, d=2)
deband = stf.masked_deband(denoise)
aa = lvf.aa.nneedi3_clamp(deband)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.20, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()