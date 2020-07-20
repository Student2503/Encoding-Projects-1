import vapoursynth as vs
core = vs.get_core()
import lvsfunc as lvf
import kagefunc as kgf
from nnedi3_rpow2 import nnedi3_rpow2
import fvsfunc as fvf
import mvsfunc as mvf
import vsutil as vsutil
from descale import Debicubic
bdsrc = lvf.src(r'D:\Projects\2.)DARLING in the FRANXX\Source Videos\Remux\DARLING in the FRANXX S01E02 2018 1080p BluRay REMUX AVC TRUEHD 5.1 Dual Audio-ZR-.mkv')
dvdsrc = lvf.src(r'D:\Projects\NCOP & NCED\Darling in the Franxx\XX-me - DARLING in the FRANXX Ending Collection vol.1 (2018) [DVDISO]\VIDEO_TS\ED 1 and 2.mkv')
trimmed = core.std.Trim(bdsrc,32444,34550)
trimmeddvd = core.std.Trim(dvdsrc,386,2494)
downscaledbd = nnedi3_rpow2(trimmed).resize.Spline36(1440, 810)

scaled = Debicubic(trimmed, 1440, 810, b=1/3, c=1/3, yuv444=True)
u = vsutil.plane(scaled, 1)
v = vsutil.plane(scaled, 2)

rgb = mvf.ToRGB(trimmeddvd, depth = 32)
wupscaled = core.w2xc.Waifu2x(rgb, -1, 2)
upscaled = nnedi3_rpow2(wupscaled).resize.Spline36(1440, 810)
upscaled = mvf.ToYUV(upscaled, depth = 8)

submask = kgf.hardsubmask(downscaledbd,upscaled)
merged = core.std.MaskedMerge(scaled, upscaled, submask)
submask.set_output()

#lvf.scomp(upscaled,scaled).set_output()
core.std.Interleave([scaled,upscaled]).set_output()


#rescaled_l = nnedi3_rpow2(descaled_l).resize.Spline36(1920, 1080)
#scaled = kgf.join([descaled_l, u, v])