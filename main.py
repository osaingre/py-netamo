import netatmo

def main():
		try:
				tok = netatmo.get_token(
						client_id='xxx',
						client_secret='xxx',
						username='xxx',
						password='xxx')
		except netatmo.NetAtmoException, e:
				print "ERROR: cannot get token: %s" % e
				return

		devs, mods = netatmo.get_devices(tok)
		for dev in devs:
				dev_id = dev['_id']
				for stamp, x in netatmo.get_measure(tok, dev_id,
							[netatmo.HUMIDITY, netatmo.TEMPERATURE]):
						print stamp, x

if __name__ == '__main__':
		main()
