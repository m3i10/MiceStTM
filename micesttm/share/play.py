#!/usr/bin/env python3
# Audio-Player mit Tonhöhen-, Tempo- und Lautstärke-Kontrolle
# Liest und speichert Voreinstellungen in ~/.config/micesttm/micesttm.ini

# Argument 2 Tempo

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
Gst.init(None)

import threading
import time
import curses
import sys
import os
import configparser

# --- micesttm.ini laden ---
home_directory = os.path.expanduser("~")
config_dir = os.path.join(home_directory, ".config", "micesttm")
config_file_path = os.path.join(config_dir, "micesttm.ini")

config = configparser.ConfigParser()
config.read(config_file_path)

# --- Standardwerte ---
notSave=1

try:
	speed = float(sys.argv[2])
except:
	speed = float(config.get("tts", "speed", fallback="1.0"))
volume = float(config.get("tts", "volume", fallback="1.0"))
pitch_shift = float(config.get("tts", "pitch", fallback="0.0"))

# --- GStreamer initialisieren ---
Gst.init(None)
eos_event = threading.Event()


# --- GStreamer-Player-Klasse ---
class GstPlayer:
	def __init__(self, filepath):
		if not os.path.isfile(filepath):
			print(f"Fehler: Datei nicht gefunden: {filepath}")
			sys.exit(1)

		self.filepath = filepath
		self.pipeline = Gst.Pipeline.new("audio-player")

		self.src = Gst.ElementFactory.make("filesrc", "src")
		self.src.set_property("location", os.path.abspath(filepath))
		self.demux = Gst.ElementFactory.make("decodebin", "demux")
		self.demux.connect("pad-added", self.on_pad_added)
		self.conv = Gst.ElementFactory.make("audioconvert", "conv")
		self.pitch = Gst.ElementFactory.make("pitch", "pitch")
		self.volume = Gst.ElementFactory.make("volume", "volume")
		self.resample = Gst.ElementFactory.make("audioresample", "resample")
		self.sink = Gst.ElementFactory.make("autoaudiosink", "sink")

		for e in [self.src, self.demux, self.conv, self.pitch, self.volume, self.resample, self.sink]:
			self.pipeline.add(e)

		self.src.link(self.demux)

		self.bus = self.pipeline.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_message)

		self.is_playing = False

	def on_pad_added(self, demux, pad):
		caps = pad.get_current_caps()
		if caps and caps.to_string().startswith("audio/"):
			pad.link(self.conv.get_static_pad("sink"))
			self.conv.link(self.pitch)
			self.pitch.link(self.volume)
			self.volume.link(self.resample)
			self.resample.link(self.sink)

	def on_message(self, bus, message):
		t = message.type
		if t == Gst.MessageType.EOS:
			eos_event.set()
			self.stop()
		elif t == Gst.MessageType.ERROR:
			err, debug = message.parse_error()
			print("GStreamer Fehler:", err, debug)
			eos_event.set()
			self.stop()

	def set_speed(self, speed):
		self.pitch.set_property("tempo", speed)

	def set_pitch_shift(self, semitones):
		factor = 2 ** (semitones / 12.0)
		self.pitch.set_property("pitch", factor)

	def set_volume(self, volume):
		self.volume.set_property("volume", volume)

	def play(self):
		self.pipeline.set_state(Gst.State.PLAYING)
		self.is_playing = True

	def pause(self):
		self.pipeline.set_state(Gst.State.PAUSED)
		self.is_playing = False

	def toggle_pause(self):
		if self.is_playing:
			self.pause()
		else:
			self.play()

	def get_position(self):
		success, pos = self.pipeline.query_position(Gst.Format.TIME)
		return pos if success else 0

	def get_duration(self):
		success, dur = self.pipeline.query_duration(Gst.Format.TIME)
		return dur if success else Gst.CLOCK_TIME_NONE

	def seek(self, seconds):
		seek_ns = int(seconds * 1e9)
		self.pipeline.seek_simple(Gst.Format.TIME,
								  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
								  seek_ns)

	def stop(self):
		self.pipeline.set_state(Gst.State.NULL)
		self.is_playing = False


