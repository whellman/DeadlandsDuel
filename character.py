import pydealer

from trait import Trait

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
        self.pace = self.nimbleness.traitDie
        self.size = 6
        self.wind = self.vigor.traitDie + self.spirit.traitDie
        # FIXME: Below this point isn't __repr__'d.
        self.aptitudePoints = self.cognition.traitDie + self.knowledge.traitDie + self.smarts.traitDie

        self.shootin_pistol = {'aptitude': 2,
                                'trait': self.deftness.traitDie}

    def __repr__(self):
        return str({'deftness': self.deftness,
                    'nimbleness': self.nimbleness,
                    'quickness': self.quickness,
                    'strength': self.strength,
                    'vigor': self.vigor,
                    'cognition': self.cognition,
                    'knowledge': self.knowledge,
                    'mien': self.mien,
                    'smarts': self.smarts,
                    'spirit': self.spirit,
                    'grit': self.grit,
                    'pace': self.pace,
                    'size': self.size,
                    'wind': self.wind})

    # A player can move twice their Pace, in Yards, per round. One yard is three feet.
    # We're assuming a standard D&D-style 5 feet per map square,
    # and not really worrying about diagonals yet (if at all).

    def get_movement_budget(self):
        #        pace.    run   y->f  f->squares
        return ((self.pace * 2) * 3) // 5

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
