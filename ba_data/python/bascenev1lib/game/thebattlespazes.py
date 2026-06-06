# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any, Sequence



class BattleTeam:

    def __init__(self, team: str):
        self.team = team
    
    def __str__(self):
        return f'BattleTeam {self.team}'

class BattleSpaz(Spaz):

    def __init__(self, team: BattleTeam, battler: str, position: tuple = (0, 0, 0)):

        cosmetic = None
        self.battler = battler
        self.team = team
        
        if battler == 'Base':
            if not bs.getactivity().player_2:

                character = 'Spaz'
                color = (0, 0, 1) if team is bs.getactivity().team_player else (1, 0, 0)
                highlight = (1, 1, 1)

            else:
                if team is bs.getactivity().team_player:
                    player = bs.getactivity().players[0]
                else:
                    player = bs.getactivity().players[1]

                character = player.character
                try:
                    cosmetic =  bs.getsession().customdata[player.sessionplayer]['cosmetic']
                except:
                    cosmetic = None
                color = player.color
                highlight = player.highlight

                
                player = None
            hp = 10000
            self.range = 9999
            self._attack_cooldown = 0.2
        elif battler == 'BattleSpaz':
            character = 'Spaz'
            color = (0, 0, 1) if team is bs.getactivity().team_player else (1, 0, 0)
            highlight = (0, 0.8, 1) if team is bs.getactivity().team_player else (0.8, 0, 0)
            hp = 100
            self.range = 0.8
            self._attack_cooldown = 0.6
        elif battler == 'WallBuilder':
            character = 'Spaz'
            color = (0, 0, 0.3) if team is bs.getactivity().team_player else (0.3, 0, 0)
            highlight = (0, 0.8, 1) if team is bs.getactivity().team_player else (0.8, 0, 0)
            hp = 100
            self.range = 1.5
            self._attack_cooldown = 7
        elif battler == 'Ranger':
            character = 'Zoe'
            color = (0, 0, 0.8) if team is bs.getactivity().team_player else (0.8, 0, 0)
            highlight = (0.8, 0.8, 0.8)
            hp = 85
            self.range = 5.5
            self._attack_cooldown = 1.3
        elif battler == 'Wall':
            character = 'Santa Claus'
            color = (0.3, 0.23, 0.8) if team is bs.getactivity().team_player else (0.8, 0.23, 0.3)
            highlight = (0.8, 0.8, 0.8)
            hp = 165
            self.range = 9999
            self._attack_cooldown = 1.2
        elif battler == 'Speedster':
            character = 'Snake Shadow'
            color = (0, 0, 0.8) if team is bs.getactivity().team_player else (0.8, 0, 0)
            highlight = (0, 0, 0.2) if team is bs.getactivity().team_player else (0.2, 0, 0)
            hp = 35
            self.range = 0.9
            self._attack_cooldown = 0.2
        elif battler == 'Healer':
            character = 'Spaz'
            color = (0, 1, 0.5) if team is bs.getactivity().team_player else (1, 0.5, 0)
            highlight = (0.5, 1, 0.5)
            hp = 80
            self.range = 5.0
            self._attack_cooldown = 1.2
        elif battler == 'Titan':
            character = 'Bones'
            color = (0.5, 0.2, 1) if team is bs.getactivity().team_player else (1, 0.2, 0.5)
            highlight = (1, 0.8, 0.2)
            hp = 300
            self.range = 1.2
            self._attack_cooldown = 2.0

        elif battler == 'Bomber':
            character = 'Kronk'
            color = (0.1, 0.4, 0.9) if team is bs.getactivity().team_player else (1, 0.2, 0.2)
            highlight = (1, 0.8, 0.3)
            hp = 70
            self.range = 2.5
            self._attack_cooldown = 1.8


        elif battler == 'Summoner':
            character = 'Grumbledorf'
            color = (0.6, 0.2, 1) if team is bs.getactivity().team_player else (1, 0.2, 0.6)
            highlight = (1, 0.8, 1)
            hp = 90
            self.range = 4.5
            self._attack_cooldown = 9.0


        else:
            raise ValueError(f'unknown Battler {battler}')
       
                 
        super().__init__(color, highlight, character, None, False, False, True, False, cosmetic)
        self.impact_scale = 0.0
        self.hitpoints_max = hp * 10
        self.hitpoints = self.hitpoints_max
        self.node.name = battler
        self.node.name_color = color
        
        self._last_attack_time = 0.0
        self._held_bomb = None
        
        self.handlemessage(bs.StandMessage(position))
        
        self.node.materials += (self.getactivity().non_collide_mat,)
        self.node.roller_materials += (self.getactivity().non_collide_mat,)
        self.node.extras_material += (self.getactivity().non_collide_mat,)
        self._held_bomb = bs.Node(None)
        

        
        
        bs.timer(0.1, self.battler_tick, repeat=True)

    def battler_move(self, move: int):
        if not self.is_alive():
            return
        
        self.node.move_up_down = 0.0
        self.node.move_left_right = move * self.get_team_direction()

    def get_team_direction(self):
        return 1 if self.team is self.getactivity().team_player else -1
    
    def _give_bomb(self):
        from bascenev1lib.actor.bomb import BombFactory
        # If we already have a held bomb, don't make another
        if self._held_bomb and self._held_bomb.exists():
            return

        # Create bomb nodes
        self._held_bomb = bs.newnode(
            'bomb',
            attrs={
                'mesh': bs.getmesh('bomb'),
                'shadow_size': 0.3,
                'color_texture': bs.gettexture('bombColor'),
                'reflection': 'soft',
                'reflection_scale': [0.3],
                'position': self.node.position,
                'owner': bs.existing(self.node),
                'materials': [BombFactory.get().bomb_material]
            },
        ) 
        self.node.hold_node = self._held_bomb
        bs.animate(self._held_bomb, 'fuse_length', {0.0: 1.0, self._attack_cooldown: 0.0})
      
        
        
    def receive_dmg(self, dmg: int, type: str = 'normal'):
        if not self.is_alive():
            return
        self.node.handlemessage('flash')
        self.hitpoints -= dmg * 10
        self.node.handlemessage('hurt_sound')
        self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )

        if self.hitpoints <= 0:
            self.handlemessage(bs.DieMessage())
    
    def handlemessage(self, msg):
        if isinstance(msg, bs.HitMessage):
            # Completely ignore hitmessages
            return
        elif isinstance(msg, bs.DieMessage):
            super().handlemessage(msg)
            if self._held_bomb:
                self._held_bomb.delete()

        else:
            return super().handlemessage(msg)




    
    def battler_tick(self):
        """Called every 0.1s to update AI."""
        if not self.is_alive():
            return
        close_to_enemy = False
        closest = None
        closest_ally = None
        now = bs.time()
        activity = self.getactivity()
        assert isinstance(activity, TheBattleSpazGame)
        if not activity:
            return

        # Detect enemies using actors instead of node visualizers
        for node in bs.getnodes():
            assert isinstance(node, bs.NodeVisualizer)
            actor = node.getdelegate(BattleSpaz)
            if not actor:
                continue
            if actor is self:
                continue
            if not actor.is_alive():
                continue
            if actor.team is self.team:
                continue

            try:
                sx, sy, sz = self.node.position
                ox, oy, oz = actor.node.position
                dx = sx - ox
                dz = sz - oz
                dist = (dx * dx + dz * dz) ** 0.5
            except Exception:
                continue

            if dist <= self.range:
                close_to_enemy = True
                closest = actor
                break
        
        for node in bs.getnodes():
            assert isinstance(node, bs.NodeVisualizer)
            actor = node.getdelegate(BattleSpaz)
            if not actor:
                continue
            if actor is self:
                continue
            if not actor.is_alive():
                continue
            if actor.team is not self.team:
                continue

            try:
                sx, sy, sz = self.node.position
                ox, oy, oz = actor.node.position
                dx = sx - ox
                dz = sz - oz
                dist = (dx * dx + dz * dz) ** 0.5
            except Exception:
                continue

            # Ignore bases
            if actor.battler == 'Base':
                continue

            if dist <= self.range:
                closest_ally = actor
                break
        
        
        if self.battler == 'Base':
            # Stand there and look pretty.
            self.on_hold_position_press()
            self.battler_move(1)

        elif self.battler == 'BattleSpaz':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    closest.receive_dmg(15)
                    self.on_punch_press()
                    self.on_punch_release()
                    self._last_attack_time = now
                self.on_hold_position_press()
                self.battler_move(1)
            else:
                # Move forward if no enemy nearby
                self.on_hold_position_release()
                self.battler_move(0.52)
        elif self.battler == 'Ranger':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    closest.receive_dmg(10)
                    self.on_punch_press()
                    self.on_punch_release()
                    self._last_attack_time = now
                self.on_hold_position_press()
                self.battler_move(1)
            else:
                # Move forward if no enemy nearby
                self.on_hold_position_release()
                self.battler_move(0.32)
        elif self.battler == 'WallBuilder':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    def trowler():
                        BattleSpaz(self.team, 'Wall', position=(
                            self.node.position[0] + 0.5 * self.get_team_direction(),
                            self.node.position[1],
                            self.node.position[2],
                        ))
                        


                    self.handlemessage(bs.CelebrateMessage(1.2))
                    bs.timer(1.2, trowler)
                    self._last_attack_time = now
                # Stop moving while in range
                self.on_hold_position_press()
                self.battler_move(1.0)
            else:
                # Move forward if no enemy nearby
                self.on_hold_position_release()
                self.battler_move(0.32)
        elif self.battler == 'Wall':
            # Stand there and look pretty.
            self.on_hold_position_press()
            self.battler_move(1)
        elif self.battler == 'Speedster':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    closest.receive_dmg(8)
                    self.on_punch_press()
                    self.on_punch_release()
                    self._last_attack_time = now
                # Stop moving while in range
                self.battler_move(1.0)
                self.on_hold_position_press()
            else:
                # Move forward if no enemy nearby
                self.on_hold_position_release()
                self.battler_move(0.8)
        elif self.battler == 'Healer':
            if close_to_enemy:
                if closest_ally is not None and now - self._last_attack_time >= self._attack_cooldown:
                    closest_ally.hitpoints = min(closest_ally.hitpoints + 200, closest_ally.hitpoints_max)
                    self.on_punch_press()
                    self.on_punch_release()
                    self._last_attack_time = now
                else:
                    self.battler_move(0.0)
            else:
                self.battler_move(0.43)
        elif self.battler == 'Titan':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    closest.receive_dmg(40)
                    self.on_punch_press()
                    self.on_punch_release()
                    self._last_attack_time = now
                self.battler_move(0.0)
            else:
                # Move forward slowly if no enemy nearby
                self.battler_move(0.3)

        elif self.battler == 'Bomber':
            # Always ensure bomber is holding a bomb
            

            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    self._give_bomb()
                   

                    

                    if self._held_bomb and self._held_bomb.exists():
                        if self._held_bomb.fuse_length == 0.0:
                            closest.receive_dmg(50)
                        
                            self._held_bomb.delete()
                            self._held_bomb = None

                            self._last_attack_time = now

                self.battler_move(0.0)
            else:
                if self._held_bomb:
                    # we dont need it right now
                    self._held_bomb.delete()
                self.battler_move(0.25)


        elif self.battler == 'Summoner':
            if close_to_enemy:
                if now - self._last_attack_time >= self._attack_cooldown:
                    self._last_attack_time = now
                    def summon_minion():
                        b=BattleSpaz(
                            self.team, 'BattleSpaz',
                            position=(
                                self.node.position[0] + 0.6 * self.get_team_direction(),
                                self.node.position[1],
                                self.node.position[2]
                            )
                        )
                        b.hitpoints_max = 500
                        b.hitpoints = b.hitpoints_max
                        b.node.name = 'Minion'
                    self.handlemessage(bs.CelebrateMessage(1.0))
                    bs.timer(1.0, summon_minion)
                    
                self.battler_move(0.0)
            else:
                self.battler_move(0.3)



                
                
        
                





