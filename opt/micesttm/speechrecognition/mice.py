#!/usr/bin/env python3

# Version 27112025
# written by m3i10
# dieses Programm und die dazugehörigen my_watchdogs dürfen verbreitet und verändert werden.
# bei Veränderung aber stets zum Original Hinweisen und Namentlich erwähnen.
# siehe https://github.com/oliverguhr/deepmultilingualpunctuation für die automatische Punkt und Komma Setzung

#Lizenzvereinbarung

#Dieses Programm und die dazugehörigen my_watchdogs dürfen verbreitet und verändert werden. Bei jeder Art von Veränderung sind die folgenden Bedingungen zu beachten:

#    Urhebernennung: Bei jeglicher Veränderung des Originals muss auf das Originalprogramm verwiesen und der Name des ursprünglichen Autors genannt werden.

#    Verbreitung: Das Programm und seine my_watchdogs dürfen in unveränderter oder veränderter Form veröffentlicht und verteilt werden, solange die oben genannten Bedingungen eingehalten werden.

#    Haftungsausschluss: Der Autor des Originals übernimmt keine Haftung für etwaige Schäden oder Probleme, die aus der Verwendung dieser Software oder ihrer Modifikationen entstehen.

#    Keine zusätzliche Einschränkungen: Es dürfen keine zusätzlichen Einschränkungen auferlegt werden, die die Bedingungen dieser Vereinbarung widersprechen.

#Diese Bedingungen gelten für alle Versionen des Programms und seiner my_watchdogs.



# Standard Sprachausgaben auf Festplatte speichern und nicht neu generieren
# Sprachausgabe nicht auf Festplatte speichern, alle Zahlen und gesprochenen Sätze werden immer neu generiert
# bzw. im Ram gespeichert und werden beim nächsten booten neu generiert

#

# ---------------------------------------------------------------------------
import argparse
import os
import queue
import sounddevice as sd
import sys
import time
import re
import say
import json
import vosk
from vosk import Model, SpkModel, KaldiRecognizer
import numpy as np
#from pynput.keyboard import Controller


# ----------------------------------------------------------------------
import configparser
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'
config = configparser.ConfigParser()
config.read(config_file_path)

# signals
muteSpeaker = config['micesttm']['muteSpeaker']
unmuteSpeaker = config['micesttm']['unmuteSpeaker']
signal = config['micesttm']['signal']
tts_player = config['micesttm']['tts_player'] # for ping
wakewordini = config['micesttm']['wakeword']

# files
macro_path = config['micesttm']['macro_path']
main_macro_file = config['micesttm']['main_macro_file']
number_replace_file = config['micesttm']['number_replace_file']
speech_replace_file = config['micesttm']['speech_replace_file']
upper_word_list_file = config['micesttm']['upper_word_list_file']
speech_mode_path = config['micesttm']['speech_model_path']

# join paths
macro_path = macro_path.replace('$HOME', home_directory)
main_macro_file = macro_path + '/' +  main_macro_file
number_replace_file = macro_path + '/' +  number_replace_file
speech_replace_file = macro_path + '/' +  speech_replace_file
upper_word_list_file = macro_path + '/' +  upper_word_list_file


macro_file = main_macro_file
dictation_mode = False
write_mode = False

#-----------------------------------------------------------------------------------------------
# eigene Library my_watchdog
import my_watchdog
my_watchdog.program_name(os.path.basename(__file__)) # eigenen Dateiname ermitteln und initialisieren
#-----------------------------------------------------------------------------------------------


# Rechtschreibung und Punktation
#try:
#	from deepmultilingualpunctuation import PunctuationModel
#	pmodel = PunctuationModel()
#	punctation = True
#except:
#	print("no punctation model found")
#	punctation = False

# ermittel das Änderungsdatum der Groß-Klein Schreib Datenbank
# falls diese während der Laufzeit geändert wird, wird diese neu 
# eingelesen
current_modified_time = os.path.getmtime(upper_word_list_file)

# Groß Klein Schreib Datenbank einladen.
# diese wird nur für den Diktiermodus benötigt
# vosk Spracherkennung kann nur Kleinschreibung
with open(upper_word_list_file, 'r', encoding='utf-8') as input_file:
	words = {line.strip().lower() for line in input_file if line.strip()}


