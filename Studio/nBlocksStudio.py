'''
	=== n-Blocks Studio Launching Menu ===
	
	This is the main file called when the Studio is invoked
	
	Author:
		Fernando Cosentino
		Nimbus Centre
		Cork Institute of Technology
	
'''

import sys
import os
import time
import Tkinter as tk

# Get the location of the 'py' file I'm running:
mydir = os.path.abspath(sys.path[0])

S_WIDTH = 400
S_HEIGHT = 390

## Splash screen before loading other modules

s_root = tk.Tk()
s_root.title('Loading nBlocks Studio')
s_root.iconbitmap(mydir + r'/res/nBlocksStudio32.ico')

screen_width = s_root.winfo_screenwidth()
screen_height = s_root.winfo_screenheight()
wx = (screen_width/2) - (S_WIDTH/2)
wy = (screen_height/2) - ((S_HEIGHT+90)/2)

s_root.rowconfigure(0, weight=1)
s_root.resizable(width=False, height=False)
s_root.minsize(width=S_WIDTH, height=(S_HEIGHT+90))
s_root.geometry('%dx%d+%d+%d' % (S_WIDTH, S_HEIGHT+90, wx, wy))

splashimg = tk.PhotoImage(file='res/menulogo.gif')
splashlabel = tk.Label(s_root, width=400, height=210, image=splashimg)
splashlabel.image = splashimg
splashlabel.pack()

s_root.update()
## ---

import ttk
import webbrowser

from nworkbench import nWorkbench
from nblockslib import nblocksnet
from nblockslib import nblockshal
from nblockslib import nblocksfile

from nblockslib.hardwarelib.PyoConnect import *



# === SCREENS
screenlist = {}
objlist = {}
def MakeWindow():
	global screenlist, objlist
	global w_root
	global user_credentials

    
	
	w_root = tk.Tk()
	w_root.title('nBlocks Studio')
	w_root.iconbitmap(mydir + r'/res/nBlocksStudio32.ico')

	screen_width = w_root.winfo_screenwidth()
	screen_height = w_root.winfo_screenheight()
	wx = (screen_width/2) - (S_WIDTH/2)
	wy = (screen_height/2) - ((S_HEIGHT+90)/2)

	w_root.rowconfigure(0, weight=1)
	w_root.resizable(width=False, height=False)
	w_root.minsize(width=S_WIDTH, height=(S_HEIGHT+90))
	w_root.geometry('%dx%d+%d+%d' % (S_WIDTH, S_HEIGHT+90, wx, wy))
	
	menubarimg = tk.PhotoImage(file='res/menulogo.gif')
	menulabel = tk.Label(w_root, width=S_WIDTH, height=90, image=menubarimg)
	menulabel.image = menubarimg
	menulabel.pack()

	w_main = tk.Frame(w_root, width=S_WIDTH, height=S_HEIGHT)
	w_main.pack()
	
	# ======== Screen creation:

	# ------------------------
	# --- Screen: Main
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT, bd=0)
	w_framein = tk.Frame(w_frame, width=S_WIDTH)
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)

	# Buttons
	ttk.Button(w_framein, text="Start nBlocks Designer", command=Act_LoginScreen).pack(fill=tk.X)
	ttk.Button(w_framein, text="Start nBlocks Control", command=Act_Dashboard).pack(fill=tk.X)
	
	tk.Frame(w_framein, width=S_WIDTH, height=12).pack() # Spacer
	
	ttk.Button(w_framein, text="Create Account", command=Act_CreateAccount).pack(fill=tk.X)
	ttk.Button(w_framein, text="Options", command=Act_Options).pack(fill=tk.X)
	
	# Bottom bar buttons
	ttk.Button(w_bottombar, text="Quit", command=quit).pack(fill=tk.X)
	
	screenlist['Main'] = w_frame
	

	# ------------------------
	# --- Screen: Login to launch
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)
	
	ttk.Label(w_framein, text="Username:").place(x=15, y=15)
	objlist['username'] = ttk.Entry(w_framein, width=55)
	objlist['username'].insert(0, user_credentials['user'])
	objlist['username'].place(x=30, y=40)

	ttk.Label(w_framein, text="Password:").place(x=15, y=75)
	objlist['password'] = ttk.Entry(w_framein, width=55, show="*")
	objlist['password'].place(x=30, y=100)
	
	objlist['autologin'] = tk.IntVar()
	objlist['autologin_obj'] = tk.Checkbutton(w_framein, text="Automatic login", variable=objlist['autologin'], onvalue=1, offvalue=0, command=debug)
	objlist['autologin_obj'].place(x=30, y=125)
	objlist['autologin'].set(user_credentials['autologin'])

	ttk.Button(w_framein, text="Login", command=Act_PerformLogin).place(x=30, y=180, width=340)
	ttk.Button(w_framein, text="Use Offline", command=Act_UseOffline).place(x=30, y=220, width=340)

	
	ttk.Button(w_bottombar, text="Cancel", command=Act_BackToMain).pack(fill=tk.X)
	
	screenlist['Login'] = w_frame


	# ------------------------
	# --- Screen: Login progress
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)
	
	ttk.Label(w_framein, text="Loggin in, please wait...").place(x=15, y=15)

	ttk.Button(w_bottombar, text="Cancel", command=Act_BackToMain).pack(fill=tk.X)
	
	screenlist['LoginProgress'] = w_frame	


	# ------------------------
	# --- Screen: Login failed
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)
	
	ttk.Label(w_framein, text="Login failed. Please enter your credentials again.").place(x=15, y=15)

	ttk.Button(w_bottombar, text="OK", command=Act_LoginScreen).pack(fill=tk.X)
	
	screenlist['LoginFailed'] = w_frame	
	
	# ------------------------
	# --- Screen: Create Account
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)

	ttk.Label(w_framein, text="To create an account, go to www.n-blocks.net").place(x=15, y=15)

	ttk.Button(w_framein, text="Create account at n-Blocks.net", command=Act_Go_nBlocksNet).place(x=30, y=60, width=340)
	
	ttk.Button(w_bottombar, text="OK", command=Act_BackToMain).pack(fill=tk.X)
	
	screenlist['CreateAccount'] = w_frame
	
	# ------------------------
	# --- Screen: Options
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	w_bottombar = tk.Frame(w_frame, width=S_WIDTH, height=30)
	w_bottombar.place(y=(S_HEIGHT-30), relwidth=1)

	
	ttk.Button(w_bottombar, text="OK", command=Act_BackToMain).pack(fill=tk.X)
	
	screenlist['Options'] = w_frame


	# ------------------------
	# --- Screen: Running
	w_frame = tk.Frame(w_main, width=S_WIDTH, height=S_HEIGHT)
	w_framein = tk.Frame(w_frame, width=S_WIDTH, height=(S_HEIGHT-30))
	w_framein.place(x=0, y=0, relwidth=1, height=(S_HEIGHT-30))
	ttk.Label(w_framein, text="n-Blocks Studio is running").place(x=15, y=15)
	
	screenlist['Running'] = w_frame
	

	# ========================

