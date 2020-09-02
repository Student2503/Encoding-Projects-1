import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsTAAmbk import TAAmbk as taa
from vsutil import *
import sys
core.max_cache_size = 8 * 1024

shader = "C:/FSRCNNX_x2_16-0-4-1.glsl"

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

def masked_deband(clip: vs.VideoNode, 
                  ref: vs.VideoNode = None,
                  show_mask: bool = False,
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  radius:  int = 15, threshold: float = 3, iterations: int = 1,
                  grain: int = 5.0, mask_denoise: Optional[float] = None, **kwargs) -> vs.VideoNode:
        deband = join([
              core.placebo.Deband(plane(clip, 0), grain=grain, iterations=iterations, threshold=threshold, radius =radius),
              core.placebo.Deband(plane(clip, 1),grain=0, iterations=iterations, threshold=threshold, radius =radius),
              core.placebo.Deband(plane(clip, 2), grain=0, iterations=iterations, threshold=threshold, radius =radius)
                 ])     
        mask = lvf.denoise.detail_mask(ref, pre_denoise=mask_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if ref is not None else False
        if show_mask:
           return mask
        return core.std.MaskedMerge(deband, clip, mask) if mask else deband


# Source
# src = lvf.src(r'Deca-Dence - 1x08 - Turbine [WEB-1080p x264 AAC] [HorribleSubs].mkv')
# encoded = lvf.src(r'Z:/testing/deca/encoded/Deca-Dence - 1x08 - Turbine [WEB-1080p x264 AAC] [HorribleSubs].mkv').set_output()
# encoded = core.std.AssumeFPS(encoded, fpsnum=24000,fpsden=1001)
# ffa = lvf.src(r'Z:/Downloads/! Nyaa/[FFA] Deca-Dence - 08 [1080p][HEVC][AAC].mkv').set_output(2)
# animetime = lvf.src(r'Z:/Downloads/! Nyaa/[Anime Time] Deca-Dence - 08 [1080p][HEVC 10bit x265][AAC][Eng Sub].mkv').set_output(3)
# akihito = lvf.src(r'Z:/Downloads/! Nyaa/[AkihitoSubs] Deca-Dence - S01E08.mkv').set_output(4)
# ember = lvf.src(r'Z:/Downloads/! Nyaa/[EMBER] Deca-Dence - 08.mkv').set_output(5)
# # arata = lvf.src(r'Z:/Downloads/! Nyaa/Deca-Dence - 08 [1080p].mkv')
# hs720 = lvf.src(r'Z:/Downloads/! Nyaa/[HorribleSubs] Deca-Dence - 08 [720p].mkv')
# hs720 = core.resize.Bicubic(hs720, 1920, 1080).set_output(6)

# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
src = depth(src, 32)

# Filtering
fix = core.edgefixer.ContinuityFixer(depth(src, 16), [1,1,1], [1,1,1], [1,1,1], [1,1,1], [5,2,2])
fix = depth(fix, 32)
rescaled = rescale(fix, fix)
denoise = core.knlm.KNLMeansCL(rescaled,h=0.4, d=2, a=4, s=3)
deband = stf.masked_deband(denoise, iterations=1, threshold = 4.0, radius = 18, grain = 1, lr=3,brz_a=0.020,brz_b=0.020)
aa = taa(depth(deband, 16), 3)
dehalo = stf.dehalo(aa)
grain = kgf.adaptive_grain(dehalo, 0.35, luma_scaling=8)

# Output
 
final = depth(grain, 10)
# final = core.std.Trim(final, first = 9000, last = 9800)
final.set_output()
# core.std.Interleave([depth(final, 10),depth(src, 10)]).set_output()
