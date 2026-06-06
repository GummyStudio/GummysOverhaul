# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)
 # bs.getactivity().create_ai(3)

from __future__ import annotations

from typing import TYPE_CHECKING, override

import math
from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
import random

if TYPE_CHECKING:
    from typing import Any, Sequence
    
class TetrisPlayer(bs.Player):
    def __init__(self):
        self.board: TetrisBoard = None



           
#import bascenev1 as bs; bs.getplayers()[0].board.queue_garbage(5)
class TetrisBoard(bs.Actor):
    def __init__(self, player: TetrisPlayer, width: 10, height: 20):
        
        super().__init__()
        self.bag: list[tuple[list[list[int]], tuple[float,float,float]]] = []
        self.refill_bag: list[tuple[list[list[int]], tuple[float,float,float]]] = []
        self.next_piece = None
        self.next_color = None
        self.garbage_entry_mode = 'instant' # instant / continuous
        self.garbage_entry_wait_time = 0.1


        # This makes the board have a simplistic view (for non players, and to make it very optimized)
        self.simple = False

        self.player = player
        self.render = True
        self.existing = True
        # grid
        self.width = width
        self.height = height

        # Load textures
        self.grid_texure = bs.gettexture('tetrigrid')
        self.block_texture = bs.gettexture('tetriblock')
        # And load sound efcts
        self.sfx_folder = 'tetris/'
        self.sfx = {
            'move': bs.getsound(self.sfx_folder + 'Move'),
            'hold': bs.getsound(self.sfx_folder + 'Hold'),
            'rotate': bs.getsound(self.sfx_folder + 'Rotate'),
            'hard_drop': bs.getsound(self.sfx_folder + 'HardDrop'),
            'clear': bs.getsound(self.sfx_folder + 'ClearLine'),
            'quad_clear': bs.getsound(self.sfx_folder + 'Tetris'),
            'tspin_clear': bs.getsound(self.sfx_folder + 'SpinClear'),
            'boardfillS': bs.getsound(self.sfx_folder + 'garbageRecieveS'),
            'boardfillM':   bs.getsound(self.sfx_folder + 'garbageRecieveM'),
            'boardfillL':   bs.getsound(self.sfx_folder + 'garbageRecieveL'),
            'boardfillL':   bs.getsound(self.sfx_folder + 'garbageRecieveL'),
            'garbageReadyS': bs.getsound('boardfillS'),
            'garbageReadyM':  bs.getsound('boardfillM'),
            'garbageReadyL':  bs.getsound('boardfillL'),
            'boardHurt':  bs.getsound(self.sfx_folder + 'damageSmall'),
            'boardHurtL':  bs.getsound(self.sfx_folder + 'damageLarge'),
            'spikeS': bs.getsound('spikeS'),
            'spikeM': bs.getsound('spikeM'),
            'spikeL': bs.getsound('spikeL'),
            'board_clear': bs.getsound('boardClear'),
            'die': bs.getsound(self.sfx_folder + 'die'),
            'SIMPLEdie':  bs.getsound(self.sfx_folder + 'SIMPLEKo'),
            'KO': bs.getsound(self.sfx_folder + 'KO'),
        }

        self.targets: list[TetrisBoard] = []
        

        # Dynamic updating
        self.active = True
        self.position = (0, 0)
        self.scale = 1

        # i have to optimize ts
        self._grid_nodes = []
        self._block_nodes = []
        self._ghost_nodes = []
        self._hold_nodes = []
        self._next_nodes = []
        self._label_nodes = []
        self._garbage_nodes = []
    
        self.position_offset = (-150,250)
        self.score = 0
        
        self.grid = [[0]*width for _ in range(height)]
        self.nodes: list[bs.NodeVisualizer] = []
        self.seperate_nodes: list[bs.NodeVisualizer] = []

        self.active_piece = None
        self.active_piece_type = None
        self.active_color = None
        self.player_last_hit_by: TetrisPlayer = None
        self.piece_x = 4
        self.piece_y = 0
        self.combo = -1

        self.hold_piece: list[list[int]] = None
        self.hold_color: tuple[float,float,float] = None
        self.hold_locked: bool = False 

    
        
        

        # I geniunely hate google
        self.TETRIS_PIECES = [
            ([[1,1,1,1]], (0,1,1)),      # I
            ([[1,1],[1,1]], (1,1,0)),    # O
            ([[0,1,0],[1,1,1]], (0.7,0,1)), # T
            ([[1,0,0],[1,1,1]], (0,0.3,1)), # J
            ([[0,0,1],[1,1,1]], (1,0.5,0)), # L
            ([[0,1,1],[1,1,0]], (0,1,0)), # S
            ([[1,1,0],[0,1,1]], (1,0,0)), # Z
        ]
        
        self.PIECE_ROTATIONS = {
            'I': [
                [
                    [0,0,0,0],
                    [1,1,1,1],
                    [0,0,0,0],
                    [0,0,0,0]
                ],
                [
                    [0,0,1,0],
                    [0,0,1,0],
                    [0,0,1,0],
                    [0,0,1,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [1,1,1,1],
                    [0,0,0,0]
                ],
                [
                    [0,1,0,0],
                    [0,1,0,0],
                    [0,1,0,0],
                    [0,1,0,0]
                ],
            ],
            'O': [
                [
                    [0,1,1,0],
                    [0,1,1,0],
                    [0,0,0,0],
                    [0,0,0,0]
                ]
            ]*4,
            'T': [
                [
                    [0,0,0,0],
                    [0,1,0,0],
                    [1,1,1,0],
                    [0,0,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,1,0,0],
                    [0,1,1,0],
                    [0,1,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [1,1,1,0],
                    [0,1,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,1,0,0],
                    [1,1,0,0],
                    [0,1,0,0]
                ]
            ],
            'L': [
                [
                    [0,0,0,0],
                    [0,0,0,1],
                    [0,1,1,1],
                    [0,0,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,1,0],
                    [0,0,1,0],
                    [0,0,1,1]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,1,1,1],
                    [0,1,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,1,1,0],
                    [0,0,1,0],
                    [0,0,1,0]
                ]
            ],
            'J': [
                [
                    [0,0,0,0],
                    [0,1,0,0],
                    [0,1,1,1],
                    [0,0,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,1,1],
                    [0,0,1,0],
                    [0,0,1,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,1,1,1],
                    [0,0,0,1]
                ],
                [
                    [0,0,0,0],
                    [0,0,1,0],
                    [0,0,1,0],
                    [0,1,1,0]
                ]
            ],
            'S': [
                [
                    [0,0,0,0],
                    [0,0,1,1],
                    [0,1,1,0],
                    [0,0,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,1,0],
                    [0,0,1,1],
                    [0,0,0,1]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,0,1,1],
                    [0,1,1,0]
                ],
                [
                    [0,0,0,0],
                    [0,1,0,0],
                    [0,1,1,0],
                    [0,0,1,0]
                ]
            ],
            'Z': [
                [
                    [0,0,0,0],
                    [0,1,1,0],
                    [0,0,1,1],
                    [0,0,0,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,1],
                    [0,0,1,1],
                    [0,0,1,0]
                ],
                [
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,1,1,0],
                    [0,0,1,1]
                ],
                [
                    [0,0,0,0],
                    [0,0,1,0],
                    [0,1,1,0],
                    [0,1,0,0]
                ]
            ],
            
        }
        self.WALL_KICKS = {
            'I': {
                (0, 1): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
                (1, 0): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
                (1, 2): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
                (2, 1): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
                (2, 3): [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
                (3, 2): [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
                (3, 0): [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
                (0, 3): [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
            },
            'JLSTZ': {
                (0, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
                (1, 0): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
                (1, 2): [(0,0), (1,0), (1,-1), (0,2), (1,2)],
                (2, 1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
                (2, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
                (3, 2): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
                (3, 0): [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],
                (0, 3): [(0,0), (1,0), (1,1), (0,-2), (1,-2)],
            }
        }

      

        self.rotation_state = 0  
        self.nodes_exist = False      
        self._init_persistent_nodes()

        bs.timer(0.1, self.draw, repeat=True)
        # Changing this later

        self.garbage_queue: list[dict] = []
        self.garbage_delay = 2.0 
        self.garbage_hole = random.randint(0, self.width - 1)

        self.gravity_timer = bs.Timer(0.7, self.gravity, repeat=True)
        bs.timer(1, self.update_garbage_timers, repeat=True)
        
        self.spawn_piece()
       
        self.soft_drop_speed = 1

        # Wow! I hate bombsquad input
        self._analog_left_right = 0.0
        self._analog_up_down = 0.0
        self._analog_left_right_accum = 0.0
        self._analog_up_down_accum = 0.0

        self.lock_counter = 0
        self.lock_delay_frames = 30

        self.horizontal_speed = 0.14
        self.soft_drop_speed = 0.16

        
        if self.player.exists():

            # Okay were rendering, let them control the board
            player.assigninput(bs.InputType.LEFT_RIGHT, self._on_left_right_axis)
            player.assigninput(bs.InputType.UP_DOWN, self._on_up_down_axis)
            player.assigninput(bs.InputType.LEFT_PRESS, self._tap_left)
            player.assigninput(bs.InputType.RIGHT_PRESS, self._tap_right)

            player.assigninput(
                bs.InputType.PICK_UP_PRESS, self.hold
            )
            player.assigninput(
                bs.InputType.PUNCH_PRESS, self.hard
            )
            player.assigninput(
                bs.InputType.JUMP_PRESS, self.ccw
            )
            player.assigninput(
                bs.InputType.BOMB_PRESS, self.cw
            )
            player.assigninput(
                bs.InputType.UP_PRESS, self.spin_180
            )

            bs.timer(1/60, self.update_input, repeat=True)
            self.change_targets()
            bs.timer(5, self.change_targets, repeat=True)
    
    # --
    # controls
    # --

    def _on_left_right_axis(self, value):
        self._analog_left_right = float(value)

    def _on_up_down_axis(self, value):
        self._analog_up_down = -float(value)
    def _tap_left(self):
        if not self.check_collision(self.piece_x - 1, self.piece_y):
            self.piece_x -= 1
            self.lock_counter = 0
            self._analog_left_right_accum = 0
            self.play_sfx("move")


    def _tap_right(self):
        if not self.check_collision(self.piece_x + 1, self.piece_y):
            self.piece_x += 1
            self.lock_counter = 0
            self._analog_left_right_accum = 0
            self.play_sfx("move")
        

    def update_input(self):
        
        self._analog_left_right_accum += self._analog_left_right * self.horizontal_speed
 
        while abs(self._analog_left_right_accum) >= 1.0:
            step = int(math.copysign(1, self._analog_left_right_accum))
            if not self.check_collision(self.piece_x + step, self.piece_y):
                self.piece_x += step
                self.play_sfx("move")




                self.lock_counter = 0
            self._analog_left_right_accum -= step
            break

        self._analog_up_down_accum += max(0.0, self._analog_up_down) * self.soft_drop_speed
        while self._analog_up_down_accum >= 1.0:
            if not self.check_collision(self.piece_x, self.piece_y + 1):
                self.piece_y += 1
                self.lock_counter = 0
            else:
                break
            self._analog_up_down_accum -= 1.0
            break

        self.update_lock()

    def hard(self):
        while not self.check_collision(self.piece_x, self.piece_y + 1):
            self.piece_y += 1
        self.lock_piece()
        self.play_sfx("hard_drop")

    def hold(self):
        if self.hold_locked:
            return

        old_piece = self.active_piece
        old_rotations = self.active_piece_rotations
        old_state = self.rotation_state
        old_color = self.active_color

        if self.hold_piece is None:
            self.hold_piece = old_piece
            self.hold_rotations = old_rotations
            self.hold_state = old_state
            self.hold_color = old_color
            self.spawn_piece()
        else:
            self.active_piece = self.hold_piece
            self.active_piece_rotations = self.hold_rotations
            self.rotation_state = self.hold_state
            self.active_color = self.hold_color

            self.hold_piece = old_piece
            self.hold_rotations = old_rotations
            self.hold_state = old_state
            self.hold_color = old_color

            self.piece_x = int(self.width / 2)-2
            self.piece_y = -len(self.active_piece)

        self.hold_locked = True
        self.lock_counter = 0
        self.play_sfx("hold")

  
    def rotate_srs(self, clockwise=True):
        if not self.active_piece:
            return False

        old_state = self.rotation_state
        new_state = (old_state + (1 if clockwise else -1)) % 4
        new_piece_matrix = self.active_piece_rotations[new_state]

        table_key = 'I' if self.active_piece_type == 'I' else 'JLSTZ'
        kicks = self.WALL_KICKS[table_key].get((old_state, new_state), [(0, 0)])

        for index, (dx, dy) in enumerate(kicks):
            
            if not self.check_collision(self.piece_x + dx, self.piece_y - dy, new_piece_matrix):
                self.active_piece = new_piece_matrix
                self.rotation_state = new_state
                self.piece_x += dx
                self.piece_y -= dy 

                self.last_move_was_rotate = True
                self.last_kick_index = index

                
                self.lock_counter = 0 
                self.play_sfx("rotate")
                return True
        return False
 

    def rotate_180_srs(self):
        old_state = self.rotation_state
        new_state = (old_state + 2) % 4
        new_piece = self.active_piece_rotations[new_state]

        if not self.active_piece:
            return False

    
        kicks = [(0,0), (0,1), (1,0), (-1,0), (1,1), (-1,1), (0,-1)]
        
        for index, (dx, dy) in enumerate(kicks):
            if not self.check_collision(self.piece_x + dx, self.piece_y - dy, new_piece):
                self.active_piece = new_piece
                self.rotation_state = new_state

                self.last_move_was_rotate = True
                self.last_kick_index = index

                self.piece_x += dx
                self.piece_y -= dy
                self.lock_counter = 0
                self.play_sfx("rotate")
                return True
            
        return False

    def cw(self):
        return self.rotate_srs(clockwise=True)

    def ccw(self):
        return self.rotate_srs(clockwise=False)

    def spin_180(self):
        self.rotate_180_srs()

    # --
    # rendering
    # --
    def _init_persistent_nodes(self):
 
        for gy in range(self.height):
            row = []
            for gx in range(self.width):
                node = bs.newnode(
                    'image',
                    attrs={
                        'texture': self.grid_texure,
                        'scale': (20*self.scale, 20*self.scale),
                        'position': (
                            self.position[0] + self.position_offset[0] + gx*20*self.scale,
                            self.position[1] + self.position_offset[1] - gy*20*self.scale
                        ),
                        'color': (1, 1, 1),
                        'opacity': 0.0,
                        'front': False,
                    }
                )
                row.append(node)
                self.nodes.append(node)
            self._grid_nodes.append(row)
        for gy in range(self.height):
            row = []
            for gx in range(self.width):
                node = bs.newnode(
                    'image',
                    attrs={
                        'texture': self.block_texture,
                        'scale': (20*self.scale, 20*self.scale),
                        'position': (
                            self.position[0] + self.position_offset[0] + gx*20*self.scale,
                            self.position[1] + self.position_offset[1] - gy*20*self.scale
                        ),
                        'color': (0, 0, 0),
                        'opacity': 0.0,
                        'front': False,
                        
                    }
                )
                row.append(node)
                self.nodes.append(node)
            self._block_nodes.append(row)
        self._ghost_nodes = []
        for _ in range(4):
            row = []
            for _ in range(4):
                node = bs.newnode(
                    'image',
                    attrs={
                        'texture': self.block_texture,
                        'scale': (20*self.scale, 20*self.scale),
                        'position': (0, 0),
                        'color': (1, 1, 1),
                        'opacity': 0.0,
                    }
                )
                row.append(node)
                self.nodes.append(node)
            self._ghost_nodes.append(row)
        self._active_nodes = []
        for _ in range(4):
            row = []
            for _ in range(4):
                node = bs.newnode(
                    'image',
                    attrs={
                        'texture': self.block_texture,
                        'scale': (20*self.scale, 20*self.scale),
                        'position': (0, 0),
                        'color': (1, 1, 1),
                        'opacity': 0.0,
                    }
                )
                row.append(node)
                self.nodes.append(node)
            self._active_nodes.append(row)
        self._hold_nodes = []
        for _ in range(4):
            row = []
            for _ in range(4):
                node = bs.newnode(
                    'image',
                    attrs={
                        'texture': self.block_texture,
                        'scale': (20*self.scale, 20*self.scale),
                        'position': (0, 0),
                        'color': (1, 1, 1),
                        'opacity': 0.0,
                    }
                )
                row.append(node)
                self.nodes.append(node)
            self._hold_nodes.append(row)
        self._next_nodes = []
        for _ in range(5):
            piece_nodes = []
            for _ in range(4):
                row = []
                for _ in range(4):
                    node = bs.newnode(
                        'image',
                        attrs={
                            'texture': self.block_texture,
                            'scale': (20*self.scale, 20*self.scale),
                            'position': (0, 0),
                            'color': (1, 1, 1),
                            'opacity': 0.0,
                        }
                    )
                    row.append(node)
                    self.nodes.append(node)
                piece_nodes.append(row)
                
            self._next_nodes.append(piece_nodes)
        self._label_nodes = []
        for _ in range(3):
            node = bs.newnode(
                'text',
                attrs={
                    'text': '',
                    'position': (0, 0),
                    'h_align': 'center',
                    'v_align': 'center',
                    'scale': 1.0,
                    'color': (1, 1, 1, 1),
                    'shadow': 0.7,
                    'flatness': 1.0,
                    'maxwidth': 200
                }
            )
            self.nodes.append(node)
            self._label_nodes.append(node)
        for i in range(self.height):
            node = bs.newnode(
                'image',
                attrs={
                    'texture': self.block_texture,
                    'scale': (20*self.scale, 20*self.scale),
                    'position': (0, 0),
                    'color': (0.7, 0.7, 0.7),
                    'opacity': 0.0,
                }
            )
            self.nodes.append(node)
            self._garbage_nodes.append(node)
        self.nodes_exist = True    

        

    def draw(self):

        if not self.active:
            return
        
        if not self.render:
            if self.nodes_exist:
                self.delete_all_nodes(mark_exists_false=False)
            return
        if not self.nodes_exist:
            self._init_persistent_nodes()
            return
        if self.simple:
        
            for node in self.nodes:
                node.opacity = 0.0
            
            base_x = self.position[0] + self.position_offset[0]
            base_y = self.position[1] + self.position_offset[1]
            size = 20 * self.scale
            
            white_tex = bs.gettexture('white')

            for gy in range(self.height):
                for gx in range(self.width):
                    node = self._block_nodes[gy][gx]
                    cell = self.grid[gy][gx]
                    node.opacity = 1.0
                    
                
                    if cell:
                        node.color = cell
                    else:
                        node.color = (0, 0, 0)
                    
                    node.texture = white_tex
                    node.scale = (size, size)
                    node.position = (base_x + gx * size, base_y - gy * size)
            
            self._label_nodes[0].text = self.player.getname()
            self._label_nodes[0].position = (base_x + (self.width * size / 2), base_y - (self.height * size) - 20)
            self._label_nodes[0].opacity = 1.0
            self._label_nodes[0].scale = self.scale
            
    
            return
            
   
        for gy in range(self.height):
            for gx in range(self.width):
                node = self._grid_nodes[gy][gx]
                node.color = (0.5, 0.5, 0.5)
                node.opacity = 0.8
                node.scale = (20*self.scale, 20*self.scale)
                node.position = (
                    self.position[0] + self.position_offset[0] + gx*20*self.scale,
                    self.position[1] + self.position_offset[1] - gy*20*self.scale
                )
        
        for gy in range(self.height):
            for gx in range(self.width):
                node = self._block_nodes[gy][gx]
                cell = self.grid[gy][gx]
                if cell:
                    node.color = cell
                    node.opacity = 1.0
                else:
                    node.opacity = 0.0
                node.scale = (20*self.scale, 20*self.scale)
                node.position = (
                    self.position[0] + self.position_offset[0] + gx*20*self.scale,
                    self.position[1] + self.position_offset[1] - gy*20*self.scale
                )
                node.texture = self.block_texture
              
       
        for py in range(4):
            for px in range(4):
                self._ghost_nodes[py][px].opacity = 0.0
       
        ghost_y = self.piece_y
        max_ghost_fall = 1000
        iterations = 0
        while not self.check_collision(self.piece_x, ghost_y + 1) and iterations < max_ghost_fall:
            ghost_y += 1
            iterations += 1
        for py, row in enumerate(self.active_piece):
            for px, cell in enumerate(row):
                if cell and 0 <= py < 4 and 0 <= px < 4:
                    node = self._ghost_nodes[py][px]
                    node.color = (1, 1, 1)
                    node.opacity = 0.3
                    node.scale = (20*self.scale, 20*self.scale)
                    node.position = (
                        self.position[0] + self.position_offset[0] + (self.piece_x + px)*20*self.scale,
                        self.position[1] + self.position_offset[1] - (ghost_y + py)*20*self.scale
                    )
                    node.texture = self.block_texture
            
        for py in range(4):
            for px in range(4):
                self._active_nodes[py][px].opacity = 0.0

                node.texture = self.block_texture
        for py, row in enumerate(self.active_piece):
            for px, cell in enumerate(row):
                if cell and 0 <= py < 4 and 0 <= px < 4:
                    node = self._active_nodes[py][px]
                    node.color = self.active_color
                    node.opacity = 1.0
                    node.scale = (20*self.scale, 20*self.scale)
                    node.position = (
                        self.position[0] + self.position_offset[0] + (self.piece_x + px)*20*self.scale,
                        self.position[1] + self.position_offset[1] - (self.piece_y + py)*20*self.scale
                    )
                    node.texture = self.block_texture
                  
                   
        if self.check_collision(self.piece_x, self.piece_y):
            self.reached_top()
        next_x_offset = self.width + 1
        next_y_start = self.height - 2
        next_spacing = 4
        preview_pieces = self.bag[:5]
        preview_pieces = list(reversed(preview_pieces))
        for idx in range(5):
            piece_nodes = self._next_nodes[idx]
            if idx < len(preview_pieces):
                piece, color = preview_pieces[idx]
                piece = piece.copy()
                piece.reverse()
                for py in range(4):
                    for px in range(4):
                        node = piece_nodes[py][px]
                        val = 0
                        if py < len(piece) and px < len(piece[py]):
                            val = piece[py][px]
                        if val:
                            node.color = color
                            node.opacity = 1.0
                            node.scale = (20*self.scale, 20*self.scale)
                            node.position = (
                                self.position[0] + self.position_offset[0] + (next_x_offset + px)*20*self.scale,
                                self.position[1] + self.position_offset[1] - (next_y_start - idx*next_spacing - py)*20*self.scale
                            )
                        else:
                            node.opacity = 0.0
                        
                
            else:
                for py in range(4):
                    for px in range(4):
                        piece_nodes[py][px].opacity = 0.0
        for py in range(4):
            for px in range(4):
                self._hold_nodes[py][px].opacity = 0.0
        if self.hold_piece:
            try:
                hold = self.hold_piece.copy()
                hold.reverse()
                hold_x_offset = self.width - 15
                hold_y_start = self.height - 16
                for py in range(4):
                    for px in range(4):
                        node = self._hold_nodes[py][px]
                        val = 0
                        if py < len(hold) and px < len(hold[py]):
                            val = hold[py][px]
                        if val:
                            node.color = self.hold_color
                            node.opacity = 1.0
                            node.scale = (20*self.scale, 20*self.scale)
                            node.position = (
                                self.position[0] + self.position_offset[0] + (hold_x_offset + px)*20*self.scale,
                                self.position[1] + self.position_offset[1] - (hold_y_start - py)*20*self.scale
                            )
                        else:
                            node.opacity = 0.0
                      
            except Exception:
                pass

        # Do you like optimizing? fuck you.
        name = self.player.getname(True, True)
        board_left = self.position[0] + self.position_offset[0]
        board_top = self.position[1] + self.position_offset[1]
        board_width_px = self.width * 20 * self.scale
        board_height_px = self.height * 20 * self.scale
        name_x = board_left + board_width_px / 2 - 15
        name_y = board_top - board_height_px - 15 * self.scale
        self._label_nodes[0].text = name
        self._label_nodes[0].position = (name_x, name_y)
        self._label_nodes[0].scale = self.scale
        self._label_nodes[0].color = (1, 1, 1, 1)
        self._label_nodes[0].opacity = 1.0
        self._label_nodes[0].maxwidth = 300 * self.scale
        next_label_x = self.position[0] + self.position_offset[0] + (next_x_offset + 2) * 20 * self.scale
        next_label_y = self.position[1] + self.position_offset[1] + 35 * self.scale
        self._label_nodes[1].text = 'NEXT'
        self._label_nodes[1].position = (next_label_x, next_label_y)
        self._label_nodes[1].scale = 0.6 * self.scale
        self._label_nodes[1].color = (0.85, 0.85, 0.85, 1)
        self._label_nodes[1].maxwidth = 120 * self.scale
        self._label_nodes[1].opacity = 1.0
        hold_label_x = self.position[0] + self.position_offset[0] + (self.width - 13) * 20 * self.scale
        hold_label_y = self.position[1] + self.position_offset[1] + 35 * self.scale
        self._label_nodes[2].text = 'HOLD'
        self._label_nodes[2].position = (hold_label_x, hold_label_y)
        self._label_nodes[2].scale = 0.6 * self.scale
        self._label_nodes[2].color = (0.85, 0.85, 0.85, 1)
        self._label_nodes[2].maxwidth = 120 * self.scale
        self._label_nodes[2].opacity = 1.0
        #Garbage 
        garbage_x = self.width - 12 
        total_visual_rows = 0

        for chunk in self.garbage_queue:
            for _ in range(chunk['lines']):
                if total_visual_rows >= self.height: 
                    break

                visual_row = (self.height - 1) - total_visual_rows
                
                node = self._garbage_nodes[total_visual_rows]
                node.scale = (20 * self.scale, 20 * self.scale)
                node.position = (
                    self.position[0] + self.position_offset[0] + (garbage_x * 20 * self.scale),
                    self.position[1] + self.position_offset[1] - (visual_row * 20 * self.scale)
                )
                node.opacity = 1.0
                
                if chunk['is_red']:
                    node.color = (1, 0, 0) # wuh oh
                else:
                   
                    node.color = (0.7, 0.7, 0.7)
                    
                total_visual_rows += 1

        for i in range(total_visual_rows, self.height):
            self._garbage_nodes[i].opacity = 0.0


    def draw_block(self, x, y, color: tuple = (1,1,1), opacity: float = 1.0, texture: bs.Texture = None):
        """ Unused, optimization is a mother fucker """
        
        node = bs.newnode(
            'image',
            attrs={
                'texture': texture if texture else self.block_texture,
                'scale': (20*self.scale, 20*self.scale),
                'position': (
                    self.position[0] + self.position_offset[0] + x*20*self.scale,
                    self.position[1] + self.position_offset[1] - y*20*self.scale
                ),
                'color': color,
                'opacity': opacity,
            }
        )
        self.nodes.append(node)
        return node
  
    

    def spawn_piece(self):
        self._analog_up_down_accum = 0.0
        if not self.refill_bag:
            self.refill_bag = self.TETRIS_PIECES.copy()
            random.shuffle(self.refill_bag)

        while len(self.bag) < 7 and self.refill_bag:
            piece, color = self.refill_bag.pop()
            self.bag.append((piece, color))

        self.active_piece, self.active_color = self.bag.pop(0)

        piece_index = None
        for i, (p, c) in enumerate(self.TETRIS_PIECES):
            if p == self.active_piece:
                piece_index = i
                break

        self.active_piece_type = ["I","O","T","J","L","S","Z"][piece_index]
        self.active_piece_rotations = self.PIECE_ROTATIONS[self.active_piece_type]
        self.active_piece = self.active_piece_rotations[0]
        self.rotation_state = 0

        self.piece_x = int(self.width / 2)-2
        self.piece_y = -len(self.active_piece)
        self.hold_locked = False
        self.last_move_was_rotate = False


        

        if self.bag:
            self.next_piece, self.next_color = self.bag[0]
        else:
            self.next_piece, self.next_color = None, None

        for py, row in enumerate(self.active_piece):
            for px, cell in enumerate(row):
                if cell:
                    gy = self.piece_y + py
                    if gy < 0:
                        continue  # let us spawn bro
                    # WHAT are you doing up here bro
                    if gy < self.height and self.grid[gy][self.piece_x + px]:
                    #    self.reached_top()
                        return

    def update_lock(self):
        if self.check_collision(self.piece_x, self.piece_y + 1):
            self.lock_counter += 1
            if self.lock_counter >= self.lock_delay_frames:
                self.lock_piece()
                self.lock_counter = 0
        else:
            self.lock_counter = 0

    def gravity(self):
        if not self.active:
            return

        if not self.check_collision(self.piece_x, self.piece_y + 1):
            self.piece_y += 1
            self.lock_counter = 0
        self.update_lock()
           
        
    def check_collision(self, x, y, piece=None):
        piece_to_check = piece if piece is not None else self.active_piece
        
        for py, row in enumerate(piece_to_check):
            for px, cell in enumerate(row):
                if cell:
                    target_x = x + px
                    target_y = y + py
                    
                    if target_x < 0 or target_x >= self.width or target_y >= self.height:
                        return True
                    
                    if target_y >= 0:
                        if self.grid[target_y][target_x]:
                            return True
        return False

    def change_targets(self):
        try:
         # send garbage to other players
            boards = self.getactivity().boards.copy()
            random.shuffle(boards)

            boards.remove(self)


            player_count = len(boards)

            if player_count <= 65:
                num_targets = 1
            elif player_count <= 80:
                num_targets = 2
            else:
                num_targets = 3  

            self.targets = boards[:num_targets]
        except:
            self.targets = []
                
           

    def lock_piece(self):
        for py, row in enumerate(self.active_piece):
            for px, cell in enumerate(row):
                if cell:
                    gx = self.piece_x + px
                    gy = self.piece_y + py
                    # why are you up here? die
                    if gy < 0:
                        self.reached_top()
                        return
                    if 0 <= gx < self.width and 0 <= gy < self.height:
                        self.grid[gy][gx] = self.active_color

        # t spene
        is_t_spin, is_t_spin_mini = self.detect_t_spin()
        lines_cleared = self.clear_lines(is_t_spin, is_t_spin_mini)
        if lines_cleared:
            self.combo += 1
        else:
            self.combo = -1

        label = None
        if is_t_spin:
            if lines_cleared > 0:
                label = "T-SPIN"
            else:
                label = "T-SPIN"
       
        elif lines_cleared == 1:
            label = "SINGLE"
        elif lines_cleared == 2:
            label = "DOUBLE"
        elif lines_cleared == 3:
            label = "TRIPLE"
        elif lines_cleared == 4:
            label = "QUAD"

        if self.combo > 0:
            label = label + f'\n{self.combo} combo' 

        if label:
            self._show_clear_label(label)
        if is_t_spin:
            self.play_sfx("tspin_clear")
        elif lines_cleared == 4:
            self.play_sfx("quad_clear")
        elif lines_cleared > 0:
            self.play_sfx("clear")

        

        garbage = 0
        if lines_cleared == 1:
            garbage = 0.2
        elif lines_cleared == 2:
            garbage = 1
        elif lines_cleared == 3:
            garbage = 2
        elif lines_cleared == 4:
            garbage = 4
        if is_t_spin and lines_cleared > 0:
            garbage += 2
        if self.combo > 0:
            combo_bonus = self.combo * 50
            self.score += combo_bonus
            garbage += garbage * (self.combo * 0.65)
        
        garbage = int(garbage*self.getactivity().garbage_multiplier)
        
        # Sorry, you got lines to clear before sending garbage
        if garbage > 0 and not self.garbage_queue:
            for board in self.targets:
                if board.active:
                    self.send_garbage_to_board(board, garbage)
                    
        lines_to_cancel = int(garbage)
        new_queue = []
       
        for chunk in self.garbage_queue:
            if lines_to_cancel > 0:
                if lines_to_cancel >= chunk['lines']:
                    lines_to_cancel -= chunk['lines']
                    continue # chunk is gone
                else:
                    chunk['lines'] -= lines_to_cancel
                    lines_to_cancel = 0
            new_queue.append(chunk)
        self.garbage_queue = new_queue
        if new_queue == 0 and lines_cleared:
            self.play_sfx('board_clear')
           
        
        # Didnt clear anything.
        if not lines_cleared:
            for chunk in list(self.garbage_queue):
                if chunk['is_red']:
                    amount = min(chunk['lines'], 10)
                    if self.garbage_entry_mode == 'continuous':
                        i=1
                        for _ in range(amount):

                            bs.timer(self.garbage_entry_wait_time*i, bs.Call(self._apply_garbage,1))
                            i+=1
                    else: self._apply_garbage(amount)
                    
                    chunk['lines'] -= amount
                    if chunk['lines'] <= 0:
                        self.garbage_queue.remove(chunk)
                    break 

        self.spawn_piece()

   
    def _show_clear_label(self, label: str):
        if not self.active:
            return
        
        if self.simple or not self.render:
            return
        
        for n in self.seperate_nodes:
            if n.exists():
                n.delete()
       
        board_left = self.position[0] + self.position_offset[0]
        board_top = self.position[1] + self.position_offset[1]
        board_width_px = self.width * 20 * self.scale
        label_x = board_left + board_width_px / 2
        label_y = board_top + 30 * self.scale
        text_node = bs.newnode(
            'text',
            attrs={
                'text': label,
                'position': (label_x, label_y),
                'h_align': 'center',
                'v_align': 'center',
                'scale': 1.0 * self.scale,
                'color': (1, 1, 1, 1),
                'shadow': 0.8,
                'flatness': 0.8,
                'maxwidth': 400 * self.scale
            }
        )
        self.seperate_nodes.append(text_node)
        
        bs.animate(text_node, 'opacity',
                    {
                        0: 1,
                        1: 1,
                        3: 0.
                    })
        
    def clear_lines(self, is_t_spin=False, is_t_spin_mini=False):
        new_grid = []
        lines = 0
        for row in self.grid:
            if all(row):
                lines += 1
            else:
                new_grid.append(row)
        while len(new_grid) < self.height:
            new_grid.insert(0, [0]*self.width)
        self.grid = new_grid
        
        # scorin
        base_score = 0
        if is_t_spin:
            if lines == 1:
                base_score = 800
            elif lines == 2:
                base_score = 1200
            elif lines == 3:
                base_score = 1600
            elif lines == 0:
                base_score = 400
        elif is_t_spin_mini:
            if lines == 1:
                base_score = 200
            elif lines == 2:
                base_score = 400 
            elif lines == 0:
                base_score = 100
        else:
            if lines == 1:
                base_score = 100
            elif lines == 2:
                base_score = 300
            elif lines == 3:
                base_score = 500
            elif lines == 4:
                base_score = 800
        self.score += base_score
        return lines
    
    def update_garbage_timers(self, dt: float = 1):
        for chunk in self.garbage_queue:
            if chunk['timer'] > 0:
                chunk['timer'] -= dt
                if chunk['timer'] <= 0:
                    chunk['is_red'] = True
                    if chunk['lines'] <= 3:
                            self.play_sfx('garbageReadyS')
                    elif chunk['lines'] <= 6:
                            self.play_sfx('garbageReadyM')
                    else:
                            self.play_sfx('garbageReadyL')
                
           

    def queue_garbage(self, lines: int, source_player: TetrisPlayer = None):
        if lines <= 0: return
        if source_player or not self.player_last_hit_by:
            self.player_last_hit_by = source_player
        hole = random.randint(0, self.width - 1)
        
        self.garbage_queue.append({
            'lines': lines,
            'timer': self.garbage_delay,
            'is_red': False,
            'hole': hole
        })
        
     
        if lines <= 3:
                self.play_sfx('boardfillS')
        elif lines <= 6:
                self.play_sfx('boardfillM')
        else:
                self.play_sfx('boardfillL')
      
    
    def send_garbage_to_board(self, board: TetrisBoard, garbage: int):
        board.queue_garbage(garbage, self.player)
            
        if garbage <= 3:
            self.play_sfx('spikeS', 1.5)
        elif garbage <= 6:
            self.play_sfx('spikeM', 1.5)
        else:
            self.play_sfx('spikeL', 1.5)


    def _apply_garbage(self, lines: int):
        if lines <= 0:
            return
        if lines <= 6:
            self.play_sfx('boardHurt', 1.5)
        else:
            self.play_sfx('boardHurtL', 1.5)
     
                    

        # Shift existing grid up to make room
        for _ in range(lines):
            if self.grid:
                self.grid.pop(0)

        # Append garbage rows at the bottom
        for _ in range(lines):
            if random.random() < 0.3:
                self.garbage_hole = random.randint(0, self.width - 1)

            new_row = []
            for x in range(self.width):
                if x == self.garbage_hole:
                    new_row.append(0)
                else:
                    new_row.append((0.7, 0.7, 0.7)) 
            self.grid.append(new_row)

        # Raise active piece if it collides with newly added garbage
        while self.check_collision(self.piece_x, self.piece_y, self.active_piece):
            self.piece_y -= 1

    def play_sfx(self, name, volume=1.0):
        if not self.active:
            return
        if self.simple or not self.render:
            pass
            return
        
        if len(self.getactivity().boards) >= 2:
            volume *= min(1.0, self.scale*0.6)

        s = self.sfx.get(name, False)
     
        if s:
            s.play(volume=volume)

    def detect_t_spin(self):
        # a hell na bruh im asking chatgpt to d ots bro fuck na
        

        
        # 1. Rule: Must be a T-piece
        if self.active_piece_type != "T":
            return False, False
        
        # 2. Rule: Last action MUST have been a rotation
        # (You need to set this flag to True in rotate_srs and False in move/gravity)
        if not getattr(self, 'last_move_was_rotate', False):
            return False, False

        # The center of the T-piece 3x3 matrix is (1, 1) relative to piece_x, piece_y
        cx, cy = self.piece_x + 1, self.piece_y + 1
        
        # Corner coordinates
        corners = [
            (self.piece_x, self.piece_y),         # Top-Left (0,0)
            (self.piece_x + 2, self.piece_y),     # Top-Right (2,0)
            (self.piece_x, self.piece_y + 2),     # Bottom-Left (0,2)
            (self.piece_x + 2, self.piece_y + 2)  # Bottom-Right (2,2)
        ]
        
        occupied = 0
        occ_map = [] # To track which specific corners are hit
        for (x, y) in corners:
            is_occ = False
            if x < 0 or x >= self.width or y >= self.height:
                is_occ = True
            elif y >= 0 and self.grid[y][x]:
                is_occ = True
            
            if is_occ:
                occupied += 1
            occ_map.append(is_occ)

        if occupied < 3:
            return False, False

        # 3. Mini vs Full Detection
        # Logic: Check the two "pointing" corners based on rotation state
        # Rotation states: 0: Up, 1: Right, 2: Down, 3: Left
        pointing_corners = {
            0: [0, 1], # Top corners
            1: [1, 3], # Right corners
            2: [2, 3], # Bottom corners
            3: [0, 2]  # Left corners
        }
        
        ptr = pointing_corners[self.rotation_state]
        # If one of the corners the T is "pointing" at is empty, it's a Mini
        # UNLESS the last kick used was the 5th kick (index 4)
        is_mini = False
        if not (occ_map[ptr[0]] and occ_map[ptr[1]]):
            is_mini = True
            
        # Standard SRS rule: If the last kick was Test 5, it's always a Full T-Spin
        if getattr(self, 'last_kick_index', 0) == 4:
            is_mini = False

        return True, is_mini
    
    def show_ko(self, player_kod: TetrisPlayer):
        if not self.active:
            return
        
        if not self.render:
            return
        
        self.play_sfx('KO')
        self.score += 350

     
        try:
            if self.player_last_hit_by:
                label = f'You KO\'d {player_kod.getname()}'
                color = (1,1,1)
        except:
            pass
        board_left = self.position[0] + self.position_offset[0]
        board_top = self.position[1] + self.position_offset[1]
        board_width_px = self.width * 20 * self.scale
        label_x = board_left + board_width_px / 2
        label_y = board_top - 20 * self.scale 
        text_node = bs.newnode(
            'text',
            attrs={
                'text': label,
                'position': (label_x, label_y),
                'h_align': 'center',
                'v_align': 'center',
                'scale': 1.0 * self.scale,
                'color': color,
                'shadow': 0.8,
                'flatness': 0.8,
                'maxwidth': 400 * self.scale
            }
        )
        self.seperate_nodes.append(text_node)
        
        
        bs.animate(text_node, 'opacity',
                    {
                        0: 1,
                        1: 1,
                        3: 0.
                    })

    def reached_top(self):
        if not self.active:
            return
        
        
        if self.simple:
            if self.render:
                self.sfx.get('SIMPLEdie').play()
        else:
            self.play_sfx('die')

        
        label = 'You KO\'d yourself.'
        color = (1,1,1)
        try:
            if self.player_last_hit_by:
                label = f'KO\'d by {self.player_last_hit_by.getname()}'
                color = (1,1,0)
                self.player_last_hit_by.board.show_ko(self.player)


        except:
            pass

        if  self.render:

            board_left = self.position[0] + self.position_offset[0]
            board_top = self.position[1] + self.position_offset[1]
            board_width_px = self.width * 20 * self.scale
            label_x = board_left + board_width_px / 2
            label_y = board_top - 20 * self.scale 
            text_node = bs.newnode(
                'text',
                attrs={
                    'text': label,
                    'position': (label_x, label_y),
                    'h_align': 'center',
                    'v_align': 'center',
                    'scale': 1.0 * self.scale,
                    'color': color,
                    'shadow': 0.8,
                    'flatness': 0.8,
                    'maxwidth': 400 * self.scale
                }
            )
            self.seperate_nodes.append(text_node)
            
            
            bs.animate(text_node, 'opacity',
                        {
                            0: 1,
                            1: 1,
                            3: 0.
                        })
        self.delete(do_animation=True)
    def delete_all_nodes(self, mark_exists_false: bool = True):
        if mark_exists_false:
            self.existing = False
        self.nodes_exist = False    
  
        for node_list in [
                self._active_nodes,
                self._grid_nodes,
                self._block_nodes,
                self._ghost_nodes,
                self._hold_nodes,
                self._next_nodes,
                self._label_nodes,
                self.nodes,
                self.seperate_nodes,
                self._garbage_nodes,
            ]:
                for sublist in node_list:
                    # Uh ok
                    if  isinstance(sublist, bs.Node):
                        sublist.delete()
                        continue

                    for node in sublist:
                            if isinstance(node, list):
                                for n in node:
                                    if n.exists():
                                        n.delete()
                            else:
                                if node.exists():
                                    node.delete()
                
                    sublist.clear()
        self._active_nodes = []
        self._grid_nodes = []
        self._block_nodes = []
        self._ghost_nodes = []
        self._hold_nodes = []
        self._next_nodes = []
        self._label_nodes = []
        self.nodes = []
        self.seperate_nodes = []
        self._garbage_nodes = []
    


    def delete(self, do_animation: bool = False): 
        self.active = False
        

        
        try:
            self.player.resetinput()
        except:
            pass
        
        if do_animation:
            
               
            bs.timer(1, self.delete_all_nodes)
            return
        else:
            self.delete_all_nodes()
            return


        bs.timer(2, self.delete_all_nodes)
    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.delete_all_nodes(True)
           
        else:    return super().handlemessage(msg)
        return None

# ba_meta export bascenev1.GameActivity
class tetrisGame(bs.GameActivity[TetrisPlayer, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'Tetris'
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
        settings['map'] = 'Empty'
        super().__init__(settings)
        
 
        


        self.default_music = (
            bs.MusicType.GOGOSUMMER
        )
        

        self.non_collide_mat = bs.Material()
        self.non_collide_mat.add_actions(
            conditions=('they_have_material', self.non_collide_mat),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
                ('modify_part_collision', 'use_node_collide', False),
            ),
        )
        self.boards: list[TetrisBoard] = []
        self.ai_players: list[AiTetrisPlayer] = []
        self.garbage_multiplier = 1.0




        
    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    def on_player_leave(self, player):
        super().on_player_leave(player)
        if player.board:
            player.board.delete(False)
    
    def increase_margin(self):
        self.garbage_multiplier += 0.0000025

    def start_increase_margin(self):
        self.garbage_multiplier
        bs.timer(0.1, self.increase_margin, repeat=True)
    #bs.getactivity().start_increase_margin()
    #bs.getactivity().garbage_multiplier

    def on_player_join(self, player):
        super().on_player_join(player)
        player.board = TetrisBoard(player, width=10, height=20)
        

    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
    

    def update_boards(self):
        try:
            living_humans = [p for p in self.players if p.board.existing]
            living_ais = [p for p in self.ai_players if p.board.existing]
            all_living = living_humans + living_ais
            self.boards = [p.board for p in all_living]

            # show AIs if they fit the sidebar limit (6) or if humans are dead
            show_ais = len(all_living) <= 7 or len(living_humans) == 0
            
            ai_count = len(living_ais)
            h_count = len(living_humans)
            if ai_count > 0:
                self.ai_count_text.text = f'Players: {ai_count}'
                self.ai_count_text.color = (1, 0.2, 0.2) if ai_count == 1 else (1, 1, 0.5)
            else:
                self.ai_count_text.text = ''

            if h_count > 0:
                h_cols = math.ceil(math.sqrt(h_count))
                h_scale = min(1.0, 1.5 / h_cols)
                h_spacing_x, h_spacing_y = 420 * h_scale, 540 * h_scale
                h_start_x = (-h_spacing_x * (h_cols - 1) / 2) - 150
                
                for i, p in enumerate(living_humans):
                    col, row = i % h_cols, i // h_cols
                    p.board.render = True
                    p.board.simple = False
                    p.board.scale = h_scale
                    p.board.position = (h_start_x + (col * h_spacing_x), 0 - (row * h_spacing_y) - 120)

            for i, p in enumerate(living_ais):
                if show_ais:
                    if h_count > 0:
                        p.board.render = True
                        p.board.scale = 0.45
                        p.board.simple = True
                        row = i % 3
                        col = i // 3
                        p.board.position = (300 + (col * 180), 110 - (row * 235))
                    
                    elif ai_count > 6:
                        if i < 4: 
                            p.board.render = True
                            p.board.simple = False
                            p.board.scale = 0.7
                            col, row = i % 2, i // 2
                            p.board.position = (-250 + (col * 230), 90 - (row * 340))
                        elif i < 10: 
                            p.board.render = True
                            p.board.simple = True
                            p.board.scale = 0.45
                            row = (i - 4) % 3
                            col = (i - 4) // 3
                            p.board.position = (300 + (col * 180), 110 - (row * 235))
                        else: # Hide the rest
                            p.board.render = False

                    else:
                        p.board.render = True
                        cols = math.ceil(math.sqrt(ai_count))
                        scale = min(1.0, 1.5 / cols)
                        spacing_x, spacing_y = 420 * scale, 540 * scale
                        start_x = -spacing_x * (cols - 1) / 2
                        idx = living_ais.index(p)
                        col, row = idx % cols, idx // cols
                        p.board.position = (start_x + (col * spacing_x), 90 - (row * spacing_y))
                        p.board.scale = scale * 0.8
                        p.board.simple = False

                else:
                    p.board.render = False

            for p in list(self.ai_players):
                if not p.board.exists: self.ai_players.remove(p)
                    
        except Exception as e:
            print(f"Error updating boards: {e}")

    @override
    def on_begin(self) -> None:
        super().on_begin(show_tips_n_stuff=False)
        gnode = self.globalsnode
        gnode.tint = (0.8, 0.8, 0.8)
        gnode.vignette_outer = (0.5, 0.5, 0.5)
        gnode.vignette_inner = (0.5, 0.5, 0.5)
        self.ai_count_text = bs.newnode(
                'text',
                attrs={
                    'text': '',
                    'position': (-400, 228),
                    'h_align': 'center',
                    'v_align': 'center',
                    'scale': 1.0,
                    'color': (1, 1, 1, 1),
                    'shadow': 0.7,
                    'flatness': 1.0,
                    'maxwidth': 200
                }
            )
        bs.timer(0.1, self.update_boards, repeat=True)

        # bs.getactivity().start_battle_royale()
    def start_battle_royale(self):
            for _ in range(100):
                self.create_ai(random.randint(1, 5))
                bs.timer(30, self.start_increase_margin)
      
   
    def create_ai(self, difficulty=3):
        self.ai_players.append(AiTetrisPlayer(difficulty=difficulty))


       

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



class AiTetrisPlayer(TetrisPlayer):
    """
    This is completely AI generated since i dont wanna spend half my weekend coding this +
    I like just having this in the background while i do other work, if you wanna use this just call
    bs.getactivity().create_ai(difficulty_level)

    bs.getactivity().create_ai(3)

    (bs is already defined in goverhaul)
    
    If you spawn too many it might get laggy.

    Used Gemini
    """
    def __init__(self, difficulty=5):
        super().__init__()
        self.board = TetrisBoard(self, 10, 20)
        self.id = random.randint(0, 999999)
        self.difficulty = max(1, min(5, difficulty))

        self.target_move = None 
        self.last_active_piece_id = None

        self.type_map = {'T': 1, 'J': 2, 'I': 3, 'S': 4, 'O': 5, 'L': 6, 'Z': 7}
        self.inv_map = {v: k for k, v in self.type_map.items()}
        
 
        initial_delay = random.uniform(.1, 0.25)
        self.name = f'AILevel{self.difficulty}-{self.id}'
        bs.timer(initial_delay, self.start_thinking)

    def start_thinking(self):
        # Standard thinking speed based on difficulty
        speed = max(0.05, 0.25 - (self.difficulty * 0.04))
        bs.timer(speed, self.think, repeat=True)

    def getname(self, full = False, icon = True):
        try:
            return self.name
        except:
            return ''
    def assigninput(self, inputtype, call):
        return 
    def resetinput(self):
        return 
    def exists(self):     return True

    # --- BRAIN ---
    def think(self):
        if not self.board or not self.board.active_piece:
            return

        curr_id = id(self.board.active_piece)
        
        if curr_id != self.last_active_piece_id:
            # We pass the next piece type to the decision loop
            next_type = None
            if self.board.bag:
                next_type = self.get_type_from_matrix(self.board.bag[0][0])
                
            self.target_move = self.get_best_move(next_type)
            self.last_active_piece_id = curr_id
            
            # Instant Hold logic
            if self.target_move and self.target_move['hold']:
                self.board.hold()
                self.target_move = None 
                return

        if self.target_move:
            self.execute_move_step(self.target_move)

    def get_best_move(self, next_type):
        best_s = -10000000
        best_m = None
        
        curr_type = self.board.active_piece_type
        
        options = [{'type': curr_type, 'hold': False}]
        
        # Aggressive Hold: Swap if it improves the stack
        if not self.board.hold_locked:
            h_type = self.get_type_from_matrix(self.board.hold_piece)
            if not h_type and self.board.bag:
                h_type = self.get_type_from_matrix(self.board.bag[0][0])
            if h_type:
                options.append({'type': h_type, 'hold': True})

        for opt in options:
            p_type = opt['type']
            rots = self.board.PIECE_ROTATIONS.get(p_type, [])
            
            seen_shapes = set()
            for r_idx, rot in enumerate(rots):
                # Optimize by skipping duplicate rotation shapes (O-piece etc)
                rot_tuple = tuple(tuple(row) for row in rot)
                if rot_tuple in seen_shapes: continue
                seen_shapes.add(rot_tuple)

                w, offset = self.get_real_width(rot)
                for x in range(-offset, 10 - w - offset + 1):
                    g, c = self.simulate_drop(self.board.grid, rot, x)
                    
                    score = self.evaluate_board(g, c, p_type)
                    
                    # HOLD PENALTY: Small bias against infinite swapping
                    if opt['hold']: score -= 10
                    
                    if score > best_s:
                        best_s = score
                        best_m = {'x': x, 'rot': r_idx, 'hold': opt['hold']}
        return best_m

    def execute_move_step(self, move):

        if self.board.rotation_state != move['rot']:
            self.board.cw() or self.board.ccw()
            return

        if self.board.piece_x < move['x']:
            self.board._tap_right()
            return
        elif self.board.piece_x > move['x']:
            self.board._tap_left()
            return

        
        
        
        self.board.hard()
        self.target_move = None

    def evaluate_board(self, grid, lines, p_type):
        score = 0
        heights = [self.get_col_height(grid, x) for x in range(10)]
        max_h = max(heights)
        
        # 1. THE FLATNESS REQUIREMENT (Bumpiness)
        # Difference in height between any two adjacent columns.
        # This is the "Staircase Killer"
        bump = sum(abs(heights[i] - heights[i+1]) for i in range(9))
        score -= bump * 150 # Massive penalty for height differences

        # 2. THE HOLE PANIC
        holes = self.count_holes(grid)
        score -= holes * 4000 

        # 3. VERTICALITY (Stay Low)
        score -= (max_h ** 3) * 5 # exponential height penalty

        # 4. QUADREDS REWARD (TETRIS ONLY)
        if lines == 4:
            score += 10000
        elif lines > 0:
            # If the board is messy (height > 10), clearing small lines is good.
            # If it's clean, small clears are bad, they waste pieces.
            score += (lines * 1000) if max_h > 10 or holes > 0 else -100

        # 5. I-PIECE PRIORITIZATION
        if p_type == 'I' and holes == 0 and bump < 2:
            score += 2000 # High reward for placing an I-piece on a clean board
            
        return score

    def count_holes(self, grid):
        """Hole: Empty space under a block."""
        count = 0
        for x in range(10):
            block = False
            for y in range(20):
                if grid[y][x] != 0: block = True
                elif block and grid[y][x] == 0: count += 1
        return count

    def simulate_drop(self, grid, piece, x):
        temp = [row[:] for row in grid]
        ph, pw = len(piece), len(piece[0])
        dy = 0
        while dy + ph <= 20:
            coll = False
            for py in range(ph):
                for px in range(pw):
                    if piece[py][px] != 0:
                        tx, ty = x + px, dy + py
                        if tx < 0 or tx >= 10 or ty >= 20 or temp[ty][tx] != 0:
                            coll = True; break
                if coll: break
            if coll: break
            dy += 1
        dy -= 1
        for py in range(ph):
            for px in range(pw):
                if piece[py][px] != 0:
                    ty = dy + py
                    if 0 <= ty < 20: temp[ty][x+px] = 1
        new_g = [r for r in temp if any(c == 0 for c in r)]
        cleared = 20 - len(new_g)
        while len(new_g) < 20: new_g.insert(0, [0]*10)
        return new_g, cleared

    def get_type_from_matrix(self, matrix):
        if matrix is None: return None
        m_tuple = tuple(tuple(row) for row in matrix)
        for p_type, rotations in self.board.PIECE_ROTATIONS.items():
            for rot in rotations:
                if tuple(tuple(r) for r in rot) == m_tuple: return p_type
        return None

    def get_real_width(self, matrix):
        cols = [i for i, col in enumerate(zip(*matrix)) if any(col)]
        if not cols: return 0, 0
        return max(cols) - min(cols) + 1, min(cols)

    def get_col_height(self, grid, x):
        for y in range(20):
            if grid[y][x] != 0: return 20 - y
        return 0