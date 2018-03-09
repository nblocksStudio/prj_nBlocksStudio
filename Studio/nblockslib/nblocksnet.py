'''
	=== n-Blocks Studio internet access library ===
	
	This library contains functions used to access n-blocks.net accounts
	
	Author:
		Fernando Cosentino
		Nimbus Centre
		Cork Institute of Technology
'''

import os
import time
import json
import requests
import hashlib
from threading import Timer

# Main Studio URL
#studio_url = 'http://157.190.53.81/public/nblocksstudio/'
studio_url = 'http://www.n-blocks.net/studio/'

def md5(val):
	md5hasher = hashlib.md5()
	md5hasher.update(val)
	return md5hasher.hexdigest()

#=== LOCAL CREDENTIALS
# Stored as JSON-syntax file:
# { "user": "<username>", "pass": "<MD5 password>" }

# Load Credentials from local file
#   returns credentials dictionary on success
#   returns False on failure
def LoadCredentials():
	try:
		with open('credentials.json') as data_file:    
			user_data = json.load(data_file)
			data_file.close()
		return user_data
	except:
		return False

# Save Credentials to local file
#   returns True on success
#   returns False on failure
def SaveCredentials(username, password, autologin):
	user_data = { "user": username, "pass": md5( password ), "autologin": autologin }
	try:
		with open('credentials.json', 'w') as outfile:
			json.dump(user_data, outfile, separators=(",\n",': '))
			outfile.close()
		return True
	except:
		return False

#=== NET LOGIN
	
def RetrieveUserData(user_credentials, callback):
	# dummy version
	'''
	if (user_credentials['user'] == 'fernando.cosentino') and (user_credentials['pass'] == md5('123456')):
		return callback({
			"auth":1,
			"customBlocks": [
				{"category":"Input", "name":"nGPI","inputs":0,"outputs":1}
			]
		})
	else:
		return callback({'auth':0})'''
	
	# real version
	payload = {}
	payload['user'] = user_credentials['user']
	payload['pass'] = user_credentials['pass']
	
	r = requests.get(studio_url + 'studio_login.php', params=payload)
	#return r.text
	#return json.loads(res)
	try:
		res = r.json()
	except:
		res = {'auth':-1}
	callback(res)
	return 0
		