import pydealer

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
        while bet < min_bet and bet != -10 and bet <= self.chips:
            print("Enter your bet, minimum to call is " + str(min_bet) + ", to fold enter -10")
            try:
                bet = int(input())
            except ValueError:
                print("Unable to read input. Please try again!")
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
                    if self.player_list[i % people_in].folded == True:
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




if __name__ == "__main__":
    test = Game([Bot("Robert"), Human("Mingu"), Human("Alex"), Bot("Jennifer")], 1000, [5, 10])
    test.play()
