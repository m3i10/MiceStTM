#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import pyautogui
import time
import cairo # cairo importiere

max_events = 7  # Maximale Anzahl der Klicks
fontsize=100
class TransparentGrid(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="screen grid")

		self.set_decorated(False)
		self.set_keep_above(True)  # Fenster immer im Vordergrund halten
		# Fokus auf das Fenster setzen 
		self.set_accept_focus(True)
		self.grab_focus()

		screen = self.get_screen()
		visual = screen.get_rgba_visual()
		if visual and screen.is_composited():
			self.set_visual(visual)
		else:
			print("Transparenz wird nicht unterstützt!")

		  # Set up CSS for transparency

		css_provider = Gtk.CssProvider()
		css_provider.load_from_data(b"""
			window {
				background-color: rgba(0, 0, 0, 0);
			}
		""")
		
		self.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

		self.screen_width, self.screen_height = pyautogui.size()
		self.set_default_size(self.screen_width, self.screen_height)
		self.fullscreen()

		self.drawing_area = Gtk.DrawingArea()
		self.drawing_area.connect("draw", self.on_draw)
		self.add(self.drawing_area)

		self.connect("key-press-event", self.on_key_press)

		self.grid_size = 2  # Startgröße des Gitters
		self.grid_cells = []  # Liste für die Zellen
		self.click_count = 0  # Zähler für die Klicks
		self.clicked_cell = None  # Das zuletzt angeklickte Feld
		self.draw_grid()  # Gitter zeichnen
		
	
	def draw_grid(self):
		self.grid_cells = []
		self.mid_points = []  # Zurücksetzen der Mittelpunkte
		cell_width = self.screen_width // self.grid_size
		cell_height = self.screen_height // self.grid_size

		for i in range(self.grid_size):
			for j in range(self.grid_size):
				cell_x = j * cell_width
				cell_y = i * cell_height
				cell_number = f"{i * self.grid_size + j + 1}"
				self.grid_cells.append((cell_x, cell_y, cell_width, cell_height, cell_number))
				#print(f"intern Field {cell_number}: Start ({cell_x}, {cell_y}) / ({cell_x + cell_width}, {cell_y + cell_height})")  # Ausgabe der Position und Nummerierung

				# Berechnung des Mittelpunkts und Hinzufügen zur Liste
				mid_x = cell_x + cell_width // 2
				mid_y = cell_y + cell_height // 2
				self.mid_points.append((mid_x, mid_y))

		self.drawing_area.queue_draw()

	def on_draw(self, widget, cr):
		global fontsize
		
		cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		cr.set_font_size(fontsize)

		if self.clicked_cell:
			fontsize=fontsize-30
			if fontsize<8:
				fontsize=8
			

			cr.set_source_rgb(1, 0, 0)  # Rote Farbe für das angeklickte Feld
			cr.set_line_width(2)

			# Linien für das angeklickte Feld zeichnen
			cell_x, cell_y, cell_width, cell_height, _ = self.clicked_cell
			cr.rectangle(cell_x, cell_y, cell_width, cell_height)
			cr.stroke()

			# Unterteile das angeklickte Feld in 4 kleinere Felder
			sub_cell_width = cell_width // 2
			sub_cell_height = cell_height // 2

			cr.set_source_rgb(1, 1, 1)  # Weiße Farbe für die Nummern
			
			cell_number = 0
			for i in range(2):
				for j in range(2):
					cell_number += 1
					sub_cell_x = cell_x + j * sub_cell_width
					sub_cell_y = cell_y + i * sub_cell_height
					cr.rectangle(sub_cell_x, sub_cell_y, sub_cell_width, sub_cell_height)
					cr.stroke()
					cr.move_to(sub_cell_x + 10, sub_cell_y + fontsize+10)
					cr.show_text(str(cell_number))  # Position und Nummerierung
					#print(f"Field {cell_number}: Start ({sub_cell_x}, {sub_cell_y}) / ({sub_cell_width}, {sub_cell_height})")  # Ausgabe der Position und Nummerierung
					#print(f"middle click {cell_number}: ({sub_cell_x+(sub_cell_width/2)}, {sub_cell_y+(sub_cell_height/2)}))")  # Ausgabe der Position Mitte
		else:
			cr.set_source_rgb(1, 1, 1)  # Weiße Farbe für die Nummern
			cr.set_line_width(1)

			# Gitterlinien zeichnen
			for cell in self.grid_cells:
				cell_x, cell_y, cell_width, cell_height, _ = cell
				cr.rectangle(cell_x, cell_y, cell_width, cell_height)
				cr.stroke()

			for cell in self.grid_cells:
				cell_x, cell_y, _, _, cell_number = cell
				cr.move_to(cell_x + 20, cell_y + fontsize)
				cr.show_text(cell_number)  # Position und Nummerierung

	
		
	def split_and_number(self, cell_number):
		index = cell_number - 1
		x = index // self.grid_size
		y = index // self.grid_size

		# Neue Gittergröße
		self.grid_size *= 2
		self.grid_cells.clear()  # Vorherige Zellen löschen
		self.mid_points = []  # Zurücksetzen der Mittelpunkte
		self.draw_grid()  # Neues Gitter zeichnen

		# Neue Zellen erstellen
		cell_width = self.screen_width // self.grid_size
		cell_height = self.screen_height // self.grid_size

		for i in range(self.grid_size):
			for j in range(self.grid_size):
				cell_x = j * cell_width
				cell_y = i * cell_height
				cell_x1 = cell_x + cell_width
				cell_y1 = cell_y + cell_height
				if i // 2 == x and j // 2 == y:  # Nur das angeklickte Feld aufteilen
					self.grid_cells.append((cell_x, cell_y, cell_width, cell_height, f"{(x * 2 + y) * 4 + (i % 2) * 2 + (j % 2) + 1}"))
		self.drawing_area.queue_draw()

	def on_key_press(self, widget, event):
		if event.keyval == Gdk.KEY_Escape:
			self.close()  # Programm schließen
		elif event.keyval in [Gdk.KEY_1, Gdk.KEY_2, Gdk.KEY_3, Gdk.KEY_4]:
			if self.click_count >= max_events:
				#print("Click Limit Exeeded")
				return
		   
			if self.clicked_cell:
				cell_x, cell_y, cell_width, cell_height, _ = self.clicked_cell
				if event.keyval == Gdk.KEY_1:
					self.clicked_cell = (cell_x, cell_y, cell_width // 2, cell_height // 2, "1")
					mid_x = cell_x + cell_width // 4
					mid_y = cell_y + cell_height // 4

				elif event.keyval == Gdk.KEY_2:
					self.clicked_cell = (cell_x + cell_width // 2, cell_y, cell_width // 2, cell_height // 2, "2")
					mid_x = cell_x + (3*(cell_width // 4))
					mid_y = cell_y + cell_height // 4

				elif event.keyval == Gdk.KEY_3:
					self.clicked_cell = (cell_x, cell_y + cell_height // 2, cell_width // 2, cell_height // 2, "3")
					mid_x = cell_x + cell_width // 4
					mid_y = cell_y + (3*(cell_height // 4))

				elif event.keyval == Gdk.KEY_4:
					self.clicked_cell = (cell_x + cell_width // 2, cell_y + cell_height // 2, cell_width // 2, cell_height // 2, "4")
					mid_x = cell_x + (3*(cell_width // 4))
					mid_y = cell_y + (3*(cell_height // 4))

				self.split_and_number(int(self.clicked_cell[4]))  # Das angeklickte Feld aufteilen (index als int)
				self.click_count += 1  # Klickzähler erhöhen
				#print(f"Number of Clicks {self.click_count}")  # Aktuelle Klickanzahl ausgeben
			else:
				if self.grid_cells:
					cell_width = self.screen_width
					cell_height = self.screen_height
					if event.keyval == Gdk.KEY_1:
						self.clicked_cell = self.grid_cells[0]
						mid_x = cell_width // 4
						mid_y = cell_height // 4

					elif event.keyval == Gdk.KEY_2:
						self.clicked_cell = self.grid_cells[1]
						mid_x = (3*(cell_width // 4))
						mid_y = cell_height // 4

					elif event.keyval == Gdk.KEY_3:
						self.clicked_cell = self.grid_cells[2]
						mid_x = cell_width // 4
						mid_y = (3*(cell_height // 4))

					elif event.keyval == Gdk.KEY_4:
						self.clicked_cell = self.grid_cells[3]
						mid_x = (3*(cell_width // 4))
						mid_y = (3*(cell_height // 4))
 
					self.split_and_number(int(self.clicked_cell[4]))  # Das angeklickte Feld aufteilen (index als int)
					self.click_count += 1  # Klickzähler erhöhen
					#print(f"Number of Clicks {self.click_count}")  # Aktuelle Klickanzahl ausgeben
			pyautogui.moveTo(mid_x, mid_y)
if __name__ == '__main__':
	window = TransparentGrid()
	window.connect("destroy", Gtk.main_quit)
	window.show_all()

	Gtk.main()
