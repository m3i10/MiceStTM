#!/usr/bin/env python3
import pyaudio
import numpy as np
import time
import os
import subprocess
import configparser

# read micesttm.ini
home_directory = os.path.expanduser("~")
config_file_path = home_directory + '/.config/micesttm/micesttm.ini'

config = configparser.ConfigParser()
config.read(config_file_path)

# volume = int(config['micautogain']['volume'])
# micpegel = int(config['micautogain']['micpegel'])
max_micpegel = int(config['micautogain']['max_micpegel'])
max_amplitude = int(config['micautogain']['max_amplitude'])
starttime = time.time()

# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# eigene Import Datei my_watchdog
import my_watchdog
my_watchdog.program_name(os.path.basename(__file__))   # eigenen Dateiname 
											# ermitteln und initialisieren
# ----------------------------------------------------------------------


# Audio-Parameter
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

def get_volume(data):

	try:
		audio_data = np.frombuffer(data, dtype=np.int16)
		amplitude_value = np.max(np.abs(audio_data))
		return amplitude_value

	except Exception as e:
		print(f"Error: {e}")
		return 0.0


try:
	prz_micpegel = 0
	while True:
		data = stream.read(CHUNK)
		volume = get_volume(data)
		volume = 100 / max_amplitude * volume
		
		if volume < 5:  # Minimum-Pegel
			prz_micpegel += 10
		
		if volume < 10:  # Minimum-Pegel
			prz_micpegel += 5

		if volume < 30:  # Minimum-Pegel
			prz_micpegel += 1

		if volume > 50:  # Maximum-Pegel
			prz_micpegel -= 2

		if prz_micpegel>=40:
			if volume > 70:  # Maximum-Pegel
				prz_micpegel -= 5

			if volume > 80:  # Maximum-Pegel
				prz_micpegel -= 10

		if prz_micpegel >= 60:
			if volume > 90:  # Maximum-Pegel
				prz_micpegel -= 15
			
			if volume > 100:  # Maximum-Pegel
				prz_micpegel -= 20
				
		micpegel = max_micpegel / 100 * prz_micpegel
		if prz_micpegel <=1 :
			prz_micpegel = 1
		if prz_micpegel >=100 :
			prz_micpegel = 100
		#print (prz_micpegel)
		
		subprocess.run(["amixer", "-q", "set", "Capture", f"0,{micpegel}"])
		time.sleep(0.1)

		if my_watchdog.check_twice_started():  # wenn das Programm ein 2. Mal gestartet wird, werden alle beendet
			quit()

except KeyboardInterrupt:

	print("Quit Program")
# Stream und PyAudio schließen

stream.stop_stream()
stream.close()
p.terminate()
