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

src = lvf.src(r'Z:\Downloads\[Beatrice-Raws] Grancrest Senki 01 [BDRip 1920x1080 HEVC FLAC].mkv')
src = fvf.Depth(src, 32)
#planes = split(src)
#y = core.resize.Spline36(planes[0], 1280, 720)
#u = core.resize.Spline36(planes[1], 1280, 720)
#v = core.resize.Spline36(planes[2], 1280, 720)
#joined = join([y,u,v])
#joined = fvf.Depth(joined,16)
#rescaled = core.placebo.Shader(joined, shader=r"C:\Users\Joel\AppData\Roaming\mpv\shaders\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
#rescaled =  core.fmtc.resample(rescaled, css = 420)
#rescaled = fvf.Depth(rescaled, 16)

aa = lvf.aa.upscaled_sraa(src)

denoise = core.knlm.KNLMeansCL(aa,a=2, h=0.7, d=3, channels="y", device_id = 0)
denoise = core.knlm.KNLMeansCL(denoise,a=1, h=0.7, d=2, channels="uv", device_id = 0)

deband = stf.masked_deband(denoise, gr = 2.0)
deband = fvf.Depth(deband, 16)

dehalo = stf.dehalo(deband)

#comp = lvf.comparison.stack_compare(rescaled, src,make_diff = True).set_output()
final = fvf.Depth(dehalo, 10)
final.set_output()
#core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(final, 10)]).set_output()