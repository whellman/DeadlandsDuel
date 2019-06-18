import random


def roll_single_die(sides):
    result = random.randint(1, sides)
    if(result == sides):
        result += roll_single_die(sides)
    return result

def skill_roll(sideness_of_dice, number_of_dice = 1, tn = 5):
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
    print("raw biggest " + str(biggest))
    print("raw onesCount " + str(onesCount))
    if(evalResult):
        return {'bust': 1}
    elif biggest < tn:
        return {'failure' : 1}
    else:
        return {'success' : biggest//tn}
