# Imports.
from __future__ import division
import numpy as np
import numpy.random as npr
import random
import math
import os, sys, signal
import pdb
import csv
from keras.models import load_model
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Dense, Activation
from heads_up import Game, Bot
import time
# import matplotlib as mpl
#import matplotlib.pyplot as plt

state_size = 7

class Learner(object):

    def __init__(self,exp_replay="experiences.csv",model=None,epsilon=0.0,gamma=0.5):

        #track "round" (so we can write on every round that has a preceding round)
        self.round = 0
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

        #available actions (for now just a list of indexes)
        self.actions = range(5)
        self.gamma = gamma
        print gamma
        self.epsilon = epsilon
        print epsilon

        #load pre-existing model
        if model:
            self.model = load_model(model)
            self.model_name = model
        else:
            self.model = self.build_model()
            #default name to save model to
            self.model_name = "model.h5"

        self.replay = []
        self.buffer = 80
        self.index = 0
        self.batchSize = 40

        # #create writer for experiences
        # #must close on end of session
        # f = open(exp_replay,'a')
        # writer = csv.writer(f)
        # self.exp_file = f
        # self.exp_writer = writer

    def build_model(self):
        print "Building new model..."
        model = Sequential()
        model.add(Dense(48,input_dim=state_size))
        model.add(Activation('relu'))
        model.add(Dense(12))
        model.add(Activation('relu'))
        model.add(Dense(6))
        model.add(Activation('softmax'))
        model.compile(loss='mse',optimizer=Adam(lr=1e-6))
        return model

    def end(self):
        #shut down writer
        #self.exp_file.close()

        #save/export model
        self.model.save(self.model_name)

    def compute_action(self,state,reward=0):
        self.last_state = state

        #decide whether or not to be greedy
        r = npr.random()
        if self.epsilon > 0:
            self.epsilon -= 0.0002
        else:
            self.epsilon = 0
        if r < self.epsilon:
            #choose action randomly
            action = np.random.choice(self.actions)
            self.last_action = action
            return action
        else:
            #choose most advantageous action
            guesses = self.model.predict(np.array(state).reshape(1,state_size),batch_size=1,verbose=0)
            action = np.argmax(guesses)
            self.last_action = action
            return action

    def train_model(self, state=None, reward=0):
        if len(self.replay) < self.buffer:
            self.replay.append((self.last_state, self.last_action, reward, state))
        else: #if buffer full, overwrite old values
            if self.index < (self.buffer-1):
                self.index += 1
            else:
                self.index = 0
            self.replay[self.index] = (self.last_state, self.last_action, reward, state)
            #randomly sample our experience replay memory
            minibatch = random.sample(self.replay, self.batchSize)
            X_train = []
            y_train = []
            for event in minibatch:
                #Get max_Q(S',a)
                old_state, action, reward, new_state = event
                old_qval = self.model.predict(np.array(old_state).reshape(1,state_size), batch_size=1)
                y = np.array(old_qval)
                if reward == 0 and new_state != None: #non-terminal state
                    new_qval = self.model.predict(np.array(new_state).reshape(1,state_size), batch_size=1)
                    max_Qval = np.max(new_qval)
                    update = (reward + (self.gamma * max_Qval))
                else: #terminal state
                    update = reward
                y[0][action] = update
                X_train.append(old_state)
                y_train.append(y[0])

            X_train = np.array(X_train)
            y_train = np.array(y_train)
            self.model.fit(X_train, y_train, batch_size=self.batchSize, nb_epoch=1, verbose=1)
            self.model.save('model.h5')

        def signal_handler(signum, frame):
            if signum is signal.SIGINT:
                print >> sys.stderr, "interrupted during training"
                self.model.save('model.h5')
                sys.exit(0)
        signal.signal(signal.SIGINT,signal_handler)
        if self.last_state != None:
            if len(self.replay) < self.buffer:
                self.replay.append((self.last_state, self.last_action, reward, state))
            else: #if buffer full, overwrite old values
                if self.index < (self.buffer-1):
                    self.index += 1
                else:
                    self.index = 0
                self.replay[self.index] = (self.last_state, self.last_action, reward, state)
                #randomly sample our experience replay memory
                minibatch = random.sample(self.replay, self.batchSize)
                X_train = []
                y_train = []
                for event in minibatch:
                    #Get max_Q(S',a)
                    old_state, action, reward, new_state = event
                    old_qval = self.model.predict(np.array(old_state).reshape(1,7), batch_size=1)
                    y = np.array(old_qval)
                    if reward == 0 and new_state != None: #non-terminal state
                        new_qval = self.model.predict(np.array(new_state).reshape(1,7), batch_size=1)
                        max_Qval = np.max(new_qval)
                        update = (reward + (self.gamma * max_Qval))
                    else: #terminal state
                        update = reward
                    y[0][action] = update
                    X_train.append(old_state)
                    y_train.append(y[0])

                X_train = np.array(X_train)
                y_train = np.array(y_train)
                self.model.fit(X_train, y_train, batch_size=self.batchSize, nb_epoch=1, verbose=1)
                self.model.save('model.h5')
        signal.signal(signal.SIGINT,signal.SIG_DFL)
    # #subroutine to record experiences
    # def experience(self, new_state=['NULL'], reward=0):
    #     self.exp_writer.writerow(self.last_state + [self.last_action] + [reward] + new_state)


