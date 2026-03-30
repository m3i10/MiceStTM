#!/bin/bash

# 1. Distribution erkennen
if [ -f /etc/arch-release ]; then
    PKG_MGR="pacman -S --noconfirm"
    AUR_MGR="pamac build --no-confirm" # oder yay -S
elif [ -f /etc/debian_version ]; then
    PKG_MGR="apt-get install -y"
    sudo apt-get update
elif [ -f /etc/fedora-release ]; then
    PKG_MGR="dnf install -y"
fi

# 2. System-Abhängigkeiten installieren
sudo $PKG_MGR wget unzip rsync python3-pip python3-tk xdotool scrot alsa-utils libatlas-base-dev tesseract-ocr tk

# Piper-TTS (AUR für Arch, sonst via pip am Ende)
if [ -n "$AUR_MGR" ]; then
    $AUR_MGR piper-tts-bin
fi

# 3. Dateien kopieren (inkl. versteckter Dateien via /.)
update.sh

# 4. Modelle laden
sudo mkdir -p /opt/micesttm/voice /opt/micesttm/model
cd /tmp

# Vosk Model
wget -N https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip -o vosk-model-small-de-0.15.zip
sudo mv vosk-model-small-de-0.15/* /opt/micesttm/model/

# Piper Voice
wget -N https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
wget -N https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
sudo mv de_DE-thorsten-high.onnx* /opt/micesttm/voice/

# 5. Python-Pakete (Zusammengefasst für Speed)
# Hinweis: re, argparse und queue sind Standard-Libraries und brauchen kein pip
pip3 install --break-system-packages numpy pyperclip vosk sounddevice \
scipy pytesseract opencv-python Pillow watchdog langdetect piper-tts \
pynput pyautogui pycairo pyscreenshot speechrecognition pyaudio
python3 -m pip install pathvalidate --break-system-packages

# 6. Test-Ausgabe
echo "Installation abgeschlossen. Teste Audio..."
echo "Das ist ein Test" | piper --model /opt/micesttm/voice/de_DE-thorsten-high.onnx --output_raw | aplay -r 22050 -f S16_LE -t raw

