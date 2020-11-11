import vapoursynth as vs
core = vs.core

import os
from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
from vsutil import *
import sys
core.max_cache_size = 16*1024

shader = r"FSRCNNX_x2_16-0-4-1.glsl"

if os.path.exists(shader) is False:
    hookpath = r"mpv/shaders/FSRCNNX_x2_16-0-4-1.glsl"
    shader = os.path.join(os.getenv("APPDATA"), hookpath)
else:
    shader = r"C:/FSRCNNX_x2_16-0-4-1.glsl"

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
    merge = merge.resize.Bicubic(width=width, height=height)  
    return join([merge,plane(ref, 1), plane(ref, 2)])

# Source
# src = lvf.src(r'Z:\Downloads\! Nyaa\[HorribleSubs] Sword Art Online - Alicization - War of Underworld - 22 [1080p].mkv')
# mtbb = lvf.src(r'Z:\Downloads\! Nyaa\[MTBB] Sword Art Onlineː Alicization - War of Underworld - 22 [CC914D04].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
aa = lvf.aa.nneedi3_clamp(src)
dehalo = stf.dehalo(aa)
deband = stf.masked_deband(dehalo, iterations=1, threshold = 2.6, radius = 22, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)
grain = kgf.adaptive_grain(deband, 0.30, luma_scaling=6)

# Output
final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(mtbb, 10)]).set_output()