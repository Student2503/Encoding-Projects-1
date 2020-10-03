import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
from vsTAAmbk import TAAmbk as taa
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 8 * 1024

shader = "C:/FSRCNNX_x2_16-0-4-1.glsl"

def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.5) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    res = get_y(clip)
    clip = core.descale.Debicubic(res, 1488, 837, 0, 1/2)
    nn3 = clip.std.Transpose().znedi3.nnedi3(0, True, **args)\
          .std.Transpose().znedi3.nnedi3(0, True, **args)
    nn3 = core.resize.Spline36(nn3, src_top=.5, src_left=.5)

    fsrcnnx = clip.resize.Point(format=vs.YUV444P16, dither_type=None)
    fsrcnnx = depth(core.placebo.Shader(fsrcnnx, width = clip.width * 2, height = clip.height * 2,
                                        shader = shader, filter = 'haasnsoft'), 32)
    merge = core.std.Merge(get_y(nn3), get_y(fsrcnnx), weight=weight)
    merge = merge.resize.Spline36(width=width, height=height)  
    return join([merge,plane(ref, 1), plane(ref, 2)])

def upscale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, weight: float = 0.5) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    clip = get_y(clip)
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
src = lvf.src(r'src/00001.m2ts')
# HS = lvf.src(r'Z:\Downloads\! Nyaa\[HorribleSubs] Dokyuu Hentai HxEros - 01 [1080p].mkv')
# HS = HS[289:]

# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)

# Filtering
src = depth(src, 32)

OP_credits = core.std.Trim(src, last=1881)
part_1 = core.std.Trim(src, first=1882, last=14384)
midcard = core.std.Trim(src, first=14385, last=14504)
part_2 = core.std.Trim(src, first=14505, last=31767)
ED = core.std.Trim(src, first=31768)

# Rescaling

rescale1 = rescale(part_1, part_1)
rescale2 = rescale(part_2, part_2)

rescaled = OP_credits + rescale1 + midcard + part_2 + ED

# mask = core.std.Expr([src, rescaled], 'x y - abs').std.Binarize(0.05)
# mask = iterate(mask, core.std.Maximum, 2)
# mask = iterate(mask, core.std.Inflate, 2)
# mask.set_output(5)

denoised = core.knlm.KNLMeansCL(rescaled, d=2, a=3, s=6, h=1.0, channels="UV")

# aa = lvf.aa.nneedi3_clamp(rescaled)
aa_1 = lvf.aa.nneedi3_clamp(denoised)
aa_2 = lvf.aa.upscaled_sraa(denoised)

aa = fvf.rfs(aa_1, aa_2, mappings="[0 1881]")
aa = fvf.rfs(aa_1, aa_2, mappings="[14385 14504]")
aa = fvf.rfs(aa_1, aa_2, mappings="[31768 34046]")

deband = stf.masked_deband(aa, iterations=1, threshold = 3.0, radius = 18, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)

dehalo = stf.dehalo(depth(deband, 16))

grain = kgf.adaptive_grain(dehalo, 0.25, luma_scaling=8)

# Output

final = depth(grain, 10)
final.set_output()
# core.std.Interleave([depth(src, 8),depth(src, 8)]).set_output()
# core.std.Interleave([depth(src, 8),depth(upaa, 8)]).set_output(1)
# core.std.Interleave([depth(src, 8),depth(nneediaa, 8)]).set_output(2)
# core.std.Interleave([depth(src, 8),depth(taa, 8)]).set_output(3)
# core.std.Interleave([depth(src, 8),depth(rescaled, 8)]).set_output(4)


# lvf.comparison.tvbd_diff(websrc, src,return_array=True).set_output()

# 16892 - Fade
# 20464 - Noisy shite
# 22026 - Banding
# 31719 - Heavy detail/light
# 32078 - Light flares and shit
# 108   - some bands and chance of lost detail
# 31935 - near invisible lines