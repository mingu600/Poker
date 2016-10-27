from __future__ import division
from deuces import Card, Evaluator, Deck
from itertools import groupby
from operator import itemgetter
import numpy as np
import rl_bot
import pdb

class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = False

    def resetBets(self):
        self.current_bet = 0

    def printName(self):
        print("It's " + self.name + "\'s turn.")

    def calc_hand_strength(self, game):
        score = [0, 0]
        table = game.table[:]
        for i in range(0, 1000):
            deck = Deck()
            new = 0
            player1_hand = self.hand
            player2_hand = deck.draw(2)
            if table == []:
                table = deck.draw(3)
                new = 1
            if len(list(set(player1_hand + table).intersection(player2_hand))) == 0:
                p1_score = game.evaluator.evaluate(table, player1_hand)
                p2_score = game.evaluator.evaluate(table, player2_hand)

                if p1_score < p2_score:
                    score[0] += 1
                    score[1] += 1
                elif p2_score < p1_score:
                    score[1] += 1
                else:
                    score[0] += 1
                    score[1] += 2
                if new == 1:
                    table = []
        strength = score[0] / score[1]
        return strength


class Human(Player):
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = False

    def bet(self, min_bet, current_bet, game=None):
        bet = -5
        min_bet -= current_bet
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
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + " to " + str(bet + self.current_bet))
        return bet




class Bot(Player):
    def __init__(self, name, strategy=None):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = True
        self.round = 0
        if strategy:
            self.bet = strategy

    def end_round(self, winnings):
        pass

    #shutdown behavior for bot
    def end(self):
        pass

    def bet(self, min_bet, current_bet,game=None):
        # For now, bot only checks or calls
        bet = -5
        min_bet -= current_bet
        while bet < min_bet and bet < self.chips:
            if min_bet > self.chips:
                bet = self.chips
            else:
                bet = min_bet
        if bet == min_bet:
            if min_bet == 0:
                print(self.name + " checks.")
            else:
                print(self.name + " calls.")
        elif bet == self.chips:
            print(self.name + "goes All In!")
        elif bet < 0:
            print(self.name + " folds.")
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + "to " + str(bet + current_bet))
        return bet


