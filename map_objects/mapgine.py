import tcod
import tcod.bsp
import random

from entity import Entity

def generate_map(game_map, player, entities):

    # Our shootout happens outdoors. Outdoors is fully walkable and fully transparent.

    game_map.walkable[:] = True
    game_map.transparent[:] = True

    # for y in range(game_map.height):
    #     for x in range(game_map.width):
    #
    bsp = tcod.bsp.BSP(x=1, y=1, width=game_map.width - 3, height=game_map.height - 3)
    bsp.split_recursive(
        depth=4,
        min_width=8,
        min_height=8,
        max_horizontal_ratio=1.5,
        max_vertical_ratio=1.5,
    )

    num_rooms = 0

    # In pre order, leaf nodes are visited before the nodes that connect them.
    for node in bsp.pre_order():
        if node.children:
            node1, node2 = node.children
            # print('Connect the rooms:\n%s\n%s' % (node1, node2))
        else:
            # print('Dig a room for %s.' % node)

            game_map.walkable[(node.y + 2), (node.x + 2) : (node.x + 2) + (node.width - 3)] = False # changing x, origin y
            game_map.walkable[(node.y + 2) + (node.height - 3), (node.x + 2) : (node.x + 2) + (node.width - 3)] = False # changing x, end y
            game_map.walkable[(node.y + 2) : (node.y + 2) + (node.height - 3), (node.x + 2)] = False # origin x, changing y
            game_map.walkable[(node.y + 2) : (node.y + 2) + (node.height - 3), (node.x + 2) + (node.width - 4)] = False # end x, changing y

            game_map.transparent[(node.y + 2), (node.x + 2) : (node.x + 2) + (node.width - 3)] = False # changing x, origin y
            game_map.transparent[(node.y + 2) + (node.height - 3), (node.x + 2) : (node.x + 2) + (node.width - 3)] = False # changing x, end y
            game_map.transparent[(node.y + 2) : (node.y + 2) + (node.height - 3), (node.x + 2)] = False # origin x, changing y
            game_map.transparent[(node.y + 2) : (node.y + 2) + (node.height - 3), (node.x + 2) + (node.width - 4)] = False # end x, changing y

            for r in range(2):
                doorrand = random.randint(0,3)

                if doorrand == 0:
                    game_map.walkable[(node.y + 2), ((node.x + 2) + ((node.width -3)//2))] = True
                    game_map.transparent[(node.y + 2), ((node.x + 2) + ((node.width -3)//2))] = True
                elif doorrand == 1:
                    game_map.walkable[((node.y + 2) + (node.height - 3)), ((node.x + 2) + ((node.width -3)//2))] = True
                    game_map.transparent[((node.y + 2) + (node.height - 3)), ((node.x + 2) + ((node.width -3)//2))] = True
                elif doorrand == 2:
                    game_map.walkable[((node.y + 2) + ((node.height - 3)//2)), (node.x + 2)] = True
                    game_map.transparent[((node.y + 2) + ((node.height - 3)//2)), (node.x + 2)] = True
                else:
                    game_map.walkable[((node.y + 2) + ((node.height - 3)//2)), ((node.x + 2) + (node.width - 4))] = True
                    game_map.transparent[((node.y + 2) + ((node.height - 3)//2)), ((node.x + 2) + (node.width - 4))] = True
            if num_rooms == 0:
                # We'll put the player in the first room we make.
                player.x = (node.x + 2) + ((node.width - 4)//2)
                player.y = (node.y + 2) + ((node.height - 3)//2)
            else:
                # We'll put one enemy in each other room.
                bandit = Entity((node.x + 2) + ((node.width - 4)//2), (node.y + 2) + ((node.height - 3)//2), 'b', tcod.black, 'Bandit', True)
                entities.append(bandit)
            num_rooms += 1
