#USAGE python exp_replay.py model_path experiences_path

# Imports
import numpy as np
import numpy.random as npr
import pandas as pd
import math
import csv
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, Activation
from heads_up import Game
from heads_up import Bot
import sys

action = 7
reward = 8
columns = 15

file_size = 1000

def load_models(model_path):
    training_model = load_model(model_path)
    target_model = load_model(model_path)
    return (training_model, target_model)

def load_data(experiences_path,target_model,epochs,chunksize):

#iterate over dataset a certain number of times
    for epoch in range(epochs):
        #read in data in chunks
        df = pd.read_table(experiences_path,chunksize=chunksize)
        for chunk in df:
            
            #separate into end-of-hand and not end-of-hand states
            chunk.iloc[:,reward] = chunk.iloc[:,reward] + (0 if chunk.iloc[:,reward+1].isNull() else ndarray.max(target_model.predict_on_batch(chunk.iloc[:,reward+1:]),axis=1))
            cols = list(chunk.columns)
            yield (chunk.iloc[:,:action].values,chunk.iloc[:,[action,reward]].values)

def train(train_model,data_gen,epochs,batches):
    for epoch in range(epochs):
        for batch in range(batches):
            b = next(data_gen)
            labels = train_model.predict_on_batch(b[0])
            labels[b[1][:,0]] = b[1][:,1]  
            train_model.train_on_batch(b[0],labels)

if __name__ == '__main__':
    m_path = sys.argv[1]
    tr_model, ta_model = load_models(m_path)
    data_gen = load_data(sys.argv[2],ta_model,10,chunksize)
    train(tr_model,data_gen,10,1)
    
