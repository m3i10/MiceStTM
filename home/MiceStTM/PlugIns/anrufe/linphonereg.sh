###############################################
# KONFIGURATION
###############################################
SIP_USER="linphone"                   # aus FRITZ!Box
SIP_PASS="xxxxxxxxxx"        # aus FRITZ!Box
SIP_SERVER="sssss.box"
###############################################

echo "[INFO] Starte Linphone..."
linphonecsh exit
sleep 2
linphonecsh init
sleep 2

echo "[INFO] Registriere bei FRITZ!Box..."
linphonecsh register --host "$SIP_SERVER" --username "$SIP_USER" --password "$SIP_PASS"
sleep 2

echo "[INFO] Status:"
linphonecsh status register

