import vapoursynth as vs
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
from vsTAAmbk import TAAmbk
import vsutil
from nnedi3_rpow2 import nnedi3_rpow2
import mvsfunc as mvf
import vsTAAmbk as taa
core = vs.core
core.max_cache_size = 8196

src = lvf.src(r'D:\1.)Sono Hanabira\Source\sonohanabira.mkv')
src = fvf.Depth(src, 32)

# splitting yuv
y, u, v = kgf.split(src)
height = 720
width = vsutil.get_w(height)


# Catmull-rom
# descaling to 720p with Mitchell-Netravali
# then rescaling to 1080p with spline36
descaled = kgf.inverse_scale(y, height=720, kernel='bicubic', b=1/2, c=0, mask_detail=True)
rescaled = nnedi3_rpow2(descaled).resize.Spline36(1920, 1080)
scaled = kgf.join([rescaled, u, v])

# Get Y plane from descaled and denoise
yplane = mvf.GetPlane(scaled, 0)
denoise = mvf.BM3D(yplane, sigma=3)
# Merge denoised Y plane with UV planes
denoised = core.std.ShufflePlanes([denoise, scaled, scaled], [0,1,2], colorfamily=scaled.format.color_family)

# Dither to 16 bits to anti alias
d16 = fvf.Depth(denoised, 16)
# Anti-Aliase
aa  = taa.TAAmbk(d16, aatype='Nnedi3')

# Mask to protect edges from deband filter
l_mask = kgf.retinex_edgemask(aa)
# Deband
deband = core.f3kdb.Deband(aa, range=16, y=40, cb=32, cr=32, grainy=0, grainc=0, output_depth=16)

merged = core.std.MaskedMerge(deband, aa, l_mask)

grain = kgf.adaptive_grain(merged, 0.2, luma_scaling=8)

trim = core.std.Trim(grain, 4396, 4918)

out = fvf.Depth(grain, 10)
out.set_output()