# -*- coding: utf-8 -*-  

from nonebot import on_command, CommandSession
from nonebot import permission as perm
# from nonebot import message
from nonebot.message import MessageSegment as ms

import time, random, datetime

from plugins.tools import local_image

major_tarot = [
    ('愚者', 'The Fool', ('憧憬自然的地方、毫无目的地前行、喜欢尝试挑战新鲜事物、四处流浪', '冒险的行动，追求可能性，重视梦想，无视物质的损失，离开家园，过于信赖别人，为出外旅行而烦恼')),
    ('魔术师', 'The Magician', ('事情的开始，行动的改变，熟练的技术及技巧，贯彻自我意志，运用自然的力量来达到野心', '意志力薄弱，起头难，走入错误的方向，知识不足，被骗和失败')),
    ('女祭司', 'The High Priestess', ('开发出内在的神秘潜力，前途将有所变化的预言，深刻地思考，敏锐的洞察力，准确的直觉', '洁癖，无知，贪心，目光短浅，自尊心过高，偏差的判断，有勇无谋，自命不凡')),
    ('皇后', 'The Empress', ('幸福，成功，收获，无忧无虑，圆满的家庭生活，良好的环境，美貌，艺术，与大自然接触，愉快的旅行，休闲', '不活泼，缺乏上进心，散漫的生活习惯，无法解决的事情，不能看到成果，担于享乐，环境险恶，与家人发生纠纷')),
    ('皇帝', 'The Emperor', ('光荣，权力，胜利，握有领导权，坚强的意志，达成目标，父亲的责任，精神上的孤单', '幼稚，无力，独裁，撒娇任性，平凡，没有自信，行动力不足，意志薄弱，被支配')),
    ('教皇', 'The Hierophant', ('援助，同情，宽宏大量，可信任的人给予的劝告，良好的商量对象，得到精神上的满足，遵守规则，志愿者', '错误的讯息，恶意的规劝，上当，援助被中断，愿望无法达成，被人利用，被放弃')),
    ('恋人', 'The Lovers', ('撮合，爱情，流行，兴趣，充满希望的未来，魅力，增加朋友', '禁不起诱惑，纵欲过度，反覆无常，友情变淡，厌倦，争吵，华丽的打扮，优柔寡断')),
    ('战车', 'The Chariot', ('努力而获得成功，胜利，克服障碍，行动力，自立，尝试，自我主张，年轻男子，交通工具，旅行运大吉', '争论失败，发生纠纷，阻滞，违返规则，诉诸暴力，顽固的男子，突然的失败，不良少年，挫折和自私自利')),
    ('力量', 'Strength', ('大胆的行动，有勇气的决断，新发展，大转机，异动，以意志力战胜困难，健壮的女人', '胆小，输给强者，经不起诱惑，屈服在权威与常识之下，没有实践便告放弃，虚荣，懦弱，没有耐性')),
    ('隐者', 'The Hermit', ('隐藏的事实，个别的行动，倾听他人的意见，享受孤独，有益的警戒，年长者，避开危险，祖父，乡间生活', '无视警告，憎恨孤独，自卑，担心，幼稚思想，过于慎重导致失败，偏差，不宜旅行')),
    ('命运之轮', 'Wheel of Fortune', ('关键性的事件，新的机会，新的潮流，环境的变化，幸运的开端，状况好转，问题解决，幸运之神降临', '挫折，计划泡汤，障碍，无法修正方向，往坏处发展，恶性循环，中断')),
    ('正义', 'Justice', ('公正、中立、诚实、心胸坦荡、表里如一、身兼二职、追求合理化、协调者、与法律有关、光明正大的交往、感情和睦', '失衡、偏见、纷扰、诉讼、独断专行、问心有愧、无法两全、表里不一、男女性格不合、情感波折、无视社会道德的恋情')),
    ('倒吊人', 'The Hanged Man', ('接受考验、行动受限、牺牲、不畏艰辛、不受利诱、有失必有得、吸取经验教训、浴火重生、广泛学习、奉献的爱', '无谓的牺牲、骨折、厄运、不够努力、处于劣势、任性、利己主义者、缺乏耐心、受惩罚、逃避爱情、没有结果的恋情')),
    ('死神', 'Death', ('失败、接近毁灭、生病、失业、维持停滞状态、持续的损害、交易停止、枯燥的生活、别离、重新开始、双方有很深的鸿沟、恋情终止', '抱有一线希望、起死回生、回心转意、摆脱低迷状态、挽回名誉、身体康复、突然改变计划、逃避现实、斩断情丝、与旧情人相逢')),
    ('节制', 'Temperance', ('单纯、调整、平顺、互惠互利、好感转为爱意、纯爱、深爱', '消耗、下降、疲劳、损失、不安、不融洽、爱情的配合度不佳')),
    ('恶魔', 'The Devil', ('被束缚、堕落、生病、恶意、屈服、欲望的俘虏、不可抗拒的诱惑、颓废的生活、举债度日、不可告人的秘密、私密恋情', '逃离拘束、解除困扰、治愈病痛、告别过去、暂停、别离、拒绝诱惑、舍弃私欲、别离时刻、爱恨交加的恋情')),
    ('塔', 'The Tower', ('破产、逆境、被开除、突然患病、致命的打击、巨大的变动、受牵连、信念崩溃、玩火自焚、纷扰不断、突然分离，破灭的爱', '困境、内讧、紧迫的状态、状况不佳、趋于稳定、骄傲自大将付出代价、背水一战、分离的预感、爱情危机')),
    ('星星', 'The Star', ('前途光明、充满希望、想象力、创造力、幻想、满足愿望、水准提高、理想的对象、美好的恋情', '挫折、失望、好高骛远、异想天开、仓皇失措、事与愿违、工作不顺心、情况悲观、秘密恋情、缺少爱的生活')),
    ('月亮', 'The Moon', ('不安、迷惑、动摇、谎言、欺骗、鬼迷心窍、动荡的爱、三角关系', '逃脱骗局、解除误会、状况好转、预知危险、等待、正视爱情的裂缝')),
    ('太阳', 'The Sun', ('活跃、丰富的生命力、充满生机、精力充沛、工作顺利、贵人相助、幸福的婚姻、健康的交际', '消沉、体力不佳、缺乏连续性、意气消沉、生活不安、人际关系不好、感情波动、离婚')),
    ('审判', 'Judgement', ('复活的喜悦、康复、坦白、好消息、好运气、初露锋芒、复苏的爱、重逢、爱的奇迹', '一蹶不振、幻灭、隐瞒、坏消息、无法决定、缺少目标、没有进展、消除、恋恋不舍')),
    ('世界', 'The World', ('完成、成功、完美无缺、连续不断、精神亢奋、拥有毕生奋斗的目标、完成使命、幸运降临、快乐的结束、模范情侣', '未完成、失败、准备不足、盲目接受、一时不顺利、半途而废、精神颓废、饱和状态、合谋、态度不够融洽、感情受挫'))
]

