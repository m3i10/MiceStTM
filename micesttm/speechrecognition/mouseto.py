import pyautogui
import pytesseract
import cv2
import numpy as np
import sys

# Setze den Pfad zu deiner Tesseract-Installation
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Standardpfad für Linux

def find_and_set(text):
	# Screenshot des Bildschirms machen
	screenshot = pyautogui.screenshot()
	screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

	# Texterkennung auf dem Screenshot durchführen
	h, w, _ = screenshot.shape
	boxes = pytesseract.image_to_data(screenshot)
	mouse_x, mouse_y = pyautogui.position()
	for i, box in enumerate(boxes.splitlines()):
		if i == 0:
			continue
		b = box.split()
		if len(b) == 12:
			x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
			detected_text = b[11]
			if text.lower() in detected_text.lower():
				# Maus zu den Koordinaten bewegen und klicken
				if mouse_x != x + w // 2 or mouse_y != y + h // 2:
					pyautogui.moveTo(x + w // 2, y + h // 2)
					#pyautogui.click()
					return

	print(f'Text "{text}" nicht gefunden.')

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Verwendung: mausto 'text'")
		sys.exit(1)
	user_input = sys.argv[1].strip("'")  # Entferne die einfachen Anführungszeichen
	find_and_set(user_input)
