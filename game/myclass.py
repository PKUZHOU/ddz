# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
from __future__ import print_function
from __future__ import absolute_import
from .gameutil import card_show, choose, game_init
from .card_util import get_moves
from rl.init_model import model_init


############################################
#                 游戏类                   #
############################################                   
class Game(object):
    def __init__(self, agent, RL=None):
        # 初始化一副扑克牌类
        # play相关参数
        self.end = False
        self.last_move_type = self.last_move = "start"
        self.playround = 1
        self.i = 0
        self.yaobuqis = []

        # choose模型
        self.models = agent.models

        # RL
        self.agent = agent
        self.RL = RL

    # 发牌
    def game_start(self, train):

        # 初始化players
        self.players = []
        self.players.append(Player(1, self.models[0], self.agent, self, self.RL))
        self.players.append(Player(2, self.models[1], self.agent, self, self.RL))
        self.players.append(Player(3, self.models[2], self.agent, self, self.RL))

        # 初始化扑克牌记录类
        self.playrecords = PlayRecords()
        # 发牌
        game_init(self.players, self.playrecords, train)

    # 返回扑克牌记录类
    def get_record(self):
        web_show = WebShow(self.playrecords)
        # return jsonpickle.encode(web_show, unpicklable=False)
        return web_show

    # 返回下次出牌列表
    def get_next_moves(self):
        next_move_types, next_moves = self.players[self.i].get_moves(self.last_move_type, self.last_move,
                                                                     self.playrecords)
        return next_move_types, next_moves

    # 游戏进行
    def get_next_move(self, action):
        while (self.i <= 2):
            if self.i != 0:
                self.get_next_moves()
            self.last_move_type, self.last_move, self.end, self.yaobuqi = self.players[self.i].play(self.last_move_type,
                                                                                                    self.last_move,
                                                                                                    self.playrecords,
                                                                                                    action)
            if self.yaobuqi:
                self.yaobuqis.append(self.i)
            else:
                self.yaobuqis = []
            # 都要不起
            if len(self.yaobuqis) == 2:
                self.yaobuqis = []
                self.last_move_type = self.last_move = "start"
            if self.end:
                self.playrecords.winner = self.i + 1
                break
            self.i = self.i + 1
        # 一轮结束
        self.playround = self.playround + 1
        self.i = 0
        return self.playrecords.winner, self.end


############################################
#              扑克牌相关类                 #
############################################


class PlayRecords(object):
    """
    扑克牌记录类
    """

    def __init__(self):
        # 当前手牌
        self.cards_left1 = []
        self.cards_left2 = []
        self.cards_left3 = []
        self.public_cards = []

        # 可能出牌选择
        self.next_moves1 = []
        self.next_moves2 = []
        self.next_moves3 = []

        # 出牌记录
        self.next_move1 = []
        self.next_move2 = []
        self.next_move3 = []

        # 出牌记录
        self.records = []

        # 胜利者
        # winner=0,1,2,3 0表示未结束,1,2,3表示winner
        self.winner = 0

        # 出牌者
        self.player = 1

    # 展示
    def show(self, info):
        print(info)
        card_show(self.cards_left1, "player 1", 1)
        card_show(self.cards_left2, "player 2", 1)
        card_show(self.cards_left3, "player 3", 1)
        # card_show(self.records, "record", 3)


