import vapoursynth as vs
core = vs.core

from vardefunc import diff_creditless_mask as DCM
from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import fvsfunc as fvf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
import adjust
from vsutil import *
import sys
core.max_cache_size = 16384

# Source
funi = lvf.src(r'Z:\Encoding\Projects\_NCOP & NCED\SAO\Funimation\[Erai-raws] Sword Art Online Alicization - War of Underworld 2nd Season - 01 [1080p][Multiple Subtitle].mkv')
waka = lvf.src(r'Z:\Encoding\Projects\_NCOP & NCED\SAO\Wakanim\Sword Art Online Alicization - War of Underworld - 13 (WEB-DL 1920x1080 x264 AAC Rus).mp4')
undimmed = lvf.src(r'Z:\Encoding\Projects\_NCOP & NCED\SAO\! OP/OP 2 Undimmed.mp4')
funi = funi[1:]
# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
waka = depth(waka, 16)
funi = depth(funi, 16)
undimmed = depth(undimmed, 16)
waka = core.std.Trim(waka, first = 911, last = 3066)
funi = core.std.Trim(funi, first = 911, last = 3066)

#undimming
dim1 = adjust.Tweak(waka, sat=1.65, cont=1.65)
dim2 = adjust.Tweak(waka, sat=1.90, cont=1.20)
dim2 = core.std.Levels(dim2, gamma = 1.05)

undim = fvf.rfs(waka, dim1, mappings="[151 164]")
# undim = fvf.rfs(undim, dim1, mappings="[1392 1402]")
undim = fvf.rfs(undim, dim2, mappings="[1679 1802]")
# undim = fvf.rfs(undim, dim1, mappings="[1890 2006]")


mask = kgf.hardsubmask_fades(waka, undim, expand_n=1)
mask = core.resize.Point(mask, format = vs.YUV420P16)

# Filtering
# denoise = core.knlm.KNLMeansCL(funi,h=0.4, d=2, a=3)
# dering = haf.HQDeringmod(denoise)
# deband = stf.masked_deband(dering, grain = 0)
# aa = lvf.aa.nneedi3_clamp(deband)
# dehalo = stf.dehalo(aa)
# grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# Output
# final = depth(grain, 10)
# mask.set_output()
# core.std.Interleave([depth(waka, 10),depth(mask, 10)]).set_output()
comp = lvf.scomp(undim, waka, undimmed, make_diff=False).set_output()