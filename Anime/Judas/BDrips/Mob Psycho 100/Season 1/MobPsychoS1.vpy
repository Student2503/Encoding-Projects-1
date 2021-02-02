import vapoursynth as vs
core = vs.core
import os
from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
import havsfunc as haf
from vsTAAmbk import TAAmbk as taa
from typing import Optional
from vsutil import *
import sys

core.num_threads = 20
core.max_cache_size = 64 * 1024

def masked_deband(clip: vs.VideoNode,
                  dmask: vs.VideoNode = None,
                  show_mask: bool = False,
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  range:  int = 15, y: float = 32, cb: int = 24,
                  cr: int = 24, grainy: float = 48, grainc: float = 0, output_depth: float = 16, **kwargs) -> vs.VideoNode:
        deband = core.f3kdb.Deband(depth(clip, 16), range=range, y=y, cb=cb, cr=cr, grainy=grainy, grainc=grainc, output_depth=output_depth)     
        mask = lvf.denoise.detail_mask(clip, pre_denoise=mask_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
        if show_mask:
           return mask
        return core.std.MaskedMerge(deband, clip, mask) if mask else deband

def cooldenoise(clip: vs.VideoNode,
                dmask: vs.VideoNode = None,
                BM3D: bool = False,
                fix_chroma: bool = False,
                show_mask: bool = False,
                tr: int = 1, thsad: float = 48, thsadc: float = 32, 
                blksize:  float = 8, overlap: float = 4, bits: int = 16, luma_scaling: float = 8.0, csigma: float = 2.5, lsigma: float=1) -> vs.VideoNode:
            if BM3D:
                denoise = mvf.BM3D(clip, sigma=lsigma) 
            else:                
                denoise = CoolDegrain(depth(clip, 16), tr=tr, thsad=thsad, thsadc=thsadc, bits=bits, blksize=blksize, overlap=overlap)
            
            mask = lvf.denoise.adaptive_mask(depth(clip, 32), luma_scaling = luma_scaling) if dmask is None else dmask

            if fix_chroma: 
                dn1 = mvf.BM3D(plane(clip, 1), sigma=csigma)
                dn2 = mvf.BM3D(plane(clip, 2), sigma=csigma)
                merged = core.std.MaskedMerge(denoise, clip, mask)
                fixed = join([depth(merged, 16), depth(dn1, 16), depth(dn2, 16)])
                return fixed
            else:
                return core.std.MaskedMerge(depth(denoise, 32), depth(clip, 32), mask) if mask else deband

            if show_mask:
                return mask

deband_args = dict(range=16, y=52, cb=32, cr=32, grainy=0, grainc=0, output_depth=16)

# Source
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)

debandmask = depth(lvf.denoise.detail_mask(depth(src, 32), rad=3, radc=2, brz_a=0.040, brz_b=0.050), 16)
denoisemask = depth(lvf.denoise.adaptive_mask(src, luma_scaling=8), 16)

# Filtering
descale = core.descale.Debicubic(depth(get_y(src), 32), 1280, 720, 0, 1/2)

reupscale = vdf.nnedi3_upscale(descale, nsize=4, nns=4, qual=2, pscrn=1) \
    .resize.Spline36(src.width, src.height)
reupscale = depth(reupscale, 8)
rescaled = join([depth(reupscale, 8), plane(src, 1), plane(src, 2)])

deband = masked_deband(depth(rescaled, 16), dmask = debandmask, **deband_args)
denoise = cooldenoise(deband, BM3D=True, fix_chroma=True, csigma=0.5, lsigma=1.0, dmask=denoisemask, bits = 16)

aa = taa(denoise, 3)
dehalo = haf.FineDehalo(aa, rx=2, darkstr=0, brightstr=1.0)
grain = kgf.adaptive_grain(dehalo, 0.35, luma_scaling=6)

# Output
final = depth(grain, 10)
final.set_output()