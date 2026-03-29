#!/bin/bash

RED_ICON="/opt/micesttm/Icons/Autogain-red.png"
GREEN_ICON="/opt/micesttm/Icons/Autogain-green.png"
DESKTOP_FILE="$HOME/Desktop/autogain.desktop"

if grep -q "Icon=$GREEN_ICON" "$DESKTOP_FILE"; then
    sed -i "s|Icon=.*|Icon=$RED_ICON|" "$DESKTOP_FILE"
else
    sed -i "s|Icon=.*|Icon=$GREEN_ICON|" "$DESKTOP_FILE"
fi

xdg-desktop-menu forceupdate
/opt/micesttm/speechrecognition/micautogain.py

