# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message
from nonebot.message import MessageSegment as ms


def local_image(file_name : str):
    file_name = '/home/ubuntu/antileaf-nonebot/images/' + file_name

    return ms.image(file = 'file://' + file_name)