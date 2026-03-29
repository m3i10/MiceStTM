#!/usr/bin/env python3
import time
#import subprocess
import re
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import say
import configparser

# read micesttm.ini
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'

config = configparser.ConfigParser()
config.read(config_file_path)

path = config['file_read__watcher']['path_to_watch']
path = path.replace('$HOME', home_directory)

#-----------------------------------------------------------------------------------------------
# eigene Import Datei my_watchdog
import my_watchdog
my_watchdog.program_name(os.path.basename(__file__)) # eigenen Dateiname ermitteln und initialisieren
#-----------------------------------------------------------------------------------------------


# Definiere den Handler für die überwachten Ereignisse
# dieser Teil ist per KI generiert und manuell angepasst
class MyHandler(FileSystemEventHandler):
	def on_modified(self, event):
		if not event.is_directory:  # Ignoriere Verzeichnisse
			print(f'{event.src_path} wurde geändert.')
			self.start_program(event.src_path)

	def on_created(self, event):
		if not event.is_directory:
			print(f'{event.src_path} wurde erstellt.')
			self.start_program(event.src_path)

	def on_deleted(self, event):
		if not event.is_directory:
			print(f'{event.src_path} wurde gelöscht.')

	def start_program(self, filepath):
		# Ersetze 'dein_programm' durch den Befehl, den du starten möchtest
		print(f'Starte Programm für: {filepath}')
		# Beispiel: subprocess.run(['dein_programm', filepath])
		
		if filepath.find('.jpg')>0 or filepath.find('.png')>0 or filepath.find('.bmp')>0:
			os.system('tesseract "' + filepath + '" ' '/tmp/out -l deu')
			print('tesseract "' + filepath + '" ' + '/tmp/out -l deu')
			outfile= '/tmp/out.txt'
		else:
			outfile=filepath
			
		try:
			lines=""
			with open(outfile, 'r', encoding='utf-8') as datei:
				for zeile in datei:
					lines = lines + zeile
			datei.close()
			print(lines)

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

			if text!="":
				say.raw(text)
				os.remove(filepath)
		except:
			try:
				os.remove(filepath)
			except:
				pass
			print('Error: I do nothing')
# KI gen. und man angepasst
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


# Initialisiere Observer und Handler
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=False)

# Starte den Observer
observer.start()
print(f'Überwache das Verzeichnis: {path}')

try:
	while True:
		if my_watchdog.check_twice_started():  # wenn das Programm ein 2. Mal gestartet wird, werden alle beendet
			quit()
		time.sleep(2)  # Das Hauptprogramm schläft alle 10 Sekunden
except KeyboardInterrupt:
	observer.stop()
observer.join()
