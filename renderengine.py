import tcod

def render_cardtable(cardtable):
    cardtable.draw_rect(0, 0, cardtable.width, cardtable.height, ch=0, bg=(70, 140, 0))
    cardtable.draw_rect(1, 1, cardtable.width-2, cardtable.height-2, ch=0, bg=(30, 60, 0))
    cardtable.draw_rect(2, 2, cardtable.width-3, cardtable.height-3, ch=0, bg=(50, 100, 0))

def render_all(root_console, cardtable, cardtable_x):
    render_cardtable(cardtable)
    cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable.width, cardtable.height)
