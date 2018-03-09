'''
	=== n-Blocks Studio file access library ===
	
	This library contains functions used to access the file system in n-Blocks Studio
	
	Author:
		Fernando Cosentino
		Nimbus Centre
		Cork Institute of Technology
'''
import json
import os
import sys
import tkFileDialog


# Get the location of the 'py' file I'm running:
mydir = os.path.abspath(sys.path[0])

defaultLibs = {
	'ADC': 'adc',
	'GPO': 'gpo',
	'GPI': 'gpi',
	'NOT': 'not',
	'FlipFlop': 'flipflop',
	'PWM': 'pwm',
	'Ticker': 'ticker'
}

def ListProjects():
	dir = os.listdir(mydir+'/Projects/')
	res = []
	for eline in dir:
		if os.path.isfile(mydir+'/Projects/'+eline):
			res.append(os.path.splitext(eline)[0])
	return res
	
def LoadProjectFromFile(filename):
	try:
		with open(mydir+ '/Projects/'+filename) as data_file:    
			load_point = json.load(data_file)
			data_file.close()
			return load_point
	except:
		return None
	
def SaveProjectToFile(filename, save_point):
	try:
		with open(mydir+ '/Projects/'+filename, 'w') as outfile:
				json.dump(save_point, outfile, indent = 4)
		return True
	except:
		return False
		
def RequestExportToFile():
	filename = tkFileDialog.asksaveasfilename(initialdir = mydir+'/Export/', title = "Export to...",filetypes = (("ARM C++ Source Code","*.cpp"),("All files","*.*")))
	return filename
