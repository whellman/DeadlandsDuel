import tcod

from rgb import rgb

def render_map(mapcon, game_map):
    for y in range(mapcon.height):
        for x in range(mapcon.width):
            if game_map.fov[y,x]:
                if game_map.walkable[y,x]:
                    mapcon.print(x, y, ' ', bg=rgb(200, 170, 90))
                else:
                    mapcon.print(x, y, ' ', bg=rgb(80, 60, 20))
            else:
                if game_map.walkable[y,x]:
                    mapcon.print(x, y, ' ', bg=rgb(0, 0, 90))
                else:
                    mapcon.print(x, y, ' ', bg=rgb(0, 0, 20))

def render_cardtable(cardtable):
    cardtable.draw_rect(0, 0, cardtable.width, cardtable.height, ch=0, bg=rgb(70, 140, 0))
    cardtable.draw_rect(1, 1, cardtable.width-2, cardtable.height-2, ch=0, bg=rgb(30, 60, 0))
    cardtable.draw_rect(2, 2, cardtable.width-3, cardtable.height-3, ch=0, bg=rgb(50, 100, 0))

def render_all(root_console, entities, mapcon, game_map, cardtable, cardtable_x):
    render_cardtable(cardtable)
    cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable.width, cardtable.height)
    render_map(mapcon, game_map)
    for entity in entities:
        if game_map.fov[entity.y, entity.x]:
            draw_entity(entity, mapcon)
    mapcon.blit(root_console, 0, 0, 0, 0, mapcon.width, mapcon.height)

def draw_entity(entity, con):
    con.print(entity.x, entity.y, entity.char, fg=entity.color)
