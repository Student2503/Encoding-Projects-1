import vapoursynth as vs
core = vs.core

from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
import stolenfunc as stf
import lvsfunc as lvf
import havsfunc as haf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
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
                  show_mask: bool = False,
                  lr: int = 3, brz_a: float = 0.05, brz_b: float = 0.05, 
                  range:  int = 15, y: float = 32, cb: int = 24,
                  cr: int = 24, grainy: float = 48, grainc: float = 0, output_depth: float = 16, **kwargs) -> vs.VideoNode:
        deband = core.f3kdb.Deband(depth(clip, 16), range=range, y=y, cb=cb, cr=cr, grainy=grainy, grainc=grainc, output_depth=output_depth)     
        mask = lvf.denoise.detail_mask(ref, pre_denoise=mask_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
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
                return core.std.MaskedMerge(depth(denoise, 16), depth(clip, 16), mask) if mask else deband

            if show_mask:
                return mask

deband_args = dict(range=15, y=52, cb=38, cr=38, grainy=0, grainc=0, output_depth=16)

opstart = 4603
opend = 6761

# Source
nv = lvf.src(r'src/Jujutsu Kaisen OP YouTube.mp4')
yt = lvf.src(r'src/Jujutsu Kaisen OP Nicovideo.mp4')[0:2160]
cr = depth(lvf.src(r'src/Jujutsu Kaisen - 1x03 - Girl of Steel [WEB-1080p x264 AAC] [SubsPlease].mkv'), 16)
cr_op = core.std.Trim(cr, first=4603, last=6761)[2:]

# Averaging Nicovideo and YouTube src in 16 bit
clips = [nv, yt]
clips = [core.fmtc.bitdepth(clip, bits=16) for clip in clips]
mean = core.average.Mean(clips)[2:2159]

# Building Creditmask
denoised_cr_src = core.knlm.KNLMeansCL(cr,h=36, d=2, a=4)
cr_op_denoised = core.knlm.KNLMeansCL(cr_op,h=36, d=2, a=4)
denoised_ncop_src = core.knlm.KNLMeansCL(mean,h=36, d=2, a=4)

creditmask = vdf.dcm(source = denoised_cr_src, titles = cr_op_denoised, nc = denoised_ncop_src, start = 4603, end=6761, sw=3, sh=3).std.Trim(first=4603, last=6761)

dehardsubbed = core.std.MaskedMerge(cr_op, mean, creditmask)
src = depth(dehardsubbed, 32)

# Other masks

debandmask = depth(lvf.denoise.detail_mask(depth(src, 32), rad=3, radc=2, brz_a=0.020, brz_b=0.020), 16)
denoisemask = depth(lvf.denoise.adaptive_mask(depth(src, 32), luma_scaling=4), 16)

# Rescaling

descale = core.descale.Debicubic(depth(get_y(src), 32), 1500, 844, 1/3, 1/3)

reupscale = vdf.fsrcnnx_upscale(descale, descale.width*2, descale.height*2, shader) \
    .resize.Spline36(src.width, src.height)
rescaled = join([reupscale, plane(src, 1), plane(src, 2)])
rescaled = depth(rescaled, 16)
# Denoising

denoise_a = cooldenoise(rescaled, dmask = denoisemask, BM3D = True, fix_chroma=True,lsigma = 2, csigma = 2.5)
denoise_b = CoolDegrain(rescaled, tr=1, thsad=56, thsadc=40, bits=16, blksize=8, overlap=4)
denoise_c = cooldenoise(rescaled, dmask = denoisemask, BM3D=False, thsad=72, thsadc=48)

denoised_clips = [denoise_a, denoise_b, denoise_c] 
denoised = core.average.Mean(denoised_clips)

# Filtering

aa = lvf.aa.nneedi3_clamp(denoised, strength=1.0)
dehalo = haf.FineDehalo(aa, darkstr=0.4, brightstr=1)

deband = masked_deband(dehalo, dmask = debandmask, **deband_args)

grain = kgf.adaptive_grain(deband, 0.35, luma_scaling=4)
# Output

final = depth(grain, 10).set_output()
# core.std.Interleave([depth(cr_op, 10),depth(final, 10)]).set_output(0)
# creditmask.set_output(1)
# mean.set_output(2)