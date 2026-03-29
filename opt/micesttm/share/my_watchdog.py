# small function to prevent a double start of the program
# if a program is started repeatedly, all will be terminated
# Version 0.3
import os
import time

ram_cache_path = '/dev/shm/' # general Linux RAM cache to store files and not burden the HD or SSD
plugin_last_Time = time.time()

# If the quit_signal file is saved in RAM, the program will be terminated
def program_name(name):
	global name_run
	name_run = ram_cache_path + name + '_run'

	if os.path.exists(name_run): 									# if a file/program is already running
		os.remove(name_run) # das Run Signal löschen				# delete the run file/signal
		quit() 														# then exit the program
	else:															# if the file does not exist
		with open (name_run, 'w') as f:								# write file this program is running
			f.write('')

def check_twice_started():	
	global plugin_last_Time
	
	if time.time() - plugin_last_Time > 2:
		plugin_last_Time = time.time()
	if os.path.exists(name_run)==False:
		return True
