import random

def unexploding_roll(sideness_of_dice, number_of_dice = 1):
    result = 0
    for i in range(number_of_dice):
        result += random.randint(1, sideness_of_dice)
    return result

def ranged_weapon_damage_roll(sideness_of_dice, number_of_dice = 1, vital_bonus = False):
    running_total = 0
    if vital_bonus:
        number_of_dice += 2
    for poolMember in range(number_of_dice):
        result = roll_single_die(sideness_of_dice)
        running_total += result
    return running_total

def roll_single_die(sides):
    result = random.randint(1, sides)
    if(result == sides):
        result += roll_single_die(sides)
    return result

def skill_roll(sideness_of_dice, number_of_dice = 1, tn = 5, modifier = 0):
    useGreaterOrEqual = False

    biggest = 0
    onesCount = 0

    for poolMember in range(number_of_dice):
        result = roll_single_die(sideness_of_dice)
        if(result == 1):
            onesCount += 1
        if(result > biggest):
            biggest = result
    if(useGreaterOrEqual):
        evalResult = (onesCount >= (number_of_dice/2))
    else:
        evalResult = (onesCount > (number_of_dice/2))

    biggest += modifier
    if biggest < 0:
        biggest = 1 # FIXME: redo how all the stuff that uses this works so that 0 is valid failure.

    if(evalResult):
        return {'bust': 1}
    elif biggest < tn:
        return {'failure' : biggest}
    else:
        return {'success' : biggest//tn}
