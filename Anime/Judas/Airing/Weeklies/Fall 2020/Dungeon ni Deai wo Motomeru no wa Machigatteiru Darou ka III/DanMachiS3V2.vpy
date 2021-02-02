import vapoursynth as vs
core = vs.core

from typing import Any, Callable, Dict, Optional
from vsTAAmbk import TAAmbk as taa
import stolenfunc as stf
import mvsfunc as mvf
import lvsfunc as lvf
import kagefunc as kgf
import havsfunc as haf
from typing import Optional
from vsutil import *
import sys
import os

core.max_cache_size = 16 * 1024

# Source
# zastin = lvf.src(r'src/[Z4ST1N] DanMachi S3 - 02 [39638AD1].mkv')
# wakanim = lvf.src(r'src/DanMachi III - 01 (WEB-DL 1920x1080 x264 AAC Rus + Jap).mkv')
# Judas = lvf.src(r'src/[Judas] Danmachi - S03E02.mkv')
# Judas = Judas[24:]
erai = lvf.src(r'src/[Erai-raws] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka III - 03 [1080p][Multiple Subtitle].mkv')
# erai = erai[24:]
shitdive = lvf.src(r'src/(Xenos) Heretics-GR4G29WJY.mp4')
# shitdive = shitdive[24:]

# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
src = depth(shitdive, 16)

# Filtering
denoise = core.knlm.KNLMeansCL(src, d=3, a=2, s=6, h=0.6)

aa = taa(denoise, 3)

deband = join([
             core.placebo.Deband(plane(aa, 0), grain=0, threshold=2.8, radius=18,),
             core.placebo.Deband(plane(aa, 1), grain=0, threshold=3.2, radius=22),
             core.placebo.Deband(plane(aa, 2), grain=0, threshold=3.2, radius=22)
                ])    

dehalo = stf.dehalo(deband) 

grain = kgf.adaptive_grain(dehalo, 0.40, luma_scaling=5)

# # Output
final = depth(grain, 10)
# final.set_output()
shitdive.set_output(0)
join([plane(shitdive, 1), plane(shitdive, 2)]).set_output(1)
plane(shitdive, 1).set_output(2)
plane(shitdive, 2).set_output(3)

erai.set_output(4)
join([plane(erai, 1), plane(erai, 2)]).set_output(5)
plane(erai, 1).set_output(6)
plane(erai, 2).set_output(7)

# core.std.Interleave([depth(erai, 10),depth(shitdive, 10)]).set_output(1)
# lvf.comparison.compare(depth(erai, 10),depth(shitdive, 10), rand_total=5).set_output(2)
# zastin.set_output(2)
