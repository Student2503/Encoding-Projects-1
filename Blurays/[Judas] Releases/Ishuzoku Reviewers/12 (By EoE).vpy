import vapoursynth as vs
import lvsfunc as lvf
import kagefunc as kgf
import fvsfunc as fvf
import mvsfunc as mvf
from vsTAAmbk import TAAmbk as taa
from nnedi3_rpow2 import nnedi3_rpow2 as rpow2
from vsutil import *
core = vs.get_core()

core.max_cache_size = 64 * 1024

atx_ohys_raw = core.ffms2.Source(r"atx12.mp4")
atx_ohys_raw = atx_ohys_raw[:2853] + atx_ohys_raw[3045:]
atx_ohys = core.resize.Spline36(atx_ohys_raw, 1914, 1080)
atx_ohys_full = core.resize.Spline36(atx_ohys_raw, 1920, 1080)
atx_ohys = core.resize.Point(atx_ohys, 1914*4, 1080*4)
atx_ohys = core.std.AddBorders(atx_ohys, 14, 14, 0, 0)
atx_ohys = core.resize.Point(atx_ohys, 1920, 1080)
thing = list(range(33500))[0::1001]
thing.pop(28)
baha = core.ffms2.Source(r"baha12.mkv").std.DeleteFrames(thing).std.DeleteFrames(27360)
waka = core.ffms2.Source(r"waka12.mp4")

subheight1 = 500
mask1_a = core.std.BlankClip(width=1920, height=subheight1, format=vs.YUV420P8, length=1, color=[0, 0, 0])
mask1_b = core.std.BlankClip(width=1920, height=1080-subheight1, format=vs.YUV420P8, length=1, color=[255, 255, 255])
mask1 = core.std.StackVertical([mask1_b, mask1_a])
mask1 = core.resize.Point(mask1, format=vs.YUV420P16)

subheight2 = 300
mask2_a = core.std.BlankClip(width=1920, height=subheight2, format=vs.YUV420P8, length=1, color=[0, 0, 0])
mask2_b = core.std.BlankClip(width=1920, height=1080-subheight2, format=vs.YUV420P8, length=1, color=[255, 255, 255])
mask2 = core.std.StackVertical([mask2_b, mask2_a])
mask2 = core.resize.Point(mask2, format=vs.YUV420P16)

ohysmask = core.std.BlankClip(width=1840, height=1080, format=vs.YUV420P8, length=1, color=[0, 0, 0])
ohysmask = core.std.AddBorders(ohysmask, 40, 40, 0, 0, color=[255, 255, 255])
ohysmask = core.resize.Point(ohysmask, format=vs.YUV420P16)

ohys = core.resize.Point(atx_ohys, format=vs.YUV420P16)
ohys_full = core.resize.Point(atx_ohys_full, format=vs.YUV420P16)
baha = core.resize.Point(baha, format=vs.YUV420P16)
waka = core.resize.Point(waka, format=vs.YUV420P16)

top = core.std.StackHorizontal([ohys.text.Text("ohys"), waka.text.Text("waka")])
bottom = core.std.StackHorizontal([baha.text.Text("baha"), get_y(core.std.MakeDiff(ohys, waka)).text.Text("ohys-waka diff").resize.Point(format=vs.YUV420P16)])
core.std.StackVertical([top, bottom]).set_output()

waka_hardsubs1 = waka[1347:1429]
baha_hardsubs1 = baha[1347:1429]
hardsubs1 = core.std.MaskedMerge(waka_hardsubs1, baha_hardsubs1, mask2)

waka_hardsubs2 = waka[1990:2116]
baha_hardsubs2 = baha[1990:2116]
hardsubs2 = core.std.MaskedMerge(waka_hardsubs2, baha_hardsubs2, mask2)

waka_hardsubs3 = waka[2853:2925]
baha_hardsubs3 = baha[2853:2925]
mask_hardsubs3 = kgf.hardsubmask(waka_hardsubs3, baha_hardsubs3, expand_n=10)
hardsubs3 = core.std.MaskedMerge(waka_hardsubs3, baha_hardsubs3, mask_hardsubs3)

