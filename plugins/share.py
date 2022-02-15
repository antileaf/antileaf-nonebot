# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

import json, re, time

bot = nonebot.get_bot()

@bot.on_message('group')
async def link_handle(session):
    prefixes = ['b23.tv/', 'www.zhihu.com/', 'www.bilibili.com/']

    text = session['raw_message']

    text = text.replace('\\/', '/')
    
    # await bot.send_group_msg(group_id = session.group_id, message = message.MessageSegment.text(text))

    for p in prefixes:
        for t in ['https://' + p, 'http://' + p]:
            if (text.startswith('[CQ:json') or text.startswith('[CQ:xml')) and t in text:
                i = text.find(t)
                url = ''
                while not text[i] in ['?', ',', ';', ' ']:
                    url += text[i]
                    i += 1
                
                await bot.send_group_msg(group_id = session.group_id, message = url)
                return