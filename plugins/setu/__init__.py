# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin

import toolkit
from toolkit.message import send_group_message, send_private_message, auto_reply

import datetime
import requests


last = dict()

@on_command('涩图', aliases = ('setu', '图', '色图'), only_to_me = False, permission = perm.EVERYBODY)
async def setu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if user_id in last:
        if last[user_id] + datetime.timedelta(seconds = 30) > datetime.datetime.now():
            await auto_reply(session, '30 秒内只能看一张图哦…')
            return
    
    last[user_id] = datetime.datetime.now()

    s = ms.image(file = 'https://1mg.obfs.dev/', cache = False)

    await session.send(s)