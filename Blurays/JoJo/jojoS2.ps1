Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv | ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe jojoS2.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a? -map 1:s? -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"rc-lookahead=100:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-intra=1:aq-mode=3:aq-strength=1.0:psy-rd=1.0:psy-rdoq=1.20:qcomp=0.6:bframes=8:ref=6:max-merge=4:subme=3:log-level=0:crqpoffs=-1:cbqpoffs=-1:crf=22`" -c:a libopus -b:a 112k -ac 2 -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}