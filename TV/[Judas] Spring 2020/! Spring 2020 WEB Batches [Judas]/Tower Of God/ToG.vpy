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
core.max_cache_size = 8096

#src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Tower of God\src\Tower of God - 01x12 - Underwater Hunt (Part Two) [WEB-1080p v2 x264 AAC] [Erai-raws].mkv')
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
upscaled = core.placebo.Shader(joined, shader=r"C:\Users\Joel\AppData\Roaming\mpv\shaders\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
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

def upscaled_sraa(clip: vs.VideoNode,
                  rfactor: float = 1.5,
                  rep: Optional[int] = None,
                  width: Optional[int] = None, height: Optional[int] = None,
                  downscaler: Callable[[vs.VideoNode, int, int], vs.VideoNode]
                  = core.resize.Spline36,
                  **eedi3_args: Any) -> vs.VideoNode:
    """
    A function that performs an upscaled single-rate AA to deal with heavy aliasing and broken-up lineart.
    Useful for Web rips, where the source quality is not good enough to descale,
    but you still want to deal with some bad aliasing and lineart.

    Original function written by Zastin, heavily modified by LightArrowsEXE.

    Alias for this function is `lvsfunc.sraa`.

    Dependencies: fmtconv, rgsf (optional: 32 bit clip), vapoursynth-eedi3, vapoursynth-nnedi3

    :param clip:            Input clip
    :param rfactor:         Image enlargement factor. 1.3..2 makes it comparable in strength to vsTAAmbk
                            It is not recommended to go below 1.3 (Default: 1.5)
    :param rep:             Repair mode (Default: None)
    :param width:           Target resolution width. If None, determine from `height`
    :param height:          Target resolution height (Default: ``clip.height``)
    :param downscaler:      Resizer used to downscale the AA'd clip
    :param kwargs:          Arguments passed to znedi3 (Default: alpha=0.2, beta=0.6, gamma=40, nrad=2, mdis=20)

    :return:                Antialiased and optionally rescaled clip
    """
    if clip.format is None:
        raise ValueError("upscaled_sraa: 'Variable-format clips not supported'")

    luma = get_y(clip)

    nnargs: Dict[str, Any] = dict(nsize=0, nns=4, qual=2)
    # TAAmbk defaults are 0.5, 0.2, 20, 3, 30
    eeargs: Dict[str, Any] = dict(alpha=0.2, beta=0.6, gamma=40, nrad=2, mdis=20)
    eeargs.update(eedi3_args)

    if rfactor < 1:
        raise ValueError("upscaled_sraa: '\"rfactor\" must be above 1'")

    ssw = round(clip.width * rfactor)
    ssh = round(clip.height * rfactor)

    while ssw % 2:
        ssw += 1
    while ssh % 2:
        ssh += 1

    if height is None:
        height = clip.height
    if width is None:
        if height != clip.height:
            width = get_w(height, aspect_ratio=clip.width / clip.height)
        else:
            width = clip.width

    # Nnedi3 upscale from source height to source height * rounding (Default 1.5)
    up_y = core.nnedi3.nnedi3(luma, 0, 1, 0, **nnargs)
    up_y = core.resize.Spline36(up_y, height=ssh, src_top=.5)
    up_y = core.std.Transpose(up_y)
    up_y = core.nnedi3.nnedi3(up_y, 0, 1, 0, **nnargs)
    up_y = core.resize.Spline36(up_y, height=ssw, src_top=.5)

    # Single-rate AA
    aa_y = core.eedi3m.EEDI3(up_y, 0, 0, 0, sclip=core.nnedi3.nnedi3(up_y, 0, 0, 0, **nnargs), **eeargs)
    aa_y = core.std.Transpose(aa_y)
    aa_y = core.eedi3m.EEDI3(aa_y, 0, 0, 0, sclip=core.nnedi3.nnedi3(aa_y, 0, 0, 0, **nnargs), **eeargs)

    # Back to source clip height or given height
    scaled = downscaler(aa_y, width, height)

    if rep:
        scaled = util.pick_repair(scaled)(scaled, luma.resize.Bicubic(width, height), mode=rep)

    if clip.format.num_planes == 1:
        return scaled
    return join([scaled, plane(clip, 1), plane(clip, 2)])

#filtering
denoise = mvf.BM3D(upscaled, sigma = 1)

dehalo = haf.YAHR(depth(denoise, 16), blur=1, depth=32)
dehalo = stf.dehaloed(depth(dehalo, 16))
masked_dehalo = core.std.MaskedMerge(depth(denoise, 16), dehalo, depth(halos, 16))

aa = upscaled_sraa(depth(masked_dehalo, 32))	

deband = masked_deband(depth(aa, 32))

grain = kgf.adaptive_grain(deband, 0.6, luma_scaling=1)

final = fvf.Depth(grain, 10)
final.set_output()
#core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()