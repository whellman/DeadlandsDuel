import tcod
import tcod.event


def handle_events():
    for event in tcod.event.wait():
        if (event.type == "QUIT"):
            raise SystemExit()
        elif (event.type == "KEYDOWN"):
            if (event.sym == tcod.event.K_ESCAPE):
                raise SystemExit()
            elif event.sym == tcod.event.K_LEFT or event.sym == tcod.event.K_h:
                return {'move': (-1, 0)}
            elif event.sym == tcod.event.K_RIGHT or event.sym == tcod.event.K_l:
                return {'move': (1, 0)}
            elif event.sym == tcod.event.K_UP or event.sym == tcod.event.K_k:
                return {'move': (0, -1)}
            elif event.sym == tcod.event.K_DOWN or event.sym == tcod.event.K_j:
                return {'move': (0, 1)}
            elif event.sym == tcod.event.K_y:
                return {'move': (-1, -1)}
            elif event.sym == tcod.event.K_u:
                return {'move': (1, -1)}
            elif event.sym == tcod.event.K_b:
                return {'move': (-1, 1)}
            elif event.sym == tcod.event.K_n:
                return {'move': (1, 1)}

            elif event.sym == tcod.event.K_RETURN:
                return {'activate_card': -1}
            elif event.sym == tcod.event.K_f:
                return {'shoot': 1}
    return {}
