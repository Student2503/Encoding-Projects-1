import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 16 * 1024
shader  = r"FSRCNNX_x2_16-0-4-1.glsl"

def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.5) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    res = core.resize.Point(get_y(clip))
    res = depth(res, 32)
    clip = core.descale.Debicubic(res, 1280, 720, 1/3, 1/3)
    nn3 = depth(depth(clip, 16).std.Transpose().nnedi3.nnedi3(0, True, **args)\
          .std.Transpose().nnedi3.nnedi3(0, True, **args),16)
    nn3 = core.resize.Spline36(nn3, src_top=.5, src_left=.5)

    fsrcnnx = get_y(clip).resize.Point(format=vs.YUV444P16, dither_type=None)
    fsrcnnx = depth(core.placebo.Shader(fsrcnnx, width = clip.width * 2, height = clip.height * 2,
                                        shader = shader, filter = 'box'), 16)
    merge = core.std.Merge(get_y(nn3), get_y(fsrcnnx), weight=weight)
    merge = merge.resize.Bicubic(width=width, height=height)  
    return join([merge,plane(ref, 1), plane(ref, 2)])

# Source
# src = lvf.src(r'src/00003.m2ts')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# # Filtering
fix = core.edgefixer.ContinuityFixer(src, [4,1,1], [4,1,1], [4,1,1], [4,1,1], [10,4,4])
rescaled = rescale(fix, fix)
denoise = core.knlm.KNLMeansCL(rescaled,h=0.4, d=2, a=3)
deband = stf.masked_deband(denoise, iterations=1, threshold = 3.2, radius = 16, grain = 0)
aa = lvf.aa.nneedi3_clamp(deband)
grain = kgf.adaptive_grain(aa, 0.8, luma_scaling=12)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()