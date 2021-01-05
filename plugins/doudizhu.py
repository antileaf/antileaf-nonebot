# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

import random

bot = nonebot.get_bot()

# 没有card类，用一个字符串取代之
# 方便起见，写一个类用于保存一手牌

def completed(s):
    t = ''
    for c in s:
        t += c
        if c == '1':
            t += '0'
    return t

def simplified(s):
    t = ''
    for i in range(len(s)):
        if i:
            if s[i] == '王' and (s[i - 1] == '大' or s[i - 1] == '小'):
                continue
            if s[i] == '0':
                if s[i - 1] == '1':
                    continue
                else:
                    return 'error'
            elif s[i] == '1':
                if i == len(s) - 1 or s[i + 1] != '0':
                    return 'error'

        c = s[i]
        if not c in '34567891JQKA2鬼王小大':
            return 'error'
        
        if c == '小':
            t += '鬼'
        elif c == '大':
            t += '王'
        else:
            t += c
        
    return t

def compare(a, b): # a < b
    if b == '王':
        return True
    if a == '王':
        return False
    if b == '鬼':
        return True
    if a == '鬼':
        return False
    
    s = '34567891JQKA2'
    return s.index(a) < s.index(b)

class Combination:
    def __init__(self, major : str, minor : str, typ : str):
        self.major = major
        self.minor = minor # 次要牌不参与比较大小，因此原样存储
        self.type = typ
        '''
        single, double, triple, triple1, triple2, 单张，对子，三张，三带一，三带二
        quadruple, quadruple2, 炸弹，四带二
        serial, 2serial, 3serial, 3serial1, 3serial2, 顺子，连对，飞机，飞机带一张，飞机带两张
        rocket 火箭
        '''

    def __str__(self):
        if self.type == 'single':
            return self.major
        elif self.type == 'double':
            return self.major * 2
        elif self.type == 'triple' or self.type == 'triple1' or self.type == 'triple2':
            return self.major * 3 + self.minor
        elif self.type == 'quadruple' or self.type == 'quadruple2':
            return self.major * 4 + self.minor
        elif self.type == 'serial':
            return self.major
        elif self.type == '2serial':
            return ''.join([c * 2 for c in self.major])
        elif self.type == '3serial' or self.type == '3serial1' or self.type == '3serial2':
            return ''.join([c * 3 for c in self.major]) + self.minor
        elif self.type == 'rocket':
            return self.major
    
    def check(self, other): # 判断other能否大过self
        if self.type == 'rocket':
            return 'smaller'

        if self.type != other.type:
            if other.type == 'quadruple' or other.type == 'rocket':
                return 'bigger'
            return 'different type'
        
        if compare(self.major[0], other.major[0]):
            return 'bigger'
        else:
            return 'smaller'



def handle(s : str): # 返回处理好的一手牌，或者'error'
    s = list(s)
    s.sort(key = lambda x : '34567891JQKA2鬼王'.find(x))
    s = ''.join(s)

    if len(s) == 1:
        return Combination(s, '', 'single')

    elif len(s) == 2:
        if s[0] == s[1]:
            return Combination(s[0], '', 'double')
        elif s[0] == '鬼' and s[1] == '王':
            return Combination(s, '', 'rocket')
        else:
            return 'error'
    
    elif len(s) == 3:
        if s[0] == s[1] and s[1] == s[2]:
            return Combination(s[0], '', 'triple')
        else:
            return 'error'

    elif len(s) == 4:
        if s[1] == s[2] and s[2] == s[3]:
            # s[0], s[3] = s[3], s[0]
            s = s[3] + s[1:3] + s[0]

        if s[0] == s[1] and s[1] == s[2]:
            if s[2] == s[3]:
                return Combination(s[0], '', 'quadruple')
            else:
                return Combination(s[0], s[3], 'triple1')
        else:
            return 'error'

    elif len(s) == 5:
        if s[2] == s[3] and s[3] == s[4]:
            # s[0], s[1], s[3], s[4] = s[3], s[4], s[0], s[1]
            s = s[3] + s[4] + s[2] + s[0] + s[1]

        if s[0] == s[1] and s[1] == s[2] and s[3] == s[4]:
            return Combination(s[0], s[3] * 2, 'triple2')
        
    elif len(s) == 6:
        if s[1] == s[2] and s[2] == s[3] and s[3] == s[4]:
            s = ''.join(list(s)[1:] + list(s)[:1])
        if s[2] == s[3] and s[3] == s[4] and s[4] == s[5]:
            s = ''.join(list(s)[2:] + list(s)[:2])
        if s[0] == s[1] and s[1] == s[2] and s[2] == s[3]:
            return Combination(s[0], s[4] + s[5], 'quadruple2')
        
    if s in '34567891JQKA' and len(s) >= 5:
        return Combination(s, '', 'serial')
    if s[0::2] == s[1::2]:
        t = ''.join(s[0::2])
        if t in '34567891JQKA' and len(t) >= 3:
            return Combination(t, '', '2serial')
    
    v = [0] * len('34567891JQKA2鬼王')
    for c in s:
        v['34567891JQKA2鬼王'.find(c)] += 1
    d = [[] for i in range(54)]
    for i in range(len(v)):
        d[v[i]].append('34567891JQKA2鬼王'[i])

    if len(d[3]) >= 2:
        k = ''.join(d[3])
        if not k in '34567891JQKA':
            return 'error'

        if len(s) == 3 * len(d[3]):
            return Combination(''.join(d[3]), '', '3serial')
        if len(s) == 4 * len(d[3]):
            return Combination(''.join(d[3]), ''.join([c if not c in d[3] else '' for c in s]), '3serial1')
        if len(s) == 3 * len(d[3]) + 2 * len(d[2]):
            return Combination(''.join(d[3]), ''.join([c * 2 for c in d[2]]), '3serial2')
    
    return 'error'


