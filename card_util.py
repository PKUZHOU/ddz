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
    return [[i] for i in poker.keys()]

def get_yidui(poker):
    #获得可以打的一对
    yidui = []
    for i in poker.keys():
        if poker[i]>=2 and i not in[16,17]: #忽略大小王
            yidui.append([i,i])
    return yidui

def get_danshun(poker):
    #获得可以打的单顺
    danshun = []
    keys = poker.keys()
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
    keys = []
    for key in poker.keys(): #找出所有不少于3张的放入keys[]中
        if poker[key] >= 3:
            keys.append(key)
    for key in keys:
        sandai.append([key,key,key])#三不带
        for other_key in poker.keys():
            if other_key !=key:
                sandai.append([key,key,key,other_key]) #三带一
        for other_key in poker.keys():
            if other_key !=key:
                if poker[other_key]>=2:
                    sandai.append([key,key,key,other_key,other_key])#三带2
    return sandai

def get_sidaier(poker):
    #获得四带二
    sidaier = []
    keys = []
    for key in poker.keys():
        if poker[key] >= 4:
            keys.append(key)

    for key in keys:
        for i in poker.keys():
            for j in poker.keys()[poker.keys().index(i):]:
                if i!=j and i!=key and j!=key: #带的两只不能一样
                    sidaier.append([key,key,key,key,i,j])#四个带两只
    for key in keys:
        for i in poker.keys():
            for j in poker.keys()[poker.keys().index(i):]:
                if poker[i] >=2 and poker[j]>=2:
                    if i!=key and j!=key and i!=j:
                        sidaier.append([key,key,key,key,i,i,j,j])#四个带两对
    return sidaier

def get_feiji(poker):
    #获取所有的飞机
    feiji = []
    keys = []#所有三条的keys
    for key in poker.keys():
        if poker[key] >= 3 and key!=15: #三条部分不能为2
            keys.append(key)
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
                feiji.append(temp)
                other_keys = list( set(poker.keys())-set(range(j,i+j)))#除去飞机前面的key

                if(len(other_keys)>=i and (4*i<=20)): #剩下的单牌可以每个飞机带一个,而且总牌数不超过20
                    xiaoyis = list(combinations(other_keys,i)) #选i个单牌
                    for xiaoyi in xiaoyis:
                        feiji.append(temp+list(xiaoyi)) #飞机带小翼

                other_keys_double = []
                for other_key in other_keys:
                    if poker[other_key]>=2:
                        other_keys_double.append(other_key)
                if len(other_keys_double)>=i and (5*i<=20):#剩下的双牌数可以每个飞机带个,而且总牌数不超过20
                    dayis = list(combinations(other_keys_double,i))
                    for dayi in dayis:
                        list_dayi = []
                        for d in dayi:
                            list_dayi+=[d,d]
                        feiji.append(temp+list_dayi)#飞机带大翼
    return feiji
def get_hangtianfeiji(poker):
    hangtianfeiji = []
    keys = []
    for key in poker.keys():
        if poker[key]>=4 and key!=15:
            keys.append(key)
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
                hangtianfeiji.append(temp)
                other_keys = list( set(poker.keys())-set(range(j,i+j)))#除去飞机前面的key
                if len(other_keys)>=i and (6*i<=20):
                    xiaoyis = list(combinations(other_keys,i*2))
                    for xiaoyi in xiaoyis:
                        hangtianfeiji.append(temp+list(xiaoyi)) #飞机带小翼

                other_keys_double = []
                for other_key in other_keys:
                    if poker[other_key]>=2:
                        other_keys_double.append(other_key)
                if len(other_keys_double)>=i and (8*i<=20):
                    dayis = list(combinations(other_keys_double,i*2))
                    for dayi in dayis:
                        list_dayi = []
                        for d in dayi:
                            list_dayi+=[d,d]
                        hangtianfeiji.append(temp+list_dayi)#飞机带大翼
    return hangtianfeiji




def partition(poker,if_ordinary):
    
    if (not if_ordinary):
        poker = sorted(ordinalTransfer(poker))
    poker_counts = Counter(poker)
    danzhang = get_danzhang(poker_counts)
    yidui = get_yidui(poker_counts)
    danshun = get_danshun(poker_counts)
    shuangshun = get_shuangshun(poker_counts)
    sandai = get_sandai(poker_counts)
    sidaier = get_sidaier(poker_counts)
    feiji =  get_feiji(poker_counts)
    hangtianfeiji = get_hangtianfeiji(poker_counts)
    print ("poker",poker)
    print ("danzhang",danzhang)
    print ("yidui",yidui)
    print ("danshun",danshun)
    print ("shuangshun",shuangshun)
    print ("sandai",sandai)
    print ("sidaier",sidaier)
    print ("feiji",feiji)
    print ("hangtianfeiji",hangtianfeiji)
    return poker


if __name__ == '__main__':
    poker = [3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,1,2,7,8]
    #poker = range(20)
    time1 = time.time()
    new = partition(poker,True)
    time1 = time.time()-time1
    print(time1)


