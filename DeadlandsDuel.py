import tcod
import tcod.event


import pydealer

from collections import Counter
from random import sample


from character import Character
from components.woundable import Woundable
from death_functions import kill_monster
from diceroller import skill_roll, ranged_weapon_damage_roll, unexploding_roll
from entity import Entity, get_blocking_entities_at_location
from input_handler import handle_events
from game_messages import MessageLog, Message
from map_objects.mapgine import generate_map
from renderengine import render_all, RenderOrder


def main():
    screen_width = 80
    screen_height = 50
    cardtable_width = 18
    cardtable_height = screen_height
    cardtable_x = screen_width - cardtable_width

    panel_height = 10
    panel_y = screen_height - panel_height
    panel_width = screen_width - cardtable_width

    map_width = screen_width - cardtable_width
    map_height = screen_height - panel_height

    message_x = 2
    message_width = panel_width - 2
    message_height = panel_height - 1

    message_log = MessageLog(message_x, message_width, message_height)

    panel = tcod.console.Console(panel_width, panel_height)
    mapcon = tcod.console.Console(map_width, map_height)
    cardtable = tcod.console.Console(cardtable_width, cardtable_height)

    # number of dice, sideness of dice. values used taken from gunslinger pregen, pg88
    player_charactersheet = Character()
    print(player_charactersheet)


    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', tcod.white, 'Player', True, RenderOrder.ACTOR, Woundable(6))
    entities = [player]

    game_map = tcod.map.Map(map_width, map_height)
    generate_map(game_map, player, entities)

    fov_recompute = True


    fate_pot = Counter({'white': 50, 'red': 25, 'blue':10})
    player_fate = Counter()
    player_fate.update(sample(list(fate_pot.elements()), 3))
    fate_pot.subtract(player_fate)



    # FIXME: Currently, this does not include Jokers, which are required
    #        for decks used in Deadlands. The class can be instantiated to
    #        use jokers, but its use of jokers does not differentiate between
    #        red and black jokers (as required in Deadlands) so the issue of
    #        jokers is left to another day.
    marshal_deck = pydealer.Deck()
    posse_deck = pydealer.Deck()

    marshal_deck.shuffle()
    posse_deck.shuffle()

    player_hand = pydealer.Stack() # pydealer.Stack()
    marshal_hand = pydealer.Stack()

    player_hand.sort()

    posse_discard = pydealer.Stack()
    marshal_discard = pydealer.Stack()

    tcod.console_set_custom_font('cp437_10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_CP437)
    root_console = tcod.console_init_root(screen_width, screen_height, 'Deadlands Duel', False, tcod.RENDERER_SDL2, vsync=True)

    player_round_movement_budget = player_charactersheet.get_movement_budget()
    move_this_action = 0

    active_card = posse_deck.deal(1) # pydealer.Stack()

    colt_army = {'shots': 6,
                 'max_shots': 6,
                 'range': 10,
                 'damage': {'number_of_dice': 3, 'sideness_of_dice': 6}}

    while True:

        if fov_recompute:
            game_map.compute_fov(player.x, player.y, algorithm=tcod.FOV_PERMISSIVE(5))

        render_all(root_console, entities, mapcon, game_map, cardtable, cardtable_x, player_hand, active_card, player_fate, panel, panel_y, message_log)

        tcod.console_flush()

        action = handle_events()

        move = action.get('move')

        activate_card = action.get('activate_card')

        shoot = action.get('shoot')

        pass_turn = action.get('pass_turn')

        reload = action.get('reload')

        if pass_turn: # pass action would be more accurate, for how i have modified this since creating it
            if active_card.size == 0:
                posse_discard.add(player_hand.deal(player_hand.size))

                player_round_movement_budget = player_charactersheet.get_movement_budget()
                roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

            elif active_card.size > 0:
                posse_discard.add(active_card.deal(active_card.size))
                if player_hand.size == 0:
                    posse_discard.add(player_hand.deal(player_hand.size))

                    player_round_movement_budget = player_charactersheet.get_movement_budget()
                    roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

        if activate_card and (active_card.size == 0):

            #nominate new active card. (test-only terminiology)
            if activate_card == -1:
                move_this_action = 0
                if player_hand.size > 0:
                    active_card.add(player_hand.deal(1, 'top'))
                    # player_hand.sort()

        if reload and colt_army['shots'] == colt_army['max_shots']:
            message_log.add_message(Message("Your revolver is fully loaded.", tcod.blue))
        elif reload:
            colt_army['shots'] += 1
            message_log.add_message(Message("You load a bullet into your revolver.", tcod.green))
            posse_discard.add(active_card.deal(active_card.size))
            if player_hand.size == 0:
                player_round_movement_budget = player_charactersheet.get_movement_budget()
                roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)            

        if shoot and (active_card.size > 0) and (colt_army['shots'] == 0):
            message_log.add_message(Message("You need to reload!", tcod.red))
        elif shoot and (active_card.size > 0) and (colt_army['shots'] > 0):
            # Shoot is currently the only "real" action that uses up the active card.
            modifier = 0
            if move_this_action > ((player_charactersheet.pace * 3) // 5):
                message_log.add_message(Message("You attempt to draw a bead while running...", tcod.orange))
                modifier = -4
            elif move_this_action > 0:
                message_log.add_message(Message("You fire while walking...", tcod.yellow))
                modifier = -2

            nearest_target = None
            nearest_distance = 999
            for entity in entities:
                if game_map.fov[entity.y, entity.x]:
                    if entity.woundable:
                        if not entity.name is 'Player':
                            new_distance = entity.distance_to(player)
                            if new_distance < nearest_distance:
                                nearest_distance = new_distance
                                nearest_target = entity
            tn = 5

            range_increments = (nearest_distance / 3) // colt_army['range']
            tn += range_increments

            shootin_roll = skill_roll(player_charactersheet.shootin_pistol['trait'], player_charactersheet.shootin_pistol['aptitude'], tn, modifier)

            bust = shootin_roll.get('bust')
            failure = shootin_roll.get('failure')
            success = shootin_roll.get('success')
            message_log.add_message(Message("BANG!!", tcod.brass))

            colt_army['shots'] -= 1
            if colt_army['shots'] == 0:
                message_log.add_message(Message("That was your last loaded bullet!", tcod.red))

            if bust:
                message_log.add_message(Message("You went bust, and narrowly avoided shooting your own foot!", tcod.red))
            else:
                if not nearest_target:
                    if failure:
                        message_log.add_message(Message("You shoot the broad side of a barn!"))
                    elif success:
                        if success == 1:
                            message_log.add_message(Message("You shoot some bottles for target practice!", tcod.green))
                        else:
                            message_log.add_message(Message("You put a bullet hole in the forehead of a Wanted poster!", tcod.blue))
                else:
                    if failure:
                        message_log.add_message(Message("The bullet whizzes past your target!"))
                    elif success:
                        vital_hit = False
                        hitlocation = unexploding_roll(20)
                        if (hitlocation == 20) or (hitlocation == 10):
                            vital_hit = True
                        if success == 1:
                            message_log.add_message(Message("You manage to hit your target!", tcod.green))
                        else:
                            if ((20 - hitlocation) <= success) or (0 < (10 - hitlocation) <= success) or (0 < (hitlocation - 10) <= success):
                                vital_hit = True
                            message_log.add_message(Message("You accurately shoot your target!", tcod.blue))

                        dmg = ranged_weapon_damage_roll(colt_army['damage']['sideness_of_dice'], colt_army['damage']['number_of_dice'], vital_bonus = vital_hit)

                        nearest_target.woundable.take_simple_damage(dmg)
                        if nearest_target.woundable.get_most_severe_wound()[1] >= 5:
                            message_log.add_message(kill_monster(nearest_target))

            posse_discard.add(active_card.deal(1))

            if player_hand.size == 0:
                player_round_movement_budget = player_charactersheet.get_movement_budget()
                roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

        # FIXME: As currently written, this lets you move both before and after an action card.
        # First, the game lets you move a partial movement,
        #     then, you can use your single card to initate a "new" action and reset the
        #     tracking of movements per action,
        #       which lets you evade potential running penalties in some situations (penalty not implemented yet)
        if (move and (player_round_movement_budget > 0) and (active_card.size > 0)):
            dx, dy = move
            # newx = self.x + dx
            # newy = self.y + dy
            # if not ((newx < 0) or (newy < 0) or (newx >= game_map.width) or (newy >= game_map.height)):
            #     if game_map.walkable[newy, newx]:
            #         self.x = newx
            #         self.y = newy
            # player.move(dx, dy, game_map)

            destination_x = player.x + dx
            destination_y = player.y + dy
            if (0 <= destination_x < game_map.width) and (0 <= destination_y < game_map.height):
                if game_map.walkable[destination_y, destination_x]:
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        message_log.add_message(Message('You kick the ' + target.name + ' in the shins, much to its annoyance!'))
                    else:
                        player.move(dx, dy)
                        player_round_movement_budget -= 1
                        # We track our movement taking place in this action card.
                        # We can move up to twice our pace the whole round spread across all our actions.
                        # We incur a running penalty on an action where we have also moved more than our pace;
                        # ie, more than half our full movement budget
                        # (which is calculated to a maximum with running in mind)
                        move_this_action += 1
                        #                       pace in yards.         yds->ft   ft->squares
                        if move_this_action > ((player_charactersheet.pace * 3) // 5):
                            message_log.add_message(Message("Running!!!", tcod.orange))
                        else:
                            message_log.add_message(Message("Walking...", tcod.yellow))
                        fov_recompute = True


def roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log):
    quickness_roll = skill_roll(player_charactersheet.quickness.traitDie, player_charactersheet.quickness.levelDice)
    message_log.add_message(Message('Beginning of new round. Rolling quickness...'))



    bust = quickness_roll.get('bust')
    failure = quickness_roll.get('failure')
    success = quickness_roll.get('success')

    if not bust:
        handsize = 1
        if success:
            message_log.add_message(Message("You succeeded in quickly getting multiple action cards this round!", tcod.green))
            handsize += success
            if handsize > 5:
                handsize = 5
        else:
            message_log.add_message(Message("You failed to get more than the default single action card this round."))
        newhand = pydealer.Stack()

        for i in range(handsize):
            if posse_deck.size == 0:
                message_log.add_message(Message("Reshuffling!", tcod.gray))
                posse_deck.add(posse_discard.deal(posse_discard.size))
                posse_deck.shuffle()
            newcard = posse_deck.deal(1)
            newhand.add(newcard)

        player_hand.add(newhand)
        player_hand.sort()
    else:
        message_log.add_message(Message("You went bust, no new cards this round!", tcod.red))


if __name__ == '__main__':
    main()
