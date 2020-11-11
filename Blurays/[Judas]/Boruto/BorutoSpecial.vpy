import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
from cooldegrain import CoolDegrain
import stolenfunc as stf
import fvsfunc as fvf
import mvsfunc as mvf
import lvsfunc as lvf
import havsfunc as haf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
import os
core.max_cache_size = 16 * 1024

def rescale(clip: vs.VideoNode, ref: vs.VideoNode, width: int = 1920, height: int = 1080, strength: float = 1) -> vs.VideoNode:
    
    args = dict(nsize=0, nns=3, qual=2, pscrn=1)
    res = core.resize.Point(get_y(clip))
    res = depth(res, 32)
    clip = core.descale.Debicubic(res, 1440, 810, 1/3, 1/3)
    nn3 = depth(depth(clip, 16).std.Transpose().nnedi3.nnedi3(0, True, **args)\
          .std.Transpose().nnedi3.nnedi3(0, True, **args),16)
    nn3 = core.resize.Spline36(nn3, src_top=.5, src_left=.5)

    nn3 = nn3.resize.Spline36(width=width, height=height)  
    return join([nn3,plane(ref, 1), plane(ref, 2)])

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
                denoise = CoolDegrain(depth(clip, 32), tr=tr, thsad=thsad, thsadc=thsadc, bits=bits, blksize=blksize, overlap=overlap)
            
            mask = lvf.denoise.adaptive_mask(depth(clip, 32), luma_scaling = luma_scaling) if dmask is None else dmask

            if fix_chroma: 
                dn1 = mvf.BM3D(plane(clip, 1), sigma=csigma)
                dn2 = mvf.BM3D(plane(clip, 2), sigma=csigma)
                merged = core.std.MaskedMerge(depth(denoise, 32), depth(clip, 32), mask)
                fixed = join([depth(merged, 16), depth(dn1, 16), depth(dn2, 16)])
                return fixed
            else:
                return core.std.MaskedMerge(depth(denoise, 32), depth(clip, 32), mask) if mask else deband

            if show_mask:
                return mask

# Source

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)

decomb = lvf.deinterlace.decomb(src, TFF = False, decimate = False, vinv = True)
vdecimate = core.vivtc.VDecimate(decomb)
src = depth(vdecimate, 16)
dmask = lvf.denoise.detail_mask(depth(src, 32), rad=3, radc=2, brz_a=0.045, brz_b=0.060)

# Filtering

rescaled = rescale(src, src)
denoised = cooldenoise(rescaled, BM3D=True, fix_chroma=True, csigma=2.5, lsigma=2.5, dmask=dmask)
aa = taa(denoised, 3)
deband = core.neo_f3kdb.Deband(aa, range=18, y=48, cb=52, cr=52, grainy=0, grainc=0, output_depth=16)
dehalo = haf.FineDehalo(deband, rx=1.5, darkstr=0, brightstr=1.0)
grain = kgf.adaptive_grain(dehalo, 0.30, luma_scaling=8)

# Output
final = depth(grain, 10)
final.set_output()