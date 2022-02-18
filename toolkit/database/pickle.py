import toolkit

from typing import *

import pickle

def get_pk_file(name : str):
	return f'data/{name}.pk'

def save(name : str, content : Any):
	with open(get_pk_file(name), 'wb') as f:
		pickle.dump(content, f)


def load(name : str) -> Optional[Any]:
	try:
		with open(get_pk_file(name), 'rb') as f:
			content = pickle.load(f)
	
	except:
		return None
		
	else:
		return content