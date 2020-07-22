Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe ReZeroS2_Weekly.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a:0 -map 1:s -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"log-level=error:rc-lookahead=100:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-intra=1:aq-strength=0.80:psy-rd=1.5:psy-rdoq=2:aq-mode=3:qcomp=0.70:ref=6:bframes=8:crf=20:deblock=0,0:crqpoffs=-1:cbqpoffs=-1:fades=1:frame-threads=2:me=umh`" -c:a copy -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}