def replace_with_uppercase(match):
	try:
		word = match.group(0)
		if word.lower() in words:
			return word.capitalize()
		return word
	except:
		pass
		
# Großschreiben nach jedem Satzzeichen nur Diktiermodus
def punctuation(text): # Function mit KI Unterstützung geschrieben
	#text = pmodel.restore_punctuation(text) # eigene Datenbank wird jetzt genutzt, wesentlich schneller als KI
	try:
		sentences = re.split(r'([.!?])', text)  # Splitte den Text nach Satzzeichen
		capitalized_sentences = []
		for i in range(len(sentences)):
			if i % 2 == 0:  # Textteile (nicht Satzzeichen)
				sentence = sentences[i].strip()
				if sentence:  # Überprüfen, ob der Textteil nicht leer ist
					# Großschreibe nur den ersten Buchstaben des Satzes
					capitalized_sentence = sentence[0].upper() + sentence[1:] if sentence else ''
					capitalized_sentences.append(capitalized_sentence)
				else:
					capitalized_sentences.append(sentence)
			else:  # Satzzeichen
				capitalized_sentences.append(sentences[i] + " ")
		return ''.join(capitalized_sentences).strip()
	except Exception as e:
		print(f"Ein Fehler ist aufgetreten: {e}")
		return text  # Gebe den ursprünglichen Text zurück

# -------------------------------------------------------------------------------

# - write text with key simulation-----------------------------------------------
def writekey(text):
	keyboard = Controller()
	text = text.replace("\\n", "\n")
	for char in text:
		keyboard.type(char)
		time.sleep(0.02)
# -------------------------------------------------------------------------------

q = queue.Queue()
def parse_macros():
	macros_dict = {}
	errsaytword = ''
	try:
		with open(macro_file, 'r', encoding='utf-8') as file:
			lines = file.readlines()

		current_trigger = None
		current_commands = []

		for line in lines:
			line = line.strip()

			if not line:
				continue
			
			if line.startswith('trigger:'):
				# Füge den aktuellen Trigger zur Map hinzu, wenn es schon einen gibt
				if current_trigger is not None:
					macros_dict[current_trigger] = current_commands # zur Liste hinzufügen
				
				# Extrahiere den Trigger
				trigger_content = line.split(':', 1)[1].strip()
				# Trennung nach Leerzeichen, nur den ersten Teil verwenden
				trigger_parts = tuple(trigger_content.split())
				current_trigger = ', '.join([f'"{part}"' for part in trigger_parts])
				current_commands = [] # Lieste wieder löschen

			elif line.startswith('terminal_command:'):
				command_content = line.split(':', 1)[1].strip()
				current_commands.append(command_content)

			elif line.startswith('intern_command:'):
				command_content = line.split(':', 1)[1].strip()
				current_commands.append(command_content)

			elif line.startswith('tts:'):
				command_content = line.split(':', 1)[1].strip()
				current_commands.append(command_content)

		# Füge den letzten Trigger hinzu, wenn vorhanden
		if current_trigger is not None:
			# Hier ist die Bedingung gelockert, sodass der Trigger auch ohne Befehle hinzugefügt wird
			macros_dict[current_trigger] = current_commands
	except:
		print('')
		print('*****************************')
		print('Error: in ' + macro_file)
		print('input error in:')
		print(errsaytword)
		os.system(unmuteSpeaker)
		os.system(tts_player + ' ' + signal + ' &')
		time.sleep(0.2)
		os.system(tts_player + ' ' + signal + ' &')
		os.system("echo Fehler in der Makro Liste! " + macro_file + "! die Zeile!" + errsaytword + " >error.txt")
		print('*****************************')
		print('')
	return macros_dict
	
