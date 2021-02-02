import vapoursynth as vs
core = vs.core

import lvsfunc as lvf
import kagefunc as kgf
import mvsfunc as mvf
import havsfunc as haf
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
DEFAULT_PATH = "USBD_EP1.m2ts"

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
#endregion

print(f"Vapoursynth: INFO --> Beginning job - (", src_path, ")", file=sys.stderr)
src = core.lsmas.LWLibavSource(src_path).resize.Spline36(format=vs.YUV420P16)

debandmask = lvf.denoise.detail_mask(src, rad=2, radc=2, brz_a=0.080, brz_b=0.025).std.Deflate()
denoisemask = lvf.denoise.adaptive_mask(src, luma_scaling=18)
predenoise = core.dfttest.DFTTest(src, sigma=6, tbsize=3, opt=0)
deband_args = dict(grain=1, iterations=1, threshold=3.5, radius=17)

denoise_a = cooldenoise(src, pre_denoise=predenoise, BM3D=True, fix_chroma=True, masked_denoise=True, lsigma=2, csigma=1.0, dmask=denoisemask)
denoise_b = core.dfttest.DFTTest(src, sigma=2.5, tbsize=3, opt=0)
denoised_clips = [denoise_a, denoise_b]
denoise_f = core.average.Mean(denoised_clips)

deband = masked_deband(denoise_f, dmask = debandmask, **deband_args)
aa = lvf.aa.nneedi3_clamp(deband, strength=2)
grain = kgf.adaptive_grain(aa, 0.30, luma_scaling=6)

final = depth(grain, 10)
final.set_output()