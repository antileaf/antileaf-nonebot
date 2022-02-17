# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin

import plugins.tools as tools
from plugins.tools import send_group_message, send_private_message, auto_reply
from plugins.tools import get_nickname, get_group_name


bot = nonebot.get_bot()

bot_author = 1094054222
bili_superusers = [1094054222, 780768723]

