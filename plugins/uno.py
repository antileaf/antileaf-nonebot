# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm

import random

bot = nonebot.get_bot()

async def debug(s):
    await bot.send_private_msg(user_id = 1094054222, message = s)

color_tbl = dict([
    ('红', ('红', 'red', 'R', 'r', '红色')),
    ('绿', ('绿', 'green', 'G', 'g', '绿色')),
    ('蓝', ('蓝', 'blue', 'B', 'b', '蓝色')),
    ('黄', ('黄', 'yellow', 'Y', 'y', '黄色')),
    ('', ('', 'black', 'W', 'w', '特殊', 'wild', '黑', '黑色', '无色', 'special', '特别'))
    # 黑色仅用于手牌，打出后即赋予颜色
])
value_tbl = dict([
    ('0', ('0')),
    ('1', ('1')),
    ('2', ('2')),
    ('3', ('3')),
    ('4', ('4')),
    ('5', ('5')),
    ('6', ('6')),
    ('7', ('7')),
    ('8', ('8')),
    ('9', ('9')),
    ('跳过', ('跳过', 'skip', '跳', 'sk', 'S', 's')),
    ('+2', ('+2', '加2')),
    ('反转', ('反转', 'reverse', '反', 'R', 'r')),
    ('+4', ('+4', '加4')),
    ('转色', ('转色', 'change', '换', 'C', 'c')),
])

class Card:
    def __init__(self, color, value : str):
        self.color = color # 红 绿 蓝 黄 黑
        self.value = value # 数字或者 跳过/+2/反转/+4/转色
        self.aliases = [i + j for i in color_tbl[self.color] for j in value_tbl[self.value]]

    def __str__(self):
        if (self.value == '+4' or self.value == '转色') and self.color:
            return self.value + '(选择%s色)' % self.color
        else:
            return self.color + self.value
    
    def __eq__(self, s : str):
        return s in self.aliases
    
    def check(self, o): # o 能否接在 self 后面
        if not self.value:
            return True
        if not o.color and (o.value == '+4' or self.value != '+4'):
            return True
        if o.color == self.color or o.value == self.value:
            return True
        return False

class Player:
    def __init__(self, user_id):
        self.user_id = self
        self.hand = []
        self.stat = ''
        
    def play(self, s : str):
        for c in self.hand:
            if c == s:
                self.hand.remove(c)
                return c
        return False

    def print_hand(self):
        v = dict()
        for i in color_tbl:
            v[i] = []
        for c in self.hand:
            v[c.color].append(c.value)
        
        l = ['总牌数：%d张' % len(self.hand)]

        for c in v:
            s = color_tbl[c][4] + '：'
            if not v[c]:
                s += ' ' + '无'
            for t in sorted(v[c]):
                s += ' ' + str(t)

            l.append(s)
        
        return '\n'.join(l)

class Game:
    def __init__(self, group_id):
        self.group_id = group_id

        self.deck = [] # 生成牌堆

        for i in ['红', '黄', '蓝', '绿']:
            self.deck.append(Card(i, '0'))
            for j in list('123456789') + ['跳过', '+2', '反转']:
                self.deck.append(Card(i, j))
                self.deck.append(Card(i, j))
        for j in ['+4', '转色']:
            self.deck.append(Card('', j))
            self.deck.append(Card('', j))
            self.deck.append(Card('', j))
            self.deck.append(Card('', j))
        # random.shuffle(self.deck)

        self.players = []
        self.tbl = dict()
        
        self.last_card = Card('', '0')
        self.total_draw = 0
        self.direction = 1
        self.current = -1
        self.current_player = 0
        self.active_player = 0

        self.skipped = False

        self.rank = []
        self.bottom = []

    def add_player(self, user_id):
        self.players.append(user_id)
        self.tbl[user_id] = Player(user_id)
    
    def remove_player(self, user_id):
        self.players.remove(user_id)
        self.tbl.pop(user_id)
    
    def draw(self, user_id, n):
        v = []
        for i in range(n):
            if not self.deck:
                return v
            
            card = random.choice(self.deck)
            v.append(card)
            self.deck.remove(card)
            self.tbl[user_id].hand.append(card)
        
        return v

    def next_player(self):
        if self.current_player:
            self.tbl[self.current_player].stat = 'free'

        self.current =  (self.current + self.direction) % len(self.players)
        self.current_player = self.players[self.current]
        while not self.tbl[self.current_player].hand:
            self.current =  (self.current + self.direction) % len(self.players)
            self.current_player = self.players[self.current]
        
        self.tbl[self.current_player].stat = 'waiting to play'
        
        if self.skipped:
            self.skipped = False
            self.next_player()
    
    def start(self):
        for user_id in self.players:
            self.draw(user_id, 7)
            self.tbl[user_id].stat = 'free'
        self.active_player = len(self.players)

        self.last_card = random.choice(self.deck)
        while self.last_card.color == '':
            self.last_card = random.choice(self.deck)
        self.deck.remove(self.last_card) # 初始牌

    def end(self):
        self.rank += reversed(self.bottom)

        s = '本局游戏排名：'
        for i in range(len(self.rank)):
            s += '\n第%d名： ' % (i + 1) + message.MessageSegment.at(self.rank[i])
        return s
    
