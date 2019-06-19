class Trait:

    def __init__(self, levelDice = 1, traitDie = 4):
        self.levelDice = levelDice
        self.traitDie = traitDie

    # def __repr__(self):
    #     return str({'levelDice': self.levelDice,
    #                 'traitDie': self.traitDie})

    def __repr__(self):
        return (str(self.levelDice) + "d" +str(self.traitDie))
