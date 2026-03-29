import re
import sys
import os
import argparse

parser = argparse.ArgumentParser(description="")

# Füge Argumente hinzu

parser.add_argument(
	'-f', '--filename', type=str,
	help='Makro Datei die bearbeitet werden soll') 			#
parser.add_argument(
	'-o', '--overwrite',  action='store_true',
	help='vorhandenen Sprachtrigger löschen und ersetzen') 	#
parser.add_argument(
	'-u', '--update', action='store_true',
	help='vorhandenen Sprachtrigger ergänzen')				#
parser.add_argument(
	'-a', '--add', action='store_true',
	help='neues Makro erstellen, benötigt min. -n')					#
parser.add_argument(
	'-d', '--deltrigger', action='store_true',
	help='lösche vorhandenes Makro, benötigt min. -e')		#
parser.add_argument(
	'-l', '--listtrigger', action='store_true',
	help='nach Trigger listen')								#
#parser.add_argument(
#	'--defrag', action='store_true',
#	help='Macro Liste aufräumen')			
parser.add_argument(
	'-e', '--existtrigger', type=str,
	help='Trigger der bearbeitet werden soll')				#
parser.add_argument(
	'-t', '--newtrigger', type=str,
	help='neuer Trigger')									#
parser.add_argument(
	'-c', '--category', type=str,
	help='neue Kategorie')			
parser.add_argument(
	'-m', '--comment', type=str,
	help='neuer Kommentar')									#
parser.add_argument(
	'-g', '--terminalcommand', type=str,
	help='neuer Terminalkommando')							#		
parser.add_argument(
	'-i', '--interncommand', type=str,
	help='neuer internes Kommando')							#		
parser.add_argument(
	'-b', '--feedback', type=str,
	help='neuer Feedback tts')
args = parser.parse_args()

inhalt=[]

def save_file():
	if len(inhalt) > 5:
		with open(args.filename, 'w') as datei:
			datei.writelines(inhalt)
	else:
		print('nothing to do!')

def extend_existing_words(existwords, new_words):
	pattern = r"\((.*?)\)"
	matches = re.findall(pattern, existwords)
	#if not matches:
	#	raise ValueError("Das Format von existwords ist ungültig.")

	groups = [group.split('|') for group in matches]
	  
	word_list = new_words.split()
	for i, word in enumerate(word_list):
		if i < len(groups):
			groups[i].append(word)
		else:
			groups.append([word])

	new_existwords = ' '.join([f"({'|'.join(sorted(set(group)))})" for group in groups])
	return new_existwords

