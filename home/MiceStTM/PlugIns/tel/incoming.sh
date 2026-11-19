#!/bin/bash

TELFILE="$HOME/MiceStTM/PlugIns/anrufe/telnrliste.txt"
declare -a ACTIVE_CALLS   # speichert aktive Anrufe

#linphonecsh init
#sleep 2

echo "[INFO] Warte auf Anrufe..."

while true
do
    OUT=$(linphonecsh generic "calls")
    # Extrahiere alle Telefonnummern aus dem aktuellen Output
    NUMS=$(echo "$OUT" | grep -oP "sip:\K[0-9]+")
	
    for NUM in $NUMS; do
        # prüfen, ob Nummer schon gemeldet
        ALREADY=0
        for N in "${ACTIVE_CALLS[@]}"; do
            if [[ "$N" == "$NUM" ]]; then
                ALREADY=1
                break
            fi
        done

        if [[ $ALREADY -eq 0 ]]; then
            # Nummer ist neu
            # Name aus telnrliste.txt suchen
            NAME=$(grep -m1 "^.*:$NUM$" "$TELFILE" | cut -d':' -f1)
            if [[ -n "$NAME" ]]; then
                echo "[BEKANNT] $NAME ruft an! Nummer: $NUM"
                espeak-ng -v german "$NAME ruft an!"
            else
                echo "[UNBEKANNT] Unbekannte Nummer: $NUM"
                espeak-ng -v german "unbekannter anrufer $NUM"
            fi
            ACTIVE_CALLS+=("$NUM")
        fi
    done

    # Prüfen, welche Nummern nicht mehr in NUMS vorkommen → entfernen
    NEW_ACTIVE=()
    for N in "${ACTIVE_CALLS[@]}"; do
        if grep -q "$N" <<< "$NUMS"; then
            NEW_ACTIVE+=("$N")
        fi
    done
    ACTIVE_CALLS=("${NEW_ACTIVE[@]}")

    sleep 1
done

