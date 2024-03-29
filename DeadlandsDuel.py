import tcod
import tcod.event

import pydealer

from collections import Counter
from random import sample

from character import Character
from components.fighter import Fighter
from death_functions import kill_monster
from diceroller import skill_roll, ranged_weapon_damage_roll, unexploding_roll
from entity import Entity, get_blocking_entities_at_location
from input_handler import handle_events
from game_messages import MessageLog, Message
from game_states import GameStates
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


    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', tcod.white, 'Player', True, RenderOrder.ACTOR, Fighter(6))
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

    # Also probably the suit hierarchy is not the same as Deadlands; that should be easy
    # to fix when I get to it.
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

    active_card = pydealer.Stack() # posse_deck.deal(1)

    colt_army = {'shots': 6,
                 'max_shots': 6,
                 'range': 10,
                 'damage': {'number_of_dice': 3, 'sideness_of_dice': 6}}

    game_state = GameStates.PLAYERS_TURN

    # FIXME: There's probably an elegant solution to be found in generalizing this
    # list to include the player, and sorting it by action cards, or something.
    enemy_combatants = []

    while True:

        if fov_recompute:
            game_map.compute_fov(player.x, player.y, algorithm=tcod.FOV_PERMISSIVE(5))

            if game_state ==GameStates.PLAYERS_TURN:
                for entity in entities:
                    if entity.name == 'Bandit' and game_map.fov[entity.y, entity.x]:
                        game_state = GameStates.BEGIN_DETAILED_COMBAT_ROUND
                        break

            if game_state ==GameStates.ROUNDS_PLAYERS_ACTION:
                enemies_in_view = False
                for entity in entities:
                    if entity.name == 'Bandit' and game_map.fov[entity.y, entity.x]:
                        enemies_in_view = True
                if enemies_in_view == False:
                    message_log.add_message(Message("All visible bandits dead, leaving combat rounds..."))
                    posse_discard.add(active_card.deal(active_card.size))
                    posse_discard.add(player_hand.deal(player_hand.size))
                    game_state =GameStates.PLAYERS_TURN
                    enemy_combatants = []

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if (entity.name == 'Bandit') and (not game_map.fov[entity.y, entity.x]):
                    if entity.fighter.shots < 6:
                        # When the player ducks behind a wall to reload their revolver,
                        # the bandits also take advantage of the opportunity!
                        entity.fighter.shots += 1
            game_state = GameStates.PLAYERS_TURN


        if game_state == GameStates.BEGIN_DETAILED_COMBAT_ROUND:
            # Let the player know what's going on
            message_log.add_message(Message("Beginning of combat round!"))

            # Deal the player a hand from the posse deck and calc their movement
            player_round_movement_budget = player_charactersheet.get_movement_budget()
            roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

            # We *should* deal the enemies an action hand, and calc their movement.
            # FIXME: Currently, we use the ultra-simple shortcut for enemies
            # from the Marshal Tricks section of the rules, dealing them a single card.
            # This combat really isn't on a scale where that is justified, at least not until
            # more enemies are clued in to the combat via sound or a vague awareness metric.
            # Also, enemy movement is not yet implemented, so we don't calc their move rate.
            for entity in entities:
                if entity.name == 'Bandit' and game_map.fov[entity.y, entity.x]:
                    entity.fighter.action_hand = marshal_deck.deal(1)
                    enemy_combatants.append(entity)

            game_state = GameStates.MEDIATE_COMBAT_ROUNDS

        if game_state == GameStates.MEDIATE_COMBAT_ROUNDS:
            # FIXME: Should we keep track of a list of combat activated enemies?
            # As a quick hack, right now it's just FOV.
            # (calculated in BEGIN_DETAILED_COMBAT_ROUNDS conditional above)
            remaining_enemy_cards = False
            for combatant in enemy_combatants:
                if combatant.fighter.action_hand.size > 0:
                    # print(combatant.fighter.action_hand.size)
                    remaining_enemy_cards = True

            if remaining_enemy_cards or (player_hand.size > 0): # and (active_card.size > 0)):

                highest_player = None
                if player_hand.size > 0:
                    highest_player = player_hand[player_hand.size - 1]
                # print("highest player card " + str(highest_player))

                highest_combatant = None
                highest_comb_card = None
                if remaining_enemy_cards:
                    for combatant in enemy_combatants:
                        print("combatant card: " + str(combatant.fighter.action_hand[combatant.fighter.action_hand.size - 1]))
                        if highest_comb_card == None:
                            highest_combatant = combatant
                            highest_comb_card =  combatant.fighter.action_hand[combatant.fighter.action_hand.size - 1]
                        elif combatant.fighter.action_hand[combatant.fighter.action_hand.size - 1] > highest_comb_card:
                            highest_combatant = combatant
                            highest_comb_card =  combatant.fighter.action_hand[combatant.fighter.action_hand.size - 1]

                # print("highest combatant card " + str(highest_comb_card))

                if remaining_enemy_cards and ((highest_combatant) and ((highest_player == None)) or (highest_comb_card > highest_player)):
                    # Enemy turn, in combat rounds. Placeholder.
                    message_log.add_message(Message("The " + highest_combatant.name + " acts on a " + str(highest_comb_card) + "!", tcod.orange))
                    if highest_combatant.fighter.shots > 0:
                        tn = 5
                        modifier = 0 - highest_combatant.fighter.get_most_severe_wound()[1]
                        range_increments = (highest_combatant.distance_to(player) / 3) // colt_army['range']
                        tn += range_increments

                        shootin_roll = skill_roll(2, 8, tn, modifier)
                        success = shootin_roll.get('success')
                        if success:
                            vital_hit = False
                            body_part = None
                            hitlocation = unexploding_roll(20)
                            if (hitlocation == 20):
                                vital_hit = True
                                body_part = 'head'
                            elif 15 <= hitlocation <= 19:
                                body_part = 'guts' #upper
                            elif 11 <= hitlocation <= 14:
                                body_part = '_arm'
                                if unexploding_roll(2) == 1:
                                    body_part = 'left' + body_part
                                else:
                                    body_part = 'right' + body_part
                            elif hitlocation == 10:
                                vital_hit = True
                                body_part = 'guts' #gizzards
                            elif 5 <= hitlocation <= 9:
                                body_part = 'guts' #lower
                            else:
                                body_part = '_leg'
                                if unexploding_roll(2) == 1:
                                    body_part = 'left' + body_part
                                else:
                                    body_part = 'right' + body_part


                            message_log.add_message(Message("The bandit takes aim and shoots, hitting you in the " + body_part + "!", tcod.red))
                            dmg = ranged_weapon_damage_roll(colt_army['damage']['sideness_of_dice'], colt_army['damage']['number_of_dice'], vital_bonus = vital_hit)
                            message_log.add_message(player.fighter.take_positional_damage(dmg, body_part, fate_pot, player_fate))
                            if (player.fighter.body_wounds['guts'] >= 5) or (player.fighter.body_wounds['head'] >= 5):
                                message_log.add_message(kill_monster(player))
                                game_state = GameStates.PLAYER_DEAD
                        else:
                            message_log.add_message(Message("The bandit takes aim and shoots! The bullet whizzes past you!", tcod.orange))
                        highest_combatant.fighter.shots -= 1
                    else:
                        message_log.add_message(Message("The bandit loads his revolver..."))
                        highest_combatant.fighter.shots += 1
                    marshal_discard.add(highest_combatant.fighter.action_hand.deal(1))
                    enemy_combatants.remove(highest_combatant)
                else:
                    # FIXME: This erroneously includes tied situations, which the rules say
                    # should result in simultaneous actions.

                    # Player's turn, in combat rounds.
                    game_state = GameStates.ROUNDS_PLAYERS_ACTION
            else:
                game_state = GameStates.BEGIN_DETAILED_COMBAT_ROUND

        if game_state == GameStates.ROUNDS_ENEMY_ACTION:
            print("Shouldn't be possible???")


        render_all(root_console, entities, mapcon, game_map, cardtable, cardtable_x, player_hand, active_card, player_fate, panel, panel_y, message_log, player.fighter.body_wounds)

        tcod.console_flush()

        action = handle_events()

        move = action.get('move')

        activate_card = action.get('activate_card')

        shoot = action.get('shoot')

        pass_turn = action.get('pass_turn')

        reload = action.get('reload')

        if move and (game_state == GameStates.PLAYERS_TURN):
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy
            if (0 <= destination_x < game_map.width) and (0 <= destination_y < game_map.height):
                if game_map.walkable[destination_y, destination_x]:
                    target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                    if target:
                        message_log.add_message(Message('You kick the ' + target.name + ' in the shins, much to its annoyance!'))
                    else:
                        player.move(dx, dy)
                        fov_recompute = True
                    game_state = GameStates.ENEMY_TURN


        if pass_turn and (game_state == GameStates.ROUNDS_PLAYERS_ACTION): # pass action would be more accurate, for how i have modified this since creating it
            # if active_card.size == 0:
            #     posse_discard.add(player_hand.deal(player_hand.size))
            #
            #     player_round_movement_budget = player_charactersheet.get_movement_budget()
            #     roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)
            #elif
            if active_card.size > 0:
                posse_discard.add(active_card.deal(active_card.size))
                game_state = GameStates.MEDIATE_COMBAT_ROUNDS
                # The following should be covered by the MEDIATE_COMBAT_ROUNDS

                # if player_hand.size == 0:
                #     posse_discard.add(player_hand.deal(player_hand.size))
                #
                #     player_round_movement_budget = player_charactersheet.get_movement_budget()
                #     roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

        if activate_card and (active_card.size == 0) and (game_state == GameStates.ROUNDS_PLAYERS_ACTION):

            #nominate new active card. (test-only terminiology)
            if activate_card == -1:
                move_this_action = 0
                if player_hand.size > 0:
                    active_card.add(player_hand.deal(1, 'top'))
                    # player_hand.sort()

        if reload and ((game_state == GameStates.ROUNDS_PLAYERS_ACTION) or (game_state ==GameStates.PLAYERS_TURN)):
            if colt_army['shots'] == colt_army['max_shots']:
                message_log.add_message(Message("Your revolver is fully loaded.", tcod.blue))
            elif (game_state ==GameStates.PLAYERS_TURN) or ((game_state == GameStates.ROUNDS_PLAYERS_ACTION) and (active_card.size > 0)):
                colt_army['shots'] += 1
                message_log.add_message(Message("You load a bullet into your revolver.", tcod.green))
                if (game_state ==GameStates.ROUNDS_PLAYERS_ACTION):
                    posse_discard.add(active_card.deal(active_card.size))
                    game_state = GameStates.MEDIATE_COMBAT_ROUNDS
                    # if player_hand.size == 0:
                    #     player_round_movement_budget = player_charactersheet.get_movement_budget()
                    #     roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

        if shoot and (game_state == GameStates.ROUNDS_PLAYERS_ACTION):
            if (active_card.size > 0) and (colt_army['shots'] == 0):
                message_log.add_message(Message("You need to reload!", tcod.red))
            elif (active_card.size > 0) and (colt_army['shots'] > 0):
                # Shoot is currently the only "real" action that uses up the active card.
                modifier = 0
                if move_this_action > ((player_charactersheet.pace * 3) // 5):
                    message_log.add_message(Message("You attempt to draw a bead while running...", tcod.orange))
                    modifier = -4
                elif move_this_action > 0:
                    message_log.add_message(Message("You fire while walking...", tcod.yellow))
                    modifier = -2

                wound_modifier = 0 - player.fighter.get_most_severe_wound()[1]
                modifier += wound_modifier

                nearest_target = None
                nearest_distance = 999
                for entity in entities:
                    if game_map.fov[entity.y, entity.x]:
                        if entity.fighter:
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

                            message_log.add_message(nearest_target.fighter.take_simple_damage(dmg))
                            if nearest_target.fighter.get_most_severe_wound()[1] >= 5:
                                message_log.add_message(kill_monster(nearest_target))
                                marshal_discard.add(nearest_target.fighter.action_hand.deal(nearest_target.fighter.action_hand.size))

                posse_discard.add(active_card.deal(1))

                game_state = GameStates.MEDIATE_COMBAT_ROUNDS
                # if player_hand.size == 0:
                #     player_round_movement_budget = player_charactersheet.get_movement_budget()
                #     roll_new_round(player_hand, player_charactersheet, posse_deck, posse_discard, message_log)

        # FIXME: As currently written, this lets you move both before and after an action card.
        # First, the game lets you move a partial movement,
        #     then, you can use your single card to initate a "new" action and reset the
        #     tracking of movements per action,
        #       which lets you evade potential running penalties in some situations (penalty not implemented yet)
        if (move and (player_round_movement_budget > 0) and (active_card.size > 0) and (game_state ==GameStates.ROUNDS_PLAYERS_ACTION)):
            dx, dy = move
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