games = dict()
players = dict()
in_game = dict()

# bot = nonebot.get_bot()


@on_command('加入游戏', aliases = ('上桌', '加入', 'join', 'jiaru', 'jr'), only_to_me = False, permission = perm.GROUP)
async def join_game(session):

    global games, in_game, players

    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
    
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id

    if group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 游戏已开始，无法加入')
        return
    
    if group_id in players and user_id in players[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 你已经加入过了')
        return
    
    if user_id in in_game:
        await session.send(message.MessageSegment.at(user_id) + ' 你已经在其他群加入过了，请先退出才能在本群加入游戏')
        return
    
    if not group_id in players:
        players[group_id] = []
    
    players[group_id].append(user_id)
    in_game[user_id] = group_id

    await session.send(message.MessageSegment.at(user_id) + ' 加入成功，当前共有%d人\n为正常进行游戏，请加bot为好友' % len(players[group_id]))
    

@on_command('退出游戏', aliases = ('退出', '下桌', '离开', 'leave', 'tuichu', 'tc'), only_to_me = False, permission = perm.GROUP)
async def leave_game(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
    
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not group_id in players or not user_id in players[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 未加入游戏，无法退出')
        return

    if group_id in games and user_id in players[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 游戏已开始，无法退出')
        return
    
    players[group_id].remove(user_id)
    in_game.pop(user_id)

    if not players[group_id]:
        players.pop(group_id)
    
    await session.send(message.MessageSegment.at(user_id) + '退出成功，当前还有%d人' % \
        (len(players[group_id]) if group_id in players else 0))


@on_command('开局', aliases = ('开始游戏', '开始', 'start', 'kj', 'ks', 'begin'), only_to_me = False, permission = perm.GROUP)
async def start_game(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
    
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    # if user_id != 1094054222:
    #    await session.send(message.MessageSegment.at(user_id) + ' 只有绿可以使用此功能')
    #    return
    
    if not group_id in players or not user_id in players[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 你还没有加入游戏')
        return

    if not group_id in players or len(players[group_id]) < 2:
        await session.send('游戏人数不足，无法开始')
        return
    
    games[group_id] = Game(group_id)
    for i in players[group_id]:
        games[group_id].add_player(i)

    games[group_id].start()
    
    s = message.MessageSegment.text('游戏已开始！\n玩家列表：')
    for i in players[group_id]:
        s += ' ' + message.MessageSegment.at(i)
    await session.send(s)

    for i in players[group_id]:
        s = games[group_id].tbl[i].print_hand()
        try:
            await bot.send_private_msg(user_id = i, message = s)
        except:pass

        s = ''

    await session.send('发牌完毕，请检查私聊查看手牌')

    await session.send('第一张牌：%s\n即将从第一位玩家开始出牌……' % str(games[group_id].last_card))

    games[group_id].next_player()
    
    s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
        + str(games[group_id].last_card)

    if games[group_id].total_draw:
        s = s + '，已累计罚牌%d张' % games[group_id].total_draw

    s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
        + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'
    await session.send(s)

@on_command('结束游戏', aliases = ('结束', 'end', 'js', 'jieshu'), only_to_me = False, permission = perm.GROUP)
async def end_game(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id

    if user_id != 1094054222:
        await session.send(message.MessageSegment.at(user_id) + '只有绿可以使用此功能')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 游戏尚未开始')
        return

    await session.send('当前游戏已被强制结束')
    v = []
    for i in games[group_id].tbl:
        if not i in games[group_id].rank and not i in games[group_id].bottom:
            v.append((len(games[group_id].tbl[i].hand) ,i))
    
    s = games[group_id].end()
    await session.send(s)

    for i in games[group_id].players:
        in_game.pop(i)
    games.pop(group_id)
    players.pop(group_id)

@on_command('放弃', aliases = ('弃牌', 'fangqi', 'fq', 'qp', 'giveup'), only_to_me = False, permission = perm.GROUP)
async def give_up(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
    
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not group_id in games or not user_id in players[group_id]:
        await session.send(message.MessageSegment.at(user_id) + ' 未加入游戏或游戏未开始，无法放弃')
        return
    
    if games[group_id].current_player == user_id:
        await session.send(message.MessageSegment.at(user_id) + ' 出牌时无法放弃，请先完成行动')
        return
    
    players[group_id].remove(user_id)
    in_game.pop(user_id)
        
    await session.send(message.MessageSegment.at(user_id) + ' 放弃了游戏，获得第%d名' % (len(games[group_id].tbl) - len(games[group_id].bottom)))
    games[group_id].tbl[user_id].hand.clear()

    games[group_id].bottom.append(user_id)
    games[group_id].active_player -= 1

    if games[group_id].active_player == 1:

        # await debug('players:' + str(players))

        await session.send('游戏结束！')
        games[group_id].rank.append(games[group_id].current_player)
        s = games[group_id].end()
        await session.send(s)

        for i in games[group_id].players:
            if i in in_game:
                in_game.pop(i)
        games.pop(group_id)
        players.pop(group_id)

        return

@on_command('出', aliases = ('出牌', 'chu', 'chupai', 'c', 'cp'), only_to_me = False, permission = perm.GROUP)
async def play(session):

    global games, in_game, players

    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not user_id in in_game or in_game[user_id] != group_id:
        await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 没开始呢，急什么')
        return

    if games[group_id].tbl[user_id].stat == 'free':
        await session.send(message.MessageSegment.at(user_id) + ' 没到你出牌呢，急什么')
        return
    
    if games[group_id].tbl[user_id].stat != 'waiting to play':
        await session.send(message.MessageSegment.at(user_id) + ' 别瞎输指令')
        return
    
    if not 'name' in session.state:
        await session.send(message.MessageSegment.at(user_id) + ' 指令格式有误')
        return

    s = session.state['name']

    card = Card('', '0')
    for c in games[group_id].tbl[user_id].hand:
        if c == s:
            card = c
            break
    
    if card.color == '' and card.value == '0':
        await session.send(message.MessageSegment.at(user_id) + ' 你就没有这张牌，会不会玩')
        return
    
    if not games[group_id].last_card.check(card):
        await session.send(message.MessageSegment.at(user_id) + ' 这张牌接不上，能不能先看看规则再来')
        return
    
    if games[group_id].total_draw and (card.value != '+2' and card.value != '+4'):
        await session.send(message.MessageSegment.at(user_id) + ' 现在罚牌呢，要不起就乖乖别出')
        return

    games[group_id].tbl[user_id].hand.remove(card)

    await bot.send_private_msg(user_id = user_id, message = '你打出了：' + str(card))

    s = message.MessageSegment.at(user_id) + ' 打出了：' + str(card)

    await debug('color = %s  value = %s' % (card.color, card.value))

    t = games[group_id].tbl[user_id].print_hand()
    try:
        await bot.send_private_msg(user_id = user_id, message = t)
    except:pass

    if card.value == '跳过':
        games[group_id].skipped = True
        s = s +  '，下家的回合被跳过了'
    elif card.value == '反转':
        games[group_id].direction *= -1
        s = s + '，出牌方向变为按' + ('顺' if games[group_id].direction == 1 else '逆') + '序出牌'

    games[group_id].last_card = card
    if card.value == '+2' or card.value == '+4':
        games[group_id].total_draw += (2 if card.value == '+2' else 4)

    await session.send(s)

    if len(games[group_id].tbl[user_id].hand) == 1 and not 'uno' in session.state:
        await session.send('在为什么不UNO，罚摸两张牌')
        v = games[group_id].draw(user_id, 2)
        s = ' '.join(map(str, v))
        try:
            await bot.send_private_msg(user_id = user_id, message = '你抽到了： ' + s)
        except:pass

        s = games[group_id].tbl[user_id].print_hand()
        try:
            await bot.send_private_msg(user_id = user_id, message = s)
        except:pass

        s = ''

    if not card.color:
        games[group_id].tbl[user_id].stat = 'waiting to choose'
        await session.send('请选择一种颜色\n\"选择\" + 你想选的颜色')
    else:
        if not games[group_id].tbl[user_id].hand:
            games[group_id].active_player -= 1
            await session.send(message.MessageSegment.at(user_id) + ' 已经出完了所有牌！')
            games[group_id].rank.append(user_id)
            
        games[group_id].next_player()
        
        if games[group_id].active_player == 1:
            await session.send('游戏结束！')
            games[group_id].rank.append(games[group_id].current_player)
            s = games[group_id].end()
            await session.send(s)

            for i in games[group_id].players:
                if i in in_game:
                    in_game.pop(i)
            games.pop(group_id)
            players.pop(group_id)

            return
        
        s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
            + str(games[group_id].last_card)

        if games[group_id].total_draw:
            s = s + '，已累计罚牌%d张' % games[group_id].total_draw

        s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
            + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'

        await session.send(s)
        
@play.args_parser
async def play_parser(session):

    global games, in_game, players
    
    v = session.current_arg_text.split()
    
    if v:
        if len(v) == 2 and v[-1].lower() == 'uno':
            session.state['uno'] = True
            v.pop()
        if len(v) == 1:
            session.state['name'] = v[0]


@on_command('不出', aliases = ('pass', '摸牌', 'buchu', 'bc'), only_to_me = False, permission = perm.GROUP)
async def buchu(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not user_id in in_game or in_game[user_id] != group_id:
        await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 没开始呢，急什么')
        return

    if games[group_id].tbl[user_id].stat == 'free':
        await session.send(message.MessageSegment.at(user_id) + ' 没到你出牌呢，急什么')
        return
    
    if games[group_id].tbl[user_id].stat != 'waiting to play':
        await session.send(message.MessageSegment.at(user_id) + ' 别瞎输指令')
        return

    s = message.MessageSegment.at(user_id) + ' 选择不出牌，'

    v = games[group_id].draw(user_id, 1)
    if not v:
        s += '牌堆已空，不再摸牌'
        await session.send(s)
        
        if games[group_id].total_draw:

            s = ' '.join(map(str, games[group_id].draw(user_id, games[group_id].total_draw)))
            try:
                await bot.send_private_msg(user_id = user_id, message = '你抽到了： ' + s)
            except:pass

            s = games[group_id].tbl[user_id].print_hand()
            try:
                await bot.send_private_msg(user_id = user_id, message = s)
            except:pass

            s = ''

            await session.send(message.MessageSegment.at(user_id) + ' 被罚摸%d张牌！\n当前手牌数：%d张' % \
             (games[group_id].total_draw, len(games[group_id].tbl[user_id].hand)))
            games[group_id].total_draw = 0

        games[group_id].next_player()
        
        s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
            + str(games[group_id].last_card)

        if games[group_id].total_draw:
            s = s + '，已累计罚牌%d张' % games[group_id].total_draw

        s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
            + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'

        await session.send(s)
        return
    
    s += '并摸了一张牌'
    await session.send(s)

    s = ' '.join(map(str, v))
    try:
        await bot.send_private_msg(user_id = user_id, message = '你抽到了： ' + s)
    except:pass

    s = games[group_id].tbl[user_id].print_hand()
    try:
        await bot.send_private_msg(user_id = user_id, message = s)
    except:pass

    s = ''

    await session.send(message.MessageSegment.at(user_id) + '请选择是否打出刚刚摸到的牌\n\"是\"打出 \"否\"不打出')

    games[group_id].tbl[user_id].stat = 'waiting to confirm'


@on_command('选择', aliases = ('choose', 'xz', 'xuanze'), only_to_me = False, permission = perm.GROUP)
async def choose_color(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not user_id in in_game or in_game[user_id] != group_id:
        await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 没开始呢，急什么')
        return
    
    if games[group_id].tbl[user_id].stat != 'waiting to choose':
        await session.send(message.MessageSegment.at(user_id) + ' 别瞎输指令')
        return
    
    if not 'color' in session.state:
        await session.send(message.MessageSegment.at(user_id) + ' 指令格式有误')
        return

    temp = session.state['color']

    color = ''

    for c in color_tbl:
        if c == '':
            break
        for t in color_tbl[c]:
            if temp == t:
                color = c
                break
        if color:
            break
    
    if not color:
        await session.send(message.MessageSegment.at(user_id) + ' 能不能给个阳间的颜色')
        return
    
    await session.send(message.MessageSegment.at(user_id) + ' 选择了%s色' % color)

    games[group_id].last_card.color = color

    if not games[group_id].tbl[user_id].hand:
        games[group_id].active_player -= 1
        await session.send(message.MessageSegment.at(user_id) + ' 已经出完了所有牌，获得第%d名！' % (len(games[group_id].rank) + 1))
        games[group_id].rank.append(user_id)
        
    games[group_id].next_player()
    
    if games[group_id].active_player == 1:
        await session.send('游戏结束！')
        games[group_id].rank.append(games[group_id].current_player)
        s = games[group_id].end()
        await session.send(s)

        for i in games[group_id].players:
            if i in in_game:
                in_game.pop(i)
        games.pop(group_id)
        players.pop(group_id)

        return

    s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
        + str(games[group_id].last_card)

    if games[group_id].total_draw:
        s = s + '，已累计罚牌%d张' % games[group_id].total_draw

    s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
        + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'

    await session.send(s)

@choose_color.args_parser
async def choose_color_parser(session):

    global games, in_game, players
    
    v = session.current_arg_text.split()
    
    if len(v) == 1:
        session.state['color'] = v[0]


@on_command('是', aliases = ('shi', 's'), only_to_me = False, permission = perm.GROUP)
async def shi(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not user_id in in_game or in_game[user_id] != group_id:
        await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 没开始呢，急什么')
        return
    
    if games[group_id].tbl[user_id].stat != 'waiting to confirm':
        await session.send(message.MessageSegment.at(user_id) + ' 别瞎输指令')
        return
    
    card = games[group_id].tbl[user_id].hand[-1]

    if not games[group_id].last_card.check(card):
        await session.send(message.MessageSegment.at(user_id) + ' 这牌跟不了，做梦呢你')
        return
    
    if games[group_id].total_draw and card.value != '+2' and card.value != '+4':
        await session.send(message.MessageSegment.at(user_id) + ' 现在罚牌呢，要不起就乖乖别出')
        return

    games[group_id].tbl[user_id].hand.remove(card)

    await bot.send_private_msg(user_id = user_id, message = '你打出了：' + str(card))

    s = message.MessageSegment.at(user_id) + ' 打出了刚刚抽到的：' + str(card) \
        + '\n当前手牌数：%d张' % len(games[group_id].tbl[user_id].hand)
    await session.send(s)

    s = games[group_id].tbl[user_id].print_hand()
    try:
        await bot.send_private_msg(user_id = user_id, message = s)
    except:pass

    s = ''

    if card.value == '跳过':
        games[group_id].skipped = True
        s += '，下家的回合被跳过了'
    elif card.value == '反转':
        games[group_id].direction *= -1
        s += '，出牌方向变为按' + ('顺' if games[group_id].direction == 1 else '逆') + '序出牌'

    games[group_id].last_card = card
    if card.value == '+2' or card.value == '+4':
        games[group_id].total_draw += (2 if card.value == '+2' else 4)
            
    games[group_id].next_player()
    
    s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
        + str(games[group_id].last_card)

    if games[group_id].total_draw:
        s = s + '，已累计罚牌%d张' % games[group_id].total_draw

    s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
        + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'

    await session.send(s)

@on_command('否', aliases = ('fou', 'f'), only_to_me = False, permission = perm.GROUP)
async def fou(session):

    global games, in_game, players
    

    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id
    
    if not user_id in in_game or in_game[user_id] != group_id:
        await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
        return

    if not group_id in games:
        await session.send(message.MessageSegment.at(user_id) + ' 没开始呢，急什么')
        return
    
    if games[group_id].tbl[user_id].stat != 'waiting to confirm':
        await session.send(message.MessageSegment.at(user_id) + ' 别瞎输指令')
        return
    
    if games[group_id].total_draw:
        s = ' '.join(map(str, games[group_id].draw(user_id, games[group_id].total_draw)))
        try:
            await bot.send_private_msg(user_id = user_id, message = '你抽到了： ' + s)
        except:pass

        s = games[group_id].tbl[user_id].print_hand()
        try:
            await bot.send_private_msg(user_id = user_id, message = s)
        except:pass

        s = ''

        await session.send(message.MessageSegment.at(user_id) + ' 被罚摸%d张牌！\n当前手牌数：%d张' % \
             (games[group_id].total_draw, len(games[group_id].tbl[user_id].hand)))
        games[group_id].total_draw = 0

    games[group_id].next_player()
    
    s = '轮到 ' + message.MessageSegment.at(games[group_id].current_player) + ' 出牌，最后一张牌是：' \
        + str(games[group_id].last_card)

    if games[group_id].total_draw:
        s = s + '，已累计罚牌%d张' % games[group_id].total_draw

    s = s + '，牌堆中还剩%d张牌' % len(games[group_id].deck) \
        + '\n\"出\" + 你要出的牌出牌，\"不出\"摸一张牌'

    await session.send(s)


@on_command('状态', aliases = ('查询状态', 'uno状态', 'zt'), only_to_me = False, permission = perm.GROUP)
async def query_stat(session):

    global games, in_game, players
    
    if not session.event.group_id:
        await session.send('请在群聊中使用UNO功能')
        return
        
    user_id = int(session.event['user_id'])
    group_id = session.event.group_id

    if not group_id in games:
        s = 'UNO未开始，目前'
        if not group_id in players:
            s = s + '无人等待中'
        else:
            s = s + '正在等待的人有：'
            for i in players[group_id]:
                s += ' ' + message.MessageSegment.at(i)
        
        await session.send(s)
        return
    
    # if not user_id in in_game or in_game[user_id] != group_id:
    #    await session.send(message.MessageSegment.at(user_id) + ' 这群打牌的没你，一边待着去')
    #    return
    
    s = message.MessageSegment.text('UNO已开始，以下是所有玩家当前的手牌数或排名：')
    for i in games[group_id].players:
        s = s + '\n' + message.MessageSegment.at(i) + ' ：'
        if games[group_id].tbl[i].hand:
            s = s + '%d张' % len(games[group_id].tbl[i].hand)
        else:
            if i in games[group_id].rank:
               s = s + '跑了，第%d名' % (games[group_id].rank.index(i) + 1)
            elif i in games[group_id].bottom:
               s = s + '已放弃，第%d名' % (len(games[group_id].tbl) - games[group_id].bottom.index(i))
    
    s = s + '\n牌堆剩余牌数：%d张   当前出牌顺序：%s序' % (len(games[group_id].deck), ('顺' if games[group_id].direction == 1 else '逆'))

    s = s + '\n当前状态：等待' + message.MessageSegment.at(games[group_id].current_player)
    if games[group_id].tbl[games[group_id].current_player].stat == 'waiting to play':
        s = s + '出牌'
    elif games[group_id].tbl[games[group_id].current_player].stat == 'waiting to confirm':
        s = s + '决定是否打出刚抽到的牌'
    elif games[group_id].tbl[games[group_id].current_player].stat == 'waiting to choose':
        s = s + '选择颜色'

    await session.send(s)

@on_command('查询手牌', aliases = ('查询', '我的手牌', 'cx', '手牌', 'shoupai', 'sp', '牌'), only_to_me = False, permission = perm.GROUP)
async def query_hand(session):

    global games, in_game, players
    
    user_id = int(session.event['user_id'])

    if not user_id in in_game:
        await session.send('你不在一场游戏中')
        return
    
    if not in_game[user_id] in games:
        await session.send('游戏未开始')
        return
    
    s = games[in_game[user_id]].tbl[user_id].print_hand()
    await session.send(s)
    return