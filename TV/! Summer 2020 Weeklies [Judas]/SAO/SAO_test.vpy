import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import lvsfunc as lvf
import kagefunc as kgf
from typing import Optional
import havsfunc as haf
from vsutil import *
import sys
core.max_cache_size = 16384
import adjust

# Source
src = lvf.src(r'Z:\Anime\Sword Art Online\Season 4\Sword Art Online - 4x13 - Episode 13 [WEB-1080p x264 AAC] [HorribleSubs].mkv')
waka = lvf.src(r'Z:\Sword Art Online Alicization - War of Underworld - 13 (WEB-DL 1920x1080 x264 AAC Rus).mp4')
OP = lvf.src(r'C:/Users/Joel\Downloads/OP 2 edited.mp4')
# src = src[1:]
# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
# src = depth(src, 16)
src = core.std.Trim(src, first = 912, last = 3067)
waka = core.std.Trim(waka, first = 911, last = 3066)
wakabright = adjust.Tweak(waka, sat=1.7, bright=0.0,cont=1.5)
clips = [waka,OP,waka]
averaged = core.average.Mean(clips, preset=1)

# Output
final = depth(src, 10)
# OP.set_output()
# core.std.Interleave([depth(src, 10),depth(atx, 10)]).set_output()
comp = lvf.scomp(wakabright, OP,make_diff=True).set_output()