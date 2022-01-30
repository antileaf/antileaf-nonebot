# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

import random, ast

bot = nonebot.get_bot()

@nonebot.on_request('friend')
async def auto_add_friend(session: nonebot.RequestSession):
    await session.approve()

# 以下是对话内容

@on_command('爬', aliases = ("爬", "给爷爬", "爪巴", "给爷爪巴"), only_to_me = False, permission = perm.GROUP)
async def pa(session):
    await session.send(random.choice(["你怎么能让可爱的我爬呢，你坏坏QAQ"]))

@on_command('绿', aliases = ("AntiLeaf", "antileaf", "绿鸽鸽", "绿哥哥", '绿'), only_to_me = False, permission = perm.GROUP)
async def lv(session):
    await session.send(random.choice(["绿鸽鸽好坏，最讨厌他了！QAQ"]))

@on_command('呐', aliases = ("呐呐", "呐呐呐", "呐 呐", "呐 呐 呐"), only_to_me = False, permission = perm.GROUP)
async def na(session):
    await session.send(random.choice(["自 动 声 呐 系 统", "巧了我也是二次元[CQ:face,id=109]"]))

@on_command('bot', aliases = ("Bot", "bot", "BOT", "⑨"), only_to_me = False, permission = perm.GROUP)
async def bottt(session):
    await session.send(random.choice(["这里是绿鸽鸽的可爱Bot~"]))

@on_command('复读', aliases = ("复读", "复读机", "复读姬"), only_to_me = False, permission = perm.GROUP)
async def fudu(session):
    await session.send(random.choice(["小火汁，原来你也是复读机？"]))

# 对话内容到此结束

# 以下是直播查询

live = [
    (("AntiLeaf", "绿鸽鸽", "绿哥哥", "antileaf", "反叶子", "反对叶子", "绿叶", "绿"), "live.bilibili.com/21493332" ),
    (("KS", "ks", "KsKun", "Kskun", "kskun"), "https://ksmeow.moe/live"),
    (("M晓", "m晓", "咕咕晓"), "live.bilibili.com/30014"),
    (("Megumin", "megumin", "蘑菇民", "蘑菇米", "mgm"), "live.bilibili.com/14866481"),
    (("北啻", "北帝口"), "live.bilibili.com/152745"),
    (("Ringoer", "ringoer"), "live.bilibili.com/706938"),
    (("Kamigen", "kamigen"), "live.bilibili.com/9508073"),
    (("Pantw", "pantw", "PTW", "Ptw", "ptw", "群主", "葡萄味"), "live.bilibili.com/4299357"),
    (("MegaOwler", "Megaowler", "megaowler", "百万猫头鹰"), "live.bilibili.com/917033"),
    (("Slanterns", "SLanterns", "slanterns", "slantern", "Slantern"), "live.bilibili.com/627355"),
    (("Democracy", "democracy"), "live.bilibili.com/4620643"),
    (("icy", "Icy", "绿泡泡", "ICY"), "live.bilibili.com/8815853")
]

@on_command('直播', aliases = ('查房', '直播查询'), only_to_me = False, permission = perm.GROUP)
async def live_number(session):
    t = ''
    tmp = ''

    if 'name' in session.state:
        for (first, last) in live:
            tmp += str(first) + '\n'
            if session.state['name'] in first:
                t = last
                break
        if not t:
            t = '没有找到' + session.state['name'] + '的直播间…\n换个名字试试吧'
        else:
            t = session.state['name'] + '的直播间： ' + t
        
    if not t:
        t = '输入格式有误！\n用法： 直播/查房/直播查询 + 你要查询的群友常用id'

    if session.event.group_id:
        t = message.MessageSegment.at(int(session.event['user_id'])) + ' ' + t

    await session.send(t)

@live_number.args_parser
async def live_number_parser(session : CommandSession):
    a = session.current_arg_text.split()

    if len(a) == 1:
        session.state['name'] = a[0]

# 直播查询到此结束

evaluate_on = False

@on_command('open', aliases = ('enable'), permission = perm.SUPERUSER)
async def open(session):
    global evaluate_on
    evaluate_on = True
    await session.send('Python功能已打开')

@on_command('close', aliases = ('disable'), permission = perm.SUPERUSER)
async def close(session):
    global evaluate_on
    evaluate_on = False
    await session.send('Python功能已关闭')

@on_command('eval', aliases = ('evaluate'), only_to_me = False, permission = perm.GROUP)
async def evaluate(session):
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id

    if not evaluate_on:
        if group_id:
            await session.send(message.MessageSegment.at(user_id) + ' Python功能未开启')
        else:
            await session.send('Python功能未开启')
        
        return

    s = ''

    if 'command' in session.state:
        try:
            s = str(eval(session.state['command']))
        except Exception:
            s = '发生错误'
    
    else:
        s = '用法：eval + 想求值的表达式或想运行的语句'
    
    if group_id:
        await session.send(message.MessageSegment.at(user_id) + ' ' + s)
    else:
        await session.send(s)

@evaluate.args_parser
async def evaluate_parser(session):
    session.state['command'] = ' '.join(session.current_arg_text.split())