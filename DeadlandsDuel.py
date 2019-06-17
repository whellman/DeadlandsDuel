import tcod
import tcod.event

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

    player_x = int(map_width / 2)
    player_y = int(map_height / 2)

    number_of_rooms = 8

    mapcon = tcod.console.Console(map_width, map_height)
    cardtable = tcod.console.Console(cardtable_width, cardtable_height)

    game_map = tcod.map.Map(map_width, map_height)
    generate_map(game_map, number_of_rooms)
    game_map.compute_fov(0, 0)

    tcod.console_set_custom_font('cp437_10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False, tcod.RENDERER_SDL2, vsync=True)

    while True:

        game_map.compute_fov(player_x, player_y, radius=8)

        render_all(root_console, mapcon, game_map, cardtable, cardtable_x)

        root_console.print(player_x, player_y, '@', fg=[255, 255, 255])

        tcod.console_flush()

        action = handle_events()

        move = action.get('move')

        if move:
            dx, dy = move
            newx = player_x + dx
            newy = player_y + dy
            if not ((newx < 0) or (newy < 0) or (newx >= map_width) or (newy >= map_height)):
                player_x = newx
                player_y = newy

if __name__ == '__main__':
    main()
