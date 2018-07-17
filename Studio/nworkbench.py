'''
	=== n-Blocks Studio Designer ===
	
	This file contains the nWorkbench class, the main Studio Designer code
	
	Author:
		Fernando Cosentino
		Nimbus Centre
		Cork Institute of Technology
	
'''

import sys
import os
import json
from math import sin, cos, radians
from tkinter import TclError

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from panda3d.core import WindowProperties
from direct.task import Task
from direct.showutil.Rope import Rope

from nblockslib import nblocksnet
from nblockslib import nblocksfile
from nblockslib import nblockssys

from nblockslib.hardwarelib.PyoConnect import *

# Get the location of the 'py' file I'm running:
mydir = os.path.abspath(sys.path[0])

# Convert that to panda's unix-style notation.
mydir = Filename.fromOsSpecific(mydir).getFullpath()
# use it like: model = loader.loadModel(mydir + "/models/mymodel.egg")

MODE_NORMAL = 0
MODE_SELECTBLOCK = 1
MODE_ADDBLOCK = 2
MODE_DIALOG = 3
MODE_ROUTING = 4

DIALOG_MAIN = 0
DIALOG_ADDNBLOCKNODE = 1
DIALOG_QUIT = 2
DIALOG_GENERIC = 3
DIALOG_LOAD = 4
DIALOG_NEW = 5
DIALOG_START = 6
DIALOG_PARAMETERS = 7

def setGeomTexture(Model, geomName, texture):
	texAttrib = TextureAttrib.make(texture)
	geomNode = Model.find('**/'+geomName).node()
	newRenderState = geomNode.getGeomState(0).addAttrib(texAttrib, 1)
	geomNode.setGeomState(0, newRenderState)
	return 0



