import tcod

def render_cardtable(cardtable, cardtable_width, cardtable_height):
    cardtable.draw_rect(0, 0, cardtable_width, cardtable_height, ch=0, bg=(70, 140, 0))
    cardtable.draw_rect(1, 1, cardtable_width-2, cardtable_height-2, ch=0, bg=(30, 60, 0))
    cardtable.draw_rect(2, 2, cardtable_width-3, cardtable_height-3, ch=0, bg=(50, 100, 0))

def render_all(root_console, cardtable, cardtable_x, cardtable_width, cardtable_height):
    render_cardtable(cardtable, cardtable_width, cardtable_height)
    cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable_width, cardtable_height)
