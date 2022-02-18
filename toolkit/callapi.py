import requests

from typing import *

def call_api(url : str, args : Dict[str, str]) -> Dict[str, Any]:
	res = requests.get(url + '?' + '&'.join([f'{s}={args[s]}' for s in args]))

	return res.json()