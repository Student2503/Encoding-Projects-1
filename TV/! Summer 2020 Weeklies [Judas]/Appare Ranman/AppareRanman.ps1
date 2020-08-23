Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe AppareRanman.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a:0 -map 1:s? -map 1:t? -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"log-level=error:rc-lookahead=40:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-intra=1:aq-strength=0.75:psy-rd=1.0:psy-rdoq=1.3:aq-mode=3:qcomp=0.65:ref=6:bframes=8:crf=21.75:deblock=0,0:fades=1:subme=5:gop-lookahead=0:amp=1:crqpoffs=-1:cbqpoffs=-1:frame-threads=2:me=umh:no-cutree=1:qp-adaptation-range=3`" -c:a copy -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}