class RLBot(Bot):
    def preflop_graph(self, pos=0, bankroll=0.5, opp_bankroll=0.5, opp_last_bet=0, pot_size=0.1, round_num=1):
        x = [float(x)/100 for x in range(0, 100)]
        y = []
        for hand_str in x:
            guesses = self.learner.model.predict(np.array([hand_str, pos, bankroll,opp_bankroll,opp_last_bet,pot_size, round_num]).reshape(1,state_size),batch_size=1,verbose=0)
            action = np.argmax(guesses)
            y.append(action)
        ax = fig.add_subplot(1,1,1,
            title='Effect of Hand Strength on Betting Pattern',
            xlabel='Hand Strength', ylabel='Action')
        ax.scatter(x, y)
        plt.show()

    def bet(self,min_bet,current_bet,times,game):
        min_bet -= current_bet
        #calculate state

        #time hand str calculation
        t = time.time()
        hand_str = self.calc_hand_strength(game)
        times['strength']['count'] += 1
        times['strength']['total'] += time.time() - t
        
        pos = np.int(game.player_list[0] is self)
        bankroll = self.chips / (self.chips + game.player_list[pos].chips)
        opp_bankroll = game.player_list[pos].chips / (self.chips + game.player_list[pos].chips)
        if game.last_bets[pos] != None:
            opp_last_bet = game.last_bets[pos] / sum(game.pot)
        else:
            opp_last_bet = 0
        pot_size = sum(game.pot) / (self.chips + game.player_list[pos].chips)
        round_num = game.bet_round
        state = [hand_str, pos, bankroll,opp_bankroll,opp_last_bet,pot_size, round_num]
        self.learner.last_state = state
        if self.learner.round > 0:
            self.learner.train_model(state)

        #now compute action
        action = self.learner.compute_action(state)
        if action == 0 and min_bet == 0:
            action = 1
            self.learner.last_action = action
        bet_sizes = [-10, min_bet, 0.5 * sum(game.pot), sum(game.pot), 1.5 * sum(game.pot), self.chips]
        bet = int(round(bet_sizes[action]))
        #reward will be 0 for the last round
        #need to police bets
        # if self.round != 0:
        #     #can also do online training
        #     self.experience(self.last_state,self.last_action,reward,state)
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
        self.learner.round += 1
        return bet

    #indicate to bot that a given round has ended
    def end_round(self, game, winnings):
        if self.recorder:
            total_chips = game.chips*game.player_num
            if self.learner.last_action == 0:
                reward = float(winnings)/total_chips
            else:
                reward = float(winnings)/total_chips
            self.learner.train_model(reward=reward)
            self.learner.last_state  = None
            self.learner.last_action = None
            self.learner.last_reward = None

    def experience(self, state, action, new_state, reward=''):
        #self.exp_writer.writerow(state + [action] + [reward] + new_state)
        pass

    def end(self):
        self.learner.end()

    def __init__(self,name,epsilon=0.0,gamma=0.5,recorder=True):

        #whether we want to have this bot record its actions or not
        self.recorder = recorder
        if os.path.isfile('model.h5'):
            self.learner = Learner(gamma=gamma,epsilon=epsilon,model='model.h5')
        else:
            self.learner = Learner(gamma=gamma,epsilon=epsilon)

        Bot.__init__(self, name)


class GreedyBot(Bot):
    def bet(self,min_bet,current_bet,times,game):

        min_bet -= current_bet
        #calculate state

        #time the hand strength calculation
        t = time.time()
        hand_str = self.calc_hand_strength(game)
        times['strength']['count'] += 1
        times['strength']['total'] += time.time() - t

        if hand_str > 0.9:
            bet = self.chips
        elif hand_str < 0.5 and min_bet > 0:
            bet = -10
        elif hand_str < 0.6:
            bet = min_bet
        elif hand_str < 0.7:
            bet = int(1.3 * min_bet)
        elif hand_str < 0.8:
            bet = int(1.5 * min_bet)
        else:
            bet = int(2 * min_bet)
        #reward will be 0 for the last round
        #need to police bets
        # if self.round != 0:
        #     #can also do online training
        #     self.experience(self.last_state,self.last_action,reward,state)
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
        return bet

    def end_round(self, game, winnings):
        pass

    def __init__(self,name):
        Bot.__init__(self, name)
if __name__ == "__main__":
    RLBot('Mingu').preflop_graph()
