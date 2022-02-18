# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

from nonebot.plugin import on_plugin

# from plugins.toolkit import send_private_message

from .tt import *



bot = nonebot.get_bot()


@on_plugin('unloaded')
async def unloaded_test():
    print('卸载测试')
    # 试过了，不行的