############################################
#              出牌相关类                   #
############################################
class Moves(object):
    """
    出牌类,单,对,三,三带一,三带二,顺子,炸弹
    """

    def __init__(self):
        # 出牌信息
        self.dan = []
        self.dui = []
        self.danshun = []
        self.shuangshun = []
        self.sanbudai = []
        self.sandaiyi = []
        self.sandaier = []
        self.sidaierzhi = []
        self.sidaierdui = []
        self.feijibudaiyi = []
        self.feijidaixiaoyi = []
        self.feijidaidayi = []
        self.hangtianfeiji = []
        self.htfjdaixiaoyi = []
        self.htfjdaidayi = []
        self.bomb = []
        self.huojian = []

        # 牌数量信息
        self.card_num_info = {}
        # 牌顺序信息,计算顺子
        self.card_order_info = []
        # 王牌信息
        self.king = []

        # 下次出牌
        self.next_moves = []
        # 下次出牌类型
        self.next_moves_type = []

    # 获取全部出牌列表
    def get_total_moves(self, cards_left):
        #  moves = Moves()
        self.dan, self.dui, self.danshun, self.shuangshun, self.sanbudai, self.sandaiyi, self.sandaier, self.sidaierzhi, self.sidaierdui, self.feijibudaiyi, self.feijidaixiaoyi, self.feijidaidayi, self.hangtianfeiji, self.htfjdaixiaoyi, self.htfjdaidayi, self.bomb, self.huojian = get_moves(
            cards_left, True)

    # return moves

    # 获取下次出牌列表
    def get_next_moves(self, last_move_type, last_move):
        # 没有last,全加上,除了bomb最后加
        if last_move_type == "start":
            moves_types = ["dan", "dui", "danshun", "shuangshun", "sanbudai", "sandaiyi",
                           "sandaier",
                           "sidaierzhi",
                           "sidaierdui",
                           "feijibudaiyi",
                           "feijidaixiaoyi",
                           "feijidaidayi",
                           "hangtianfeiji",
                           "htfjdaixiaoyi",
                           "htfjdaidayi",
                           "bomb",
                           "huojian"]
            i = 0
            for move_type in [self.dan, self.dui, self.danshun, self.shuangshun, self.sanbudai, self.sandaiyi,
                              self.sandaier, self.sidaierzhi, self.sidaierdui, self.feijibudaiyi, self.feijidaixiaoyi,
                              self.feijidaidayi, self.hangtianfeiji, self.htfjdaixiaoyi, self.htfjdaidayi]:

                for move in move_type:
                    self.next_moves.append(move)
                    self.next_moves_type.append(moves_types[i])
                i = i + 1
        # 出单
        elif last_move_type == "dan":
            for move in self.dan:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("dan")
        # 出对
        elif last_move_type == "dui":
            for move in self.dui:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("dui")

        elif last_move_type == "danshun":
            for move in self.danshun:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("danshun")
        elif last_move_type == "shuangshun":
            for move in self.shuangshun:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("shuangshun")

        elif last_move_type == "sanbudai":
            for move in self.sanbudai:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("sanbudai")
        elif last_move_type == "sandaiyi":
            for move in self.sandaiyi:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("sandaiyi")
        elif last_move_type == "sandaier":
            for move in self.sandaier:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("sandaier")
        # 出三带二
        elif last_move_type == "sidaierzhi":
            for move in self.sidaierzhi:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("sidaierzhi")
        elif last_move_type == "sidaierdui":
            for move in self.sidaierdui:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("sidaierdui")
        elif last_move_type == "feijibudaiyi":
            for move in self.feijidaidayi:
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("feijibudaiyi")
        elif last_move_type == "feijidaixiaoyi":
            for move in self.feijidaixiaoyi:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("feijidaixiaoyi")
        elif last_move_type == "feijidaidayi":
            for move in self.feijidaidayi:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("feijidaidayi")
        elif last_move_type == "hangtianfeiji":
            for move in self.hangtianfeiji:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("hangtianfeiji")
        elif last_move_type == "htfjdaixiaoyi":
            for move in self.htfjdaixiaoyi:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("htfjdaixiaoyi")
        elif last_move_type == "htfjdaidayi":
            for move in self.htfjdaixiaoyi:
                # 比last大
                if len(move) == len(last_move):
                    if move[0] > last_move[0]:
                        self.next_moves.append(move)
                        self.next_moves_type.append("htfjdaidayi")
        # 出炸弹
        elif last_move_type == "bomb":
            for move in self.bomb:
                # 比last大
                if move[0] > last_move[0]:
                    self.next_moves.append(move)
                    self.next_moves_type.append("bomb")
        elif last_move_type == "huojian":
            pass

        else:
            print("last_move_type_wrong")

        # 除了bomb,都可以出炸
        if last_move_type != "bomb":
            for move in self.bomb:
                self.next_moves.append(move)
                self.next_moves_type.append("bomb")

        if len(self.huojian) != 0:
            self.next_moves.append(self.huojian[0])
            self.next_moves_type.append("huojian")

        return self.next_moves_type, self.next_moves

    # 展示
    def show(self, info):
        print(info)
        # card_show(self.dan, "dan", 2)
        # card_show(self.dui, "dui", 2)
        # card_show(self.san, "san", 2)
        # card_show(self.san_dai_yi, "san_dai_yi", 2)
        # card_show(self.san_dai_er, "san_dai_er", 2)
        # card_show(self.bomb, "bomb", 2)
        # card_show(self.shunzi, "shunzi", 2)
        # card_show(self.next_moves, "next_moves", 2)


