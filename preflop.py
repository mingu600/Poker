from __future__ import division
import numpy
from deuces import Card, Evaluator, Deck
import itertools
import pickle

evaluator = Evaluator()
pre_flop = pickle.load(open("preflop_scores.p", "rb"))

for i in range(0, 1000000):
    deck = Deck()
    board = deck.draw(5)
    player1_hand = deck.draw(2)
    player2_hand = deck.draw(2)
    player1_hand.sort()

    p1_score = evaluator.evaluate(board, player1_hand)
    p2_score = evaluator.evaluate(board, player2_hand)
    key = tuple(player1_hand)

    if key not in pre_flop:
        pre_flop[key] = [0, 0]

    if p1_score < p2_score:
        pre_flop[key] = [pre_flop[key][0] + 1, pre_flop[key][1] + 1]
    elif p2_score < p1_score:
        pre_flop[key][1] += 1
    else:
        pre_flop[key] = [pre_flop[key][0] + 1, pre_flop[key][1] + 2]

# for key in pre_flop:
#     pre_flop[key] = pre_flop[key][0] / pre_flop[key][1]

pickle.dump(pre_flop, open("preflop_scores.p", "wb"))
#
# results = sorted(pre_flop.items(), key=lambda x: x[1], reverse=True)
# for i in range(0, 30):
#     Card.print_pretty_cards(list(results[i][0]))
#     print "Winning Percentage: " + str(results[i][1] * 100)
