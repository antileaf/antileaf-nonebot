# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message
from nonebot.message import MessageSegment as ms

bot = nonebot.get_bot()

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