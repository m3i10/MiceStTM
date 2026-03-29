#!/usr/bin/env python3
import os
import time
import re
import pyperclip
import subprocess
# Mice mini Imports
import say

def add_commas_to_digits(text):
	def replace_digit(match):
		digit = match.group()
		if len(digit) > 4:
			return ". ".join(digit)
		else:
			return digit
	modified_text = re.sub(r'\d+', lambda m: replace_digit(m), text)
	return modified_text

time.sleep(0.1)

try:
	result = subprocess.run(['xsel', '-p', '--output'], text=True, capture_output=True, check=True)
	lines = result.stdout.strip()
except subprocess.CalledProcessError as e:
	print(f"Error retrieving clipboard contents: {e}")


lines =  re.sub(r'(\d+,\d+)\s+(\d+,\d+)', r'\1 und \2', lines) # 23,4 23,4 convert to 23,3 - 23,3
lines = re.sub(r'(?<=\d) (?=\d)', '', lines) # 3443 34 23 convert to 34433423
lines = add_commas_to_digits(lines)

text = ''
for line in lines:
	if not line:
		continue
	text=text + line

say.raw(text)
