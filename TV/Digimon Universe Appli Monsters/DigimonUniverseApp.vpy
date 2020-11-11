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
# src = lvf.src(r'src/[BlueLobster] Digimon Universe Appli Monsters - 01 [1080p].mkv')

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = mvf.BM3D(src, sigma=1.5)	

aa = taa(denoise, 3)

deband = core.neo_f3kdb.Deband(aa, range=18, y=32, cb=48, cr=48, grainy=0, grainc=0, output_depth=16)

dehalo = stf.dehalo(deband) 
grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=10)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output(1)
# src.set_output(2)