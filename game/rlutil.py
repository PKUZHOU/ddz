# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
from __future__ import print_function
import numpy as np   
from .config import Config
############################################
#                   LR相关                 #
############################################   
def get_state(playrecords, player):
    cfg = Config()
    state = np.zeros(cfg.dim_states).astype("int") #33+dim_action
    #手牌
    if player == 1:
        cards_left = playrecords.cards_left1
        state[30] = len(playrecords.cards_left1)
        state[31] = len(playrecords.cards_left2)
        state[32] = len(playrecords.cards_left3)
    elif player == 2:
        cards_left = playrecords.cards_left2
        state[30] = len(playrecords.cards_left2)
        state[31] = len(playrecords.cards_left3)
        state[32] = len(playrecords.cards_left1)
    else:
        cards_left = playrecords.cards_left3
        state[30] = len(playrecords.cards_left3)
        state[31] = len(playrecords.cards_left1)
        state[32] = len(playrecords.cards_left2)
    for i in cards_left:
        state[i] += 1
    #底牌
    for cards in playrecords.records:
        if cards[1] in ["buyao","yaobuqi"]:
            continue
        for card in cards[1]:
            state[card + 15] += 1
          
    return state    

def get_actions(next_moves, actions_lookuptable, game):
    """

    """
    actions = []
    for cards in next_moves:
        actions.append(actions_lookuptable[str(cards)])
    
    #yaobuqi
    if len(actions) == 0:
        actions.append(34348)
    #buyao
    elif game.last_move != "start":
        actions.append(34347)
        
    return actions

#结合state和可以出的actions作为新的state    
def combine(s, a):
    for i in a:
        s[33+i] = 1
    return s
    

        
    
    
    