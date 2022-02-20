# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin

from typing import *

import toolkit
from toolkit.message import send_group_message, send_private_message, auto_reply

from . import parser


bot = nonebot.get_bot()

bot_author = 1094054222
bili_superusers = [1094054222, 780768723, 1048275447, 759997057]
# 我 KS M晓 Panda

help_message = f'''\
bilibili_live module of antileaf-nonebot
by AntiLeaf

注意：以下指令需要\"%live\"前缀才可识别
注意：以下指令除\"all\"\"订阅者\"\"详情\"外均需要在私聊中使用，在群聊中使用会视为群聊订阅

all：主播列表
订阅者/subscribers/list + <主播>：查询某位主播的订阅者列表
详情/detail + <主播>：查询某位主播的直播间信息，如果已开播还会显示标题、分区、封面等信息
我的/my/mine/查询：查询你或者本群（取决于你在何处使用命令）的订阅列表
订阅/关注/subsc(ribe)/watch + <主播>：订阅某位主播
取消/取关/unsubsc(ribe)/stop + <主播>：取消订阅某位主播

例：\"%live subsc antileaf\" 表示订阅主播 antileaf\

如果您想增删主播，请与绿联系
'''

subsc = toolkit.subscribe.Subscribe('bilibili_live')

'''
details:

room_id : 房间号
uid : 主播uid
area : 分区
cover : 封面url
title : 标题
live_status : 0未开播，1直播中，2轮播中
'''

def update_all() -> List[str]:
	'''
	刷新所有直播间状态，返回新开播的主播名称列表
	'''

	authors = list(subsc.get_authors())

	datas = parser.get_live_info([subsc.get_detail(author, 'uid') for author in authors])

	new_lives : List[str] = []

	for author in authors:
		uid = subsc.get_detail(author, 'uid')

		info = datas[str(uid)]

		room_id = info['room_id']
		area = info['area_v2_name']
		cover = info['cover_from_user']
		title = info['title']
		live_status = info['live_status']

		if subsc.get_detail(author, 'live_status') != 1 and live_status == 1:
			new_lives.append(author)
		
		subsc.set_detail(author, {'uid' : uid, 'room_id' : room_id, 'area' : area, 'cover' : cover, 'title' : title, 'live_status' : live_status})
		
	return new_lives


@on_plugin('loading')
async def awake():
	subsc.load()

	update_all()


async def send_notice(author : str):
	users = subsc.get_subscribed_users(author)
	groups = subsc.get_subscribed_groups(author)

	msg = f'主播 {author} 开播了！\n\n' + parser.generate_live_notice(subsc.get_details(author)) \
		+ ms.image(subsc.get_detail(author, 'cover')) + f'\n\n此消息来自于 Bilibili 直播订阅功能，如不想再收到此通知，可以随时取消订阅\n如需获取帮助，请使用\"%live help\"指令'

	for user_id in users:
		await toolkit.message.send_private_message(user_id, '您关注的' + msg)
	
	for group_id in groups:
		await bot.send_group_msg(group_id = group_id, message = msg)
	

@nonebot.scheduler.scheduled_job('interval', seconds = 2 * 60)
async def regular_work():
	lives = update_all()

	for author in lives:
		await send_notice(author)


def get_live_info(author : str) -> str:
	status = subsc.get_detail(author, 'live_status')

	if status != 1:
		msg = f'当前主播 {author} 未开播，直播间信息如下：\n'
	else:
		msg = f'当前主播 {author} 已开播，直播间信息如下：\n'
		
	msg += parser.generate_live_notice(subsc.get_details(author)) + ms.image(subsc.get_detail(author, 'cover'))

	return msg


