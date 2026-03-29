#!/usr/bin/env python3
#﻿wie kann ich den screenshot so ändern, das nur aufnahmen unter meinem angezeigten fenster erstellt werden? hier der code:
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import pyscreenshot
import argparse

# Funktion zum Parsen von Argumenten
def parse_arguments():
	parser = argparse.ArgumentParser(description='Screenshot Viewer')
	parser.add_argument('--width', type=int, help='Breite des Fensters in Pixel', default=100)
	parser.add_argument('--height', type=int, help='Höhe des Fensters in Pixel', default=100)
	parser.add_argument('--topmost', action='store_true', help='Fenster immer im Vordergrund', default=False)
	parser.add_argument('--mouse_cursor', action='store_true', help='Mauszeiger ein', default=False)
	
	parser.add_argument('--cursor_text', type=str, help='Text für den Mauszeiger', default='⬤')
	parser.add_argument('--cursor_size', type=int, help='Größe des Mauszeiger Textes', default=10)
	parser.add_argument('--cursor_bg_color', type=str, help='Hintergrundfarbe des Mauszeigers', default='black')
	parser.add_argument('--cursor_fg_color', type=str, help='Textfarbe des Mauszeigers', default='red')
	
	parser.add_argument('--window_with_mouse', action='store_true', help='Fenster mit Maus bewegen', default=False)
	parser.add_argument('--window_mouse_x', type=int, help='Position Mausfenster Bewegung x', default=-50)
	parser.add_argument('--window_mouse_y', type=int, help='Position Mausfenster Bewegung y', default=50)

	parser.add_argument('--x', type=int, help='x Fenster Position beim Starten', default=100)
	parser.add_argument('--y', type=int, help='y Fenster Position beim Starten', default=100)
	
	return parser.parse_args()

args = parse_arguments()

# Erstelle ein tkinter Fenster
root = tk.Tk()
root.title("Screenshot Viewer")
# Setze die Größe des Fensters auf die angegebenen Werte
root.geometry(f'{args.x}x{args.y}+{args.width}+{args.height}') 
# Überlisten des Fensterrahmens
root.overrideredirect(True)

# Stelle das Fenster immer im Vordergrund, basierend auf dem Argument
if args.topmost:
	root.attributes('-topmost', True)

# Erstelle ein tkinter Label um das Bild anzuzeigen
label = tk.Label(root)
label.pack()

# Erstelle ein Label für den Mauszeiger mit dem angegebenen Text
if args.mouse_cursor:
	mouse_cursor = tk.Label(root, text=args.cursor_text, font=("Arial", args.cursor_size), bg=args.cursor_bg_color, fg=args.cursor_fg_color)
	mouse_cursor.place(relx=0.5, rely=0.5, anchor="center")  # Positioniere den Mauszeiger in der Mitte

def take_screenshot():
	# Hole die aktuelle Mausposition
	x, y = root.winfo_pointerxy()  # Gibt die Position der Maus relativ zum Bildschirm zurück
	
	#Fenster mit dem Mousecursor mitbewegen
	if args.window_with_mouse==True:
		root.geometry(f'{args.width}x{args.height}+{x+args.window_mouse_x}+{y+args.window_mouse_y}')

	# Berechne die Größen für den Screenshot-Bereich basierend auf der Fenstergröße
	area_size = (root.winfo_width(), root.winfo_height())  # Dynamisch die Fenstergröße verwenden

	# Berechnen Sie die Grenzen für den Screenshot-Bereich
	x = x - (area_size[0] // 2)
	y = y - (area_size[1] // 2)
	bbox = (x, y, x + area_size[0], y + area_size[1])
	
	# Screenshot des Bereichs unter dem Mauszeiger machen
	img = pyscreenshot.grab(bbox=bbox, childprocess=False)
	
	# Bild invertieren
	img_inverted = ImageOps.invert(img)
	
	# Konvertiere das Bild in ein tkinter-kompatibles Format
	img_tk = ImageTk.PhotoImage(img_inverted)
	
	# Label mit dem neuen Bild aktualisieren
	label.config(image=img_tk)
	label.image = img_tk  # Halte eine Referenz auf das Bild um Garbage Collection zu verhindern

def update_screenshot():
	take_screenshot()
	root.after(10, update_screenshot)

def close_program(event):
	root.destroy()  # Beende das Tkinter Fenster



# Binde die ESC-Taste an die close_program-Funktion
root.bind('<Escape>', close_program)

# Starte die Screenshot-Schleife
update_screenshot()

# Führe die tkinter-Ereignisschleife aus
root.mainloop()
