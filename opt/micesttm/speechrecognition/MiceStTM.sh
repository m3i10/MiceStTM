#!/bin/bash

# Pfade zu den Icons
RED_ICON="/opt/micesttm/Icons/MiceSTTM-red.png"
GREEN_ICON="/opt/micesttm/Icons/MiceSTTM-green.png"
DESKTOP_FILE=$HOME"/Desktop/MiceStTM.desktop"

# Überprüfen, welches Icon aktuell ist
if grep -q "Icon=$GREEN_ICON" "$DESKTOP_FILE"; then
    # Wenn das grüne Icon aktiv ist, wechsle zu rot
    sed -i "s|Icon=.*|Icon=$RED_ICON|" "$DESKTOP_FILE"
else
    # Wenn das rote Icon aktiv ist, wechsle zu grün
    sed -i "s|Icon=.*|Icon=$GREEN_ICON|" "$DESKTOP_FILE"
fi

# Aktualisiere den Desktop
xdg-desktop-menu forceupdate
gnome-terminal --name MiceStTM --hide-menubar --geometry 20x7+1600+3 -- bash -c "/opt/micesttm/speechrecognition/mice_sttm.py"