baha_scene1_a = baha[3278:3398]
ohys_scene1_a = ohys[3278:3398]
mask_scene1_a = kgf.hardsubmask(baha_scene1_a, ohys_scene1_a, expand_n=10)
scene1_a = core.std.MaskedMerge(baha_scene1_a, ohys_scene1_a, mask_scene1_a)

baha_scene1_b = baha[3486:3558]
ohys_scene1_b = ohys[3486:3558]
mask_scene1_b = kgf.hardsubmask(baha_scene1_b, ohys_scene1_b, expand_n=10)
scene1_b = core.std.MaskedMerge(baha_scene1_b, ohys_scene1_b, mask_scene1_b)

baha_scene1_c = baha[3627:4165]
ohys_scene1_c = ohys[3627:4165]
mask_scene1_c = kgf.hardsubmask(baha_scene1_c, ohys_scene1_c, expand_n=10)
scene1_c = core.std.MaskedMerge(baha_scene1_c, ohys_scene1_c, mask_scene1_c)

waka_hardsubs4 = waka[4165:4249]
baha_hardsubs4 = baha[4165:4249]
mask_hardsubs4 = kgf.hardsubmask(waka_hardsubs4, baha_hardsubs4, expand_n=10)
hardsubs4 = core.std.MaskedMerge(waka_hardsubs4, baha_hardsubs4, mask_hardsubs4)

baha_scene1_d = baha[6306:6349]
ohys_scene1_d = ohys[6306:6349]
ohys_scene1_d_slow = ohys[6305:6349]
ohys_scene1_d = fvf.rfs(ohys_scene1_d, ohys_scene1_d_slow, "36")
mask_scene1_d = kgf.hardsubmask(baha_scene1_d, ohys_scene1_d, expand_n=10)
scene1_d = core.std.MaskedMerge(baha_scene1_d, ohys_scene1_d, mask_scene1_d)

waka_hardsubs5 = waka[7234:7426]
baha_hardsubs5 = baha[7234:7426]
hardsubs5 = core.std.MaskedMerge(waka_hardsubs5, baha_hardsubs5, mask2)

waka_hardsubs6 = waka[7823:7936]
baha_hardsubs6 = baha[7823:7936]
hardsubs6 = core.std.MaskedMerge(waka_hardsubs6, baha_hardsubs6, mask2)

baha_scene1_e = baha[8815:9249]
ohys_scene1_e = ohys[8815:9249]
ohys_scene1_e_slow = ohys[8814:9249]
ohys_scene1_e = fvf.rfs(ohys_scene1_e, ohys_scene1_e_slow, "30 43 51 95 103 127 131 135")
mask_scene1_e = kgf.hardsubmask(baha_scene1_e, ohys_scene1_e, expand_n=10).std.Inflate().std.Inflate().std.Inflate()
scene1_e = core.std.MaskedMerge(baha_scene1_e, ohys_scene1_e, mask_scene1_e)
# fixed some dumb mask shit thing
mask_ohys_scene1_e = core.std.BlankClip(width=1100, height=100, format=vs.GRAY16, color=[65535])
mask_ohys_scene1_e = core.std.AddBorders(mask_ohys_scene1_e, 410, 410, 890, 90, color=[0])
scene1_e = core.std.MaskedMerge(baha_scene1_e, scene1_e, mask_ohys_scene1_e)

scene1 = scene1_a + waka[3398:3486] + scene1_b + waka[3558:3627] + scene1_c + hardsubs4 + waka[4249:6306] + scene1_d + waka[6349:7234] + hardsubs5 + waka[7426:7823] + hardsubs6 + waka[7936:8815] + scene1_e

