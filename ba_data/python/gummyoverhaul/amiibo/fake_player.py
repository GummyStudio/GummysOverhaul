import bascenev1 as bs
from bascenev1 import InputType
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.spazbot import SpazBot
import random
from bascenev1lib.actor.popuptext import PopupText
import math
import bauiv1 as bui
from bascenev1lib.actor import powerupbox, bomb, flag
import os, zlib, json, base64
from .helpers import _xor_cipher
from bascenev1lib.activity.multiteamvictory import (
            TeamSeriesVictoryScoreScreenActivity
        )
from bascenev1lib.activity.freeforallvictory import (
    FreeForAllVictoryScoreScreenActivity
)

# activities

# UNIQUE GAMES
from bascenev1lib.game.bowling import BowlingGame
from bascenev1lib.game.chosenone import ChosenOneGame
from bascenev1lib.game.crown import CrownGame
from bascenev1lib.game.ffactp import FreeForAllCTFByGUMMYBOIYT
from bascenev1lib.game.keepaway import KeepAwayGame
from bascenev1lib.game.kingofthehill import KingOfTheHillGame
from bascenev1lib.game.meteorshower import MeteorShowerGame
from bascenev1lib.game.CoopGame import OnslaughtFFAGame, RunaroundFFAGame

# Basiacally death match.
from bascenev1lib.game.deathmatch import DeathMatchGame
from bascenev1lib.game.ClassicDuel import DuelClassicGame
from bascenev1lib.game.eggies import DeathMatchGame as EggiesGame
from bascenev1lib.game.elimination import EliminationGame
from bascenev1lib.game.SuperSmash import SuperSmash, SuperSmashDM
from bascenev1lib.game.thedisasters import DisasterGame
from bascenev1lib.game.war import EliminationGame as WarGame


# from gummyoverhaul.amiibo.fake_player import FigureSessionPlayer as f; f()

