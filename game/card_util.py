#coding=utf-8
import random
from collections import Counter
from itertools import combinations
import time
# 红桃 方块 黑桃 草花
# 3 4 5 6 7 8 9 10 J Q K A 2 joker & Joker
# (0-h3 1-d3 2-s3 3-c3) (4-h4 5-d4 6-s4 7-c4) …… 52-小王->16 53-大王->17

def ordinalTransfer(poker): 
    #把0-53 表示方式变成 牌面数字的表示方式，忽略花色。
    newPoker = [int(i / 4) + 3 for i in poker if i <= 52]
    if 53 in poker:
        newPoker += [17]
    return newPoker

#以下的分析函数输入都是字典，key为牌面大小，value 为该大小的牌数。

def get_danzhang(poker):
    # 获得可以打的单张
    return [[i] for i in sorted(poker.keys())]

def get_yidui(poker):
    #获得可以打的一对
    yidui = []
    for i in sorted(poker.keys()):
        if poker[i]>=2 and i not in[16,17]: #忽略大小王
            yidui.append([i,i])
    return yidui

def get_danshun(poker):
    #获得可以打的单顺
    danshun = []
    keys = sorted(poker.keys())
    for i in range(5,13): #顺子可能的总长度
        for j in range(3,16):#顺子第一张牌的大小
            flag = True
            for k in range(i):
                if not j+k in keys:#从j开始遍历i张，看是不是都有
                    flag = False
            if flag == True:
                danshun.append([x+j for x in range(i) ])
    return danshun

def get_shuangshun(poker):
    #获得双顺
    shuangshun = []
    keys = []
    for key in poker.keys():
        if key!=15 and poker[key]>=2: #不能有2 而且牌数不少于2张，结果放入kes[] 中
            keys.append(key)

    sorted(keys)
    for i in range(3, 11): #双顺可能的总长度 (6-20)
        for j in range(3, 16):#从3开始找i张
            flag = True
            for k in range(i):
                if not j + k in keys:
                    flag = False
            if flag == True:
                temp = []
                for x in range(i):
                    temp+=[x+j,x+j]
                shuangshun.append(temp)
    return shuangshun
def get_sandai(poker):
    #找出三带
    sandai = []
    sandaiyi = []
    sandaier = []
    keys = []
    for key in poker.keys(): #找出所有不少于3张的放入keys[]中
        if poker[key] >= 3:
            keys.append(key)
    sorted(keys)
    poker_keys = sorted(poker.keys())
    for key in keys:
        sandai.append([key,key,key])#三不带
        for other_key in  poker_keys:
            if other_key !=key:
                sandaiyi.append([key,key,key,other_key]) #三带一
        for other_key in  poker_keys:
            if other_key !=key:
                if poker[other_key]>=2:
                    sandaier.append([key,key,key,other_key,other_key])#三带2
    return sandai,sandaiyi,sandaier


def get_sidaier(poker):
    #获得四带二
    liangzhi = []
    liangdui = []
    keys = []
    for key in poker.keys():
        if poker[key] >= 4:
            keys.append(key)
    sorted(keys)
    poker_keys = sorted(poker.keys())
    for key in keys:
        for i in poker_keys:
            for j in list(poker_keys)[list(poker_keys).index(i):]:
                if i!=j and i!=key and j!=key: #带的两只不能一样
                    liangzhi.append([key,key,key,key,i,j])#四个带两只
    for key in keys:
        for i in poker_keys:
            for j in poker_keys[poker_keys.index(i):]:
                if poker[i] >=2 and poker[j]>=2:
                    if i!=key and j!=key and i!=j:
                        liangdui.append([key,key,key,key,i,i,j,j])#四个带两对
    return liangzhi,liangdui

def get_feiji(poker):
    #获取所有的飞机
    budaiyi = []
    daixiaoyi = []
    daidayi = []
    keys = []#所有三条的keys
    for key in poker.keys():
        if poker[key] >= 3 and key!=15: #三条部分不能为2
            keys.append(key)
    sorted(keys)
    for i in range(2, 7): #飞机数 2-6
        for j in range(3, 16): #从3开始遍历
            flag = True
            for k in range(i):
                if not j + k in keys:
                    flag = False
            if flag == True:
                temp = []
                for x in range(i):
                    temp+=[x+j,x+j,x+j] #飞机不带翼
                budaiyi.append(temp)
                other_keys = sorted(list( set(poker.keys())-set(range(j,i+j))))#除去飞机前面的key

                if(len(other_keys)>=i and (4*i<=20)): #剩下的单牌可以每个飞机带一个,而且总牌数不超过20
                    xiaoyis = list(combinations(other_keys,i)) #选i个单牌
                    sorted(xiaoyis)
                    for xiaoyi in xiaoyis:
                        daixiaoyi.append(temp+list(xiaoyi)) #飞机带小翼

                other_keys_double = []
                for other_key in other_keys:
                    if poker[other_key]>=2:
                        other_keys_double.append(other_key)
                if len(other_keys_double)>=i and (5*i<=20):#剩下的双牌数可以每个飞机带个,而且总牌数不超过20
                    dayis = list(combinations(other_keys_double,i))
                    for dayi in dayis:
                        list_dayi = []
                        sorted(dayi)
                        for d in dayi:
                            list_dayi+=[d,d]

                        daidayi.append(temp+list_dayi)#飞机带大翼
    return budaiyi,daixiaoyi,daidayi