def Check_trigger(trigger_words, speechtext): # Funktion mit KI Unterstützung geschrieben
	try:
		errsaytword = trigger_words.lower()
		trigger_words=eval("[" + trigger_words.lower() + "]")
		# Erzeuge den Regex-Ausdruck dynamisch basierend auf der Liste
		trigger_patterns = ''.join(f'(?=.*\\b({word})\\b)' for word in trigger_words)
		triggertext = r'^(?=.*\b)(?=.*\b){}'.format(trigger_patterns)

		trigger_words = str(trigger_words).translate(str.maketrans("", "", "[]'().*,"))  # Entfernt die angegebenen Zeichen		trigger_words = trigger_words.replace("|", " ")
		trigger_words = trigger_words.replace("|", " ")
				
		# Überprüfen, ob die Trigger-Wörter im speechtext vorhanden sind
		if re.search(triggertext, speechtext.lower()):
			# Finde die Position des letzten Trigger-Wortes
			max_pos = max((speechtext.lower().find(word) for word in trigger_words.split() if speechtext.lower().find(word) >= 0), default=0)
			
			last_trigger_pos = max_pos
			# Den restlichen Text nach dem letzten Trigger-Wort extrahieren
			
			return speechtext[last_trigger_pos + len(speechtext[last_trigger_pos:].split()[0]):].strip()
		else:
			return "none"
	except:
		print('')
		print('*****************************')
		print('Error: in ' + macro_file)
		print('input error in:')
		print(errsaytword)
		os.system(unmuteSpeaker)
		os.system(tts_player + ' ' + signal + ' &')
		print(tts_player + ' ' + signal + ' &')
		time.sleep(0.2)
		os.system(tts_player + ' ' + signal + ' &')
		os.system("echo Fehler in der Makro Liste! " + macro_file + "! die Zeile!" + errsaytword + " >error.txt")
		print('*****************************')
		print('')
	return "none"

		
# Main()

def number_replace(speechtext):
	with open(number_replace_file, 'r', encoding='utf-8') as datei:
		for zeile in datei:
			zeile = zeile.lower()[:-1]
			if zeile.find('#') == -1:
				um = zeile.split('(->)')
				if len(um)>1:
					speechtext = speechtext.lower().replace(um[0], um[1])
					speechtext = ' '.join(speechtext.split())
	datei.close()
	speechtext = speechtext.replace(' .', '.')

	print(speechtext)
	
	return speechtext.replace('. ', '.')

def speech_replace(speechtext):
	try:
		with open(speech_replace_file, 'r', encoding='utf-8') as datei:
			for zeile in datei:
				zeile = zeile.strip()  # Entferne führende und nachfolgende Leerzeichen
				um = zeile.split('(->)')
				if um[0].find('#') != 0 and um[0] != '':
					if len(um) > 1:  # Überprüfe, ob es mehr als ein Element gibt
						speechtext = " " + speechtext + " "
						if "{delspace}" in speechtext:
							speechtext = speechtext.replace(" " + um[0] + " ", um[1] + " ")
						else:
							speechtext = speechtext.replace(" " + um[0] + " ", " " + um[1] + " ")
						# Doppelte Leerzeichen entfernen
						speechtext = ' '.join(speechtext.split())

		speechtext = speechtext.replace('{space}', ' ')
		speechtext = speechtext.replace('{->}', '(->)')

		if "{delspace}" in speechtext:  # Überprüfe, ob der Platzhalter vorhanden ist
			speechtext = speechtext.replace('{delspace} ', '')
			speechtext = speechtext.replace(' {delspace}', '')
			speechtext = speechtext.replace('{delspace}', '')

		print("speech replace:")
		print(speechtext)
		return speechtext
	except Exception as e:  # Fange spezifische Ausnahmen
		print(f"Ein Fehler ist aufgetreten: {e}")

