# -*- coding: utf-8 -*-

import pickle, math

pk_file = 'temp/doudizhu.pk'

INITIAL_MMR = 2000

# def get_pkfile(group_id : int):
#     return 'temp/doudizhu/%d.pk' % group_id

class Stat:
    def __init__(self, name : str):
        # self.user_id = user_id
        self.name = name
        self.mmr = INITIAL_MMR

        self.count = [0] * 2
        self.win = [0] * 2
    
    def __str__(self):
        s = '游戏局数：%d  胜利局数：%d  胜率：%.2f%%\n' % \
            (sum(self.count), sum(self.win), sum(self.win) / sum(self.count) * 100)
        s += '地主局数：%d  农民局数：%d  地主选取率：%.2f%%' % \
            (self.count[1], self.count[0], self.count[1] / sum(self.count) * 100)
        return s
    
    def exist(self):
        return bool(sum(self.count))

stat_tbl = dict()

def save_stat():
    f = open(pk_file, 'wb')
    pickle.dump(stat_tbl, f)
    f.close()

def load_stat():
    global stat_tbl
    
    try:
        f = open(pk_file, 'rb')
    except:
        stat_tbl = dict()
    else:
        stat_tbl = pickle.load(f)
        f.close()

def check_user(group_id : int, user_id : int):
    return group_id in stat_tbl and user_id in stat_tbl[group_id]

def check_exist(group_id : int, user_id : int):
    return check_user(group_id, user_id) and stat_tbl[group_id][user_id].exist()

def create_user(group_id : int, user_id : int, name : str):
    global stat_tbl

    if not group_id in stat_tbl:
        stat_tbl[group_id] = dict()
    
    stat_tbl[group_id][user_id] = Stat(name)

    save_stat()

def change_name(group_id : int, user_id : int, name : str):
    global stat_tbl

    assert check_user(group_id, user_id)
    
    stat_tbl[group_id][user_id].name = name

    save_stat()

def change_mmr(group_id : int, user_id : int, new_mmr : int, save = True): # change MMR manually
    global stat_tbl

    assert check_user(group_id, user_id)

    stat_tbl[group_id][user_id].mmr = new_mmr

    if save:
        save_stat()


def update(group_id : int, user_id : int, is_dizhu : bool, win : bool, save = True):
    global stat_tbl

    assert check_user(group_id, user_id)
    
    stat_tbl[group_id][user_id].count[is_dizhu] += 1
    if win:
        stat_tbl[group_id][user_id].win[is_dizhu] += 1

    if save:
        save_stat()

def get_mmr(group_id : int, user_id : int):
    if not check_user(group_id, user_id):
        return None
    
    return stat_tbl[group_id][user_id].mmr

def get_stat(group_id : int, user_id : int):
    if not check_exist(group_id, user_id):
        return None
    
    return str(stat_tbl[group_id][user_id])

def del_user(group_id : int, user_id : int):
    if not check_user(group_id, user_id):
        return False
    
    global stat_tbl
    stat_tbl[group_id].remove(user_id)

    save_stat()

    return True

def clear_group(group_id : int):
    global stat_tbl

    if not group_id in stat_tbl:
        return
    
    for u in stat_tbl[group_id]:
        stat_tbl[group_id][u] = Stat(stat_tbl[group_id][u].name)
    
    save_stat()

def get_userid(group_id : int, s : str):
    global stat_tbl

    if not group_id in stat_tbl:
        stat_tbl[group_id] = dict()
        
        save_stat()
    
    tbl = stat_tbl[group_id]

    for u in tbl:
        if str(u) == s or '[CQ:at,qq=%d]' % u == s:
            return u
        
    for u in tbl:
        if tbl[u].name == s:
            return u
    
    flag = False
    userid = 0

    for u in tbl:
        if s in tbl[u].name:
            if flag:
                return -1
            
            flag = True
            userid = u
    
    return userid

def get_name(group_id : int, user_id : int):
    assert check_user(group_id, user_id)

    return stat_tbl[group_id][user_id].name

def get_ranklist(group_id : int):
    if not group_id in stat_tbl:
        return []
    
    tbl = stat_tbl[group_id]
    a = []

    for i in tbl:
        if tbl[i].exist():
            a.append((i, tbl[i].name, tbl[i].mmr))
    
    a.sort(key = lambda x : -x[-1])
    return a

# ---------- calculate MMR ----------

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def calc(x):
    return sigmoid(x / 500) * 2 + 1

def calc_delta(group_id, players : list, master : int, won : bool, score):
    a = dict()

    average = 0

    for i in players:
        # assert check_user(group_id, user_id)

        a[i] = stat_tbl[group_id][i].mmr
        average += a[i]
    
    average /= 3

    delta = dict()
    sc = int((math.log2(score / 10) + 3) * 40 / 3)

    for i in players:
        delta[i] = sc * (1 + int(i == master))

        if (i == master) == won:
            delta[i] *= calc(average - a[i])
        else:
            delta[i] *= -calc(a[i] - average)
        
        delta[i] = int(delta[i] + 0.5) + 10 # 15有点太多了，为减轻通货膨胀改为10分
    
    return delta