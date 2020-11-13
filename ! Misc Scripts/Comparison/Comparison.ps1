Clear-Host; Get-ChildItem *.mkv | ForEach-Object {New-Item -Type Directory -Name $($_.BaseName)}; Get-ChildItem *.mkv| ForEach-Object {Write-Host "Starting $($_.Name)`n"; cmd /k "vspipe Comparison.vpy --arg `"src_path=$($_.Name)`" -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: -i `"$($_.Name)`" -map 0:v -pix_fmt yuv420p10le `"$($_.BaseName)\$($_.BaseName)-%03d.png`" & exit"; Write-Host "`n----------------`n"}