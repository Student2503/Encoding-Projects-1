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
shader = "C:/FSRCNNX_x2_16-0-4-1.glsl"


def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.50) -> vs.VideoNode:
    res = get_y(clip)
    clip = core.descale.Debicubic(res, 1500, 844, 0, 1/2)

    fsrcnnx = clip.resize.Point(format=vs.YUV444P16, dither_type=None)
    fsrcnnx = depth(core.placebo.Shader(fsrcnnx, width = clip.width * 2, height = clip.height * 2,
                                        shader = shader, filter = 'haasnsoft'), 32)
    merge = fsrcnnx.resize.Spline36(width=1920, height=1080, format=vs.YUV420P16)
    merge = depth(merge, 32)
    merge = core.std.Merge(res, get_y(merge), weight=weight)

    return join([merge,plane(ref, 1), plane(ref, 2)])

# Source
# src = lvf.src(r'src/[Erai-raws] Jujutsu Kaisen - 01 [1080p][Multiple Subtitle].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, d=2, a=3, s=6, h=0.7)

aa = taa(denoise, 3)

deband = join([
             core.placebo.Deband(plane(aa, 0), grain=0, threshold=2.2, radius=18),
             core.placebo.Deband(plane(aa, 1), grain=0, threshold=3.0, radius=18),
             core.placebo.Deband(plane(aa, 2), grain=0, threshold=3.0, radius=18)
                ])    

dehalo = stf.dehalo(deband) 

grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# # Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output(1)
# final.set_output(2)
