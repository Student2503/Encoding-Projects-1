import vapoursynth as vs
core = vs.core

import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
from vsutil import *
import havsfunc as haf
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2
import vsTAAmbk as taa
from typing import Optional
import sys
#functions
def upscaled_sraa(clip: vs.VideoNode,
                  rfactor: float = 1.5,
                  rep: Optional[int] = None,
                  h: Optional[int] = None, ar: Optional[float] = None,
                  sharp_downscale: bool = False) -> vs.VideoNode:
        
    if clip.format is None:
        raise ValueError("upscaled_sraa: 'Variable-format clips not supported'")

    luma = get_y(clip)

    nnargs: Dict[str, Any] = dict(nsize=0, nns=4, qual=2)
    # TAAmbk defaults are 0.5, 0.2, 20, 3, 30
    eeargs: Dict[str, Any] = dict(alpha=0.2, beta=0.6, gamma=40, nrad=2, mdis=20)

    ssw = round(clip.width * rfactor)
    ssh = round(clip.height * rfactor)

    while ssw % 2:
        ssw += 1
    while ssh % 2:
        ssh += 1

    if h:
        if not ar:
            ar = clip.width / clip.height
        w = get_w(h, aspect_ratio=ar)
    else:
        w, h = clip.width, clip.height

    # Nnedi3 upscale from source height to source height * rounding (Default 1.5)
    up_y = core.nnedi3.nnedi3(luma, 0, 1, 0, **nnargs)
    up_y = core.resize.Spline36(up_y, height=ssh, src_top=.5)
    up_y = core.std.Transpose(up_y)
    up_y = core.nnedi3.nnedi3(up_y, 0, 1, 0, **nnargs)
    up_y = core.resize.Spline36(up_y, height=ssw, src_top=.5)

    # Single-rate AA
    aa_y = core.eedi3m.EEDI3(up_y, 0, 0, 0, sclip=core.nnedi3.nnedi3(up_y, 0, 0, 0, **nnargs), **eeargs)
    aa_y = core.std.Transpose(aa_y)
    aa_y = core.eedi3m.EEDI3(aa_y, 0, 0, 0, sclip=core.nnedi3.nnedi3(aa_y, 0, 0, 0, **nnargs), **eeargs)

    # Back to source clip height or given height
    scaled = (core.fmtc.resample(aa_y, w, h, kernel='gauss', invks=True, invkstaps=2, taps=1, a1=32)
              if sharp_downscale else core.resize.Spline36(aa_y, w, h))

    if rep:
        scaled = util.pick_repair(scaled)(scaled, luma.resize.Spline36(w, h), rep)
    return scaled if clip.format.color_family is vs.GRAY else core.std.ShufflePlanes([scaled, clip], [0, 1, 2], vs.YUV)


def dehalo(clip, rep: int = 13) -> vs.VideoNode:
	# perform dehalo
    dehalo = haf.FineDehalo(clip, rx=2.2, thmi=130, thma=191, darkstr=0.5, brightstr=1.2, contra=1, showmask=0, edgeproc=0.0)
    # repair against input clip, to make sure we dont fuck it too hard
    return core.rgvs.Repair(dehalo, clip, mode=rep)      
    
    
# source
src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Noragami\src\haranatsu\[Harunatsu] Noragami Aragoto OAD - 02 [DVD 576p-AAC][EDD8EEFB].mkv')
# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
src = fvf.Depth(src, 16)
src = core.resize.Spline36(src, matrix_in_s="709", matrix_s="170m")

#actually filtering


denoise = mvf.BM3D(src, sigma=1.5)

aa = taa.TAAmbk(denoise, 3)

dering = haf.HQDeringmod(aa)

dehalo = dehalo(dering)	

deband = stf.masked_deband(depth(dehalo,16))

grain = kgf.adaptive_grain(deband, 1, luma_scaling=10)
    
final = fvf.Depth(grain, 10)
final.set_output()
deband.set_output()

#core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(final, 10)]).set_output()