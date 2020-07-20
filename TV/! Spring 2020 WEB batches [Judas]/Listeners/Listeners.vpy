import vapoursynth as vs
core = vs.get_core()
import lvsfunc as lvf
import fvsfunc as fvf
import kagefunc as kgf
import mvsfunc as mvf
import havsfunc as haf
from vsutil import *
from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
from nnedi3_rpow2 import *
from typing import Optional
import sys

# src = lvf.src('Z:\Downloads\! Nyaa\[Erai-raws] Listeners - 03 [1080p].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

#filtering
denoise = mvf.BM3D(src, sigma = 1.5)
denoise = depth(denoise, 16)
# dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
# dehalo = stf.dehaloed(depth(dehalo, 16))
# masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), dehalo, depth(halos, 16))

aa = taa(denoise, 3)	

deband = stf.masked_deband(depth(aa, 32))

grain = kgf.adaptive_grain(deband, 0.6, luma_scaling=1)

final = fvf.Depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()