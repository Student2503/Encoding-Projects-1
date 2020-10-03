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

core.max_cache_size = 16 * 1024

# Source
AnimeTime = lvf.src(r'Z:\Downloads\! Nyaa\[Anime Time] Demon Slayer [BD P1][Dual-Audio][1080p][HEVC 10bit x265][AAC]/[Anime Time] Demon Slayer - S01E02 - Trainer Sakonji Urokodaki.mkv')
beatrice = lvf.src(r'E:\!Seedbox/[Beatrice-Raws] Kimetsu no Yaiba 02 [BDRip 1920x1080 HEVC FLAC].mkv')
Judas = lvf.src(r'E:\!Seedbox/[Judas] Kimetsu no Yaiba 02 [BDRip 1920x1080 HEVC FLAC].mkv')
# Output
# final = depth(grain, 10)
# final.set_output()
core.std.Interleave([beatrice, Judas]).set_output()