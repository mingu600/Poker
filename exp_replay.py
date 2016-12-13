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
import sys
import pdb

action = 7
reward = 8
columns = 15
chunksize =40
file_size = 1000

gamma = 0.5

def load_models(model_path):
    training_model = load_model(model_path)
    target_model = load_model(model_path)
    return (training_model, target_model)

def load_data(experiences_path,target_model,epochs,chunksize):

    #iterate over dataset a certain number of times
    for epoch in range(epochs):
        #read in data in chunks
        df = pd.read_table(experiences_path,chunksize=chunksize,sep=',',header=None)
        for chunk in df:

            #separate into end-of-hand and not end-of-hand states
            end = pd.isnull(chunk.iloc[:,reward+1])
            end_chunk = chunk[end]
            nend_chunk = chunk[~end]

            #batch predict on new states
            rewards_nend = target_model.predict_on_batch(nend_chunk.iloc[:,:action]).max(1) * gamma
            chunk.loc[~end,reward] = rewards_nend

            yield (chunk.iloc[:,:action].values,chunk.iloc[:,[action,reward]].values)

# def load_data(experiences_path,target_model,epochs,chunksize):
#     pd.read_csv(experiences_path)

def train(train_model,data_gen,epochs,batches,m_path):
    for epoch in range(epochs):
        for batch in range(batches):
            b = next(data_gen)
            labels = train_model.predict_on_batch(b[0])

            for row in b[1]:
                print row[0]
                labels[int(row[0])] = row[1]

            train_model.train_on_batch(b[0],labels)
    train_model.save(m_path)

if __name__ == '__main__':
    m_path = sys.argv[1]
    tr_model, ta_model = load_models(m_path)
    data_gen = load_data(sys.argv[2],ta_model,10,chunksize)
    train(tr_model,data_gen,10,1,m_path)
