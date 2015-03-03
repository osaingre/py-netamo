import datetime
import httplib
import json
import urllib

SERVER = "api.netatmo.net"

HUMIDITY = 'Humidity'
TEMPERATURE = 'Temperature'

class NetAtmoException(Exception):
		def __init__(self, code, message):
				Exception.__init__(self, "%s (%s)" % (message, code))
				self.code = code
				self.message = message

def _post_request(service, params, addr=SERVER):
		headers = {
				"Content-type" : "application/x-www-form-urlencoded;charset=UTF-8"
		}

		conn = httplib.HTTPSConnection(addr)
		try:
				conn.request("POST", service, urllib.urlencode(params), headers)
				resp = conn.getresponse()
				if resp.status != 200:
						details = json.loads(resp.read())
						error = details['error']
						if isinstance(error, dict):
								msg = details['error']['message']
								code = details['error']['code']
								raise NetAtmoException(code, msg)
						else:
								raise NetAtmoException('', error)
				return resp.read()
		finally:
				conn.close()

def get_token(client_id, client_secret, username, password):
		params = {
				'grant_type' : 'password',
				'client_id' : client_id,
				'client_secret' : client_secret,
				'username' : username,
				'password' : password,
				'scope' : 'read_station',
		}
		tok = json.loads(_post_request("/oauth2/token", params))
		return tok

def get_devices(tok):
		params = { 'access_token' : tok['access_token'] }
		data = json.loads(_post_request("/api/devicelist", params))
		body = data['body']
		return body['devices'], body['modules']

def get_measure(token, device_id, types):
		params = {
				'access_token' : token['access_token'],
				'device_id' : device_id,
				'scale' : 'max',
				'optimize' : 'true',
				'type' : ','.join(types),
		}
		data = json.loads(_post_request("/api/getmeasure", params))
		for sample in data['body']:
				stamp = datetime.datetime.utcfromtimestamp(sample['beg_time'])
				step = sample.get('step_time', 0)
				for x in sample['value']:
						yield stamp, x
						stamp += datetime.timedelta(seconds=step)
