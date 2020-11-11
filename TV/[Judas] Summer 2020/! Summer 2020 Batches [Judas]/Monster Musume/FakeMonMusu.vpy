import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsTAAmbk import TAAmbk as taa
import havsfunc as haf
from vsutil import *
import sys
core.max_cache_size = 8 * 1024

# Source
# src = lvf.src(r'src/[HorribleSubs] Monster Musume no Oisha-san - 08 [1080p].mkv')

def masked_deband(clip: vs.VideoNode, 
                  radius:  int = 15, threshold: float = 3, iterations: int = 1,
                  grain: int = 5.0, mask_denoise: Optional[float] = None, **kwargs) -> vs.VideoNode:
        deband = join([
              core.placebo.Deband(plane(clip, 0), grain=grain, iterations=iterations, threshold=threshold, radius =radius),
              core.placebo.Deband(plane(clip, 1), grain=0, iterations=iterations, threshold=threshold, radius =radius),
              core.placebo.Deband(plane(clip, 2), grain=0, iterations=iterations, threshold=threshold, radius =radius)
                 ])     
        mask = kgf.kirsch(clip)
        return core.std.MaskedMerge(deband, clip, mask)

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# Filtering
fix = core.edgefixer.ContinuityFixer(depth(src, 16), [0,0,0], [0,0,0], [1,1,1], [1,1,1], [5,2,2])
denoise = mvf.BM3D(fix, sigma=2)	
dering = haf.HQDeringmod(denoise)
deband = masked_deband(dering, iterations=1, threshold = 3.6, radius = 18, grain = 1)
aa = taa(depth(deband, 16), 3)
grain = kgf.adaptive_grain(aa, 0.30, luma_scaling=8)

# Output
 
final = depth(grain, 10)
# final = core.std.Trim(final, first = 9000, last = 9800)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(src, 10)]).set_output()
