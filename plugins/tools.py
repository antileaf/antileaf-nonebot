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

async def auto_reply(session : CommandSession, s): # at must be true
    '''
    根据 session 自动回复，记得传 session
    '''

    if session.event.group_id:
        await send_group_message(session, s)
    else:
        await session.send(s)


async def get_nickname(user_id : int):
    info = await bot.get_stranger_info(user_id = user_id)

    return info['nickname']

async def get_group_card(group_id : int, user_id : int, subst : bool = False):
    info = await bot.get_group_member_info(group_id = group_id, user_id = user_id)

    s = info['card']
    if s:
        return s
    elif subst:
        s = info['nickname']

        return s if s else str(user_id)

async def get_group_name(group_id : int):
    info = await bot.get_group_info(group_id = group_id)

    return info['group_name']

def local_image(file_name : str):
    file_name = '../../../antileaf-nonebot/images/' + file_name
    # TODO: 这太逆天了，有空改成绝对路径

    return ms.image(file = file_name)