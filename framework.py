import pydealer
from itertools import groupby
from more_itertools import unique_everseen

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

class Human:
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False

    def bet(self, min_bet):
        bet = -5
        min_bet -= self.current_bet
        while bet < min_bet and bet != -10:
            print("Enter your bet, minimum to call is " + str(min_bet) + ", to fold enter -10")
            try:
                bet = int(input())
            except ValueError:
                print("Unable to read input. Please try again!")
        if bet > self.chips:
            print("All In!")
            bet = self.chips
        if bet == min_bet:
            if min_bet == 0:
                print(self.name + " checks.")
            else:
                print(self.name + " calls.")
        elif bet < 0:
            print(self.name + " folds.")
            self.hand = []
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + " to " + str(bet + self.current_bet))
        self.chips -= bet
        return bet

    def resetBets(self):
        self.current_bet = 0

    def printName(self):
        print("It's " + self.name + "\'s turn.")

    def handResult(self, hand):
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


class Bot:
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False

    def bet(self, min_bet):
        # For now, bot only checks or calls
        bet = -5
        min_bet -= self.current_bet
        while bet < min_bet:
            bet = min_bet
        if bet == min_bet:
            if min_bet == 0:
                print(self.name + " checks.")
            else:
                print(self.name + " calls.")
        elif bet < 0:
            print(self.name + " folds.")
            self.hand = []
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + "to " + str(bet + self.current_bet))
        self.chips -= bet
        return bet

    def resetBets(self):
        self.current_bet = 0

    def printName(self):
        print("It's " + self.name + "\'s turn.")

    def handResult(self, hand):
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

class Game:
    def __init__(self, player_list, chips, blinds):
        self.player_list = player_list
        self.player_num = len(player_list)
        #self.hands = [[] for i in range(len(player_list))]
        self.deck = pydealer.Deck()
        self.deck.shuffle()
        self.blinds = blinds
        self.chips = chips
        self.pot = 0
        self.table_chips = 0
        self.raise_counter = 0
        self.table = []

    def dealCards(self):
        for i in range(0, self.player_num):
            self.player_list[i].hand = self.deck.deal(2)
            print(self.player_list[i].hand[0], self.player_list[i].hand[1])

    def resetChips(self):
        for i in range(0, self.player_num):
            self.player_list[i].chips = self.chips
            self.player_list[i].resetBets

    def shuffleCards(self):
        self.deck = pydealer.Deck()
        self.deck.shuffle()

    def clearTableChips(self):
        self.table_chips = 0

    def resetPot(self):
        self.pot = 0

    def rounds(self, round_num):
        if round_num == 1:
            print("The Flop")
            self.table.append(self.deck.deal(3))
        elif round_num == 2:
            print("The Turn")
            self.table.append(self.deck.deal(1))
        elif round_num == 3:
            print("The River")
            self.table.append(self.deck.deal(1))
        else:
            print("Showdown")
        print(self.table)

    def play(self):
        # Gameplay is initilalized
        self.resetChips()
        self.shuffleCards()
        # Position of dealer at the beginning
        dealer = 0
        min_bet = 0
        # Round starts
        # People are dealt cards at the start of the round
        self.dealCards()
        # Small and Big blinds are put on the table
        self.player_list[(dealer + 1) % self.player_num].chips -= self.blinds[0]
        self.player_list[(dealer + 1) % self.player_num].current_bet = self.blinds[0]
        print(self.player_list[(dealer + 1) % self.player_num].name + " pays small blind of " + str(self.blinds[0]))
        self.player_list[(dealer + 2) % self.player_num].chips -= self.blinds[1]
        self.player_list[(dealer + 2) % self.player_num].current_bet = self.blinds[1]
        print(self.player_list[(dealer + 2) % self.player_num].name + " pays big blind of " + str(self.blinds[1]))
        self.table_chips += self.blinds[1] + self.blinds[0]
        min_bet = self.blinds[1]
        people_in = self.player_num
        turn = 0

        # Rounds of betting
        for j in xrange(0, 4):
            raise_counter = -10
            place = dealer + 2
            raise_const = 1
            while raise_counter != min_bet:
                raise_counter = min_bet
                for i in xrange(place + 1, place + people_in + raise_const):
                    if self.player_list[i % people_in].folded == True or self.player_list[i % people_in].chips == 0:
                        continue
                    print("Current bet: " + str(min_bet))
                    self.player_list[i % people_in].printName()
                    amount_bet = self.player_list[i % people_in].bet(min_bet)
                    self.table_chips += amount_bet
                    tot = amount_bet + self.player_list[i % people_in].current_bet
                    self.player_list[i % self.player_num].current_bet += amount_bet
                    print(self.player_list[i % people_in].chips)
                    if min_bet < tot:
                        min_bet = tot
                        place = i
                        raise_const = 0
                        break
            self.pot += self.table_chips
            self.clearTableChips()
            for i in xrange(0, self.player_num):
                self.player_list[i].resetBets()
            min_bet = 0
            turn += 1
            self.rounds(turn)

            stack = pydealer.Stack()
            stack.add()
            for i in xrange(0, self.player_num):
                for j in
                    self.player_list[i].hand
                    self.player_list[i].handResult(self.player_list[i].hand)





if __name__ == "__main__":
    test = Game([Bot("Robert"), Human("Mingu"), Human("Alex"), Bot("Jennifer")], 1000, [5, 10])
    test.play()
