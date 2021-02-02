import vapoursynth as vs
core = vs.core

import lvsfunc as lvf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
import havsfunc as haf
from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
from vsutil import *
from vsTAAmbk import TAAmbk as taa
import nnedi3_rpow2
import sys

# Default number of threads
DEFAULT_THREADS=8

# Default RAM allocation (in GiB)
DEFAULT_CACHE=8

# above three are only really used for script writing and debugging.

#region functions

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

def masked_deband(clip: vs.VideoNode,
                  dmask: vs.VideoNode = None,
                  show_mask: bool = False, pre_denoise: vs.VideoNode = None, 
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  range:  int = 15, y: float = 32, cb: int = 24,
                  cr: int = 24, grainy: float = 48, grainc: float = 0, output_depth: float = 16, **kwargs) -> vs.VideoNode:
        deband = core.f3kdb.Deband(clip, range=range, y=y, cb=cb, cr=cr, grainy=grainy, grainc=grainc, output_depth=output_depth)     
        mask = lvf.denoise.detail_mask(clip, pre_denoise=pre_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
        if show_mask:
           return mask
        return core.std.MaskedMerge(deband, clip, depth(mask, 16)) if mask else deband
#endregion

print(f"Vapoursynth: INFO --> Beginning job - (", src_path, ")", file=sys.stderr)
src = core.lsmas.LWLibavSource(src_path)
# src = lvf.src(r"[SubsPlease] Kimi to Boku no Saigo no Senjou, Arui wa Sekai ga Hajimaru Seisen - 03 (1080p) [4C7BE7EB].mkv")

b = 0
c = 1/2
src = depth(src, 16)

debandmask = lvf.denoise.detail_mask(src, brz_a=0.050, brz_b=0.028, sigma=0.5)
deband_args = dict(range=14, y=28, cb=8, cr=8, grainy=0, grainc=0, output_depth=16)

descale = core.descale.Debicubic(depth(get_y(src), 32), 1440, 810, b=b, c=c)
reupscale = znedi3_upscale(depth(descale, 16), nsize=0, nns=3, qual=2, pscrn=1) \
    .resize.Spline36(src.width, src.height)
rescaled = join([reupscale, plane(src, 1), plane(src, 2)])

planes = split(rescaled)

ref0 = core.bilateral.Gaussian(planes[0], sigma=0.5)
ref1 = core.dfttest.DFTTest(planes[1], sigma=0.5)
ref2 = core.dfttest.DFTTest(planes[2], sigma=0.5)
ref = join([ref0, ref1, ref2])
denoise = mvf.BM3D(rescaled, ref=ref, profile1="lc", sigma=1.0)

deband = masked_deband(denoise, dmask = debandmask, **deband_args)

aa = taa(deband, 3)

grain = kgf.adaptive_grain(aa, 0.20, luma_scaling=50)
grain = kgf.adaptive_grain(grain, 0.15, luma_scaling=4)

final = depth(grain, 10)
final.set_output()