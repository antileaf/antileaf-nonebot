# -*- coding: utf-8 -*-  

import nonebot
from nonebot import on_command, CommandSession
from nonebot import permission as perm
from nonebot import message
from nonebot.message import MessageSegment as ms

from random import randint, choice

tbl = (
    ('斑点', '泡普卡', '米格鲁', '卡缇', '安塞尔', '芙蓉', '芬', '翎羽', '香草', '炎熔', '史都华德', '空爆', '安德切尔', '克洛丝', '玫兰莎', '月见夜', '梓兰'), #3*
    ('豆苗', '松果', '杰克', '泡泡', '芳汀', '酸糖', '孑', '卡达', '波登可', '刻刀', '宴', '安比尔', '梅', '红云', '桃金娘', '苏苏洛', '格雷伊', '蛇屠箱', '角峰', '古米', '嘉维尔', '调香师', '末药', '红豆', '讯使', '清道夫', '远山', '夜烟', '杰西卡', '流星', '白雪', '猎蜂', '慕斯', '霜叶', '缠丸', '杜宾', '深海色', '地灵', '阿消', '暗索', '砾'), #4*
    ('熔泉', '暴雨', '乌有', '爱丽丝', '罗宾', '卡夫卡', '絮雨', '奥斯塔', '鞭刃', '四月', '燧石', '特米米', '安哲拉', '贾维', '蜜蜡', '断崖', '亚叶', '莱恩哈特', '苦艾', '月禾', '石棉', '极境', '巫恋', '铸铁', '慑砂', '惊蛰', '吽', '雪雉', '灰喉', '苇草', '布洛卡', '槐琥', '送葬人', '星极', '格劳克斯', '诗怀雅', '可颂', '临光', '雷蛇', '华法琳', '白面鸮', '赫默', '德克萨斯', '凛冬', '夜魔', '天火', '蓝毒', '守林人', '白金', '普罗旺斯', '陨星', '幽灵鲨', '拉普兰德', '芙兰卡', '初雪', '真理', '空', '梅尔', '食铁兽', '狮蝎', '崖心', '红'), #5*
    ('浊心斯卡蒂', '凯尔希', '异客', '嵯峨', '空弦', '山', '泥岩', '瑕光', '史尔特尔', '森蚺', '棘刺', '铃兰', '早露', '温蒂', '傀影', '风笛', '刻俄柏', '阿', '煌', '莫斯提马', '麦哲伦', '赫拉格', '黑', '陈', '塞雷娅', '星熊', '夜莺', '闪灵', '伊芙利特', '艾雅法拉', '斯卡蒂', '推进之王', '能天使', '银灰', '安洁莉娜') #6
)

@on_command('十连', aliases = ('抽卡'), only_to_me = False, permission = perm.EVERYBODY)
async def shilian(session):

    v = []
    while not v or v == [0] * 10:
        v = []

        for i in range(10):
            x = randint(1, 100)
            if x <= 2:
                v.append(3)
            elif x <= 10:
                v.append(2)
            elif x <= 58:
                v.append(1)
            else:
                v.append(0)
    
    s = '你抽到了：'
    for i in v:
        s = s + '\n[%d星] %s' % (i + 3, choice(tbl[i]))
    
    if session.event.group_id:
        s = ms.at(session.event.user_id) + ' ' + s

    await session.send(s)
