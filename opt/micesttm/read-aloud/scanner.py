#!/usr/bin/env python3
# Version 0.3 Jan 25
# das Script scannt einen Brief, dreht diesen bis eine Sprache deutsch erkannt wird.
# der Text wird gelesen und gefiltert, abkürzungen werden verlängert. Zahlen
# so umgewandelt, dass sie langsam bzw. einzeln vorgelesen werden
# und dann in Sprache umgewandelt

import subprocess
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

language = config['language']['scanner_language']
tesseract_language = config['language']['tesseract_language']
HomePath = home_directory + config['scanner']['outputDir']
outputText = config['scanner']['outputText']


original = os.path.join(HomePath, config['scanner']['original'])
original_rotate = os.path.join(HomePath, config['scanner']['original_rotate'])
rotate_invert = os.path.join(HomePath, config['scanner']['rotate_invert'])
say_scan_letter = config['scanner']['say_scan_letter']
say_error_no_scanner_found = config['scanner']['say_error_no_scanner_found']
say_please_wait = config['scanner']['say_please_wait']
say_path_not_found = config['scanner']['say_path_not_found']
os.system("rm + " + HomePath + "/" + outputText + ".wav")

# ----------------------------------------------------------------------


# Mice mini Imports
import say
#
if os.path.isdir(HomePath) == False:
	say.raw(say_path_not_found)
	quit()

def execute_command(command):
    try:
        # Führe den Befehl aus und speichere die Ausgabe und Fehler
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        
        # Gibt die Standardausgabe zurück
        output = result.stdout
        return output, None  # Rückgabe der Ausgabe und None für den Fehler
    except subprocess.CalledProcessError as e:
        # Wenn ein Fehler auftritt, speichere den Fehler
        error_message = e.stderr
        return None, error_message  # Rückgabe von None für die Ausgabe und dem F

def get_skew_angle(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	_, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
	kernel = np.ones((5, 5), np.uint8)
	binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

	coords = np.column_stack(np.where(binary > 0))
	if coords.size == 0:
		return 0  # kein Text gefunden

	angle = cv2.minAreaRect(coords)[-1]

	if angle < -45:
		angle = -(90 + angle)
	else:
		angle = -angle	
	return angle
		
def rotate_image(image, angle):
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
	return rotated

def validate_text(text):
	try:
		lang = langdetect.detect(text)
		if lang == language:
			return True
	except Exception as e:
		print(e)
	return False

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
def read_scanner():
	say.raw(say_scan_letter)
	
	command = "scanimage --format=png --resolution=300 --mode=color -l 0 -t 0 -x 215 -y 297 --mode Gray --depth 16 --resolution 300 --calibration-cache=yes --brightness 100 > " + original
	output, error = execute_command(command)

	print(error)
	if error!=None:
		say.raw(say_error_no_scanner_found)
		time.sleep(5)
		quit()
		
	# Bild laden
	image = cv2.imread(original)

	# Versuche, den Text mit mehreren Rotationen zu erkennen
	for attempt in range(3):  # Maximal 3 Versuche
		text = pytesseract.image_to_string(image, lang=tesseract_language)  # Verwenden Sie die deutsche Sprache
		print(text)
		if validate_text(text):
			say.raw(say_please_wait)

			os.system('echo "' + text + '" >' + HomePath + "/" + outputText)
			# gedrehtes Bild speichern
			cv2.imwrite(original_rotate, image)
			# Bild invertieren
			inverted_image = cv2.bitwise_not(image)
			# invertiertes Bild speichern
			cv2.imwrite(rotate_invert, inverted_image)
			# Validieren Sie den Text auf Deutsch

			return text  # Erfolgreiche Erkennung
		
		# Wenn der Text nicht erkannt wurde, drehen Sie das Bild um 180 Grad
		say.raw(say_please_wait)
		image = rotate_image(image, 180)  # Bild um 180 Grad drehen
	quit()



# Main
lines = read_scanner()

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
