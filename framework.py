import pydealer

class Player:
    def __init__(self, name):
        self.hand = []
        self.name = name
        self.chips = 0


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

    def dealCards(self):
        for i in range(0, self.player_num):
            self.player_list[i].hand = self.deck.deal(2)

    def resetChips(self):
        for i in range(0, self.player_num):
            self.player_list[i].chips = self.chips

    def shuffleCards(self):
        self.deck = pydealer.Deck()
        self.deck.shuffle()

    def clearTableChips(self):
        self.table_chips = 0

    def resetPot(self):
        self.pot = 0

    def play(self):
        # Gameplay is initilalized
        self.resetChips()
        self.shuffleCards()
        # Position of dealer at the beginning
        dealer = 0

        # Round starts
        # People are dealt cards at the start of the round
        self.dealCards()
        # Small and Big blinds are put on the table
        self.player_list[dealer + 1].chips -= self.blinds[1]
        self.player_list[dealer + 2].chips -= self.blinds[0]
        self.pot += self.blinds[1] + self.blinds[0]




if __name__ == "__main__":
    test = Game([Player("Robert"), Player("Mingu")])
    test.dealCards()