#scene2
baha_scene2_a = baha[10359:10636]
ohys_scene2_a = ohys[10359:10636]
mask_scene2_a = kgf.hardsubmask(baha_scene2_a, ohys_scene2_a, expand_n=10)
scene2_a = core.std.MaskedMerge(baha_scene2_a, ohys_scene2_a, mask_scene2_a)

baha_scenefuckssake = baha[10738:10851]
ohys_scenefuckssake = ohys[10738:10851]
ohys_scenefuckssake_slow = ohys[10737:10851]
ohys_scenefuckssake = fvf.rfs(ohys_scenefuckssake, ohys_scenefuckssake_slow, "48 51 56 80")
mask_scenefuckssake = kgf.hardsubmask(baha_scenefuckssake, ohys_scenefuckssake, expand_n=10)
scenefuckssake = core.std.MaskedMerge(baha_scenefuckssake, ohys_scenefuckssake, mask_scenefuckssake)

baha_scene2_b = baha[10882:11219]
ohys_scene2_b = ohys[10882:11219]
mask_scene2_b = kgf.hardsubmask(baha_scene2_b, ohys_scene2_b, expand_n=10)
scene2_b = core.std.MaskedMerge(baha_scene2_b, ohys_scene2_b, mask_scene2_b)
# dehardsubs failed here
scene2_b_fail = core.std.MaskedMerge(baha_scene2_b, ohys_scene2_b, mask_scene2_b[233])
scene2_b = fvf.rfs(scene2_b, scene2_b_fail, "[227 332]")

baha_scene2_c = baha[11988:12068]
ohys_scene2_c = ohys[11988:12068]
mask_scene2_c = kgf.hardsubmask(baha_scene2_c, ohys_scene2_c, expand_n=10)
scene2_c = core.std.MaskedMerge(baha_scene2_c, ohys_scene2_c, mask_scene2_c)

baha_scene2_d = baha[12277:12348]
ohys_scene2_d = ohys[12277:12348]
mask_scene2_d = kgf.hardsubmask(baha_scene2_d, ohys_scene2_d, expand_n=10)
scene2_d = core.std.MaskedMerge(baha_scene2_d, ohys_scene2_d, mask_scene2_d)

baha_scene2_e = baha[12568:13181]
ohys_scene2_e = ohys[12568:13181]
mask_scene2_e = kgf.hardsubmask(baha_scene2_e, ohys_scene2_e, expand_n=10)
scene2_e = core.std.MaskedMerge(baha_scene2_e, ohys_scene2_e, mask_scene2_e)

baha_scene2_f = baha[13800:13936]
ohys_scene2_f = ohys[13800:13936]
mask_scene2_f = kgf.hardsubmask(baha_scene2_f, ohys_scene2_f, expand_n=10)
scene2_f = core.std.MaskedMerge(baha_scene2_f, ohys_scene2_f, mask_scene2_f)

baha_scene2_g = baha[13998:14184]
ohys_scene2_g = ohys[13998:14184]
mask_scene2_g = kgf.hardsubmask(baha_scene2_g, ohys_scene2_g, expand_n=10)
scene2_g = core.std.MaskedMerge(baha_scene2_g, ohys_scene2_g, mask_scene2_g)

baha_scene2_h = baha[14243:14777]
ohys_scene2_h = ohys[14243:14777]
ohys_scene2_h_slow = ohys[14242:14777]
ohys_scene2_h = fvf.rfs(ohys_scene2_h, ohys_scene2_h_slow, "11 47 59 83")
mask_scene2_h = kgf.hardsubmask(baha_scene2_h, ohys_scene2_h, expand_n=10)
scene2_h = core.std.MaskedMerge(baha_scene2_h, ohys_scene2_h, mask_scene2_h)

baha_scene2_i = baha[14827:14981]
ohys_scene2_i = ohys[14827:14981]
mask_scene2_i = kgf.hardsubmask(baha_scene2_i, ohys_scene2_i, expand_n=10)
scene2_i = core.std.MaskedMerge(baha_scene2_i, ohys_scene2_i, mask_scene2_i)

