import tcod

def generate_map(game_map, number_of_rooms):

    # Our shootout happens outdoors. Outdoors is fully walkable and fully transparent.

    game_map.walkable[:] = True
    game_map.transparent[:] = True

    # for y in range(game_map.height):
    #     for x in range(game_map.width):
    #
