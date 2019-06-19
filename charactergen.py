import pydealer

class Trait:

    def __init__(self, levelDice = 1, traitDie = 4):
        self.levelDice = levelDice
        self.traitDie = trait

class Character:

    def __init__(self):
        traits = character_generator()

        self.deftness = traits['deftness']
        self.nimbleness = traits['nimbleness']
        self.quickness = traits['quickness']
        self.strength = traits['strength']
        self.vigor = traits['vigor']
        self.cognition = traits['cognition']
        self.knowledge = traits['knowledge']
        self.mien = traits['mien']
        self.smarts = traits['smarts']
        self.spirit = traits['spirit']

        self.grit = 0
        self.pace = nimbleness.traitDie
        self.size = 6
        self.wind = vigor.traitDie + spirit.traitDie

        self.aptitudePoints = self.cognition.traitDie + self.knowledge.traitDie + self.smarts.traitDie

def character_generator():

    mapping = {'Ace': 12,
               'King': 10,
               'Queen': 10,
               'Jack': 8,
               '10': 8,
               '9': 8,
               '8': 6,
               '7': 6,
               '6': 6,
               '5': 6,
               '4': 6,
               '3': 6,
               '2': 4,
               'Spades': 4,
               'Hearts': 3,
               'Diamonds': 2,
               'Clubs': 1}

    deck = pydealer.Deck()
    deck.shuffle()

    # Deadlands rules are deal 12, toss two from 3 to A inclusive (2, Jkr must stay)
    # selection = deck.deal(12)

    # But for now, we'll just take 10 randomly and live with it.
    selection = deck.deal(10)

    traits = {
    'deftness': Trait(mapping[selection[0].suit], mapping[selection[0].value]),
    'nimbleness': Trait(mapping[selection[1].suit], mapping[selection[1].value]),
    'quickness': Trait(mapping[selection[2].suit], mapping[selection[2].value]),
    'strength': Trait(mapping[selection[3].suit], mapping[selection[3].value]),
    'vigor': Trait(mapping[selection[4].suit], mapping[selection[4].value]),
    'cognition': Trait(mapping[selection[5].suit], mapping[selection[5].value]),
    'knowledge': Trait(mapping[selection[6].suit], mapping[selection[6].value]),
    'mien': Trait(mapping[selection[7].suit], mapping[selection[7].value]),
    'smarts': Trait(mapping[selection[8].suit], mapping[selection[8].value]),
    'spirit': Trait(mapping[selection[9].suit], mapping[selection[9].value])}
    # deftness = Trait(mapping[selection[0].suit], mapping[selection[0].value])
    # nimbleness = Trait(mapping[selection[1].suit], mapping[selection[1].value])
    # quickness = Trait(mapping[selection[2].suit], mapping[selection[2].value])
    # strength = Trait(mapping[selection[3].suit], mapping[selection[3].value])
    # vigor = Trait(mapping[selection[4].suit], mapping[selection[4].value])
    #
    # cognition = Trait(mapping[selection[5].suit], mapping[selection[5].value])
    # knowledge = Trait(mapping[selection[6].suit], mapping[selection[6].value])
    # mien = Trait(mapping[selection[7].suit], mapping[selection[7].value])
    # smarts = Trait(mapping[selection[8].suit], mapping[selection[8].value])
    # spirit = Trait(mapping[selection[9].suit], mapping[selection[9].value])

    return traits
