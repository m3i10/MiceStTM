#!/bin/bash
# erstellt mit Unterstützung von gpt5
# tasmota hinzufügen Stehlampe

# --------------------------
# KONFIGURATION
# --------------------------
FRITZ_SSID="FRITZ"
FRITZ_PASS="xxxxxxxxxxxxxxx"
NETZWERK_RANGE="xxx.xxx.0.0/24"

TASMOTA_NEW_NAME=$1
echo $TASMOTA_NEW_NAME


# MQTT
MQTT_SERVER="xxx.xxx.xxx.xxx"
MQTT_PORT="1883"
MQTT_USER=""
MQTT_PASS=""
MQTT_TOPIC="tasmota/"$TASMOTA_NEW_NAME
# --------------------------

TASMOTA_AP_IP="xxx.xxx.xxx.xxx"

# --------------------------
# Mit Tasmota-AP verbinden
# --------------------------
echo "Wifi ausschalten"
nmcli radio wifi off
sleep 2
echo "Wifi einschalten"
nmcli radio wifi on
sleep 2

echo "Wifi neu scannen"
nmcli device wifi rescan
sleep 3

echo "nach Tasmota suchen und an AP Verbinden"
AP_SSID=$(nmcli -t -f SSID device wifi list | grep -i "tasmota" | head -n1)
if [[ -z "$AP_SSID" ]]; then
    echo "Konnte keine Tasmota Steckdose finden!"
    espeak-ng -v german "Konnte keine Tasmota Steckdose finden!"
    exit 1
fi
nmcli device wifi connect "$AP_SSID"
sleep 6

# --------------------------
# WLAN + MQTT an Tasmota senden (%3B)
# --------------------------
CMD="Backlog%20SSID1%20$FRITZ_SSID%3BPassword1%20$FRITZ_PASS%3BWifiConfig%205%3BFriendlyName1%20$TASMOTA_NEW_NAME%3BMqttHost%20$MQTT_SERVER%3BMqttPort%20$MQTT_PORT%3BMqttUser%20$MQTT_USER%3BMqttPassword%20$MQTT_PASS%3BTopic%20$MQTT_TOPIC"
echo "Wifi Daten Übertragen"
curl -s "http://$TASMOTA_AP_IP/cm?cmnd=$CMD"
sleep 10

# --------------------------
# Zurück zur FritzBox verbinden
# --------------------------
echo "zurück zum WLAN Router"
nmcli device wifi connect "$FRITZ_SSID" password "$FRITZ_PASS"
sleep 4

# --------------------------
# Neue IP anhand FriendlyName suchen
# --------------------------
echo "➡ Suche IP anhand FriendlyName: $TASMOTA_NEW_NAME ..."

NEW_IP=$(nmap -p 80 --open $NETZWERK_RANGE \
        -oG - 2>/dev/null | \
        grep "$TASMOTA_NEW_NAME" | \
        grep "Ports" | \
        awk '{print $2}')

if [[ -z "$NEW_IP" ]]; then
    echo "❌ Konnte IP für $TASMOTA_NEW_NAME nicht finden!"
    exit 1
fi

echo ""
echo " NEUE TASMOTA‑STECKDOSE:"
echo "➡ Name: $TASMOTA_NEW_NAME"
echo "➡ MQTT Topic: $MQTT_TOPIC"
echo "➡ Neue IP: $NEW_IP"

echo "" >>$HOME/.config/micesttm/macros/de/macro
echo category: Tasmota >>$HOME/.config/micesttm/macros/de/macro
echo comment: $TASMOTA_NEW_NAME schalten >>$HOME/.config/micesttm/macros/de/macro
echo trigger: $TASMOTA_NEW_NAME ein.* >>$HOME/.config/micesttm/macros/de/macro
echo terminal_command: curl -m 2 "http://$NEW_IP/cm?cmnd=Power+on" >>$HOME/.config/micesttm/macros/de/macro
echo intern_command:  >>$HOME/.config/micesttm/macros/de/macro
echo tts: der $TASMOTA_NEW_NAME wurde eingeschaltet >>$HOME/.config/micesttm/macros/de/macro
echo "" >>$HOME/.config/micesttm/macros/de/macro
echo category: Tasmota >>$HOME/.config/micesttm/macros/de/macro
echo comment: $TASMOTA_NEW_NAME schalten >>$HOME/.config/micesttm/macros/de/macro
echo trigger: $TASMOTA_NEW_NAME aus.* >>$HOME/.config/micesttm/macros/de/macro
echo terminal_command: curl -m 2 "http://$NEW_IP/cm?cmnd=Power+off" >>$HOME/.config/micesttm/macros/de/macro
echo intern_command:  >>$HOME/.config/micesttm/macros/de/macro
echo tts: der $TASMOTA_NEW_NAME wurde ausgeschaltet >>$HOME/.config/micesttm/macros/de/macro