class FigureSessionPlayer:
    def __init__(self, data: dict = {}):
        if not data:
            raise ValueError("No data provided for FigureSessionPlayer")
        self.active = True
        
        # Use the session first specifically
        with bs.get_foreground_host_session().context:
        

           
            self.data = data
            # Let the lobby / game know that we are an figure so they can show our level
            self.amiibo = True

            self._input_bindings = {}
            self.sessionteam: bs.SessionTeam | None
            self.activity: bs.Activity | None = None
            self.activityplayer: bs.Player = None
            self.tick_timer: bs.Timer = None

            # Figure data.
            self.character = self.data['character']
            self.color = self.data['color']
            self.highlight = self.data['color']
            self.nickname = self.data['nickname']
            self.cosmetic = self.data['cosmetic']
            self.abilities = self.data['abilities']
            self.level = self.data['level']
            self.xp = self.data['xp']
            self.learn = self.data['learn'] # Change behvaior
            self.behaviors = self.data['behaviors']
            self.targeting = self.data['targeting']
            self.extra_data = self.data['extra_data']  # save combos
            self.extra_data2 = self.data['extra_data_2'] #whatever
            self.serial_number = self.data["id"]
            
            self._cached_target = None
            self._target_refresh = 0.0
            self.saved = False

            self.state = 'idle'
            self.state_timer = 0.0
            self.state_locked = False

            # Combat memory / anti-spam.
            self.last_attack_time = 0.0
            self.last_jump_time = 0.0
            self.combo_hits = 0
            self.failed_attacks = 0
            self.recently_hit = False
            self.last_edge_check = 0.0

            

            


            self.id = len(bs.getsession().sessionplayers)
            self.node=bs.Node(None)

            
            
            self.inputdevice = FigureInputDevice(data)

            # Okay ask ourselves if we should be in-game 
            # (automaticaly makes us join etc)
            result = bs.getsession()._request_player(self)
            

            # No? Okay bye
            if not result:
                self.active = False
                return None
            
            
            
            
            self.active = True
            # Okay well get the damn sessointeam thingy
            our_chooser: bs.Chooser = bs.getsession().lobby.choosers[-1]

            # We gotta be quick, someone could join
            self.sessionteam = our_chooser.sessionteam
            # Tell the chooser to be our uhhh h h Profile
            




            # So our level and stuff gets shown
            our_chooser.is_figure_player = True
            our_chooser.update_from_profile()


            # Ready up
            our_chooser._set_ready(True)
            # Instantly clean this up
            our_chooser = None
    
            

            # Play a sound that we joined
            bs.getsound('amiibo/entry').play(0.25)
            # And start acting! 
        
        bs.apptimer(0.1, self.check)

    def set_state(
        self,
        state: str,
        duration: float = 0.25,
        lock: bool = False
    ):
        self.state = state
        self.state_timer = bs.time() + duration
        self.state_locked = lock
    
    def save(self):
        if not self.active:
            return
        if not self.saved:
                        mods_dir = bs.app.env.python_directory_user
                        safe_name = "".join([c for c in self.data['nickname'] if c.isalnum()]).strip()
                        if not safe_name:
                            safe_name = "figure"
                            
                        file_name = f"{safe_name}.figureplayer"
                        target_path = os.path.join(mods_dir, file_name)

                        if not os.path.exists(target_path):
                            print(f'[Figure Player] Save for {self.nickname} was a  failure.\nReason: Target file does not exist anymore')
                            bui.getsound('error').play()
                            bs.screenmessage("Save failed. Check console.", color=(1, 0, 0))
                            
                        else:
                            try:
                                json_str = json.dumps(self.data, indent=4)
                                json_bytes = json_str.encode('utf-8')
                                
                                compressed_bytes = zlib.compress(json_bytes)
                                
                                ciphered_bytes = _xor_cipher(compressed_bytes)
                                
                                final_b64_string = base64.b64encode(ciphered_bytes).decode('ascii')

                                with open(target_path, 'w', encoding='utf-8') as f:
                                    f.write(final_b64_string)
                                    
                                bui.getsound('gunCocking').play()
                                bs.screenmessage(f"Saved {self.data['nickname']} in Mods folder.", color=(0.3, 1, 0.5))
                                return True
                            except Exception as e:
                                print(f"[Figure Player] Figure Encryption Save Error: {e}")
                                bui.getsound('error').play()
                                bs.screenmessage("Svae failed. Check console.", color=(1, 0, 0))
                                return False
                        self.saved = True

    
    def check(self):
        if not self.active:
            return
        
        # Does contesxt work
        context = self.get_context()
        if context is None:
            self.tick_timer = None
            bs.apptimer(0.1, self.check)
            return
            
        if self.activity:
            with context:
                if isinstance(self.activity, bs.GameActivity) and hasattr(self.activity, 'has_ended') and not self.activity.has_ended():
                    if not self.tick_timer:
                        self.tick_timer = bs.Timer(0.1, self.act, repeat=True)
                        self.saved = False
                        self.save()
                elif isinstance(self.activity, (FreeForAllVictoryScoreScreenActivity,TeamSeriesVictoryScoreScreenActivity)):
                    # very specific check, but allow 
                    self.tick_timer = None
                    def still_():
                        if isinstance(self.activity, (FreeForAllVictoryScoreScreenActivity,TeamSeriesVictoryScoreScreenActivity)):
                            self.punch()
                    # Continue after 3 seconds.
                    bs.timer(3, still_)
                else:
                    self.tick_timer = None
                    # Okay, just clear our stuff when activity is dyin
                    if self.activity.expired:

                        self.sessionteam=None
                        self.activity=None
                        self.activityplayer=None
                        
                    
        else:
            self.tick_timer = None
                
        bs.apptimer(0.1, self.check)

    # AI
    def act(self):
        if not self.active or not self.activity or not self.activityplayer:
            return

        if hasattr(self.activity, 'has_ended') and self.activity.has_ended():
            self.tick_timer = None
            return

        if self.activity.globalsnode.paused:
            return

        context = self.get_context()
        if context is None:
            return

        with context:
            spaz: PlayerSpaz = getattr(self.activityplayer, 'actor', None)
            if not spaz or not spaz.is_alive():
                return

            node = spaz.node
            if not node.exists():
                return

            if random.random() < 0.15:
                self.award_xp(1)

            # Yes im rewriting my entire ai

            behaviors = self.data.get('behaviors', {})
            targeting = self.data.get('targeting', {})
            level_scale = min(1.0, max(0.02, self.data['level'] / 50.0))
            aggressive = behaviors.get('aggressive', 0.5)
            runner = behaviors.get('runner', 0.5)
            grounded = behaviors.get('grounded', 0.5)
            punchiness = behaviors.get('punch', 0.5)
            bombiness = behaviors.get('bomb', 0.3)
            pickupiness = behaviors.get('pickup', 0.2)
            nearness = behaviors.get('near', 0.5)
            runner_value = behaviors.get('hold_runner', 0.5)
            current_time = bs.time()

            level_mult = 0.5 + level_scale
            level_mult = min(level_mult, 1.35)

            


            if (
                self._cached_target is None
                or current_time > self._target_refresh
                or not getattr(self._cached_target, 'node', None)
                or not self._cached_target.is_alive()
            ):
                self._cached_target = self._find_target()
                self._target_refresh = current_time + 0.35

            target_actor = self._cached_target
            flag_pos = self.get_flag_position()
            
            target_node = getattr(target_actor, 'node', None)

            try:
                target_pos = target_node.position
                our_pos = node.position
            except Exception:
                return

            distance = 999.0
            dx = target_pos[0] - our_pos[0]
            dz = target_pos[2] - our_pos[2]
            distance = math.sqrt(dx * dx + dz * dz)

            current_game = type(self.activity)

            if self.learn and target_actor:
                self._learn_from_target(target_actor)

            
            self.move_left_right(0.0)
            self.move_up_down(0.0)
            self.run(0.0)

            # mini game specifics

            # Meteor Shower: only jump input matters.
            if isinstance(self.activity, MeteorShowerGame):

                velocity = getattr(node, 'velocity', (0, 0, 0))

                # Panic jumps when moving dangerously.
                if abs(velocity[1]) > 1.2:
                    self.jump()
                    return

                # Random survival movement.
                if random.random() < (0.02 + ((1.0 - grounded) * 0.08)):
                    self.jump()

                if random.random() < 0.08:
                    self.move_left_right(random.uniform(-1.0, 1.0))
                    self.move_up_down(random.uniform(-1.0, 1.0))

                return

            
            if isinstance(self.activity, BowlingGame):

                try:
                    pos = node.position
                except Exception:
                    return

                
                if pos[0] > 0.4:
                    self.move_left_right(-1.0)
                    self.run(1.0)
                else:
                    
                    self.move_up_down(random.uniform(-0.15, 0.15))

                    if random.random() < (0.12 + (bombiness * 0.25)):
                        self.bomb()

                    if (
                        level_scale > 0.45
                        and random.random() < (0.03 + (bombiness * 0.08))
                    ):
                        self.jump()

                return

        
            if isinstance(self.activity, (OnslaughtFFAGame, RunaroundFFAGame)):

                if target_actor and target_actor.node.exists():
                    target_pos_vec = self.get_target_by_pos(
                        node,
                        target_actor.node.position
                    )

                    # Runaround prefers bombing.
                    if isinstance(self.activity, RunaroundFFAGame):
                        self.move_left_right(-target_pos_vec.x * 0.35)
                        self.move_up_down(target_pos_vec.z * 0.35)

                        if distance > 1.4:
                            self.bomb()

                        if distance < 1.2 and aggressive > 0.55:
                            self.punch()

                    # Onslaught allows more aggression.
                    else:
                        self.move_to_target(target_pos_vec)
                        self.run(min(1.0, 0.35 + runner_value))

                        if distance < 2.4:
                            if bombiness > 0.35:
                                self.bomb()

                            if aggressive > 0.28:
                                self.punch()

                return

            # King of the Hill.
            if isinstance(self.activity, KingOfTheHillGame):

                if flag_pos:
                    hill_target = self.get_target_by_pos(node, flag_pos)

                    self.move_left_right(hill_target.x)
                    self.move_up_down(-hill_target.z)

                    self.run(min(1.0, 0.35 + runner_value))

                    # Offensive hill defense.
                    if target_actor and distance < 2.3:

                        if aggressive > 0.3:
                            self.punch()

                        if bombiness > 0.45 and distance > 1.0:
                            self.bomb()

                        if pickupiness > 0.65:
                            self.pickup()

                return

            # Keep Away.
            if isinstance(self.activity, KeepAwayGame):

                try:
                    holding_flag = bool(
                        node.hold_node
                        and node.hold_node.getdelegate(flag.Flag)
                    )
                except Exception:
                    holding_flag = False

                if holding_flag:
                    # Defensive circling while holding.
                    if target_actor and target_actor.node.exists():
                        target_pos_vec = self.get_target_by_pos(
                            node,
                            target_actor.node.position
                        )

                        perp_x = target_pos_vec.z
                        perp_z = -target_pos_vec.x

                        self.move_left_right(perp_x)
                        self.move_up_down(-perp_z)

                        if distance < 2.2:
                            if aggressive > 0.35:
                                self.punch()

                            if bombiness > 0.45:
                                self.bomb()

                    self.run(min(1.0, 0.5 + runner_value))

                elif flag_pos:
                    # Chase flag.
                    flag_target = self.get_target_by_pos(node, flag_pos)

                    self.move_left_right(flag_target.x)
                    self.move_up_down(-flag_target.z)
                    self.run(1.0)

                    if random.random() < 0.03:
                        self.jump()

                return

            # Chosen One / Crown.
            if isinstance(self.activity, (ChosenOneGame, CrownGame)):

                is_chosen = False

                try:
                    is_chosen = self.activity._chosen_one_player == self.activityplayer
                except Exception:
                    pass

                if is_chosen:
                    # Run away and survive.
                    if target_actor and target_actor.node.exists():
                        target_pos_vec = self.get_target_by_pos(
                            node,
                            target_actor.node.position
                        )

                        self.move_left_right(-target_pos_vec.x)
                        self.move_up_down(target_pos_vec.z)
                        self.run(1.0)

                        if distance < 2.5:
                            if bombiness > 0.35:
                                self.bomb()

                            if aggressive > 0.55:
                                self.punch()

                else:
                    # Rush objective/target.
                    if flag_pos:
                        flag_target = self.get_target_by_pos(node, flag_pos)

                        self.move_left_right(flag_target.x)
                        self.move_up_down(-flag_target.z)
                        self.run(1.0)

                    elif target_actor and target_actor.node.exists():
                        target_pos_vec = self.get_target_by_pos(
                            node,
                            target_actor.node.position
                        )

                        self.move_to_target(target_pos_vec)

                        if distance < 2.0:
                            self.punch()

                return

            # Free For All CTF.
            if isinstance(self.activity, FreeForAllCTFByGUMMYBOIYT):

                flags = []

                for n in bs.getnodes():
                    try:
                        if n.getdelegate(flag.Flag):
                            flags.append(n)
                    except Exception:
                        pass

                home_flag = None
                enemy_flag = None

                if len(flags) >= 2:
                    enemy_flag = flags[0]
                    home_flag = flags[1]

                try:
                    holding_flag = bool(
                        node.hold_node
                        and node.hold_node.getdelegate(flag.Flag)
                    )
                except Exception:
                    holding_flag = False

                # Return stolen flag.
                if holding_flag and home_flag:
                    home_target = self.get_target_by_pos(
                        node,
                        home_flag.position
                    )

                    self.move_left_right(home_target.x)
                    self.move_up_down(-home_target.z)
                    self.run(1.0)

                    if target_actor and distance < 2.0:
                        if aggressive > 0.3:
                            self.punch()

                        if bombiness > 0.45:
                            self.bomb()

                # Steal enemy flag.
                elif enemy_flag:
                    enemy_target = self.get_target_by_pos(
                        node,
                        enemy_flag.position
                    )

                    self.move_left_right(enemy_target.x)
                    self.move_up_down(-enemy_target.z)
                    self.run(1.0)

                    if target_actor and distance < 2.2:
                        if aggressive > 0.4:
                            self.punch()

                        if bombiness > 0.4:
                            self.bomb()

                return

            if not target_actor or not target_actor.node.exists():
             
                if flag_pos:
                    try:
                        holding_flag = bool(
                            node.hold_node
                            and node.hold_node.getdelegate(flag.Flag)
                        )
                    except Exception:
                        holding_flag = False

                    # Chase the flag.
                    if not holding_flag:
                        flag_target = self.get_target_by_pos(node, flag_pos)

                        self.move_left_right(flag_target.x)
                        self.move_up_down(-flag_target.z)

                        if random.random() < runner:
                            self.run(behaviors.get('hold_runner')*0.5)

                        # Dive toward the flag sometimes.
                        if random.random() < 0.015:
                            self.jump()

                        return
                return

            # Basic edge awareness.
            near_edge = (
                abs(our_pos[0]) > 6.5
                or abs(our_pos[2]) > 6.5
            )

            if distance <= 0.01:
                return

            target_pos_vec = self.get_target_by_pos(node, target_node.position)

            

            # State expiration.
            if current_time > self.state_timer:
                self.state_locked = False

            
            if not self.state_locked:
                # states
                state_scores = {}

                
                combo_bonus = min(2.0, self.combo_hits * 0.35)
                hesitation_penalty = min(1.5, self.failed_attacks * 0.2)

                state_scores['attack'] = (
                    aggressive * (2.1 * level_mult)
                    + punchiness * (1.8 * level_mult)
                    + nearness * (1.2 * level_mult)
                    + (max(0.0, 2.2 - distance) * max(0.15, level_scale))
                    + combo_bonus
                    - hesitation_penalty
                )

                # Avoid suicidal aggression near map edges.
                if near_edge:
                    state_scores['attack'] *= 0.55

                
                state_scores['bomb'] = (
                    bombiness * (5.0 * level_mult)
                    + max(0.0, distance - 1.2)
                    + ((1.0 - nearness) * 2.2)
                )
                
                state_scores['pickup'] = (
                    pickupiness * (3.0 * level_mult)
                    + nearness * (1.2 * level_mult)
                    + max(0.0, 1.8 - distance)
                )

                # Chase
                state_scores['chase'] = (
                    runner * (2.0 * level_mult)
                    + max(0.0, distance - 3.0)
                )

                # circling.
                state_scores['circle'] = (
                    grounded * (1.8 - level_scale)
                    + aggressive * 0.2
                    + ((1.0 - level_scale) * 2.5)
                )


                # Objective behavior.
                objective_focus = targeting.get(
                    'targets_objective',
                    0.0
                )

                if flag_pos:
                    state_scores['flag'] = (
                        4.0
                        + (objective_focus * 8.0)
                        + (runner * 2.0)
                    )

                    # Objective-focused bots still fight.
                    state_scores['attack'] += objective_focus * 2.5
                    state_scores['bomb'] += objective_focus * 1.5
                    state_scores['chase'] += objective_focus * 1.0

                

               
                # Revenge targeting 
                revenge = targeting.get('target_revenge', 0.0)
                state_scores['attack'] += revenge * 3.0
                state_scores['pickup'] += revenge * 1.2
                state_scores['chase'] += revenge * 2.0

                # Winning-player 
                hunt_winner = targeting.get('targets_winning', 0.0)
                state_scores['attack'] += hunt_winner * 1.5
                state_scores['bomb'] += hunt_winner * 1.0

                # Losing-player
                hunt_loser = targeting.get('targets_losing', 0.0)
                state_scores['attack'] += hunt_loser * 1.0
                state_scores['pickup'] += hunt_loser * 2.0

                # Random personalities
                target_random = targeting.get('target_random', 1.0)
                state_scores['circle'] += target_random * random.uniform(0.0, 2.0)

                # slight randomness
                for state_name in state_scores:
                    state_scores[state_name] += random.uniform(0.0, 0.35 * (1.2 - level_scale))

                best_state = max(
                    state_scores,
                    key=state_scores.get
                )

                if best_state == 'attack':
                    self.set_state(
                        'attack',
                        0.35 + aggressive * 0.35,
                        lock=True
                    )

                elif best_state == 'bomb':
                    self.set_state(
                        'bomb',
                        0.55 + bombiness * 0.3,
                        lock=True
                    )

                elif best_state == 'pickup':
                    self.set_state(
                        'pickup',
                        0.5,
                        lock=True
                    )

                elif best_state == 'flag':
                    self.set_state('flag', 1.2)

                elif best_state == 'chase':
                    self.set_state('chase', 0.9)

                else:
                    self.set_state('circle', 0.6)

            
            if level_scale < 0.2 and random.random() < 0.18:
                self.move_left_right(0.0)
                self.move_up_down(0.0)

            elif self.state == 'attack':

                self.run(min(1.0, runner_value * level_mult))
                self.move_to_target(target_pos_vec)

                attack_window = 0.65 - (level_scale * 0.35)

                if current_time - self.last_attack_time > attack_window:
                    if random.random() < (0.25 + (level_scale * 0.75)):
                        self.punch()
                        self.last_attack_time = current_time

                if level_scale > 0.3:
                    bs.timer(0.08, self.punch)

                if (
                    level_scale > 0.72
                    and not near_edge
                    and random.random() < 0.18
                ):
                    bs.timer(0.18, self.jump)

                if level_scale > 0.82:
                    bs.timer(0.24, self.punch)

            elif self.state == 'bomb':

                self.run(min(1.0, runner_value * (0.4 + level_scale)))

                # Bombers should strafe and maintain spacing,
                # not blindly reverse themselves off cliffs.
                perp_x = target_pos_vec.z
                perp_z = -target_pos_vec.x

                strafe_dir = random.choice([-1.0, 1.0])

                move_x = (perp_x * 0.55 * strafe_dir) - (target_pos_vec.x * 0.18)
                move_z = (-perp_z * 0.55 * strafe_dir) + (target_pos_vec.z * 0.18)

                # Strong edge correction.
                if near_edge:
                    center_target = self.get_0x0(node, (0, 0, 0))
                    move_x += center_target.x * 1.25
                    move_z += -center_target.z * 1.25

                self.move_left_right(move_x)
                self.move_up_down(move_z)

                # Better bomb timing.
                if distance > 1.35 or level_scale > 0.7:
                    self.bomb()

               
                if near_edge:
                    center_target = self.get_0x0(node, (0, 0, 0))
                    self.move_left_right(center_target.x)
                    self.move_up_down(-center_target.z)
                    self.run(0.25)

                if level_scale > 0.45:
                    bs.timer(
                        random.uniform(0.08, 0.18),
                        self.punch
                    )

                # jump n bomb
                if (
                    level_scale > 0.82
                    and not near_edge
                    and random.random() < 0.12
                ):
                    bs.timer(0.05, self.jump)
            elif self.state == 'chase':

                # High-level bots chase more carefully.
                chase_strength = min(
                    1.0,
                    (0.35 + runner) * (0.45 + level_scale)
                )

                if near_edge:
                    chase_strength *= 0.5

                self.run(chase_strength)
                self.move_to_target(target_pos_vec)
            elif self.state == 'circle':

                perp_x = target_pos_vec.z * 0.4
                perp_z = -target_pos_vec.x

                strafe_dir = random.choice([-1.0, 1.0])

                self.move_left_right(perp_x * strafe_dir)
                self.move_up_down(-perp_z * strafe_dir)

                if distance > 2.5:
                    self.move_left_right(
                        (perp_x * strafe_dir) + (target_pos_vec.x * 0.35)
                    )
                    self.move_up_down(
                        (-perp_z * strafe_dir) + (-target_pos_vec.z * 0.35)
                    )

                if (
                    current_time - self.last_jump_time > (0.9 - (level_scale * 0.45))
                    and random.random() < (0.08 + ((1.0 - grounded) * 0.05))
                ):
                    self.jump()
                    self.last_jump_time = current_time

            elif self.state == 'pickup':

                # Don't blindly sprint off edges.
                self.run(min(0.9, runner_value * (0.5 + level_scale)))

                if distance > 0.9:
                    self.move_to_target(target_pos_vec)

                self.pickup()

                if level_scale > 0.45:
                    bs.timer(0.12, self.punch)

                if level_scale > 0.7:
                    bs.timer(0.2, self.throw)

          
            
            elif self.state == 'flag':

                if flag_pos:

                    flag_target = self.get_target_by_pos(
                        node,
                        flag_pos
                    )

                    self.move_left_right(flag_target.x)
                    self.move_up_down(-flag_target.z)

                    self.run(min(1.0, 0.5 + runner_value))

                    # Fight while pathing to objective.
                    if distance < 2.2:

                        if aggressive > 0.35:
                            self.punch()

                            if level_scale > 0.45:
                                bs.timer(0.08, self.punch)

                        if (
                            bombiness > 0.45
                            and distance > 1.2
                        ):
                            if random.random() < 0.18:
                                self.bomb()

                        if pickupiness > 0.65:
                            self.pickup()

                    # Mobility.
                    if random.random() < (0.04 + (1.0 - grounded) * 0.08):
                        self.jump()

            

            # Anti-stuck movement.
            velocity = getattr(node, 'velocity', (0.0, 0.0, 0.0))
            horizontal_speed = math.sqrt((velocity[0] ** 2) + (velocity[2] ** 2))

            if (
                distance > 3.0
                and horizontal_speed < 0.05
                and not self.state_locked
            ):
                self.move_left_right(random.uniform(-1.0, 1.0))
                self.move_up_down(random.uniform(-1.0, 1.0))

                if (
                    not near_edge
                    and current_time - self.last_jump_time > 1.25
                    and random.random() < (0.08 + (level_scale * 0.12))
                ):
                    self.jump()
                    self.last_jump_time = current_time

            # Powerup collection.
            if random.random() < 0.4:
                powerup_pos = self.get_nearby_powerups(node, range=2.5)

                if powerup_pos:
                    target = self.get_target_by_pos(node, powerup_pos)
                    self.move_left_right(target.x)
                    self.move_up_down(-target.z)
                    self.run(behaviors.get('hold_runner'))

    def _find_target(self):
        if not self.activity or not hasattr(self.activity, 'players'):
            return None

        best_target = None
        highest_score = -1.0

        weights = self.data.get('targeting', {})
        w_random = weights.get('target_random', 1.0)
        w_winning = weights.get('targets_winning', 0.0)
        w_losing = weights.get('targets_losing', 0.0)
        w_revenge = weights.get('target_revenge', 0.0)

        max_fall = -1.72
        if isinstance(bs.getsession(), bs.CoopSession):
            try:
                all_players = [b for b in self.activity._bots.get_living_bots()]
            except:
                all_players = []
        else:
            all_players = [p for p in self.activity.players if p.is_alive() and p != self.activityplayer]
        if not all_players:
            return None

        players_by_score = sorted(all_players, key=lambda p: getattr(p, 'score', 0))

        for p in all_players:
            if isinstance(p, SpazBot):
                actor = p
            else:
                actor = p.actor
            if not actor or not actor.is_alive() or actor.node.velocity[2] < max_fall:
                continue
            
            score = random.random() * max(0.15, w_random)

            try:
                my_pos = self.activityplayer.actor.node.position
                target_pos = actor.node.position

                distance = math.dist(my_pos, target_pos)

                # Prefer nearby enemies.
                score += max(0.0, 8.0 - distance) * 0.18

            except Exception:
                pass
            
            if len(players_by_score) > 1:
                if p == players_by_score[-1]: 
                    score += w_winning
                if p == players_by_score[0]:  
                    score += w_losing

            # Revenge targeting.
            try:
                last_attacker = self.extra_data2.get('last_attacker')

                if (
                    last_attacker is not None
                    and getattr(p, 'sessionplayer', None)
                ):
                    if id(p.sessionplayer) == last_attacker:
                        score += w_revenge * 5.0

            except Exception:
                pass

            if score > highest_score:
                highest_score = score
                best_target = actor

        return best_target

    def _learn_from_target(self, target_actor):
        if not self.learn or not target_actor or not target_actor.node.exists():
            return

        target_node = target_actor.node
        behaviors = self.data['behaviors']
        targeting = self.data['targeting']
        spaz = getattr(self.activityplayer, 'actor', None)

      
        # High-level amiibo should stabilize instead of constantly rewriting
        # their entire personality from a few interactions.
        level_scale = min(1.0, max(0.02, self.level / 50.0))

        base_lr = 0.035
        base_decay = 0.008

        # Older/high-level bots learn slower and forget slower.
        memory_strength = 1.0 - (level_scale * 0.7)

        lr = base_lr * memory_strength
        decay = base_decay * memory_strength

        target_move_x = getattr(target_node, 'move_left_right', 0.0)
        target_move_z = getattr(target_node, 'move_up_down', 0.0)
        target_speed = (target_move_x**2 + target_move_z**2)**0.5
        target_running = getattr(target_node, 'run', 0.0)

        if target_speed > 0.8:
            behaviors['aggressive'] = min(1.0, behaviors['aggressive'] + lr*0.5)
            behaviors['runner'] = min(1.0, behaviors['runner'] + lr)
            if target_running:
                behaviors['hold_runner'] = min(1.0, behaviors['hold_runner'] + (target_speed * lr))
        else:
            behaviors['aggressive'] = max(0.0, behaviors['aggressive'] - decay)
            behaviors['runner'] = max(0.0, behaviors['runner'] - decay*1.5)
            behaviors['hold_runner'] = max(0.0, behaviors['hold_runner'] - decay*0.5)


        dist = 999.0
        if spaz and spaz.node.exists():
            dx = target_node.position[0] - spaz.node.position[0]
            dz = target_node.position[2] - spaz.node.position[2]
            dist = (dx**2 + dz**2)**0.5

        if dist < 2.5:
                behaviors['near'] = min(1.0, behaviors['near'] + lr * 2.8)
                behaviors['aggressive'] = max(
                    0.0,
                    behaviors['aggressive'] - (decay * 1.8)
                )
        else:
                behaviors['near'] = max(0.0, behaviors['near'] - decay * 0.3)

        # Punch
        if getattr(target_node, 'punch_pressed', False):
            behaviors['aggressive'] = min(1.0, behaviors['aggressive'] + (lr * 0.2))
            behaviors['punch'] = min(1.0, behaviors['punch'] + lr)

            # Do NOT massively erase bombing identity from a few punches.
            behaviors['bomb'] = max(
                0.08,
                behaviors['bomb'] - (decay * 0.25)
            )

            behaviors['pickup'] = max(
                0.0,
                behaviors['pickup'] - (decay * 0.18)
            )

            behaviors['near'] = min(
                1.0,
                behaviors['near'] + (lr * 0.35)
            )

        # Bomb
        if getattr(target_node, 'bomb_pressed', False):
            # Bomb identity should build strongly.
            behaviors['bomb'] = min(
                1.0,
                behaviors['bomb'] + (lr * 3.2)
            )

            # Preserve hybrid playstyles.
            behaviors['punch'] = max(
                0.12,
                behaviors['punch'] - (decay * 0.22)
            )

            behaviors['pickup'] = max(
                0.0,
                behaviors['pickup'] - (decay * 0.18)
            )

            # Bombers prefer spacing.
            behaviors['near'] = max(
                0.05,
                behaviors['near'] - (lr * 0.65)
            )

        # Grab
        if getattr(target_node, 'pickup_pressed', False):
            behaviors['pickup'] = min(1.0, behaviors['pickup'] + lr)
            behaviors['punch'] = max(0.0, behaviors['punch'] - decay)
            behaviors['bomb'] = max(0.0, behaviors['bomb'] - decay)
            behaviors['near'] = min(1.0, behaviors['near'] + lr)

        # Jumping
        if getattr(target_node, 'jump_pressed', False): 
            behaviors['grounded'] = max(0.0, behaviors['grounded'] - lr)
        else:
            behaviors['grounded'] = min(1.0, behaviors['grounded'] + decay)

        # Learn targeting personality.
        # Aggressive close-range targets.
        if dist < 2.0:
            targeting['target_revenge'] = min(
                1.0,
                targeting['target_revenge'] + (lr * 0.15)
            )

            targeting['targets_winning'] = min(
                1.0,
                targeting['targets_winning'] + (lr * 0.08)
            )

        # Bomb/spacer targets teach objective spacing.
        if getattr(target_node, 'bomb_pressed', False):
            targeting['targets_objective'] = min(
                1.0,
                targeting['targets_objective'] + (lr * 0.12)
            )

        # Random movement creates less predictable AI.
        if target_speed > 0.9:
            targeting['target_random'] = min(
                1.5,
                targeting['target_random'] + (lr * 0.08)
            )
        else:
            targeting['target_random'] = max(
                0.15,
                targeting['target_random'] - (decay * 0.03)
            )

        # dont want thigs to be maxed
        for k in behaviors:
            behaviors[k] = max(0.0, min(1.0, behaviors[k]))

        # behaviors
        behavior_keys = [
            'aggressive',
            'runner',
            'hold_runner',
            'punch',
            'bomb',
            'pickup',
            'near',
            'grounded'
        ]

        total_behavior = sum(
            max(0.0, behaviors.get(k, 0.0))
            for k in behavior_keys
        )

        
        if total_behavior > 4.6:
            overflow = total_behavior - 4.6

            for k in behavior_keys:
                value = behaviors.get(k, 0.0)

                # Preserve dominant traits.
                if value > 0.55:
                    reduction = overflow * 0.035
                else:
                    reduction = overflow * 0.08

                behaviors[k] = max(0.0, value - reduction)

    
        for k in targeting:
            targeting[k] = max(0.0, min(1.5, targeting[k]))

    
        target_total = sum(max(0.0, targeting.get(k, 0.0)) for k in targeting)

        if target_total > 2.5:
            scale = 2.5 / target_total
            for k in targeting:
                targeting[k] *= scale

    def award_xp(self, amount: int):
        if self.level >= 50:
            return

        self.xp += amount
        
        while self.level < 50:
            threshold = self.level * 3
            if self.xp >= threshold:
                self.xp -= threshold
                self.level += 1
                self.data['level'] = self.level
                
                with self.get_context():
                   
                    bs.getsound('amiibo/levelup').play(0.5)
                    
                        
                    if self.activityplayer.actor and self.activityplayer.actor.exists():
                        self.activity.show_level_up(self.level, self.activityplayer.node.position, self.activityplayer.color)
                 
                        
                        if self.activityplayer.actor.exists():
                            self.activityplayer.actor.handlemessage(bs.CelebrateMessage(0.3))
            else:
                break
                
        self.data['xp'] = self.xp

    def get_target_by_pos(self, node, tpos):
        context = self.get_context()
        if context is None:
            return bs.Vec3(0, 0, 0)
        with context:
            pos = node.position if node else (0, 0, 0)
            our_pos = bs.Vec3(pos[0], 0, pos[2])
            target_pt_raw = bs.Vec3(*tpos)
            diff = target_pt_raw - our_pos
            diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
            return diff.normalized()

    def get_0x0(self, node, def_pos):
        context = self.get_context()
        if context is None:
            return bs.Vec3(0, 0, 0)
        with context:
            pos = node.position if node else (0, 0, 0)
            our_pos = bs.Vec3(pos[0], 0, pos[2])
            target_pt_raw = bs.Vec3(*def_pos)
            diff = target_pt_raw - our_pos
            diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
            return diff.normalized()

    def move_to_target(self, target, flee=False):
        context = self.get_context()
        if context is None:
            return
        with context:
            multiplier = -1.0 if flee else 1.0
            if target is None:
                self.move_left_right(0)
                self.move_up_down(0)
            else:
                
                    self.move_left_right( target.x * multiplier)
                    self.move_up_down(-target.z * multiplier)

    def get_flag_position(self):
        context = self.get_context()
        if context is None:
            return None
        with context:
            for node in bs.getnodes():
                if node.getdelegate(flag.Flag): 
                    return node.position
            return None

    def get_nearby_powerups(self, node, range: float = 3):
        context = self.get_context()
        if context is None:
            return None
        with context:
            closest_powerup = None
            closest_distance = 9999.0

            for n in bs.getnodes():
                if n.getdelegate(powerupbox.PowerupBox):

                    powerup_position = n.position
                    spaz_position = node.position

                    distance = math.dist(
                        spaz_position,
                        powerup_position
                    )

                    if (
                        distance <= range
                        and distance < closest_distance
                    ):
                        closest_distance = distance
                        closest_powerup = powerup_position

            return closest_powerup

    # FAKE CONTROLLER


    # oh my fucking god you're annoying
    def get_context(self):
        if not self.active:
            return None
        try:
            # Check if host session and its context are fully real
            sess = bs.get_foreground_host_activity()
            if sess and hasattr(sess, 'context') and sess.context:
                return sess.context
        except Exception:
            pass
        try:
            act = bs.get_foreground_host_session()
            if act and hasattr(act, 'context') and act.context:
                return act.context
        except Exception:
            pass
        return None

    def punch(self):
        # Okay.. context ref
        with self.get_context():
            try:
                self._input_bindings[InputType.PUNCH_PRESS]()
                self._input_bindings[InputType.PUNCH_RELEASE]()
            except Exception:
                pass    
    def pickup(self):
        with self.get_context():
            try:
                self._input_bindings[InputType.PICK_UP_PRESS]()
                self._input_bindings[InputType.PICK_UP_RELEASE]()
            except Exception:
                pass   
    def bomb(self):
        with self.get_context():
            try:
                self._input_bindings[InputType.BOMB_PRESS]()
                self._input_bindings[InputType.BOMB_RELEASE]()
            except Exception:
                pass
    def jump(self):
        with self.get_context():
            try:
                self._input_bindings[InputType.JUMP_PRESS]()
                self._input_bindings[InputType.JUMP_RELEASE]()
            except Exception:
                pass
    def throw(self):
        # Maps simulated throwing combinations from AIBot
        with self.get_context():
            spaz = getattr(self.activityplayer, 'actor', None)
            if spaz and spaz.node.exists() and spaz.node.hold_node:
                self.jump()
                self.bomb()
    def move_up_down(self, value):
        with self.get_context():
            try:
                self._input_bindings[InputType.UP_DOWN](value)
            except Exception:
                pass
    def move_left_right(self, value):
        with self.get_context():
            try:
                self._input_bindings[InputType.LEFT_RIGHT](value)
            except Exception:
                pass
    def run(self, value):
        with self.get_context():
            try:
                self._input_bindings[InputType.RUN](value)
            except Exception:
                pass
        
        
        
    
    # Okay lets define the internal functions for
    # _bascenev1.SessionPlayer
    def get_v1_account_id(self):
        return 0   

    def in_game(self):
        return self.active
    
    def exists(self):
        return self.active
    
    def setname(self, *args, **kwargs):
        # Dont care
        self.name = self.data['nickname']
    
    def getname(self, *args, **kwargs):
        with self.get_context():
            return self.nickname
    
    def setdata(
            # WoW!
            self,
            team: bs.SessionTeam,
            character: str,
            color: tuple[float, float, float],
            highlight: tuple[float, float, float],
        ):
            with self.get_context():
                self.sessionteam = team
                self.character = character
                self.color = color
                self.highlight = highlight
    def set_icon_info(self,
            tex_name,
            tint_tex_name,
            clr,
            clr2,
        ):  
        with self.get_context():
            self.icon = {
                'texture': tex_name,
                'tint_texture': tint_tex_name,
                'tint_color': clr,
                'tint2_color': clr2,
            }
            
    def get_icon(self):
        with self.get_context():
            # Dude, fuck you honestly. im trying to optimize this shit
            return {
                'texture': bs.gettexture(self.icon['texture']),
                'tint_texture': bs.gettexture(self.icon['tint_texture']),
                'tint_color': self.icon['tint_color'],
                'tint2_color': self.icon['tint2_color'],
                # For stuff with images.
                'is_amiibo': True,
                'level': int(self.data['level'])
            }
        
    
    def assigninput(self, type: bs.InputType | tuple[bs.InputType, ...], call: callable):
        with self.get_context():
            
            if isinstance(type, tuple):
                for single_input in type:
                    self._input_bindings[single_input] = call
            else:
                self._input_bindings[type] = call

    def resetinput(self):
        self._input_bindings.clear()

    def setactivity(self, activity: bs.Activity):
        self.activity = activity

    def remove_from_game(self):
        # This is basically our self.expire() function 
        # So expire lol
        self.tick_timer = None
        self.saved = False
        self.save()
        self.active = False
        self.node = bs.Node(None)
        self.icon = {}
        self.inputdevice.remove_from_game()
        self.activity = None
        self.resetinput()

    def setnode(self, node: bs.Node):
        with self.get_context():
            self.node = node

        
class FigureInputDevice:
    def __init__(self,data: dict = {}):
        self.data = data
        self.active = True
        # Set attributes that _bascenev1.InputDevice has
    

        # Always local device
        self.is_remote_client = True # Let's like prevent this guy from accessing silly controller input
        self.is_test_input = False
        self.is_controller_app = False

        self.has_meaningful_button_names = False
        self.id = len(bs.getsession().sessionplayers)
        self.name = self.data['nickname'] + 'Input'
        self.unique_identifier = f'#{self.id}'
        self.client_id = -1
    
    def get_v1_account_name(self, *args, **kwargs):
        return 'Device'
    
    def remove_from_game(self):
        self.active = False
    
    def get_default_player_name(self):
        return self.data['nickname']
    def get_player_profiles(self):
        return {
             self.data['nickname']: {
        "character": self.data['character'],
        "color": list(self.data['color']),
        "global": False,
        "cosmetic": self.data['cosmetic'],
        "highlight":list(self.data['highlight']),
        "icon": "\ue01e",
            },
        }
   