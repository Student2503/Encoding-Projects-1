Clear-Host; cmd /k "vspipe -o 1 shieldbro.vpy -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: `"asakura\asakura-%03d.bmp`" & exit";cmd /k "vspipe -o 2 shieldbro.vpy -y - | ffmpeg -y -hide_banner -loglevel warning -stats -i pipe: `"mottoj\mottoj-%03d.bmp`" & exit" ; Write-Host "`n----------------`n"