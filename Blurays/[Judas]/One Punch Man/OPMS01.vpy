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
                  radius:  int = 14, threshold: float = 3, iterations: int = 1,
                  grain: int = 5.0, mask_denoise: Optional[float] = None, **kwargs) -> vs.VideoNode:
        deband = join([
              core.placebo.Deband(plane(clip, 0), grain=grain, iterations=iterations, threshold=threshold, radius=radius),
              core.placebo.Deband(plane(clip, 1), grain=0, iterations=iterations, threshold=threshold, radius=radius),
              core.placebo.Deband(plane(clip, 2), grain=0, iterations=iterations, threshold=threshold, radius=radius)
                 ])    
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
                denoise = mvf.BM3D(plane(clip, 0), sigma=lsigma, pre=plane(pre_denoise, 0), profile1="lc")
                denoise = join([denoise, plane(clip, 1), plane(clip, 2)])
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
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

debandmask = depth(lvf.denoise.detail_mask(depth(src, 32), rad=2, radc=2, brz_a=0.70, brz_b=0.040), 16)
denoisemask = depth(lvf.denoise.adaptive_mask(depth(src, 32), luma_scaling=18), 16)
predenoise = core.dfttest.DFTTest(src, sigma=56, tbsize=3, opt=0)
deband_args = dict(grain=1, iterations=1, threshold=4, radius=24)

descale = core.descale.Debicubic(depth(get_y(src), 32), 1280, 720, b=1/5, c=1/2)
reupscale = vdf.nnedi3_upscale(descale, nsize=4, nns=4, qual=2, pscrn=1) \
    .resize.Spline36(src.width, src.height)
rescaled = join([depth(reupscale, 16), plane(src, 1), plane(src, 2)])

denoise_a = cooldenoise(rescaled, pre_denoise=predenoise, BM3D=True, fix_chroma=True, masked_denoise=True, lsigma=1.5, csigma=1.0, dmask=denoisemask)
denoise_b = core.dfttest.DFTTest(rescaled, sigma=2.5, tbsize=3, opt=0)
denoised_clips = [denoise_a, denoise_b]
denoise_f = core.average.Mean(denoised_clips)

deband = masked_deband(denoise_f, dmask = debandmask, **deband_args)

grain = kgf.adaptive_grain(deband, 0.30, luma_scaling=6)

final = depth(grain, 10)
final.set_output()