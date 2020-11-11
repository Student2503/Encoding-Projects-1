import vapoursynth as vs
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
import mvsfunc as mvf
from nnedi3_rpow2CL import nnedi3_rpow2CL
from vsutil import join, split
import vsTAAmbk as taa
from vsutil import *
from rekt import *
import havsfunc as haf
from nnedi3_resample import *
import lostfunc as lof
core = vs.core
core.max_cache_size = 3956

def _fix_lineart(clip) -> vs.VideoNode:
    dehalo = haf.FineDehalo(clip, rx=2.2, thmi=91, thma=191, darkstr=0, brightstr=1.6, contra=1)
    dering = haf.EdgeCleaner(dehalo, strength=6, rmode=13, smode=1, hot=True)
    return core.rgvs.Repair(dering, clip, 13)

src = lvf.src(r"00001.m2ts")
src =  src[24:]

src = core.resize.Spline36(src, matrix_in_s="170m", matrix_s="709")

ef_c = core.edgefixer.ContinuityFixer(src,[0,2,2],[0,1,1],[0,2,2],[0,1,1], 0)
ef_l = rektlvls(ef_c, rownum=[0, 1079], rowval=[27, 27], colnum=[0, 1, 2, 3, 1919, 1918, 1917], colval=[24, 7, 0, 5, 20, 5, -5], prot_val=0)


ef = fvf.Depth(ef_l, 32)                                            

b, c = 0, 1/2

planes = split(ef)

descaled = core.descale.Debicubic(planes[0], 1440, 810, b, c)

descaled = mvf.BM3D(descaled,sigma=1.5, profile1="lc")


upscaled = nnedi3_resample(descaled, planes[0].width, planes[0].height, kernel='gauss', invks=True, invkstaps=2, taps=1, a1=32, nns=4, qual=2, pscrn=4).resize.Spline36(1920, 1080)
scaled = join([upscaled, planes[1], planes[2]])


denoise = mvf.BM3D(scaled,sigma=[0, 0.8, 0.8], depth=16)

aa = lvf.nneedi3_clamp(denoise, opencl=True)

dehalo = _fix_lineart(aa)


detail_mask = kgf.retinex_edgemask(dehalo)
deband = core.placebo.Deband(dehalo, planes=1, iterations=1, threshold=3.5, radius=14, grain=10)
deband = core.placebo.Deband(deband, planes=2|4, iterations=1, threshold=2.5, radius=14, grain=0)
merged = core.std.MaskedMerge(deband, dehalo, detail_mask)


grain = kgf.adaptive_grain(merged, 1.5, luma_scaling=3) 


final = grain 
final = fvf.Depth(final, 10)
final.set_output()