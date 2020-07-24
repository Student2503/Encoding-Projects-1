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
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
deband = stf.masked_deband(src, iterations = 1, threshold = 3.2, radius = 18, grain = 0)
grain = kgf.adaptive_grain(deband, 0.20, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()