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
		os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachlinks'")
		print('left')	
	
	
	for i in range(0, 2):
		os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachoben'")
		print('up')
	

	os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachunten'")
	print('down')
	time.sleep(5)

	

	for i in range(0, 2):
		os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachrechts'")	
		print('right')

	os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachunten'")
	print('down')
		
	istZeile=1
	istReihe=1
	altReihe=0
	if args.word:
		for buchstabe in args.word:
			if buchstabe.lower()=="a":
				zZeile=1
				zReihe=1

			if buchstabe.lower()=="b":
				zZeile=1
				zReihe=2
				
			if buchstabe.lower()=="c":
				zZeile=1
				zReihe=3

			if buchstabe.lower()=="d":
				zZeile=1
				zReihe=4
				
			if buchstabe.lower()=="e":
				zZeile=1
				zReihe=5

			if buchstabe.lower()=="f":
				zZeile=1
				zReihe=6
				
			if buchstabe.lower()=="g":
				zZeile=1
				zReihe=7

			if buchstabe.lower()=="h":
				zZeile=2
				zReihe=1
				
			if buchstabe.lower()=="i":
				zZeile=2
				zReihe=2

			if buchstabe.lower()=="j":
				zZeile=2
				zReihe=3
				
			if buchstabe.lower()=="k":
				zZeile=2
				zReihe=4

			if buchstabe.lower()=="l":
				zZeile=2
				zReihe=5
			if buchstabe.lower()=="m":
				zZeile=2
				zReihe=6

			if buchstabe.lower()=="n":
				zZeile=2
				zReihe=7
				
			if buchstabe.lower()=="o":
				zZeile=3
				zReihe=1

			if buchstabe.lower()=="p":
				zZeile=3
				zReihe=2
			if buchstabe.lower()=="q":
				zZeile=3
				zReihe=3

			if buchstabe.lower()=="r":
				zZeile=3
				zReihe=4
				
			if buchstabe.lower()=="s":
				zZeile=3
				zReihe=5

			if buchstabe.lower()=="t":
				zZeile=3
				zReihe=6

			if buchstabe.lower()=="u":
				zZeile=3
				zReihe=7
				
			if buchstabe.lower()=="v":
				zZeile=4
				zReihe=1

			if buchstabe.lower()=="w":
				zZeile=4
				zReihe=2
				
			if buchstabe.lower()=="x":
				zZeile=4
				zReihe=3

			if buchstabe.lower()=="y":
				zZeile=4
				zReihe=4
			if buchstabe.lower()=="z":
				zZeile=4
				zReihe=5
				
			if buchstabe.lower()==" ":
				zZeile=5
				zReihe=1
				altReihe=istReihe
				istReihe=1

			
			sollZeile=istZeile-zZeile
			sollReihe=istReihe-zReihe
			
			
			if istZeile>3 and zZeile<3 and istReihe==1: #Buchstabe O und Ö sind 2 Zeilen
				sollZeile=sollZeile+1
			
			if istZeile>3 and zZeile<3 and istReihe==5: #Buchstabe s und ß sind 2 Zeilen
				sollZeile=sollZeile+1
				
			
			
			print(buchstabe + " " + str(sollZeile) + " " + str(istZeile))
			
			
			if sollZeile>0:
				for i in range(0, sollZeile):
					os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachoben'")
					print('up')
					time.sleep(.3)
					
			if sollZeile<0:
				sollZeile=sollZeile*-1
				for i in range(0, sollZeile):
					os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachunten'")
					print('down')
					time.sleep(.3)
			
			if sollReihe>0:
				for i in range(0, sollReihe):
					os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachlinks'")
					print('left')
					time.sleep(.3)	

			if sollReihe<0:
				sollReihe=sollReihe*-1
				for i in range(0, sollReihe):
					os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/nachrechts'")	
					print('right')
					time.sleep(.3)
			
			if altReihe>0:
				zReihe=altReihe
				altReihe=0
				
			istZeile=zZeile
			istReihe=zReihe
					
			os.system("mosquitto_pub -h 192.168.0.21 -m 'replay' -t 'broadlink/Fernseher/enter'")
			time.sleep(.5)
			
if __name__ == "__main__":
	main()

# if w then yz=3: xz=1...
# ypos=1 xpos=7
# ysoll=ypos-yz
# l l l l o o  o o u r r u

