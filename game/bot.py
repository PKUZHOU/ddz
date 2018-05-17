#coding=utf-8
import random
import math
import json

# 红桃 方块 黑桃 草花
# 3 4 5 6 7 8 9 10 J Q K A 2 joker & Joker
# (0-h3 1-d3 2-s3 3-c3) (4-h4 5-d4 6-s4 7-c4) …… 52-小王->16 53-大王->17

def get_bot_response(input):
    full_input = input.copy()
    my_history = full_input["responses"]
    use_info = full_input["requests"][0]
    poker, history, publiccard = use_info["own"], use_info["history"], use_info["publiccard"]
    last_history = full_input["requests"][-1]["history"]
    currBotID = 0  # 判断自己是什么身份，地主0 or 农民甲1 or 农民乙2
    if len(history[0]) == 0:
        if len(history[1]) != 0:
            currBotID = 1
    else:
        currBotID = 2
    history = history[2 - currBotID:]

    for i in range(len(my_history)):
        history += [my_history[i]]
        history += full_input["requests"][i + 1]["history"]


    lenHistory = len(history)

    for tmp in my_history:
        for j in tmp:
            try:
                poker.remove(j)
            except:
                pass
    poker.sort()  # 用0-53编号的牌


    def ordinalTransfer(poker):
        newPoker = [int(i / 4) + 3 for i in poker if i <= 52]
        if 53 in poker:
            newPoker += [17]
        return newPoker


    def transferOrdinal(subPoker, newPoker, poker):
        singlePoker, res = list(set(subPoker)), []
        singlePoker.sort()
        for i in range(len(singlePoker)):
            tmp = singlePoker[i]
            idx = newPoker.index(tmp)
            num = subPoker.count(tmp)
            res += [poker[idx + i] for i in range(num)]
        return res


    def separate(poker):  # 拆分手牌牌型并组成基本牌集合，返回的只是点数
        res = []
        if len(poker) == 0:
            return res
        myPoker = [i for i in poker]
        newPoker = ordinalTransfer(myPoker)
        if 16 in newPoker and 17 in newPoker:  # 单独列出火箭
            newPoker = newPoker[:-2]
            res += [[16, 17]]
        elif 16 in newPoker:
            newPoker = newPoker[:-1]
            res += [[16]]
        elif 17 in newPoker:
            newPoker = newPoker[:-1]
            res += [[17]]

        singlePoker = list(set(newPoker))  # 都有哪些牌
        singlePoker.sort()

        for i in singlePoker:  # 分出炸弹，其实也可以不分，优化点之一
            if newPoker.count(i) == 4:
                idx = newPoker.index(i)
                res += [newPoker[idx:idx + 4]]
                newPoker = newPoker[0:idx] + newPoker[idx + 4:]

        # 为了简便处理带2的情形，先把2单独提出来
        specialCount, specialRes = 0, []
        if 15 in newPoker:
            specialCount = newPoker.count(15)
            idx = newPoker.index(15)
            specialRes = [15 for i in range(specialCount)]
            newPoker = newPoker[:-specialCount]

        def findSeq(p, dupTime, minLen):  # 这里的p是点数，找最长的顺子，返回值为牌型组合
            resSeq, tmpSeq = [], []
            singleP = list(set(p))
            singleP.sort()
            for curr in singleP:
                if p.count(curr) >= dupTime:
                    if len(tmpSeq) == 0:
                        tmpSeq = [curr]
                        continue
                    elif curr == (tmpSeq[-1] + 1):
                        tmpSeq += [curr]
                        continue
                if len(tmpSeq) >= minLen:
                    tmpSeq = [i for i in tmpSeq for j in range(dupTime)]
                    resSeq += [tmpSeq]
                tmpSeq = []
            return resSeq

        def subSeq(p, subp):  # 一定保证subp是p的子集
            singleP = list(set(subp))
            singleP.sort()
            for curr in singleP:
                idx = p.index(curr)
                countP = subp.count(curr)
                p = p[0:idx] + p[idx + countP:]
            return p

        # 单顺：1，5；双顺：2，3；飞机：3，2；航天飞机：4，2。因为前面已经把炸弹全都提取出来，所以这里就不主动出航天飞机了

        para = [[1, 5], [2, 3], [3, 2]]
        validChoice = [0, 1, 2]
        allSeq = [[], [], []]  # 分别表示单顺、双顺、三顺（飞机不带翼）
        restRes = []
        while (True):  # myPoker，这里会找完所有的最长顺子
            if len(newPoker) == 0 or len(validChoice) == 0:
                break
            dupTime = random.choice(validChoice)
            tmp = para[dupTime]
            newSeq = findSeq(newPoker, tmp[0], tmp[1])
            for tmpSeq in newSeq:
                newPoker = subSeq(newPoker, tmpSeq)
            if len(newSeq) == 0:
                validChoice.remove(dupTime)
            else:
                allSeq[dupTime] += [tmpSeq]
        res += allSeq[0] + allSeq[1]  # 对于单顺和双顺没必要去改变
        plane = allSeq[2]

        allRetail = [[], [], []]  # 分别表示单张，对子，三张
        singlePoker = list(set(newPoker))  # 更新目前为止剩下的牌，newPoker和myPoker是一一对应的
        singlePoker.sort()
        for curr in singlePoker:
            countP = newPoker.count(curr)
            allRetail[countP - 1] += [[curr for i in range(countP)]]

        # 接下来整合有需要的飞机or三张 <-> 单张、对子。这时候的飞机和三张一定不会和单张、对子有重复。
        # 如果和单张有重复，即为炸弹，而这一步已经在前面检测炸弹时被检测出
        # 如果和对子有重复，则同一点数的牌有5张，超出了4张

        # 先整合飞机
        for curr in plane:
            lenKind = int(len(curr) / 3)
            tmp = curr
            for t in range(2):  # 分别试探单张和对子的个数是否足够
                tmpP = allRetail[t]
                if len(tmpP) >= lenKind:
                    tmp += [i[j] for i in tmpP[0:lenKind] for j in range(t + 1)]
                    allRetail[t] = allRetail[t][lenKind:]
                    break
            res += [tmp]

        if specialCount == 3:
            allRetail[2] += [specialRes]
        elif specialCount > 0 and specialCount <= 2:
            allRetail[specialCount - 1] += [specialRes]
        # 之后整合三张
        for curr in allRetail[2]:  # curr = [1,1,1]
            tmp = curr
            for t in range(2):
                tmpP = allRetail[t]
                if len(tmpP) >= 1:
                    tmp += tmpP[0]
                    allRetail[t] = allRetail[t][1:]
                    break
            res += [tmp]

        res += allRetail[0] + allRetail[1]
        return res


    def checkPokerType(poker, hasTransfer):  # poker：list，表示一个人出牌的牌型
        poker.sort()
        lenPoker = len(poker)
        newPoker = [i for i in poker]
        if not hasTransfer:
            newPoker = ordinalTransfer(poker)
        # J,Q,K,A,2-11,12,13,14,15
        # 单张：1 一对：2 三带：零3、一4、二5 单顺：>=5 双顺：>=6
        # 四带二：6、8 飞机：>=6
        typeP, mP, sP = "空", newPoker, []

        for tmp in range(2):
            if tmp == 1:
                return "错误", poker, []  # 没有判断出任何牌型，出错
            if lenPoker == 0:  # 没有牌，也即pass
                break
            if poker == [52, 53]:
                typeP = "火箭"
                break
            if lenPoker == 4 and newPoker.count(newPoker[0]) == 4:
                typeP = "炸弹"
                break
            if lenPoker == 1:
                typeP = "单张"
                break
            if lenPoker == 2:
                if newPoker.count(newPoker[0]) == 2:
                    typeP = "一对"
                    break
                continue

            firstPoker = newPoker[0]

            # 判断是否是单顺
            if lenPoker >= 5 and 15 not in newPoker:
                singleSeq = [firstPoker + i for i in range(lenPoker)]
                if newPoker == singleSeq:
                    typeP = "单顺"
                    break

            # 判断是否是双顺
            if lenPoker >= 6 and lenPoker % 2 == 0 and 15 not in newPoker:
                pairSeq = [firstPoker + i for i in range(int(lenPoker / 2))]
                pairSeq = [j for j in pairSeq for i in range(2)]
                if newPoker == pairSeq:
                    typeP = "双顺"
                    break

            thirdPoker = newPoker[2]
            # 判断是否是三带
            if lenPoker <= 5 and newPoker.count(thirdPoker) == 3:
                mP, sP = [thirdPoker for k in range(3)], [k for k in newPoker if k != thirdPoker]
                if lenPoker == 3:
                    typeP = "三带零"
                    break
                if lenPoker == 4:
                    typeP = "三带一"
                    break
                if lenPoker == 5:
                    typeP = "三带二"
                    if sP[0] == sP[1]:
                        break
                    continue

            if lenPoker < 6:
                continue

            fifthPoker = newPoker[4]
            # 判断是否是四带二
            if lenPoker == 6 and newPoker.count(thirdPoker) == 4:
                typeP, mP = "四带两只", [thirdPoker for k in range(4)]
                sP = [k for k in newPoker if k != thirdPoker]
                if sP[0] != sP[1]:
                    break
                continue
            if lenPoker == 8:
                typeP = "四带两对"
                mP, sP = [], []
                if newPoker.count(thirdPoker) == 4:
                    mP, sP = [thirdPoker for k in range(4)], [k for k in newPoker if k != thirdPoker]
                elif newPoker.count(fifthPoker) == 4:
                    mP, sP = [fifthPoker for k in range(4)], [k for k in newPoker if k != fifthPoker]
                if len(sP) == 4:
                    if sP[0] == sP[1] and sP[2] == sP[3] and sP[0] != sP[2]:
                        break

            # 判断是否是飞机or航天飞机
            singlePoker = list(set(newPoker))  # 表示newPoker中有哪些牌种
            singlePoker.sort()
            mP, sP = newPoker, []
            dupTime = [newPoker.count(i) for i in singlePoker]  # 表示newPoker中每种牌各有几张
            singleDupTime = list(set(dupTime))  # 表示以上牌数的种类
            singleDupTime.sort()

            if len(singleDupTime) == 1 and 15 not in singlePoker:  # 不带翼
                lenSinglePoker, firstSP = len(singlePoker), singlePoker[0]
                tmpSinglePoker = [firstSP + i for i in range(lenSinglePoker)]
                if singlePoker == tmpSinglePoker:
                    if singleDupTime == [3]:  # 飞机不带翼
                        typeP = "飞机不带翼"
                        break
                    if singleDupTime == [4]:  # 航天飞机不带翼
                        typeP = "航天飞机不带翼"
                        break

            def takeApartPoker(singleP, newP):
                m = [i for i in singleP if newP.count(i) >= 3]
                s = [i for i in singleP if newP.count(i) < 3]
                return m, s

            m, s = [], []
            if len(singleDupTime) == 2 and singleDupTime[0] < 3 and singleDupTime[1] >= 3:
                c1, c2 = dupTime.count(singleDupTime[0]), dupTime.count(singleDupTime[1])
                if c1 != c2 and not (c1 == 4 and c2 == 2):  # 带牌的种类数不匹配
                    continue
                m, s = takeApartPoker(singlePoker, newPoker)  # 都是有序的
                if 15 in m:
                    continue
                lenm, firstSP = len(m), m[0]
                tmpm = [firstSP + i for i in range(lenm)]
                if m == tmpm:  # [j for j in pairSeq for i in range(2)]
                    m = [j for j in m for i in range(singleDupTime[1])]
                    s = [j for j in s for i in range(singleDupTime[0])]
                    if singleDupTime[1] == 3:
                        if singleDupTime[0] == 1:
                            typeP = "飞机带小翼"
                            mP, sP = m, s
                            break
                        if singleDupTime[0] == 2:
                            typeP = "飞机带大翼"
                            mP, sP = m, s
                            break
                    elif singleDupTime[1] == 4:
                        if singleDupTime[0] == 1:
                            typeP = "航天飞机带小翼"
                            mP, sP = m, s
                            break
                        if singleDupTime[0] == 2:
                            typeP = "航天飞机带大翼"
                            mP, sP = m, s
                            break

        omP, osP = [], []
        for i in poker:
            tmp = int(i / 4) + 3
            if i == 53:
                tmp = 17
            if tmp in mP:
                omP += [i]
            elif tmp in sP:
                osP += [i]
            else:
                return "错误", poker, []
        return typeP, omP, osP


    def recover(h):  # 只考虑倒数3个，返回最后一个有效牌型及主从牌，且返回之前有几个人选择了pass；id是为了防止某一出牌人在某一牌局后又pass，然后造成连续pass
        typeP, mP, sP, countPass = "空", [], [], 0
        for i in range(-1, -3, -1):
            lastPoker = h[i]
            typeP, mP, sP = checkPokerType(lastPoker, 0)
            if typeP == "空":
                countPass += 1
                continue
            break
        return typeP, mP, sP, countPass


    def searchCard(poker, objType, objMP, objSP):  # 搜索自己有没有大过这些牌的牌
        if objType == "火箭":  # 火箭是最大的牌
            return []
        # poker.sort() # 要求poker是有序的，使得newPoker一般也是有序的
        newPoker = ordinalTransfer(poker)
        singlePoker = list(set(newPoker))  # 都有哪些牌
        singlePoker.sort()
        countPoker = [newPoker.count(i) for i in singlePoker]  # 这些牌都有几张

        res = []
        idx = [[i for i in range(len(countPoker)) if countPoker[i] == k] for k in range(5)]  # 分别有1,2,3,4的牌在singlePoker中的下标
        quadPoker = [singlePoker[i] for i in idx[4]]
        flag = 0
        if len(poker) >= 2:
            if poker[-2] == 52 and poker[-1] == 53:
                flag = 1

        newObjMP, lenObjMP = ordinalTransfer(objMP), len(objMP)

        if objType == "炸弹":
            for curr in quadPoker:
                if curr > newObjMP[0]:
                    res += [[(curr - 3) * 4 + j for j in range(4)]]
            if flag:
                res += [[52, 53]]
            return res

        singleObjMP = list(set(newObjMP))  # singleObjMP为超过一张的牌的点数
        singleObjMP.sort()
        countObjMP, maxObjMP = newObjMP.count(singleObjMP[0]), singleObjMP[-1]
        # countObjMP虽取首元素在ObjMP中的个数，但所有牌count应相同；countObjMP * len(singleObjMP) == lenObjMP

        newObjSP, lenObjSP = ordinalTransfer(objSP), len(objSP)  # 只算点数的对方拥有的主牌; 对方拥有的主牌数
        singleObjSP = list(set(newObjSP))
        singleObjSP.sort()
        countObjSP = 0
        if len(objSP) > 0:  # 有可能没有从牌，从牌的可能性为单张或双张
            countObjSP = newObjSP.count(singleObjSP[0])

        tmpMP, tmpSP = [], []

        for j in range(1, 16 - maxObjMP):
            tmpMP, tmpSP = [i + j for i in singleObjMP], []
            if all([newPoker.count(i) >= countObjMP for i in tmpMP]):  # 找到一个匹配的更大解
                if j == (15 - maxObjMP) and countObjMP != lenObjMP:  # 与顺子有关，则解中不能出现2（15）
                    break
                if lenObjSP != 0:
                    tmpSP = list(set(singlePoker) - set(tmpMP))
                    tmpSP.sort()
                    tmpSP = [i for i in tmpSP if newPoker.count(i) >= countObjSP]  # 作为从牌有很多组合方式，是优化点
                    species = int(lenObjSP / countObjSP)
                    if len(tmpSP) < species:  # 剩余符合从牌特征的牌种数少于目标要求的牌种数，比如334455->lenObjSP=6,countObjSP=2,tmpSP = [8,9]
                        continue
                    tmp = [i for i in tmpSP if newPoker.count(i) == countObjSP]
                    if len(tmp) >= species:  # 剩余符合从牌特征的牌种数少于目标要求的牌种数，比如334455->lenObjSP=6,countObjSP=2,tmpSP = [8,9]
                        tmpSP = tmp
                    tmpSP = tmpSP[0:species]
                tmpRes = []
                idxMP = [newPoker.index(i) for i in tmpMP]
                idxMP = [i + j for i in idxMP for j in range(countObjMP)]
                idxSP = [newPoker.index(i) for i in tmpSP]
                idxSP = [i + j for i in idxSP for j in range(countObjSP)]
                idxAll = idxMP + idxSP
                tmpRes = [poker[i] for i in idxAll]
                res += [tmpRes]

        if objType == "单张":  # 以上情况少了上家出2，本家可出大小王的情况
            if 52 in poker and objMP[0] < 52:
                res += [[52]]
            if 53 in poker:
                res += [[53]]

        for curr in quadPoker:  # 把所有炸弹先放进返回解
            res += [[(curr - 3) * 4 + j for j in range(4)]]
        if flag:
            res += [[52, 53]]
        return res


    lastTypeP, lastMP, lastSP, countPass = recover(last_history)

    everyOneHistory = [[], [], []]
    everyOneLack = [[], [], []]  # 表示三个人都缺少什么牌型
    everyOneRestPokerLen = [20, 17, 17]

    lastTurnTypeP, lenMP, lenSP = "空", 0, 0
    for i in range(lenHistory):
        tmp, tmpID = history[i], i % 3
        everyOneRestPokerLen[tmpID] -= len(tmp)
        everyOneHistory[tmpID] += [tmp]
        typeP, _, _ = checkPokerType(tmp, 0)
        if typeP == "空":  # 说明在这一回合里选了pass，很大几率是因为对方没有这种牌型的牌，在下方随机出牌的时候可以
            everyOneLack[tmpID] += [lastTurnTypeP]
        else:
            lastTurnTypeP = typeP


    def randomOut(poker, everyOneLack, currBotID):  # everyOneRestPokerLen直接看这里！
        sepRes, res, lenPoker = separate(poker), [], len(poker)
        lenRes, idx = len(sepRes), 0
        enemyBotLack, mateBotLack = [], []
        pokerType, score = [], []

        # listLenSepRes, listMinSepRes, listMaxSepRes= [len(i) for i in sepRes], [min(i) for i in sepRes], [max(i) for i in sepRes]

        if currBotID == 0:  # 是地主，需要看两个农民
            enemyBotLack = everyOneLack[1] + everyOneLack[2]
        else:  # 是地主上家，农民2号
            enemyBotLack, mateBotLack = everyOneLack[0], everyOneLack[3 - currBotID]

        for tmp in sepRes:
            typeP, _, _ = checkPokerType(tmp, 1)
            lenTmp, minNum, maxNum = len(tmp), min(tmp), max(tmp)
            tmpScore = 0
            if lenPoker <= 10:  # 手上的牌数很少了
                tmpScore = (17 - minNum) / lenTmp
                if len(sepRes) == 2:
                    tmpScore = minNum * lenTmp
                if typeP in enemyBotLack and typeP in mateBotLack:  # 这种情况基本上是农民了
                    if currBotID == 1:  # 农民1，是地主下家，没事，先随便出
                        tmpScore += 10
                    else:
                        tmpScore += 5
                elif typeP in enemyBotLack:
                    tmpScore += 10
                elif typeP in mateBotLack:
                    tmpScore -= 3
                else:
                    tmpScore -= 1
            else:
                tmpScore = (17 - minNum) * lenTmp
                if typeP in enemyBotLack and typeP in mateBotLack:
                    if currBotID == 1:  # 农民1，是地主下家，没事，先随便出
                        tmpScore += enemyBotLack.count(typeP) + mateBotLack.count(typeP)
                    else:
                        tmpScore += enemyBotLack.count(typeP)
                elif typeP in enemyBotLack:
                    tmpScore += enemyBotLack.count(typeP)
                elif typeP in mateBotLack:
                    tmpScore -= mateBotLack.count(typeP)
            if len(sepRes) == 2:
                if typeP == "炸弹" or typeP == "火箭" or (
                        lenTmp > everyOneRestPokerLen[(currBotID + 1) % 3] and lenTmp > everyOneRestPokerLen[
                    (currBotID + 2) % 3]):
                    tmpScore += 1000
            else:
                if typeP == "炸弹" or typeP == "火箭":
                    tmpScore -= 100
                elif lenTmp > everyOneRestPokerLen[(currBotID + 1) % 3] and lenTmp > everyOneRestPokerLen[
                    (currBotID + 2) % 3]:
                    tmpScore += 2

            if currBotID == 0:  # 是地主，需要看两个农民
                if lenTmp > everyOneRestPokerLen[1] and lenTmp > everyOneRestPokerLen[2]:
                    tmpScore += 5
                elif lenTmp > everyOneRestPokerLen[1] or lenTmp > everyOneRestPokerLen[2]:
                    tmpScore += 2
            else:  # 是农民
                if lenTmp > everyOneRestPokerLen[0]:
                    tmpScore += 5
                else:
                    pass
            score += [tmpScore]
        maxScore = max(score)
        maxScoreIdx = [i for i in range(lenRes) if score[i] == maxScore]
        idx = random.choice(maxScoreIdx)

        # idx = random.randint(0, lenRes-1)
        tmp = sepRes[idx]  # 只包含点数
        newPoker, singleTmp = ordinalTransfer(poker), list(set(tmp))
        singleTmp.sort()
        for curr in singleTmp:
            tmpCount = tmp.count(curr)
            idx = newPoker.index(curr)
            res += [poker[idx + j] for j in range(tmpCount)]
        # tmpCount = newPoker.count(newPoker[0])
        # res = [[poker[i] for i in range(tmpCount)]]
        return res


    if countPass == 2:  # 长度为0，自己是地主，随便出；在此之前已有两个pass，上一个轮是自己占大头，不能pass，否则出错失败
        # 可以考虑出的和上一轮回一样的牌
        res = randomOut(poker, everyOneLack, currBotID)
        return {
            "response": res
        }
        exit()

    res = searchCard(poker, lastTypeP, lastMP, lastSP)
    lenRes = len(res)

    if lenRes == 0:  # 应当输出pass
        return {
            "response": []
        }
    else:
        pokerOut, typeP, idx, minLen = [], "空", 0, 21

        if (currBotID == 2 and countPass == 0) or (currBotID == 1 and countPass == 1):  # 两个农民不能起内讧，起码不能互相炸
            for i in range(lenRes):
                pokerOut = res[i]
                typeP, _, _ = checkPokerType(pokerOut, 0)
                if typeP != "火箭" and typeP != "炸弹":
                    break
            if typeP == "火箭" or typeP == "炸弹":
                pokerOut = []
            if len(pokerOut) != 0:
                if max(pokerOut) > 14 and random.choice([0, 1]) and everyOneRestPokerLen[3 - currBotID] < 5:
                    pokerOut = []

        else:  # 其他情况是一定要怼的，但是也要考虑到出了牌以后剩下牌的情况
            bomb = []
            res += [[]]  # 最后一种是不出牌，判断跟牌之后，分牌的结果数最少
            for i in range(lenRes):
                pokerOut = res[i]
                typeP, _, _ = checkPokerType(pokerOut, 0)

                restPoker = [x for x in poker if x not in pokerOut]
                restSepRes = separate(restPoker)
                tmpLen = len(restSepRes)
                if tmpLen < minLen:
                    idx = i
                    minLen = tmpLen
                if (typeP == "火箭" or typeP == "炸弹") and len(bomb) == 0:
                    bomb = pokerOut

            if currBotID == 0:  # 是地主，要看农民的剩余张数
                enemyRestPokerLen = min(everyOneRestPokerLen[1:3])
            else:  # 是农民，也要看地主和农民的剩余张数，尽可能早的让队友走掉，或者让地主阻塞住不给他出
                enemyRestPokerLen = everyOneRestPokerLen[0]

            if enemyRestPokerLen < 4 and len(bomb) != 0:
                pokerOut = bomb
            else:
                try:
                    pokerOut = res[idx]
                except:
                    pass

        return ({
            "response": pokerOut
        })