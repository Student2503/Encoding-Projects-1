import vapoursynth as vs
core = vs.core

from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
import lvsfunc as lvf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 4 * 1024

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

def cooldenoise(clip: vs.VideoNode,
                dmask: vs.VideoNode = None,
                pre_denoise: vs.VideoNode = None,
                BM3D: bool = False,
                fix_chroma: bool = False,
                masked_denoise: bool = True,
                show_mask: bool = False,
                tr: int = 1, thsad: float = 48, thsadc: float = 32, 
                blksize:  float = 8, overlap: float = 4, bits: int = 32, luma_scaling: float = 8.0, csigma: float = 2.5, lsigma: float=1) -> vs.VideoNode:
                
            mask = lvf.denoise.adaptive_mask(clip, luma_scaling = luma_scaling) if dmask is None else dmask

            if BM3D == True:
                denoise = mvf.BM3D(clip, sigma=lsigma, pre=pre_denoise, profile1="lc") 
            else:                
                denoise = CoolDegrain(clip, tr=tr, thsad=thsad, thsadc=thsadc, bits=32, blksize=blksize, overlap=overlap)
            
            if masked_denoise == True:
                denoised = core.std.MaskedMerge(denoise, clip, mask)
            else:
                denoised = denoise

            if fix_chroma == True:
                dn1 = mvf.BM3D(plane(clip, 1), sigma=csigma)
                dn2 = mvf.BM3D(plane(clip, 2), sigma=csigma)
                chroma = join([denoised, dn1, dn2])
                return chroma
            else:
                return denoised

            if show_mask == True:
                return mask

# src1 = lvf.src(r'src/00008.m2ts')
src = lvf.src(r'src/[anti-raws]One Punch Man ep.01[BDRemux].mkv')
src = depth(src, 16)

debandmask = depth(lvf.denoise.detail_mask(depth(src, 32), rad=2, radc=2, brz_a=0.60, brz_b=0.030), 16)
denoisemask = depth(lvf.denoise.adaptive_mask(depth(src, 32), luma_scaling=16), 16)
predenoise = core.dfttest.DFTTest(src, sigma=6, tbsize=3, opt=0)
deband_args = dict(range=14, y=28, cb=8, cr=8, grainy=0, grainc=0, output_depth=16)

descale = core.descale.Debicubic(depth(get_y(src), 32), 1280, 720, b=1/5, c=1/2)
reupscale = vdf.nnedi3_upscale(descale, nsize=4, nns=4, qual=2, pscrn=1) \
    .resize.Spline36(src.width, src.height)
rescaled = join([depth(reupscale, 16), plane(src, 1), plane(src, 2)])

# denoise_a = cooldenoise(rescaled, pre_denoise=predenoise, BM3D=True, fix_chroma=True, masked_denoise=True, csigma=0.8, lsigma=1.0, dmask=denoisemask)
# denoise_b = core.dfttest.DFTTest(rescaled, sigma=1, tbsize=3, opt=0)
# denoised_clips = [denoise_a, denoise_b]
# denoised = core.average.Mean(denoised_clips)

# deband = masked_deband(denoised, dmask = debandmask, **deband_args)

# aa = lvf.aa.nneedi3_clamp(deband, strength=2)

# grain = kgf.adaptive_grain(aa, 0.2, luma_scaling=8)

# final = depth(grain, 10)

src.set_output(0)
debandmask.set_output(1)
denoisemask.set_output(2)
predenoise.set_output(3)

core.std.Interleave([depth(src, 8), depth(rescaled, 8)]).set_output(4)

# Banding = 12901 (interleaved)