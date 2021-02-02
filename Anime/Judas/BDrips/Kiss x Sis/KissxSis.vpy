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
core.max_cache_size = 16384

# Source
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

def _dehalo(clip, rx, darkstr, brightstr):
    return haf.FineDehalo(clip, rx=rx, darkstr=darkstr, brightstr=brightstr, contra=1, showmask=0)

denoise = core.knlm.KNLMeansCL(src, d=2, a=4, s=4, h=0.6)

dehalo = _dehalo(denoise, 2.3, 0.6, 1.0)

deband = core.placebo.Deband(dehalo, planes=1, threshold=2, radius=16, grain=0)

grain = kgf.adaptive_grain(deband, 0.25, luma_scaling=8)

final = depth(grain, 10)
final.set_output()