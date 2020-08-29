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
core.max_cache_size = 8 * 1024
shader = "C:/FSRCNNX_x2_16-0-4-1.glsl"
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
                                        shader = shader, filter = 'haasnsoft'), 16)
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
#src = lvf.src(r'Sakurasou no Pet na Kanojo – 01 [BDRemux 1920x1080 x264 PCM].mkv')
#yousei = lvf.src(r'src/[Yousei-raws] Sakurasou no Pet na Kanojo 01 [BDrip 1920x1080 x264 FLAC].mkv')
#yousei = core.std.Trim(yousei, first = 15000, last = 15500)
#encoded = lvf.src(r'encoded/Sakurasou no Pet na Kanojo – 01 [BDRemux 1920x1080 x264 PCM].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
rescaled = rescale(src, src)
deband = stf.masked_deband(depth(rescaled, 32), iterations=1, threshold = 2.8, radius = 24, grain = 0, lr=3,brz_a=0.025,brz_b=0.025)
aa = lvf.aa.nneedi3_clamp(depth(deband, 16))
grain = kgf.adaptive_grain(aa, 0.25, luma_scaling=8)

# Output
 
final = depth(grain, 10)
final.set_output()
#core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()
#core.std.Interleave([depth(encoded, 10),depth(yousei, 10)]).set_output()