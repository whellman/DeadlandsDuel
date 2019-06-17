import tcod

def main():
    screen_width = 80
    screen_height = 50
    cardtable_width = 18
    cardtable_height = screen_height
    cardtable_x = screen_width - cardtable_width
    map_width = screen_width - cardtable_width
    map_height = screen_height

    mapcon = tcod.console_new(map_width, map_height)
    cardtable = tcod.console_new(cardtable_width, cardtable_height)


    tcod.console_set_custom_font('cp437_10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_ASCII_INROW)
    root_console = tcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False)

    while not tcod.console_is_window_closed():

        # for y in range(cardtable_height):
        #     for x in range(cardtable_width):
        #         tcod.console_set_char_background(cardtable, x, y, tcod.Color(50, 100, 0))
        cardtable.draw_rect(0, 0, cardtable_width, cardtable_height, ch=0, bg=(70, 140, 0))
        cardtable.draw_rect(1, 1, cardtable_width-2, cardtable_height-2, ch=0, bg=(30, 60, 0))
        cardtable.draw_rect(2, 2, cardtable_width-3, cardtable_height-3, ch=0, bg=(50, 100, 0))

        # tcod.console_blit(cardtable, 0, 0, cardtable_width, cardtable_height, 0, cardtable_x, 0)
        cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable_width, cardtable_height)

        tcod.console_flush()



        key = tcod.console_check_for_keypress()

        if key.vk == tcod.KEY_ESCAPE:
            return True


if __name__ == '__main__':
    main()