# ba_meta export bascenev1.GameActivity
class TheBattleSpazGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'The Battle Spaz\'s'
    description = ''

    announce_player_deaths = False

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
        ]



        return settings



    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # (Pylint Bug?) pylint: disable=missing-function-docstring
        return []

    def __init__(self, settings: dict, twoplayer: bool = False):
        settings['map'] = 'Melee'
        super().__init__(settings)
        

        


        self.default_music = (
            bs.MusicType.BATTLEBRICKS
        )
        self.team_player = BattleTeam('player')
        self.team_enemy = BattleTeam('enemy')

        self.battlers = {
            'Battler': 'BattleSpaz',
            'WallBuilder': 'WallBuilder',
            'Ranger':  'Ranger',
            'Speedster': 'Speedster',
            'Healer': 'Healer',
            'Titan': 'Titan',
            'Bomber': 'Bomber',
            'Summoner': 'Summoner',
        }
        self._current_team = self.team_player
        self.battler_list = list(self.battlers.keys())
        self._battler_index = 0

       

        # Player 2 battler selection index
        self._p2_battler_index = 0

        self.non_collide_mat = bs.Material()
        self.non_collide_mat.add_actions(
            conditions=('they_have_material', self.non_collide_mat),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
                ('modify_part_collision', 'use_node_collide', False),
            ),
        )


        
    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    def spawn_battler(self, battlename: str, team: BattleTeam):
        # Retrieve battler class
        try:
            battler_name_instantace = self.battlers[battlename]
        except KeyError:
            print(f'Battler "{battlename}" does not exist')
            return

        # Decide spawn position
        if team is self.team_enemy:
            pos = (11, 0, 0)
        elif team is self.team_player:
            pos = (-11, 0, 0)
        else:
            raise ValueError(f'Unknown team: {team}')

        # Instantiate battler
        BattleSpaz(battler=battler_name_instantace, team=team, position=pos)

    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
 
    @override
    def on_begin(self) -> None:
        super().on_begin()
        # Player 2 VS mode toggle
        self.player_2 = self.session.game == 'Battle Spazes 2P'
        BattleSpaz(battler='Base', team=self.team_enemy, position=(11, 0, 0))
        BattleSpaz(battler='Base', team=self.team_player, position=(-11, 0, 0))

        # Controller help text (face buttons)
        yoffs = 120
        base_x = 0

       
        self._ui_text_spawn_player = bs.newnode(
            'text',
            attrs={
                'text': 'Pickup: Spawn',
                'position': (base_x + 0, -100 - yoffs),
                'scale': 1.0,
                'h_align': 'center',
                'v_align': 'bottom',
                'color': (0, 0.2, 1, 1),
                'shadow': 1.0,
                'flatness': 0.4,
            },
        )

        self._ui_text_spawn_player = bs.newnode(
            'text',
            attrs={
                'text': 'Bomb: Swap Index Right',
                'position': (base_x + 140, -140 - yoffs),
                'scale': 1.0,
                'h_align': 'center',
                'v_align': 'bottom',
                'color': (1, 0.3, 0.3, 1),
                'shadow': 1.0,
                'flatness': 0.4,
            },
        )

        self._ui_text_spawn_enemy = bs.newnode(
            'text',
            attrs={
                'text': 'Punch: Swap Index Left',
                'position': (base_x - 140, -140 - yoffs),
                'scale': 1.0,
                'h_align': 'center',
                'v_align': 'bottom',
                'color': (0.3, 1, 0.3, 1),
                'shadow': 1.0,
                'flatness': 0.4,
            },
        )
        if not self.player_2:

            self._ui_text_swap_team = bs.newnode(
                'text',
                attrs={
                    'text': 'Jump: Swap Team',
                    'position': (base_x + 0, -180 - yoffs),
                    'scale': 1.0,
                    'h_align': 'center',
                    'v_align': 'bottom',
                    'color': (0.8, 0.8, 1, 1),
                    'shadow': 1.0,
                    'flatness': 0.4,
                },
            )
        # Player 1 UI positioning logic
        if self.player_2:
            base_x = -200
        else:
            base_x = 0


        self._ui_selected_battler = bs.newnode(
            'text',
            attrs={
                'text': f'Selected: {self.battler_list[self._battler_index]}' if not self.player_2 else f'({self.players[0].getname()})\nSelected: {self.battler_list[self._battler_index]}',
                'position': (base_x + 0, -60 - yoffs),
                'scale': 1.2,
                'h_align': 'center',
                'v_align': 'bottom',
                'color': (0, 1, 1, 1),
                'shadow': 1.0,
                'flatness': 0.4,
            },
        )
        
        # Player 2 UI (only shows if player_2 mode is enabled)
        p2_x = 200 if self.player_2 else 0
        try:
            self._ui_selected_battler_p2 = bs.newnode(
                'text',
                attrs={
                    'text': f'({self.players[1].getname()})\nSelected: {self.battler_list[self._p2_battler_index]}',
                    'position': (p2_x, -60 - yoffs),
                    'scale': 1.2,
                    'h_align': 'center',
                    'v_align': 'bottom',
                    'color': (1, 0.4, 0.4, 1),
                    'shadow': 1.0,
                    'flatness': 0.4,
                },
            )
        except:
            self._ui_selected_battler_p2 =bs.newnode(
                'text',
                attrs={
                    'text': f'{self.battler_list[self._p2_battler_index]}',
                    'position': (p2_x, -60 - yoffs),
                    'scale': 1.2,
                    'h_align': 'center',
                    'v_align': 'bottom',
                    'color': (1, 0.4, 0.4, 1),
                    'shadow': 1.0,
                    'flatness': 0.4,
                },
            )
        self._ui_selected_battler_p2.opacity = 0.0
        player = self.players[0]

        try:
                player2 = self.players[1]
        except:
                player2 = False
        

        if player2 and self.player_2:

            # Lock P2 to enemy team
            self._p2_current_team = self.team_enemy

            # Make P2 UI visible
            if self._ui_selected_battler_p2.exists():
                self._ui_selected_battler_p2.opacity = 1.0

            # Controls for P2
            player2.sessionplayer.assigninput(
                bs.InputType.PUNCH_PRESS,
                self._next_battler_p2
            )
            player2.sessionplayer.assigninput(
                bs.InputType.BOMB_PRESS,
                self._prev_battler_p2
            )
            player2.sessionplayer.assigninput(
                bs.InputType.PICK_UP_PRESS,
                lambda: self.spawn_battler(
                    self.battler_list[self._p2_battler_index],
                    self.team_enemy
                )
            )

         



        # --- PLAYER 1 LOGIC ---
        # Scroll forward through battlers with PUNCH
        player.sessionplayer.assigninput(
            bs.InputType.PUNCH_PRESS,
            self._next_battler
        )

        # Scroll backward through battlers with BOMB
        player.sessionplayer.assigninput(
            bs.InputType.BOMB_PRESS,
            self._prev_battler
        )

        # Spawn currently selected battler with PICKUP
        player.sessionplayer.assigninput(
            bs.InputType.PICK_UP_PRESS,
            lambda: self.spawn_battler(
                self.battler_list[self._battler_index],
                self._current_team
            )
        )

        # Swap team with JUMP
        if not self.player_2:
            player.sessionplayer.assigninput(
                bs.InputType.JUMP_PRESS,
                self._swap_team
            )



    def _swap_team(self):
        if self._current_team is self.team_player:
            self._current_team = self.team_enemy
            color = (0.3, 1, 1, 1) if self._current_team is self.team_player else (1, 0.3, 0.3, 1)
            self._ui_selected_battler.color = color
        else:
            self._current_team = self.team_player
            color = (0.3, 1, 1, 1) if self._current_team is self.team_player else (1, 0.3, 0.3, 1)
            self._ui_selected_battler.color = color

    def _next_battler(self):
        self._battler_index = (self._battler_index + 1) % len(self.battler_list)
        name = self.battler_list[self._battler_index]
        self._ui_selected_battler.text = f'Selected: {name}' if not self.player_2 else f'{self.players[0].getname()}\nSelected: {name}' 

    def _prev_battler(self):
        self._battler_index = (self._battler_index - 1) % len(self.battler_list)
        name = self.battler_list[self._battler_index]
        self._ui_selected_battler.text = f'Selected: {name}' if not self.player_2 else f'{self.players[0].getname()}\nSelected: {name}' 

    @override
    def spawn_player(self, player: bs.Player):

    
        return



    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        
        return super().handlemessage(msg)
        return None

    @override
    def end_game(self) -> None:
        from gummyoverhaul._singleplayergame import SinglePlayerSession  
        assert isinstance(self.session, SinglePlayerSession)
        self.session.return_to_main_menu()

    def _next_battler_p2(self):
        self._p2_battler_index = (self._p2_battler_index + 1) % len(self.battler_list)
        if self._ui_selected_battler_p2.exists():
            self._ui_selected_battler_p2.text = (
                f'({self.players[1].getname()}\nSelected: {self.battler_list[self._p2_battler_index]}'
            )

    def _prev_battler_p2(self):
        self._p2_battler_index = (self._p2_battler_index - 1) % len(self.battler_list)
        if self._ui_selected_battler_p2.exists():
            self._ui_selected_battler_p2.text = (
                f'({self.players[1].getname()})\nSelected: {self.battler_list[self._p2_battler_index]}'
            )