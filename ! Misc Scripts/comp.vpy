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
Judas = lvf.src(r'C:/Users/Joel/Downloads/Yahari Ore no Seishun Love Comedy wa Machigatteiru. Kan - 06 (VRV HIDIVE 1080p).mkv')
src = lvf.src(r'Z:\Downloads\! Nyaa/Yahari Ore no Seishun Love Comedy wa Machigatteiru. Kan - 06 (VRV HIDIVE 1080p).mkv')

output = core.std.Interleave([depth(src,8), depth(Judas, 8)]).set_output()