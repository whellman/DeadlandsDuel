import tcod
import tcod.event

import pydealer

from entity import Entity, get_blocking_entities_at_location
from input_handler import handle_events
from map_objects.mapgine import generate_map
from renderengine import render_all


def main():
    screen_width = 80
    screen_height = 50
    cardtable_width = 18
    cardtable_height = screen_height
    cardtable_x = screen_width - cardtable_width
    map_width = screen_width - cardtable_width
    map_height = screen_height


    mapcon = tcod.console.Console(map_width, map_height)
    cardtable = tcod.console.Console(cardtable_width, cardtable_height)


    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', tcod.white, 'Player', True)
    entities = [player]

    game_map = tcod.map.Map(map_width, map_height)
    generate_map(game_map, player, entities)

    fov_recompute = True


    tcod.console_set_custom_font('cp437_10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False, tcod.RENDERER_SDL2, vsync=True)

    while True:

        if fov_recompute:
            game_map.compute_fov(player.x, player.y, algorithm=tcod.FOV_PERMISSIVE(5))

        render_all(root_console, entities, mapcon, game_map, cardtable, cardtable_x)

        tcod.console_flush()

        action = handle_events()

        move = action.get('move')

        if move:
            dx, dy = move
            # newx = self.x + dx
            # newy = self.y + dy
            # if not ((newx < 0) or (newy < 0) or (newx >= game_map.width) or (newy >= game_map.height)):
            #     if game_map.walkable[newy, newx]:
            #         self.x = newx
            #         self.y = newy
            # player.move(dx, dy, game_map)

            destination_x = player.x + dx
            destination_y = player.y + dy

            if game_map.walkable[destination_y, destination_x]:
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    print('You kick the ' + target.name + ' in the shins, much to its annoyance!')
                else:
                    player.move(dx, dy)

                    fov_recompute = True


if __name__ == '__main__':
    main()
