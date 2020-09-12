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
Judas = lvf.src(r'Z:/Anime/Re-ZERO -Starting Life in Another World-/Season 2/Re-ZERO -Starting Life in Another World- - 2x06 - Episode 06 [WEB-1080p x265 AAC] [Judas].mkv').set_output(0)
# Edge = lvf.src(r'Z:/Downloads/! Nyaa/[Edge]Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 06[1080p][10Bit][x265[Multiple Subtitle] (1).mkv').set_output(1)
# Akihito = lvf.src(r'Z:/Downloads/! Nyaa/[AkihitoSubs] Re_Zero kara Hajimeru Isekai Seikatsu - S02E06.mkv').set_output(2)
# AnT = lvf.src(r'Z:/Downloads/! Nyaa/[Anime Time] Re Zero kara Hajimeru Isekai Seikatsu S2 - 06 [1080p][HEVC 10bit x265][Multi Sub][AAC].mkv').set_output(3)
# FFA = lvf.src(r'Z:/Downloads/! Nyaa/[FFA] Re_Zero kara Hajimeru Isekai Seikatsu 2nd Season - 06 [1080p][HEVC][AAC].mkv').set_output(4)
Erai = lvf.src(r'Z:\Downloads/! Sonarr/imported-sonarr/[Erai-raws] Re.Zero kara Hajimeru Isekai Seikatsu 2nd Season - 06 [1080p][Multiple Subtitle].mkv').set_output(1)
# Ember = lvf.src(r'Z:/Downloads/! Nyaa/[EMBER] Re Zero kara Hajimeru Isekai Seikatsu S02  - 06.mkv').set_output(6)
# Output
# final = depth(grain, 10)
# src1.set_output()
# final = core.std.Interleave([depth(Erai,8), depth(Judas, 8)]).set_output()
# plane1 = plane(src1, 2)
# plane2 = plane(src2, 2)
# out = lvf.scomp(src1, depth(src2, 8),make_diff=True)
# stats = core.text.FrameProps(src2).set_output()

# mask = core.std.MakeDiff(src1, depth(src2, 8)).set_output()
# out2 = lvf.scomp(src1,depth(src2, 8), make_diff=True ).set_output()
# 19161
