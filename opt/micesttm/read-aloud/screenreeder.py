#!/usr/bin/env python3
# Version 0.1 Okt 25
# der Text wird gelesen und gefiltert, abkürzungen werden verlängert. Zahlen
# so umgewandelt, dass sie langsam bzw. einzeln vorgelesen werden
# und dann in Sprache umgewandelt

import os
import time
import re
import cv2
import pytesseract
import numpy as np
import langdetect
import configparser

# read micesttm.ini
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'

config = configparser.ConfigParser()
config.read(config_file_path)

tesseract_language = config['language']['tesseract_language']
HomePath = "/dev/shm"
outputText = "screen_text"


os.system("rm /dev/shm/screenshot.wav")
os.system("rm /dev/shm/screenshot.png")

# ----------------------------------------------------------------------


# Mice mini Imports
import say

def add_commas_to_digits(text):
	# Funktion, die eine Ziffer in das Format mit Kommas umwandelt
	def replace_digit(match):
		digit = match.group()
		if len(digit) > 4:
			return ". ".join(digit)  # Fügt ein Komma zwischen jede Ziffer ein
		else:
			return digit
	# Ersetzt alle Ziffern im Text
	modified_text = re.sub(r'\d+', lambda m: replace_digit(m), text)
	return modified_text



# Hauptfunktion
def read_screen():
	command = "scrot -s /dev/shm/screenshot.png"
	os.system(command)
	
	# Bild laden
	image = cv2.imread("/dev/shm/screenshot.png")

	text = pytesseract.image_to_string(image, lang=tesseract_language)  # Verwenden Sie die deutsche Sprache
	return text
	quit()



# Main
lines = read_screen()

# folgende schritte sind nötig um die Sprachausgabe besser zu verstehen
lines =  re.sub(r'(\d+,\d+)\s+(\d+,\d+)', r'\1 und \2', lines) # 23,4 23,4 wird zu 23,3 - 23,3
lines = re.sub(r'(?<=\d) (?=\d)', '', lines) # 3443 34 23 wird zu 34433423

lines = add_commas_to_digits(lines)

text = ''
for line in lines:
	if not line:
		continue
	text=text + line
	
print(text)

# zurückspulen möglich

say.raw(text) # zurück und vorspulen können. Nach dem Scannen muss länger gewartet werden
