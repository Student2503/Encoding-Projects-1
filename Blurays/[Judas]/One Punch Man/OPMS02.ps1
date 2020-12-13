Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe OPMS1.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a? -map 1:s? -map 1:t? -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"pools=20,-:log-level=error:rc-lookahead=60:weightb=1:b-intra=1:aq-strength=1.0:psy-rd=1.5:psy-rdoq=2:me=3:aq-mode=3:qcomp=0.60:ref=6:bframes=8:rskip=0:crf=21.5:b-adapt=2:min-keyint=24:merange=57:limit-sao=1:deblock=0,0:fades=1:subme=5:gop-lookahead=0:max-merge=5:limit-modes=1:qp-adaptation-range=3:amp=1`" -c:a libopus -b:a 112k -ac 2 -c:s copy -metadata:s:v:0 title=`"[Judas] x265 10b`" -metadata:s:a:0 title=`"Japanese`"  `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}