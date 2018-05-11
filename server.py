#coding=utf-8
import json
import random

from bot import get_bot_response
class Server:
    def __init__(self):
        pass
    def allocator(self):
        total_num = 54
        publiccard_num = 3
        farmercard_num = 17
        all_cards = set(range(total_num))
        publiccards = set(random.sample(all_cards,publiccard_num))
        all_cards = all_cards - publiccards
        farmer_0_cards = set(random.sample(all_cards,farmercard_num))
        all_cards = all_cards - farmer_0_cards
        farmer_1_cards = set(random.sample(all_cards,farmercard_num))
        loard_cards = all_cards-farmer_1_cards
        loard_cards = loard_cards | publiccards
        return [list(publiccards),list(loard_cards),list(farmer_0_cards),list(farmer_1_cards)]
    def ordinalTransfer(self,poker):
        newPoker = [int(i / 4) + 3 for i in poker if i <= 52]
        if 53 in poker:
            newPoker += [17]
        return newPoker
    def checkPokerType(self,poker, hasTransfer):  # poker：list，表示一个人出牌的牌型
        poker.sort()
        lenPoker = len(poker)
        newPoker = [i for i in poker]
        if not hasTransfer:
            newPoker = self.ordinalTransfer(poker)
        # J,Q,K,A,2-11,12,13,14,15
        # 单张：1 一对：2 三带：零3、一4、二5 单顺：>=5 双顺：>=6
        # 四带二：6、8 飞机：>=6
        typeP, mP, sP = "空", newPoker, []

        for tmp in range(2):
            if tmp == 1:
                return "错误"  # 没有判断出任何牌型，出错
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
        weight = 0
        if(typeP == "单张"):
            weight = 1
        elif(typeP == "一对"):
            weight = 2
        elif( "三带" in typeP):
            weight = 4
        elif(typeP == "单顺"):
            weight = 6
        elif(typeP == "双顺"):
            weight = 6
        elif(typeP in["飞机不带翼" , "飞机带大翼" ,"飞机带小翼"]):
            weight = 8
        elif(typeP == "四带二"):
            weight = 8
        elif(typeP == "炸弹"):
            weight = 10
        elif("航天飞机" in typeP):
            weight = 10
        elif(typeP == "火箭"):
            weight = 16

        return typeP,weight
    def add_request(self,info,request):
        info["requests"].append(request)
    def get_putted_card_num(self,res):
        num = 0
        for cards in res:
            num+=len(cards)
        return num
    def check_end(self,info_farmer0,info_farmer1,info_loard):
        if (self.get_putted_card_num(info_farmer0['responses']) == 17):
            print("winner: farmer")
            return 1
        if (self.get_putted_card_num(info_farmer1['responses']) == 17):
            print("winner: farmer")
            return 1
        if (self.get_putted_card_num(info_loard['responses']) == 20):
            print("winner: loard")
            return 0
        return 2
    def run(self):
        info_farmer0 = {"requests":[],"responses":[]}
        info_farmer1 = {"requests":[],"responses":[]}
        info_loard   = {"requests":[],"responses":[]}

        weight_loard = 0
        weight_farmer0 = 0
        weight_farmer1 = 0

        #allocate cards
        publiccards,loard_cards,farmer0_cards,farmer1_cards = self.allocator()

        #first round
        info_loard["requests"].append({"history":[[],[]],"publiccard":publiccards,'own':loard_cards})
        loard_response = get_bot_response(info_loard)
        info_loard["responses"].append(loard_response["response"])
        Type,w_l = self.checkPokerType(loard_response["response"], False)
        weight_loard+=w_l
        print('loard ', Type)
        if (Type == '错误'):
            print("ERROR!")
            exit(-1)

        info_farmer0['requests'].append({"history":[[],loard_response["response"]],"publiccard":publiccards,'own':farmer0_cards})
        farmer0_response = get_bot_response(info_farmer0)
        info_farmer0['responses'].append(farmer0_response["response"])
        Type,w_f0 = self.checkPokerType(farmer0_response["response"], False)
        weight_farmer0+=w_f0
        print('farmer0 ', Type)
        if (Type == '错误'):
            print("ERROR!")
            exit(-1)

        info_farmer1['requests'].append({"history":[loard_response["response"],farmer0_response['response']],"publiccard":publiccards,'own':farmer1_cards})
        farmer1_response = get_bot_response(info_farmer1)
        info_farmer1['responses'].append(farmer1_response['response'])
        Type,wf1 = self.checkPokerType(farmer1_response["response"], False)
        weight_farmer1+=wf1
        print('farmer1', Type)
        if (Type == '错误'):
            print("ERROR!")
            exit(-1)
        #start loop

        while(True):
            #loard
            info_loard["requests"].append({"history": [farmer0_response['response'], farmer1_response['response']]})
            loard_response = get_bot_response(info_loard)
            Type,w_l = self.checkPokerType(loard_response["response"],False)
            weight_loard+=w_l
            print('loard ',Type)
            if(Type == '错误'):
                print("ERROR!")
                exit(-1)
            info_loard["responses"].append(loard_response["response"])
            if(self.check_end(info_farmer0,info_farmer1,info_loard)!=2):
                break

            #farmer-0
            info_farmer0['requests'].append(
                {"history": [farmer1_response['response'], loard_response["response"]]})
            farmer0_response = get_bot_response(info_farmer0)
            Type,w_f0 = self.checkPokerType(farmer0_response["response"], False)
            weight_farmer0+=w_f0
            print('farmer0 ',Type)
            if (Type == '错误'):
                print("ERROR!")
                exit(-1)
            info_farmer0['responses'].append(farmer0_response["response"])
            if (self.check_end(info_farmer0, info_farmer1, info_loard) != 2):
                break

            #farmer-1
            info_farmer1['requests'].append(
                {"history": [loard_response["response"], farmer0_response['response']]})
            farmer1_response = get_bot_response(info_farmer1)
            Type,wf1 = self.checkPokerType(farmer1_response["response"], False)
            weight_farmer1+=wf1
            print('farmer1',Type)
            if (Type == '错误'):
                print("ERROR!")
                exit(-1)
            info_farmer1['responses'].append(farmer1_response['response'])
            if(self.check_end(info_farmer0,info_farmer1,info_loard)!=2):
                break

        print('score loard: ',weight_loard,'score farmer0:',weight_farmer0,'score farmer1:',weight_farmer1)

if __name__ == '__main__':
    server = Server()
    # while True:
    server.run()

