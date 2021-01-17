# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

@on_command('echo', aliases = ('print'), only_to_me = False, permission = perm.GROUP)
async def report(session):
    if not 'text' in session.state:
        return

    await session.send(session.state['text'])
    

@report.args_parser
async def report_parser(session):
    s = session.current_arg_text.strip()

    if s:
        session.state['text'] = s