import tcod
from game_messages import Message
from renderengine import RenderOrder

def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.woundable = None
    # monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message
