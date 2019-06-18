import tcod
import tcod.event


def handle_events():
    for event in tcod.event.wait():
        if (event.type == "QUIT"):
            raise SystemExit()
        elif (event.type == "KEYDOWN"):
            if (event.sym == tcod.event.K_ESCAPE):
                raise SystemExit()
            elif event.sym == tcod.event.K_LEFT:
                return {'move': (-1, 0)}
            elif event.sym == tcod.event.K_RIGHT:
                return {'move': (1, 0)}
            elif event.sym == tcod.event.K_UP:
                return {'move': (0, -1)}
            elif event.sym == tcod.event.K_DOWN:
                return {'move': (0, 1)}

            elif event.sym == tcod.event.K_c:
                return {'testhand': 1}
            elif event.sym == tcod.event.K_v:
                return {'testhand': -1}
    return {}
