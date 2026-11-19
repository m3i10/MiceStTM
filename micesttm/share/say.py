import os
import re
import configparser
import replacements
import hashlib
# In this case, the player must be a separate process. If you wish to stop the audio output from the outside, you can always do so using `pkill`.


# read micesttm.ini
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'
cache_path = home_directory + "/.cache"

config = configparser.ConfigParser()
config.read(config_file_path)

piperModelDir = config['say']['piperModelDir']
tempFile = "/dev/shm/say.wav"

tts_player = config['micesttm']['tts_player']

def raw(tts):

	for old, new in replacements.tts.items():
		tts = tts.replace(old, new)
	
	player = tts_player.split(" ", 1)[0]
	print("ttsplayer = " + player)
	os.system('pkill piper')
	os.system('pkill -f ' + player)
	
	os.system("echo '" + tts + "' | piper --model " + piperModelDir + " --output-file " + tempFile + " && " + tts_player  + " " + tempFile + " &")
	print("echo '" + tts + "' | piper --model " + piperModelDir + " --output-file " + tempFile + " && " + tts_player  + " " + tempFile + " &")

def cache(tts, path = cache_path, filename = ''): 
	path = path + '/'

	for old, new in replacements.tts.items():
		tts = tts.replace(old, new)
		
	player = tts_player.split(" ", 1)[0]
	print("ttsplayer = " + player)
	os.system('pkill piper')
	os.system('pkill -f ' + player)
	
	say_file = filename or hashlib.sha256(tts.encode('utf-8')).hexdigest()[:16]
		
	print(filename)
	
	if tts != '':
		if os.path.isfile(path + say_file + '.wav') == True:
			print(tts_player + " '" + path + say_file + ".wav'")
			os.system(tts_player + " '" + path + say_file + ".wav'")
		else:
			print("echo '" + tts + "' | piper --model " + piperModelDir + " --output-file '" + path + say_file + ".wav' && " +  tts_player + " '" + path + say_file + ".wav' &")
			os.system("echo '" + tts + "' | piper --model " + piperModelDir + " --output-file '" + path + say_file + ".wav' && " +  tts_player + " '" + path + say_file + ".wav' &")