async def live_add_author(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']
	room_id = session.state['room_id']

	uid = parser.get_room_uid(room_id)

	if uid < 0:
		await toolkit.message.auto_reply(session, f'直播间 {room_id} 不存在，请重试')
		return
	
	subsc.add_author(author)
	subsc.update_detail(author, 'uid', uid)

	update_all()
	
	await toolkit.message.auto_reply(session, f'已成功添加主播 {author}！\n' + get_live_info(author))


async def live_del_author(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']
	
	subsc.del_author(author)

	await toolkit.message.auto_reply(session, f'已成功删除主播 {author}')


async def live_get_author_list(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if not subsc.any_author():
		await toolkit.message.auto_reply(session, '当前还没有添加任何主播')
		return

	msg = '已添加的主播列表如下：'

	for author in subsc.get_authors():
		msg += f'\n{author} {parser.get_room_url(subsc.get_detail(author, "room_id"))}'
	
	await toolkit.message.auto_reply(session, msg)


async def live_get_subscribers(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	users = subsc.get_subscribed_users(author)
	groups = subsc.get_subscribed_groups(author)

	if not users and not groups:
		msg = f'主播 {author} 还没有任何订阅者'

	else:
		msg = f'主播 {author} 的订阅者如下：'

		if users:
			msg += '\n用户：' + '，'.join([f'{await toolkit.cq.get_nickname(i)}({i})' for i in users])
		
		if groups:
			msg += '\n群聊：' + '，'.join([f'{await toolkit.cq.get_group_name(i)}({i})' for i in groups])
	
	await toolkit.message.auto_reply(session, msg)


async def live_my_subscribes(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id
	
	if group_id:
		v = subsc.get_group_subscribes(group_id)
	else:
		v = subsc.get_user_subscribes(user_id)
	
	if not v:
		msg = ('你' if not group_id else '本群') + '还没有订阅任何主播'
	
	else:
		msg = ('你' if not group_id else '本群') + '订阅的主播如下：\n'
		
		msg += '\n'.join([f'{author} {parser.get_room_url(subsc.get_detail(author, "room_id"))}' for author in v])
	
	await toolkit.message.auto_reply(session, msg)


async def live_get_detail(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	await toolkit.message.auto_reply(session, get_live_info(author))


async def live_subscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if group_id:
		if group_id in subsc.get_subscribed_groups(author):
			msg = f'本群已订阅主播 {author}'

		else:
			subsc.group_subscribe(group_id, author)
			msg = f'已成功为本群订阅主播 {author}'

	else:
		
		if user_id in subsc.get_subscribed_users(author):
			msg = f'你已经订阅过主播 {author} 了'

		else:
			subsc.user_subscribe(user_id, author)
			msg = f'已成功订阅主播 {author}'
	
	await auto_reply(session, msg)


async def live_unsubscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if group_id:
		if not group_id in subsc.get_subscribed_groups(author):
			msg = f'本群还没有订阅主播 {author}'

		else:
			subsc.group_unsubscribe(group_id, author)
			msg = f'已成功为本群取消订阅主播 {author}'

	else:
		
		if not user_id in subsc.get_subscribed_users(author):
			msg = f'你还没有订阅主播 {author}'

		else:
			subsc.user_unsubscribe(user_id, author)
			msg = f'已成功取消订阅主播 {author}'
	
	await auto_reply(session, msg)


async def live_debug(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id
	
	room_id = session.state['room_id']

	uid = parser.get_room_uid(room_id)

	if uid < 0:
		await toolkit.message.auto_reply(session, f'直播间 {room_id} 不存在')
		return
	
	msg = f'直播间 {room_id} 对应的 uid 为：{uid}\n'

	liveinfo = parser.get_live_info([uid])
	
	# if liveinfo['code']:
	# 	await auto_reply('访问出错')
	# 	return

	info = liveinfo[str(uid)]

	details = {'uid' : uid, 'room_id' : room_id, 'area' : info['area_v2_name'], 'cover' : info['cover_from_user'], 'title' : info['title'], 'live_status' : info['live_status']}

	status = details['live_status']

	if status != 1:
		msg += f'当前直播间 {room_id} 未开播'
	else:
		msg += f'当前直播间 {room_id} 已开播，直播间信息如下：\n' + parser.generate_live_notice(details) + ms.image(details['cover'])
	
	await toolkit.message.auto_reply(session, msg)


async def live_get_help_message(session : CommandSession):
	await auto_reply(session, help_message)


alias_table : Dict[str, Tuple[str]] = {
	'添加' : ('add', 'create', '新增', '增加'),
	'删除' : ('del', 'delete', 'remove'),
	'作者' : ('authors', '作者列表', 'all', 'show'),
	'详情' : ('detail', '详细', '查询', '查房', 'query', 'url', 'addr', 'address'),
	'订阅者' : ('subscribers', '查询订阅者', '所有订阅', '关注者', 'list'),
	'我的' : ('my', 'mine', '我的订阅', '订阅列表', '我的关注'),
	'订阅' : ('关注', 'subscribe', 'subsc', '添加订阅', '添加关注', 'watch'),
	'取消' : ('取关', 'unsubscribe', 'unsubsc', '取消订阅', '取消关注', 'stop'),
	'帮助' : ('help'),
	'调试' : ('debug', 'direct', 'test')
}

functions_table : Dict[str, Any] = {
	'添加' : live_add_author,
	'删除' : live_del_author,
	'作者' : live_get_author_list,
	'详情' : live_get_detail,
	'订阅者' : live_get_subscribers,
	'我的' : live_my_subscribes,
	'订阅' : live_subscribe,
	'取消' : live_unsubscribe,
	'帮助' : live_get_help_message,
	'调试' : live_debug
}

@on_command('live', aliases = ('Live', '直播'), only_to_me = False, permission = perm.EVERYBODY)
async def bilibili_live_main(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if 'error' in session.state or not 'type' in session.state:
		await auto_reply(session, '指令有误，如需帮助请使用\"%live help\"')
		return

	if session.state['type'] in ('添加', '删除', '详情', '订阅者', '订阅', '取消', '调试'):
		if not 'author' in session.state or not session.state['author']:
			await auto_reply(session, '指令有误，如需帮助请使用\"%live help\"')
			return
		
		if session.state['type'] == '调试':
			session.state['room_id'] = int(session.state['author'])
			# del session.state['author']
		
		author = session.state['author'] # if 'author' in session.state else ''
		
		res = subsc.check_author(author)
		
		if session.state['type'] in ('添加', '删除'):
			if not user_id in bili_superusers:
				await auto_reply(session, '只有超级用户可以增删主播，如有需求请联系绿')
				return
		
		if session.state['type'] in ('删除', '详情', '订阅者', '订阅', '取消'):
			if not res:
				await auto_reply(session, f'未找到主播 {author}')
				return
			
			if session.state['type'] in ('订阅', '取消'):
				if group_id and not user_id in bili_superusers:
					await auto_reply(session, '只有超级用户可以修改群订阅，如有需求请联系绿')
					return
		
		elif session.state['type'] == '添加':
			if res:
				await auto_reply(session, f'主播 {author} 已存在')
				return

			elif not 'room_id' in session.state:
				await auto_reply(session, f'请输入房间号')
				return
			
			elif not session.state['room_id']:
				await auto_reply(session, f'房间号格式有误，请重新输入')
				return
	
	await functions_table[session.state['type']](session)


@bilibili_live_main.args_parser
async def bilibili_live_main_parser(session : CommandSession):
	v = session.current_arg_text.split()

	if len(v) < 1:
		session.state['error'] = True
	
	else:
		s = v[0]
		
		for t in alias_table:
			if s == t or s in alias_table[t]:
				session.state['type'] = t
				break

		if 'type' in session.state:
			if len(v) >= 2:
				session.state['author'] = v[1]

				if len(v) >= 3:
					try:
						session.state['room_id'] = int(v[2])
					except:
						session.state['room_id'] = 0

		else:
			session.state['author'] = ''