baha_scene2_j = baha[15041:15157]
ohys_scene2_j = ohys[15041:15157]
mask_scene2_j = kgf.hardsubmask(baha_scene2_j, ohys_scene2_j, expand_n=10)
scene2_j = core.std.MaskedMerge(baha_scene2_j, ohys_scene2_j, mask_scene2_j)

baha_scene2_k = baha[15202:15334]
ohys_scene2_k = ohys[15202:15334]
ohys_scene2_k_slow = ohys[15201:15334]
ohys_scene2_k = fvf.rfs(ohys_scene2_k, ohys_scene2_k_slow, "8 20 99 100")
mask_scene2_k = kgf.hardsubmask(baha_scene2_k, ohys_scene2_k, expand_n=10)
scene2_k = core.std.MaskedMerge(baha_scene2_k, ohys_scene2_k, mask_scene2_k)

#15456
baha_scene2_l = baha[15456:15682]
ohys_scene2_l = ohys[15456:15682]
ohys_scene2_l_slow = ohys[15455:15682]
ohys_scene2_l = fvf.rfs(ohys_scene2_l, ohys_scene2_l_slow, "1")
mask_scene2_l = kgf.hardsubmask(baha_scene2_l, ohys_scene2_l, expand_n=10)
scene2_l = core.std.MaskedMerge(baha_scene2_l, ohys_scene2_l, mask_scene2_l)

scene2 = scene2_a + waka[10636:10738] + scenefuckssake + waka[10851:10882] + scene2_b + waka[11219:11988] + scene2_c + waka[12068:12277] + scene2_d + waka[12348:12568] + scene2_e + waka[13181:13800] + scene2_f + waka[13936:13998] + scene2_g + waka[14184:14243] + scene2_h + waka[14777:14827] + scene2_i + waka[14981:15041] + scene2_j + waka[15157:15202] + scene2_k + waka[15334:15456] + scene2_l

mask_hardsubs7 = core.std.BlankClip(width=402, height=56, format=vs.YUV420P16, color=[65535]*3)
mask_hardsubs7 = core.std.AddBorders(mask_hardsubs7, 760, 758, 808, 216, color=[0]*3).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Inflate().std.Inflate()
hardsubs7 = core.std.MaskedMerge(waka[15682:15742], baha[15682:15742], mask_hardsubs7)

hardsubs8 = core.std.MaskedMerge(waka[15908:16040], baha[15908:16040], mask2)

midcard = baha[16160:16280]

mask_hardsubs9 = kgf.hardsubmask_fades(waka[16346], baha[16346]).std.Maximum().std.Maximum().std.Maximum().std.Maximum().std.Inflate()
hardsubs9 = core.std.MaskedMerge(waka[16346:16460], baha[16346:16460], mask_hardsubs9) 

baha_scene3_a = baha[20020:20135]
ohys_scene3_a = ohys[20020:20135]
mask_scene3_a = kgf.hardsubmask(baha_scene3_a, ohys_scene3_a, expand_n=10)
scene3_a = core.std.MaskedMerge(baha_scene3_a, ohys_scene3_a, mask_scene3_a)

baha_scene3_b = baha[20872:20972]
ohys_scene3_b = ohys[20872:20972]
mask_scene3_b = kgf.hardsubmask(baha_scene3_b, ohys_scene3_b, expand_n=10)
scene3_b = core.std.MaskedMerge(baha_scene3_b, ohys_scene3_b, mask_scene3_b)

baha_scene3_c = baha[21235:21542]
ohys_scene3_c = ohys[21235:21542]
mask_scene3_c = kgf.hardsubmask(baha_scene3_c, ohys_scene3_c, expand_n=10)
scene3_c = core.std.MaskedMerge(baha_scene3_c, ohys_scene3_c, mask_scene3_c)

