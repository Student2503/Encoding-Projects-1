import vapoursynth as vs
core = vs.core

import lvsfunc as lvf
import kagefunc as kgf
import mvsfunc as mvf
import havsfunc as haf
import fvsfunc as fvf
from functools import partial
from typing import Any, Callable, Dict, Optional
from vsutil import *
import nnedi3_rpow2
import sys
import os
import placebo

# Default number of threads
DEFAULT_THREADS=24

# Default RAM allocation (in GiB)
DEFAULT_CACHE=48

# Default source path
DEFAULT_PATH = "src/EP 03/[SubsPlease] Dr. Stone S2 - 03 (1080p) [ED08888D].mkv"

# above three are only really used for script writing and debugging.

#region setup

print(file=sys.stderr)

# set cache
try:
    core.max_cache_size = int(max_cache_size.decode("utf-8")) * 1024
    print(f"Vapoursynth: INFO --> Allocated max {core.max_cache_size/1024}GiB of RAM", file=sys.stderr)
except ValueError:
    print(f"Vapoursynth: ERROR --> That's not a number. Allocating max {DEFAULT_CACHE}GiB of RAM", file=sys.stderr)
    core.max_cache_size = DEFAULT_CACHE * 1024
except:
    print(f"Vapoursynth: WARNING --> No max cache size set or error reading input, allocating max {DEFAULT_CACHE}GiB of RAM", file=sys.stderr)
    core.max_cache_size = DEFAULT_CACHE * 1024

try:
    core.num_threads = int(num_threads.decode("utf-8"))
    print(f"Vapoursynth: INFO --> Using {core.num_threads} threads", file=sys.stderr)
except ValueError:
    print(f"Vapoursynth: ERROR --> That's not a number. Using {DEFAULT_THREADS} threads", file=sys.stderr)
    core.num_threads = DEFAULT_THREADS
except:
    print(f"Vapoursynth: WARNING --> No thread count set or error reading input, using {DEFAULT_THREADS} threads by default", file=sys.stderr)
    core.num_threads = DEFAULT_THREADS

try:
    GPU = int(GPU.decode("utf-8"))
    print(f"Vapoursynth: INFO --> Using GPU {GPU}", file=sys.stderr)
except ValueError:
    print(f"Vapoursynth: ERROR --> That's not a number. Using GPU 0", file=sys.stderr)
    GPU = 0
except:
    print("Vapoursynth: WARNING --> No GPU specified or error reading input, using GPU 0 by default", file=sys.stderr)
    GPU = 0

try:
    src_path = src_path.decode("utf-8")
    debug = False
except:
    src_path = DEFAULT_PATH
    print(f"Vapoursynth: WARNING --> No input video specified, using default {src_path}", file=sys.stderr)
    debug = True

#endregion

