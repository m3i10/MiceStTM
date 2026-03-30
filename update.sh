#!/bin/bash

DESKTOP_PATH=$(xdg-user-dir DESKTOP)
CMD="sudo rsync -vau micesttm/Icons/MiceStTM.desktop $DESKTOP_PATH/ && sudo rsync -vau micesttm /opt/ && rsync -avu home/. $HOME/; echo 'Fertig! Beliebige Taste zum Schließen...'; read"

TERMINALS=("gnome-terminal" "konsole" "xfce4-terminal" "mate-terminal" "lxterminal" "xterm")

for TERM in "${TERMINALS[@]}"; do
    if command -v "$TERM" >/dev/null 2>&1; then
        case "$TERM" in
            "gnome-terminal")
                "$TERM" -- bash -c "$CMD" &
                ;;
            "konsole"|"xfce4-terminal"|"mate-terminal"|"lxterminal"|"xterm")
                "$TERM" -e "bash -c \"$CMD\"" &
                ;;
        esac
        TERM_FOUND=true
        break
    fi
done

if [ "$TERM_FOUND" != true ]; then
    echo "Fehler: Kein Terminal-Emulator gefunden!"
    exit 1
fi
