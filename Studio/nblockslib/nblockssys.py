'''
	=== n-Blocks Studio OS access library ===

	This library contains OS-dependent functions used by n-Blocks Studio
	to access clipboard and window methods 
	
	Author:
		Fernando Cosentino
		Nimbus Centre
		Cork Institute of Technology
'''

import sys
import pyperclip

#================================
# Windows version
if sys.platform == 'win32':
	import win32gui

	def SetWindowFocus(handle):
		win32gui.SetForegroundWindow(handle)
		
#================================
# Linux version
elif (sys.platform == 'linux') or (sys.platform == 'linux2'):
	def SetWindowFocus(handle):
		pass
		
#================================
# OS X version
elif sys.platform == 'darwin':
	def SetWindowFocus(handle):
		pass

#================================
# Unknown system version
else:	
	def SetWindowFocus(handle):
		pass

		
def CopyToClipboard(value):
	pyperclip.copy(value)