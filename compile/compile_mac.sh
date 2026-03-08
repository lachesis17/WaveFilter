#!/bin/bash
set -e

cd "$(dirname "$0")/.."

HOOK=$(mktemp /tmp/hook_cwd.XXXXXX.py)
echo 'import os,sys; os.chdir(sys._MEIPASS)' > "$HOOK"
trap "rm -f '$HOOK'" EXIT

# .png → .icns for all PNGs in ui/icons/
for png in ui/icons/*.png; do
    [ -f "$png" ] || continue
    icns="${png%.png}.icns"
    [ -f "$icns" ] && continue
    iconset=$(mktemp -d)/icon.iconset
    mkdir -p "$iconset"
    for size in 16 32 128 256 512; do
        sips -z $size $size "$png" --out "$iconset/icon_${size}x${size}.png" > /dev/null
        double=$((size * 2))
        sips -z $double $double "$png" --out "$iconset/icon_${size}x${size}@2x.png" > /dev/null
    done
    iconutil -c icns "$iconset" -o "$icns"
    rm -rf "$(dirname "$iconset")"
    echo "Created $icns"
done

cp ui/wavefilter.ui ui/wavefilter.ui.bak
sed -i '' 's/\.ico/.icns/g' ui/wavefilter.ui
pyside6-uic ui/wavefilter.ui > ui/wavefilter_ui.py
cp ui/wavefilter.ui.bak ui/wavefilter.ui

pyinstaller \
    --noconfirm \
    --windowed \
    --clean \
    --icon=ui/icons/icon.icns \
    --name=WaveFilter \
    --contents-directory=. \
    --distpath=output \
    --add-data=examples:examples \
    --add-data=ui:ui \
    --exclude-module=PyQt5 \
    --exclude-module=PyQt6 \
    --runtime-hook="$HOOK" \
    main.py
