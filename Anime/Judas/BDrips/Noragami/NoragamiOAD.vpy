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
import sys
core.max_cache_size = 2048

#functions

def dehalo(clip, rep: int = 13) -> vs.VideoNode:
	# perform dehalo
    dehalo = haf.FineDehalo(clip, rx=2.2, thmi=130, thma=191, darkstr=0.5, brightstr=1.2, contra=1, showmask=0, edgeproc=0.0)
    # repair against input clip, to make sure we dont fuck it too hard
    return core.rgvs.Repair(dehalo, clip, mode=rep)      
    
    
# source
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = fvf.Depth(src, 16)

#actually filtering


denoiseY = mvf.BM3D(src, sigma=1.5)
denoiseU = core.knlm.KNLMeansCL(split(src)[1], d=2, a=4, s=5, h=0.9)
denoiseV = core.knlm.KNLMeansCL(split(src)[2], d=2, a=4, s=5, h=0.6)
denoise = join([denoiseY, denoiseU, denoiseV])


aa = taa.TAAmbk(denoise, 3)

dering = haf.HQDeringmod(aa)

dehalo = dehalo(dering)	

deband = stf.masked_deband(dehalo)

grain = kgf.adaptive_grain(deband, 1, luma_scaling=10)
    
final = fvf.Depth(grain, 10)
final.set_output()