# Imports.
import numpy as np
import numpy.random as npr
import math
import csv
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Activation

from framework import Game

class Learner(object):

    def __init__(self,exp_replay="experiences.csv",model=None):

        #track "round" (so we can write on every round that has a preceding round)
        self.round = 0
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

        #available actions (for now just a list of indexes)
        self.actions = range(5)

        self.Q = np.random.rand(2000,2)
        self.alpha = 0.5
        self.gamma = 0.5
        self.epsilon = 0.0
        self.opponent_agg = 0.5
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
        model.add(Dense(24,input_dim=6))
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

    def reset(self):
        self.round = 0
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

    def compute_action(self,state,reward=0):
        #record the experience if it isn't the first round
        if self.round != 0:
            #can also do online training
            self.experience(self.last_state,self.last_action,reward,state)

        self.last_state = state
        self.round+=1

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
            self.last_action
            return action

    #subroutine to record experiences
    def experience(self, state, action, reward, new_state):
        self.exp_writer.writerow(state + [action] + [reward] + new_state)
