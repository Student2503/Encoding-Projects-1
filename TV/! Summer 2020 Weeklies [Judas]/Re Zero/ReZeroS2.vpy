import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
from nnedi3_rpow2 import znedi3_rpow2

shader  = r"FSRCNNX_x2_16-0-4-1.glsl"

core.max_cache_size = 16 * 1024

def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.5) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    res = core.resize.Point(get_y(clip))
    res = depth(res, 32)
    clip = core.descale.Debicubic(res, 1280, 720, 0, 1/2)
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
# src = lvf.src(r"Z:\Downloads\! Sonarr\imported-sonarr/[Erai-raws] Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 02 [1080p][Multiple Subtitle].mkv")
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
rescaled = rescale(src, src)
denoise = core.knlm.KNLMeansCL(rescaled,h=0.4, d=2, a=3)
deband = stf.masked_deband(denoise, iterations = 1, threshold = 3.2, radius = 18, grain = 0)
aa = taa(deband, 3, cycles = 2)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.20, luma_scaling=10)

# Output
final = depth(grain, 10)
grain.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()