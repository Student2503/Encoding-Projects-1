import vapoursynth as vs
import havsfunc as haf
import kagefunc as kgf
import mvsfunc as muf
from vsTAAmbk import TAAmbk as taa
from vsutil import *
core = vs.core

core.max_cache_size = 24 * 1024

#src = core.lsmas.LWLibavSource(r"To Love-Ru S01E01 2008 1080p Bluray REMUX AVC DTS-HD MA 2.0 Dual Audio -ZR-.mkv")


src = core.lsmas.LWLibavSource(src_path.decode("utf-8"))                        # input
QTGMC = haf.QTGMC(src, "Slow", TFF=True, FPSDivisor=2)                          # deinterlace
QTGMC = core.vivtc.VDecimate(QTGMC)                                             # decimate
src = core.fmtc.bitdepth(QTGMC, bits=16)                                        # increase bitdepth

denoise = core.knlm.KNLMeansCL(src, d=2, a=3, h=0.7, channels="y")              # denoise luma
denoise = core.knlm.KNLMeansCL(denoise, d=1, a=2, h=0.7, s=6, channels="uv")    # denoise chroma

dehalo = haf.YAHR(denoise, blur=1, depth=48)                                    # dehalo largest ring
dehalo = haf.DeHalo_alpha(dehalo, darkstr=0.5, brightstr=1)                     # center
dehalo = haf.YAHR(dehalo, blur=1, depth=64)                                     # inner (very bright, needed high depth)

ld = haf.FastLineDarkenMOD(dehalo, strength=32)                                 # line darken
ld = core.std.Expr([denoise, ld], "x y < x y ?")                                # clamp line darken to source
ld = core.std.MaskedMerge(dehalo, ld, dehalo.std.Sobel().std.Maximum())         # clamp line darken to lines

sharp = core.warp.AWarpSharp2(ld, thresh=16, blur=3, type=1)                    # minor sharpening

aa = taa(sharp, 3)                                                              # anti-aliasing (nnedi3)

deband = core.neo_f3kdb.Deband(aa, 16, 32, 24, 24, 24, 8, keep_tv_range=True)   # simple deband

grain = kgf.adaptive_grain(deband, 0.35, luma_scaling=8)                        # added a fair amount (less) grain, effect works (less) nicely

#comp = core.std.Interleave([vcb.resize.Point(format=grain.format).text.Text("vcb"), aa])

final = grain                                                                   # define output
final = core.resize.Point(final, format=vs.YUV420P10)                           # drop bitdepth to 10 bits
final.set_output()                                                              # set clip to output, pipe to x265

"""
Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.m2ts | ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe TLR_S1.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a -map 1:s -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"rc-lookahead=100:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-inta=1:aq-mode=3:aq-strength=0.85:psy-rd=0.9:psy-rdoq=1.25:qcomp=0.7:bframes=8:ref=6:max-merge=4:subme=4:log-level=0:crqpoffs=-1:cbqpoffs=-1:crf=22`" -c:a libopus -b:a 112k -ac 2 -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}
"""