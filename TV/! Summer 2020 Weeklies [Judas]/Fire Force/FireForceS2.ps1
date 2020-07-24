Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe Fire.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a:0 -map 1:s -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"log-level=error:rc-lookahead=20:aq-strength=0.80:psy-rd=1.3:psy-rdoq=2:aq-mode=3:qcomp=0.65:ref=6:bframes=8:frame-threads=2:crf=20:no-strong-intra-smoothing=1:deblock=1,-1:subme=5:crqpoffs=-1:cbqpoffs=-1:fades=1:frame-threads=2:me=umh:no-cutree=1:hevc-aq=1:qp-adaptation-range=3:gop-lookahead=0:`" -c:a copy -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}