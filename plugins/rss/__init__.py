# -*- coding: utf-8 -*-

import threading
import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin

import time, asyncio

import plugins.tools as tools
from plugins.tools import send_group_message, send_private_message, auto_reply
from plugins.tools import get_nickname, get_group_name

from .parser import Article, get_articles, generate_article_info, generate_blog_info
from .statistics import *
from .check_update import *

bot = nonebot.get_bot()

bot_author = 1094054222
rss_superusers = [1094054222, 780768723]

help_message = f'''\
RSS module of antileaf-nonebot
by AntiLeaf

注意：以下指令需要\"%rss\"前缀才可识别
注意：以下指令除\"作者\"\"订阅者\"\"最新\"外均需要在私聊中使用，在群聊中使用会视为群聊订阅

作者/authors/all：作者列表
订阅者/subscribers/list + <作者>：查询某位作者的订阅者列表
详情/detail + <作者>：查询某位作者的博客信息（地址、标题、副标题）
我的/my/mine/查询：查询你或者本群（取决于你在何处使用命令）的订阅列表
订阅/关注/sucsc/watch + <作者>：订阅某位作者
取消/取关/unsubsc/stop + <作者>：取消订阅某位作者
最新/动态/new/newest + <作者> [ + <数量>]：查询某位作者的最新文章，如果不给出数量则只显示最新一条

例：\"%rss 订阅 antileaf\" 表示订阅作者 antileaf\

如果您想加入或退出作者列表，请%反馈或者私聊联系绿
另外美观起见，在您加入作者列表前，请检查 RSS 是否返回文章摘要而非全文，否则可能出现显示错误

更多信息参见：https://github.com/AntiLeaf/antileaf-nonebot/tree/main/plugins/rss/doc.md
'''


async def send_notice(author : str, art : Article):
	users = query_users(author)
	groups = query_groups(author)

	msg = f'{author} 发表了一篇新文章！\n\n' + generate_article_info(art) \
		+ '\n\n此消息来自于 AntiLeaf-Bot 的 RSS 订阅功能，如不想再收到此通知，可以随时取消订阅\n\
如需获取帮助，请使用\"%help rss\"指令'

	for user_id in users:
		await send_private_message(user_id, '您订阅的 ' + msg)
	
	for group_id in groups:
		await bot.send_group_msg(group_id = group_id, message = msg)


@nonebot.scheduler.scheduled_job('interval', seconds = 5 * 60)
async def work():
	# await send_private_message(bot_author, 'starts work!')

	rss_tbl = get_rss_tbl()

	for author in rss_tbl:
		v = get_articles(rss_tbl[author])

		for art in v:
			if is_new(art.published):
				await send_notice(author, art) # 也许不需要 await
			# else:
			# 	await send_private_message(bot_author, str(art.published) + ' ' + str(last_checked))

	hell_its_about_time()
	
	# await send_private_message(bot_author, 'end work!')
	# TODO: 记录一条 log


# async def main_process(): # 定时检查
# 	while True:
# 		# await send_private_message(bot_author, '???')
# 		# print('Test\n')
# 		await work() # async
# 		await asyncio.sleep(5 * 60)


# started = True

# @on_command('start', permission = perm.SUPERUSER)
# async def start_working(session : CommandSession):
# 	global started

# 	if started:
# 		await auto_reply(session, '已经开始过了')
# 		return
	
# 	started = True
# 	await auto_reply(session, '已开始轮询')
# 	await main_process()


@on_plugin('loading')
async def you_will_never_fade_away(): # awake
	load_all()

	hell_its_about_time()
	# await work()

	# main_process()