baha_scene3_d = baha[21772:21870]
ohys_scene3_d = ohys[21772:21870]
mask_scene3_d = kgf.hardsubmask(baha_scene3_d, ohys_scene3_d, expand_n=10)
scene3_d = core.std.MaskedMerge(baha_scene3_d, ohys_scene3_d, mask_scene3_d)

hardsubs10 = core.std.MaskedMerge(waka[22212:22296], baha[22212:22296], mask2)

hardsubs11 = core.std.MaskedMerge(waka[22739:22781], baha[22739:22781], mask2)

baha_scene3_e = baha[23441:23525]
ohys_scene3_e = ohys[23441:23525]
mask_scene3_e = kgf.hardsubmask(baha_scene3_e, ohys_scene3_e, expand_n=10)
scene3_e = core.std.MaskedMerge(baha_scene3_e, ohys_scene3_e, mask_scene3_e)

baha_scene3_f = baha[24874:24994]
ohys_scene3_f = ohys[24874:24994]
ohys_scene3_f_fast = ohys[24875:24995]
ohys_scene3_f = fvf.rfs(ohys_scene3_f, ohys_scene3_f_fast, "119")
mask_scene3_f = kgf.hardsubmask(baha_scene3_f, ohys_scene3_f, expand_n=10)
scene3_f = core.std.MaskedMerge(baha_scene3_f, ohys_scene3_f, mask_scene3_f)

baha_scene3_g = baha[25186:25417]
ohys_scene3_g = ohys[25186:25417]
mask_scene3_g = kgf.hardsubmask(baha_scene3_g, ohys_scene3_g, expand_n=10)
scene3_g = core.std.MaskedMerge(baha_scene3_g, ohys_scene3_g, mask_scene3_g)

baha_scene3_h = baha[26191:26286]
ohys_scene3_h = ohys[26191:26286]
mask_scene3_h = kgf.hardsubmask(baha_scene3_h, ohys_scene3_h, expand_n=10)
scene3_h = core.std.MaskedMerge(baha_scene3_h, ohys_scene3_h, mask_scene3_h)

baha_scene3_i = baha[26715:26835]
ohys_scene3_i = ohys[26715:26835]
mask_scene3_i = kgf.hardsubmask(baha_scene3_i, ohys_scene3_i, expand_n=10)
scene3_i = core.std.MaskedMerge(baha_scene3_i, ohys_scene3_i, mask_scene3_i)

hardsubs12 = core.std.MaskedMerge(waka[26835:26895], baha[26835:26895], mask2)

baha_scene3_j = baha[26940:27171]
ohys_scene3_j = ohys[26940:27171]
mask_scene3_j = kgf.hardsubmask(baha_scene3_j, ohys_scene3_j, expand_n=10)
scene3_j = core.std.MaskedMerge(baha_scene3_j, ohys_scene3_j, mask_scene3_j)

baha_scene3_k = baha[27181:27360]
ohys_scene3_k = ohys[27181:27360]
mask_scene3_k = kgf.hardsubmask(baha_scene3_k, ohys_scene3_k, expand_n=10)
scene3_k = core.std.MaskedMerge(baha_scene3_k, ohys_scene3_k, mask_scene3_k)

baha_scene3_l = baha[27498:27705]
ohys_scene3_l = ohys[27498:27705]
mask_scene3_l = kgf.hardsubmask(baha_scene3_l, ohys_scene3_l, expand_n=10)
scene3_l = core.std.MaskedMerge(baha_scene3_l, ohys_scene3_l, mask_scene3_l)

baha_scene3_m = baha[27752:28141]
ohys_scene3_m = ohys[27752:28141]
ohys_scene3_m_fast = ohys[27753:28141]
ohys_scene3_m = fvf.rfs(ohys_scene3_m, ohys_scene3_m_fast, "[329 331]")
mask_scene3_m = kgf.hardsubmask(baha_scene3_m, ohys_scene3_m, expand_n=10)
scene3_m = core.std.MaskedMerge(baha_scene3_m, ohys_scene3_m, mask_scene3_m)

