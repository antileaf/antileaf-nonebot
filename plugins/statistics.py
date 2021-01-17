# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

import os, datetime

bot = nonebot.get_bot()

global_table = dict() # global_table[group_id] = table   table[word][user_id] = (count, date)

directory = 'stat'

# groups_file = directory + '/groups.txt'

def get_date():
    return (datetime.date.today() - datetime.date(2000, 1, 1)).days

async def save_table():
    # global global_table

    for group_id in global_table:
        table = global_table[group_id]
        path = directory + '/' + str(group_id)

        for word in table:
            try:
                f = open(path + '/' + word + '.txt', 'wt')
            except:
                os.system('cd ' + directory + ' & mkdir ' + str(group_id))
                f = open(path + '/' + word + '.txt', 'wt')
            
            for user_id in table[word]:
                f.write(str(user_id) + ' ' + str(table[word][user_id][0]) + ' ' + str(table[word][user_id][1]) + '\n')
            
            f.close()
            
async def read_table():
    global global_table

    global_table = dict()

    groups = os.listdir(directory)
    for g in groups:
        if os.path.isdir(directory + '/' + g):
            group_id = int(g)
            global_table[group_id] = dict()
            table = global_table[group_id]
            path = directory + '/' + g

            words = os.listdir(path)
            for vv in words:
                if vv.endswith('.txt') and os.path.isfile(path + '/' + vv):
                    try:
                        f = open(path + '/' + vv, 'rt')
                    except:
                        continue

                    w = vv[:-4]

                    table[w] = dict()
                    for s in f.readlines():
                        if s:
                            user_id, count, date = map(int, s.split())
                            table[w][user_id] = (count, date)
                    
                    f.close()

async def check(group_id, word, user_id, date):
    global global_table

    if not group_id in global_table:
        global_table[group_id] = dict()
    
    if not word in global_table[group_id]:
        global_table[group_id][word] = dict()

    if not user_id in global_table[group_id][word]:
        global_table[group_id][word][user_id] = (0, date)

    if global_table[group_id][word][user_id][1] != date:
        global_table[group_id][word][user_id] = (0, date)


@on_command('统计添加', aliases = ('添加', '添加词语', 'add'), only_to_me = False, permission = perm.GROUP)
async def add_word(session):
    global global_table

    if not global_table:
        await read_table()
    
    group_id = session.event.group_id
    if not group_id:
        return

    user_id = session.event.user_id
    if user_id != 1094054222:
        await session.send(message.MessageSegment.at(user_id) + ' 只有绿可以使用此功能')
        return

    if not 'word' in session.state:
        await session.send(message.MessageSegment.at(user_id) + ' 用法：统计添加/add + 你要添加的词语')
        return

    w = session.state['word']

    if not group_id in global_table:
        global_table[group_id] = dict()

    table = global_table[group_id]
    if w in table:
        await session.send(message.MessageSegment.at(user_id) + ' 词语已存在')
        return

    table[w] = dict()
    await save_table()
    await session.send(message.MessageSegment.at(user_id) + ' 添加成功')

@add_word.args_parser
async def add_word_parser(session):
    args = session.current_arg_text.split()
    if len(args) == 1:
        session.state['word'] = args[0]


@on_command('统计删除', aliases = ('删除', '删除词语', 'del'), only_to_me = False, permission = perm.GROUP)
async def del_word(session):
    global global_table

    if not global_table:
        await read_table()
    
    group_id = session.event.group_id
    if not group_id:
        return

    user_id = session.event.user_id
    if user_id != 1094054222:
        await session.send(message.MessageSegment.at(user_id) + ' 只有绿可以使用此功能')
        return

    if not 'word' in session.state:
        await session.send(message.MessageSegment.at(user_id) + ' 用法：统计删除/del + 你要删除的词语')
        return

    w = session.state['word']

    if not group_id in global_table or not w in global_table[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 词语不存在')
        return
        
    global_table.pop(w)
    await save_table()
    await session.send(message.MessageSegment.at(user_id) + ' 删除成功')

@del_word.args_parser
async def del_word_parser(session):
    args = session.current_arg_text.split()
    if len(args) == 1:
        session.state['word'] = args[0]

@on_command('统计列表', aliases = ('列表', 'list'), only_to_me = False, permission = perm.GROUP)
async def get_list(session):
    global global_table

    if not global_table:
        await read_table()

    group_id = session.event.group_id
    if not group_id:
        return

    user_id = session.event.user_id

    if not group_id in global_table:
        await session.send(message.MessageSegment.at(user_id) + ' 本群未启用词语统计功能')
        return

    s = '本群统计词语列表：'
    for w in global_table[group_id]:
        s = s + '\n' + w
    
    await session.send(message.MessageSegment.at(user_id) + ' ' + s)

@on_command('统计排行', aliases = ('排行'), only_to_me = False, permission = perm.GROUP)
async def rank_list(session):
    global global_table

    if not global_table:
        await read_table()

    group_id = session.event.group_id
    if not group_id:
        return

    user_id = session.event.user_id

    if not 'word' in session.state:
        await session.send(message.MessageSegment.at(user_id) + ' 用法：统计排行 + 你想查询的词语')
        return
    
    w = session.state['word']

    if not group_id in global_table:
        await session.send(message.MessageSegment.at(user_id) + ' 本群未启用词语统计功能')
        return
    
    if not w in global_table[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 本群未启用对\"' + w + '\"的统计')
        return

    v = []
    date = get_date()
    for u in global_table[group_id][w]:
        check(group_id, w, u, date)
        if global_table[group_id][w][u][0]:
            v.append((u, global_table[group_id][w][u][0]))
    
    if not v:
        await session.send(message.MessageSegment.at(user_id) + ' 本群今日暂无人说过\"' + w + '\"')
        return

    v.sort(key = lambda x : -x[1])

    nick = dict()
    for o in v:
        nick[o[0]] = str(o[0])
    ddz_mmr_file = 'temp/mmr.txt'
    f = open(ddz_mmr_file, 'rt')
    for s in f.readlines():
        if s:
            u, nk = s.split()[:2]
            nick[int(u)] = nk

    s = '本群今日\"' + w + '\"发言频率排行：'
    for o in v:
        s = s + '\n' + str(v.index(o) + 1) + '. ' + nick[o[0]] + '(' + str(o[0]) + '): ' + str(o[1]) + '次'
    
    await session.send(message.MessageSegment.at(user_id) + ' ' + s)

@rank_list.args_parser
async def rank_list_parser(session):
    args = session.current_arg_text.split()
    if len(args) == 1:
        session.state['word'] = args[0]


@bot.on_message
async def counting(message):
    global global_table

    if not global_table:
        await read_table()
    
    group_id = message.group_id
    if not group_id:
        return

    if not group_id in global_table:
        return

    s = message['raw_message']
    if s in global_table[group_id]:
        user_id = message.user_id
        date = get_date()
        await check(group_id, s, user_id, date)
        global_table[group_id][s][user_id] = (global_table[group_id][s][user_id][0] + 1, date)
        await save_table()