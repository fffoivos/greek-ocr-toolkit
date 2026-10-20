#!/bin/zsh
# pix.sh src x y w h [thr]
f=$1; x=$2; y=$3; w=$4; h=$5; t=${6:-130}
magick "$f" -crop ${w}x${h}+${x}+${y} +repage -colorspace gray -depth 8 txt:- | awk -v t=$t -v W=$w -v H=$h 'NR>1{split($1,a,/[,:]/); g=$0; sub(/.*gray\(/,"",g); sub(/\).*/,"",g); g=g+0; v=(g<t*0.6)?"#":((g<t)?"+":"."); row[a[2]]=row[a[2]] v} END{for(i=0;i<H;i++)printf "%2d %s\n", i, row[i]}'
