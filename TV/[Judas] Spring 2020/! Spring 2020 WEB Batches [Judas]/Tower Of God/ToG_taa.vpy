import vapoursynth as vs
core = vs.get_core()
import lvsfunc as lvf
import fvsfunc as fvf
import kagefunc as kgf
import mvsfunc as mvf
import havsfunc as haf
from vsutil import *
from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
from nnedi3_rpow2 import *
from typing import Optional
import sys

#src = lvf.src(r'Z:\Encoding\Projects\Ongoing\ToG\src\Tower of God - 01x12 - Underwater Hunt (Part Two) [WEB-1080p v2 x264 AAC] [Erai-raws].mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 32)
#Judas = lvf.src(r'Z:\Encoding\Projects\Experiments\Tower of God\src\[Judas] Kami no Tou - S01E08.mkv')

# scaling
planes = split(src)
y = core.descale.Debicubic(planes[0], 1476, 830, 0, 1/2)
resized = core.resize.Bicubic(src, 1476, 830)
replanes = split(resized)

joined = join([y,replanes[1],replanes[2]])
joined = depth(joined,16)
upscaled = core.placebo.Shader(joined, shader=r"path\to\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
upscaled = core.fmtc.resample(upscaled, css = 420)
upscaled = depth(upscaled, 32)
# dehalo masking
mask = core.std.Sobel(src, 0)
luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
mask_outer = iterate(luma, core.std.Maximum, 2)
mask_inner = iterate(mask_outer, core.std.Minimum, 3)
halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
halos = iterate(halos, core.std.Minimum, 1)

# Functions
def masked_deband(clip: vs.VideoNode, 
                  ref: vs.VideoNode = None,
                  show_mask: bool = False,
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  gr: int = 5.0, mask_denoise: Optional[float] = None, **kwargs) -> vs.VideoNode:
    
     

    debargs = dict(radius=15, threshold=3, iterations=1)
    debargs.update(kwargs)

    deband = join([    
              core.placebo.Deband(plane(clip, 0), grain=gr, **debargs),
              core.placebo.Deband(plane(clip, 1),grain=0, **debargs),
              core.placebo.Deband(plane(clip, 2), grain=0, **debargs)
                 ])     
    mask = lvf.denoise.detail_mask(ref, pre_denoise=mask_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if ref is not None else False
    if show_mask:
        return mask
    return core.std.MaskedMerge(deband, clip, mask) if mask else deband

#filtering
denoise = mvf.BM3D(upscaled, sigma = 1)

dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
dehalo = stf.dehaloed(depth(dehalo, 16))
masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), dehalo, depth(halos, 16))

aa = taa(depth(masked_dehalo, 16), 3)	

deband = masked_deband(depth(aa, 32))

grain = kgf.adaptive_grain(deband, 0.6, luma_scaling=1)

final = fvf.Depth(grain, 10)
final.set_output()
#core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()