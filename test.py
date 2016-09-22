from __future__ import division
import pickle
from deuces import Card, Evaluator, Deck
test = pickle.load(open("preflop_scores.p", "rb"))
pre_flop = test.copy()
for key in pre_flop:
    pre_flop[key] = pre_flop[key][0] / pre_flop[key][1]

results = sorted(pre_flop.items(), key=lambda x: x[1], reverse=True)
for i in range(0, 30):
    Card.print_pretty_cards(list(results[i][0]))
    print "Winning Percentage: " + str(results[i][1] * 100)


