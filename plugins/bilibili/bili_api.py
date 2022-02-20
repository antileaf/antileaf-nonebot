import toolkit
import requests

from typing import *

def room_init(room_id : int):
	return toolkit.callapi.call_api_get('http://api.live.bilibili.com/room/v1/Room/room_init', {'id' : room_id})

def get_status_info_by_uids(uids : List[int]):
	return toolkit.callapi.call_api_post('http://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids', data = {'uids' : uids})