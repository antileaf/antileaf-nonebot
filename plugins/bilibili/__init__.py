# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin

import plugins.toolkit as toolkit
from plugins.toolkit.message import send_group_message, send_private_message, auto_reply
from plugins.toolkit.cq import get_nickname, get_group_name


bot = nonebot.get_bot()

bot_author = 1094054222
bili_superusers = [1094054222, 780768723, 1048275447, 759997057]
# 我 KS M晓 Panda