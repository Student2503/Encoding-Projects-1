import vapoursynth as vs
core = vs.core

from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
import adjust
from typing import Optional
from vsutil import *
import sys

core.max_cache_size = 8 * 1024
shader = "C:/FSRCNNX_x2_16-0-4-1.glsl"

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

def masked_deband(clip: vs.VideoNode,
                  dmask: vs.VideoNode = None,
                  show_mask: bool = False, pre_denoise: vs.VideoNode = None, 
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  range:  int = 15, y: float = 32, cb: int = 24,
                  cr: int = 24, grainy: float = 48, grainc: float = 0, output_depth: float = 16, **kwargs) -> vs.VideoNode:
        deband = core.f3kdb.Deband(clip, range=range, y=y, cb=cb, cr=cr, grainy=grainy, grainc=grainc, output_depth=output_depth)     
        mask = lvf.denoise.detail_mask(ref, pre_denoise=pre_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
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
                denoise = mvf.BM3D(clip, sigma=lsigma, pre=predenoise, profile1="lc") 
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

signs = [
    (5642, 5869), (3463, 3509), (3881, 4000), (7297, 7394), (8779, 8837), (8851, 8903), (9858, 10042), 
    (10970, 10992), (19846, 19893), (25089, 25160), (27898, 27923), (34405, 34524)
]

replace = [
]

# Source
amzn = lvf.src(r'Z:/Encoding-Projects/TV/Assault Lily - BOUQUET/src/Assault Lily - Bouquet - 01 (Amazon Prime VBR 1080p).mkv')
wakanim = lvf.src(r'Z:/Encoding-Projects/TV/Assault Lily - BOUQUET/src/Assault Lily - Bouquet - 01v2 (Wakanim DE 1080p).mkv')

# Editing wakanim clip to work

ep1_p1 = core.std.Trim(amzn, 0, 29)
ep1_p2 = core.std.Trim(wakanim, 0, 34377)
ep1_p3 = core.std.Trim(amzn, 34408, 34428)
ep1_p4 = core.std.Trim(wakanim, 34378, 34617)
ep1_p5 = core.std.Trim(amzn, 34669, 34692)

fixed_waka = ep1_p1+ep1_p2+ep1_p3+ep1_p4+ep1_p5

# dehardsubbed = dehardsub(fixed_waka, amzn, signs, replace)
# src = depth(dehardsubbed, 16)

# Filtering

# opstart = 792
# opend = 2948
# edstart = 32248
# edend = 34404
# midcardstart = 16664
# midcardend = 16855

# debandmask = depth(lvf.denoise.detail_mask(depth(src, 32), rad=3, radc=2, brz_a=0.060, brz_b=0.030), 16)
# denoisemask = depth(lvf.denoise.adaptive_mask(depth(src, 32), luma_scaling=12), 16)
# predenoise = core.dfttest.DFTTest(src, sigma=4, tbsize=3, opt=0)
# deband_args = dict(range=14, y=64, cb=32, cr=32, grainy=0, grainc=0, output_depth=16)

# # Filterchain a

# denoise_op = cooldenoise(src, pre_denoise=predenoise, BM3D=True, fix_chroma=True, masked_denoise=True, csigma=1.0, lsigma=1.0, dmask=denoisemask)
# deband_op = masked_deband(denoise_op, dmask = debandmask, **deband_args)

# grain_op = kgf.adaptive_grain(deband_op, 0.40, luma_scaling=3)

# # Filterchain b
# denoise = cooldenoise(src, pre_denoise=predenoise, BM3D=True, fix_chroma=True, masked_denoise=True, csigma=1.5, lsigma=1.0, dmask=denoisemask)
# deband = masked_deband(denoise, dmask = debandmask, **deband_args)

# aa = lvf.aa.nneedi3_clamp(deband, strength=1.5)

# grain = kgf.adaptive_grain(aa, 0.3, luma_scaling=5)

# # splicing parts 
# intro = grain[:opstart]
# op = grain_op[opstart:opend]
# part1 = grain[opend:midcardstart]
# midcards = grain_op[midcardstart:midcardend]
# part2 = grain[midcardend:edstart]
# ed = grain_op[edstart:edend]
# outro = grain_op[edend:]

# final = intro+op+part1+midcards+part2+ed+outro

# # Output
# final = depth(final, 10)
amzn.set_output(0)
wakanim.set_output(1)
# fixed_waka.set_output(2)
ep1_p3.set_output(3)
# 38523
# 317