async def rss_add_author(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if not user_id in rss_superusers:
		await auto_reply(session, '只有超级用户可以增删作者，如果想添加可以%反馈或者私聊绿')
		return

	author = session.state['author']

	if not author:
		await auto_reply(session, '作者名字呢？')
		return
	
	if check_author(author):
		await auto_reply(session, f'{author} 已在作者列表中')
		return
	
	if not 'link' in session.state:
		await auto_reply(session, '你地址呢？')
		return
	
	add_rss(author, session.state['link'])

	await auto_reply(session, f'添加成功！\n作者：{author}\tRSS 地址：{session.state["link"]}')


async def rss_del_author(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if not user_id in rss_superusers:
		await auto_reply(session, '只有超级用户可以增删作者，如果想添加可以%反馈或者私聊绿')
		return

	author = session.state['author']

	if not author:
		await auto_reply(session, '作者名字呢？')

	if not check_author(author):
		await auto_reply(f'作者 {author} 不存在')
		return
	
	del_rss(author)

	await auto_reply(session, f'已成功删除作者 {author}')


async def rss_user_subscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要订阅的作者')
		return

	if not check_author(author):
		await session.send(f'作者 {author} 不存在')
		return

	res = add_user(user_id, author)

	await session.send('订阅成功' if res else f'你已经订阅过作者 {author} 了')


async def rss_user_unsubscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要取消订阅的作者')
		return

	if not check_author(author):
		await session.send(f'作者 {author} 不存在')
		return
	
	res = del_user(user_id, author)

	await session.send('取消订阅成功' if res else f'你没有关注作者 {author}')
	

async def rss_group_subscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要订阅的作者')
		return

	if not user_id in rss_superusers:
		await send_group_message(session, '只有超级用户才能修改群订阅')
		return

	res = add_group(group_id, author)

	await send_group_message(session, '订阅成功' if res else f'本群已订阅过作者 {author}')


async def rss_group_unsubscribe(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要取消订阅的作者')
		return

	if not user_id in rss_superusers:
		await send_group_message(session, '只有超级用户才能修改群订阅')
		return
	
	if not check_author(author):
		await session.send(f'作者 {author} 不存在')
		return

	res = del_group(group_id, author)

	await send_group_message(session, '取消订阅成功' if res else f'本群没有订阅作者 {author}')


async def rss_get_list(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	rss_tbl = get_rss_tbl()

	if not rss_tbl:
		s = '目前还没有任何作者'
	else:
		s = '作者列表如下：'

		for author in rss_tbl:
			s += f'\n{author}\t{get_blog_url(author)}'
	
	await auto_reply(session, s)


async def rss_get_subscribers(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要查询的作者')
		return
	
	if not check_author(author):
		await auto_reply(session, f'作者 {author} 不存在')
		return
	
	users = query_users(author)
	groups = query_groups(author)

	if not users and not groups:
		s = '该作者还没有任何订阅者'

	else:
		s = f'作者 {author} 的订阅者如下：'

		if users:
			s += '\n用户：' + '，'.join([f'{await get_nickname(i)}({i})' for i in users])
		
		if groups:
			s += '\n群聊：' + '，'.join([f'{await get_group_name(i)}({i})' for i in groups])
	
	await auto_reply(session, s)


async def rss_my_subscribes(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if group_id:
		v = query_author_by_group(group_id)
	else:
		v = query_author_by_user(user_id)
	
	if not v:
		s = ('你' if not group_id else '本群') + '还没有订阅任何作者'
	
	else:
		s = ('你' if not group_id else '本群') + '订阅的作者如下：\n'
		
		s += '\n'.join([f'{o}\t{get_blog_url(o)}' for o in v])
	
	await auto_reply(session, s)	


async def rss_get_newest(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要查询的作者')
		return
	
	if not check_author(author):
		await auto_reply(session, f'作者 {author} 不存在')
		return
	
	# await auto_reply(session, '处理中……')

	v = get_articles(get_feed_url(author))

	if not v:
		s = f'作者 {author} 还没有发表过文章'
	
	else:
		cnt = min(min(len(v), 5), int(session.state['link'] if 'link' in session.state else 1))

		v = v[:cnt]

		s = f'作者 {author} 的最新文章如下：\n\n' + \
			'\n\n'.join([generate_article_info(art) for art in v])

		s += '\n\n（如需查看更多文章，请访问作者主页）'
	
	await auto_reply(session, s)


async def rss_get_detail(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	author = session.state['author']

	if not author:
		await auto_reply(session, '请输入你要查询的作者')
		return
	
	if not check_author(author):
		await auto_reply(session, f'作者 {author} 不存在')
		return
	
	s = f'作者 {author} 的博客信息如下：\n' + generate_blog_info(query_blog(author))

	await auto_reply(session, s)


async def rss_update_blog(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if not user_id in rss_superusers:
		await auto_reply(session, '只有超级用户可使用此功能，如果你想更新自己的博客信息，请联系绿')
		return

	author = session.state['author']

	if author:
		update_blog_info(author)
	else:
		update_all()
	
	await auto_reply(session, '更新成功')


@on_command('rss', aliases = ('RSS', 'Rss', '博客', 'blog', 'Blog'), only_to_me = False, permission = perm.EVERYBODY)
async def rss_work(session : CommandSession):
	group_id = session.event.group_id
	user_id = session.event.user_id

	if 'error' in session.state or not 'type' in session.state:
		await auto_reply(session, '指令有误，如需帮助请使用\"%rss help\"')
		return

	author = session.state['author']
	
	if author:
		pass
		# if not await check_author(author):
		# 	await session.send(f'作者 {author} 不存在')
		# 	return
	
	op = session.state['type']

	if op == '添加':
		await rss_add_author(session)
	elif op == '删除':
		await rss_del_author(session)
	elif op == '作者':
		await rss_get_list(session)
	elif op == '地址':
		await rss_get_detail(session)
	elif op == '订阅者':
		await rss_get_subscribers(session)
	elif op == '我的':
		await rss_my_subscribes(session)

	elif op == '订阅':
		if group_id:
			await rss_group_subscribe(session)
		else:
			await rss_user_subscribe(session)

	elif op == '取消':
		if group_id:
			await rss_group_unsubscribe(session)
		else:
			await rss_user_unsubscribe(session)

	elif op == '最新':
		await rss_get_newest(session)
	elif op == '帮助':
		await auto_reply(session, help_message)
	
	elif op == '更新':
		await rss_update_blog(session)

	elif op == '调试':
		v = get_articles(author)

		if not v:
			s = '没有找到文章'
		
		else:
			art = v[0]

			s = f'最新文章如下：\n\n' + generate_article_info(art)

		# print('test')
		
		# await auto_reply(session, '你妹的')

		# print('s = ', s)

		await auto_reply(session, s)
	
	else:
		await auto_reply(session, '指令有误，如需帮助请使用\"%rss help\"')


alias_table = [
	('添加', ('add', 'create', '新增', '增加')),
	('删除', ('del', 'delete', 'remove')),
	('作者', ('authors', '作者列表', 'all', 'show')),
	('地址', ('detail', '详细', '详情', 'url', 'addr', 'address')),
	('订阅者', ('subscribers', '查询订阅者', '所有订阅', '关注者', 'list')),
	('我的', ('my', 'mine', '我的订阅', '订阅列表', '查询', '我的关注')),
	('订阅', ('关注', 'subscribe', 'subsc', '添加订阅', '添加关注', 'watch')),
	('取消', ('取关', 'unsubscribe', 'unsubsc', '取消订阅', '取消关注', 'stop')),
	('最新', ('newest', 'new', 'recent', '新', '最新动态', '最新文章', '近期文章', '查询动态')),
	('帮助', ('help')),
	('更新', ('update', 'refresh', '刷新')),
	('调试', ('debug', 'direct'))
]

@rss_work.args_parser
async def rss_work_parser(session : CommandSession):
	v = session.current_arg_text.split()

	if len(v) < 1:
		session.state['error'] = True
	
	else:
		s = v[0]

		for o in alias_table:
			if s == o[0] or s in o[1]:
				session.state['type'] = o[0]
				break

		if len(v) >= 2:
			session.state['author'] = v[1]

			if len(v) >= 3:
				session.state['link'] = v[2]

		else:
			session.state['author'] = ''