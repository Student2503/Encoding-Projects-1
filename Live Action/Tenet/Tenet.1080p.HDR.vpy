import vapoursynth as vs
core = vs.core

from functools import partial
from typing import Any, Callable, Dict, Optional
from cooldegrain import CoolDegrain
import lvsfunc as lvf
import kagefunc as kgf
import vardefunc as vdf
import mvsfunc as mvf
import awsmfunc as awf
from vsTAAmbk import TAAmbk as taa
from typing import Optional
from vsutil import *
import sys

src = lvf.src(r'src/Tenet.2020.2160p.UHD.Bluray.Remux.HDR10.HEVC.DTS-HDMA.5.1-4K4U.mkv')
depth(rescale, 8).set_output(0)