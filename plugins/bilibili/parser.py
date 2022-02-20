from typing import *

import ujson

import toolkit

from . import bili_api


def get_room_url(room_id : int) -> str:
	return f'https://live.bilibili.com/{room_id}'


def check_live_status(room_id : int) -> int:
	'''
	-1 : 直播间不存在
	0 : 未开播
	1 : 已开播
	'''

	info = bili_api.room_init(room_id)

	if info['code'] > 60000: # 60004
		return -1
	
	return int(info['data']['live_status'] == 1)


def get_room_uid(room_id : int) -> int:
	'''
	查询主播 uid，-1表示出错或者直播间不存在
	'''

	info = bili_api.room_init(room_id)

	if info['code']:
		return -1
	
	if info['data']['live_status'] < 0:
		return -1
	
	return info['data']['uid']


def get_live_info(uids : List[int]) -> Dict[str, Dict[str, Any]]:
	'''
	批量查询直播间信息，传入参数为用户 uid （而非房间号）
	'''

	info = bili_api.get_status_info_by_uids(uids)

	if info['code'] != 0:
		return {'error_msg' : 'fail'}
	
	return info['data']


def generate_live_notice(info : Dict[str, Any]) -> str:
	'''
	不带封面信息
	'''

	return f'''\
直播标题：{info['title']}
地址：{get_room_url(info["room_id"])}
分区：{info['area']}'''