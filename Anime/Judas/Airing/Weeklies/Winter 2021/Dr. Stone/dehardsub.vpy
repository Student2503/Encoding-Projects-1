import vapoursynth as vs
core = vs.core
import vapoursynth as vs
import vsutil
import lvsfunc as lvf
import kagefunc as kgf
from functools import partial
from typing import Any, Callable, Dict, Optional

cr = lvf.src(r'EP 02/[Erai-raws] Dr. Stone - Stone Wars - 02 [1080p][Multiple Subtitle].mkv')
aod = lvf.src(r'EP 02/Dr. STONE 2 - Stone Wars (Sub), Ep. 2-episode-2.mp4')

trimmedcr = core.std.Trim(cr, 13899, 14005)
trimmedaod = core.std.Trim(aod, 13899, 14005)

def dehardsub(clip_a: vs.VideoNode, clip_b: vs.VideoNode,
              signs = [], replace_scenes = []) -> vs.VideoNode:
    hardsubmask = kgf.hardsubmask(clip_a, clip_b)
    clip = core.std.MaskedMerge(clip_a, clip_b, hardsubmask)

    hardsubmask_fade = lvf.util.quick_resample(
        clip_a, partial(kgf.hardsubmask_fades, ref=clip_b, expand_n=15, highpass=2350)
    )
    clip_fade = core.std.MaskedMerge(clip_a, clip_b, hardsubmask_fade)
    clip = lvf.rfs(clip, clip_fade, ranges=signs)
    return lvf.rfs(clip, clip_b, ranges=replace_scenes)

signs = [
    # (34336, 34403), (13899, 14005), (19051, 19335), (7769, 8293)
]

replace = [
]

dehard = dehardsub(trimmedaod, trimmedcr, signs, replace)
# out = lvf.diff(dehard, trimmedcr, thr=106, return_frames=True)
# print(out[1])

# ns = out[1]
replace = [
]
testmeme = kgf.hardsubmask_fades(trimmedaod, ref=trimmedcr, expand_n=17, highpass=2500).set_output()
trimmedaod.set_output(1)
trimmedcr.set_output(2)
# nd = dehardsub(dehard, trimmedcr, ns, replace)
# nd.set_output()