def calculate_string(input_string):

	for i in range(1,10):
		input_string = re.sub(r'(\d+)\s*\.\s*(\d+)\s*(\d+)?', lambda m: f"{m.group(1)}.{m.group(2)}{m.group(3) if m.group(3) else ''}", input_string) # KI U
	
	# Entferne Leerzeichen zwischen Ziffern
	input_string = re.sub(r'(\d+)\s+', r'\1 ', input_string)  # Ziffern vor Leerzeichen # KI Z.
	input_string = re.sub(r'\s+(\d+)', r' \1', input_string)  # Ziffern nach Leerzeichen # KI U.
	
	# Ersetze Leerzeichen zwischen Ziffern und Operatoren
	input_string = re.sub(r'\s*([\+\-\*/])\s*', r' \1 ', input_string)  # Operatoren KI U.
	# 
	if input_string.find('*')>0:
		input_string = '(' + input_string + ')'
	if input_string.find('+')>0:
		input_string = '(' + input_string + ')'
		
	if input_string.find('/')>0:
		input_string = '(' + input_string + ')'
	if input_string.find('-')>0:
		input_string = '(' + input_string + ')'
	
	input_string = input_string.replace('+', ')+(')
	input_string = input_string.replace('*', ')*(')
	
	input_string = input_string.replace('-', ')-(')
	input_string = input_string.replace('/', ')/(')


	
	input_string = input_string.replace('1000', ')*1000')
	if input_string.find('1000')>0:
		input_string = '(' + input_string
	input_string = re.sub(r'\s+', ' ', input_string).strip() # doppelte leerzeichen entfernen
	input_string = input_string.replace(' 100', '*100 ')
	input_string = input_string.replace('1000*100', '1000+100')  
	input_string = input_string.replace(' ', '+')
	input_string = input_string.replace('()', '')
	input_string = input_string.replace('+.+', '.')
	input_string = input_string.strip('+*')
	input_string = input_string.replace('++', '+')
	input_string = re.sub(r'\+\)', ')', input_string)
	input_string = input_string.replace('(*', '(')
	input_string = input_string.replace('+*+', '*')
	input_string = input_string.replace('()', '(1)')
	print ("input string: " + input_string)
	
	value = round(eval(input_string),7)	
	return value



def load_macro(speechtext):
	global dictation_mode, write_mode
	global macro_file
	global macro_path
	triggertext=""

	sh = parse_macros() # Makro Datei auslesen und in sh übergeben

	for triggertext in list(sh):
		last_spoken_number = "1"
		last_spoken_text = ""
		try:		
			last_spoken_text = Check_trigger(triggertext, speechtext)
			# vor komma frage zeichen usw. leerstelle entfernen, wichtig bei der Diktierfunktion
			for zeichen in ".,;:?(":
				last_spoken_text = last_spoken_text.replace(' ' + zeichen, zeichen)
			
		except:
			print('Error: in ' + macro_file)
			print('input error in:')
			print(triggertext)
			return 0

		if last_spoken_text!="none":
			terminal_command = sh[triggertext][0]
			intern_command = sh[triggertext][1]
			tts = sh[triggertext][2]
			
			# schauen, ob eine andere datei als macro genutzt werden soll
			intern_command_list = 'repeat calc spell puncture'
			find_cmd = 0
			for cmd_list in intern_command_list.split():
				if intern_command.find(cmd_list) > -1 or intern_command == "" :
					find_cmd = find_cmd + 1
						
			if find_cmd == 0:
				macro_file = macro_path + '/' +  intern_command
				dictation_mode = True
			
			if macro_file == main_macro_file: 	# deaktiviere mit wakeword
				dictation_mode = False
			change_numbers=False
			
			if intern_command.find("write") >= 0: 	# im Dateinamen write bedeutet dauerhaft schreiben können
				write_mode = True					# deaktivieren mit wakeword
				
			if intern_command.find("spell") >= 0:
				last_spoken_text = last_spoken_text.replace(' ', '') # spell remove space
				
			if intern_command.find("puncture") >= 0: # Groß Kleinschreibung aktivieren
				# erstmal die Punktation
				if last_spoken_text.find("{nopuncture}") == -1 and len(last_spoken_text) > 3:
					last_spoken_text = punctuation(last_spoken_text)  # Großschreibung nach Satzzeichen 
				last_spoken_text = last_spoken_text.replace("{nopuncture}", "")
			
			print("dictation_mode: " + str(dictation_mode))
			print("write_mode: " + str(write_mode)	)
			#----------------------------------------------------------------
			
			
			placeholders = ['{last_spoken_number}', '{last_spoken_numeral}', '{last_spoken_text}', 'repeat']
			if any(placeholder in tts or placeholder in terminal_command or intern_command for placeholder in placeholders):
				change_numbers=True
				speechtext = number_replace(speechtext) # geschr. zahlen werden in zahlen
				print("numberreplcae")
				print(speechtext)

				try:
					last_spoken_number = re.sub(r'[a-zA-ZäüöÄÜÖß]', '', speechtext).strip('+').strip('*')
					last_spoken_numeral = re.sub(r'[a-zA-ZüöäÜÖÄß ]', '', speechtext).strip('+').strip('*')

					last_spoken_number = str(calculate_string(last_spoken_number))
					if intern_command.find('calc') >=0:
						last_spoken_number = last_spoken_number.replace(".", ",")			
				except:
					pass
			try:
				# wenn der Text übergeben werden soll
				tts = tts.replace('{last_spoken_text}', last_spoken_text)
				terminal_command = terminal_command.replace('{last_spoken_text}', last_spoken_text)
				
				# wenn die Zahl übergeben werden soll um Werte zu ändern				
				tts = tts.replace('{last_spoken_number}', last_spoken_number)
				terminal_command = terminal_command.replace('{last_spoken_number}', last_spoken_number)
			
				# einzelne Ziffern ändern
				tts = tts.replace('{last_spoken_numeral}', last_spoken_numeral)
				terminal_command = terminal_command.replace('{last_spoken_numeral}', last_spoken_numeral)
			except:
				pass
			
			print("Command is found")
			print("Output:")
			print(terminal_command)
			print(intern_command)
			os.system(unmuteSpeaker)

			try:
				repeats = int(last_spoken_number)
			except:
				repeats = 1
			if intern_command == 'repeat':
				for i in range(repeats):
					time.sleep(0.03)
					print(terminal_command)
					if terminal_command != '':
						os.system(terminal_command + " &")

			else:
				print('tts:')
				print(tts)
				print('tts end')
				print(terminal_command)
				if terminal_command != '':
					os.system(terminal_command + " &")
					
				if tts != '':
					if change_numbers == True:
						say.raw(tts)
					else:
						say.cache(tts)

			print()
			print("Variable:")
			print(last_spoken_text)
			print(last_spoken_number)
			print(str(dictation_mode) + ' ' + macro_file)
			if dictation_mode == True:
				time.sleep(2)
			return True
	
	# wenn kein Befehl erkannt wurde und der Schreibmodus ist eingeschaltet
	# so wird er alles schreiben was er hört
	if write_mode == True:
		if speechtext.find("{nopuncture}") == -1 and len(speechtext) > 3:
				speechtext = punctuation(speechtext)  # Großschreibung nach Satzzeichen 
		speechtext = speechtext.replace("{nopuncture}", "")
		#writekey(speechtext)
		return True
			
				
