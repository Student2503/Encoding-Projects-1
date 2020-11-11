import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
import havsfunc as haf
from typing import Optional
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2
import sys
core.max_cache_size = 8192

# Source
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, a=2, h=0.60, d=3) 
aa = taa(denoise, aatype = "Nnedi3", cycle = 3, dark = 0.1)
deband = stf.masked_deband(aa)
grain = kgf.adaptive_grain(deband, 0.3, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()