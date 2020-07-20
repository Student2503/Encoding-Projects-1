import vapoursynth as vs
core = vs.get_core()
import vapoursynth as vs
core = vs.get_core()
import kagefunc as kgf
import lvsfunc as lvf
import fvsfunc as fvf
import vsutil
from nnedi3_rpow2 import nnedi3_rpow2
import mvsfunc as mvf
# import muvsfunc as muf
#import vsTAAmbk as taa
# import adjust
from rekt import *
import havsfunc as haf
import hysteria as hys
from vsTAAmbk import TAAmbk as taa

core.max_cache_size = 8096

src = lvf.src(r'Z:\Encoding\Projects\Araiya-san! Ore to Aitsu ga Onnayu de! (BDRip 1920x1080 FLAC)\src\Araiya-san! Ore to Aitsu ga Onnayu de! - 01 (BDRip 1920x1080 FLAC).mkv')
src = fvf.Depth(src, 32)
y = vsutil.plane(src, 0)
u = vsutil.plane(src, 1)
v = vsutil.plane(src, 2)

descaled = kgf.inverse_scale(y, height=864, kernel='bicubic', b=1/3, c=1/3, mask_detail=True)															# Rescaling
rescaled = nnedi3_rpow2(descaled).resize.Spline36(1920, 1080)
scaled = kgf.join([rescaled, u, v])
scaled = fvf.Depth(scaled, 16)


denoise = mvf.BM3D(scaled, sigma=2)																															# Denoising

dering = haf.HQDeringmod(denoise)																														# Dering

aa = taa(dering, 3)																																		# Anti - Aliasing
aa = fvf.Depth(aa, 32)

deband = core.placebo.Deband(aa, planes = 1, iterations = 2,grain = 2)																				# Debanding
deband = core.placebo.Deband(deband, planes = 2|4, iterations = 1,grain = 0)
deband = fvf.Depth(deband, 16)

dehalo = haf.DeHalo_alpha(deband, rx=1.0, ry=1.0, darkstr=0.4, brightstr=1.0, lowsens=50, highsens=50, ss=1.5)											# De halo

final = fvf.Depth(dehalo, 10)																															# Output
final.set_output()
#core.std.Interleave([scaled, final]).set_output()
"""
Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.m2ts | ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe TLR_S1.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a -map 1:s -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"rc-lookahead=100:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-inta=1:aq-mode=3:aq-strength=0.85:psy-rd=0.9:psy-rdoq=1.25:qcomp=0.7:bframes=8:ref=6:max-merge=4:subme=4:log-level=0:crqpoffs=-1:cbqpoffs=-1:crf=22`" -c:a libopus -b:a 112k -ac 2 -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}
"""