# Imports.
from __future__ import division
import numpy as np
import numpy.random as npr
import random
import math
import os, sys, signal
import csv
from keras.models import load_model
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras.layers import Dense, Activation
from heads_up import Game, Bot
import time

state_size = 10

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
        self.epsilon = epsilon

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

        # Builds neural network
        #create writer for experiences
        #must close on end of session

    def build_model(self):
        print "Building new model..."
        model = Sequential()
        model.add(Dense(24,input_dim=state_size, init='lecun_uniform'))
        model.add(Activation('relu'))
        model.add(Dense(12, init='lecun_uniform'))
        model.add(Activation('relu'))
        model.add(Dense(6, init='lecun_uniform'))
        model.add(Activation('linear'))
        rms = RMSprop()
        model.compile(loss='mse', optimizer=rms)
        return model

    # Saves and exports model
    def end(self):
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
            #print guesses
            action = np.argmax(guesses)
            self.last_action = action
            return action

    def train_model(self, state=[None]*state_size, reward=0):

        def signal_handler(signum, frame):
            if signum is signal.SIGINT:
                print >> sys.stderr, "interrupted during training"
                self.model.save('model.h5')
                sys.exit(0)
        signal.signal(signal.SIGINT,signal_handler)

        experience = (self.last_state, self.last_action, reward, state)
        if experience[0] != None and experience[1] != None:
            # If the buffer is not full, add new experience
            if len(self.replay) < self.buffer:
                self.replay.append(experience)
            # When buffer is full, train the model and then clear the buffer
            else:
                X_train = []
                y_train = []
                for event in self.replay:
                    #Get max_Q(S',a)
                    old_state, action, reward, new_state = event
                    self.exp_writer.writerow(old_state + [action] + [reward] + new_state)
                    old_qval = self.model.predict(np.array(old_state).reshape(1,state_size), batch_size=1)
                    y = np.array(old_qval)
                    if reward == 0 and new_state[0] != None: #non-terminal state
                        new_qval = self.model.predict(np.array(new_state).reshape(1,state_size), batch_size=1)
                        max_Qval = np.max(new_qval)
                        update = (reward + (self.gamma * max_Qval))
                    else: #terminal state
                        update = reward
                    print "OLD: " + str(y[0])
                    y[0][action] = update
                    print 'NEW: ' + str(y[0])
                    X_train.append(old_state)
                    y_train.append(y[0])

                X_train = np.array(X_train)
                y_train = np.array(y_train)
                self.model.fit(X_train, y_train, batch_size=self.batchSize, nb_epoch=1, verbose=1, shuffle=True)
                self.model.save('model.h5')
                self.replay = []
        signal.signal(signal.SIGINT,signal.SIG_DFL)

class RLBot(Bot):

    # Creates csv files used to make figure 8 of the paper
    def bankroll_graph(self, time, pos=0, hand_str=0.5, opp_last_bet=0, pot_size=0.1, round_num=2):
        x = np.arange(0, 1, 0.01)
        y = []
        if round_num == 0:
            round_v = [1,0,0,0]
        elif round_num ==1:
            round_v = [0,1,0,0]
        elif round_num== 2:
            round_v = [0, 0, 1, 0]
        else:
            round_v = [0, 0, 0, 1]
        # Iterates through bankroll values and saves csv files for the plot
        for bankroll in x:
            guesses = self.learner.model.predict(np.array([hand_str, pos, bankroll, 1-bankroll,opp_last_bet,pot_size] + round_v).reshape(1,state_size),batch_size=1,verbose=0)
            action = np.argmax(guesses)
            y.append([val for sublist in guesses for val in sublist])
        print [np.argmax(state) for state in y]
        np.savetxt("bankroll/bankroll_pre_flop" + str(time) + ".csv", np.asarray(y), delimiter=",")

    # Creates csv files used to make figure 8 of the paper
    def hand_str_graph(self, time, pos=0, bankroll=0.5, opp_bankroll=0.5, opp_last_bet=0, pot_size=0.1, round_num=2):
        x = np.arange(0, 1, 0.01)
        y = []
        if round_num == 0:
            round_v = [1,0,0,0]
        elif round_num ==1:
            round_v = [0,1,0,0]
        elif round_num== 2:
            round_v = [0, 0, 1, 0]
        else:
            round_v = [0, 0, 0, 1]
        # Iterate through hand strengths and save csv files for the plot
        for hand_str in x:
            guesses = self.learner.model.predict(np.array([hand_str, pos, bankroll,opp_bankroll,opp_last_bet,pot_size] + round_v).reshape(1,state_size),batch_size=1,verbose=0)
            action = np.argmax(guesses)
            y.append([val for sublist in guesses for val in sublist])
        print [np.argmax(state) for state in y]
        np.savetxt("hand_str/pre_flop" + str(time) + ".csv", np.asarray(y), delimiter=",")

    # Function for Deep Q-learning agent betting
    def bet(self,min_bet,current_bet,times,game):
        min_bet -= current_bet

        #time hand str calculation
        t = time.time()
        hand_str = self.calc_hand_strength(game)
        times['strength']['count'] += 1
        times['strength']['total'] += time.time() - t

        # Determine state space
        # Position: either first or second to bet
        # Opponet's bankroll: how many chips they have as a proportion
        # Opponent's last bet amount
        # Pot size
        # Round number: Pre-flop, flop, turn, river
        pos = np.int(game.player_list[0] is self)
        bankroll = self.chips / (self.chips + game.player_list[pos].chips)
        opp_bankroll = game.player_list[pos].chips / (self.chips + game.player_list[pos].chips)
        if game.last_bets[pos] != None:
            opp_last_bet = game.last_bets[pos] / (game.player_list[pos].chips + sum(game.pot))
        else:
            opp_last_bet = 0
        pot_size = sum(game.pot) / (self.chips + game.player_list[pos].chips)
        round_num = game.bet_round
        if game.bet_round == 0:
            round_num = [1,0,0,0]
        elif game.bet_round ==1:
            round_num = [0,1,0,0]
        elif game.bet_round == 2:
            round_num = [0, 0, 1, 0]
        else:
            round_num = [0, 0, 0, 1]
        state = [hand_str, pos, bankroll,opp_bankroll,opp_last_bet,pot_size] + round_num
        self.learner.last_state = state
        # Train model if after pre-flop
        if self.learner.round > 0:
            self.learner.train_model(state)
        # Now compute action
        action = self.learner.compute_action(state)
        if (action == 0 and min_bet == 0):
            action = 1
            self.learner.last_action = action
        # Convert action into bet size
        bet_sizes = [-10, min_bet, 0.5 * sum(game.pot) + min_bet, sum(game.pot) + min_bet, 1.5 * sum(game.pot) + min_bet, self.chips]
        bet = int(round(bet_sizes[action]))
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
            if winnings > 0:
                reward = float(winnings)/(total_chips)
            else:
                reward = float(winnings)/(total_chips)
            self.learner.train_model(reward=reward)
            self.learner.last_state  = None
            self.learner.last_action = None
            self.learner.last_reward = None

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

# Monte Carlo bot used to evaluate performance of RL bot.
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
