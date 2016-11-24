import pydealer
from itertools import groupby
from more_itertools import unique_everseen

deck = pydealer.Deck()
# Shuffle the deck, in place.
# Construct a Stack instance, for use as a hand in this case.
hand = pydealer.Stack()

deck.shuffle()
# Sort the deck, in place.
deck.sort()
# If you want it shuffle when rebuilding:
deck = pydealer.Deck(rebuild=True, re_shuffle=True)
# Deal some cards from the deck.
dealt_cards = deck.deal(7)

# Add the cards to the top of the hand (Stack).
hand.add(dealt_cards)

card = hand[0]

# ``deck`` is a Deck instance, and ``card`` is a Card instance. ``20`` is
# the position (or indice) the card is inserted to.
deck.insert(card, 20)

# ``stack`` is a Stack instance, and ``cards`` is a list of Card instances,
# or a Stack/Deck instance. ``20`` is the  position (or indice) the card is
# inserted into.
stack.insert_list(cards, 20)

# Access the indice of the ``Deck`` instance.
card = deck[25]

# Find the indice(s) of the Ace of Spades.
indices = deck.find("Ace of Spades")

# Construct a list of terms to search for.
terms = ["Ace of Spades", "QH", "2", "Clubs"]
# Find the indices of the cards matching the terms in the given list.
indices = deck.find_list(terms)

# Get the card with the given name from the deck.
cards = deck.get("Ace of Spades")

# Construct a list of terms to search for.
terms = ["Queen of Hearts", "KD", "2", "Clubs", 25]
# Get the cards matching the terms and indices in the given list.
cards = deck.get_list(terms)

deck.empty()
# Or if you would like to keep the emptied cards elsewhere:
cards = deck.empty()

deck_size = deck.size

#Compare whether they have the same decks (order doesn't matter)
result = compare_stacks(deck_x, deck_y)

#Compare two card values
card_x = deck.deal()
card_y = deck.deal()
result = card_x > card_y
result = card_x >= card_y
result = card_x < card_y
result = card_x <= card_y
