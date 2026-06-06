from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
import random
from collections import deque
from bascenev1lib.maps import PacManMap

if TYPE_CHECKING:
    from typing import Any, Sequence

class GhostSpaz(Spaz):
    def __init__(self, pos, type: str):
        if type == 'Red':
            character = 'Kronk'
            color = (1, 0, 0)
            highlight = (0.5, 0, 0)
            cosmetic = None
        elif type == 'Pink':
            character = 'Zoe'
            color = (1, 0.75, 0.8)
            highlight = (0.75, 0.5, 0.55)
            cosmetic = None
        elif type == 'Blue':
            character = 'Spaz'
            color = (0, 0.8, 1)
            highlight = (0, 0, 0.5)
            cosmetic = None
        elif type == 'Orange':
            character = 'Mel'
            color = (1, 0.5, 0)
            highlight = (0.5, 0.25, 0)
            cosmetic = None
        else:
            character = 'Spaz'
            color = (1, 1, 1)
            highlight = (0.5, 0.5, 0.5)
            cosmetic = None

        super().__init__(color, highlight, character, None, False, False, False, True, cosmetic)

        self.handlemessage(bs.StandMessage((pos[0], pos[1]-0.7, pos[2])))
        self.type = type
        self.target_position = (0, 0, 0)
        self.next_tile = None
        self.path = deque()
        self.ai_active = False
        self.escaped_house = False
        self.last_tile = None
        self.last_dir = (0, 0)
        self.target_shield: bs.NodeVisualizer = bs.Node(None)
        self.eaten = False
        self.scared = False
        self.impact_scale = 0.0
        self.award_xp = False
        # Store original meshes for restoration after being eaten
        self.meshes_backup = {
            'head': self.node.head_mesh,
            'torso': self.node.torso_mesh,
            'toes': self.node.toes_mesh,
            'hand': self.node.hand_mesh,
            'pelvis': self.node.pelvis_mesh,
            'forearm': self.node.forearm_mesh,
            'lower_leg': self.node.lower_leg_mesh,
            'upper_arm': self.node.upper_arm_mesh,
            'upper_leg': self.node.upper_leg_mesh
        }
        # Anti-softlock tracking
        self._last_stuck_pos = pos
        self._stuck_time = 0.0
        self._eaten_time = 0.0
        self.return_sound_node = bs.newnode(
            'sound',
            attrs={
                'sound': bs.getsound('return_to_home'),  
                'volume': 0.0,
            }
        )
        
    def update_ai(self):
        if not self.node.exists():
            return
        
        if not self.ai_active:
            self.node.hold_position_pressed = True
            self.node.move_left_right = 0
            self.node.move_up_down = -1
            return
        else:
            self.node.hold_position_pressed = False

        map = self.getactivity().map
        assert isinstance(map, PacManMap)

        # Track eaten time for anti-softlock
        if self.eaten:
            self._eaten_time += 0.2
        else:
            self._eaten_time = 0.0

        # Convert world position to grid
        current_tile = map.world_to_tile(self.node.position)

        if self.eaten:
            target_tile = map.world_to_tile(map.ghost_house_position)
        elif not self.escaped_house:
            target_tile = map.world_to_tile((4.48, 0.7, 3.82))
        else:
            target_tile = map.world_to_tile(self.target_position)
       

        # Restore meshes if ghost is eaten and has reached the ghost house
        if current_tile in map.ghost_house_tiles and self.eaten:
            # Restore all meshes
            self.node.head_mesh = self.meshes_backup['head']
            self.node.torso_mesh = self.meshes_backup['torso']
            self.node.toes_mesh = self.meshes_backup['toes']
            self.node.hand_mesh = self.meshes_backup['hand']
            self.node.pelvis_mesh = self.meshes_backup['pelvis']
            self.node.forearm_mesh = self.meshes_backup['forearm']
            self.node.lower_leg_mesh = self.meshes_backup['lower_leg']
            self.node.upper_arm_mesh = self.meshes_backup['upper_arm']
            self.node.upper_leg_mesh = self.meshes_backup['upper_leg']

            self.scared = False
            self.eaten = False
            self.node.hockey = False
            self.escaped_house = False
            self.last_dir = (0, 0)
            self.node.color = self.Dcolor
            self.return_sound_node.volume = 0.0

        # checking the target r sosmething
        if False and self.node.exists():
            
            if not self.target_shield:
                self.target_shield = bs.newnode(
                    'shield',
                    attrs={
                    'radius': 1.0,
                    'position': (
                        self.target_position[0],
                        self.target_position[1]+1,
                        self.target_position[2]
                    ),
                    'color': (self.node.color[0]*5, self.node.color[1]*5, self.node.color[2]*5),
                    }
                )
            else:
                self.target_shield.position = (
                    self.target_position[0],
                     self.target_position[1]+1,
                      self.target_position[2]
                )
        


        hallway_teleports = {
            (-2.3, 0.7, 5.4): (9, 0.7, 5.4),
            (10, 0.7, 5.4): (-1.3, 0.7, 5.4)
        }

        # Check if ghost is at any teleport position
        for src, dest in hallway_teleports.items():
            node_pos = (self.node.position[0], self.node.position[1], self.node.position[2])
            if (abs(node_pos[0] - src[0]) < 0.2 * (1.39 if self.eaten else 1.0) and
                abs(node_pos[1] - src[1]) < 0.2 * (1.33 if self.eaten else 1.0) and
                abs(node_pos[2] - src[2]) < 0.2 * (1.39 if self.eaten else 1.0)):
                self.node.handlemessage(bs.StandMessage((dest[0], dest[1]-0.8, dest[2])))
                break

        ghost_house_tiles = map.ghost_house_tiles

        if not self.escaped_house and current_tile not in ghost_house_tiles:
            self.escaped_house = True

        # Determine walkable neighbors
        neighbors = [
            (current_tile[0] + 1, current_tile[1]),
            (current_tile[0] - 1, current_tile[1]),
            (current_tile[0], current_tile[1] + 1),
            (current_tile[0], current_tile[1] - 1),
        ]

        # Walkable check
        def walkable(tile):
            # Always block normal walls
            if tile in map.wall_tiles:
                return False
            # If ghost is eaten, ignore only ghost house tiles
            if self.eaten and tile in map.ghost_house_tiles:
                return True
            else:
                if tile in map.wall_tiles:
                    return False

            # Normal escaped ghosts should treat ghost house as wall
            if not self.eaten and self.escaped_house and tile in map.ghost_house_tiles:
                return False
            return True

        # Filter neighbors: walkable and never reverse
        reverse_tile = (current_tile[0] - self.last_dir[0], current_tile[1] - self.last_dir[1]) if self.last_dir else None

        # Primary filter: avoid reverse + avoid last tile to stop back-forth oscillation
        walk_choices = [
            t for t in neighbors
            if walkable(t)
            and t != reverse_tile
            and t != self.last_tile
        ]

        # If everything got filtered out, allow going to last_tile as last resort
        if not walk_choices:
            walk_choices = [
                t for t in neighbors
                if walkable(t) and t != reverse_tile
            ]

        # If still inside ghost house and no walkable tiles, allow moving forward into exit
        if not self.escaped_house and not walk_choices:
            walk_choices = [t for t in neighbors if t not in map.wall_tiles]

        # Pick the neighbor: prefer tile closest to target but never reverse
        if walk_choices:
            # Only allow forward or sideways moves; do not reverse
            forward_tile = (current_tile[0] + self.last_dir[0], current_tile[1] + self.last_dir[1]) if self.last_dir else None
            forward_choices = [t for t in walk_choices if t == forward_tile or t != forward_tile]
            next_tile = min(forward_choices, key=lambda t: abs(t[0] - target_tile[0]) + abs(t[1] - target_tile[1]))
        else:
            next_tile = current_tile  # stuck

        # Update last_dir and last_tile if moved
        if next_tile != current_tile:
            self.last_dir = (next_tile[0] - current_tile[0], next_tile[1] - current_tile[1])
            self.last_tile = current_tile

        # Move toward next tile in world space
        pos = map.walk_world_positions.get(next_tile, self.node.position)
        dx = pos[0] - self.node.position[0]
        dz = pos[2] - self.node.position[2]
        dist = (dx*dx + dz*dz)**0.5
        speed = 0.5 if self.scared else 0.86 if self.eaten else 0.68 
        if dist != 0:
            self.node.move_left_right = dx / dist * speed
            self.node.move_up_down = -dz / dist * speed
        else:
            self.node.move_left_right = 0
            self.node.move_up_down = 0

        # ---------------- Anti-Softlock ----------------
        try:
            ghost_house_pos = map.ghost_house_position
        except Exception:
            ghost_house_pos = (0, 1, 0)

        # Track movement
        cur = self.node.position
        dxs = cur[0] - self._last_stuck_pos[0]
        dzs = cur[2] - self._last_stuck_pos[2]
        moved = (dxs*dxs + dzs*dzs)**0.5

        if moved < 0.05:
            self._stuck_time += 0.2
        else:
            self._stuck_time = 0.0
            self._last_stuck_pos = cur

        # If ghost is stuck too long OR eaten too long, teleport to house
        if self._stuck_time > 3.0 or (self.eaten and self._eaten_time > 10.0):
            self.node.handlemessage(bs.StandMessage((ghost_house_pos[0], ghost_house_pos[1]-0.8, ghost_house_pos[2])))
            self._stuck_time = 0.0
            self._eaten_time = 0.0
            self.escaped_house = False

