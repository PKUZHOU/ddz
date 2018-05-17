# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 21:55:58 2017

@author: XuGang
"""
from __future__ import absolute_import
from .card_util import get_action_dic
from .long_act_dic import action_dict
############################################
#                  config                  #
############################################
class Config(object):
    def __init__(self):
        self.actions_lookuptable = action_dict
        self.dim_actions = len(self.actions_lookuptable) + 2 #34347 buyao, 34348 yaobuqi
        self.dim_states = 30 + 3 + self.dim_actions #431为dim_actions

if __name__ == '__main__':
    actdict = get_action_dic()
    with open("long_act_dic.py",'w') as f:
        f.write(str(actdict))