from __future__ import division
from deuces import Card, Evaluator, Deck
from itertools import groupby
from operator import itemgetter
import numpy as np
import rl_bot
import pdb
import argparse as ap
import time


from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


# This is the player class. Humans and bots are both Players with chips and cards.
class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = False

    # Reset your betting amount
    def resetBets(self):
        self.current_bet = 0

    # For printing turn order
    def printName(self):
        print("It's " + self.name + "\'s turn.")

    # Simulates 500 games with the given information of the current state and derives hand strength
    # Returns the likelihood that the player will win the round if the entire round is played out
    def calc_hand_strength(self, game):
        score = [0, 0]
        table = game.table[:]
        for i in range(0, 500):
            deck = Deck()
            new = 0
            player1_hand = self.hand
            player2_hand = deck.draw(2)
            if table == []:
                table = deck.draw(3)
                while len(set(player1_hand + player2_hand + table)) < len(player1_hand) + len(player2_hand) + len(table):
                    player2_hand = deck.draw(2)
                    table = deck.draw(3)
                new = 1
            if len(player1_hand) + len(player2_hand) + len(table) == len(set(player1_hand + player2_hand + table)):
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

# This is the Human class, a subclass of Player
class Human(Player):
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0
        self.current_bet = 0
        self.folded = False
        self.bot = False

    # How people can bet, mainly for printing purposes
    # If your bet amount is -10, then this is synonymous with folding
    def bet(self, min_bet, current_bet, times, game=None):
        bet = -5
        min_bet -= current_bet
        # You are reprompted if you try to bet less than you should
        while bet < min_bet and bet != -10:
            print("Enter your bet, minimum to call is " + str(min_bet) + ", to fold enter -10")
            try:
                bet = int(input())
            except ValueError:
                print("Unable to read input. Please try again!")
        # If you bet more than you have, you bet all your chips
        if bet > self.chips:
            print("All In!")
            bet = self.chips
        # If you bet the minimum, this is equivalent to check/call
        if bet == min_bet:
            if min_bet == 0:
                print(self.name + " checks.")
            else:
                print(self.name + " calls.")
        # If you bet -10, you folded
        elif bet < 0:
            print(self.name + " folds.")
            bet = 0
            self.folded = True
        else:
            print(self.name + " raises " + str(bet - min_bet) + " to " + str(bet + self.current_bet))
        return bet



# Bot is also a subclass of player
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

    #shutdown behavior for bot
    def end(self):
        pass

    def bet(self, min_bet, current_bet,times,game=None):
        # The default betting behavior is to always call. This is overridden with our RL bot.
        # See comments in bet() for Human
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

# Game Class- the game holds all the information about the game, and play() starts a poker game
class Game:
    def __init__(self, player_list, chips, blinds, num_hands=100):
        self.player_list = player_list
        self.player_num = 2
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
        self.times = dict([('main',{'total':0,'count':0}),('strength',{'total':0,'count':0})]+[(player.name,{'total':0,'count':0}) for player in player_list])

    # Function for dealing cards to every player
    def dealCards(self):
        for i in range(2):
            self.player_list[i].hand = self.deck.draw(2)
            print self.player_list[i].name
            Card.print_pretty_cards(self.player_list[i].hand)

    # Reset player chip amounts and bets
    def resetChips(self):
        for i in range(2):
            self.player_list[i].chips = self.chips
            self.player_list[i].resetBets

    # Shuffle deck
    def shuffleCards(self):
        self.deck = Deck()

    # Clear chips off table
    def clearTableChips(self):
        self.table_chips = 0

    # Reset the pot to 0
    def resetPot(self):
        self.pot = 0

    # Reset every player's flag that indicates folding
    def resetFolds(self):
        for player in self.player_list:
            player.folded = False

    # Adds one card to the table and prints cards each time the round ends
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
            if self.pot[0] > self.pot[1]:
                self.player_list[0].chips += self.pot[0] - self.pot[1]
                self.pot = [min(self.pot), min(self.pot)]
            elif self.pot[0] < self.pot[1]:
                self.player_list[1].chips += self.pot[1] - self.pot[0]
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
            self.player_list[0].chips += self.pot[0]
            self.player_list[1].chips += self.pot[1]
        for i in range(2):
            print self.player_list[i].name + ': ' + str(self.player_list[i].chips)
        print "\n"
        for j,i in enumerate(self.player_list):
                i.end_round(self, winnings[j])

    # Starts one game of poker
    def play(self):
        t1 = time.time()

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
                for j,i in enumerate(self.player_list):
                    if isinstance(i, Bot):
                        i.end()
                break
            for j,i in enumerate(test.player_list):
                if isinstance(i, rl_bot.RLBot):
                    i.learner.round = 0
            print "Next Round"
            self.player_list = np.roll(self.player_list, 1)
            self.last_bets = np.roll(self.last_bets,1)
            # Round starts
            # People are dealt cards at the start of the round
            self.dealCards()

            # Small and Big blinds are put on the table
            print(self.player_list[(dealer + 1) % 2].name + " pays small blind of " + str(self.blinds[0]))
            self.player_list[(dealer + 1) % 2].chips -= self.blinds[0]
            self.pot[(dealer + 1) % 2] = self.blinds[0]
            print(self.player_list[dealer % 2].name + " pays big blind of " + str(self.blinds[1]))
            self.pot[dealer % 2] = min([self.player_list[dealer % 2].chips,self.blinds[1]])
            self.player_list[dealer % 2].chips -= min([self.player_list[dealer % 2].chips,self.blinds[1]])
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

                        #track amount of time for player
                        t2 = time.time()
                        amount_bet = self.player_list[i % 2].bet(min_bet, self.pot[i % 2], self.times, self)
                        self.times[self.player_list[i % 2].name]['count'] += 1
                        self.times[self.player_list[i % 2].name]['total'] += time.time() - t2

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
                self.distribute_chips()
            self.resetFolds()

        #update times
        self.times['main']['count'] += 1
        self.times['main']['total'] += time.time() - t1