baha_scene3_n = baha[28291:28534]
ohys_scene3_n = ohys[28291:28534]
mask_scene3_n = kgf.hardsubmask(baha_scene3_n, ohys_scene3_n, expand_n=10)
scene3_n = core.std.MaskedMerge(baha_scene3_n, ohys_scene3_n, mask_scene3_n)

baha_scene3_o = baha[28561:29307]
ohys_scene3_o = ohys[28561:29307]
ohys_scene3_o_fast = ohys[28562:29307]
ohys_scene3_o = fvf.rfs(ohys_scene3_o, ohys_scene3_o_fast, "105 117 141 153 189 233 [249 252] 261 265 [273 276] 293 [296 298] 309 317")
mask_scene3_o = kgf.hardsubmask(baha_scene3_o, ohys_scene3_o, expand_n=10)
scene3_o = core.std.MaskedMerge(baha_scene3_o, ohys_scene3_o, mask_scene3_o)

baha_hardsubs13 = baha[31084:31958]
ohys_hardsubs13 = ohys[31084:31958]
ohys_hardsubs13_fast = ohys[31085:31958]
ohys_hardsubs13 = fvf.rfs(ohys_hardsubs13, ohys_hardsubs13_fast, "109 110 410 414 434 439 463 466 478 481 502 505 645 646 655 685 718 730 781 853 862 865")
mask_hardsubs13 = kgf.hardsubmask(baha_hardsubs13, ohys_hardsubs13, expand_n=10)
hardsubs13 = core.std.MaskedMerge(baha_hardsubs13, ohys_hardsubs13, mask_hardsubs13)
# deal with bad hardsubmask
mask_ohys_hardsubs13 = core.std.BlankClip(width=1048, height=186, format=vs.GRAY16, color=[65535])
mask_ohys_hardsubs13 = core.std.AddBorders(mask_ohys_hardsubs13, 436, 436, 804, 90, color=[0]).std.BoxBlur(hradius=5, vradius=5)
hardsubs13 = core.std.MaskedMerge(baha_hardsubs13, hardsubs13, mask_ohys_hardsubs13)

baha_scene3_p = baha[32335:32494]
ohys_scene3_p = ohys[32335:32494]
mask_scene3_p = kgf.hardsubmask(baha_scene3_p, ohys_scene3_p, expand_n=10)
scene3_p = core.std.MaskedMerge(baha_scene3_p, ohys_scene3_p, mask_scene3_p)

baha_scene3_q = baha[32954:32972]
ohys_scene3_q = ohys[32954:32972]
mask_scene3_q = kgf.hardsubmask(baha_scene3_q, ohys_scene3_q, expand_n=10)
scene3_q = core.std.MaskedMerge(baha_scene3_q, ohys_scene3_q, mask_scene3_q)

baha_scene3_r = baha[33016:33059]
ohys_scene3_r = ohys[33016:33059]
mask_scene3_r = kgf.hardsubmask(baha_scene3_r, ohys_scene3_r, expand_n=10)
scene3_r = core.std.MaskedMerge(baha_scene3_r, ohys_scene3_r, mask_scene3_r)

baha_scene3_s = baha[33085:33100]
ohys_scene3_s = ohys[33085:33100]
mask_scene3_s = kgf.hardsubmask(baha_scene3_s, ohys_scene3_s, expand_n=10)
scene3_s = core.std.MaskedMerge(baha_scene3_s, ohys_scene3_s, mask_scene3_s)

baha_scene3_t = baha[33118:33132]
ohys_scene3_t = ohys[33118:33132]
mask_scene3_t = kgf.hardsubmask(baha_scene3_t, ohys_scene3_t, expand_n=10)
scene3_t = core.std.MaskedMerge(baha_scene3_t, ohys_scene3_t, mask_scene3_t)

baha_scene3_u = baha[33233:33248]
ohys_scene3_u = ohys[33233:33248]
mask_scene3_u = kgf.hardsubmask(baha_scene3_u, ohys_scene3_u, expand_n=10)
scene3_u = core.std.MaskedMerge(baha_scene3_u, ohys_scene3_u, mask_scene3_u)

