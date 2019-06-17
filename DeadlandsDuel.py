import tcod as libtcod

def main():
    screen_width = 80
    screen_height = 50
    cardtable_width = 18
    cardtable_height = screen_height
    cardtable_x = screen_width - cardtable_width
    map_width = screen_width - cardtable_width
    map_height = screen_height

    mapcon = libtcod.console_new(map_width, map_height)
    cardtable = libtcod.console_new(cardtable_width, cardtable_height)


    libtcod.console_set_custom_font('cp437_10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    root_console = libtcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False)

    while not libtcod.console_is_window_closed():

        # for y in range(cardtable_height):
        #     for x in range(cardtable_width):
        #         libtcod.console_set_char_background(cardtable, x, y, libtcod.Color(50, 100, 0))
        cardtable.draw_rect(0, 0, cardtable_width, cardtable_height, ch=0, bg=(70, 140, 0))
        cardtable.draw_rect(1, 1, cardtable_width-2, cardtable_height-2, ch=0, bg=(30, 60, 0))
        cardtable.draw_rect(2, 2, cardtable_width-3, cardtable_height-3, ch=0, bg=(50, 100, 0))

        # libtcod.console_blit(cardtable, 0, 0, cardtable_width, cardtable_height, 0, cardtable_x, 0)
        cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable_width, cardtable_height)

        libtcod.console_flush()



        key = libtcod.console_check_for_keypress()

        if key.vk == libtcod.KEY_ESCAPE:
            return True


if __name__ == '__main__':
    main()
