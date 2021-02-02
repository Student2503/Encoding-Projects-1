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

# Default number of threads
DEFAULT_THREADS=24

# Default RAM allocation (in GiB)
DEFAULT_CACHE=48

# Default source path
DEFAULT_PATH = "[SRW] Kaifuku Jutsushi no Yarinaoshi (Redo of a Healer) - 01 [HIDIVE 1080p x264 AAC].mkv"

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

def get_descale_mask(source: vs.VideoNode, upscaled: vs.VideoNode, threshold: float = 0.015) \
    -> vs.VideoNode:
    '''
    '''
    mask = core.std.Expr([source, upscaled], f"x y - abs {threshold} < 0 1 ?")
    mask = iterate(mask, core.std.Maximum, 2)
    mask = iterate(mask, core.std.Inflate, 2)
    return mask

def deinterlace(clip: vs.VideoNode, TFF: bool) -> vs.VideoNode:
    """
        Experimental script for inverse telecining and deinterlacing
        This will be slower than YADIF and more resource-intensive,
        but since it involves IVTC, it's less destructive overall

        Requires VapourSynth <http://www.vapoursynth.com/doc/about.html>

        Additional dependencies:
            * NNEDI3CL <https://github.com/HomeOfVapourSynthEvolution/VapourSynth-NNEDI3CL>
            * vs-util <https://github.com/Irrational-Encoding-Wizardry/vsutil>

        :param clip:         Input clip
        :param TFF:          Top-Field-First

        :return:             IVTC'd clip with deinterlacing applied to frames with leftover combing
    """
    def deint(n, f, clip: vs.VideoNode, nn3: vs.VideoNode) -> vs.VideoNode:
        """
            Only nnedi3 frames that are marked as being combed.
            After IVTC, this should ideally only be frames that had no matching fields.
            This can mean either a failure in the fieldmatching or 60i content.

            In an ideal world I'd also have 60i content returned in 60 fps,
            but there's no real way to do so reliably here.
        """
        return nn3 if f.props['_Combed'] > 0 else clip

    down = depth(clip, 8)

    vfm = core.vivtc.VFM(down, True)
    nn3 = core.nnedi3cl.NNEDI3CL(down, True)

    deint = core.std.FrameEval(vfm, partial(deint, clip=vfm, nn3=nn3), prop_src=vfm)
    return depth(deint, clip.format.bits_per_sample)


#endregion

print(f"Vapoursynth: INFO --> Beginning job - (", src_path, ")", file=sys.stderr)

src = core.lsmas.LWLibavSource(src_path).resize.Spline36(format=vs.YUV420P16)
atx = lvf.src(r"Kaifuku Jutsushi no Yarinaoshi - 01 (АТ-х 1080p AAC).m2t")

b = 0
c = 1
taps = 5
deband_args = dict(range=14, y=24, cb=8, cr=8, grainy=4, grainc=4, output_depth=16)
ref = core.dfttest.DFTTest(src, sigma=10, tbsize=3, opt=0)

# TV a shit
atx = core.std.AssumeFPS(atx, fpsnum=30000, fpsden=1001)
atx = deinterlace(atx, TFF=True)
atx = core.resize.Spline36(atx, 1920, 1080)

# fuck ads
# atx = core.std.Trim(atx, 952, 36984)
# src = core.std.Trim(src, 300, 29587)

# Filterchain
# planes = split(src)

# denoise = mvf.BM3D(planes[0], ref=plane(ref, 0), sigma=2.0, radius1=1, profile1="lc")
# denoise = join([denoise, planes[1], planes[2]])

# deband = masked_deband(denoise, **deband_args)

# grain = kgf.adaptive_grain(deband, 0.25, luma_scaling=100)
# grain = kgf.adaptive_grain(grain, 0.15, luma_scaling=8)

# Output

debug = True
# final = depth(grain, 10)
# final.set_output(0)

if debug:
    try:
        from EoEfunc import debug_output
    except:
        print("Vapoursynth: WARNING --> Unable to output debug clips. Missing EoEfunc")
        exit
    debug_output(src, "VRV")
    debug_output(atx, "AT-X")
    # debug_output(PAS, "PAS")
    # debug_output(denoise, "denoise")
    # debug_output(deband, "deband")