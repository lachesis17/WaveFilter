#!/bin/bash
set -e

cd "$(dirname "$0")/.."

HOOK=$(mktemp /tmp/hook_cwd.XXXXXX.py)
echo 'import os,sys; os.chdir(sys._MEIPASS)' > "$HOOK"
trap "rm -f '$HOOK'" EXIT

cp ui/wavefilter.ui ui/wavefilter.ui.bak
sed -i '' 's/colors\.ico/colors.icns/g' ui/wavefilter.ui
pyside6-uic ui/wavefilter.ui > ui/wavefilter_ui.py
cp ui/wavefilter.ui.bak ui/wavefilter.ui

pyinstaller \
    --noconfirm \
    --windowed \
    --clean \
    --icon=ui/icon.icns \
    --name=WaveFilter \
    --contents-directory=. \
    --distpath=output \
    --add-data=examples:examples \
    --add-data=ui:ui \
    --exclude-module=PyQt5 \
    --exclude-module=PyQt6 \
    --runtime-hook="$HOOK" \
    main.py