bot = nonebot.get_bot()

async def send_group_message(session : CommandSession, s, at = True):
    if at:
        s = message.MessageSegment.at(session.event.user_id) + ' ' + s
    await session.send(s)

async def send_private_message(user_id, s):
    try:
        await bot.send_private_msg(user_id = user_id, message = s)
    except:
        pass


class Player:
    def __init__(self):
        self.hand = ''
        self.type = '未知'
        self.state = ''
    
    def check(self, s):
        t = self.hand[:]
        for c in s:
            if not c in t:
                return False
            p = t.find(c)
            t = t[:p] + t[p + 1:]
        return True
    
    def play(self, s):
        t = self.hand[:]
        for c in s:
            if not c in t:
                return False
            p = t.find(c)
            t = t[:p] + t[p + 1:]
        self.hand = t
    
    def join(self, s):
        self.hand += s
        self.sort()
    
    def sort(self):
        self.hand = ''.join(sorted(list(self.hand), key = lambda x : '34567891JQKA2鬼王'.index(x)))
    
    def get_hand(self):
        return completed(' '.join(list(self.hand)))

class Game:
    def __init__(self):
        self.players = []
        self.tbl = dict()
        self.cur = 0
        self.cur_player = 0
        self.last_step = None
        self.last_player = 0
        self.state = ''
        self.deck = ''

    def next_player(self):
        self.cur = (self.cur + 1) % len(self.players)
        self.cur_player = self.players[self.cur]

    def prepare(self):
        random.shuffle(self.players)

        for i in self.players:
            self.tbl[i] = Player()

        self.deck = list('鬼王' + '34567891JQKA2' * 4)
        random.shuffle(self.deck)
        self.deck = ''.join(self.deck)

        for i in range(17):
            for j in self.players:
                self.tbl[j].join(self.deck[0])
                self.deck = self.deck[1:]
        
        # 剩下三张底牌
        self.cur = random.randint(0, 2)
        self.cur_player = self.players[self.cur]
        self.last_step = self.cur_player
        return random.choice(list(self.tbl[self.cur_player].hand)) # 从抽中明牌者开始叫地主
    
    def clear(self):
        self.players = []
        self.tbl.clear()

games = dict()


