!#/bin/bash
# Test Version(Notiz)

cp -r home/MiceStTM $HOME/
cp -r home/.config $HOME/
sudo cp -r opt/micesttm /opt

sudo mkdir /opt/micesttm/voice
sudo mkdir /opt/micesttm/model
wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
sudo unzip vosk-model-small-de-0.15.zip -d /opt/micesttm
sudo mv /opt/micesttm/vosk-model-small-de-0.15 /opt/micesttm/model
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx
sudo cp de_DE-thorsten-high.onnx de_DE-thorsten-high.onnx.json /opt/micesttm/voice
pamac build piper-tts-bin
sudo pacman -S tk

sudo pacman -S xdotool
sudo pacman -S scrot

echo "das ist ein Test!" | piper-tts --model /opt/micesttm/voice/de_DE-thorsten-high.onnx --output_raw |aplay -r 22050 -f S16_LE -t raw

pip3 install numpy --break-system-packages

pip3 install pyperclip --break-system-packages
pip3 install vosk --break-system-packages
pip3 install re --break-system-packages
pip3 install sounddevice --break-system-packages
pip3 install argparse --break-system-packages
pip3 install queue --break-system-packages
pip3 install scipy --break-system-packages
pip3 install pytesseract opencv-python Pillow --break-system-packages
pip3 install watchdog --break-system-packages
pip3 install langdetect --break-system-packages
pip3 install piper-tts --break-system-packages
pip3 install pynput --break-system-packages
pip3 install pyautogui --break-system-packages
pip3 install pycairo --break-system-packages
pip3 install pyscreenshot --break-system-packages
pip3 install speechrecognition --break-system-packages
pip3 install pyaudio --break-system-packages
