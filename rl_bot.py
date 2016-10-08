# Imports.
from __future__ import division
import numpy as np
import numpy.random as npr
import math
import csv
from keras.models import load_model
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense, Activation
from heads_up import Game, Bot

class Learner(object):

    def __init__(self,exp_replay="experiences.csv",model=None):

        #track "round" (so we can write on every round that has a preceding round)
        self.round = 0
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

        #available actions (for now just a list of indexes)
        self.actions = range(5)
        self.gamma = 0.5
        self.epsilon = 0.0
        self.pos = 0

        #load pre-existing model
        if model:
            self.q_model = load_model(model)
            self.model_name = model
        else:
            self.q_model = self.build_model()
            #default name to save model to
            self.model_name = "model.h5"


        #create writer for experiences
        #must close on end of session
        f = open(exp_replay,'a')
        writer = csv.writer(f)
        self.exp_file = f
        self.exp_writer = writer

    def build_model(self):
        print "Building new model..."
        model = Sequential()
        model.add(Dense(24,input_dim=7))
        model.add(Activation('relu'))
        model.add(Dense(20))
        model.add(Activation('relu'))
        model.add(Dense(6))
        model.add(Activation('softmax'))
        model.compile(loss='mse',optimizer=Adam(lr=1e-6))
        return model

    def end(self):
        #shut down writer
        self.exp_file.close()

        #save/export model
        self.model.save(self.model_name)

    def compute_action(self,state,reward=0):
        #record the experience if it isn't the first round

        self.last_state = state

        #decide whether or not to be greedy
        r = npr.random()
        if r > self.epsilon:
            #choose action randomly
            action = np.random.choice(self.actions)
            self.last_action = action
            return action
        else:
            #choose most advantageous action
            guesses = self.model.predict(state,batch_size=1,verbose=0)
            action,_ = max(zip(actions,guesses),key=lambda x: x[1])
            return action

    #subroutine to record experiences
    def experience(self, state, action, new_state, reward=''):
        #self.exp_writer.writerow(state + [action] + [reward] + new_state)
        pass


class RLBot(Bot):
    def bet(self,min_bet,current_bet,game):
        min_bet -= current_bet
        #calculate state
        hand_str = self.calc_hand_strength(game)
        pos = np.int(game.player_list[0] is self)
        bankroll = self.chips / (self.chips + game.player_list[pos].chips)
        opp_bankroll = game.player_list[pos].chips / (self.chips + game.player_list[pos].chips)
        opp_last_bet = game.last_bets[pos] / sum(game.pot)
        pot_size = sum(game.pot) / (self.chips + game.player_list[pos].chips)
        round_num = game.bet_round
        state = [hand_str,pos,bankroll,opp_bankroll,opp_last_bet,pot_size, round_num]
        action = self.learner.compute_action(state)
        bet_sizes = [-10, min_bet, 0.5 * sum(game.pot), sum(game.pot), 1.5 * sum(game.pot), self.chips]
        bet = round(bet_sizes[action])
        #reward will be 0 for the last round
        #need to police bets
        # if self.round != 0:
        #     #can also do online training
        #     self.experience(self.last_state,self.last_action,reward,state)
        print self.name
        if min_bet > self.chips:
            bet = self.chips
        if bet > self.chips:
            bet = self.chips
        if bet == min_bet:
            if min_bet == 0:
                print(self.name + " checks.")
            else:
                print(self.name + " calls.")
        elif bet == self.chips:
            print(self.name + " goes All In!")
        elif bet < 0:
            print(self.name + " folds.")
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + " to " + str(bet + current_bet))
        self.round += 1
        return bet

    #indicate to bot that a given round has ended
    #TODO: calculate reward
    def end_round(self, game):
        self.learner.reset()

    def experience(self, state, action, new_state, reward=''):
        #self.exp_writer.writerow(state + [action] + [reward] + new_state)
        pass


    def __init__(self,name):
        self.learner = Learner()

        Bot.__init__(self, name)
