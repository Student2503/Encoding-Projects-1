import vapoursynth as vs
core = vs.get_core()
import vapoursynth as vs
core = vs.get_core()
import lvsfunc as lvf
import fvsfunc as fvf
import kagefunc as kgf
import mvsfunc as mvf
from vsutil import *
from vsTAAmbk import TAAmbk as taa

src = lvf.src(r'Z:\list.mkv')
src = fvf.Depth(src, 16)
src1 = fvf.Depth(src, 16)
src1 = core.fmtc.resample (src1, css="444")
src1 = core.resize.Spline36(src1, 1920, 1080)

shader = core.placebo.Shader(src, shader=r"C:\Users\Joel\AppData\Roaming\mpv\shaders\FSRCNNX_x2_16-0-4-1.glsl", width = 1920, height = 1080,filter = "haasnsoft")
core.std.Interleave([shader,src1]).set_output()