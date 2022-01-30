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


async def send_private_message(user_id, s, noexcept = True):
    try:
        await bot.send_private_msg(user_id = user_id, message = s)
    except:
        if not noexcept:
            raise 'Failed to send private message'


def get_nickname(user_id : int):
    pass