baha_scene3_v = baha[33320:33332]
ohys_scene3_v = ohys[33320:33332]
mask_scene3_v = kgf.hardsubmask(baha_scene3_v, ohys_scene3_v, expand_n=10)
scene3_v = core.std.MaskedMerge(baha_scene3_v, ohys_scene3_v, mask_scene3_v)

baha_scene3_w = baha[33339:33350]
ohys_scene3_w = ohys[33339:33350]
mask_scene3_w = kgf.hardsubmask(baha_scene3_w, ohys_scene3_w, expand_n=10)
scene3_w = core.std.MaskedMerge(baha_scene3_w, ohys_scene3_w, mask_scene3_w)

scene3 = scene3_a + waka[20135:20872] + scene3_b + waka[20972:21235] + scene3_c + waka[21542:21772] + scene3_d + waka[21870:22212] + hardsubs10 + waka[22296:22739] + hardsubs11 + waka[22781:23441] + scene3_e + waka[23525:24874] + scene3_f + waka[24994:25186] + scene3_g + waka[25417:26191] + scene3_h + waka[26286:26715] + scene3_i + hardsubs12 + waka[26895:26940] + scene3_j + waka[27171:27181] + scene3_k + waka[27360:27498] + scene3_l + waka[27705:27752] + scene3_m + waka[28141:28291] + scene3_n + waka[28534:28561] + scene3_o + waka[29307:31084] + hardsubs13 + waka[31958:32335] + scene3_p + waka[32494:32954] + scene3_q + waka[32972:33016] + scene3_r + waka[33059:33085] + scene3_s + waka[33100:33118] + scene3_t + waka[33132:33233] + scene3_u + waka[33248:33320] + scene3_v + waka[33332:33339] + scene3_w

video = waka[:1347] + hardsubs1 + waka[1429:1990] + hardsubs2 + waka[2116:2853] + hardsubs3 + waka[2925:3278] + scene1 + waka[9249:10359] + scene2 + hardsubs7 + waka[15742:15908] + hardsubs8 + waka[16040:16160] + midcard + waka[16280:16346] + hardsubs9 + waka[16460:20020] + scene3 + waka[33350:]

video.set_output()

lvf.scomp(baha, waka, make_diff=True).set_output()

#endcard = core.std.MaskedMerge(waka[33674], baha[33674], mask2) * 120
## ======================

##1490 838
def rescale(src, x, y, luma, chroma):
    planes = split(src)
    srcY = core.fmtc.bitdepth(planes[0], bits=32)
    descaled = core.descale.Debilinear(srcY, x, y)
    rescaled = core.resize.Bicubic(descaled, 1920, 1080, filter_param_a=1/3, filter_param_b=1/3)
    mask = core.std.Expr([srcY, rescaled], "x y - abs 0.025 < 0 1 ?").std.Maximum().std.Maximum().std.Inflate().std.Inflate()
    upscaled = rpow2(descaled).resize.Spline36(1920, 1080)
    fixed = core.std.MaskedMerge(upscaled, srcY, mask)
    finalY = core.fmtc.bitdepth(fixed, bits=16)
    denoiseY = mvf.BM3D(finalY, sigma=[luma]) 
    denoiseU, denoiseV = [core.knlm.KNLMeansCL(p, h=chroma) for p in planes[1:]]
    return join([denoiseY, denoiseU, denoiseV]), mask

rescale, mask = rescale(video, 1490, 838, 3, 0.6)

aa = taa(rescale, 3)

deband = core.neo_f3kdb.Deband(aa, 16, 48, 36, 36, 16, 16)

grain = kgf.adaptive_grain(deband, 0.4, luma_scaling = 8)

out = grain
out = fvf.Depth(out, 10)
out = out.std.AssumeFPS(fpsnum=24000, fpsden=1001)
out.set_output()
