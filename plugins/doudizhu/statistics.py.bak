# -*- coding: utf-8 -*-

import pickle

pk_file = 'temp/stat.pk'

class Stat:
    def __init__(self, user_id):
        self.user_id = user_id
        self.count = [0] * 2
        self.win = [0] * 2
    
    def __str__(self):
        s = '游戏局数：%d  胜利局数：%d  胜率：%.2f%%\n' % \
            (sum(self.count), sum(self.win), sum(self.win) / sum(self.count) * 100)
        s += '地主局数：%d  农民局数：%d  地主选取率：%.2f%%' % \
            (self.count[1], self.count[0], self.count[1] / sum(self.count) * 100)
        return s

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
        pass
    else:
        stat_tbl = pickle.load(f)
        f.close()

def add(user_id, is_dizhu : bool, win : bool):
    global stat_tbl

    if not stat_tbl:
        load_stat()

    if not user_id in stat_tbl:
        stat_tbl[user_id] = Stat(user_id)
    
    stat_tbl[user_id].count[is_dizhu] += 1
    if win:
        stat_tbl[user_id].win[is_dizhu] += 1

    save_stat()

def query(user_id):
    global stat_tbl
    if not stat_tbl:
        load_stat()

    if user_id in stat_tbl:
        return str(stat_tbl[user_id])
    return ''

def clear(user_id):
    global stat_tbl

    stat_tbl.clear()
    save_stat()