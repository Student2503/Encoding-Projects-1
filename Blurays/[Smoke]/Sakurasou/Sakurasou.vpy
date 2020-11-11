import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
from typing import Optional
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

# Source
# src = lvf.src(r'Sakurasou no Pet na Kanojo – 01.mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)


# Filtering
rescaled = rescale(src, src)

aa = lvf.aa.nneedi3_clamp(rescaled)
dehalo = stf.dehalo(depth(aa, 16))
dehalo = depth(dehalo, 32)

deband_a = stf.masked_deband(dehalo, iterations=1, threshold = 3.0, radius = 22, grain = 0, lr=3,brz_a=0.020,brz_b=0.020)
deband_b = stf.masked_deband(dehalo, iterations=1, threshold = 2.4, radius = 26, grain = 0, lr=3,brz_a=0.030,brz_b=0.030)

deband = fvf.rfs(deband_a, deband_b, mappings="[257 339]")
deband = fvf.rfs(deband, deband_b, mappings="[5965 6015]")
deband = fvf.rfs(deband, deband_b, mappings="[9984 10128]")
deband = fvf.rfs(deband, deband_b, mappings="[10247 10586]")
deband = fvf.rfs(deband, deband_b, mappings="[18797 18894]")
deband = fvf.rfs(deband, deband_b, mappings="[20988 21633]")
deband = fvf.rfs(deband, deband_b, mappings="[24020 24257]")

grain_a = kgf.adaptive_grain(depth(deband, 16), 0.25, luma_scaling=10)
grain_b = kgf.adaptive_grain(depth(deband, 16), 0.75, luma_scaling=20)

grain = fvf.rfs(grain_a, grain_b, mappings="[257 339]")
grain = fvf.rfs(grain, grain_b, mappings="[5965 6015]")
grain = fvf.rfs(grain, grain_b, mappings="[9984 10128]")
grain = fvf.rfs(grain, grain_b, mappings="[10247 10586]")
grain = fvf.rfs(grain, grain_b, mappings="[18797 18894]")
grain = fvf.rfs(grain, grain_b, mappings="[20988 21633]")
grain = fvf.rfs(grain, grain_b, mappings="[24020 24257]")

# Output
 
final = depth(grain, 10)
# temp cuts because my encode broke midway
trimmed = core.std.Trim(final, first=31079)

trimmed.set_output()