class nWorkbench(ShowBase):
	# Hardware objects
	myo = None
	spacenav = None

	# System variables
	system_mode = MODE_NORMAL
	dialog_mode = DIALOG_MAIN
	
	shift_state = False
	alt_state = False
	ctrl_state = False
	mouse1_state = False
	mouse2_state = False
	mouse3_state = False
	mouse_centred_flag = False
	myo_grab_state = False
	
	cam_type = 1
	
	current_floor = 1
	
	# Blocks
	last_picked = None # raypicking = just under the cursor
	last_selected = None # actually selected using mouse click
	last_edited = None  # actually selected for editting using right mouse click
	to_be_placed = None # new block to place
	
	# Connection edges
	last_conn_picked = None
	last_conn_selected = None
	
	ground = None
	block_list = []
	nBlockNodeList = {}
	connection_list = []
	GUI = {}
	
	dialog_yes_callback = None
	dialog_no_callback = None
	
	user_data = {}
	node_iterator = 0
	conn_iterator = 0
	
	project_name = None

	def __init__(self, caller_window = None, userdata = {}):
		ShowBase.__init__(self)
		self.windowHandle = self.win.getWindowHandle().getIntHandle()
		self.callerWindow = caller_window
		
		self.user_data = userdata
		
		base.disableMouse()
		base.mouseWatcherNode.set_modifier_buttons(ModifierButtons())
		base.buttonThrowers[0].node().set_modifier_buttons(ModifierButtons())
		

		# ======================== 3D Interface

		#self.picker.showCollisions(render) # comment this to hide collisions
		
		#=== Invisible Tree
		self.nBlockNodes = render.attachNewNode("nBlockNode Holder")
		self.nBlockNodes_Floors = {
			0: self.nBlockNodes.attachNewNode("nBLockNode Floor 0"),
			1: self.nBlockNodes.attachNewNode("nBLockNode Floor 1"),
			2: self.nBlockNodes.attachNewNode("nBLockNode Floor 2"),
			3: self.nBlockNodes.attachNewNode("nBLockNode Floor 3"),
			4: self.nBlockNodes.attachNewNode("nBLockNode Floor 4"),
			5: self.nBlockNodes.attachNewNode("nBLockNode Floor 5"),
			6: self.nBlockNodes.attachNewNode("nBLockNode Floor 6"),
			7: self.nBlockNodes.attachNewNode("nBLockNode Floor 7")
		}
		self.TotalFloors = len(self.nBlockNodes_Floors)
		self.nBlockNodeConns = render.attachNewNode("nBlockNode Connection Holder")
		
		#self.Colls = render.attachNewNode("CollHolder")

		# Camera
		ConfigVariableBool('framebuffer-multisample').setValue(True)
		ConfigVariableInt('multisamples').setValue(8)
		render.setAntialias(AntialiasAttrib.MMultisample) #MAuto

		self.ViewHolder = render.attachNewNode("ViewHolder") # this is moved XY
		self.CamHolder = render.attachNewNode("CamHolder") # this is rotated
		self.CamHolder.reparentTo(self.ViewHolder)
		self.camera.reparentTo(self.CamHolder) # this is moved Z
		self.camera.setPos(0,0,100)
		self.camera.setHpr(0,-90,0)
		
		# Sky box/sphere
		'''
		self.Sky = loader.loadModel(mydir + "/models/skysphere.egg")
		skytex = loader.loadTexture(mydir + "/models/tex/skybox.png")
		skytex.setMinfilter(SamplerState.FT_linear_mipmap_linear)
		self.Sky.setTexture(skytex, 1)
		self.Sky.setName('Sky')
		self.Sky.setBin("background", 0)
		self.Sky.setDepthWrite(False)
		self.Sky.setCompass()
		self.Sky.reparentTo(self.camera)
		self.Sky.setPos(0,0,0)
		self.Sky.setScale(100)'''
		
		
		# Object picking
		self.picker = CollisionTraverser()
		self.pq = CollisionHandlerQueue()
		self.pickerNode = CollisionNode('mouseRay')
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
		self.pickerRay = CollisionRay()
		self.pickerNode.addSolid(self.pickerRay)
		self.picker.addCollider(self.pickerNP, self.pq)

		# Global objects
		# - ambient light
		alight = AmbientLight('AmbientLight')
		alight.setColor(VBase4(0.5, 0.5, 0.5, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)		
		# - Directional light
		dlight = DirectionalLight('MainLight')
		dlight.setColor(VBase4(0.7, 0.7, 0.7, 1))
		#dlight.setShadowCaster(True)#, 512, 512)
		#dlight.getLens().setFov(40)
		#dlight.getLens().setNearFar(10, 100)
		dlnp = self.camera.attachNewNode(dlight)		
		dlnp.setPos(0,0,0)
		dlnp.setHpr(30,-60,0)
		render.setLight(dlnp)
		#self.Sky.setLightOff(dlnp)
		#render.setShaderAuto()
		
		self.GroundTexture = loader.loadTexture(mydir + "/models/tex/ground.png")
		self.GroundTexture.setMinfilter(SamplerState.FT_linear_mipmap_linear)

		self.MakeGround()
		
		# Helper line
		segs = LineSegs("HelperLine");
		segs.setColor(1, 1 ,1 ,1);
		segs.drawTo(0, 0, 0);
		segs.drawTo(0, 1, 0);
		segsnode = segs.create(False);
		self.helperline = render.attachNewNode(segsnode);
		self.helperline.setScale(30)
		#self.helperline.setHpr(90,0,0)
		
		# Font
		#self.font = loader.loadFont('res/arial_round.ttf')
		self.font = loader.loadFont('res/kingthings_clarity.ttf')
		self.font.setMinfilter(SamplerState.FT_linear_mipmap_linear)
		#self.font.setRenderMode(TextFont.RMSolid) # Solid 3D blocks!
		self.buttonFont = loader.loadFont('res/lady_ice.ttf')
		self.buttonFont.setMinfilter(SamplerState.FT_linear_mipmap_linear)
		
		

		# ======================== 2D interface
		self.GUIStyle = {
			'buttoncolor': (0.7, 0.7, 0.7, 0.7)
		}
		
		# --- Main Screen
		self.MainScreen = {
			'center':self.aspect2d.attachNewNode("MainScreen_Center"),
			'topleft':self.aspect2d.attachNewNode("MainScreen_TopLeft"),
			'topright':self.aspect2d.attachNewNode("MainScreen_TopRight")
		}
		
		''' items = [
					{'name':<name>, 'icon':<icon>, 'action':<callback>},
					...
		]  '''

		self.GUI['ProjFrame'] = self.HUD_BuildFrame(self.MainScreen['topright'], [25,2.5])
		self.GUI['ProjFrame'].setPos(-1.5,0,-0.05)
		self.GUI['ProjFrame'].setAlphaScale(0.75)
		self.GUI['ProjLabel'] = DirectLabel(parent=self.GUI['ProjFrame'], text="", scale=1, pos=(0.65,0,-1.5), text_fg=(1,1,1,1), text_align=TextNode.ALeft)

		self.GUI['Menus'] = {}
		
		# Helper interface
		
		self.GUI['PinHelper'] = DirectLabel(parent=self.MainScreen['center'], text="X", text_fg=(1,1,1,1), text_mayChange=True, frameColor=(0.3,0.3,0.3,0.5), pad=(1.0,0.5), scale=0.05, pos=(0,0,0))
		self.GUI['PinHelper'].hide()

		# Main menu
		self.HUD_BuildMenu(self.MainScreen['topleft'], 'MainMenu', [0.2,0,-0.05], [
			{'name':'Add Item', 	'icon':'icon_add.png', 'action':self.Act_AddBlockList},
			{'name':'New Project', 	'icon':'icon_new.png', 'action':self.Act_NewProject},
			{'name':'Load Project', 'icon':'icon_load.png', 'action':self.Act_LoadProject},
			{'name':'Save Project', 'icon':'icon_save.png', 'action':self.Act_SaveProject},
			{'name':'Quit',			'icon':'icon_quit.png', 'action':self.Act_QuitDialog}
		]).hide()
		self.HUD_CreateSmallButton(self.MainScreen['topleft'], 'icon_down.png', [0.1,0,-0.1], 0.06, self.Act_ToggleMenu, [self.GUI['Menus']['MainMenu'], True])
		
		# Assemble block adding menus
		all_categories = []
		for block_cat in userdata['customBlocks']:
			all_categories.append('AddMenu_'+block_cat['category'])
		
		categories_to_add = []
		for block_cat in userdata['customBlocks']:
			cat_menu_name = 'AddMenu_'+block_cat['category']
			categories_to_add.append({'name':block_cat['category'], 'icon':'icon_blank.png', 'action':self.HUD_ShowMenu, 'args':[cat_menu_name], 'menu_hide':all_categories})
			blocks_to_add = []
			for blockitem in block_cat['blocks']:
				block_name = blockitem['name']
				blocks_to_add.append({'name':blockitem['name'], 'icon':'icon_blank.png', 'action':self.Act_AddBlock, 'args':[blockitem], 'menu_hide':True}) 
			# Create the submenu for this category
			self.HUD_BuildListMenu(self.MainScreen['topleft'], cat_menu_name, [0.8,0,-0.15], 8).hide()
			self.HUD_UpdateListMenu(cat_menu_name, blocks_to_add)
		# Create the add menu
		self.HUD_BuildMenu(self.MainScreen['topleft'], 'AddItemMenu', [0.2,0,-0.20], categories_to_add).hide()
		# Create the Add button
		self.HUD_CreateSmallButton(self.MainScreen['topleft'], 'icon_add.png', [0.1,0,-0.25], 0.06, self.Act_ToggleMenu, [self.GUI['Menus']['AddItemMenu'], True])

		# Export menu
		self.HUD_BuildMenu(self.MainScreen['topleft'], 'ExportMenu', [0.2,0,-0.35], [
			{'name':'Export to File', 		'icon':'icon_new.png', 'action':self.ExportToFile},
			{'name':'Export to Clipboard',	'icon':'icon_copy.png', 'action':self.ExportToClipboard}
		]).hide()
		self.HUD_CreateSmallButton(self.MainScreen['topleft'], 'icon_export.png', [0.1,0,-0.4], 0.06, self.Act_ToggleMenu, [self.GUI['Menus']['ExportMenu'], True])

		
		self.GUI['FloorUp'] = self.HUD_CreateSmallButton(self.MainScreen['topright'], 'icon_up.png', [-0.1,0,-0.85], 0.06, self.Act_FloorUp)
		self.GUI['FloorLabel'] = DirectLabel(text="1", text_pos=(0,-0.23,0), text_fg=(1,1,1,1), scale=0.1, pos=(-0.1,0,-1), parent=self.MainScreen['topright'], relief=None, image=mydir+'/res/squarefield_48.png', image_scale=0.65)
		self.GUI['FloorLabel'].setTransparency(TransparencyAttrib.MAlpha)
		self.GUI['FloorUp'] = self.HUD_CreateSmallButton(self.MainScreen['topright'], 'icon_down.png', [-0.1,0,-1.15], 0.06, self.Act_FloorDown)
		

		# --- Quit Screen
		self.QuitScreen = aspect2d.attachNewNode("QuitScreen")
		
		
		self.GUI['QuitFrame'] = DirectFrame(scale=0.06, pos=(0,0,0), parent=self.QuitScreen, relief=None)
		self.HUD_BuildFrame(self.GUI['QuitFrame'], [32,7], 1.0).setPos(-16,0,2.1)
		self.GUI['QuitLabel'] = DirectLabel(parent=self.QuitScreen, text="Do you want to quit nBlocks Studio Designer?", text_fg=(1,1,1,1), scale=0.05, pos=(0,0,0), relief=None)
		self.GUI['QuitYes'] = DirectButton(parent=self.QuitScreen, text="Yes", scale=0.07, pos=(-0.25,0,-0.2), frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=sys.exit)
		self.GUI['QuitNo'] = DirectButton(parent=self.QuitScreen, text="No", scale=0.07, pos=(0.25,0,-0.2), frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_QuitCancel)
		
		self.QuitScreen.hide()
		
		
		# --- Yes/No Generic Dialog
		self.GenericDialogYesNo = aspect2d.attachNewNode("GenericDialogScreen")
		self.GUI['DialogLabel'] = DirectLabel(parent=self.GenericDialogYesNo, text="", text_fg=(1,1,1,1), scale=0.05, pos=(0,0,0), relief=None)
		self.GUI['DialogYes'] = DirectButton(text="Yes", scale=0.1, pos=(-0.25,0,-0.2), parent=self.GenericDialogYesNo, frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_DialogYes)
		self.GUI['DialogNo'] = DirectButton(text="No", scale=0.1, pos=(0.25,0,-0.2), parent=self.GenericDialogYesNo, frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_DialogNo)
		self.GenericDialogYesNo.hide()

		# --- OK Generic Dialog
		self.GenericDialogOK = aspect2d.attachNewNode("GenericDialogOKScreen")
		
		self.GUI['DialogOKFrame'] = DirectFrame(scale=0.06, pos=(0,0,0), parent=self.GenericDialogOK, relief=None)
		self.HUD_BuildFrame(self.GUI['DialogOKFrame'], [32,7], 1.0).setPos(-16,0,2.1)
		self.GUI['DialogOKLabel'] = DirectLabel(parent=self.GenericDialogOK, text="", text_fg=(1,1,1,1), scale=0.05, pos=(0,0,0), relief=None)
		self.GUI['DialogOK'] = DirectButton(text="OK", scale=0.07, pos=(0,0,-0.2), parent=self.GenericDialogOK, frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_DialogOK)
		self.GenericDialogOK.hide()

		# --- Block Edit Dialog
		self.NodeEditDialog = aspect2d.attachNewNode("NodeEditDialogScreen")
		
		self.GUI['NodeEditDialogFrame'] = DirectFrame(scale=0.06, pos=(0,0,0), parent=self.NodeEditDialog, relief=None)
		self.HUD_BuildFrame(self.GUI['NodeEditDialogFrame'], [32,21], 1.0).setPos(-16,0,10.0)

		p_i = 0
		self.GUI['NodeParamLabel'] = {}
		self.GUI['NodeParamEdit'] = {}
		while (p_i < 4):
			self.GUI['NodeParamLabel'][p_i] = DirectLabel(parent=self.NodeEditDialog, text="", text_fg=(1,1,1,1), text_align=TextNode.ALeft, scale=0.07, pos=(-0.7,0,0.46 - p_i*0.25), relief=None)
			self.GUI['NodeParamEdit'][p_i]  = DirectEntry(parent=self.NodeEditDialog, initialText='', scale=0.07, width=20, pos=(-0.7,0, 0.36 - p_i*0.25), frameColor=(1,1,1,0.7))
			p_i += 1

		self.GUI['NodeEditDialogOK'] = DirectButton(text="OK", scale=0.07, pos=(-0.55,0,-0.55), parent=self.NodeEditDialog, frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_NodeEditDialogOK)
		self.GUI['NodeEditDialogCancel'] = DirectButton(text="Cancel", scale=0.07, pos=(-0.2,0,-0.55), parent=self.NodeEditDialog, frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_NodeEditDialogCancel)
		self.GUI['NodeEditDialogODelete'] = DirectButton(text="Delete Block", scale=0.07, pos=(0.5,0,-0.55), parent=self.NodeEditDialog, frameSize=(-4, 4, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], command=self.Act_NodeEditDialogDelete)
		self.NodeEditDialog.hide()
		
		# --- New Project screen
		self.NewScreen = self.aspect2d.attachNewNode("NewScreen")
		self.Newer = {}

		self.GUI['NewFrame'] = DirectFrame(scale=0.06, pos=(0,0,0), parent=self.NewScreen, relief=None)
		self.HUD_BuildFrame(self.GUI['NewFrame'], [32,12], 1.0).setPos(-16,0,6)

		self.GUI['NewLabel'] = DirectLabel(parent=self.NewScreen, text="Project file name:", text_fg=(1,1,1,1), scale=0.07, pos=(0,0,0.16), relief=None)
		self.Newer['input'] = DirectEntry(parent=self.NewScreen, initialText='new_project', scale=0.07, width=20, pos=(-0.7,0, 0), frameColor=(1,1,1,0.7))
		DirectButton(text="Create", scale=0.07, pos=(-0.25,0,-0.2), frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], parent=self.NewScreen, command=self.Act_NewProjectCreate)
		DirectButton(text="Cancel", scale=0.07, pos=(0.25,0,-0.2), frameSize=(-2, 2, -0.45, 0.9), frameColor=self.GUIStyle['buttoncolor'], parent=self.NewScreen, command=self.Act_NewProjectCancel)
		self.NewScreen.hide()
		

		# --- Load Project Screen
		self.LoadScreen = self.aspect2d.attachNewNode("LoadScreen")
		self.HUD_BuildListMenu(self.LoadScreen, 'LoadMenu', [-0.58,0,0.58], 6, 2.0)#.hide()
		DirectButton(text="Cancel", scale=0.1, pos=(0,0,-0.7), parent=self.LoadScreen, command=self.Act_LoadListCancel)
		self.LoadScreen.hide()
		
		# --- Starting Screen
		self.StartScreen = self.aspect2d.attachNewNode("StartScreen")
		self.StartMenu = self.HUD_BuildMenu(self.StartScreen, 'StartMenu', [-0.30,0,0.3], [
			{'name':'New Project', 	'icon':'icon_new.png', 'action':self.Act_NewProject},
			{'name':'Load Project', 'icon':'icon_load.png', 'action':self.Act_LoadProject},
			{'name':'Quit',			'icon':'icon_quit.png', 'action':self.Act_QuitDialog}
		])
		self.StartMode = True
		self.StartScreen.hide()

		
		
		# ========================  Key events
		#self.accept('x', self.ExportToFile, [])

		#self.accept('w', base.toggleWireframe)
		
		self.accept('0', self.SetLayer, [0])
		self.accept('1', self.SetLayer, [1])
		self.accept('2', self.SetLayer, [2])
		self.accept('3', self.SetLayer, [3])
		self.accept('4', self.SetLayer, [4])
		self.accept('5', self.SetLayer, [5])
		self.accept('6', self.SetLayer, [6])
		self.accept('7', self.SetLayer, [7])
		
		
		self.accept('f1', self.Act_HelpScreen)
		self.accept('f2', self.SetCamType, [1])
		self.accept('f3', self.SetCamType, [2])
		self.accept('f4', self.SetCamType, [3])
		
		self.accept('shift', self.SetShift, [True])
		self.accept('shift-up', self.SetShift, [False])
		self.accept('alt', self.SetAlt, [True])
		self.accept('alt-up', self.SetAlt, [False])
		self.accept('control', self.SetCtrl, [True])
		self.accept('control-up', self.SetCtrl, [False])
		self.accept('mouse1', self.SetMouse1, [True])
		self.accept('mouse1-up', self.SetMouse1, [False])
		self.accept('mouse2', self.SetMouse2, [True])
		self.accept('mouse2-up', self.SetMouse2, [False])
		self.accept('mouse3', self.SetMouse3, [True])
		self.accept('mouse3-up', self.SetMouse3, [False])
		self.accept('wheel_up', self.SetWheel, [-1.0])
		self.accept('wheel_down', self.SetWheel, [1.0])
		
		self.accept('escape',self.Act_Escape) #sys.exit)

		self.accept('aspectRatioChanged', self.Event_ResizeWindow)
		
		self.taskMgr.add(self.CameraTask, "CameraTask")
		
		# ======================== INITIALIZE
		self.SetCamType(2)
		self.SetLayer(1)
		self.ShowHelperLine((0,0,0), (1,0,0), False)

		self.I2d_ShowStartScreen()
		
		
	def Event_ResizeWindow(self):
		winprop = self.win.getProperties()
		self.win_width = winprop.getXSize()
		has_to_resize = False
		if self.win_width < 700:
			self.win_width = 700
			has_to_resize = True
		self.win_height = winprop.getYSize()
		if self.win_height < 500:
			self.win_height = 500
			has_to_resize = True
		if has_to_resize is True:
			#self.win.setSize(self.win_width, self.win_height)
			pass
			
		if self.win_height > self.win_width: # portrait window, width defines sized
			top = (self.win_height*1.0) / (self.win_width*1.0)
			left = -1
			ratio = 600.0 / self.win_width
		else: # landscape window
			top = 1
			left = -(self.win_width*1.0) / (self.win_height*1.0)
			ratio = 600.0 / self.win_height
		right = -left
		
		self.MainScreen['topleft' ].setPos(left ,0,top )
		self.MainScreen['topleft' ].setScale(ratio)
		self.MainScreen['topright'].setPos(right,0,top )
		self.MainScreen['topright' ].setScale(ratio)
		self.MainScreen['center' ].setScale(ratio)
		self.LoadScreen.setScale(ratio)
		self.QuitScreen.setScale(ratio)
		self.StartScreen.setScale(ratio)
		
		self.win_proportion = (self.win_width*1.0) / (self.win_height*1.0)
		
		#print "Resize: "+str([self.win_width, self.win_height])+" TopLeft="+str([left,top])+" Ratio="+str(ratio)

	#===================== Menu Building
	def HUD_HideMenus(self):
		for emenu in self.GUI['Menus']:
			self.GUI['Menus'][emenu].hide()
	def HUD_ShowMenu(self, menu_item):
		if menu_item in self.GUI['Menus']:
			self.GUI['Menus'][menu_item].show()
	def Act_ToggleMenu(self, mmenu, all_menus=False):
		if mmenu.isHidden() is True:
			if all_menus is True:
				self.HUD_HideMenus()
			mmenu.show()
		else:
			if all_menus is True:
				self.HUD_HideMenus()
			else:
				mmenu.hide()
	def HUD_CreateSmallButton(self, btn_parent, btn_icon='', btn_pos=[0,0,0], btn_scale=1.0, btn_command=None, btn_cmd_args=[]):
		btn = DirectButton(parent=btn_parent, image=mydir+'/res/button_48.png', image_scale=(1,1,1), image_pos=(0,0,0), relief=None, scale=btn_scale, pos=(btn_pos[0], btn_pos[1], btn_pos[2]), command=btn_command, extraArgs=btn_cmd_args)
		btn.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=btn, image=mydir+'/res/'+btn_icon, scale=0.7, pos=(0,0,0), relief=None).setTransparency(TransparencyAttrib.MAlpha)
		return btn
	def HUD_CreateButton(self, btn_parent, btn_name, btn_icon='', btn_pos=[0,0,0], btn_command=None, btn_args=[], menu_to_hide=None, btn_scale=1.0):
		btn = DirectButton(image=mydir+'/res/button_210.png', image_scale=(4.375,1,1), image_pos=(0,0,0), text=btn_name, text_fg=(1,1,1,1), text_align=TextNode.ALeft, text_pos=(-2,-0.25,-0), text_scale=0.9, text_font=self.buttonFont, relief=None, scale=btn_scale, command=self.HUD_MenuAction, extraArgs=[btn_command, btn_args, menu_to_hide])
		if btn_parent is not None:
			btn.reparentTo(btn_parent)
		if btn_pos is not None:
			btn.setPos(btn_pos[0], btn_pos[1], btn_pos[2])
		btn.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=btn, image=mydir+'/res/'+btn_icon, scale=0.7, pos=(-3.35,0,0), relief=None).setTransparency(TransparencyAttrib.MAlpha)
		return btn
	def HUD_CreateLargeButton(self, btn_parent, btn_name, btn_icon='', btn_pos=[0,0,0], btn_command=None, btn_args=[], menu_to_hide=None, btn_scale=1.0):
		btn = DirectButton(image=mydir+'/res/button_500.png', image_scale=(9.60,1,1), image_pos=(0,0,0), text=btn_name, text_fg=(1,1,1,1), text_align=TextNode.ALeft, text_pos=(-5,-0.25,-0), text_scale=0.8, relief=None, scale=btn_scale, command=self.HUD_MenuAction, extraArgs=[btn_command, btn_args, menu_to_hide])
		if btn_parent is not None:
			btn.reparentTo(btn_parent)
		if btn_pos is not None:
			btn.setPos(btn_pos[0], btn_pos[1], btn_pos[2])
		btn.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=btn, image=mydir+'/res/'+btn_icon, scale=0.7, pos=(-8.6,0,0), relief=None).setTransparency(TransparencyAttrib.MAlpha)
		return btn
	''' items = [
					{'name':<name>, 'icon':<icon>, 'action':<callback>, 'args':[], 'menu_hide':0},
					...
	]  '''
	def HUD_BuildMenu(self, menu_parent, menu_name, menu_pos=[0,0,0], items=[], large=False): 
		num_items = len(items)
		menu_len = -2.7*num_items-0.3
		#this_menu = DirectFrame(parent=menu_parent, scale=0.058,  frameSize=(0, 10, menu_len, 0), frameColor=(0.0, 0.0, 0.0, 0.63), pos=(menu_pos[0], menu_pos[1], menu_pos[2]))
		this_menu = DirectFrame(parent=menu_parent, scale=0.06,  relief=None, pos=(menu_pos[0], menu_pos[1], menu_pos[2]))
		for i, eitem in enumerate(items):
			itemname = menu_name+':item'+str(i)
			if 'action' not in eitem:
				eitem['action']=None
			if 'args' not in eitem:
				eitem['args'] = []
			if 'menu_hide' not in eitem:
				menu_hide = this_menu
			else:
				menu_hide = eitem['menu_hide']
			if large is True:
				self.GUI[itemname] = self.HUD_CreateLargeButton(this_menu, eitem['name'], eitem['icon'], [5,0,-2.7*i-1.5], eitem['action'], eitem['args'], menu_hide)
			else:
				self.GUI[itemname] = self.HUD_CreateButton(this_menu, eitem['name'], eitem['icon'], [5,0,-2.7*i-1.5], eitem['action'], eitem['args'], menu_hide)
		
		self.HUD_BuildFrame(this_menu, size=[10,-menu_len], frame_scale=1.0)

		self.GUI['Menus'][menu_name] = this_menu
		return this_menu

	def HUD_BuildFrame(self, menu_parent, size=[1,1], frame_scale=0.06):
		corner_size=0.4
		corner_offset = corner_size # size is radius, not diameter
		bar_size_x = size[0]/2.0 # size is radius, not diameter
		bar_size_y = size[1]/2.0 # size is radius, not diameter
		middle_x = size[0] / 2.0
		middle_y = -size[1] / 2.0
		bg = DirectFrame(parent=menu_parent, scale=frame_scale, sortOrder=-1, pos=(0,0,0), frameSize=(0, size[0], -size[1], 0), relief=None)
		bg.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=bg, image=mydir+'/res/frame_tl.png', image_scale=(corner_size,1,corner_size), pos=(corner_offset,0,-corner_offset), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_t.png', image_scale=((bar_size_x-corner_size*2),1,corner_size), pos=(middle_x,0,-corner_offset), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_tr.png', image_scale=(corner_size,1,corner_size), pos=(size[0]-corner_offset,0,-corner_offset), relief=None)

		DirectFrame(parent=bg, image=mydir+'/res/frame_l.png', image_scale=(corner_size,1,(bar_size_y-corner_size*2)), pos=(corner_offset,0,middle_y), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_c.png', image_scale=((bar_size_x-corner_size*2),1,(bar_size_y-corner_size*2)), pos=(middle_x,0,middle_y), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_r.png', image_scale=(corner_size,1,(bar_size_y-corner_size*2)), pos=(size[0]-corner_offset,0,middle_y), relief=None)

		DirectFrame(parent=bg, image=mydir+'/res/frame_bl.png', image_scale=(corner_size,1,corner_size), pos=(corner_offset,0,-(size[1]-corner_offset)), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_b.png', image_scale=((bar_size_x-corner_size*2),1,corner_size), pos=(middle_x,0,-(size[1]-corner_offset)), relief=None)
		DirectFrame(parent=bg, image=mydir+'/res/frame_br.png', image_scale=(corner_size,1,corner_size), pos=(size[0]-corner_offset,0,-(size[1]-corner_offset)), relief=None)

		return bg
		#bg = DirectFrame(parent=menu_parent, image=mydir+'/res/icon_down.png', scale=0.7, pos=(0,0,0), sortOrder=-1, relief=None).setTransparency(TransparencyAttrib.MAlpha)
	def HUD_BuildListMenu(self, menu_parent, menu_name, menu_pos=[0,0,0], num_items=8, horz_scale=1.0):
		menu_len = -2.5*num_items-0.4
		vert_gap = 2.0
		horz_gap = 0.0
		this_menu = DirectScrolledList(parent=menu_parent,
			decButton_pos= (5*horz_scale, 0, 1),
			decButton_relief=None,
			decButton_image=mydir+'/res/button_48.png',
		 
			incButton_pos= (5*horz_scale, 0, menu_len-1),
			incButton_relief=None,
			incButton_image=mydir+'/res/button_48.png',
		 
			frameSize = (0-horz_gap, 10*horz_scale + horz_gap, menu_len-vert_gap, 0+vert_gap),
			frameColor = (0.8,0.8,0.8,0.5),
			relief=None,
			pos = (menu_pos[0], menu_pos[1], menu_pos[2]),
			scale=0.058,
			numItemsVisible = num_items,
			items = [],
			forceHeight = 2.5,
			itemFrame_frameSize = (-4.8*horz_scale, 4.8*horz_scale, menu_len+1.6, 1.35),
			itemFrame_pos = (5*horz_scale, 0, -1.45),
			itemFrame_relief=None
			)
		this_menu.decButton.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=this_menu.decButton, image=mydir+'/res/icon_up.png', scale=0.7, pos=(0,0,0), relief=None).setTransparency(TransparencyAttrib.MAlpha)
		this_menu.incButton.setTransparency(TransparencyAttrib.MAlpha)
		DirectFrame(parent=this_menu.incButton, image=mydir+'/res/icon_down.png', scale=0.7, pos=(0,0,0), relief=None).setTransparency(TransparencyAttrib.MAlpha)
		
		self.HUD_BuildFrame(this_menu, size=[10*horz_scale,-menu_len], frame_scale=1.0)
		
		self.GUI['Menus'][menu_name] = this_menu
		return this_menu
	def HUD_UpdateListMenu(self, menu_name, items=[], large=False):
		if menu_name in self.GUI['Menus']:
			this_menu = self.GUI['Menus'][menu_name]
			this_menu.removeAndDestroyAllItems()
			for i, eitem in enumerate(items):
				itemname = menu_name+':item'+str(i)
				if 'action' not in eitem:
					eitem['action']=None
				if 'args' not in eitem:
					eitem['args'] = []
				if 'menu_hide' not in eitem:
					menu_hide = this_menu
				else:
					menu_hide = eitem['menu_hide']
					
				if large is True:
					b = self.HUD_CreateLargeButton(None, eitem['name'], eitem['icon'], None, eitem['action'], eitem['args'], menu_hide)
				else:
					b = self.HUD_CreateButton(None, eitem['name'], eitem['icon'], None, eitem['action'], eitem['args'], menu_hide)
				
				this_menu.addItem( b )
				#print "Adding["+str(itemname)+"("+str(b.getX())+","+str(b.getZ())+")]: "+str(b)
			

	def HUD_MenuAction(self, callback=None, args=[], menu_to_hide=None):
		if menu_to_hide is True:
			self.HUD_HideMenus()
		elif type(menu_to_hide) is list:
			for emenu in menu_to_hide:
				if emenu in self.GUI['Menus']:
					self.GUI['Menus'][emenu].hide()
		elif menu_to_hide is not None:
			menu_to_hide.hide()
		if callback is not None:
			callback(*args)
		
	# === CameraTask will check which mode we are at and call the appropriate function below
	def CameraTask(self, task):
		mw = base.mouseWatcherNode
		hasMouse = mw.hasMouse()
		if hasMouse:
			# get the window manager's idea of the mouse position
			x, y = mw.getMouseX(), mw.getMouseY()
		else:
			x,y = 0,0
			
		if self.system_mode == MODE_NORMAL:
			self.Process_DiagramInteraction(hasMouse, (x,y))
		if self.system_mode == MODE_SELECTBLOCK:
			self.Process_BlockSelection(hasMouse, (x,y))
		if self.system_mode == MODE_ADDBLOCK:
			self.Process_DiagramInteraction(hasMouse, (x,y))
		if self.system_mode == MODE_DIALOG:
			pass
		
		if self.myo is not None:
			self.myo.run()
			self.myo.tick()	
			#if self.myo.onPeriodic is not None:
			#	self.myo.onPeriodic()
			
		if self.callerWindow is not None:
			try:
				self.callerWindow.update()
			except TclError:
				quit() # window is closed

		return Task.cont
	def CameraMove(self, dx, dy):
		lepos = self.ViewHolder.getPos()
		lerot = self.CamHolder.getHpr()
		campos = self.camera.getPos()
		factor = campos.getZ()/100.0 + 1
		#lepos.addX(dx*factor)
		ang = -radians(lerot[0])
		lepos.addX( ( dx*cos(ang) + dy*sin(ang))*factor)
		#lepos.addY(dy*factor)
		lepos.addY( ( -dx*sin(ang) + dy*cos(ang))*factor)
		self.ViewHolder.setPos(lepos)
		self.ground.setTexOffset(TextureStage.getDefault(), lepos.getX()/10, lepos.getY()/10)
	def CameraZoom(self, delta):
		lepos = self.camera.getPos()
		lepos.addZ(delta*((lepos.getZ()+50)/10.0))
		if (lepos.getZ() < 50): lepos.setZ(50.0)
		if (lepos.getZ() > 1000.0): lepos.setZ(1000.0)
		self.camera.setPos(lepos)
	def CameraRotate(self, dHpr):
		lerot = self.CamHolder.getHpr()
		leH = lerot[0]+dHpr[0]
		if leH > 90: leH = 90
		if leH < -90: leH = -90
		leP = lerot[1]+dHpr[1]
		if leP > 80: leP = 80
		if leP < 0: leP = 0
		#leR = lerot[2]+dHpr[2]
		self.CamHolder.setHpr( ( leH, leP, 0 ) )
	
	#=======================================================
	#=== FRAME CALLING - one of these will be called, depending on the current system state
	def Process_DiagramInteraction(self, hasMouse, cursor):
		x=cursor[0]
		y=cursor[1]
		z=self.ViewHolder.getZ()
		#=== MOVING THE CAMERA
		if ((self.shift_state is True) and (self.mouse1_state is True)) or (self.mouse2_state is True) or (self.myo_grab_state is True):
			# x, y = mouse delta
			self.MouseRecenter()
			# this flag is to make sure we recenter the mouse FIRST
			# and use deltas only in the following frames
			if self.mouse_centred_flag is True: 
				'''
				lepos = self.ViewHolder.getPos()
				campos = self.camera.getPos()
				factor = campos.getZ()/100.0 + 1
				lepos.addX(-x*10*factor)
				lepos.addY(-y*10*factor)
				self.ViewHolder.setPos(lepos)
				self.ground.setTexOffset(TextureStage.getDefault(), lepos.getX()/10, lepos.getY()/10)
				'''
				self.CameraMove(-x*10, -y*10)
			else:
				self.mouse_centred_flag = True

		#=== NORMAL MOUSE CURSOR
		else:
			self.mouse_centred_flag = False
			
			# Are we holding mouse button?
			if (self.mouse1_state is True):
				# Are we grabbing something?
				if self.last_selected is not None:
					if self.ground is not None:
						curpick = self.CollideObject(self.ground, [x, y])
						if curpick is not False:
							cpos = curpick.getSurfacePoint(render)
							self.last_selected.setPos(cpos[0],cpos[1],z)
				
			# Not holding mouse, but hovering
			else:
				# Are we grabbing new block?
				if self.to_be_placed is not None:
					if self.ground is not None:
						curpick = self.CollideObject(self.ground, [x, y])
						if curpick is not False:
							cpos = curpick.getSurfacePoint(render)
							self.to_be_placed.setPos(cpos[0],cpos[1],z)
				else:
					# Looks for picking up objects
					if hasMouse:
						curpick = self.PickObject(self.nBlockNodes_Floors[self.current_floor],     [x, y])
						conpick = self.PickObject(self.nBlockNodeConns, [x, y])
					else: # no mouse
						curpick = None
						conpick = None
					
					if curpick != self.last_picked:
						if self.last_picked is not None:
							self.last_picked.clearColor()
						self.last_picked = curpick
						self.ShowHelperText(curpick, [x, y])
						
					if conpick != self.last_conn_picked:
						print "conn="+str(conpick)
						self.last_conn_picked = conpick
					
					if self.last_conn_selected is not None:
						curpick = self.CollideObject(self.ground, [x, y])
						if curpick is not False:
							cpos = curpick.getSurfacePoint(render)
							cpos[2] += 0.2
							self.ShowHelperLine(self.last_conn_selected.getPos(self.render), cpos, True)
						else:
							self.ShowHelperLine((0,0,0), (1,0,0), False)
					else:
						self.helperline.hide()
						
			if self.spacenav is not None:
				sn_state = self.spacenav.read()
				self.CameraMove(sn_state.x*2.0, sn_state.y*2.0)
				self.CameraZoom(sn_state.z*1.0)
				self.CameraRotate( (-sn_state.yaw*2.0, -sn_state.pitch*2.0, sn_state.roll*2.0) )
				
						
	def Process_BlockSelection(self, hasMouse, cursor):
		pass

	
	#=======================================================
	def SetLayer(self, lnum):
		if ((self.system_mode == MODE_NORMAL) or (self.system_mode == MODE_ADDBLOCK)) and (self.dialog_mode == DIALOG_MAIN):
			self.current_floor = lnum
			self.ViewHolder.setZ((self.current_floor-1)*25)
			# --- Re-work all the alphas
			# Lower layers
			for i in range(0,lnum):
				self.nBlockNodes_Floors[i].setTransparency(TransparencyAttrib.MNone)
				self.nBlockNodes_Floors[i].setAlphaScale(0.7)
			# Current layer
			self.nBlockNodes_Floors[lnum].setTransparency(TransparencyAttrib.MNone)
			self.nBlockNodes_Floors[lnum].setAlphaScale(1.0)
			# Upper layers
			for i in range(lnum+1,self.TotalFloors):
				self.nBlockNodes_Floors[i].setTransparency(TransparencyAttrib.MAlpha)
				self.nBlockNodes_Floors[i].setAlphaScale(0.2)
			# Are we grabbing a block to move it's floor?
			if self.to_be_placed is not None: # Placing new block
				self.to_be_placed.reparentTo(self.nBlockNodes_Floors[self.current_floor])
				self.to_be_placed.setTag('floor', str(self.current_floor))
			if self.last_selected is not None: # Moving existing block
				self.last_selected.reparentTo(self.nBlockNodes_Floors[self.current_floor])
				self.last_selected.setTag('floor', str(self.current_floor))
				
			self.GUI['FloorLabel']['text'] = str(lnum)
			
	def ShowHelperText(self, conn_object, cursor):
		if (conn_object is not False) and (conn_object is not None) and (conn_object.getTag('type') == 'ConnPoint'):
			dir = conn_object.getTag('dir')
			num = int(conn_object.getTag('num'))
			conn_object.setColor(1,1,0,1)
			#print "wp="+str(self.win_proportion)
			try:
				self.GUI['PinHelper']['text'] = conn_object.getParent().getPythonTag('savable')['template']['labels'][dir][num]
				self.GUI['PinHelper'].resetFrameSize()
				self.GUI['PinHelper'].setPos(cursor[0]*self.win_proportion+0.15+0.01*len(self.GUI['PinHelper']['text']), 0, cursor[1]+0.05)
				self.GUI['PinHelper'].show()
			except Exception as e:
				#print "Error: "+str(e)
				self.GUI['PinHelper'].hide()
		else:
			self.GUI['PinHelper'].hide()
	
	def ShowHelperLine(self,from_point, to_point, visible):
		vec = (LPoint3f(to_point)-LPoint3f(from_point))
		dist = vec.length()
		self.helperline.setPos(from_point)
		self.helperline.setScale(dist)
		self.helperline.lookAt(to_point)
		if visible is not False:
			self.helperline.show()
		else:
			self.helperline.hide()
		
	
	# Group is a NodePath object, the collision will traverse only this object and it's children
	def PickObject(self, group, cursor):
		x = cursor[0]
		y = cursor[1]
		self.pickerRay.setFromLens(self.camNode, x, y)
		self.picker.traverse(group) # call one node instead of render to check only it's children?
		
		# has something
		if self.pq.getNumEntries() > 0: 
			self.pq.sortEntries()
			return self.pq.getEntry(0).getIntoNodePath().getParent()
		# nothing selected
		else: 
			return None
	def CollideObject(self, group, cursor):
		x = cursor[0]
		y = cursor[1]
		self.pickerRay.setFromLens(self.camNode, x, y)
		self.picker.traverse(group) # call one node instead of render to check only it's children?
		
		# has something
		if self.pq.getNumEntries() > 0: 
			self.pq.sortEntries()
			return self.pq.getEntry(0)
		# nothing selected
		else: 
			return False
		
	def SetCamType(self, number):
		if ((self.system_mode == MODE_NORMAL) or (self.system_mode == MODE_ADDBLOCK)) and (self.dialog_mode == DIALOG_MAIN):
			cam_type = number
			if (number == 1):
				self.CamHolder.setHpr(0,0,0)
			if (number == 2):
				#self.camera.setPos(0,-100,0)
				#base.camera.setHpr(0,0,0)
				self.CamHolder.setHpr(0,30,0)
			if (number == 3):
				#self.camera.setPos(0,-70,70)
				#base.camera.setHpr(0,-45,0)
				self.CamHolder.setHpr(-15,60,0)
	
	
	def SetShift(self, value): 
		self.shift_state = value
	def SetAlt(self, value): 
		self.alt_state = value
	def SetCtrl(self, value): 
		self.ctrl_state = value
	def SetMouse1(self, value):  # Left click
		self.mouse1_state = value
		self.MouseClick(value)
	def SetMouse2(self, value): # Middle click
		self.mouse2_state = value
	def SetMouse3(self, value): # Right click
		self.mouse3_state = value
		self.MouseRClick(value)
	def SetWheel(self, delta):
		if ((self.system_mode == MODE_NORMAL) or (self.system_mode == MODE_ADDBLOCK)) and (self.dialog_mode == DIALOG_MAIN):
			'''
			lepos = self.camera.getPos()
			lepos.addZ(delta*((lepos.getZ()+50)/10.0))
			if (lepos.getZ() < 50): lepos.setZ(50.0)
			if (lepos.getZ() > 400.0): lepos.setZ(400.0)
			self.camera.setPos(lepos)
			#print "lepos="+str(lepos)
			'''
			self.CameraZoom(delta)
	
	def MouseRelative(self):
		# To set relative mode and hide the cursor:
		props = WindowProperties()
		props.setCursorHidden(True)
		props.setMouseMode(WindowProperties.M_relative)
		self.base.win.requestProperties(props)
		 
	def MouseNormal(self):
		# To revert to normal mode:
		props = WindowProperties()
		props.setCursorHidden(False)
		props.setMouseMode(WindowProperties.M_absolute)
		self.base.win.requestProperties(props)	

	def MouseRecenter(self):
		self.win.movePointer(0, int(self.win_width / 2), int(self.win_height / 2))

	def MouseClick(self, down): # down=True: mouse click / down=False: mouse release
		if (self.shift_state is True):
			pass
		else:
			if down is True:
				if self.to_be_placed is not None:
					self.to_be_placed = None
					self.system_mode = MODE_NORMAL
				else:
					# -- Clicked on something?
					# Is it block?
					if (self.last_picked is not None) and (self.last_picked.getTag('type') == 'Block'):
						self.last_selected = self.last_picked.getParent()
					#Is it Connection?
					elif (self.last_picked is not None) and (self.last_picked.getTag('type') == 'ConnPoint'):
						if self.last_conn_selected is None: # First conn edge
							self.last_conn_selected = self.last_picked
						else: # second conn edge 
							if (self.last_conn_selected.getTag('dir') == 'output') and (self.last_picked.getTag('dir') == 'input'): # output->input?
								self.MakeConnection(self.last_conn_selected, self.last_picked)
							if (self.last_conn_selected.getTag('dir') == 'input') and (self.last_picked.getTag('dir') == 'output'): # input->output? link backwards
								self.MakeConnection(self.last_picked, self.last_conn_selected)
							self.last_conn_selected = None
						#print "ConnPoint: "+str(self.last_picked)+" Parent: "+str(self.last_picked.getParent())
					else:
						self.last_selected = None
						self.last_conn_selected = None
			else:
				if self.last_selected is not None: # did we just release a block?
					self.RefreshAllConnections()
				self.last_selected = None

		
	def MouseRClick(self, down): # down=True: mouse click / down=False: mouse release
		if down is True:
			if (self.last_picked is not None) and (self.last_picked.getTag('type') == 'Block'): # right-clicked a block
				
				self.last_edited = self.last_picked
				self.last_picked = None
				self.last_selected = None
				self.last_conn_selected = None
				
				params = self.last_edited.getParent().getPythonTag('savable')['template']['parameters']
				p_i = 0
				while (p_i < len(params)):
					self.GUI['NodeParamLabel'][p_i]['text'] = params[p_i]['name']
					self.GUI['NodeParamLabel'][p_i].show()
					self.GUI['NodeParamEdit'][p_i].enterText(str(params[p_i]['value']))
					self.GUI['NodeParamEdit'][p_i].show()
					p_i += 1
				while (p_i < 4):
					self.GUI['NodeParamLabel'][p_i].hide()
					self.GUI['NodeParamEdit'][p_i].hide()
					p_i += 1
				
				self.I2d_HideMainWindow()
				self.NodeEditDialog.show()
				self.system_mode = MODE_DIALOG
				self.dialog_mode = DIALOG_PARAMETERS
				
				
				#self.last_picked.getParent().setRenderModeWireframe() 
				#self.last_picked.getParent().setRenderModeFilledWireframe( (1,1,0,0.5) ) 

	#=== OBJECT CREATION
	def MakeGround(self):
		cm = CardMaker('GroundMaker')
		#cm.setUvRange(self.GroundTexture) #(-100,100),(-100,-100),(-100,100),(100,100))
		cm.setFrame(-500,500,-500,500)
		gnode = render.attachNewNode(cm.generate())
		
		ts = TextureStage.getDefault()
		gnode.setTexture(ts, self.GroundTexture)
		gnode.setTexScale(ts, 100, 100)
		gnode.setPos(0,200,-3)
		gnode.setHpr(0,-90,0)
		gnode.setTransparency(TransparencyAttrib.MAlpha)
		gnode.setAlphaScale(0.8)
		gnode.reparentTo(self.ViewHolder)
		self.ground = gnode
		
	def MakeBlockNode(self, blockItem, forceName=None):
		# Params
		blockItem['inputs'] = int(blockItem['inputs'])
		blockItem['outputs'] = int(blockItem['outputs'])
		if ('parameters' not in blockItem) or (type(blockItem['parameters']) is not list):
			blockItem['parameters'] = []
		
		conndist = 3.5 # distance between connections
		bsize = blockItem['inputs']
		if blockItem['outputs'] > bsize:
			bsize = blockItem['outputs']
		#bsize *= 1.5
		
		# Model:
		if forceName is not None:
			iname = forceName
		else:
			iname = 'nBlockNode'+str(self.node_iterator)+'_'+blockItem['name']
			
		m = self.nBlockNodes_Floors[self.current_floor].attachNewNode(iname)
		self.node_iterator += 1
		m.setPos(0.0,0.0,0.0)
		m.setScale(1.0)
		b = loader.loadModel(mydir + "/models/block.egg")
		b.reparentTo(m)
		b.setScale(7.0, 7.0+conndist*(bsize-1) ,7.0)
		b.setPos(0.0,0.0,0.0)
		b.setTag('type','Block')
		# Text:
		t = TextNode('Title'+str(self.node_iterator))
		t.setFont(self.font)
		t.setText(blockItem['name'])
		t.setTextColor(0, 0, 0, 1)
		t.setAlign(TextNode.ACenter)
		tn = m.attachNewNode(t)
		tn.setAttrib(DepthTestAttrib.make(RenderAttrib.MLessEqual ))
		tn.setPos(0.0,-3.8,1.5)
		tn.setHpr(0.0,-80.0,0.0)
		tn.setScale(1.75)
		# Connection balls
		local_conns = {'inputs':{},'outputs':{}} # to create a loadable
		for i in range(0,blockItem['inputs']):
			bb = loader.loadModel(mydir + "/models/clickball_left.egg")
			bb.setName('input'+str(i))
			bb.reparentTo(m)
			bb.setPos(-7,-3.5-conndist*i,0)
			bb.setScale(2.1)
			bb.setTag('type','ConnPoint')
			bb.setTag('dir','input')
			bb.setTag('num',str(i))
			local_conns['inputs'][i] = bb
		for i in range(0,blockItem['outputs']):
			bb = loader.loadModel(mydir + "/models/clickball_right.egg")
			bb.setName('output'+str(i))
			bb.setPos(7,-3.5-conndist*i,0)
			bb.reparentTo(m)
			bb.setScale(2.1)
			bb.setTag('type','ConnPoint')
			bb.setTag('dir','output')
			bb.setTag('num',str(i))
			local_conns['outputs'][i] = bb
		m.setTag('floor', str(self.current_floor))
		m.setPythonTag('savable', {'template':blockItem,'name':iname})
		m.setPythonTag('loadable', local_conns)
		self.block_list.append(m)
		self.nBlockNodeList[iname] = m
		return m
	
	def RemoveBlockNode(self, blocknode):
		if blocknode in self.block_list:
			self.DeleteConnectionsInvolving(blocknode)
			self.block_list.remove(blocknode)
			del self.nBlockNodeList[blocknode.getName()]
			blocknode.removeNode()
			return True
		else:
			return False
		
	def MakeConnection(self, source_conn, target_conn):
		if self.FindConnectionBetween(source_conn, target_conn, True) is False:
			r = Rope()
			r.reparentTo(self.nBlockNodeConns)
			r.ropeNode.setNumSubdiv(12)
			r.ropeNode.setRenderMode(RopeNode.RMTube)
			r.ropeNode.setUseVertexColor(1)
			r.ropeNode.setUseVertexThickness(1)
			self.ReshapeConnection(r, source_conn, target_conn)
			self.connection_list.append({'rope':r,'source':source_conn, 'target':target_conn})
	
	# Finds a connection involving one specific block (source or target). Optionally deletes it
	def DeleteConnectionsInvolving(self, blocknode):
		i = len(self.connection_list)
		while (i > 0):
			i -= 1
			conn_item = self.connection_list[i]
			if (conn_item['source'].getParent() == blocknode) or (conn_item['target'].getParent() == blocknode):
				r = conn_item['rope']
				self.connection_list.pop(i)
				r.removeNode()
		
	# Finds a connection between two specific connection points. Optionally deletes it
	def FindConnectionBetween(self, source, target, delete=False):
		for conn_item in self.connection_list:
			if (conn_item['source'] == source) and (conn_item['target'] == target):
				eitem = conn_item
				if delete is True:
					eitem['rope'].removeNode()
					self.connection_list.remove(eitem)
					return True
				else:
					return eitem
			#else continue with the loop
		return False
		
	def ReshapeConnection(self, conn, source_conn, target_conn):
		conn.setup(3, [	{'node':source_conn, 'point':( 0,0,0), 'color':(0.4, 7.0, 0.4, 0.7), 'thickness':(1.0)},
						{'node':source_conn, 'point':( 7,0,0), 'color':(0.7, 0.7, 0.7, 0.7), 'thickness':(0.5)},
						{'node':target_conn, 'point':(-7,0,0), 'color':(0.7, 0.7, 0.7, 0.7), 'thickness':(0.5)},
						{'node':target_conn, 'point':( 0,0,0), 'color':(0.4, 0.4, 7.0, 0.7), 'thickness':(1.0)}])
						
	def RefreshAllConnections(self):
		#for conn_item in self.connection_list:
		#	self.ReshapeConnection(conn_item['rope'], conn_item['source'], conn_item['target'])
		pass
			
						
	#=== 2D interface functions
	def Act_HelpScreen(self):
		pass
		#print "help"
	def Act_Escape(self):
		if self.dialog_mode == DIALOG_ADDNBLOCKNODE:
			self.Act_AddBlockListCancel()
		if self.dialog_mode == DIALOG_QUIT:
			self.Act_QuitCancel()
		elif self.dialog_mode == DIALOG_MAIN:
			self.Act_QuitDialog()
			
	def I2d_HideMainWindow(self):
		self.MainScreen['center'].hide()
		self.MainScreen['topleft'].hide()
		self.MainScreen['topright'].hide()
		self.nBlockNodes.setRenderModeWireframe() 
		self.nBlockNodeConns.setRenderModeWireframe()
	def I2d_ShowMainWindow(self):
		self.MainScreen['center'].show()
		self.MainScreen['topleft'].show()
		self.MainScreen['topright'].show()
		self.nBlockNodes.setRenderModeFilled() 
		self.nBlockNodeConns.setRenderModeFilled()
	def I2d_ShowStartScreen(self):
		self.I2d_HideMainWindow()
		self.system_mode = MODE_DIALOG 
		self.dialog_mode = DIALOG_START
		self.StartMenu.show()
		self.StartScreen.show()

		
	def Act_AddBlockList(self):
		self.I2d_HideMainWindow()
		self.AddScreen.show()
		self.system_mode = MODE_SELECTBLOCK
		self.dialog_mode = DIALOG_ADDNBLOCKNODE
		
	def Act_AddBlockListCancel(self):
		self.AddScreen.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN

	def Act_AddBlock(self, blockItem):
		#self.AddScreen.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_ADDBLOCK
		self.dialog_mode = DIALOG_MAIN
		self.to_be_placed = self.MakeBlockNode(blockItem)

	def Act_RemoveSelectedBlock(self):
		self.RemoveBlockNode(self.last_edited.getParent())
		self.last_edited = None
		self.last_picked = None
		self.last_selected = None
		self.last_conn_selected = None

	def Act_LoadList(self):
		self.I2d_HideMainWindow()
		plist = nblocksfile.ListProjects()
		projs_list = []
		for eproj in plist:
			projs_list.append({
				'name': eproj,
				'icon': 'icon_new.png',
				'action':self.LoadProject,
				'args':[eproj]
			})
		self.HUD_UpdateListMenu('LoadMenu', projs_list, True)

		self.GUI['Menus']['LoadMenu'].show()
		self.LoadScreen.show()
		self.system_mode = MODE_DIALOG
		self.dialog_mode = DIALOG_LOAD
		
	
	def Act_LoadListCancel(self):
		self.LoadScreen.hide()
		if self.StartMode is True:
			self.I2d_ShowStartScreen()
		else:
			self.system_mode = MODE_NORMAL
			self.dialog_mode = DIALOG_MAIN
			self.I2d_ShowMainWindow()
	


	def Act_FloorUp(self):
		if self.current_floor < (self.TotalFloors-1):
			self.SetLayer(self.current_floor + 1)
	def Act_FloorDown(self):
		if self.current_floor > 0:
			self.SetLayer(self.current_floor - 1)
	
	
	def Act_QuitDialog(self):
		self.I2d_HideMainWindow()
		self.QuitScreen.show()
		self.system_mode = MODE_DIALOG
		self.dialog_mode = DIALOG_QUIT
	def Act_QuitCancel(self):
		self.QuitScreen.hide()
		if self.StartMode is True:
			self.I2d_ShowStartScreen()
		else:
			self.system_mode = MODE_NORMAL
			self.dialog_mode = DIALOG_MAIN
			self.I2d_ShowMainWindow()
		
	def Act_ShowDialog(self, dialog_text, yes_callback, no_callback=None):
		self.I2d_HideMainWindow()
		self.GUI['DialogLabel']['text'] = dialog_text
		self.dialog_yes_callback = yes_callback
		self.dialog_no_callback = no_callback
		self.GenericDialogYesNo.show()
		self.system_mode = MODE_DIALOG
		self.dialog_mode = DIALOG_GENERIC
	def Act_CancelDialog(self):
		self.GenericDialogYesNo.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
	def Act_ShowDialogOK(self, dialog_text):
		self.I2d_HideMainWindow()
		self.GUI['DialogOKLabel']['text'] = dialog_text
		self.GenericDialogOK.show()
		self.system_mode = MODE_DIALOG
		self.dialog_mode = DIALOG_GENERIC
	
	def Act_DialogYes(self):
		if self.dialog_yes_callback is not None:
			self.dialog_yes_callback()
		self.Act_CancelDialog()
	def Act_DialogNo(self):
		if self.dialog_no_callback is not None:
			self.dialog_no_callback()
		self.Act_CancelDialog()
	def Act_DialogOK(self):
		self.GenericDialogOK.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
		
	def Act_NodeEditDialogOK(self):
		m = self.last_edited.getParent()
		savable = m.getPythonTag('savable')
		plen = len(savable['template']['parameters'])
		p_i = 0
		while (p_i < plen):
			try:
				val = self.GUI['NodeParamEdit'][p_i].get(True) # True removes formatting characters
				if (savable['template']['parameters'][p_i]['type'] == 'int'):
					val = int(val)
				savable['template']['parameters'][p_i]['value'] = val
			except: pass
			p_i += 1
		m.setPythonTag('savable', savable)		
		self.last_edited = None
		self.NodeEditDialog.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
		
	def Act_NodeEditDialogCancel(self):
		self.NodeEditDialog.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
		
	def Act_NodeEditDialogDelete(self):
		self.Act_RemoveSelectedBlock()
		self.NodeEditDialog.hide()
		self.I2d_ShowMainWindow()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
			
	def Act_NewProject(self):
		#self.Act_ShowDialog("Discard changes and start a new project?", self.NewProject)
		self.I2d_HideMainWindow()
		self.NewScreen.show()
		self.system_mode = MODE_DIALOG
		self.dialog_mode = DIALOG_NEW
		
	def ClearProject(self):
		self.node_iterator = 0
		i = len(self.block_list)
		while (i > 0):
			i -= 1
			self.RemoveBlockNode( self.block_list[i] )
	
	def Act_NewProjectCreate(self):
		filename = self.Newer['input'].get(True) # argument is plaintext?
		self.project_name = filename
		self.GUI['ProjLabel']['text'] = self.project_name
		self.ClearProject()
		self.NewScreen.hide()
		self.system_mode = MODE_NORMAL
		self.dialog_mode = DIALOG_MAIN
		self.StartMode = False
		self.I2d_ShowMainWindow()
		
	def Act_NewProjectCancel(self):
		#if self.project_name is not None:
		self.NewScreen.hide()
		if self.StartMode is True:
			self.I2d_ShowStartScreen()
		else:
			self.system_mode = MODE_NORMAL
			self.dialog_mode = DIALOG_MAIN
			self.I2d_ShowMainWindow()
		#else:
		#	sys.exit()

		
		
		
	def Act_LoadProject(self):
		self.Act_LoadList()
	def Act_SaveProject(self):
		self.SaveProject()
		
		
	def LoadProject(self, filename):
		load_point = nblocksfile.LoadProjectFromFile(filename+'.nsd')
		if load_point is not None:
			self.project_name = filename
			self.ClearProject()
			self.GUI['ProjLabel']['text'] = self.project_name
					
			node_list = load_point['nBlockNodes']
			for enode in node_list:
				m = self.MakeBlockNode(enode['template'], enode['name'])
				m.setPos( enode['pos'][0], enode['pos'][1], enode['pos'][2] )
				m.reparentTo(self.nBlockNodes_Floors[ int(enode['layer']) ])
				m.setTag('floor', str( enode['layer'] ))
				
			conn_list = load_point['nBlockNode Connections']
			for econn in conn_list:
				#try:
				source_loadable = self.nBlockNodeList[ econn['source_node'] ].getPythonTag('loadable')
				target_loadable = self.nBlockNodeList[ econn['target_node'] ].getPythonTag('loadable')
				
				source_conn = source_loadable['outputs'][ int(econn['source_output']) ]
				target_conn = target_loadable['inputs'][ int(econn['target_input']) ]
				self.MakeConnection(source_conn, target_conn)
			self.node_iterator = load_point['Node Iterator']
			self.StartMode = False
			self.Act_LoadListCancel()
		else:
			return False
		
	def SaveProject(self):
		save_point = {'nBlockNodes':[], 'nBlockNode Connections':[], 'Node Iterator':0}
		node_list = self.nBlockNodeList.keys()
		for eblocknodename in node_list:
			eblocknode = self.nBlockNodeList[eblocknodename]
			enodeinfo = eblocknode.getPythonTag('savable')
			enodeinfo['pos'] = [eblocknode.getX(), eblocknode.getY(), eblocknode.getZ()]
			enodeinfo['layer'] = int(eblocknode.getTag('floor'))
			save_point['nBlockNodes'].append(enodeinfo)
		for econn in self.connection_list:
			econn_src = econn['source']
			enode_src = econn_src.getParent().getName()
			econn_tgt = econn['target']
			enode_tgt = econn_tgt.getParent().getName()
			save_point['nBlockNode Connections'].append({'source_node':enode_src, 'source_output':int(econn_src.getTag('num')), 'target_node':enode_tgt, 'target_input':int(econn_tgt.getTag('num'))})
		save_point['Node Iterator'] = self.node_iterator
		nblocksfile.SaveProjectToFile(self.project_name+'.nsd', save_point)

		
	# ========================
	# Compiler Interface
	def GenerateOutput(self):
		outstr  = "/* ================================================================ *\n"
		outstr += " *       Automatically generated by n-Blocks Studio Designer        *\n"
		outstr += " *                                                                  *\n"
		outstr += " *                         www.n-blocks.net                         *\n"
		outstr += " * ================================================================ */\n"
		outstr += "#include \"nblocks.h\"\n"
		catlist = self.user_data['customBlocks']
		for ecat in catlist:
			for etype in ecat['blocks']:
				libtitle = etype['name']
				if libtitle in nblocksfile.defaultLibs:
					pass
					#libname = nblocksfile.defaultLibs[libtitle]
				else:
					libname = libtitle.lower()
					outstr += "#include \""+str(libname)+".h\"\n"
			
		outstr += "\n\n// -*-*- List of node objects -*-*-\n"
		

		node_list = self.nBlockNodeList.keys()
		for eblocknodename in node_list:
			eblocknode = self.nBlockNodeList[eblocknodename]
			enodeinfo = eblocknode.getPythonTag('savable')
			class_str = "nBlock_"+str(enodeinfo['template']['name'])
			outstr += class_str
			rlen = 30 - len(class_str)
			if rlen > 0:
				while rlen > 0:
					outstr += ' '
					rlen -= 1
			outstr += "nb_"+str(enodeinfo['name'])
			# Parameters?
			params_str = ''
			p_i = 0
			params = enodeinfo['template']['parameters']
			plen = len(params)
			if plen > 0:
				while (p_i < plen):
					if (params_str != ''):
						params_str += ','
					if (params[p_i]['type'] == 'string'):
						params_str += '"'+str(params[p_i]['value'])+'"'
					else:
						params_str += str(params[p_i]['value'])
					p_i += 1
				outstr += '('+params_str+')'
			outstr += ";\n"

		outstr += "\n// -*-*- List of connection objects -*-*-\n"

		i = 0
		for econn in self.connection_list:
			econn_src = econn['source']
			enode_srci = econn_src.getParent().getPythonTag('savable')
			outnum = econn_src.getTag('num')
			
			econn_tgt = econn['target']
			enode_tgti = econn_tgt.getParent().getPythonTag('savable')
			innum = econn_tgt.getTag('num')
			
			outstr += "nBlockConnection         n_conn"+str(i)+"(&nb_"+str(enode_srci['name'])+", "+str(outnum)+", &nb_"+str(enode_tgti['name'])+", "+str(innum)+");\n"
			i += 1

		outstr += "\n// -*-*- Main function -*-*-\n"
		outstr += "int main(void) {\n    SetupWorkbench();\n    while(1) {\n        // Your custom code here!\n    }\n}\n"
		
		return outstr
			
	def ExportToFile(self):
		filename = nblocksfile.RequestExportToFile().strip()
		#print "Le filename is: ["+str(filename)+"]"
		nblockssys.SetWindowFocus(self.windowHandle)
		if filename != '':
			if filename.endswith('.cpp') is False:
				filename += '.cpp'
			print "Saving filename: "+filename
			try:
				with open(filename, "w") as text_file:
					text_file.write(self.GenerateOutput())
				print "Saved successfully"
			except:
				print "Error while saving file"
			#print self.GenerateOutput()
			
	def ExportToClipboard(self):
		nblockssys.CopyToClipboard(self.GenerateOutput())
		self.Act_ShowDialogOK("The source code was exported to your clipboard.\nNow go to your file editor and paste.")
		
		pass
			
	# ========================
	# Hardware Interfaces
	def HAL_Myo_Init(self, myo_object):
		self.myo = myo_object
		if self.myo is not None:
			self.myo.onPeriodic = self.HAL_Myo_onPeriodic
			self.myo.onPoseEdge = self.HAL_Myo_onPoseEdge
	
	def HAL_Myo_onPeriodic(self):
		#return
		if self.myo.getPose() == 'fist': 
			self.win.movePointer(0, int((self.win_width / 2)+self.myo.rotYaw()*2000), int((self.win_height / 2)-self.myo.rotPitch()*2000))
			self.myo.rotSetCenter()
		#self.myo.mouseMove(int((self.win_width / 2)+self.myo.rotYaw()*2000), int((self.win_height / 2)-self.myo.rotPitch()*2000))


		
	def HAL_Myo_onPoseEdge(self, pose, edge):
		#return
		if pose == 'fist':
			if edge == 'on':
				self.myo.rotSetCenter()
				self.myo_grab_state = True
			else:
				self.myo_grab_state = False
			print "onPoseEdge: "+str(pose)+" "+str(edge)
			
			
			
			
			
	def HAL_SpaceNav_Init(self, spacenav_object):
		self.spacenav = spacenav_object
		if self.spacenav is not None:
			self.spacenav.set_led(True)
