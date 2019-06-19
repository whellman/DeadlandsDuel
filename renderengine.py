import tcod
import pydealer

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

def render_chip(cardtable, color, x, y):
    if color == 'white':
        fgcolor = rgb(255, 255, 255)
    elif color == 'red':
        fgcolor = rgb(255, 0, 60)
    else:
        fgcolor = rgb(0, 0, 200)

    cardtable.print(x, y, '▀▀', fg=fgcolor)

def render_card(cardtable, card, x, y, bgcolor):
    # We'll start off with very simple cards, 3 wide by 5 tall.
    if card.suit == "Spades":
        fgcolor = rgb(0, 0, 0)
        suitchar = '♠'
    elif card.suit == "Clubs":
        fgcolor = rgb(0, 0, 0)
        suitchar = '♣'
    elif card.suit == "Hearts":
        fgcolor = rgb(255, 0, 60)
        suitchar = '♥'
    else:
        fgcolor = rgb(255, 0, 60)
        suitchar = '♦'

    cardtable.draw_rect(x, y, 3, 5, ch=20, bg=bgcolor)

    cardtable.print(x + 1, y + 2, suitchar, fg=fgcolor)

    if card.value == '10':
        cardtable.print(x, y, card.value, fg=fgcolor)
        cardtable.print(x + 1, y + 4, card.value, fg=fgcolor)
    else:
        cardtable.print(x, y, card.value[0], fg=fgcolor)
        cardtable.print(x + 2, y + 4, card.value[0], fg=fgcolor)


def render_cardtable(cardtable, player_hand, active_card, player_fate):
    cardtable.draw_rect(0, 0, cardtable.width, cardtable.height, ch=20, bg=rgb(70, 140, 0))
    cardtable.draw_rect(1, 1, cardtable.width-2, cardtable.height-2, ch=20, bg=rgb(30, 60, 0))
    cardtable.draw_rect(2, 2, cardtable.width-3, cardtable.height-3, ch=20, bg=rgb(50, 100, 0))

    stepamount = 30
    startingshade = 255 - (stepamount * (player_hand.size - 1))

    for i in range(player_hand.size):
        render_card(cardtable, player_hand[i], (3 + (2 * i)), 10, [(startingshade + (stepamount * i)), (startingshade + (stepamount * i)), (startingshade + (stepamount * i))])

    if active_card.size > 0:
        render_card(cardtable, active_card[0], 3, 3, [255, 255, 200])

    chip_x = 3
    chip_y = cardtable.height - 2
    for color in iter(player_fate):
        for i in range(player_fate[color]):
            render_chip(cardtable, color, chip_x, (chip_y - i))
        chip_x += 3


def render_all(root_console, entities, mapcon, game_map, cardtable, cardtable_x, player_hand, active_card, player_fate):
    render_cardtable(cardtable, player_hand, active_card, player_fate)
    cardtable.blit(root_console, cardtable_x, 0, 0, 0, cardtable.width, cardtable.height)
    render_map(mapcon, game_map)
    for entity in entities:
        if game_map.fov[entity.y, entity.x]:
            draw_entity(entity, mapcon)
    mapcon.blit(root_console, 0, 0, 0, 0, mapcon.width, mapcon.height)

def draw_entity(entity, con):
    con.print(entity.x, entity.y, entity.char, fg=entity.color)
