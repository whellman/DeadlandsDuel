import tcod

def generate_map(game_map, map_width, map_height):

    # Our shootout happens outdoors. Outdoors is fully walkable and fully transparent.

    game_map.walkable[:] = True
    game_map.transparent[:] = True

    # for y in range(map_height):
    #     for x in range(map_width):
