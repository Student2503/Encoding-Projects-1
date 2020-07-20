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
core.max_cache_size = 12288

# Source
# src = lvf.src(r'Z:\Downloads\! Nyaa\Gleipnir [2020] [WEB-DL] [1080p] [RUS + JAP]\Gleipnir - 12 (WEB-DL 1920x1080 x264 AAC Rus + Jap).mkv')
# src = lvf.src(r'C:\Users\Joel\Downloads\[Erai-raws] Gleipnir - 12 [1080p].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, h=0.40,d=2,a=3) 
dehalo= stf.dehalo(denoise)
aa = taa(dehalo, aatype = "Nnedi3")	
deband = stf.masked_deband(aa)
grain = kgf.adaptive_grain(deband, 0.2, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()