import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
from vsutil import *
import sys
core.max_cache_size = 16384

# Source
# amazon = lvf.src(r'Z:/Downloads/! Sonarr/imported-sonarr/[SNAFU] Yahari Ore no Seishun Love Comedy wa Machigatteiru. Kan - 02 [1C7D7345].mkv')
# erai = lvf.src(r'Z:/Downloads/! Sonarr/imported-sonarr/[Erai-raws] Yahari Ore no Seishun LoveCome wa Machigatte Iru. Kan - 02 [1080p][Multiple Subtitle].mkv')
# erai = core.std.Trim(erai, first = 144)
# Judas = lvf.src(r'Z:/Downloads/! Sonarr/imported-sonarr/[Judas] Oregairu - S03E02.mkv')
# motbob = lvf.src(r'Z:/Downloads/! Sonarr/imported-sonarr/[MTBB] Yahari Ore no Seishun Love Comedy wa Machigatteiru. Kan - 02 [04BE0754].mkv')

srcFile = src_path.decode("utf-8")
print(file=sys.stderr)
print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
src = core.ffms2.Source(srcFile)
src = depth(src, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src,h=0.2, d=2, a=3)
deband = stf.masked_deband(denoise, iterations=1, grain = 0)
aa = taa(deband, 3)
grain = kgf.adaptive_grain(aa, 0.05, luma_scaling=10)

# Output
final = depth(src, 10)
# Judas = stf.dehalo(Judas)
final.set_output()
# core.std.Interleave([depth(grain, 10),depth(motbob, 10)]).set_output()
# core.std.Interleave([amazon,motbob]).set_output()