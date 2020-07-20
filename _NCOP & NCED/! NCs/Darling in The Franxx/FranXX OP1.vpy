import vapoursynth as vs
core = vs.get_core()
import lvsfunc as lvf
import fvsfunc as fvf
core.std.LoadPlugin(path=r'C:\average.dll')
import adjust
import kagefunc as kgf
import mvsfunc as mvf
from nnedi3_rpow2 import nnedi3_rpow2
import vsTAAmbk as taa
from vsutil import *
from rekt import *
import havsfunc as haf
core.max_cache_size = 12288


#remux = lvf.src(r'Z:\Encoding\Projects\NCOP & NCED\Darling in the Franxx\Openings\usbd remux.mkv')												#srcs
#remux1 = fvf.Depth(remux, 16)
#vcb = lvf.src(r'Z:\Encoding\Projects\NCOP & NCED\Darling in the Franxx\Openings\vcb studio.mkv')
#vcb = fvf.Depth(vcb, 16)
ncop = lvf.src(r'Z:\Encoding\Projects\NCOP & NCED\Darling in the Franxx\Openings\ncop m2ts.m2ts')
ncop = fvf.Depth(ncop, 16)
ncop = core.std.Trim(ncop, 24, 2181)
#chotabnc = lvf.src(r'Z:\Encoding\Projects\2.)DARLING in the FRANXX\Source Videos\Chotab\chotab op.mkv')
#chotabnc = fvf.Depth(chotabnc, 16)
#ops = [chotabnc,ncop,remux1]
out = core.resize.Spline36(ncop, matrix_in_s="170m", matrix_s="709")


ef_c = core.edgefixer.ContinuityFixer(out,[0,2,2],[0,1,1],[0,2,2],[0,1,1], 0)
ef = rektlvls(ef_c, rownum=[0, 1079], rowval=[27, 27], colnum=[0, 1, 2, 3, 1919, 1918, 1917], colval=[24, 7, 0, 5, 20, 5, -5], prot_val=0)
ef = fvf.Depth(ef, 32)

h = 810
b, c = 1/3, 1/3

planes = split(ef)

descaled = core.descale.Debicubic(planes[0], get_w(h), h, b, c)

upscaled = nnedi3_rpow2(descaled, rfactor=2, nns=4, qual=2).resize.Spline36(1920, 1080)
scaled = join([upscaled, planes[1], planes[2]])

denoise = mvf.BM3D(scaled,sigma=[2.5, 1.5], profile1="lc", depth=16)

aa = lvf.nneedi3_clamp(denoise, opencl=True)


detail_mask = lvf.denoise.detail_mask(ef, pre_denoise=None, rad=3, brz_a=0.025, brz_b=0.030) 
deband = core.placebo.Deband(aa, planes=1, iterations=1, threshold=2.0, radius=15, grain=5)
deband = core.placebo.Deband(deband, planes=2|4, iterations=1, threshold=2, radius=15, grain=0)
deband = core.std.MaskedMerge(deband, aa, fvf.Depth(detail_mask, get_depth(aa)))

grain = kgf.adaptive_grain(deband, 0.4, luma_scaling=7)

dering = haf.HQDeringmod(grain)																														# Dering
dering = fvf.Depth(dering, 10)

final = fvf.Depth(dering, 10)
#srcav = core.average.Mean(ops, output_depth = 8)																									#averaging
final.set_output()
#core.std.Interleave([final,dering]).set_output()