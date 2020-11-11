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
import os

shader  = r"FSRCNNX_x2_16-0-4-1.glsl"

core.max_cache_size = 16 * 1024

def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.5) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    res = get_y(clip)
    clip = core.descale.Debicubic(res, 1280, 720, 0, 1/2)
    nn3 = clip.std.Transpose().znedi3.nnedi3(0, True, **args)\
          .std.Transpose().znedi3.nnedi3(0, True, **args)
    nn3 = core.resize.Spline36(nn3, src_top=.5, src_left=.5)

    fsrcnnx = clip.resize.Point(format=vs.YUV444P16, dither_type=None)
    fsrcnnx = depth(core.placebo.Shader(fsrcnnx, width = clip.width * 2, height = clip.height * 2,
                                        shader = shader, filter = 'haasnsoft'), 32)
    merge = core.std.Merge(get_y(nn3), get_y(fsrcnnx), weight=weight)
    merge = merge.resize.Spline36(width=width, height=height)  
    return join([merge,plane(ref, 1), plane(ref, 2)])

# Source
# src = lvf.src(r"Z:/Downloads/! Nyaa/[HorribleSubs] Re Zero kara Hajimeru Isekai Seikatsu - 31 [1080p].mkv")
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
fix = core.edgefixer.ContinuityFixer(src, [2,1,1], [2,1,1], [2,1,1], [2,1,1], [5,2,2])
fix = depth(fix, 32)
rescaled = rescale(fix, fix)
denoise = core.knlm.KNLMeansCL(depth(rescaled, 16),h=0.4, d=2, a=3)
deband = stf.masked_deband(denoise, iterations = 1, threshold = 3.0, radius = 18, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)
dehalo = stf.dehalo(deband)
grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()