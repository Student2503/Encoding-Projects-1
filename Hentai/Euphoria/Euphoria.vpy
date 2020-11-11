import vapoursynth as vs
core = vs.get_core()

import stolenfunc as stf
import lvsfunc as lvf
import fvsfunc as fvf
import mvsfunc as mvf
import kagefunc as kgf
from vsutil import *
from nnedi3_rpow2 import nnedi3_rpow2 as nnedi3_rpow2

src = lvf.src(r'Z:\Encoding\Projects\Up next\Euphoria\(18禁アニメ) [魔人] euphoria 1 ～真中合歓 地獄始動編～ (BD 1920x1080 x264 FLAC).mkv')

final = fvf.Depth(src, 10)
final.set_output()
#core.std.Interleave([fvf.Depth(src, 10),fvf.Depth(final, 10)])