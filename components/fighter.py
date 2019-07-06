import rgb
from game_messages import Message

class Fighter:
    def __init__(self, size, heavy_armor=None, light_armor=None, action_hand=None, shots=6):
        self.size = size
        self.heavy_armor = heavy_armor
        self.light_armor = light_armor
        self.body_wounds = {'head': 0,
                            'guts': 0,
                            'right_arm': 0,
                            'left_arm': 0,
                            'right_leg': 0,
                            'left_leg': 0}
        self.shots=shots

        self.action_hand = action_hand
        if self.action_hand:
            self.action_hand.owner = self

    def reduce_damage_dice(self, num, sides):
        if not self.heavy_armor:
            return (num, sides)
        armor_temp = self.heavy_armor
        while armor_temp > 0:
            if sides == 20:
                sides = 12
            elif sides == 12:
                sides = 10
            elif sides == 10:
                sides = 8
            elif sides == 8:
                sides = 6
            elif sides == 6:
                sides = 4
            else: # sides == 4
                if num > 0:
                    num -= 1
            armor_temp -= 1
        return (num, sides)

    def get_most_severe_wound(self):
        highest_number_wounds = 0
        most_injured_part = None
        for location, wounds in self.body_wounds.items():
            if wounds > highest_number_wounds:
                highest_number_wounds = wounds
                most_injured_part = location
        return (most_injured_part, highest_number_wounds)

    def take_positional_damage(self, damage, location, fate_pot=None, player_fate=None):
        if self.light_armor:
            damage += self.light_armor
        wounds_total = damage // self.size

        fate_message = ""

        if(player_fate is not None and fate_pot is not None):
            if wounds_total >= 3 and player_fate['blue'] > 0:
                fate_message = "After spending 1 blue fate chip, "
                wounds_total -= 3
                player_fate['blue'] -= 1
            elif wounds_total >= 2 and player_fate['red'] > 0:
                fate_message = "After spending 1 red fate chip, "
                wounds_total -= 2
                player_fate['red'] -= 1
            elif wounds_total >= 1 and player_fate['white'] > 0:
                fate_message = "After spending 1 white fate chip, "
                wounds_total -= 1
                player_fate['white'] -= 1

        self.body_wounds[location] += wounds_total
        return Message(fate_message + self.owner.name + " was hit for " + str(damage) + " causing " + str(wounds_total) + " wounds!")#, rgb(255, 200, 0))

    def take_simple_damage(self, damage):
        return self.take_positional_damage(damage, 'guts')
