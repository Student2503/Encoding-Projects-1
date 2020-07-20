from vapoursynth import core
import vsutil
import kagefunc as kgf
import fvsfunc as fvf
import lvsfunc as lvf
#source
src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Promare\src\Promare.2019.1080p.BluRay.REMUX.DTS-HD.MA.5.1-Meakes.mkv')
src = fvf.Depth(src, 32)

#split planes
y, u, v = kgf.split(src)
height = 810
width = vsutil.get_w(height)

#descale
# Bilinear
descale_a = core.descale.Debilinear(y, width, height).resize.Bilinear(1920, 1080)
descale_a = kgf.join([descale_a, u, v])
# Mitchell-Netravali
descale_b = core.descale.Debicubic(y, width, height, b=1/3, c=1/3).resize.Bicubic(1920, 1080, filter_param_a=1/3, filter_param_b=1/3)
descale_b = kgf.join([descale_b, u, v])
# Sharp Bicubic
descale_c = core.descale.Debicubic(y, width, height, b=0, c=1).resize.Bicubic(1920, 1080, filter_param_a=0, filter_param_b=1)
descale_c = kgf.join([descale_c, u, v])
# B-Spline
descale_d = core.descale.Debicubic(y, width, height, b=1, c=0).resize.Bicubic(1920, 1080, filter_param_a=1, filter_param_b=0)
descale_d = kgf.join([descale_d, u, v])
# Catmull-rom
descale_e = core.descale.Debicubic(y, width, height, b=0, c=1/2).resize.Bicubic(1920, 1080, filter_param_a=0, filter_param_b=1/2)
descale_e = kgf.join([descale_e, u, v])
# Spline36
descale_f = core.descale.Despline36(y, width, height).resize.Spline36(1920, 1080)
descale_f = kgf.join([descale_f, u, v])

#change output descale
out = fvf.Depth(descale_e, 10)
src1 = fvf.Depth(src, 10)
#output
#out.set_output()
core.std.Interleave([out, src1]).set_output()
