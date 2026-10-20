#!/bin/zsh
# crop.sh src out x0pct x1pct scalepct
src=$1; out=$2; x0=$3; x1=$4; s=${5:-400}
w=$(magick identify -format %w "$src"); h=$(magick identify -format %h "$src")
X0=$(( w*x0/100 )); W=$(( w*(x1-x0)/100 ))
magick "$src" -crop ${W}x${h}+${X0}+0 +repage -filter Lanczos -resize ${s}% "$out"
magick identify "$out"
