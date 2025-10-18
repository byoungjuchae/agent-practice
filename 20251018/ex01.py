#create_react_agent 활용하여 Agent 만들어보기
import random
from langgraph.prebuilt import create_react_agent


def random_dice(dice_count : int) -> str :
    dice_value = []
    for x in range(dice_count) :
        dice = random.randint(1,6)
        dice_value.append(dice)

    return dice_value



random_dice_value = random_dice(3)
print(type(random_dice_value))
