# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message

import aiocqhttp

bot = nonebot.get_bot()

@bot.on_message('group')
async def repeater(message):
    
    group_id = message.group_id
    user_id = message.user_id

    s = message['raw_message']
    if s.startswith('[CQ:xml,') and 'name=\"\"' in s and 'icon=\"\"' in s and 'action=\"\"' in s and 'appid=\"-1\"' in s:
        try:
            await bot.set_group_ban(group_id = group_id, user_id = user_id, duration = 30 * 60)
        except:
            pass
        await bot.send_group_msg(group_id = group_id, message = message.MessageSegment.at(user_id) + ' 请不要恶意使用xml消息')

@on_command('escape', only_to_me = False, permission = (perm.GROUP, perm.SUPERUSER))
async def manual_escape(session):
    if not 'content' in session.state:
        return

    s = aiocqhttp.message.unescape(session.state['content'])

    '''t = message.MessageSegment()
    t.type = 'xml'
    t.params = '''

    await session.send(session.state['content'])

@manual_escape.args_parser
async def manual_escape_parser(session):
    session.state['content'] = session.current_arg_text