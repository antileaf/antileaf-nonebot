import requests
import ujson

from typing import *

def call_api_get(url : str, params : Dict[str, str] = {}, data : Dict[str, Any] = {}) -> Dict[str, Any]:
	# params = ujson.dump(params)
	# data = ujson.dump(data)

	return requests.get(url + '?' + '&'.join([f'{o}={params[o]}' for o in params]), data = ujson.dumps(data)).json()

def call_api_post(url : str, params : Dict[str, str] = {}, data : Dict[str, Any] = {}) -> Dict[str, Any]:
	# params = ujson.dump(params)
	# data = ujson.dump(data)

	return requests.post(url, params = ujson.dumps(params), data = ujson.dumps(data)).json()