def calc(x, z):
    z = abs(z)
    y = (datetime.date.today() - datetime.date(2000, 1, 1)).days
    return (x ^ y ^ z) + (pow(x, y, 1000000007) ^ pow(y, x, 998244353) ^ pow(z, x, 1000000007) ^ pow(y, z, 1000000007))

@on_command('tarot', aliases = ('塔罗牌', '占卜', '单张塔罗牌'), only_to_me = False, permission = perm.GROUP)
async def single_tarot(session):
    user_id = int(session.event['user_id'])

    i = calc(user_id, session.state['hash']) % (2 * len(major_tarot))
    j, i = int(i >= len(major_tarot)), i % len(major_tarot)

    s = '你抽到了： %d %s %s %s\n' % (i, *major_tarot[i][:2], ('正位', '逆位')[j])

    s = s + local_image('tarot/%s.png' % major_tarot[i][1]) + '\n'

    s = s + '释义：%s' % major_tarot[i][2][j]

    if session.state['text']:
        s = '占卜事项：' + session.state['text'] + '\n' + s
    if session.event.group_id:
        s = ms.at(user_id) + ' ' + s

    await session.send(s)

@single_tarot.args_parser
async def single_tarot_parser(session):
    s = session.current_arg_text.strip()
    session.state['text'] = s
    session.state['hash'] = hash(s)


@on_command('检定', aliases = ('check', 'dice'), only_to_me = False, permission = perm.GROUP)
async def check(session):
    user_id = int(session.event['user_id'])

    s = ''

    if 'bad' in session.state:
        s = ms.at(user_id) + ' 参数格式：ndm，表示投掷n枚有m面的骰子，例如2d6表示投掷2枚立方体骰子'
    
    else:
        if session.state['n'] > 1000000:
            await session.send(ms.at(user_id) + '李在赣神魔')
            return
        if session.state['m'] < 1 or session.state['m'] > 1000000000:
            await session.send(ms.at(user_id) + '能不能整点阳间骰子')
            return

        s = '投掷结果：'
        a = []

        for i in range(session.state['n']):
            if i:
                s = s + ' '
            a.append(random.randint(1, session.state['m']))
            s = s + str(a[-1])

        if session.state['n'] > 1 and session.state['n'] <= 10:
            if session.event.group_id:
                s = ms.at(user_id) + '\n' + s
            s = s + '\n总和：' + str(sum(a))
        else:
            if session.state['n'] > 10:
                s = '总和：' + str(sum(a))
            if session.event.group_id:
                s = ms.at(user_id) + ' ' + s

    await session.send(s)

@check.args_parser
async def check_parser(session):
    s = session.current_arg_text.strip()

    a = s.split('d')
    if len(a) != 2:
        session.state['bad'] = True
    
    try:
        a = map(int, a)
        session.state['n'], session.state['m'] = a
    except:
        session.state['bad'] = True
    