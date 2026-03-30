import os
import re
import configparser
import replacements

# read micesttm.ini
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'
cache_path = home_directory + "/.cache"

config = configparser.ConfigParser()
config.read(config_file_path)

piperModelDir = config['say']['piperModelDir']
max_tts_Filename = int(config['say']['max_tts_Filename'])

#tts_player =  ""
tts_player = config['micesttm']['tts_player']

def raw(tts):
	# Lambda für einfache Ersetzungen
	for old, new in replacements.tts.items():
		tts = tts.replace(old, new)
	
	print(tts)
	os.system('pkill piper')
	os.system('pkill play.py')
	
	os.system("echo '" + tts + "' | piper-tts --model " + piperModelDir + " --output-file " + "/dev/shm/say.wav && " + tts_player  + " /dev/shm/say.wav")
	print("echo '" + tts + "' | piper-tts --model " + piperModelDir + " --output-file " + "/dev/shm/say.wav  && " + tts_player  + " /dev/shm/say.wav")

def cache(tts, path = cache_path, filename = ''): # dieser Teil ist für Standart Ausgaben der Spracherkennung, um diese zu beschleunigen
	path = path + '/'
	# Lambda für einfache Ersetzungen
	for old, new in replacements.tts.items():
		tts = tts.replace(old, new)

	print(tts)
	os.system('pkill play.py')
	os.system('pkill piper')
	if filename == '':
		say_file = re.sub(r'[^a-zA-ZÄÖÜäöüß]\s', '', tts)[:max_tts_Filename]
	else:
		say_file = filename
		
	print(filename)
	
	if tts != '':
		if os.path.isfile(path + say_file + '.wav') == True:
			os.system(tts_player + " '" + path + say_file + ".wav'")
		else:
			os.system("echo '" + tts + "' | piper-tts --model " + piperModelDir + " --output-file '" + path + say_file + ".wav' && " +  tts_player + " '" + path + say_file + ".wav'")

