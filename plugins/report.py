# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from plugins.tools import send_group_message, send_private_message

bot = nonebot.get_bot()

@on_command('report', aliases = ('反馈', 'issue'), only_to_me = False, permission = perm.GROUP)
async def report(session):
    user_id = int(session.event['user_id'])
    if 'text' in session.state:
        s = '收到来自%d的反馈： ' % user_id + session.state['text']
        await bot.send_private_msg(user_id = 1094054222, message = message.MessageSegment.text(s))
        t = '已成功反馈，感谢支持！'
    else:
        t = '用法： 反馈 + 你要反馈的内容'
    t = message.MessageSegment.text(t)

    if session.event.group_id:
        t = message.MessageSegment.at(user_id) + ' ' + t
    
    await session.send(t)
    

@report.args_parser
async def report_parser(session):
    s = session.current_arg_text.strip()

    if s:
        session.state['text'] = s