# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
from bascenev1lib.gameutils import SharedObjects

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
from bascenev1lib.actor.spazfactory import SpazFactory
import random
import bascenev1 as bs

if TYPE_CHECKING:
    from typing import Any, Sequence

from gummyoverhaul.pvz.plants import (
    Plant, Sun, PeaShooter, Sunflower, Wallnut, Repeater, IcePea, PotatoMine, CherryBomb
)
from gummyoverhaul.pvz.zombies import (
    Zombie, FlagZombie, BrownCoat, Conehead, Buckethead, PoleVaulter, NewsPaper,FootballZombie, JackinTheBox
)

class PlantAttackMessage:
    """ ouw .."""
    def __init__(self, plant: Plant, damage: int = 10):
        self.plant = plant
        self.damage = damage

class ZombieAttackMessage:
    """ ouw .. THE SEQUEL"""
    def __init__(self, zombie: Zombie, damage: int = 10):
        self.zombie = zombie
        self.damage = damage



# ba_meta export bascenev1.GameActivity
class PVZGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'PVZ'
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
        
 
        


        self.default_music=None
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))
        

        self.non_collide_mat = bs.Material()
        self.non_collide_mat.add_actions(
            conditions=('they_have_material', self.non_collide_mat),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
                ('modify_part_collision', 'use_node_collide', False),
            ),
        )


        self.seed_bar_bg = None
        self.sun_icon = None
        self.sun_text_node = None
        self.bar_bg=None
        self.zombies_spawned = 0
        self.delete_uhh = []
        self.bar_fill=None
        self.spawning_complete = False
        self.flag_icon=None
        self.input_x = 0.0
        self.input_y = 0.0
        self.controller_input_x = 0.0
        self.controller_input_y = 0.0
        self._cur_plant_idx = 0
        self.selected_plants: list[Plant] = []
        self.file = 'pvz/'
        self.images: list[bs.Node] = []
        self.plants: list[Plant] = []
        self.zombies: list[Zombie] = []
        self.flag_count = 0

        def getsound(sound):
            # Yeah, call me lazy. i dont wanna type it all the damn time.
            return bs.getsound(f'pvz/{sound}')
        self.sfx = {
            'plant1': getsound('plant'),
            'plant2': getsound('plant2'),
            'sun_collect': getsound('points'),
            'zombies_coming': getsound('awooga'),
            'huge_wave': getsound('hugewave'),
            'huge_wave2': getsound('siren'),
            'change_seed': getsound('seedlift'),
            'click': getsound('ceramic'),
            'shovel': getsound('shovel'),
            'error': bs.getsound('error'),


        }
        self.last_plant_times = {}
        


       


        
    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    def play_sound(self, sound):
        s = self.sfx.get(sound, None)
        if s:
            s.play()

    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
    
    def set_music(self, music: str):
        if music is None:
            if self.music:
                self.music.delete()
                self.music = bs.newnode('sound', attrs={'music': True})
            return
        if self.music:
            self.music.delete()
            self.music = bs.newnode('sound', attrs={'sound':bs.getsound(self.file + music), 'music': True})
    
    def _start_sky_sun_loop(self):
        self.sun_timer = bs.Timer(14, self.drop_sun, repeat=True)

    def drop_sun(self):
        sun=Sun(
                (
                    random.uniform(-2, 2),
                    3,
                    random.uniform(-4, 4),

                )
            ).autoretain()
        sun.sun = 50
        sun.node.mesh_scale = 0.35
        
 
    def on_expire(self):
        super().on_expire()
        # i was thinking about doing this but i realized you can just 
        # reset and keep your sun count and swap plants without consquences 
        # plus you can just have an army on round 1 lol
        #self.auto_save()
        self.sun_timer=None
    @override
    def on_begin(self) -> None:
        super().on_begin(show_tips_n_stuff=False)
        self.sun_count = 50
        self.game_state = 'SELECTING'
        # im actually so lazy LMFAO
        self.music = bs.newnode('sound', attrs={'music': True})
        self.jack_in_the_box = bs.newnode('sound', attrs={
            'sound': bs.getsound('pvz/jackinthebox'),
            'volume': 0.0
        })
        gnode = self.globalsnode
        
        gnode.tint = (0.65, 0.65, 0.65)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)


        self.load_save()
        #self.auto_save()
        self.flag_text = bs.newnode('text', attrs={
            'text': f"FLAGS COMPLETED:\n{self.flag_count}",
            'scale': 0.8,
            'position': (0, 50),
            'h_align': 'right',
            'v_align': 'center',
            'h_attach': 'right',
            'shadow': 1.0,
                'v_attach': 'bottom',
            'color': (1, 0, 0) 
        })
    
        
        self.setup_grid()
        self.cursor = bs.newnode(
            'prop',
            attrs={
                    'mesh': bs.getmesh('box'),
                    'light_mesh': None,
                    'body': 'crate',
                    'body_scale': 0.05,
                    'shadow_size': 0.44,
                    'mesh_scale': 0.5,
                    'color_texture': bs.gettexture('white'),
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                    'gravity_scale': 0.0,
                    'materials': [self.non_collide_mat], 
                },
        )
        
        
        # Start in selection mode
        self.spawn_selection_menu()
        bs.timer(0.001, self.tick, repeat=True)
    
    def tick(self):
     
        self._update_progress_bar()
        self._check_lose_condition()
        self._check_wave_cleared()
        self.input_x += self.controller_input_x
        maxc = 400 if self.game_state == 'SELECTING'else 10
        
        self.input_x = max(-maxc, min(maxc, self.input_x))
        self.input_y += self.controller_input_y
        self.input_y = max(-maxc, min(maxc, self.input_y))
        exists = False
        for zombie in self.zombies:
            if isinstance(zombie, JackinTheBox):
                # make sure were alive
                if zombie.is_alive():
                    # Theres one in existance.
                    exists=True
                    break
                else:
                    exists=False
            else:
                exists=False
        if exists:
            self.jack_in_the_box.volume = 0.5
        else:
            self.jack_in_the_box.volume = 0.0
            
                
        if self.cursor:
            # 3d
            if self.cursor.getnodetype() == 'prop':
                self.cursor.position = (self.input_x, 0, self.input_y)
                self.cursor.velocity = (0, 0, 0)
            
                
                for node in bs.getnodes():
                    sun = node.getdelegate(Sun)
                    

                    if not sun:
                        continue     
                    if not sun.node:
                        continue
                        
                    dist = ((sun.node.position[0]-self.cursor.position[0])**2 +
                            (sun.node.position[1]-self.cursor.position[1])**2)**0.5
                    if dist < 1.0 and sun.collectable: 
                        # eat
                                
            
                        self.play_sound('sun_collect')
                        self.sun_count += sun.sun
                        self.sun_count = min(9990, self.sun_count)
                        self.sun_text_node.text = str(self.sun_count)
                        sun.handlemessage(bs.DieMessage())
            else:
                # assume 2d
                self.cursor.position = (self.input_x, self.input_y)
                    
        
        for plant in self.plants:
            if not plant.node:
                self.plants.remove(plant)
        for zombie in self.zombies:
            if not zombie.is_alive():
                self.zombies.remove(zombie)
        

    def load_save(self):
        config = bs.app.config
        data = config.get('GUMMY_pvzsave', None)
        
        if not data:
            return False 
            
        self.flag_count = data.get('flag_count', 0)
        self.sun_count = data.get('sun_count', 50)
        
        mapping = {
            'PeaShooter': PeaShooter, 'Sunflower': Sunflower,
            'Wallnut': Wallnut, 'Repeater': Repeater,
            'PotatoMine': PotatoMine, 'IcePea': IcePea , 
            'CherryBomb': CherryBomb,
        }
        
        # clear
        for p in self.plants: p.handlemessage(bs.DieMessage(immediate=True))
        self.plants = []
        
        for p_info in data.get('plants', []):
            p_cls = mapping.get(p_info['type'])
            if p_cls:
                new_plant = p_cls(position=p_info['pos'])
                new_plant.toughness = p_info['hp']
                # tell them to stay inactive tho, sunflowers can still produce sun
                new_plant.active = False
                self.plants.append(new_plant)

        
        return True

    def auto_save(self, game_over: bool = False):
        if game_over:
            # Clear save on game over
            if 'GUMMY_pvzsave' in bs.app.config:
                del bs.app.config['GUMMY_pvzsave']
                bs.app.config.apply_and_commit()
            return
        bs.broadcastmessage("Game Saved!", color=(1, 1, 1))
        config = bs.app.config
        
        plant_data = []
        for plant in self.plants:
            if plant and plant.node and plant.node.exists():
                plant_data.append({
                    'type': plant.name,
                    'pos': plant.node.position,
                    'hp': plant.toughness
                })
        
        save_packet = {
            'flag_count': self.flag_count,
            'sun_count': self.sun_count,
            'plants': plant_data
        }
        
        config['GUMMY_pvzsave'] = save_packet
        config.apply_and_commit()
    
    def _spawn_zombie(self, zombie: Zombie) -> None:
        
        lane_z = random.choice(self.lane_coords)
        
        self.zombies_in_current_flag += 1
        self.zombies_spawned += 1

        spawn_pos = (7.0, 1.0, lane_z)
    
        new_zombie = zombie(position=spawn_pos)
        self.zombies.append(new_zombie)

    def _check_lose_condition(self) -> None:
        if self.game_state == 'GAMEOVER':
            return
        for zombie in getattr(self, 'zombies', []):
            if zombie and zombie.node and zombie.node.position[0] < -7.0:
                self._do_game_over()
                break
    
 
    def _check_wave_cleared(self) -> None:
        if self.game_state != 'PLAYING':
            return
        if not self.spawning_complete:
            return

        active_zombies = [z for z in getattr(self, 'zombies', []) if z and z.is_alive()]
        
        if len(active_zombies) == 0:
            self.reset_to_selection()
       

    def _do_game_over(self) -> None:
        self.game_state = 'GAMEOVER'


        bs.broadcastmessage("THE ZOMBIES ATE YOUR BRAINS!", color=(0, 1, 0))
        bs.getsound('pvz/losemusic').play() 
        self.set_music(None)
        
        
        self.auto_save(True)
            
        # Return to menu after 5 seconds
        bs.timer(5.0, self.end_game)
        
    
    def _start_gameplay_loop(self) -> None:
        if len(self.selected_plants) < 1:
            return 
            
        self.game_state = 'PLAYING'
        self.delete_seed_bar()
        self.create_seed_bar()
        self.setup_cursor()
        self._start_sky_sun_loop()
        self.last_plant_times = {}
        
       


        for n in self.images:
            
            n.delete()
        #self.start_zombie_waves()
        self.spawning_complete = False
        

        self.setup_player_inputs()
        self.zombies_spawned = 0
        self.set_music('play'+str(random.randint(1,1)))
        for plant in self.plants:
            plant.active = True
        for zombie in self.zombies:
            zombie.handlemessage(bs.DieMessage(True))
        
        self.play_sound('zombies_coming')
        bs.broadcastmessage("Zombies are coming!", color=(1, 0, 0))
        self.start_wave_controller()
    
    def start_wave_controller(self) -> None:
        self.zombies_in_current_flag = 0
        
       
        self.max_zombies_per_flag = 10 + (self.flag_count * 5)
        if self.flag_count == 0:
      
            bs.timer(15.0, self._schedule_next_spawn)
        else:
            bs.timer(2.0, self._schedule_next_spawn)

    def _schedule_next_spawn(self) -> None:
        if self.game_state != 'PLAYING':
            return
            
        active_zombies = [z for z in self.zombies if z.is_alive()]
        base_delay = max(0.2, 8.0 - (self.flag_count * 1.8))
        
        # w rushing
        setup_phase = self.zombies_in_current_flag < (self.max_zombies_per_flag * 0.15)
        
        if len(active_zombies) == 0 and not setup_phase:
            actual_delay = 0.5
        else:
            actual_delay = base_delay

        bs.timer(actual_delay, self._spawn_logic)
        
    def _spawn_logic(self) -> None:
        if self.game_state != 'PLAYING':
            return

        if self.zombies_in_current_flag >= self.max_zombies_per_flag:
            self._trigger_flag_wave()
            return

        self._spawn_zombie_by_difficulty()
        self._schedule_next_spawn()

    def _trigger_flag_wave(self) -> None:
        
        
        bs.broadcastmessage("A HUGE WAVE IS COMING!", color=(1, 0.1, 0.1))
        
        self._spawn_zombie(FlagZombie)
       
        self.play_sound('huge_wave')
        self.play_sound('huge_wave2')
        
        num_to_spawn = 3 + self.flag_count
        for i in range(num_to_spawn):
            bs.timer(i * 0.3, self._spawn_zombie_by_difficulty)

        self.flag_count += 1
        self.zombies_in_current_flag = 0
        self.max_zombies_per_flag += 2
        num_to_spawn = 5 + self.flag_count
        for i in range(num_to_spawn):
            is_last = (i == num_to_spawn - 1)
            bs.timer(i * 0.4, bs.Call(self._final_spawn_step, is_last))

    def _final_spawn_step(self, is_last: bool) -> None:
        self._spawn_zombie_by_difficulty()
        if is_last:
            self.spawning_complete = True
            self._check_wave_cleared()
        
        
        

    
    def _spawn_zombie_by_difficulty(self) -> None:
        choices = []
        choices += [BrownCoat] * max(1, 10 - self.flag_count)
        choices += [Conehead]
        
        if self.flag_count >= 2:
            choices += [Conehead] * min(8, self.flag_count)
            choices += [PoleVaulter] * min(12, self.flag_count)
            choices += [NewsPaper] * min(7, self.flag_count * 2)
            choices += [Buckethead]
            
        if self.flag_count >= 4:
           
            choices += [JackinTheBox] * min(4, self.flag_count - 2)
            
        if self.flag_count >= 7:
            choices += [Buckethead] * min(5, self.flag_count - 3)
            choices += [NewsPaper] * min(12, self.flag_count * 2)
            choices += [FootballZombie] * min(8, self.flag_count)
        
        if self.flag_count >= 10:
            choices += [Buckethead] * 5 
            choices += [FootballZombie] * 5
            choices += [JackinTheBox] * 3

        z_type = random.choice(choices)
        self._spawn_zombie(z_type)

    def reset_to_selection(self) -> None:
        self.auto_save()
        
        
        self.game_state = 'SELECTING'
        
   

            
        self.spawn_selection_menu()
        self.sun_timer = None
        self.flag_text.text = f"FLAGS COMPLETED:\n{self.flag_count}"
        for plant in self.plants:
            plant.active = False
    
    def setup_player_inputs(self) -> None:
        player = self.players[0]

        player.resetinput()
        self.input_x = 0.0
        self.input_y = 0.0
        player.assigninput(bs.InputType.LEFT_RIGHT, self._handle_movement_h)
        player.assigninput(bs.InputType.UP_DOWN, self._handle_movement_v)

        if self.game_state == 'SELECTING':
            player.assigninput(bs.InputType.PUNCH_PRESS, self._on_select_confirm)
            player.assigninput(bs.InputType.JUMP_PRESS, self._start_gameplay_loop)
        
        elif self.game_state == 'PLAYING':
            player.assigninput(bs.InputType.PUNCH_PRESS, self._on_plant_press)
            player.assigninput(bs.InputType.BOMB_PRESS, self._on_cycle_plants)
            player.assigninput(bs.InputType.PICK_UP_PRESS, self._use_shovel)
        
    def _use_shovel(self) -> None:
   
        pos = self._get_snapped_coords((self.input_x, 0, self.input_y))
        if pos is None:
            return


        for plant in self.plants:
            if plant :
                if plant.node:
                    p_pos = plant.node.position
                    dist = ((pos[0] - p_pos[0])**2 + (pos[2] - p_pos[2])**2)**0.5
                    
                    if dist < 0.6:
                       
                        plant.handlemessage(bs.DieMessage(True))
                        self.play_sound('shovel')
                        return
        
        self.play_sound('error')
        bs.broadcastmessage("No plant here.", color=(1, 0, 0))

    
    
    def _handle_movement_h(self, value: float) -> None:
        self.controller_input_x = value*(7 if self.game_state == 'SELECTING'else 0.08)
        
      
        
    def _handle_movement_v(self, value: float) -> None:
        self.controller_input_y = -value*(-7 if self.game_state == 'SELECTING'else 0.08)
    
    def _on_cycle_plants(self) -> None:
        
        self._cur_plant_idx = (self._cur_plant_idx + 1) % len(self.selected_plants)
        name = self.selected_plants[self._cur_plant_idx].name
        self.create_seed_bar()
        self.play_sound('change_seed')
         

    def _on_plant_press(self) -> None:
   
        pos = self._get_snapped_coords((self.input_x, 0, self.input_y))
        if pos is None:
            return
        plant_cls = self.selected_plants[self._cur_plant_idx]


      
        for plant in self.plants:
            if plant :
                if plant.node:
                    p_pos = plant.node.position
                    dist = ((pos[0] - p_pos[0])**2 + (pos[2] - p_pos[2])**2)**0.5
                    
                    if dist < 0.6:
                        self.play_sound('error')
                        bs.broadcastmessage("Spot is occupied!", color=(1, 0, 0))
                        return

        if self.sun_count < plant_cls.cost:
            bs.broadcastmessage("Not enough Sun!", color=(1, 0.5, 0))
            return
        
        now = bs.time()
        last_time = self.last_plant_times.get(plant_cls, -999.0)
        
        time_passed = now - last_time
        
        if time_passed < plant_cls.recharge:
            remaining = int(plant_cls.recharge - time_passed)
            bs.broadcastmessage(f"Recharging... ({remaining}s)", color=(1, 0, 0))
            self.play_sound('error')
            return

        self.sun_count -= plant_cls.cost
        self.last_plant_times[plant_cls] = now
        self.sun_text_node.text = str(self.sun_count)

        #yummy in my belly spawn it   
        self.plants.append(plant_cls(position=pos))
        self.play_sound('plant'+str(random.randint(1, 2)))
    
    def setup_cursor(self) -> None:
        if self.cursor:
            self.cursor.delete()

        if self.game_state == 'SELECTING':
            # 2d cursor for menus
            self.cursor = bs.newnode('image', attrs={
                'texture': bs.gettexture('textClearButton'), 
                'scale': (50, 50),
                'color': (1, 1, 1),
                'attach': 'center'
            })

        else:
            
            # 3d cursor for planting stuf ingame
            self.cursor= bs.newnode('prop', attrs={
                'mesh': bs.getmesh('box'),
                'body': 'crate',
                'body_scale': 0.1,
                'mesh_scale': 0.5,
                'color_texture': bs.gettexture('white'),
                'materials': [self.non_collide_mat], 
            })
        
        

    def _get_snapped_coords(self, pos: tuple[float, float, float]) -> tuple[float, float, float] | None:
        closest_x = min(self.col_coords, key=lambda x: abs(x - pos[0]))
        closest_z = min(self.lane_coords, key=lambda z: abs(z - pos[2]))
        
        if abs(pos[0] - closest_x) < 1.0 and abs(pos[2] - closest_z) < 1.0:
            return (closest_x, 0.55, closest_z)
        return None
    
    def spawn_selection_menu(self) -> None:
        self.set_music('seed_select')
        self.game_state == 'SELECTING'
        self.setup_player_inputs()
       
        self.selected_plants = []
        self.images = []
        self.menu_icons = []
        
        bg = bs.newnode('image', attrs={
            'texture': bs.gettexture('black'),
            'position': (0, 0),
            'scale': (700, 450),
            'opacity': 0.8
        })
        self.images.append(bg)

        avail = [PeaShooter, Sunflower, Wallnut, Repeater, IcePea, PotatoMine, CherryBomb]
        for i, plant_cls in enumerate(avail):
            # Calculate grid: 2 rows, 4 columns
            row = i // 4
            col = i % 4
            x_pos = -250 + (col * 150)
            y_pos = 100 - (row * 120)
            
            card = bs.newnode('image', attrs={
                'texture': bs.gettexture('buttonSquare'),
                'position': (x_pos, y_pos),
                'scale': (100, 100),
                'color': (0.3, 0.3, 0.3)
            })
            
            name_txt = bs.newnode('text', attrs={
                'text': plant_cls.name,
                'position': (x_pos, y_pos - 10),
                'scale': 0.7,
                'h_align': 'center'
            })
            
            cost_txt = bs.newnode('text', attrs={
                'text': str(plant_cls.cost),
                'position': (x_pos, y_pos - 35),
                'scale': 0.5,
                'color': (1, 1, 0),
                'h_align': 'center'
            })
            
            self.images.extend([card, name_txt, cost_txt])
            self.menu_icons.append({
                'node': card, 
                'cls': plant_cls, 
                'ui_pos': (x_pos, y_pos) 
            })

        instr = bs.newnode('text', attrs={
            'text': "PUNCH to Select | JUMP to Start",
            'position': (0, -180),
            'scale': 1.0,
            'h_align': 'center',
            'color': (0, 1, 0)
        })
        self.images.append(instr)
        self.setup_cursor()

    def _on_select_confirm(self) -> None:
        if self.game_state != 'SELECTING':
            return
            

        cursor_ui_x = self.input_x 
        cursor_ui_y = self.input_y

        for item in self.menu_icons:
            icon_x, icon_y = item['ui_pos'] 
            
            if (abs(cursor_ui_x - icon_x) < 50 and 
                abs(cursor_ui_y - icon_y) < 50):
                
                plant_cls = item['cls']
                if plant_cls in self.selected_plants:
                    self.selected_plants.remove(plant_cls)
                    item['node'].color = (0.3, 0.3, 0.3)
                    self.play_sound('click')
                else:
                    if len(self.selected_plants) < 6:
                        self.selected_plants.append(plant_cls)
                        item['node'].color = (1, 1, 1)
                        self.play_sound('click')
                
                bs.broadcastmessage(f"Selected: {len(self.selected_plants)}/6", color=(1,1,1) if len(self.selected_plants) < 6 else (0,1,0))
                
                break

       
        
    
    def setup_grid(self) -> None:
        
        self.lane_coords = [2.4, 1.2, 0.0, -1.2, -2.4]
        
        self.col_coords = [-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5, 6.0]


        bs.newnode('region', attrs={
            'position': (0, 0.02, 0), 
            'scale': (999, 0.05, 999),
            'type': 'box',
            'materials': [self.collision, SharedObjects.get().footing_material]
        })
        
        for z in self.lane_coords:
            for x in self.col_coords:
           
                size = (1.5, 0.05, 1.2) 
                
                bs.newnode('locator', attrs={
                    'position': (x, 0.02, z),
                    'shape': 'box',
                    'additive': False,
                    'size': (size[0], 0.0,size[2]),
                    'color': (0, 0.5, 0),
                    'draw_beauty': True,
                })
                
                bs.newnode(
                    "region",
                    attrs=dict(
                        type="box",
                        scale=size,
                        position=(x, 0.02, z),
                        materials=[self.collision, SharedObjects.get().footing_material],
                    ),
                )
    
    def delete_seed_bar(self):
        if self.seed_bar_bg:
            self.seed_bar_bg.delete()
        if self.sun_icon:
            self.sun_icon.delete()
        if self.sun_text_node:
            self.sun_text_node.delete()
        if self.bar_bg:
            self.bar_bg.delete()
        if self.bar_fill:
            self.bar_fill.delete()
        if self.flag_icon:
            self.flag_icon.delete()
        
       
        for node in self.delete_uhh:
            node.delete()
        self.delete_uhh = []
    def _update_progress_bar(self) -> None:
        if not self.bar_fill or not self.bar_fill.exists():
            return
            
        try:  
            progress = min(1.0, self.zombies_spawned / self.max_zombies_per_flag)
        except: 
            progress = 0.0
            
        new_width = progress * 400
        
        bs.animate_array(self.bar_fill, 'scale', 2, {
            0: self.bar_fill.scale,
            0.3: (new_width, 20)
        })

        self.bar_fill.position = (-200 + (new_width / 2), -130)
    def create_seed_bar(self):
        self.delete_seed_bar()
        self.seed_bar_bg = bs.newnode('image', attrs={
            'texture': bs.gettexture('black'),
            'position': (0, 350),
            'scale': (600, 80),
            'opacity': 0.5,
            'color': (0.2, 0.2, 0.2),
        })

        self.sun_icon = bs.newnode('image', attrs={
            'texture': bs.gettexture('star'), 
            'position': (-280, 350),
            'scale': (40, 40),
        })
        
        self.sun_text_node = bs.newnode('text', attrs={
            'text': str(self.sun_count),
            'position': (-250, 350),
            'scale': 1.0,
            "maxwidth": 100,
            'v_align': 'center',
            'h_align': 'left',
        })
        for i, plant_cls in enumerate(self.selected_plants):
            x_offset = -180 + (i * 75) 
            
            is_active = (i == self._cur_plant_idx)
            text_color = (1, 1, 0) if is_active else (1, 1, 1)

    

            txt = bs.newnode('text', attrs={
                'text': plant_cls.name,
                'position': (x_offset, 350),
                'scale': 0.5, 
                'maxwidth': 100, 
                'h_align': 'center',
                'v_align': 'center',
                'color': text_color
            })
            self.delete_uhh.append(txt)
        self.bar_bg = bs.newnode('image', attrs={
            'texture': bs.gettexture('black'),
            'position': (0, -130), 
            'scale': (400, 20),
            'color': (0.2, 0.2, 0.2),
            'attach': 'topCenter'
        })
        
        self.bar_fill = bs.newnode('image', attrs={
            'texture': bs.gettexture('bar'),
            'position': (-200, -130), 
            'scale': (0, 20),
            'color': (1, 1, 0),
            'attach': 'topCenter'
        })
        
        self.flag_icon = bs.newnode('image', attrs={
            'texture': bs.gettexture('nextLevelIcon'),
            'position': (200, -120),
            'scale': (30, 30),
            'attach': 'topCenter'
        })
       
    
  


    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        
        return super().handlemessage(msg)
        return None
    
    @override
    def spawn_player(self, player: bs.Player):

    
        return

    @override
    def end_game(self) -> None:
        from gummyoverhaul._singleplayergame import SinglePlayerSession  
        assert isinstance(self.session, SinglePlayerSession)
        self.session.return_to_main_menu()
