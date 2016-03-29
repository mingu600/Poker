import pydealer
from itertools import groupby
from more_itertools import unique_everseen

deck = pydealer.Deck()
deck.shuffle()
hand = pydealer.Stack()
hand.add(
[pydealer.Card("King", "H"),
pydealer.Card("Ace", "C"),
pydealer.Card("3", "H"),
pydealer.Card("2", "S"),
pydealer.Card("Ace", "S"),
pydealer.Card("King", "D"),
pydealer.Card("3", "C")])

new_ranks = {
    "values": {
        "Ace": 1,
        "King": 2,
        "Queen": 3,
        "Jack": 4,
        "10": 5,
        "9": 6,
        "8": 7,
        "7": 8,
        "6": 9,
        "5": 10,
        "4": 11,
        "3": 12,
        "2": 13
    }
}


def handResult(hand):
    sorted_hand = hand
    sorted_hand.sort(ranks=new_ranks)
    values = []
    suits = []
    for i in sorted_hand:
        values.append(i.value)
    for i in sorted_hand:
        suits.append(i.suit)
    tallied_values = [[k , len(list(g))] for k, g in groupby(values)]
    tallied_suits = [[k, len(list(g))] for k, g in groupby(suits)]
    triples = []
    pairs = []
    straights = []
    values2 = list(unique_everseen(values))
    values3 = values2[:]
    values3.reverse()
    # Straight/Royal Flush
    for i in range(0, len(values2) - 4):
        if (int(new_ranks['values'].get(values2[i])) == int(new_ranks['values'].get(values2[i + 1])) - 1 == int(new_ranks['values'].get(values2[i + 2])) - 2 and
        int(new_ranks['values'].get(values2[i + 2])) - 2 == int(new_ranks['values'].get(values2[i + 3])) - 3 == int(new_ranks['values'].get(values2[i + 4])) - 4):
            straights.append([i, int(new_ranks['values'].get(values2[i]))])
        if (int(new_ranks['values'].get(values3[i])) == 13 and int(new_ranks['values'].get(values3[i + 1])) == 12 and int(new_ranks['values'].get(values3[i + 2])) == 11 and
        int(new_ranks['values'].get(values3[i + 3])) == 10 and int(new_ranks['values'].get(values3[-1])) == 1):
            if(int(new_ranks['values'].get(values3[i + 4])) == 9 and int(new_ranks['values'].get(values3[i + 5])) == 8):
                straights.append([i, 8])
            elif(int(new_ranks['values'].get(values3[i + 4])) == 9):
                straights.append([i, 9])
            else:
                straights.append([i, 10])
    straights.sort(reverse=True)
    straight_cards = []
    indices = []
    kicker = []
    for s in straights:
        if s[1] != 10:
            for u in xrange(s[1], s[1] + 5):
                indices.append(hand.find(new_ranks['values'].keys()[new_ranks['values'].values().index(u)]))
            for t in indices:
                for v in t:
                    straight_cards.append(hand[v].suit)
            tallied_flushes = [[x,straight_cards.count(x)] for x in set(straight_cards)]
            for q in tallied_flushes:
                if q[1] >= 5:
                    print(["Straight Flush", 15 - s[1]])
                    return ["Straight Flush", 15 - s[1]]
        else:
            for u in xrange(10, 14):
                indices.append(hand.find(new_ranks['values'].keys()[new_ranks['values'].values().index(u)]))
            indices.append(hand.find(new_ranks['values'].keys()[new_ranks['values'].values().index(1)]))
            for t in indices:
                for v in t:
                    straight_cards.append(hand[v].suit)
            tallied_flushes = [[x,straight_cards.count(x)] for x in set(straight_cards)]
            for q in tallied_flushes:
                if q[1] >= 5:
                    print(["Straight Flush", 5])
                    return ["Straight Flush", 5]
    for i in tallied_values:
        # Four of a Kind
        if i[1] == 4:
            for j in sorted_hand:
                if j.value != i[0]:
                    kicker.append(j.value)
            print(["Four of a Kind", 15 - int(new_ranks['values'].get(i[0])), "Kicker: " + kicker[0]])
            return ["Four of a Kind", 15 - int(new_ranks['values'].get(i[0])), 15 - int(new_ranks['values'].get(kicker[0]))]

        # Find triples and pairs for later
        if i[1] == 3:
            triples.append([i[0], int(new_ranks['values'].get(i[0]))])
        elif i[1] == 2:
            pairs.append([i[0], int(new_ranks['values'].get(i[0]))])

        # Full House
        if len(triples) != 0 and len(pairs) != 0:
            if int(triples[1][1]) < int(pairs[0][1]):
                print(["Full House", 15 - int(triples[0][1]), 15 - int(triples[1][1])] )
                return ["Full House", 15 - triples[0][1], 15 - triples[1][1]]
            else:
                print(["Full House", 15 - int(triples[0][1]), 15 - int(pairs[0][1])] )
                return ["Full House", 15 - triples[0][1], 15 - pairs[0][1]]
        elif len(triples) >= 2:
            print(["Full House", 15 - int(triples[0][1]), 15 - int(triples[1][1])] )
            return ["Full House", 15 - triples[0][1], 15 - triples[1][1]]

    # Flush
    for i in tallied_suits:
        if i[1] >= 5:
            for j in sorted_hand:
                if j.suit == i[0]:
                    print(["Flush", 15 - int(new_ranks['values'].get(j.value))])
                    return ["Flush", 15 - int(new_ranks['values'].get(j.value))]
    # Straight
    if len(straights) > 0:
        print(["Straight", 15 - s[1]])
        return ["Straight", 15 - s[1]]

    # Three of a Kind
    elif len(triples) > 0:
        print(triples)
        for j in sorted_hand:
            if j.value != new_ranks['values'].keys()[new_ranks['values'].values().index(triples[0][1])]:
                kicker.append(j.value)
        print(["Three of a Kind", 15 - triples[0][1]], "Kickers: " + kicker[0] + ", " + kicker[1])
        return ["Three of a Kind", 15 - triples[0][1], [15 - int(new_ranks['values'].get(kicker[0])), 15 - int(new_ranks['values'].get(kicker[1]))]]

    # Two Pairs
    elif len(pairs) > 1:
        print(pairs)
        for j in sorted_hand:
            if (j.value != new_ranks['values'].keys()[new_ranks['values'].values().index(pairs[0][1])]
            and j.value != new_ranks['values'].keys()[new_ranks['values'].values().index(pairs[1][1])]):
                kicker.append(j.value)
        print(["Two Pairs", [15 - pairs[0][1], 15 - pairs[1][1]], "Kickers: " + kicker[0]])
        return ["Two Pairs", [15 - pairs[0][1], 15 - pairs[1][1]], 15 - int(new_ranks['values'].get(kicker[0]))]

    # One Pair
    elif len(pairs) > 0:
        for j in sorted_hand:
            if j.value != new_ranks['values'].keys()[new_ranks['values'].values().index(pairs[0][1])]:
                kicker.append(j.value)
        print(["One Pair", 15 - pairs[0][1]], "Kickers: " + kicker[0] + ", " + kicker[1] + ", " + kicker[2])
        return ["One Pair", 15 - pairs[0][1], [15 - int(new_ranks['values'].get(kicker[0])), 15 - int(new_ranks['values'].get(kicker[1]))], 15 - int(new_ranks['values'].get(kicker[2]))]

    # High Card
    else:
        value_nums = [15 - int(new_ranks['values'].get(x)) for x in values]
        print(["High Card", "Kickers: " + values[0] + ", " + values[1] + ", " + values[2] + ", " + values[3] + ", " + values[4]])
        return ["High Card", value_nums]


handResult(hand)
