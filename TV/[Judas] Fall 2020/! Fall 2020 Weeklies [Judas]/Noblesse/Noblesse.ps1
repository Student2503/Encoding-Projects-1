Clear-Host; New-Item -ItemType "directory" encoded 2>&1>$null; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe Noblesse.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -map 1:a:0 -map 1:s? -map 1:t? -metadata:s:v:0 title="[Judas] x265 10b" -metadata:s:a:0 title="Japanese" -pix_fmt yuv420p10le -c:v libx265 -preset slow -x265-params `"log-level=error:rc-lookahead=60:tu-intra-depth=3:tu-inter-depth=3:weightb=1:b-intra=1:aq-strength=0.90:psy-rd=1.5:psy-rdoq=1.5:aq-mode=3:qcomp=0.63:ref=6:bframes=8:crf=19.5:deblock=0,0:crqpoffs=-1:cbqpoffs=-1:frame-threads=3:me=umh:amp=1:rect=1`" -c:a copy -c:s copy `"encoded\$($_.BaseName).mkv`" & exit"; Write-Host "`n----------------`n"}