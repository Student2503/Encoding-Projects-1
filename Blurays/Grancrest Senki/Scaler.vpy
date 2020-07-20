import vapoursynth as vs
core = vs.get_core()

import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2

src = fvf.Depth(lvf.src(r'Z:\filtered.mkv'), 16)
comp= lvf.src(r'Z:\Encoding\Projects\Ongoing\Grancrest Senki\src\[Beatrice-Raws] Grancrest Senki 01 [BDRip 1920x1080 HEVC FLAC].mkv')

rescaled = core.placebo.Shader(src, shader=r"C:\Users\Joel\AppData\Roaming\mpv\shaders\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
rescaled =  core.fmtc.resample(rescaled, css = 420)

final = fvf.Depth(rescaled, 10)
final.set_output()
#core.std.Interleave([fvf.Depth(final, 10),fvf.Depth(comp, 10)]).set_output()
