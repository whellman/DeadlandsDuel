import tcod
import tcod.event as event

from renderengine import render_all
from mapgine import generate_map

def main():
    screen_width = 80
    screen_height = 50
    cardtable_width = 18
    cardtable_height = screen_height
    cardtable_x = screen_width - cardtable_width
    map_width = screen_width - cardtable_width
    map_height = screen_height

    # FIXME: JUst started this. number_of_rooms = 8

    mapcon = tcod.console.Console(map_width, map_height)
    cardtable = tcod.console.Console(cardtable_width, cardtable_height)

    game_map = tcod.map.Map(map_width, map_height)
    generate_map(game_map, map_width, map_height)
    game_map.compute_fov(0, 0)


    tcod.console_set_custom_font('cp437_10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False, tcod.RENDERER_SDL2, vsync=True)

    while True:

        for y in range(mapcon.height):
            for x in range(mapcon.width):
                if game_map.walkable[y,x]:
                    mapcon.print(x, y, ' ', bg=[200, 170, 90])
                else:
                    mapcon.print(x, y, ' ', bg=[80, 60, 20])



        mapcon.blit(root_console, 0, 0, 0, 0, mapcon.width, mapcon.height)


        render_all(root_console, cardtable, cardtable_x)
        tcod.console_flush()


        for event in tcod.event.wait():
            if (event.type == "QUIT"):
                raise SystemExit()
            elif (event.type == "KEYDOWN"):
                if (event.sym == 27):
                    raise SystemExit()
                # elif (event.sym == 'h')
                # print(event.scancode)
                # print(event.sym)
if __name__ == '__main__':
    main()