#region functions
def masked_deband(clip: vs.VideoNode,
                  dmask: vs.VideoNode = None,
                  show_mask: bool = False, pre_denoise: vs.VideoNode = None, 
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  range:  int = 15, y: float = 32, cb: int = 24,
                  cr: int = 24, grainy: float = 48, grainc: float = 0, output_depth: float = 16, **kwargs) -> vs.VideoNode:
        deband = core.f3kdb.Deband(clip, range=range, y=y, cb=cb, cr=cr, grainy=grainy, grainc=grainc, output_depth=output_depth)     
        mask = lvf.denoise.detail_mask(clip, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
        if show_mask:
           return mask
        return core.std.MaskedMerge(deband, clip, depth(mask, 16)) if mask else deband


def get_descale_mask(source: vs.VideoNode, upscaled: vs.VideoNode, threshold: float = 0.015) \
    -> vs.VideoNode:
    '''
    '''
    mask = core.std.Expr([source, upscaled], f"x y - abs {threshold} < 0 1 ?")
    mask = iterate(mask, core.std.Maximum, 2)
    mask = iterate(mask, core.std.Inflate, 2)
    return mask

def znedi3_upscale(clip: vs.VideoNode, scaler: Callable[[vs.VideoNode, Any], vs.VideoNode] = core.resize.Spline36,
                   correct_shift: bool = True, **nnedi3_args)-> vs.VideoNode:
    """Classic based nnedi3 upscale.

    Args:
        clip (vs.VideoNode): Source clip.
        scaler (Callable[[vs.VideoNode, Any], vs.VideoNode], optional): Resizer used to correct the shift. Defaults to core.resize.Spline36.
        correct_shift (bool, optional): Defaults to True.

    Returns:
        vs.VideoNode: Upscaled clip.
    """
    nnargs: Dict[str, Any] = dict(nsize=4, nns=4, qual=2, pscrn=2)
    nnargs.update(nnedi3_args)
    clip = clip.std.Transpose().znedi3.nnedi3(0, True, **nnargs).std.Transpose().znedi3.nnedi3(0, True, **nnargs)
    return scaler(clip, src_top=.5, src_left=.5) if correct_shift else clip

def fsrcnnx_upscale(source: vs.VideoNode, width: int = None, height: int = 1080, shader_file: str = None,
                    downscaler: Callable[[vs.VideoNode, int, int], vs.VideoNode] = core.resize.Bicubic,
                    upscaler_smooth: Callable[[vs.VideoNode, Any], vs.VideoNode] = partial(znedi3_upscale, nsize=0, nns=3, qual=2, pscrn=1),
                    draft: bool = False)-> vs.VideoNode:
    """Upscale the given luma source clip with FSRCNNX to a given width / height and deal with the occasional ringing
       that can occur by replacing too bright pixels with a smoother nnedi3 upscale.

    Args:
        source (vs.VideoNode): Source clip.
        width (int): Target resolution width. Defaults to None.
        height (int): Target resolution height. Defaults to 1080.
        shader_file (str): Path to the FSRCNNX shader file. Defaults to None.
        luma_only (bool, optional): If process the luma only. Defaults to True.
        downscaler (Callable[[vs.VideoNode, int, int], vs.VideoNode], optional): Resizer used to downscale the upscaled clip.
                                                                                 Defaults to core.resize.Bicubic.
        upscaler_smooth (Callable[[vs.VideoNode, Any], vs.VideoNode], optional): Resizer used to replace the smoother nnedi3 upscale.
                                                                                 Defaults to partial(nnedi3_upscale, nsize=4, nns=4, qual=2, pscrn=2).
        draft (bool, optional): Allow to only output the FSRCNNX resized without the nnedi3 one. Defaults to False.

    Returns:
        vs.VideoNode: Upscaled luma clip.
    """
    if source.format.num_planes > 1:
        source = get_y(source)

    if (depth_src := get_depth(source)) != 16:
        clip = depth(source, 16)
    else:
        clip = source

    if width is None:
        width = get_w(height, clip.width/clip.height)



    fsrcnnx = placebo.shader(clip, clip.width*2, clip.height*2, shader_file)


    if draft:
        upscaled = fsrcnnx
    else:
        smooth = upscaler_smooth(clip)
        upscaled = core.std.Expr([fsrcnnx, smooth], 'x y min')


    if downscaler:
        scaled = downscaler(upscaled, width, height)
    else:
        scaled = upscaled


    if get_depth(scaled) != depth_src:
        out = depth(scaled, depth_src)
    else:
        out = scaled

    return out

def dehardsub(clip_a: vs.VideoNode, clip_b: vs.VideoNode,
              signs = [], replace_scenes = []) -> vs.VideoNode:
    hardsubmask = kgf.hardsubmask(clip_a, clip_b)
    clip = core.std.MaskedMerge(clip_a, clip_b, hardsubmask)

    hardsubmask_fade = lvf.util.quick_resample(
        clip_a, partial(kgf.hardsubmask_fades, ref=clip_b, expand_n=15, highpass=600)
    )
    clip_fade = core.std.MaskedMerge(clip_a, clip_b, hardsubmask_fade)
    clip = lvf.rfs(clip, clip_fade, ranges=signs)
    return lvf.rfs(clip, clip_b, ranges=replace_scenes)

#endregion

# Setup
print(f"Vapoursynth: INFO --> Beginning job - (", src_path, ")", file=sys.stderr)
src = core.lsmas.LWLibavSource(src_path).fmtc.bitdepth(bits=16)
AoD = core.lsmas.LWLibavSource(r'src/EP 03/Dr. STONE 2 - Stone Wars (Sub), Ep. 3-episode-3.mp4').fmtc.bitdepth(bits=16)

signs = [
    (16433, 16488), (31871, 31927), (6792, 6905), (34336, 34404), (25543, 25632)
]

replace = [
]

dehardsubbed = dehardsub(AoD, src, signs, replace)
dehardsubbed = lvf.rfs(dehardsubbed, src, [(16433, 16488)])
dehardsubbed = lvf.rfs(dehardsubbed, src, [(31871, 31927)])
dehardsubbed = lvf.rfs(dehardsubbed, src, [(25543, 25632)])

src = dehardsubbed

deband_args = dict(range=14, y=32, cb=8, cr=8, grainy=4, grainc=4, output_depth=16)
ref = core.dfttest.DFTTest(src, sigma=10, tbsize=3, opt=0)

# Filterchain
planes = split(src)
denoise = mvf.BM3D(planes[0], ref=plane(ref, 0), sigma=2.0, radius1=1, profile1="lc")
denoise = join([denoise, planes[1], planes[2]])

dehalo = haf.FineDehalo(denoise, darkstr=0.6, brightstr=1, thma=128, contra=0.0)

deband = masked_deband(dehalo, **deband_args)

grain = kgf.adaptive_grain(deband, 0.10, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()

if debug:
    try:
        from EoEfunc import debug_output
    except:
        print("Vapoursynth: WARNING --> Unable to output debug clips. Missing EoEfunc")
        exit
    debug_output(src, "src")
    debug_output(AoD, "AoD")
    debug_output(dehalo, "Dehalo")
    # debug_output(grain, "grain")
    # debug_output(rescaledm, "masked rescale")