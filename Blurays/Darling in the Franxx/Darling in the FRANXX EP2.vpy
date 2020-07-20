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
src = lvf.src(r'D:\Projects\2.)DARLING in the FRANXX\Source Videos\Remux\DARLING in the FRANXX S01E05 2018 1080p BluRay REMUX AVC TRUEHD 5.1 Dual Audio-ZR-.mkv')
src = fvf.Depth(src, 32)

opstart, opend, edstart, edend = 2997, 5153, 32393, 34575


#splitting yuv
y, u, v = kgf.split(src)
height = 810
width = vsutil.get_w(height)


# Mitchell-Netravali
#descale_b = core.descale.Debicubic(y, width, height, b=1/3, c=1/3)
#descale_b = kgf.join([descale_b, u, v])
#descaling to 810p with Mitchell-Netravali
#then rescaling to 1080p with spline36
descaled_l = kgf.inverse_scale(y, height=810, kernel='bicubic', b=1/3, c=1/3, mask_detail=True, descale_mask_zones=f"[{opstart} {opend}] [{edstart} {edend}]")
rescaled_l = nnedi3_rpow2(descaled_l).resize.Spline36(1920, 1080)
scaled = kgf.join([rescaled_l, u, v])

# Get Y plane from descaled clip to denoise OP and ED
yplane = mvf.GetPlane(scaled, 0)

#Denoise OP with weaker denoise_op and ED with stronger denoise_ed
denoise_op = mvf.BM3D(yplane, sigma=3)
denoise_ed = mvf.BM3D(yplane, sigma=4)
denoise = fvf.rfs(denoise_op, denoise_ed, mappings=f"[{opstart} {opend}] [{edstart} {edend}]")

# Merge denoised Y plane with UV planes
denoised = core.std.ShufflePlanes([denoise, scaled, scaled], [0,1,2], colorfamily=scaled.format.color_family)

# Dither to 16 bits to anti alias
denoised16 = fvf.Depth(denoised, 16)

# Anti-Aliase
aa  = taa.TAAmbk(denoised16, aatype='Nnedi3')

# Mask to protect edges from deband filter
l_mask = kgf.retinex_edgemask(aa)

# Deband
deband = core.f3kdb.Deband(aa, range=16, y=40, cb=32, cr=32, grainy=0, grainc=0, output_depth=16)

# Merge aa, Deband and edges
merge = core.std.MaskedMerge(deband, aa, l_mask)

# Adding grain to OP and ED, lesser to rest of Ep
#grain_a = kgf.adaptive_grain(merge, 0.8,static=False, luma_scaling=8)
#grain_b = kgf.adaptive_grain(merge, 0.8,static=False, luma_scaling=5) 
#grain = fvf.rfs(grain_a, grain_b, mappings=f"[{opstart} {opend}] [{edstart} {edend}]")

#dither down to 10 bit
final = fvf.Depth(merge, 10)

#output
final.set_output()