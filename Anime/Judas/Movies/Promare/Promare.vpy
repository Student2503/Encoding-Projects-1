import vapoursynth as vs
core = vs.core

import sys
import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2
from vsTAAmbk import TAAmbk as taa

#src = lvf.src(r'Z:\Encoding\Projects\Ongoing\Promare\src\Promare.2019.1080p.BluRay.REMUX.DTS-HD.MA.5.1-Meakes.mkv')
srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (srcFile)", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src =  fvf.Depth(src, 16)

denoise = core.knlm.KNLMeansCL(src, d=1, a=3, s=4, h=1.2)

denoised = fvf.rfs(src, denoise, mappings = "[1 689]")
denoised = fvf.rfs(denoised, denoise, mappings = "[6306 34959]")
denoised = fvf.rfs(denoised, denoise, mappings = "[35190 96986]")
denoised = fvf.rfs(denoised, denoise, mappings = "[98068 159840]")

aa = taa(denoised, aatype='Nnedi3')

deband = stf.masked_deband(aa, gr = 2.0)

final = fvf.Depth(deband, 10)

final.set_output()
#core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(final, 10)]).set_output()