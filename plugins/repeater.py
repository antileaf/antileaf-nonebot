# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

bot = nonebot.get_bot()

d = dict()

@bot.on_message
async def repeater(message):
    if not message.group_id:
        return
    
    group_id = message.group_id
    s = message['raw_message']
    if not group_id in d:
        d[group_id] = ['', 0]
    
    if s == d[group_id][0]:
        d[group_id][1] += 1
        if d[group_id][1] == 3:
            await bot.send_group_msg(group_id = group_id, message = s)
            d.pop(group_id)
    
    else:
        d[group_id] = [s, 1]