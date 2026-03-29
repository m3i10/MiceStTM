#!/usr/bin/env python3
import re
import sys
import os
import time
import argparse

parser = argparse.ArgumentParser(description="")

# Füge Argumente hinzu

parser.add_argument(
	'-w', '--word', type=str,
	help='Word eingeben') 			#

args = parser.parse_args()
	  

def main():
	for i in range(0, 10):
		os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachlinks'")
		print('left')	
	
	
	for i in range(0, 2):
		os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachoben'")
		print('up')
	

	os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachunten'")
	print('down')
	time.sleep(5)

	

	for i in range(0, 2):
		os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachrechts'")
		print('right')

	os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachunten'")
	print('down')
		
	istZeile=1
	istReihe=1
	altReihe=0
	
	buchstabe_dict={
		"a": (1,1),"b": (1,2),"c": (1,3),"d": (1,4),"e": (1,5),"f": (1,6),"g": (1,7),
		"h": (2,1),"i": (2,2),"j": (2,3),"k": (2,4),"l": (2,5),"m": (2,6),"n": (2,7),
		"o": (3,1),"p": (3,2),"q": (3,3),"r": (3,4),"s": (3,5),"t": (3,6),"u": (3,7),
		"v": (4,1),"w": (4,2),"x": (4,3),"y": (4,4),"z": (4,5)," ": (5,1),"-": (1,8)
		}
	
	if args.word:
		for buchstabe in args.word:
			zZeile, zReihe = buchstabe_dict.get(buchstabe.lower())
			
				
			if buchstabe==" ":
				altReihe=istReihe
				istReihe=1


			sollZeile=istZeile-zZeile
			sollReihe=istReihe-zReihe
			
			
			if istZeile>3 and zZeile<3 and istReihe==1: #Buchstabe O und Ö sind 2 Zeilen
				sollZeile=sollZeile+1
			
			if istZeile>3 and zZeile<3 and istReihe==5: #Buchstabe s und ß sind 2 Zeilen
				sollZeile=sollZeile+1
				

			if istZeile==1 and zZeile>3 and istReihe==8: #von löschen nach Z
				sollReihe=sollReihe-1
			
			
			print(buchstabe + " " + str(sollZeile) + " " + str(istZeile))
			
			
			if sollZeile>0:
				for i in range(0, sollZeile):
					os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachoben'")
					print('up')
					time.sleep(.1)
					
			if sollZeile<0:
				sollZeile=sollZeile*-1
				for i in range(0, sollZeile):
					os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachunten'")
					print('down')
					time.sleep(.1)
			
			if sollReihe>0:
				for i in range(0, sollReihe):
					os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachlinks'")
					print('left')
					time.sleep(.1)	

			if sollReihe<0:
				sollReihe=sollReihe*-1
				for i in range(0, sollReihe):
					os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/nachrechts'")
					print('right')
					time.sleep(.1)
			
			if altReihe>0:
				zReihe=altReihe
				altReihe=0
				
			istZeile=zZeile
			istReihe=zReihe
			
			
			os.system("mosquitto_pub -h xxx.xxx.xxx.xxx -m 'replay' -t 'broadlink/Fernseher/enter'")
			time.sleep(.2)
			
if __name__ == "__main__":
	main()