def int_or_str(text):
	"""Helper function for argument parsing."""
	try:
		return int(text)
	except ValueError:
		return text


def callback(indata, frames, time, status):
	"""This is called (from a separate thread) for each audio block."""
	#if status:
		#print(status, file=sys.stderr)
	q.put(bytes(indata))


def speech_conversion(message):
	global ready_to_recive
	global wait_window
	global speech_wait_time
	global listening
	
	speech_text = speech_replace(message)
	speech_text = re.sub(r'\b(\w+)\b', replace_with_uppercase, speech_text)
	
	if load_macro(speech_text)==True:
		ready_to_recive=False
		wait_window = time.time()
		speech_wait_time = time.time()
		listening = False
		rec.Reset()

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
	'-l', '--list-devices', action='store_true',
	help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
	print(sd.query_devices())
	parser.exit(0)
parser = argparse.ArgumentParser(
	description=__doc__,
	formatter_class=argparse.RawDescriptionHelpFormatter,
	parents=[parser])
parser.add_argument(
	'-f', '--filename', type=str, metavar='FILENAME',
	help='audio file to store recording to')
parser.add_argument(
	'-m', '--model', type=str, metavar='MODEL_PATH',
	help='Path to the model')
parser.add_argument(
	'-w', '--wakeword', type=str, metavar='WAKEWORD',
	help='Wakeword for command')
parser.add_argument(
	'-d', '--device', type=int_or_str,
	help='input device (numeric ID or substring)')
parser.add_argument(
	'-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)

# pipeout = os.open("pipename", O_WRONLY)
if args.wakeword==None:
	args.wakeword = wakewordini
	
print(args.wakeword)

try:
	if args.model is None:
		args.model = speech_mode_path
	if not os.path.exists(args.model):
		print ("Please download a model for your language from https://alphacephei.com/vosk/models")
		print ("and unpack as 'model' in the current folder.")
		parser.exit(0)
	if args.samplerate is None:
		device_info = sd.query_devices(args.device, 'input')
		args.samplerate = int(device_info['default_samplerate'])

	model = Model(args.model)
	#spk_model = SpkModel("/opt/micesttm/model-spk")

	if args.filename:
		dump_fn = open(args.filename, "wb")
	else:
		dump_fn = None
	
	with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device, dtype='int16',
							channels=1, callback=callback):
								
			# Variablen intitialisieren
			ready_to_recive = False
			old_message = ''
			speech_text = ''
			message=''
			wait_window = 0.0
			speech_wait_time = 0.0
			macro_file_bak = ''			

			rec = vosk.KaldiRecognizer(model, args.samplerate)#, grammar_json)
			#rec.SetSpkModel(spk_model)
