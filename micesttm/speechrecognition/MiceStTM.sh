#!/bin/bash

DESKTOP_PATH=$(xdg-user-dir DESKTOP)
RED_ICON="/opt/micesttm/Icons/MiceSTTM-red.png"
GREEN_ICON="/opt/micesttm/Icons/MiceSTTM-green.png"
DESKTOP_FILE="${DESKTOP_PATH}/MiceStTM.desktop"

if [ ! -f "$DESKTOP_FILE" ]; then
    echo "Fehler: $DESKTOP_FILE nicht gefunden!"
    exit 1
fi

if grep -q "Icon=$GREEN_ICON" "$DESKTOP_FILE"; then
    sed -i "s|Icon=.*|Icon=$RED_ICON|" "$DESKTOP_FILE"
else
    sed -i "s|Icon=.*|Icon=$GREEN_ICON|" "$DESKTOP_FILE"
fi
update-desktop-database "$DESKTOP_PATH" 2>/dev/null

# english sst library
gnome-terminal --name MiceStTM --hide-menubar --geometry 200x7+1600+3 -- bash -c "/opt/micesttm/speechrecognition/mice_sttm.py -m /opt/micesttm/model/vosk-model-small-en-us-0.15/"

# german sst library
# gnome-terminal --name MiceStTM --hide-menubar --geometry 200x7+1600+3 -- bash -c "/opt/micesttm/speechrecognition/mice_sttm.py -m /opt/micesttm/model/vosk-model-small-de-0.15/"