@on_command('开始游戏', aliases = ('开始', '开局', 'ks'), only_to_me = False, permission = perm.GROUP)
async def kaiju(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if len(g.players) < 3:
        await send_group_message(session, '人数不足，无法开始')
        return

    if g.state:
        await send_group_message(session, '游戏已开始')
        return
    
    card = g.prepare()
    for i in g.players:
        await send_private_message(i, g.tbl[i].get_hand())

    g.state = 'jdz'
    s = '游戏已开始！\n玩家列表：'
    for i in g.players:
        s = s + ' ' + message.MessageSegment.at(i)
    s = s + '\n' + message.MessageSegment.at(g.cur_player) + ' 抽到了明牌' + completed(card) + '，请决定是否叫地主'
    await session.send(s)


@on_command('结束游戏', aliases = ('结束', 'js'), only_to_me = False, permission = perm.GROUP)
async def jieshu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id != 1094054222:
        await send_group_message(session, '只有绿可以使用此功能')
        return

    if not group_id in games:
        await send_group_message(session, '游戏未开始')
        return
    
    games[group_id].clear()
    games.pop(group_id)
    await send_group_message(session, '结束成功')


@on_command('加入游戏', aliases = ('加入', 'jr', '上桌', 'sz'), only_to_me = False, permission = perm.GROUP)
async def jiaru(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games:
        games[group_id] = Game()
        
    g = games[group_id]

    if user_id in g.players:
        await send_group_message(session, '你已经加入过了')
        return

    if g.tbl:
        await send_group_message(session, '游戏已开始，无法加入')
        return
    
    if len(g.players) == 3:
        await send_group_message(session, '人数已满，无法加入')
        return
    
    g.players.append(user_id)

    await send_group_message(session, '加入成功，当前共有%d人\n为正常进行游戏，请加bot为好友' % len(g.players))


@on_command('退出游戏', aliases = ('退出', '下桌', 'tc', 'xz'), only_to_me = False, permission = perm.GROUP)
async def tuichu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]
    
    if g.tbl:
        await send_group_message(session, '游戏已开始，无法退出')
        return
        
    g.players.remove(user_id)

    await send_group_message(session, '退出成功，当前还剩%d人' % len(g.players))

    if not g.players:
        games.pop(group_id)


@on_command('叫地主', aliases = ('叫', 'j'), only_to_me = False, permission = perm.GROUP)
async def jiaodizhu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if not g.state:
        await send_group_message(session, '游戏未开始')
        return
    
    if g.state == 'qdz':
        await send_group_message(session, '现在是抢地主环节')
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你叫地主')
        return
    
    await send_group_message(session, '选择叫地主')
    g.last_player = g.cur_player
    g.state = 'qdz'
    g.next_player()
    await session.send('请 ' + message.MessageSegment.at(g.cur_player) + ' 选择是否抢地主')

@on_command('不叫', aliases = ('bujiao', 'bj'), only_to_me = False, permission = perm.GROUP)
async def bujiao(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if not g.state:
        await send_group_message(session, '游戏未开始')
        return
    
    if g.state == 'qdz':
        await send_group_message(session, '现在是抢地主环节')
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你叫地主')
        return

    await send_group_message(session, '选择不叫地主')
    g.next_player()

    if g.cur_player == g.last_player:
        g.clear()
        games.pop(group_id)
        await session.send('由于无人叫地主，本局流局，请重新加入并开始游戏')
        return

    await session.send('请 ' + message.MessageSegment.at(g.cur_player) + ' 选择是否叫地主')


@on_command('抢地主', aliases = ('抢', 'qiang', 'qdz', 'q'), only_to_me = False, permission = perm.GROUP)
async def qiangdizhu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if not g.state:
        await send_group_message(session, '游戏未开始')
        return
    
    if g.state == 'jdz':
        await send_group_message(session, '还没到抢地主环节')
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你抢地主')
        return

    await send_group_message(session, '选择抢地主')

    if g.cur_player == g.last_player:
        dizhu = g.last_player

        g.tbl[dizhu].type = '地主'
        for i in g.tbl:
            if i != dizhu:
                g.tbl[i].type = '农民'
        
        await session.send(message.MessageSegment.at(dizhu) + ' 成为了地主！\n底牌是：' + ' '.join(map(completed, list(g.deck))))
        g.tbl[dizhu].join(g.deck)
        await send_private_message(dizhu, g.tbl[dizhu].get_hand())
        # g.deck = ''

        g.state = 'started'

        await session.send('请地主 ' + message.MessageSegment.at(dizhu) + ' 开始出牌')
        g.cur_player = g.last_player = dizhu
        g.cur = g.players.index(dizhu)

        return

    g.next_player()

    await session.send('请 ' + message.MessageSegment.at(g.cur_player) + ' 选择是否抢地主')


@on_command('不抢', aliases = ('buqiang', 'bq'), only_to_me = False, permission = perm.GROUP)
async def buqiang(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if not g.state:
        await send_group_message(session, '游戏未开始')
        return
    
    if g.state == 'jdz':
        await send_group_message(session, '还没到抢地主环节')
        return
    
    if g.state == 'started':
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你抢地主')
        return

    await send_group_message(session, '选择不抢地主')

    dizhu = g.players[(g.players.index(user_id) - 1) % 3]

    g.tbl[dizhu].type = '地主'
    for i in g.tbl:
        if i != dizhu:
            g.tbl[i].type = '农民'
    
    await session.send(message.MessageSegment.at(dizhu) + ' 成为了地主！\n底牌是：' + ' '.join(map(completed, list(g.deck))))
    g.tbl[dizhu].join(g.deck)
    await send_private_message(dizhu, g.tbl[dizhu].get_hand())
    # g.deck = ''

    g.state = 'started'

    await session.send('请地主 ' + message.MessageSegment.at(dizhu) + ' 开始出牌')
    g.cur_player = g.last_player = dizhu
    g.cur = g.players.index(dizhu)


@on_command('出', aliases = ('出牌', 'chu', 'c'), only_to_me = False, permission = perm.GROUP)
async def chu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if g.state != 'started':
        await send_group_message(session, '游戏未开始或未开始出牌')
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你出牌')
        return
    
    if not 'text' in session.state:
        await send_group_message(session, '用法：出/chu/c + 你要出的牌(顺序随意，不要有空格)')
        return
    
    s = simplified(session.state['text'])
    if s == 'error':
        await send_group_message(session, '输入不合法')
        return

    v = handle(s)
    if v == 'error':
        await send_group_message(session, '牌型不合法')
        return
    
    if not g.tbl[user_id].check(s):
        await send_group_message(session, '你没有这些牌')
        return
    
    if g.last_player != user_id:
        t = g.last_step.check(v)
        if t == 'different type':
            await send_group_message(session, '牌型不符')
        elif t == 'smaller':
            await send_group_message(session, '这牌盖不过刚才出的牌')
        if t != 'bigger':
            return
    
    g.tbl[user_id].play(s)

    if not g.tbl[user_id].hand:
        await send_group_message(session, '打出了：' + completed(str(v)))
        await send_group_message(session, '已经出完了所有牌！')
        
        s = ''
        for i in g.players:
            if g.tbl[i].type == g.tbl[user_id].type:
                if s:
                    s = s + '和'
                s = s + ' ' + message.MessageSegment.at(i)
        
        await session.send(g.tbl[user_id].type + s + ' 获得了胜利！')

        g.clear()
        games.pop(group_id)

    
    await send_group_message(session, '打出了：' + completed(str(v)) + '，还剩%d张牌' % len(g.tbl[user_id].hand))

    await send_private_message(user_id, g.tbl[user_id].get_hand())

    g.last_step = v
    g.last_player = user_id

    g.next_player()

    s = '轮到 ' + g.tbl[g.cur_player].type + ' ' + message.MessageSegment.at(g.cur_player) + ' 出牌，上一次出牌是 ' + message.MessageSegment.at(user_id) \
        + ' 出的：' + completed(str(v))
    await session.send(s)


@chu.args_parser
async def chu_parser(session):
    v = session.current_arg_text.split()
    if len(v) == 1:
        session.state['text'] = v[0].upper()

@on_command('过', aliases = ('pass', '不出', 'g', 'bc', 'p'), only_to_me = False, permission = perm.GROUP)
async def buchu(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games or not user_id in games[group_id].players:
        await send_group_message(session, '你没有加入当前游戏')
        return
    
    g = games[group_id]

    if g.state != 'started':
        await send_group_message(session, '游戏未开始或未开始出牌')
        return
    
    if g.cur_player != user_id:
        await send_group_message(session, '还没有轮到你出牌')
        return
    
    if g.last_player == user_id:
        await send_group_message(session, '现在不能过牌')
        return
    
    g.next_player()
    await send_group_message(session, '选择不出牌')
    
    s = '轮到 ' + g.tbl[g.cur_player].type + ' ' + message.MessageSegment.at(g.cur_player) + ' 出牌，上一次出牌是 ' + message.MessageSegment.at(g.last_player) \
        + ' 出的：' + completed(str(g.last_step))
    await session.send(s)


@on_command('状态', aliases = ('zhuangtai', 'stat', 'status', 'zt'), only_to_me = False, permission = perm.GROUP)
async def zhuangtai(session):
    group_id = session.event.group_id
    user_id = session.event.user_id

    if not group_id:
        await session.send('请在群聊中使用斗地主功能')
        return
    
    if user_id == 80000000:
        await send_group_message(session, '请解除匿名后再使用斗地主功能', at = False)
        return
    
    if not group_id in games:
        await send_group_message(session, '本群还没有人使用斗地主功能')
        return
    
    g = games[group_id]

    if not g.state:
        s = '斗地主未开始，当前等待中的玩家有：'
        for i in g.players:
            s = s + '\n' + message.MessageSegment.at(i)
        
        await send_group_message(session, s)

    elif g.state == 'jdz' or g.state == 'qdz':
        s = '斗地主已开始，当前玩家有：'
        for i in g.players:
            s = s + '\n' + message.MessageSegment.at(i)
        
        s = s + '\n当前状态：等待 ' + message.MessageSegment.at(g.cur_player) + ' ' + ('叫' if g.state == 'jdz' else '抢') + '地主'
        
        await send_group_message(session, s)
    
    else:
        s = '斗地主已开始，当前玩家和手牌张数如下：'
        for i in g.players:
            s = s + '\n' + g.tbl[i].type + ' ' + message.MessageSegment.at(i) + '：%d张' % len(g.tbl[i].hand)
        
        s = s + '\n底牌是：' + ' '.join(map(completed, list(g.deck)))
        
        s = s + '\n当前状态：等待 ' + message.MessageSegment.at(g.cur_player) + ' 出牌'

        if g.cur_player != g.last_player:
            s = s + '\n上一次出牌是 ' + message.MessageSegment.at(g.last_player) + ' 出的：' + completed(str(g.last_step))
        
        await send_group_message(session, s)