#_________________________________________________________________________________________________________________________
			
			while True:
				data = q.get()
				 
				# Berechnen der Lautstärke wieder entfernt. Dies sollte zunächst reagieren um nicht ständig
				# auf Bereitschaft zu sein. Hatte keine Vorteile
				
				# falls die Großschreibdatenbank ergänzt wurde, wird diese neu geladen
				current_modified_time_last = os.path.getmtime(upper_word_list_file)
				if current_modified_time_last != current_modified_time:
					with open(upper_word_list_file, 'r', encoding='utf-8') as input_file:
						words = {line.strip().lower() for line in input_file if line.strip()}
					current_modified_time = os.path.getmtime(upper_word_list_file) # änderungsdatum erkennen
				
				
				# wird kein trigger erkannt hat man ca 10-15 Sek. Zeit sich zu wiederholen 30/2	
				if time.time() - wait_window > 10:
					ready_to_recive = False
					wait_window = time.time()
					listening = False
					os.system(unmuteSpeaker)
				
				
				# Dictationmode
				if dictation_mode == True:
					ready_to_recive = True
				# -------------
				
				# RAM Remote; diktiermodus über diese datei einschalten/genutzt für den Makroeditor
				if os.path.exists("/dev/shm/micesttm-dictationmode"):
					macro_file_bak = macro_file
					
					with open("/dev/shm/micesttm-dictationmode", 'r') as file:
						content = file.read()
						if content.find("write") >= 0:
							dictation_mode = True
							write_mode = True
							macro_file = content.replace('$HOME', home_directory)
						else:
							macro_file = content.replace('$HOME', home_directory)
				else:
					if len(macro_file_bak) > 0:
						macro_file = macro_file_bak
						dictation_mode = False
						write_mode = False
						macro_file_bak = ""
						
				#------------
				
				if rec.AcceptWaveform(data):
					speech_text = json.loads(rec.Result())["text"]
					
						
					if ready_to_recive == True and speech_text != '':
						speech_conversion(speech_text) #Groß Kleinschr. wird auch bearbeitet

				else:
					message = json.loads(rec.PartialResult())["partial"] # + " "
					if message == 'nun':
						message = ''
						rec.Reset()
						
					if old_message != message:
						if len(message) >=1:
							print(message)
							
						speech_wait_time = time.time() #ein warte Fenster erstellen, da oft zu lange gewartet wird
						
					old_message = message
					
					# Wake Word wird erkannt
					if message.lower().find(args.wakeword)>=0:
						macro_file = main_macro_file		# zurück zur Hauptmakrofile, und Diktiermodus beenden
						dictation_mode = False
						write_mode = False
						os.system(unmuteSpeaker)
						os.system(tts_player + ' ' + signal + ' &')
						time.sleep(0.2)
						os.system(muteSpeaker)
						ready_to_recive=True
						wait_window = time.time()
						speech_wait_time = time.time()
						rec.Reset()
						
					# wenn re.AcceptWaveform nicht greift, was häufig passiert, dann greift die folgende
					# man hört auf zu sprechen und nach ca. 1,5 sek wird das Kommando ausgeführt
					
					if (time.time() - speech_wait_time > 2) and (ready_to_recive == True) and message != '':
						speech_conversion(message)
							
				if dump_fn is not None:
					dump_fn.write(data)
			
				if my_watchdog.check_twice_started():	# wenn das Programm ein 2. Mal gestartet wird, werden alle beendet
					print('\nDone')
					parser.exit(0)
					parser.exit(type(e).__name__ + ': ' + str(e))
					quit()


except KeyboardInterrupt:
	print('\nDone')
	parser.exit(0)
except Exception as e:
	parser.exit(type(e).__name__ + ': ' + str(e))
