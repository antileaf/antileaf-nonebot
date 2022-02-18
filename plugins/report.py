# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

import toolkit
from toolkit.message import send_group_message, send_private_message

bot = nonebot.get_bot()

@on_command('report', aliases = ('反馈', 'issue'), only_to_me = False, permission = perm.EVERYBODY)
async def report(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if 'text' in session.state:

        card, nick, group = '', '', ''

        if group_id:
            card = await toolkit.cq.get_group_card(group_id, user_id)
            group = await toolkit.cq.get_group_name(group_id)
        
        nick = await toolkit.cq.get_nickname(user_id)

        s = '收到 ' + nick

        if card:
            s = s + '(%s, %d)' % (card, user_id)
        else:
            s = s + '(%d)' % user_id
        
        if group_id:
            s = s + ' 在群聊 ' + group + '(%d)' % group_id
 
        s = s + ' 的反馈：\n' + session.state['text']
        await send_private_message(1094054222, s)

        t = '已成功反馈，感谢支持！'

    else:
        t = '用法： 反馈 + 你要反馈的内容'

    if group_id:
        await send_group_message(session, t)
    else:
        await send_private_message(user_id, t)
    

@report.args_parser
async def report_parser(session):
    s = session.current_arg_text.strip()

    if s:
        session.state['text'] = s