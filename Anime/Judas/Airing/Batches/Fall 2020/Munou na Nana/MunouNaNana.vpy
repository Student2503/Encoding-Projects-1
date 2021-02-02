import vapoursynth as vs
core = vs.core

import lvsfunc as lvf
import kagefunc as kgf
import mvsfunc as mvf
import havsfunc as haf
from functools import partial
from typing import Any, Callable, Dict, Optional
from vsutil import *
import sys

# Default number of threads
DEFAULT_THREADS=24

# Default RAM allocation (in GiB)
DEFAULT_CACHE=48

# Default source path
DEFAULT_PATH = "[SubsPlease] Munou na Nana - 01 (1080p) [7BAAC64C].mkv"

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
        mask = lvf.denoise.detail_mask(clip, pre_denoise=pre_denoise, rad=lr, radc=2, brz_a=brz_a, brz_b=brz_b) if dmask is None else dmask
        if show_mask:
           return mask
        return core.std.MaskedMerge(deband, clip, depth(mask, 16)) if mask else deband
#endregion

print(f"Vapoursynth: INFO --> Beginning job - (", src_path, ")", file=sys.stderr)
src = core.lsmas.LWLibavSource(src_path).resize.Spline36(format=vs.YUV420P16)

detailmask = lvf.denoise.detail_mask(src, brz_a=0.060, brz_b=0.045, sigma=0.5)
deband_args = dict(range=14, y=24, cb=8, cr=8, grainy=4, grainc=4, output_depth=16)
planes = split(src)

planes[0] = haf.ContraSharpening(mvf.BM3D(planes[0], ref=core.bilateral.Gaussian(planes[0], sigma=1.0), sigma=2, radius1=1, profile1="lc"), planes[0])
planes[1] = core.knlm.KNLMeansCL(planes[1], d=2, a=3, s=6, h=0.6)
planes[2] = core.knlm.KNLMeansCL(planes[2], d=2, a=3, s=6, h=0.6)
denoise = join(planes)

deband = masked_deband(denoise, dmask = detailmask, **deband_args)

grain = kgf.adaptive_grain(deband, 0.20, luma_scaling=6)

final = depth(grain, 10)
final.set_output()