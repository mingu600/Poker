import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Generates figure 8 (assumes you've generated csv files already using heads_up performance option)
def bankroll():
    guesses = []
    for i in range(0, 5000, 50):
        guess = np.genfromtxt ('bankroll/bankroll_pre_flop' + str(i) + '.csv', delimiter=",")
        action = [np.argmax(state) for state in guess]
        guesses.append(action)
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111,
                     xlabel='Bankroll',
                     ylabel='Time (games played)')
    im = ax.imshow(guesses, interpolation='none', aspect='auto', cmap='RdBu_r', origin='lower')
    cb = plt.colorbar(im, label='Actions')
    ax.set_yticks(range(0, 100, 10))
    ax.set_yticklabels(range(0, 5000, 500))
    ax.set_xticks(range(0, 100, 10))
    ax.set_xticklabels(np.arange(0, 1, 0.1))
    cb.set_ticks(range(1, 6))
    cb.set_ticklabels(['Check/Call', 'Bet half-pot', 'Bet pot', 'Bet 1.5-pot', 'All-in'])
    plt.savefig('bankroll_pre_flop.png')

# Generates figure 7 (assumes you've generated csv files already using heads_up performance option)
def pre_flop():
    guesses = []
    for i in range(0, 5000, 50):
        guess = np.genfromtxt ('pre_flop' + str(i) + '.csv', delimiter=",")
        action = [np.argmax(state) for state in guess]
        guesses.append(action)
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111,
                     xlabel='Hand Strength',
                     ylabel='Time (games played)')
    im = ax.imshow(guesses, interpolation='none', aspect='auto', cmap='RdBu_r', origin='lower')
    cb = plt.colorbar(im, label='Actions')
    ax.set_yticks(range(0, 100, 10))
    ax.set_yticklabels(range(0, 5000, 500))
    ax.set_xticks(range(0, 100, 10))
    ax.set_xticklabels(np.arange(0, 1, 0.1))
    cb.set_ticks(range(1, 6))
    cb.set_ticklabels(['Check/Call', 'Bet half-pot', 'Bet pot', 'Bet 1.5-pot', 'All-in'])
    plt.savefig('pre_flop.png')

bankroll()
