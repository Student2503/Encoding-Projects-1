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
HRI = core.ffms2.Source(r'C:/Users/Joel/Desktop/[HRI] Fragtime v2 (BD 1080p) [ACABACAB].mkv')
beatrice = lvf.src(r'C:/Users/Joel/Downloads/[Beatrice-Raws] Fragtime [BDRip 1920x1080 HEVC FLAC]/[Beatrice-Raws] Fragtime [BDRip 1920x1080 HEVC FLAC].mkv')
# src = lvf.src(r'Z:\Downloads\! Nyaa\[Anime Time] Demon Slayer [BD P1][Dual-Audio][1080p][HEVC 10bit x265][AAC]/[Anime Time] Demon Slayer - S01E02 - Trainer Sakonji Urokodaki.mkv')
# Output
# final = depth(grain, 10)
# HRI.set_output()
core.std.Interleave([beatrice, HRI]).set_output()