# --- GStreamer MainLoop ---
def gst_main_loop():
	loop = GLib.MainLoop()
	loop.run()


# --- Hilfsfunktion: INI speichern ---
def save_to_ini(speed, volume, pitch_shift):
	global notSave
	os.makedirs(config_dir, exist_ok=True)
	if notSave==0:
		if "tts" not in config:
			config["tts"] = {}
		config["tts"]["speed"] = f"{speed:.2f}"
		config["tts"]["volume"] = f"{volume:.2f}"
		config["tts"]["pitch"] = f"{pitch_shift:.2f}"
		with open(config_file_path, "w") as f:
			config.write(f)


# --- curses UI ---
def run_player(stdscr, filepath):
	global speed, volume, pitch_shift
	global notSave
	
	player = GstPlayer(filepath)
	player.set_speed(speed)
	player.set_volume(volume)
	player.set_pitch_shift(pitch_shift)
	player.play()

	#curses.curs_set(0)
	#stdscr.nodelay(True)
	stdscr.timeout(100)

	while True:
		pos_ns = player.get_position()
		dur_ns = player.get_duration()
		pos_s = pos_ns / 1e9
		dur_s = dur_ns / 1e9 if dur_ns != Gst.CLOCK_TIME_NONE else 0

		stdscr.clear()
		stdscr.addstr(0, 0, f"Datei: {filepath}")
		stdscr.addstr(1, 0, f"Position: {pos_s:.1f}s / {dur_s:.1f}s")
		stdscr.addstr(2, 0, f"Geschwindigkeit: {speed:.2f}x")
		stdscr.addstr(3, 0, f"Lautstärke: {int(volume * 100)}%")
		stdscr.addstr(4, 0, f"Tonhöhe: {pitch_shift:+.1f} Halbton")
		stdscr.addstr(6, 0, "←/→  5s vor/zurück | +/- Tempo | ↑/↓ Lautstärke | o/p Tonhöhe | Leertaste Pause | q Beenden")

		if eos_event.is_set():
			break

		key = stdscr.getch()
		if key == curses.KEY_RIGHT:
			player.seek(min(pos_s + 5, dur_s))
		elif key == curses.KEY_LEFT:
			player.seek(max(pos_s - 5, 0))
		elif key == ord('+'):
			speed = min(speed + 0.1, 2.5)
			player.set_speed(speed)
			notSave=0
		elif key == ord('-'):
			speed = max(speed - 0.1, 0.5)
			player.set_speed(speed)
			notSave=0
		elif key == curses.KEY_UP:
			volume = min(volume + 0.1, 2.0)
			player.set_volume(volume)
			notSave=0
		elif key == curses.KEY_DOWN:
			volume = max(volume - 0.1, 0)
			player.set_volume(volume)
			notSave=0
		elif key == ord('p'):
			pitch_shift = min(pitch_shift + 0.5, 12.0)
			player.set_pitch_shift(pitch_shift)
			notSave=0
		elif key == ord('o'):
			pitch_shift = max(pitch_shift - 0.5, -12.0)
			player.set_pitch_shift(pitch_shift)
			notSave=0
		elif key == ord(' '):
			player.toggle_pause()
		elif key == ord('q'):
			break

		#stdscr.refresh()
		time.sleep(0.05)

	player.stop()
	save_to_ini(speed, volume, pitch_shift)


# --- Einstiegspunkt ---
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 player.py <audiofile>")
		sys.exit(1)

	filepath = sys.argv[1]
	gst_thread = threading.Thread(target=gst_main_loop, daemon=True)
	gst_thread.start()

	curses.wrapper(run_player, filepath)