def get_hangtianfeiji(poker):
    budaiyi = []
    daixiaoyi = []
    daidayi = []
    keys = []
    for key in poker.keys():
        if poker[key]>=4 and key!=15:
            keys.append(key)
    sorted(keys)
    for i in range(2,6): #飞机数2-5
        for j in range(3,16):
            flag = True
            for k in range(i):
                if not j + k in keys:
                    flag = False
            if flag == True:
                temp = []
                for x in range(i):
                    temp+=[x+j,x+j,x+j,x+j] #航天飞机不带翼
                budaiyi.append(temp)
                other_keys = list( set(poker.keys())-set(range(j,i+j)))#除去飞机前面的key
                if len(other_keys)>=i and (6*i<=20):
                    xiaoyis = list(combinations(other_keys,i*2))
                    sorted(xiaoyis)
                    for xiaoyi in xiaoyis:
                        daixiaoyi.append(temp+list(xiaoyi)) #飞机带小翼

                other_keys_double = []
                for other_key in other_keys:
                    if poker[other_key]>=2:
                        other_keys_double.append(other_key)
                if len(other_keys_double)>=i and (8*i<=20):
                    dayis = list(combinations(other_keys_double,i*2))
                    for dayi in dayis:
                        list_dayi = []
                        sorted(dayi)
                        for d in dayi:
                            list_dayi+=[d,d]

                        daidayi.append(temp+list_dayi)#飞机带大翼
    return budaiyi,daixiaoyi,daidayi

def get_zhadan(poker):
    zhadan = []
    keys = []
    for key in poker.keys():
        if poker[key]>=4:
            keys.append(key)
    sorted(keys)
    for key in keys:
        zhadan.append([key,key,key,key])

    return zhadan


def get_huojian(poker):
    if 16 in poker.keys() and 17 in poker.keys():
        return [[16,17]]
    else:
        return []
def partition(poker,if_ordinary):
    if (not if_ordinary):
        poker = sorted(ordinalTransfer(poker))
    poker_counts = Counter(poker)
    # sorted(poker_counts.keys())
    # sorted(poker_counts.items(),key = lambda item:item[1])
    danzhang = get_danzhang(poker_counts)
    yidui = get_yidui(poker_counts)
    danshun = get_danshun(poker_counts)
    shuangshun = get_shuangshun(poker_counts)
    sanbudai,sandaiyi,sandaier = get_sandai(poker_counts)
    sidaierzhi,sidaierdui = get_sidaier(poker_counts)
    feiji,feijidaixiaoyi,feijidaidayi =  get_feiji(poker_counts)
    hangtianfeiji,htfjdaixiaoyi,htfjdaidayi = get_hangtianfeiji(poker_counts)
    zhadan = get_zhadan(poker_counts)
    huojian = get_huojian(poker_counts)
    # print ("poker",   len(poker))
    # print ("danzhang",  len(danzhang))
    # print ("yidui",     len(yidui))
    # print ("danshun",   len(danshun))
    # print ("shuangshun",len(shuangshun))
    # print ("sanbudai",    len(sanbudai))
    # print ("sandaiyi",    len(sandaiyi))
    # print ("sandaier",    len(sandaier))
    # print ("sidaierzhi",   len(sidaierzhi))
    # print ("sidaierdui",   len(sidaierdui))
    # print ("feijibudaiyi",     len(feiji))
    # print ("feijidaixiaoyi",   len(feijidaixiaoyi))
    # print ("feijidaidayi", len(feijidaidayi))
    # print ("hangtianfeiji",len(hangtianfeiji))
    # print ("zhadan",len(zhadan))
    # print ("huojian",len(huojian))
    total = (danzhang+yidui+danshun+shuangshun+sanbudai+sandaiyi+sandaier+sidaierzhi+sidaierdui+feiji+feijidaixiaoyi+feijidaidayi+hangtianfeiji+htfjdaixiaoyi+htfjdaidayi+zhadan+huojian)
    return total

def get_moves(poker,if_ordinary):
    if (not if_ordinary):
        poker = sorted(ordinalTransfer(poker))
    poker_counts = Counter(poker)
    danzhang = get_danzhang(poker_counts)
    yidui = get_yidui(poker_counts)
    danshun = get_danshun(poker_counts)
    shuangshun = get_shuangshun(poker_counts)
    sanbudai,sandaiyi,sandaier = get_sandai(poker_counts)
    sidaierzhi,sidaierdui = get_sidaier(poker_counts)
    feiji,feijidaixiaoyi,feijidaidayi =  get_feiji(poker_counts)
    hangtianfeiji,htfjdaixiaoyi,htfjdaidayi = get_hangtianfeiji(poker_counts)
    zhadan = get_zhadan(poker_counts)
    huojian = get_huojian(poker_counts)
    return danzhang,yidui,danshun,shuangshun,sanbudai,sandaiyi,sandaier,sidaierzhi,sidaierdui,feiji,feijidaixiaoyi,feijidaidayi,hangtianfeiji,htfjdaixiaoyi,htfjdaidayi,zhadan,huojian

def to_str(poker_list):
    s = []
    for poker in poker_list:
        s.append(str(poker))
    return s

def get_action_dic():
    poker = range(54)
    new = partition(poker,False)
    dictionary = dict(zip(to_str(new),range(len(new))))
    return dictionary
if __name__ == '__main__':
    # poker = range(54)
    #poker = range(20)
    poker = [3,3,3,3,17,4]
    time1 = time.time()
    new = partition(poker,True)
    dictionary = dict(zip(to_str(new),range(len(new))))
   #print(dictionary)
    time1 = time.time()-time1
    print(time1)


