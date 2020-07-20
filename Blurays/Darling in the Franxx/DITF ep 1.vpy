# Imports
import vapoursynth as vs
import descale as descale
from nnedi3_rpow2 import nnedi3_rpow2

core = vs.get_core()
# Loading Plugins
# Loading C:\Users\Joel\Documents\Encoding Projects\DARLING in the FRANXX\Source Videos\[SweetSub&VCB-Studio] DARLING in the FRANXX [01][Ma10p_1080p][x265_flac_aac].mkv using LWLibavSource
clip = core.lsmas.LWLibavSource(source="C:/Users/Joel/DOCUME~1/ENCODI~1/DARLIN~1/SOURCE~1/_SWEET~2.MKV", format="YUV420P10", cache=0, prefer_hw=3)
# making sure input color matrix is set as 709
clip = core.resize.Point(clip, matrix_in_s="709",range_s="limited")
# making sure frame rate is set to 23.976
clip = core.std.AssumeFPS(clip, fpsnum=24000, fpsden=1001)
# Setting color range to TV (limited) range.
clip = core.std.SetFrameProp(clip=clip, prop="_ColorRange", intval=1)

clip = descale.Debilinear(clip,1440,810)
clip = nnedi3_rpow2(clip).resize.Spline36(1920, 1080)
clip = core.f3kdb.Deband(clip, range=17, y=64, cb=40, cr=40, grainy=64, grainc=8, output_depth=16, keep_tv_range=True)

# Output
clip.set_output()