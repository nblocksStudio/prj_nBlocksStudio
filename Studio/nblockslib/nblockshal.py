import serial
from serial.serialutil import SerialException
import _winreg as winreg
import re
from hardwarelib.PyoConnect import *
from hardwarelib import spacenavigator

myo = None

# ========================
# This finds the last port assigned to Myo, even if no longer connected
# You must check win32_serial_ports() to see if it's still online
def win32_find_myo_port():
	path = 'SYSTEM\\CurrentControlSet\\Enum\\USB\\VID_2458&PID_0001\\1\\Device Parameters'
	key = None
	try:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
		info = winreg.QueryInfoKey(key)
		values_count = info[1]
		i = 0
		while (i < values_count):
			val = winreg.EnumValue(key, i) #(keyname, value, type), type 1: REG_SZ
			if val[0] == 'PortName': # That's the keyname we are interested in
				portname = val[1]
				winreg.CloseKey(key)
				return portname
			# else continue with loop
		# If loop ended, we don't have PortName
		winreg.CloseKey(key)
		return None
	except WindowsError:
		if key is not None:
			winreg.CloseKey(key)
		return None

# ========================
# This finds the current active serial ports under windows
def win32_serial_ports():
	path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
	res = []
	key = None
	try:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
		info = winreg.QueryInfoKey(key)
		device_count = info[1]
		i = 0
		while (i < device_count):
			val = winreg.EnumValue(key, i) #(device_identifier, COMport, type), type 1: REG_SZ
			pname = val[1]
			m = re.match('^COM(\d+)$', pname)
			if m:
				res.append(pname)
			else:
				res.append('\\\\.\\'+pname)
			i += 1
		winreg.CloseKey(key)
		return res
	except WindowsError:
		if key is not None:
			winreg.CloseKey(key)
		return []

# ========================
# Checks if Myo is definitely available
# checking simultaneously the installed port and available ports
def MyoPresent():
	print "Checking myo (platform: "+str(sys.platform)+")"
	try:
		if sys.platform=='win32': # windows
			myo_port = win32_find_myo_port()
			serial_ports = win32_serial_ports()
		elif sys.platform.startswith('linux'): # Linux
			myo_port = '/dev/ttyACM0'
			serial_ports = []
			pass # TODO
		else:
			return False # no Myo available under unsupported OS
	except OSError:
		return False # no Myo available when OS error

	if myo_port is None:
		return False # This computer doesn't have a Myo device

	if myo_port in serial_ports:
		return myo_port # Myo is here
	else:
		return False # Myo was installed in this computer but is not currently connected

		
# ========================
# Creates a Myo object in the correct serial port
# If no Myo available, returns None
# Myo is a product by Thalmic Labs
def CreateMyo():
	global myo
	
	myo_port = MyoPresent()
	if (myo_port is not None) and (myo_port is not False):
		try:
			myo = Myo(cls=None, tty=myo_port)
			if myo.connect() is True:
				myo.setLockingPolicy('none')
				myo.unlock('hold')
				myo.notifyUserAction()
			else:
				myo = None
		except SerialException:
			myo = None # Myo already under use by MyoConnect
	else:
		myo = None
	
	return myo
	
###=================================================================================
def SpaceNavPresent():
	dlist = spacenavigator.list_devices()
	if len(dlist) == 0:
		return False
	else:
		return dlist[0]

def CreateSpaceNav():
	device = SpaceNavPresent()
	if device is False:
		return None
	else:
		sn_obj = spacenavigator.open(device=device)
	return sn_obj

