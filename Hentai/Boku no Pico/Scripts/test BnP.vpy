import vapoursynth as vs
core = vs.get_core()

#imports
import kagefunc as kgf
import lvsfunc as lvf
import fvsfunc as fvf
import vsutil
from nnedi3_rpow2 import nnedi3_rpow2
import mvsfunc as mvf
import vsTAAmbk as taa
import adjust
from rekt import *
import havsfunc as haf

#prep
src = lvf.src(r'D:\Projects\Boku no Pico\Source\Boku no Pico Remux.mkv')
src = fvf.Depth(src, 8)
fps = core.std.AssumeFPS(src, fpsnum=30000, fpsden=1001)

#deinterlace
deint = lvf.decomb(fps, True, decimate = False, vinv = True)
dec = core.vivtc.VDecimate(deint, cycle=5,ovr="C:\ovr.txt")
chroma = core.nnedi3.nnedi3(dec,field=1, planes=[ 1, 2])
deinterlaced = core.std.ShufflePlanes([dec, chroma, chroma], [0,1,2], colorfamily=src.format.color_family)

#chroma1 = vsutil.plane(deinterlaced, 1)
#chroma2 = vsutil.plane(deinterlaced, 2)

#dec1 = core.vivtc.VDecimate(dec, cycle=5,ovr="C:\ovr2.txt")

#upscale
dec2 = fvf.Depth(deinterlaced, 32)
#upscaled = nnedi3_rpow2(dec).resize.Spline36(1920, 1080)

# denoise 
yplane = mvf.GetPlane(dec2, 0)


#dn = mvf.BM3D(yplane, sigma=1)
dn = core.knlm.KNLMeansCL(yplane, a=2, h=0.65, d=3)
denoise = core.std.ShufflePlanes([dn, dec2, dec2], [0,1,2], colorfamily=src.format.color_family)

# Anti-Aliase
dn16 = fvf.Depth(denoise, 16)
aa  = taa.TAAmbk(dn16, aatype='Nnedi3')

#warping
#warped = core.warp.AWarpSharp2(aa)

warped = core.warp.AWarpSharp2(aa, depth=16, planes=[1,2])
warp = core.std.ShufflePlanes([aa, warped, warped], [0,1,2], colorfamily=src.format.color_family)


#deband
deband = rektdb(warp, range=16, y=40, cb=32, cr=32, grainy=4, grainc=4, output_depth=16)

#output

fin = fvf.Depth(deband, 10)
fin.set_output()

#comparision
#src1 = fvf.Depth(deband, 8)
#comp = lvf.comp(src, src1)
#core.std.Interleave([fin, deinterlaced]).set_output()