class Game:
    def __init__(self, player_list, chips, blinds, num_hands=100):
        self.player_list = player_list
        self.player_num = 2
        #self.hands = [[] for i in range(len(player_list))]
        self.num_hands = num_hands
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.blinds = blinds
        self.chips = chips
        self.pot = [0 for x in range(0, 2)]
        self.table_chips = 0
        self.raise_counter = 0
        self.table = []
        self.bet_round = 0
        self.strengths =[[], []]
        self.last_bets = [None,None]

    def dealCards(self):
        for i in range(2):
            self.player_list[i].hand = self.deck.draw(2)
            print self.player_list[i].name
            Card.print_pretty_cards(self.player_list[i].hand)

    def resetChips(self):
        for i in range(2):
            self.player_list[i].chips = self.chips
            self.player_list[i].resetBets

    def shuffleCards(self):
        self.deck = Deck()

    def clearTableChips(self):
        self.table_chips = 0

    def resetPot(self):
        self.pot = 0

    def resetFolds(self):
        for player in self.player_list:
            player.folded = False

    def rounds(self):
        round_num = self.bet_round
        if round_num == 1:
            print("The Flop")
            self.table += self.deck.draw(3)
        elif round_num == 2:
            print("The Turn")
            self.table += [self.deck.draw(1)]
        elif round_num == 3:
            print("The River")
            self.table += [self.deck.draw(1)]
        else:
            print("Showdown")
        Card.print_pretty_cards(self.table)
        for i in range(2):
            self.strengths[i].append(self.player_list[i].calc_hand_strength(self))

    #returns list of players remaining in hand in order of hand strength
    def handRank(self):
        scores = []
        for i in range(2):
            if self.player_list[i].folded == False:
                strength = self.evaluator.evaluate(self.table, self.player_list[i].hand)
                scores.append([i, strength])
                print self.player_list[i].name + ": " + self.evaluator.class_to_string(self.evaluator.get_rank_class(strength))
                Card.print_pretty_cards(self.player_list[i].hand)
        scores = sorted(scores,key=itemgetter(1))
        groups = groupby(scores, itemgetter(1))
        result = [[item[0] for item in data] for (key, data) in groups]
        for i in result[0]:
            print self.player_list[i].name + " wins!"
        return result

    def distribute_chips(self, order=0):

        #keep track of winnings for each player so we can pass it to bots
        winnings = self.player_num*[0]

        if order == 0:
            handRank = self.handRank()
        else:
            handRank = order
        if self.player_list[0].folded == False and self.player_list[1].folded == False:
            self.pot = [min(self.pot), min(self.pot)]
        #print repr(handRank) + '\n'
        if len(handRank[0]) ==1:
            print "Player %s won %d chips" % (self.player_list[handRank[0][0]].name,self.pot[handRank[1][0]])
            self.player_list[handRank[0][0]].chips += sum(self.pot)
            winnings[handRank[0][0]] = self.pot[handRank[1][0]]
            print "Player %s lost %d chips" % (self.player_list[handRank[1][0]].name,self.pot[handRank[1][0]])
            #self.player_list[handRank[1][0]].chips -= self.pot[handRank[1][0]]
            winnings[handRank[1][0]] = -self.pot[handRank[1][0]]

        else:
            print "Player %s won %d chips" % (self.player_list[handRank[0][0]].name,0)
            print "Player %s won %d chips" % (self.player_list[handRank[0][1]].name,0)
        for i in range(2):
            print self.player_list[i].name + ': ' + str(self.player_list[i].chips)
        print "\n"
        for j,i in enumerate(self.player_list):
            if isinstance(i, Bot):
                i.end_round(winnings[j])

    def play(self):
        # Gameplay is initilalized
        self.resetChips()
        # Position of dealer at the beginning
        dealer = 0
        for num_hand in range(self.num_hands):
            self.shuffleCards()
            self.pot = [0 for x in range(2)]
            self.table_chips = 0
            self.raise_counter = 0
            self.table = []
            self.strengths =[[], []]
            counter = 0
            for i in range(2):
                if self.player_list[i].chips > 0:
                    self.player_list[i].folded = False
                else:
                    self.player_list[i].folded = True
            if self.player_list[0].folded == True or self.player_list[1].folded == True:
                print "Game Over"
                break
            print "Next Round"
            self.player_list = np.roll(self.player_list, 1)
            self.last_bets = np.roll(self.last_bets,1)
            # Round starts
            # People are dealt cards at the start of the round
            self.dealCards()
            # Small and Big blinds are put on the table
            self.player_list[(dealer + 1) % 2].chips -= self.blinds[0]
            #self.player_list[(dealer + 1) % self.player_num].current_bet = self.blinds[0]
            print(self.player_list[(dealer + 1) % 2].name + " pays small blind of " + str(self.blinds[0]))
            self.pot[(dealer + 1) % 2] = self.blinds[0]
            self.player_list[dealer % 2].chips -= self.blinds[1]
            #self.player_list[(dealer + 2) % self.player_num].current_bet = self.blinds[1]
            print(self.player_list[dealer % 2].name + " pays big blind of " + str(self.blinds[1]))
            self.pot[(dealer + 2) % self.player_num] = self.blinds[1]
    #self.table_chips += self.blinds[1] + self.blinds[0]
            min_bet = self.blinds[1]
            self.bet_round = 0
            # Rounds of betting
            for j in range(4):
                raise_counter = -10
                raise_const = 1
                counter = 0
                if self.player_list[0].folded == True:
                    self.distribute_chips([[1],[0]])
                    break
                elif self.player_list[1].folded == True:
                    self.distribute_chips([[0],[1]])
                    break
                for i in range(2):
                    if self.player_list[i].chips > 0:
                        counter += 1
                while raise_counter != min_bet:
                    raise_counter = min_bet
                    for i in xrange(dealer + 1, dealer + 2 + raise_const):
                        if self.player_list[i % 2].folded == True or self.player_list[i % 2].chips == 0 or counter == 1:
                            continue
                        print("Current bet: " + str(min_bet))
                        self.player_list[i % 2].printName()
                        amount_bet = self.player_list[i % 2].bet(min_bet, self.pot[i % 2], self)
                        self.last_bets[i % 2] = amount_bet
                        if self.player_list[0].folded == True or self.player_list[1].folded == True :
                            break
                        #still have to verify correct bet
                        self.pot[i % 2] += amount_bet
                        self.player_list[i%2].chips -= amount_bet
                        if min_bet < self.pot[i % 2]:
                            min_bet = self.pot[i % 2]
                            dealer = i
                            raise_const = 0
                            break
                self.bet_round += 1
                self.rounds()

            #distribute chips to winner(s)
            if self.player_list[0].folded == False and self.player_list[1].folded == False:
                print self.strengths
                self.distribute_chips()
            self.resetFolds()


if __name__ == "__main__":
    test = Game([Human("Robert"), Bot("Mingu")], 40, [5, 10])
    test.play()