if __name__ == "__main__":
    #parse command line
    np.set_printoptions(suppress=True)
    #bots of players
    p1 = rl_bot.RLBot
    p1_args = []
    p2 = rl_bot.GreedyBot
    p2_args = []

    #number of rounds to run
    length = 100

    #chips to initiate rounds with
    chips = 40

    #blinds (only track the little blind)
    lb = 5

    #construct parser
    parser = ap.ArgumentParser(description='Input parameters to run the game')
    parser.add_argument("-n","--number-iterations",help="number of times to simulate game between two bots",type=int,dest="n")
    parser.add_argument("-p1","--player1-controller",help="name of program to control player 1. [rlbot, greedy, human]. For bots, you can specify -p1 rlbot [epsilon] [gamma]",type=str,dest="p1",nargs='+')
    parser.add_argument("-p2","--player2-controller",help="name of program to control player 2. [rlbot, greedy, human]. For bots, you can specify, -p2 rlbot [epsilon] [gamma]",type=str,dest="p2",nargs='+')
    parser.add_argument("-c","--start-chips",help="number of chips to give players at the beginning of the game",type=int,dest="c")
    parser.add_argument("-lb","--little-blind",help="number of chips for little blind, big blind will be double this number",type=int,dest="lb")
    parser.add_argument("-v","--verbose",help="allow output to stdout from print statements throughout code",action="store_true")
    parser.add_argument("-p","--performance",help="performance statistics for player 1",action="store_true")
    parser.add_argument("-t","--timing",help="print time usage statistics for poker and player components",action="store_true")
    parser.add_argument("--custom",help="run custom execution plan",action="store_true")


    #parse input
    results = parser.parse_args(sys.argv[1:])
    if results.performance:
        score = 0
        test = Game([rl_bot.GreedyBot("Robert"), rl_bot.RLBot("Mingu")], 40, [5, 10])
        for n in range(200):
            with suppress_stdout():
                test.play()
                for j,i in enumerate(test.player_list):
                    if isinstance(i, rl_bot.RLBot):
                        if i.chips > 0:
                            score += 1
                        i.learner.round = 0
                        i.end()
            if n % 50 == 0:
                print n
                #rl_bot.RLBot("Mingu").last_bet_graph(n)
                #print ''
        print 'Win Percentage: ' + str(float(score) / 2) + '%'
        sys.exit(1)

    if results.custom:
        score = 0
        for x in range(10):
            test = Game([rl_bot.GreedyBot("Robert"), rl_bot.RLBot("Mingu")], 40, [5, 10])
            for n in range(200):
                #with suppress_stdout():
                test.play()
                for j,i in enumerate(test.player_list):
                    if isinstance(i, rl_bot.RLBot):
                        i.learner.round = 0
                        i.end()
                print n
            test = Game([rl_bot.RLBot("Robert"), rl_bot.RLBot("Mingu")], 40, [5, 10])
            for n in range(50):
                with suppress_stdout():
                    test.play()
                    for j,i in enumerate(test.player_list):
                        if isinstance(i, rl_bot.RLBot):
                            i.learner.round = 0
                            i.end()
                print n
            print ""
            print x
    else:
        if results.n is not None:
            length = results.n
        if results.c is not None:
            chips = results.c
        if results.lb is not None:
            lb = results.lb
        #pass string representing player ('p1','p2'), as well as controller from command line args
        def assign_player(p,controller):
            if controller == 'greedy':
                locals()[p] = rl_bot.GreedyBot
            elif controller == 'rlbot':
                locals()[p] = rl_bot.RLBot
            elif controller == 'human':
                if not results.verbose:
                    print >> sys.stderr, 'Cannot have human player without verbose output'
                    sys.exit(1)
                locals()[p] = Human
            else:
                print >> sys.stderr, 'Unrecognised player controller. heads_up.py -h to lean more'
                sys.exit(1)
        #we will use directly the flags for output
        if results.p1 is not None:
            assign_player("p1",results.p1[0])
            p1_args = map(float, results.p1[1:])
        if results.p2 is not None:
            assign_player("p2",results.p2[0])
            p2_args = map(float, results.p2[1:])

        test = Game([p1("Robert", *p1_args), p2("Mingu", *p2_args)], chips, [lb, 2*lb])

        t = time.time()
        for n in range(length):
            def play_games():
                test.play()
                for j,i in enumerate(test.player_list):
                    if isinstance(i, rl_bot.RLBot):
                        i.learner.round = 0
                        i.end()

            if results.verbose:
                output = play_games()
            else:
                with suppress_stdout():
                    output = play_games()
            if n % 25 == 0:
                print n

        if results.timing:
            print "Total time taken: {:0}".format(time.time() - t)
            for k,v in test.times.items():
                print "Code Segment: {}, Times executed: {}, Total time: {}, Average Time: {}".format(k,v['count'],v['total'],float(v['total'])/v['count'])
