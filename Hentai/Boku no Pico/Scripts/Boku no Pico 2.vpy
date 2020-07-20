import vapoursynth as vs
core = vs.get_core()
# import kagefunc as kgf
import lvsfunc as lvf
import fvsfunc as fvf
import vsutil
# from nnedi3_rpow2 import nnedi3_rpow2
import mvsfunc as mvf
# import muvsfunc as muf
import vsTAAmbk as taa
# import adjust
from rekt import *
# import havsfunc as haf
core.max_cache_size = 8096

# Input
src = lvf.src(r'D:\Projects\Boku no Pico\Source\Boku no Pico Remux.mkv')
src = fvf.Depth(src, 8)
src = core.std.AssumeFPS(src, fpsnum=30000, fpsden=1001)

nnedi3 = core.nnedi3cl.NNEDI3CL(src, 1,planes=[0,1,2], device=0, info = False)                                       # Deinterlacing
decomb = lvf.decomb(nnedi3, False, decimate = False, vinv = True)
vdecimate = core.vivtc.VDecimate(decomb, cycle=5)

deinterlaced = fvf.Depth(vdecimate, 16)

luma = core.knlm.KNLMeansCL(deinterlaced,a=2, h=0.7, d=3, channels="y")                                             # Denoising
chroma = core.knlm.KNLMeansCL(luma,a=1, h=0.7, d=2, channels="uv")

aa = fvf.Depth(chroma, 16)                                                                                          # Anti-aliasing
aa  = taa.TAAmbk(aa, aatype='Nnedi3')

awarpsharp = core.warp.AWarpSharp2(aa, depth=16, planes=[1,2])                                                      # Sharpening chroma
warped = core.std.ShufflePlanes([aa, awarpsharp, awarpsharp], [0,1,2], colorfamily=src.format.color_family)

warped = fvf.Depth(warped, 8)

deband = rektdb(warped, range=16, y=40, cb=32, cr=32, grainy=4, grainc=4, output_depth=16)                          # Debanding

final = fvf.Depth(deband, 10)                                                                                       
comp =  fvf.Depth(deband, 16)

final.set_output()                                                                                                  # Output


#lvf.comp(comp,deinterlaced).set_output()                                                                           # Comparisions
#core.std.Interleave([comp, deinterlaced]).set_output()
