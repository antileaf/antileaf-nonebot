# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message
from nonebot.message import MessageSegment as ms

bot = nonebot.get_bot()

async def send_group_message(session : CommandSession, s, at = True):
    if at:
        s = ms.at(session.event.user_id) + ' ' + s
    await session.send(s)


async def send_private_message(user_id, message, noexcept = True):
    try:
        await bot.send_private_msg(user_id = user_id, message = message)
    except:
        if not noexcept:
            raise 'Failed to send private message'

async def auto_reply(session : CommandSession, s): # at must be true
    '''
    根据 session 自动回复，记得传 session
    '''

    if session.event.group_id:
        await send_group_message(session, s)
    else:
        await session.send(s)