# ba_meta export bascenev1.GameActivity
class PacManGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'Pac-Man'
    description = ''

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

    def __init__(self, settings: dict):
        settings['map'] = 'pacuy'
        super().__init__(settings)
        self.player_spaz: Spaz | None = None
        self.game_over = False
        
 
        


        self.default_music = (
           None

        )
        self.blue_ghost = False
        self.ghosts: list[GhostSpaz] = []
        

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


    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
 
    @override
    def on_begin(self) -> None:
        super().on_begin()
        bs.getsound('introPackman').play()

        bgnode = bs.newnode('image', attrs={
            'texture': bs.gettexture('black'),
            'opacity': 1.0,
            'position': (0, 0),
            'scale': (1920, 1080),
            'fill_screen': True
        })
        textnode = bs.newnode('text', attrs={
            'text': f'{self.players[0].getname().upper()} START!',
            'scale': 1.5,
            'color': (1, 1, 0),
            'h_align': 'center',
            'v_align': 'center',
            'shadow': 1.0,
            'position': (0, 0),
        })

        def remove_intro():
            textnode.delete()
            bgnode.delete()
            if self.player_spaz:
                self.player_spaz.disconnect_controls_from_player()
                def left_right(value):
                    if value == 0:
                        return
                    if value > 0:
                        self.player_spaz.on_move_up_down(0)
                        self.player_spaz.on_move_left_right(0.90)
                    else:
                        self.player_spaz.on_move_up_down(0)
                        self.player_spaz.on_move_left_right(-0.90)
                    
                def up_down(value):
                    if value == 0:
                        return
                    if value > 0:
                        self.player_spaz.on_move_left_right(0)
                        self.player_spaz.on_move_up_down(0.90)
                    else:
                        self.player_spaz.on_move_left_right(0)
                        self.player_spaz.on_move_up_down(-0.90)
                    
                
                bs.timer(0.1, self._check_collision, repeat=True)

                self.player_spaz.source_player.assigninput(
                    bs.InputType.LEFT_RIGHT, left_right
                )
                self.player_spaz.source_player.assigninput(
                    bs.InputType.UP_DOWN, up_down
                )

            ghost_house_pos = self.map.ghost_house_position
    
            offsets = {
                'Blue': (ghost_house_pos[0] - 1.0, ghost_house_pos[1], ghost_house_pos[2]),
                'Pink': (ghost_house_pos[0] + 1.0, ghost_house_pos[1], ghost_house_pos[2]),
                'Red': (ghost_house_pos[0], ghost_house_pos[1], ghost_house_pos[2] - 1.5),
                'Orange': (ghost_house_pos[0], ghost_house_pos[1], ghost_house_pos[2] + -.5),
            }

            for ghost_type, pos in offsets.items():
                self.spawn_ghost(pos, ghost_type)
         
            bs.timer(0.35, self._update_ghost_ai, repeat=True)
            bs.timer(0.38, lambda: bs.getsound('ghostMove').play(0.5), repeat=True)

        bs.timer(3.6, remove_intro)

    def _check_collision(self) -> None:
        if not self.player_spaz:
            return
        if not self.map.pellets and not self.game_over:
            self._win_game()
            return
        pos = self.player_spaz.node.position
        pellets_to_remove = []
        for pellet_pos, pellet_node in self.map.pellets.items():
            pellet_world_pos = pellet_node.position
            dx = pos[0] - pellet_world_pos[0]
            dy = pos[1] - pellet_world_pos[1]
            dz = pos[2] - pellet_world_pos[2]
            distance = (dx*dx + dy*dy + dz*dz)**0.5
            if distance <= 0.44:
                pellet_node.delete()
                bs.getsound('chomp').play(0.6)
                pellets_to_remove.append(pellet_pos)
                if pellet_pos in self.map.power_pellets:
                    self._enter_power_mode()
                    self.map.power_pellets.remove(pellet_pos)
        for pellet_pos in pellets_to_remove:
            self.map.pellets.pop(pellet_pos, None)
        
        hallway_teleports = {
            (-2.3, 0.7, 5.4): (9, 0.7, 5.4),
            (10, 0.7, 5.4): (-1.3, 0.7, 5.4)
        }

        for src, dest in hallway_teleports.items():
            node_pos = pos
            # simple distance check
            if (abs(node_pos[0] - src[0]) < 0.1 and
                abs(node_pos[1] - src[1]) < 0.1 and
                abs(node_pos[2] - src[2]) < 0.1):
                self.player_spaz.node.handlemessage(bs.StandMessage((dest[0], dest[1]-0.8, dest[2])))
                break
        


    def _enter_power_mode(self) -> None:
        bs.setmusic(bs.MusicType.GHOST_BLUE)
        self.blue_ghost = True
        self.ghost_blue_timer = None
        self.ghost_blue_timer = bs.Timer(10, self.un_power)
        
        for ghost in self.ghosts:
            ghost.scared = True
            ghost.handlemessage(bs.CelebrateMessage(10))
            ghost.node.color = (0, 0, 3)
            ghost.node.move_left_right = -ghost.node.move_left_right
            ghost.node.move_up_down = -ghost.node.move_up_down
            

    
    def un_power(self):
        self.blue_ghost=False
        bs.setmusic(None)
        for ghost in self.ghosts:
            ghost.scared = False
            ghost.node.color = ghost.Dcolor

    def spawn_ghost(self, position, type: str):
        ghost = GhostSpaz(position, type)
        ghost.node.materials += (self.map.ghost_material, self.non_collide_mat,)
        ghost.node.roller_materials += (self.map.ghost_material, self.non_collide_mat,)
        ghost.node.extras_material  += (self.map.ghost_material, self.non_collide_mat,)
        delays = {
            'Red': 0.5,    
            'Pink': 5.5,
            'Blue': 14.0,
            'Orange': 20.5   
        }

        delay = delays[type]
        bs.timer(delay, lambda: setattr(ghost, 'ai_active', True))
        self.ghosts.append(ghost)

    def _update_ghost_ai(self) -> None:
        if not self.player_spaz:
            return
        player_pos = self.player_spaz.node.position

        for ghost in self.ghosts:
            if ghost.eaten:
                ghost.target_position = self.map.ghost_house_position
            elif ghost.scared:
                # go random stuf
                ghost.target_position = (random.uniform(10, -6), 1, random.uniform(10, -6))
            else:
                
            
                if ghost.type == 'Red':
                    # Blinky: directly chases the player
                    ghost.target_position = self.player_spaz.node.position
                elif ghost.type == 'Pink':
                    # Pinky: targets a few tiles ahead of the player's current direction
                    dir_x, dir_y = self.player_spaz.node.move_left_right, -self.player_spaz.node.move_up_down
                    ghost.target_position = (
                        self.player_spaz.node.position[0] + dir_x * 4,
                        self.player_spaz.node.position[1],
                        self.player_spaz.node.position[2] + dir_y * 4
                    )
                elif ghost.type == 'Blue':
                    # Inky: weird combinatino

                    player_pos = self.player_spaz.node.position
                    dir_x = self.player_spaz.node.move_left_right
                    dir_z = -self.player_spaz.node.move_up_down
                    two_tiles_ahead = (
                        player_pos[0] + dir_x * 2,
                        player_pos[1],
                        player_pos[2] + dir_z * 2
                    )
                    blinky = next((g for g in self.ghosts if g.type == 'Red'), None)
                    vec_x = (two_tiles_ahead[0] - blinky.node.position[0])*1.2
                    vec_z = (two_tiles_ahead[2] - blinky.node.position[2])*1.2

                    ghost.target_position = (
                        vec_x,
                        player_pos[1],
                        vec_z
                    )

                    
                elif ghost.type == 'Orange':
                    # Clyde: if far, chase player; if near, go to corner
                    ghost_pos = ghost.node.position
                    px, py, pz = self.player_spaz.node.position
                    dx, dz = px - ghost_pos[0], pz - ghost_pos[2]
                    dist = (dx*dx + dz*dz)**0.5

                    chase_distance = 6

                    corner_pos = (-2, 0.7, -2) 
                    if dist > chase_distance:
                        # Far: chase the player
                        ghost.target_position = self.player_spaz.node.position
                    else:
                        # Near: retreat to corner
                        ghost.target_position = corner_pos
            ghost.update_ai()

            for ghost in self.ghosts:
                ghost_pos = ghost.node.position
                dx = player_pos[0] - ghost_pos[0]
                dz = player_pos[2] - ghost_pos[2]
                dist = (dx*dx + dz*dz)**0.5
                if dist <= 0.6 and not self.game_over:
                    if ghost.scared and not ghost.eaten:
                        bs.getsound('ghostEaten').play()
                        ghost.escaped_house = False
                        ghost.eaten = True
                        self.player_spaz.on_punch_press()
                        self.player_spaz.on_punch_release()

                        ghost.last_dir = (0, 0)
                        ghost.node.head_mesh = None
                        ghost.node.torso_mesh = None
                        ghost.node.toes_mesh = None
                        ghost.node.hand_mesh = None
                        ghost.node.hockey = True
                        ghost.node.pelvis_mesh = None
                        ghost.node.forearm_mesh = None
                        ghost.node.lower_leg_mesh = None
                        ghost.node.upper_arm_mesh = None
                        ghost.node.upper_leg_mesh = None
                        ghost.return_sound_node.volume = 1.0
                    else:
                        if not ghost.eaten:
                            ghost.on_punch_press()
                            ghost.on_punch_release()
                            self._kill_player()
                    break

    def _kill_player(self):
        if self.game_over:
            return
        if self.player_spaz:
            self.game_over = True
            bs.getsound('pacmanDie').play()
            
            self.player_spaz.node.handlemessage(bs.DieMessage())
            bs.timer(3.5, self.end_game) 
    
    def _win_game(self):
        if self.game_over:
            return
        self.game_over = True
        bs.cameraflash()
        for ghost in self.ghosts:
            ghost.node.is_area_of_interest = False
        self.player_spaz.on_hold_position_press()
        self.player_spaz.on_move_up_down(-1)
        self.player_spaz.on_hold_position_press()
        self.player_spaz.handlemessage(bs.CelebrateMessage(999))
        bs.getsound('score').play()
        bs.timer(4.5, self.end_game)

    @override
    def spawn_player(self, player: bs.Player):
        spaz = self.spawn_player_spaz(player, position=self.map.start_position)
        spaz.connect_controls_to_player(enable_punch=False,
                                        enable_bomb=False,
                                        enable_pickup=False,
                                        enable_jump=False,
                                        enable_run=False)
       



        spaz.impact_scale = 0.0
        self.player_spaz = spaz
        spaz.node.materials += (self.non_collide_mat,)
        spaz.node.roller_materials += (self.non_collide_mat,)
        spaz.node.extras_material  += (self.non_collide_mat,)
        spaz.award_xp = False


    
        return spaz



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
