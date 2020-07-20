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
core.max_cache_size = 16384

# Source
# funi = lvf.src(r'Z:\Encoding\Projects\_NCOP & NCED\SAO\Funimation\[Erai-raws] Sword Art Online Alicization - War of Underworld 2nd Season - 01 [1080p][Multiple Subtitle].mkv')
# waka = lvf.src(r'Z:\Encoding\Projects\_NCOP & NCED\SAO\Wakanim\Sword Art Online Alicization - War of Underworld - 13 (WEB-DL 1920x1080 x264 AAC Rus).mp4')
# funi = src[1:]
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(waka, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.4, d=2, a=3)
dering = haf.HQDeringmod(denoise)
deband = stf.masked_deband(dering, grain = 0)
aa = lvf.aa.nneedi3_clamp(deband)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(atx, 10)]).set_output()
# comp = lvf.scomp(funi, waka, make_diff=True).set_output()