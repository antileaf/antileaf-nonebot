# -*- coding: utf-8 -*-  
import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message
from nonebot.message import MessageSegment as ms

bot = nonebot.get_bot()

groups = [
	# [1042285895, 1150908622]
]

# forward_flag = False

# @on_command('关闭转发', only_to_me = false, permission = perm.SUPERUSER)
# async def disable_forward(session):
# 	forward_flag = False

# 	await session.send('已关闭转发')

@bot.on_message('group')
async def forward(message):
	if not message.group_id:
		return

	group_id = message.group_id
	user_id = message.user_id
	s = message['raw_message']
	
	flag = False

	for group in groups:
		if group_id in group:
			flag = True
			break
	
	if not flag:
		return

	if user_id == 80000000:
		new_msg = '匿名用户：' + s

	else:
		info = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
		name = info['card']

		if name == '':
			name = info['nickname']

		new_msg = name + '(%d)' % user_id + '：' + s
	
	for group in groups:
		if group_id in group:
			for g in group:
				if g != group_id:
					await bot.send_group_msg(group_id = g, message = new_msg)