############################################
#              玩家相关类                   #
############################################        
class Player(object):
    """
    player类
    """

    def __init__(self, player_id, model, agent=None, game=None, RL=None):
        self.player_id = player_id
        self.cards_left = []
        # 出牌模式
        self.model = model
        # RL_model
        self.game = game
        self.agent = agent

        self.RL = RL

    # 展示
    def show(self, info):
        self.total_moves.show(info)
        card_show(self.next_move, "next_move", 1)
        # card_show(self.cards_left, "card_left", 1)

    # 根据next_move同步cards_left
    def record_move(self, playrecords):
        # 记录出牌者
        playrecords.player = self.player_id
        # playrecords中records记录[id,next_move]
        if self.next_move_type in ["yaobuqi", "buyao"]:
            self.next_move = self.next_move_type
            playrecords.records.append([self.player_id, self.next_move_type])
        else:
            playrecords.records.append([self.player_id, self.next_move])
            for i in self.next_move:
                self.cards_left.remove(i)
        # 同步playrecords
        if self.player_id == 1:
            playrecords.cards_left1 = self.cards_left
            playrecords.next_moves1.append(self.next_moves)
            playrecords.next_move1.append(self.next_move)
        elif self.player_id == 2:
            playrecords.cards_left2 = self.cards_left
            playrecords.next_moves2.append(self.next_moves)
            playrecords.next_move2.append(self.next_move)
        elif self.player_id == 3:
            playrecords.cards_left3 = self.cards_left
            playrecords.next_moves3.append(self.next_moves)
            playrecords.next_move3.append(self.next_move)
        # 是否牌局结束
        end = False
        if len(self.cards_left) == 0:
            end = True
        return end

    # 选牌
    def get_moves(self, last_move_type, last_move, playrecords):
        # 所有出牌可选列表
        self.total_moves = Moves()
        # 获取全部出牌列表
        self.total_moves.get_total_moves(self.cards_left)
        # 获取下次出牌列表
        self.next_move_types, self.next_moves = self.total_moves.get_next_moves(last_move_type, last_move)
        # 返回下次出牌列表
        return self.next_move_types, self.next_moves

    # 出牌
    def play(self, last_move_type, last_move, playrecords, action):
        # 在next_moves中选择出牌方法
        self.next_move_type, self.next_move = choose(next_move_types=self.next_move_types,
                                                     next_moves=self.next_moves,
                                                     last_move_type=last_move_type,
                                                     last_move=last_move,
                                                     cards_left=self.cards_left,
                                                     model=self.model,
                                                     RL=self.RL,
                                                     agent=self.agent,
                                                     game=self.game,
                                                     player_id=self.player_id,
                                                     action=action)
        # 记录
        end = self.record_move(playrecords)
        # 展示
        # self.show("Player " + str(self.player_id))
        # 要不起&不要
        yaobuqi = False
        if self.next_move_type in ["yaobuqi", "buyao"]:
            yaobuqi = True
            self.next_move_type = last_move_type
            self.next_move = last_move

        return self.next_move_type, self.next_move, end, yaobuqi


############################################
#               网页展示类                 #
############################################
class WebShow(object):
    """
    网页展示类
    """

    def __init__(self, playrecords):

        # 胜利者
        self.winner = playrecords.winner

        # 剩余手牌
        self.cards_left1 = []
        for i in playrecords.cards_left1:
            self.cards_left1.append(i)
        self.cards_left2 = []
        for i in playrecords.cards_left2:
            self.cards_left2.append(i)
        self.cards_left3 = []
        for i in playrecords.cards_left3:
            self.cards_left3.append(i)

        # 可能出牌
        self.next_moves1 = []
        if len(playrecords.next_moves1) != 0:
            next_moves = playrecords.next_moves1[-1]
            for move in next_moves:
                cards = []
                for card in move:
                    cards.append(card)
                self.next_moves1.append(cards)
        self.next_moves2 = []
        if len(playrecords.next_moves2) != 0:
            next_moves = playrecords.next_moves2[-1]
            for move in next_moves:
                cards = []
                for card in move:
                    cards.append(card)
                self.next_moves2.append(cards)
        self.next_moves3 = []
        if len(playrecords.next_moves3) != 0:
            next_moves = playrecords.next_moves3[-1]
            for move in next_moves:
                cards = []
                for card in move:
                    cards.append(card)
                self.next_moves3.append(cards)

        # 出牌
        self.next_move1 = []
        if len(playrecords.next_move1) != 0:
            next_move = playrecords.next_move1[-1]
            if next_move in ["yaobuqi", "buyao"]:
                self.next_move1.append(next_move)
            else:
                for card in next_move:
                    self.next_move1.append(card)
        self.next_move2 = []
        if len(playrecords.next_move2) != 0:
            next_move = playrecords.next_move2[-1]
            if next_move in ["yaobuqi", "buyao"]:
                self.next_move2.append(next_move)
            else:
                for card in next_move:
                    self.next_move2.append(card)
        self.next_move3 = []
        if len(playrecords.next_move3) != 0:
            next_move = playrecords.next_move3[-1]
            if next_move in ["yaobuqi", "buyao"]:
                self.next_move3.append(next_move)
            else:
                for card in next_move:
                    self.next_move3.append(card)

        # 记录
        self.records = []
        for i in playrecords.records:
            tmp = []
            tmp.append(i[0])
            tmp_name = []
            # 处理要不起
            try:
                for j in i[1]:
                    tmp_name.append(j)
                tmp.append(tmp_name)
            except:
                tmp.append(i[1])
            self.records.append(tmp)