def main():
	global inhalt
	
	if args.listtrigger:
		os.system("cat " + args.filename + " | grep trigger:")
		quit()	
	
	new_words = args.newtrigger
	
	if args.existtrigger:
		woerter = args.existtrigger.split()
		woerter_mit_klammern = [f'({wort})' for wort in woerter]
		existwords = ' '.join(woerter_mit_klammern)
		existwords = existwords.replace("((", "(")
		existwords = existwords.replace("))", ")")
	
	terminal_command = args.terminalcommand
	if terminal_command is not None:
		terminal_command = terminal_command.replace("[sqm]", "'")
	args.terminalcommand = terminal_command
	output = ''
	try:
		output = extend_existing_words(existwords, new_words)
	except:
		pass
		
	if args.filename:
		try:
			with open(args.filename, 'r', encoding='utf-8') as datei:
				inhalt = datei.readlines()
		except:
			print("file not found!")
			quit()
		
		find_index=0
		
		if args.deltrigger:
			finde=0
			if args.existtrigger:
				for index, zeile in enumerate(inhalt):
					zeile=zeile.rstrip()
					if zeile.find(args.existtrigger)>0 and len(zeile)-9==len(args.existtrigger):
							print('delete trigger at line: ' + str(index))
							finde=1
							if inhalt[index-3].startswith('---'):
								inhalt[index-3] = ''
								
							if inhalt[index-2].startswith('category'):
								inhalt[index-2] = ''
							
							if inhalt[index-1].startswith('comment'):
								inhalt[index-1] = ''
							
							if inhalt[index].startswith('trigger'):
								inhalt[index] = ''
							
							if inhalt[index+1].startswith('terminal_command'):
								inhalt[index+1] = ''
							
							if inhalt[index+2].startswith('intern_command'):
								inhalt[index+2] = ''
							
							if inhalt[index+3].startswith('tts'):
								inhalt[index+3] = ''

				if finde == 1:
					save_file()
				else:
					print('entry not found')
			else:
				print('-e missing')
			quit()
		
		if (not args.add) and args.existtrigger:
			for index, zeile in enumerate(inhalt):
				if args.newtrigger and zeile.find(args.newtrigger)>=0 and len(zeile)-10==len(args.newtrigger) and args.newtrigger!=args.existtrigger:
					print("filename: " + args.filename)
					print("entry in line :" + str(index+1))
					print("entry already exists")
					find_index=index
					quit()
					
				if zeile.find(args.existtrigger)>=0 and len(zeile)-10==len(args.existtrigger):
					print("filename: " + args.filename)
					print("entry in line :" + str(index+1))
					if not args.overwrite:
						print(output)
					find_index=index

			if find_index > 0:
				if args.category:
					if inhalt[find_index-2].startswith('category:'):
						inhalt[find_index-2] = 'category: ' + args.category.strip() + '\n'
				if args.comment:
					if inhalt[find_index-1].startswith('comment:'):
						inhalt[find_index-1] = 'comment: ' + args.comment.strip() + '\n'
				if args.terminalcommand:
					if inhalt[find_index+1].startswith('terminal_command:'):
						inhalt[find_index+1] = 'terminal_command: ' + args.terminalcommand.strip()  + '\n'
				if args.interncommand:
					if inhalt[find_index+2].startswith('intern_command:'):
						inhalt[find_index+2] = 'intern_command: ' + args.interncommand.strip() + '\n'
				if args.feedback:
					if inhalt[find_index+3].startswith('tts:'):
						inhalt[find_index+3] = 'tts: ' + args.feedback.strip() + '\n'
				if args.newtrigger:
					if args.overwrite:
						inhalt[find_index] = inhalt[find_index].replace(args.existtrigger, args.newtrigger.strip())
					else:
						inhalt[find_index] = inhalt[find_index].replace(args.existtrigger, output.strip())

		else:
			for index, zeile in enumerate(inhalt):
				if zeile.find(args.newtrigger)>=0 and len(zeile)-10==len(args.newtrigger):
					print("filename: " + args.filename)
					print("entry in line :" + str(index+1))
					print("entry already exists")
					find_index=index
					quit()
					
			if args.newtrigger:
				find_index=1
				inhalt.append("-----------------------\n")

				if args.category:
					inhalt.append('category: ' + args.category.strip() + '\n')
				else:
					inhalt.append("category:\n")
					
				if args.comment:
					inhalt.append('comment: ' + args.comment.strip() + '\n')
				else:
					inhalt.append("comment:\n")
					
				inhalt.append("trigger: " + args.newtrigger.strip() + "\n")

				if args.terminalcommand:
					inhalt.append('terminal_command: ' + args.terminalcommand.strip()  + '\n')
				else:
					inhalt.append("terminal_command:\n")
					
				if args.interncommand:
					inhalt.append('intern_command: ' + args.interncommand.strip() + '\n')
				else:
					inhalt.append('intern_command:' + '\n')
					
				if args.feedback:
					inhalt.append('tts: ' + args.feedback.strip() + '\n')
				else:
					inhalt.append("tts:\n")
			
			else:
				print('-n missing')
				
		if find_index==0:
			print('entry not found')
		else:
			save_file()
	else:
		print('no filename')

if __name__ == "__main__":
	main()
