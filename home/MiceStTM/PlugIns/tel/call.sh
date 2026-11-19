#!/bin/bash

TELFILE="$HOME/MiceStTM/PlugIns/anrufe/telnrliste.txt"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <Name>"
    exit 1
fi

NAME=$1
NUM=$(grep -m1 "^$NAME:" "$TELFILE" | cut -d':' -f2)

if [[ -z "$NUM" ]]; then
    echo "Name '$NAME' nicht gefunden in $TELFILE"
    espeak-ng -v german  "Name '$NAME' nicht gefunden!"
    echo "[INFO] Registriere neu..."
	pkill -f "eingehender.sh"
	$HOME/MiceStTM/PlugIns/anrufe/linphonereg.sh

	# Optional: eingehender Script wieder starten
	$HOME/MiceStTM/PlugIns/anrufe/eingehender.sh &

    exit 1
fi

# 1️⃣ Eingehendes-Script stoppen, falls aktiv
if pgrep -f "eingehender.sh" >/dev/null; then
    echo "[INFO] Stoppe eingehender.sh..."
    pkill -f "eingehender.sh"
fi

# 2️⃣ Linphone-Daemon prüfen
if ! linphonecsh status &>/dev/null; then
    echo "[INFO] Starte Linphone-Daemon..."
    linphonecsh init
    sleep 1
fi

# 3️⃣ Anruf starten
echo "[INFO] Rufe $NAME ($NUM) an..."
linphonecsh dial "sip:$NUM@fritz.box"

# 4️⃣ Warten bis der Anruf beendet ist
echo "[INFO] Warte auf Ende des Telefonats..."
while true; do
    CALLS=$(linphonecsh generic "calls")
    if [[ -z "$CALLS" ]]; then
        break
    fi
    sleep 1
done

echo "[INFO] Telefonat beendet."

pkill -f "eingehender.sh"
# 5️⃣ Registrierung wiederherstellen
echo "[INFO] Registriere neu..."
$HOME/MiceStTM/PlugIns/anrufe/linphonereg.sh

# Optional: eingehender Script wieder starten
$HOME/MiceStTM/PlugIns/anrufe/eingehender.sh &

