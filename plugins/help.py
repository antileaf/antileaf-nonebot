# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

help_info = [
    (('all'), '可用帮助：帮助 直播 反馈 占卜 uno'),
    (('帮助', 'help'), '帮助\n功能：获取全部或者某个指令的用法\n用法：帮助/help 或 帮助/help + 你要查询的指令'),
    (('直播', '查房', '直播查询'), '直播查询\n功能：获取群友的直播间地址\n用法：直播/查房/直播查询 + 你要查询的群友常用id'),
    (('反馈', 'report'), '反馈\n功能：向绿反馈一些信息\n用法：反馈 + 你要反馈的内容'),
    (('占卜', 'tarot', '塔罗牌', '单张塔罗牌'), '塔罗牌\n功能：抽取单张塔罗牌，借以占卜每日运势\n注：同一天的结果是相同的，不必试图重抽\n用法：占卜/塔罗牌/单张塔罗牌/tarot'),
    (('uno', 'UNO', 'Uno', '打牌'), 'https://github.com/AntiLeaf/antileaf-nonebot/blob/main/uno_help.md')
]

@on_command('help', aliases = ('帮助', 'Help'), only_to_me = False, permission = perm.GROUP)
async def help(session : CommandSession):
    if 'name' in session.state:
        s = ''
        for o in help_info:
            if session.state['name'] in o[0]:
                s = o[1]
                break
        if not s:
            s = '未找到对应指令，请重试'
    else:
        s = '用法：帮助/help 或 帮助/help + 你要查询的指令'

    if session.event.group_id:
        s = message.MessageSegment.at(int(session.event['user_id'])) + ' ' + s

    await session.send(s)

@help.args_parser
async def help_parser(session):
    s = session.current_arg_text.strip()

    if not s:
        session.state['name'] = 'all'
    if len(s.split()) == 1:
        session.state['name'] = s