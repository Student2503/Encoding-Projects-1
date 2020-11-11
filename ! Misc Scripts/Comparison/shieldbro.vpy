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

core.max_cache_size = 2 * 1024

# Source
# srcFile = src_path.decode("utf-8")
# print(file=sys.stderr)
# print(f"Vapoursynth: Beginning job - (", srcFile, ")", file=sys.stderr)
# src = core.ffms2.Source(srcFile)
# src = src[::1440]

src1 = lvf.src(r'[Asakura] Tate no Yuusha no Nariagari - 01 [DCF54FF3].mkv')
src2 = lvf.src(r'[mottoj] Tate no Yuusha no Nariagari - 01 (BDRip 1920x1080 HEVC FLAC).mkv')[24:]

src1 = src1[::1440].set_output(1)
src2 = src2[::1440].set_output(2)