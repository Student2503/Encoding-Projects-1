# general imports

import vapoursynth as vs
from vsutil import *
from functools import partial
import mvsfunc as mvf
import EoEfunc as eoe
import havsfunc as haf
import kagefunc as kgf
import fvsfunc as fvf
core = vs.core

# i need more ram (this allocates 24 gigs)
core.max_cache_size = 48 * 1024

# scrads dehalo repair function, fairly simple, modified slightly to be less aggressive
def dehalo(clip, rep: int = 13) -> vs.VideoNode:
	# perform dehalo
    dehalo = haf.FineDehalo(denoise, rx=2.2, thmi=130, thma=191, darkstr=0.5, brightstr=1.2, contra=1, showmask=0, edgeproc=0.0)
    # repair against input clip, to make sure we dont fuck it too hard
    return core.rgvs.Repair(dehalo, clip, mode=rep)    
   
# take our input
#src = core.lsmas.LWLibavSource(r"[Kametsu] Noragami Aragoto - 01 (BD 1080p Hi10 FLAC)[2E0BADB7].mkv")
src = core.lsmas.LWLibavSource(src_path.decode("utf-8"))

# define some useful arrays (ill explain these later)
vertical = [0, 1, 0, 0, 0, 0, 1, 0]
horizontal = [0, 0, 0, 1, 1, 0, 0, 0]

# find vertical lines using a modified "Sobel" kernel (search Sobel up on google if you are interested.
# we do this twice to find both sides and be a little more accurate (tbh i probably dont need to do this)
lines_a = get_y(core.std.Convolution(src, matrix=[0, 2, 0, -2, 0]*2 + [0, 1, 0, -1, 0] + [0, 2, 0, -2, 0]*2))
lines_b = get_y(core.std.Convolution(src, matrix=[0, -2, 0, 2, 0]*2 + [0, -1, 0, 1, 0] + [0, -2, 0, 2, 0]*2))
# only take the brightest ones, this should really be done in a better way tbh, but whatever its like 100 cpu cycles
lines_vert = core.std.Expr([lines_a, lines_b], f"x y max 1023 = x y max 0 ?")
# remove small holes and stuff, basically just cleanes up the mask so we only have the vertical lines left
lines_vert = core.morpho.Open(lines_vert, size=2)

# final removal of only the lines themselves, this takes the minimum of the pixels using the `vertical` array defined earlier, arranged as follows
# 0 1 0
# 0 X 0
# 0 1 0
# where X is each input pixel, we only take the mimimum of the above and below pixel

lines_outer = iterate(lines_vert, partial(core.std.Minimum, coordinates=vertical), 2)

# similar idea for this, except (lol i cant spell) that we are expanding horizontally using a transposed kernel
lines_outer = iterate(lines_outer, partial(core.std.Maximum, coordinates=horizontal), 4)
# make the transition less hard (before it was like 0 0 0 255 255 255, now its like 0 80 120 200 255 255 or smth, so that when we use the mask, you can see the edges
lines_outer = iterate(lines_outer, core.std.Inflate, 2)
# remove vertical lines from mask themselves, so that we are left with only the outside portion, or the halos
halos = core.std.Expr([lines_outer, lines_vert], "x y -")

# descale to native (well not really, but whatever) resolution, and then upscale again. this deals with a lot of the crap, but leaves some pepega vertical halos
rescaled = get_y(eoe.rescale(src, 1280, 720, "lanczos", taps=3, mask_detail=True, rescale_threshold=0.03, denoise=False))
# increase src bitdepth to the same as `rescaled`
src_precise = fvf.Depth(src, 32) # its this line right here i think, it must be fucking something up
# replace areas of our halo mask in the `rescaled` frames with our (precise) source. this gets rid of our pepega halos, but its a pretty pepega method anyway
pepega = core.std.MaskedMerge(rescaled, get_y(src_precise), halos.resize.Point(format=rescaled.format))

# denoise luma (detail) using BM3D, very accurate, but very slow. 
#this is also done temporally (i.e. taking the last and next frames into account too) which makes it ultraslow and ultraram consuming
denoiseY = mvf.BM3D(src_precise, sigma=2.5, radius1=1) # luma
# denoise chroma (colour info) direct from source. the red information was slightly crappier than the blue, so we use a higher h (or strength) parameter for it.
denoiseU = core.knlm.KNLMeansCL(split(src_precise)[1], d=2, a=4, s=5, h=0.9)
denoiseV = core.knlm.KNLMeansCL(split(src_precise)[2], d=2, a=4, s=5, h=0.6)
# join our planes back together again, and resample to a slightly less precise, but still pretty damn precise format
denoise = join([denoiseY, denoiseU, denoiseV]).resize.Point(format=vs.YUV420P16)

# dehalo using our function defined on line 16
dehalo = dehalo(denoise)

# simple deband, nothing too special
deband = core.placebo.Deband(dehalo, planes=1, threshold=2, radius=12, grain=0)
# add in some static grain to retain gradients -> try to protect against banding a little, though this is very difficult at lower bitrates, so there'll still inevitably be banding.
# but this is a mini encode, so fuck you
grain = kgf.adaptive_grain(deband, 0.3, luma_scaling=10)

# output
#final = core.std.Interleave([src.resize.Point(format=grain.format)[::2], grain[::2]])
final = core.resize.Point(grain, format=vs.YUV420P10)
final.set_output()

'''
Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv | ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe Noragami.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a? -map 1:s? -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"rc-lookahead=100:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-intra=1:aq-mode=3:aq-strength=0.8:psy-rd=0.5:psy-rdoq=1.2:qcomp=0.68:bframes=8:ref=6:max-merge=4:subme=4:log-level=0:crqpoffs=-1:cbqpoffs=-1:crf=22`" -c:a libopus -b:a 112k -ac 2 -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}
'''
