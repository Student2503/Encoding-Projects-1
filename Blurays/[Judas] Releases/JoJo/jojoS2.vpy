from vsutil import *
import vapoursynth as vs
import havsfunc as haf
import kagefunc as kgf
import mvsfunc as mvf
import fvsfunc as fvf
import nnedi3_rpow2
import lvsfunc as lvf
import stolenfunc as stf
import sys
from vsTAAmbk import TAAmbk as taa

core = vs.core

core.max_cache_size = 10 * 1024

def rescale(source: vs.VideoNode, width: int = None, height: int = 0, kernel: str = 'bilinear', taps: int = 4,
                  b: float = 1 / 3, c: float = 1 / 3, mask_detail: bool = False, rescale_threshold: float = 0.015,
                  rescale_mask_zones: str = '', denoise: bool = False, bm3d_sigma: float = 1, knl_luma: float = 0.6,
                  knl_chroma: float = 0.6, use_gpu: bool = True, get_rescale_mask: bool = False) \
        -> vs.VideoNode:
    if not height:
        raise ValueError('inverse_scale: you need to specify a value for the output height')

    only_luma = source.format.num_planes == 1

    if get_depth(source) != 32:
        source = source.resize.Point(format=source.format.replace(bits_per_sample=32, sample_type=vs.FLOAT))

    if denoise and not only_luma:
        source = core.knlm.KNLMeansCL(source, a=1, h=knl_chroma, d=2, s=5, channels='UV')

    planes = split(source)
    planes[0] = descaled = kgf._descale_luma(planes[0], width, height, kernel, taps, b, c)

    if denoise:
        if use_gpu:
            planes[0] = core.knlm.KNLMeansCL(planes[0], a=2, h=knl_luma, d=3)
        else:
            planes[0] = mvf.BM3D(planes[0], sigma=bm3d_sigma)

    planes[0] = nnedi3_rpow2.nnedi3_rpow2(planes[0], rfactor=2).resize.Spline36(source.width, source.height)

    if only_luma and not mask_detail:
        return planes[0]

    if mask_detail:
        upscaled = fvf.Resize(descaled, source.width, source.height, kernel=kernel, taps=taps, a1=b, a2=c)
        mask = get_descale_mask(get_y(source), upscaled, rescale_threshold)
        if get_rescale_mask:
            return mask
        planes[0] = core.std.MaskedMerge(planes[0], get_y(source), mask)
    scaled = join(planes)
    return scaled

def get_descale_mask(source: vs.VideoNode, upscaled: vs.VideoNode, threshold: float = 0.015) \
    -> vs.VideoNode:
    '''
    '''
    mask = core.std.Expr([source, upscaled], f"x y - abs {threshold} < 0 1 ?")
    mask = iterate(mask, core.std.Maximum, 2)
    mask = iterate(mask, core.std.Inflate, 2)
    return mask

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
#src = core.lsmas.LWLibavSource(r"00000.m2ts")
# src = lvf.src(r"Z:/Downloads/JoJo's Bizarre Adventure (2012) - S02E05 (031) - Silver Chariot.mkv")
try:
	src = core.edgefixer.ContinuityFixer(src, 1, 1, 1, 1, 3)
except:
	src = core.edgefixer.Continuity(src, 1, 1, 1, 1, 3)
		
src = core.fmtc.bitdepth(src, bits=16)

rescaled = rescale(src, 1280, 720, kernel="bicubic", b=0.5, c=0, mask_detail=True, rescale_threshold=0.03, denoise=True, bm3d_sigma=3, knl_chroma=0.9, use_gpu=False)
rescaled = core.resize.Point(rescaled, format=vs.YUV420P16)
aa = taa(rescaled, 3, opencl=True)

dehalo = haf.FineDehalo(aa, darkstr=0.4, brightstr=0.9)

deband_a = stf.masked_deband(dehalo, radius = 16, grain = 0)
deband_b = core.placebo.Deband(dehalo, planes=1, grain=0, radius=8)
deband = core.average.Mean([deband_a, deband_b], preset=0)

grain = kgf.adaptive_grain(deband, 0.10)

final = grain
final = core.resize.Point(final, format=vs.YUV420P10)
final.set_output()
# core.std.Interleave([depth(src, 10),depth(final, 10)]).set_output()


'''
Clear-Host;
New-Item -ItemType "directory" video 2>&1 | out-null;
New-Item -ItemType "directory" other 2>&1 | out-null;
New-Item -ItemType "directory" muxed 2>&1 | out-null;
Get-ChildItem *.mkv | ForEach-Object {
    Write-Host "Starting $($_.Name)";
    cmd /k "vspipe jojo.vpy --arg `"srcFile=$($_.Name)`" --y4m - | x265 --input - --y4m --preset slow --ref 6 --b-intra --tu-intra-depth 3 --tu-inter-depth 3 --subme 4 --weightb --psy-rd 0.6 --psy-rdoq 1.3 --keyint 340 --min-keyint 34 --rc-lookahead 100 --bframes 8 --fades --crf 21.5 --aq-mode 3 --aq-strength 0.9 --qcomp 0.68 --deblock -1:-1 --output-depth 10 --output `"video\$($_.BaseName).h265`" & exit"
    
    Write-Host "`nEncoding audio...`n";
    ffmpeg -nostdin -y -hide_banner -loglevel warning -stats -i "$($_.Name)" -map 0:a -map 0:s -c:a libopus -b:a 112k -c:s copy "other\$($_.Name)"
    
    Write-Host "`nMuxing`n"
    mkvmerge.exe --output "muxed\$($_.Name)" "video\$($_.BaseName).h265" "other\$($_.Name)"
}
'''