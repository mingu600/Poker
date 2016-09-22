from __future__ import division
from deuces import Card, Evaluator, Deck
from itertools import groupby
from operator import itemgetter
import numpy as np

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
        for i in range(0, 1000):
            deck = Deck()
            player1_hand = self.hand
            player2_hand = deck.draw(2)
            if len(list(set(player1_hand + game.table).intersection(player2_hand))) == 0:
                p1_score = game.evaluator.evaluate(game.table, player1_hand)
                p2_score = game.evaluator.evaluate(game.table, player2_hand)

                if p1_score < p2_score:
                    score[0] += 1
                    score[1] += 1
                elif p2_score < p1_score:
                    score[1] += 1
                else:
                    score[0] += 1
                    score[1] += 2
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

    def bet(self, min_bet, current_bet):
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
            self.hand = []
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + " to " + str(bet + self.current_bet))
        self.chips -= bet
        return bet




class Bot(Player):
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = True

    def bet(self, min_bet, current_bet):
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
            self.hand = []
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + "to " + str(bet + current_bet))
        self.chips -= bet
        return bet


class Game:
    def __init__(self, player_list, chips, blinds):
        self.player_list = player_list
        self.player_num = len(player_list)
        #self.hands = [[] for i in range(len(player_list))]
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.blinds = blinds
        self.chips = chips
        self.pot = [0 for x in range(0,self.player_num)]
        self.table_chips = 0
        self.raise_counter = 0
        self.table = []
        self.strengths =[[], []]

    def dealCards(self):
        for i in range(0, self.player_num):
            self.player_list[i].hand = self.deck.draw(2)
            Card.print_pretty_cards(self.player_list[i].hand)

    def resetChips(self):
        for i in range(0, self.player_num):
            self.player_list[i].chips = self.chips
            self.player_list[i].resetBets

    def shuffleCards(self):
        self.deck = Deck()

    def clearTableChips(self):
        self.table_chips = 0

    def resetPot(self):
        self.pot = 0

    def rounds(self, round_num):
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
        for i in range(len(self.player_list)):
            self.strengths[i].append(self.player_list[i].calc_hand_strength(self))

    #returns list of players remaining in hand in order of hand strength
    def handRank(self):
        scores = []
        for i in range(0, self.player_num):
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

    def play(self):
        # Gameplay is initilalized
        self.resetChips()
        # Position of dealer at the beginning
        dealer = 0
        while True:
            self.shuffleCards()
            self.pot = [0 for x in range(0,self.player_num)]
            self.table_chips = 0
            self.raise_counter = 0
            self.table = []
            self.strengths =[[], []]
            counter = 0
            for i in range(self.player_num):
                if self.player_list[i].chips <= 0:
                    counter += 1
                else:
                    self.player_list[i].folded = False
            if counter == self.player_num - 1:
                print "Game Over"
                break
            print "Next Round"
            self.player_list = np.roll(self.player_list, 1)
            min_bet = 0
            # Round starts
            # People are dealt cards at the start of the round
            self.dealCards()
            # Small and Big blinds are put on the table
            self.player_list[(dealer + 1) % self.player_num].chips -= self.blinds[0]
            #self.player_list[(dealer + 1) % self.player_num].current_bet = self.blinds[0]
            print(self.player_list[(dealer + 1) % self.player_num].name + " pays small blind of " + str(self.blinds[0]))
            self.pot[(dealer + 1) % self.player_num] = self.blinds[0]
            self.player_list[(dealer + 2) % self.player_num].chips -= self.blinds[1]
            #self.player_list[(dealer + 2) % self.player_num].current_bet = self.blinds[1]
            print(self.player_list[(dealer + 2) % self.player_num].name + " pays big blind of " + str(self.blinds[1]))
            self.pot[(dealer + 2) % self.player_num] = self.blinds[1]
    #self.table_chips += self.blinds[1] + self.blinds[0]
            min_bet = self.blinds[1]
            people_in = self.player_num
            turn = 0
            # Rounds of betting
            for j in xrange(0, 4):
                raise_counter = -10
                place = dealer + 2
                raise_const = 1
                counter = 0
                for i in range(self.player_num):
                    if self.player_list[i].chips > 0:
                        counter += 1
                while raise_counter != min_bet:
                    raise_counter = min_bet
                    for i in xrange(place + 1, place + people_in + raise_const):
                        if self.player_list[i % people_in].folded == True or self.player_list[i % people_in].chips == 0 or counter == 1:
                            continue
                        print("Current bet: " + str(min_bet))
                        self.player_list[i % people_in].printName()
                        amount_bet = self.player_list[i % people_in].bet(min_bet,self.pot[i % people_in])
                        #still have to verify correct bet
                        self.pot[i % people_in] += amount_bet
                        tot = self.pot[i % people_in]
                        '''
                        self.table_chips += amount_bet
                        tot = amount_bet + self.player_list[i % people_in].current_bet
                        self.player_list[i % self.player_num].current_bet += amount_bet
                        print(self.player_list[i % people_in].chips)
                        '''
                        if min_bet < tot:
                            min_bet = tot
                            place = i
                            raise_const = 0
                            break
                #self.pot += self.table_chips
                #self.clearTableChips()
                #for i in xrange(0, self.player_num):
                #    self.player_list[i].resetBets()
                turn += 1
                self.rounds(turn)

            #distribute chips to winner(s)
            print self.strengths
            handRank = self.handRank()
            #print repr(handRank) + '\n'
            for winner in handRank:
                #print repr(winner) + '\n'
                #for tied winners, sort by the amount they've bet (least first)
                winner.sort(key = lambda x: self.pot[x])
                #loop over tied winners, resolve smaller sidepots first
                for i in range(0,len(winner)):
                #loop over pot and grab their bet size from every other player
                    amount_bet = self.pot[winner[i]]
                    chips_won = 0
                    for j in range(0,len(self.pot)):
                        if self.pot[j] > amount_bet:
                            self.pot[j] -= amount_bet
                            chips_won += amount_bet
                        else:
                            chips_won += self.pot[j]
                            self.pot[j] = 0
                    #split chips proportionally among players that bet enough for this pot
                    for j in range(i,len(winner)):
                        self.player_list[winner[j]].chips += int(chips_won*(1/(len(winner)-i)))
                        #print "player %d won %d chips \n" % (winner[j],chips_won*(1/(len(winner)-i)))
                        print "Player %s won %d chips" % (self.player_list[winner[j]].name,chips_won*(1/(len(winner)-i)))
            for i in range(self.player_num):
                print self.player_list[i].chips
            print "\n"


if __name__ == "__main__":
    test = Game([Bot("Robert"), Human("Mingu")], 40, [5, 10])
    test.play()
