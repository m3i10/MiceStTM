#!/usr/bin/env python3
# Version Jan 2025

import time
import os
import sys

from pynput import mouse
from pathlib import Path
from PIL import Image

#-----------------------------------------------------------------------------------------------
# eigene Import Datei my_watchdog
import my_watchdog
my_watchdog.program_name(os.path.basename(__file__)) # eigenen Dateiname ermitteln und initialisieren
import say
#-----------------------------------------------------------------------------------------------
# Variablen initialisieren
# 

ram_cache_path = '/dev/shm/'

last_position = None
last_movement_time = time.time()
screenshot_delay = 0.1  # Zeit in Sekunden, um die Bewegung zu detektieren

sperre=0
def on_move(x, y):
	global last_position, last_movement_time, sperre
	sperre = 0
	if (last_position is None) or (last_position != (x, y)):
		last_position = (x, y)
		last_movement_time = time.time()

def take_screenshot():
	if last_position is not None:
		x, y = last_position

		# Screenshot erstellen und zuschneiden
		x1=int(x)-70
		y1=int(y)-20
		if x1<0:
			x1=0
		if y1<0:
			y1=0
		#convert /dev/shm/screenshot.png -negate out.png 
		os.system('pkill aplay')
		os.system('scrot -a ' + str(x1) + ',' + str(y1) + ',300,50 -o ' + ram_cache_path + 'screenshot_sw.png')
		os.system('tesseract ' + ram_cache_path + 'screenshot_sw.png ' + ram_cache_path + 'ausgabe -l deu --psm 6 2>/dev/zero')
		
		text=""
		with open(ram_cache_path + 'ausgabe.txt', 'r', encoding='utf-8') as datei:
			for zeile in datei:
				text = text + zeile
		say.raw(text)
		
# Mausüberwacher initialisieren
listener = mouse.Listener(on_move=on_move)
listener.start()


while True:
	# Überprüfen, ob die Maus 2 Sekunden lang nicht bewegt wurde
	if time.time() - last_movement_time >= screenshot_delay and sperre == 0:
		sperre = 1
		take_screenshot()
	time.sleep(0.1)  # Kurze Pause zur Entlastung der CPU
	
	if my_watchdog.check_twice_started():	# wenn das Programm ein 2. Mal gestartet wird, werden alle beendet
		listener.stop()
		quit()
			



