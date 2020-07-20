import vapoursynth as vs
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
from vsTAAmbk import TAAmbk
core = vs.core

src = lvf.src(r'D:\Encoding Projects Temp\sonohanabira.mkv')

#32 bit
src = fvf.Depth(src, 32)
src16 = fvf.Depth(src, 16)
denoise = fvf.Depth(core.knlm.KNLMeansCL(src, d=3, a=2, h=0.4), 16)

deband = core.f3kdb.Deband(denoise, range=15, y=40, cb=32, cr=32, grainy=0, grainc=0, output_depth=16)

l_mask = kgf.retinex_edgemask(src16)

aa = TAAmbk(fvf.Depth(src, 16), aatype='Nnedi3', repair=2)

aa = core.std.MaskedMerge(deband, aa, l_mask)

grain = kgf.adaptive_grain(aa, 0.1, luma_scaling=8)

out = fvf.Depth(grain, 10)
out.set_output()