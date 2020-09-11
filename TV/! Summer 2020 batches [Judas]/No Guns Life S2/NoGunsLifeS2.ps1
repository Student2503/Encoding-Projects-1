Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe NoGunsLiveS2.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:t? -map 1:a:0 -map 1:s? -pix_fmt yuv420p10le -c:v libx265 -preset veryslow -x265-params `"log-level=error:rc-lookahead=250:weightb=1:b-intra=1:aq-strength=0.85:psy-rd=1.2:psy-rdoq=1.0:me=3:aq-mode=3:qcomp=0.60:ref=6:bframes=16:rskip=0:crf=21:b-adapt=2:min-keyint=24:merange=57:limit-sao=1:deblock=-1,-1:fades=1:subme=5:gop-lookahead=0:limit-refs=1:max-merge=5:frame-threads=1:no-limit-modes=1:qp-adaptation-range=3`" -c:a copy -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}