def debug():
	#Res_LoginResults({'auth':0})
	pass

	
def Screen_HideAll():
	global screenlist
	slist = screenlist.keys()
	for s in slist:
		screenlist[s].pack_forget()

	
# === ACTIONS
def Act_BackToMain():
	global screenlist
	Screen_HideAll()
	screenlist['Main'].pack(expand=1, fill=tk.BOTH)

def Act_Dashboard():
	pass

def Act_LoginScreen():
	global screenlist, objlist, user_credentials
	if user_credentials['autologin'] == 1:
		Act_PerformLogin()
	else:
		Screen_HideAll()
		screenlist['Login'].pack(expand=1, fill=tk.BOTH)

def Res_LoginResults(results):
	global screenlist, objlist, StudioApp
	if results['auth'] == 1:
		Act_StartStudio(results)
	else:
		objlist['autologin_obj'].deselect()
		user_credentials['autologin'] = 0
		Screen_HideAll()
		screenlist['LoginFailed'].pack(expand=1, fill=tk.BOTH)
	
def Act_PerformLogin():
	global screenlist, objlist, w_root, user_credentials
	Screen_HideAll()
	screenlist['LoginProgress'].pack(expand=1, fill=tk.BOTH)
	w_root.update()
	
	if user_credentials['autologin'] == 1: # autologin BEFORE entering login screen
		md5pass = user_credentials['pass']
		
	else: # Came here from Login screen
		user_credentials['user'] = objlist['username'].get()
		user_credentials['autologin'] = objlist['autologin'].get()
		md5pass = nblocksnet.md5(objlist['password'].get())
		if user_credentials['autologin'] == 1:
			epass = objlist['password'].get()
			user_credentials['pass'] = md5pass
		else:
			epass = ""
			user_credentials['pass'] = ""
			
		nblocksnet.SaveCredentials(user_credentials['user'], epass, user_credentials['autologin'])

	ucred = {'user':user_credentials['user'], 'pass':md5pass}
	#print "Login: "+str(ucred)
	w_root.after(500, nblocksnet.RetrieveUserData(ucred, Res_LoginResults) )
	
	
def Act_CreateAccount():
	Screen_HideAll()
	screenlist['CreateAccount'].pack(expand=1, fill=tk.BOTH)

def Act_StartStudio(user_data={}):
	#global w_root
	#w_root.destroy()
	Screen_HideAll()
	screenlist['Running'].pack(expand=1, fill=tk.BOTH)
	StudioApp = nWorkbench(w_root, user_data)
	StudioApp.HAL_Myo_Init(nblockshal.CreateMyo())
	StudioApp.HAL_SpaceNav_Init( nblockshal.CreateSpaceNav() )
	StudioApp.run()

def Act_UseOffline():
	Act_StartStudio({'auth':0, "customBlocks":[]})

def Act_Go_nBlocksNet():
	url = nblocksnet.studio_url+'new_account.php'
	try:
		if sys.platform=='win32': # windows
			os.startfile(url)
		elif sys.platform=='darwin': # OS X
			subprocess.Popen(['open', url])
		elif sys.platform.startswith('linux'): # Linux
			subprocess.Popen(['xdg-open', url])
		else:
			webbrowser.open_new_tab(url)
	except OSError:
		webbrowser.open_new_tab(url)

def Act_Options():
	Screen_HideAll()
	screenlist['Options'].pack(expand=1, fill=tk.BOTH)
	
# === === === ===

user_credentials = nblocksnet.LoadCredentials()
if user_credentials is False:
	user_credentials = {"user": "", "pass": "", "autologin": 0}

s_root.destroy()
	
MakeWindow()
Act_BackToMain()
w_root.mainloop()

