import tcod
import tcod.bsp

def generate_map(game_map, number_of_rooms):

    # Our shootout happens outdoors. Outdoors is fully walkable and fully transparent.

    game_map.walkable[:] = True
    game_map.transparent[:] = True

    # for y in range(game_map.height):
    #     for x in range(game_map.width):
    #
    print(game_map.width)
    bsp = tcod.bsp.BSP(x=1, y=1, width=game_map.width - 2, height=game_map.height - 2)
    bsp.split_recursive(
        depth=4,
        min_width=5,
        min_height=5,
        max_horizontal_ratio=1.5,
        max_vertical_ratio=1.5,
    )

    # In pre order, leaf nodes are visited before the nodes that connect them.
    for node in bsp.pre_order():
        if node.children:
            node1, node2 = node.children
            # print('Connect the rooms:\n%s\n%s' % (node1, node2))
        else:
            # print('Dig a room for %s.' % node)

            game_map.walkable[node.y, node.x : node.x + node.width] = False # changing x, origin y
            game_map.walkable[node.y + node.height, node.x : node.x + node.width] = False # changing x, end y
            game_map.walkable[node.y : node.y + node.height, node.x] = False # origin x, changing y
            game_map.walkable[node.y : node.y + node.height, node.x + node.width] = False # end x, changing y

            game_map.transparent[node.y, node.x : node.x + node.width] = False # changing x, origin y
            game_map.transparent[node.y + node.height, node.x : node.x + node.width] = False # changing x, end y
            game_map.transparent[node.y : node.y + node.height, node.x] = False # origin x, changing y
            game_map.transparent[node.y : node.y + node.height, node.x + node.width] = False # end x, changing y
