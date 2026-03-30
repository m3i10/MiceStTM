#!/bin/bash

# WICHTIG: Die $(...) Syntax führt den Befehl aus
DESKTOP_PATH=$(xdg-user-dir DESKTOP)

# Pfade zu den Icons
RED_ICON="/opt/micesttm/Icons/MiceSTTM-red.png"
GREEN_ICON="/opt/micesttm/Icons/MiceSTTM-green.png"
DESKTOP_FILE="${DESKTOP_PATH}/MiceStTM.desktop"

# Überprüfen, ob die Datei überhaupt existiert
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "Fehler: $DESKTOP_FILE nicht gefunden!"
    exit 1
fi

# Icon-Tausch via sed
if grep -q "Icon=$GREEN_ICON" "$DESKTOP_FILE"; then
    sed -i "s|Icon=.*|Icon=$RED_ICON|" "$DESKTOP_FILE"
else
    sed -i "s|Icon=.*|Icon=$GREEN_ICON|" "$DESKTOP_FILE"
fi

# Desktop-Cache leeren (manchmal nötig, damit das Icon sofort umschaltet)
update-desktop-database "$DESKTOP_PATH" 2>/dev/null

# Terminal starten
gnome-terminal --name MiceStTM --hide-menubar --geometry 200x7+1600+3 -- bash -c "/opt/micesttm/speechrecognition/mice_sttm.py"
