Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe Promare.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a:0 -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"rc-lookahead=90:aq-strength=0.6:psy-rd=1.00:psy-rdoq=1:aq-mode=3:qcomp=0.60:ref=6:bframes=8:frame-threads=6:crf=18:deblock=0,0:fades=1:subme=5:amp=1:max-merge=4:lookahead-slices=2`" -c:a libopus -b:a 112k -ac 2 -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}