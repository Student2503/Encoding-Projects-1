# Imports
import vapoursynth as vs
import descale as descale
from nnedi3_rpow2 import nnedi3_rpow2

# Import scripts
import mvsfunc
import edi_rpow2
import fvsfunc as fvf
import havsfunc
import muvsfunc
import hysteria as hys
import vsTAAmbk as taa
import kagefunc as kgf
core = vs.get_core()

# Source
clip = core.ffms2.Source(r'C:\Users\Joel\Documents\Encoding Projects\sonohanabira.mkv')

# Converting to 16 bit
clip = fvf.Depth(clip, 32)

# making sure input color matrix is set as 709
clip = core.resize.Point(clip, matrix_in_s="709",range_s="limited")

# making sure frame rate is set to 24
clip = core.std.AssumeFPS(clip, fpsnum=24, fpsden=1)

# Setting color range to TV (limited) range.
clip = core.std.SetFrameProp(clip=clip, prop="_ColorRange", intval=1)

#clip = core.descale(clip, 1280,720)

#Denoise
clip = core.knlm.KNLMeansCL(clip, d=3, a=2, h=0.4)

# Anti Aliasing using TAAmbk
clip = taa.TAAmbk(fvf.Depth(clip, 16), aatype='Nnedi3')

# Debanding using GradFun3
clip = fvf.GradFun3(src=clip, thr=0.40)

# Add Grain
clip = kgf.adaptive_grain(clip, 0.2, luma_scaling=10)

# Dithering to 10 bit
clip = fvf.Depth(clip, 10)

# Adjusting output color from: YUV420P16 to YUV420P10 for x265Model (i420)
fil = core.resize.Bicubic(clip=clip, format=vs.YUV420P10, range_s="limited")

# Output
clip.set_output()
