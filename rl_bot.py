# Imports.
import numpy as np
import numpy.random as npr
import math

from framework import Game

class Learner(object):

    def __init__(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.Q = np.random.rand(2000,2)
        self.alpha = 0.5
        self.gamma = 0.5
        self.opponent_agg = 0.5
        self.pos = 0

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

    def find_index(self, state):
        # State is [Hand Strength, Button Position, Opponent Aggressiveness, Opponent Action]

        a = state[1]
        b = math.floor(3 * state[1])
        c = state[3]
        d = math.floor(10 * state[0] - 0.0001)

        return 1000 * a + 100 * b + 10 * c + d

    def action_callback(self, state):
        index = self.find_index(state)

        old_action = self.Q[self.find_index(self.last_state)][self.last_action]
        #print self.find_index(self.last_state) ,self.last_action

        #changed from self.Q[index] = ...
        #also debugged equation -- need to double-check
        self.Q[self.find_index(self.last_state)][self.last_action] = old_action + self.alpha * (self.last_reward + self.gamma * np.argmax(self.Q[index]) - old_action)
        self.last_action = np.argmax(self.Q[index])
        #print self.last_action
        self.last_state  = new_state
        #print [self.Q[index][0], self.Q[index][1]]
        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''
        self.last_reward = reward
