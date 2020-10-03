import vapoursynth as vs
core = vs.get_core()

import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2
import havsfunc as haf
from vsTAAmbk import TAAmbk as taa
core.max_cache_size = 12288

src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Grancrest Senki\src\[Beatrice-Raws] Grancrest Senki 01 [BDRip 1920x1080 HEVC FLAC].mkv')
src = fvf.Depth(src, 16)

aa = taa(src, 3)	

#denoise1 = mvf.BM3D(fvf.Depth(aa, 32), sigma = 2)
denoise = core.knlm.KNLMeansCL(fvf.Depth(aa, 16), d=1, a=2, s=4, h=0.8)
deband = stf.masked_deband(denoise, gr = 2.0)

dehalo = stf.dehalo(fvf.Depth(deband, 16))

#comp = lvf.comparison.stack_compare(rescaled, src,make_diff = True).set_output()
#rescaled =  core.fmtc.resample(dehalo, css = 420)
#rescaled = core.placebo.Shader(rescaled, shader=r"C:\Users\Joel\AppData\Roaming\mpv\shaders\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
final = fvf.Depth(dehalo, 10)

final.set_output()

#core.std.Interleave([fvf.Depth(denoise1, 10),fvf.Depth(denoise, 10)]).set_output()