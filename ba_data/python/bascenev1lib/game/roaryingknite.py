# Released under the MIT License. See LICENSE for details.
#
"""Singleplayer game for the Roaring Knight fight."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

import babase
from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
from bascenev1lib.actor.popuptext import PopupText
import random
import math
from gummyoverhaul.mells2dengine.engine import (
    Scene, ScenePlayer, SHOW_HITBOXES, HITBOX_COLOR
)
from gummyoverhaul.mells2dengine.image_looped import LoopingImageAnimation

from gummyoverhaul.mells2dengine.dialog import (
    DialogText
)
""" Thanks for mell's 2d engine for this lol"""


if TYPE_CHECKING:
    from typing import Any, Sequence



        
class DialogueEngine:
    def __init__(self, position=(0, -280), scale=0.6):
        self.position = position
        self.scale = scale
        self.default_talk = bs.getsound('knight/snd_text')
        self.susie_talk = bs.getsound('knight/snd_txtsus')
        self.ralsei_talk = bs.getsound('knight/snd_txtral')
        self.face = None
        self.dialogue = None
        self.dialogbox = None

        self.clear()

        

    def clear(self):

        if self.face:
            self.face.delete()
            self.face = None
        if self.dialogue:
            self.dialogue.node.delete()
        if self.dialogbox:
            self.dialogbox.delete()
        

    def speak_dialog(self,
                text: str,
                delay: float = 0.03,
                face: str = 'cutespaz',
                sound: str = 'basictxt'
                ):
        self.dbox_x = self.position[0]
        self.dbox_y = self.position[1]
        if self.face:
            self.face.delete()
            self.face = None
        if self.dialogue:
            self.dialogue.node.delete()
            self.dialogue = None
        if not self.dialogbox:
            self.dialogbox = bs.newnode('image', 
                        attrs={
                            'texture': bs.gettexture('diabox'),
                            'absolute_scale': True,
                            'position': (self.dbox_x, self.dbox_y),
                            'opacity': 1.0,
                            'scale': (1000*self.scale, 1000*self.scale),
                            'color': (1, 1, 1)
                        }
                    )
        if face:
            self.face = bs.newnode('image', 
                attrs={
                    'texture': face,
                    'absolute_scale': True,
                    'position': (self.dbox_x - 300*self.scale, self.dbox_y),
                    'opacity': 1.0,
                    'scale': (160*self.scale, 160*self.scale),
                    'color': (1, 1, 1)
                }
            )
        self.dialogue = DialogText(
                text,
                position=(self.dbox_x - (150*self.scale if face else 230), self.dbox_y + 5*self.scale),
                delay=delay,
                sound=sound,
                scale=1.3*self.scale
            )

    


    def display_message(self, message: str, speed: float = 0.03, sound: bs.Sound = None, texture: bs.Texture = None) -> float:
        if bs.getactivity().gameover:
            self.clear()
            return
        total_time = 0.0
        # autoamtic line breaks because FUCK YOU MELL LMFAOOFE
        def wrap_text(text, max_len=40):
            words = text.split(' ')
            lines = []
            current = ''
            for w in words:
                if len(current) + len(w) + 1 <= max_len:
                    current = (current + ' ' + w).strip()
                else:
                    lines.append(current)
                    current = w
            if current:
                lines.append(current)
            return '\n'.join(lines)

        message = wrap_text(message, max_len=40 if texture else 60)
        for i, char in enumerate(message):
            t = speed * i
            total_time = t
        self.speak_dialog(message, speed, texture, sound)
        
        return total_time + 1.5 

    def display_sequence(self, messages: list[tuple[str, float, str, str]]) -> float:
        """
        messages: [(text, speed, talk, texture), ...]
        """
        self.clear()
       
       
        total_delay = 0.0
        for text, speed, talk, texture in messages:
   

            if isinstance(texture, str):
                texture = bs.gettexture(texture)
            elif isinstance(texture, bs.Texture):
                pass
            else:
                texture = None
            
            if talk == 'susie':
                sound = self.susie_talk
            elif talk == 'ralsei':
                sound = self.ralsei_talk
            else:
                sound = self.default_talk
            start_at = total_delay 
            bs.timer(start_at, bs.Call(self.display_message, text, speed, sound, texture))
            
            
            total_delay += (len(text) * speed) + 1.5

        return total_delay
        

       
 
        

    def _append_char(self, char, sound: bs.Sound = None):
        if sound:
            sound.play(3)
        self.current_text += char
        self.text_node.text = self.current_text


# ba_meta export bascenev1.GameActivity
class roaryGame(bs.GameActivity[bs.Player, bs.Team]):
    """A gametype where you beat the Roaring Knight."""

    name = 'Roaring Knight'
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
        settings['map'] = 'The Pad'
        super().__init__(settings)
        
        
 
        


        self.default_music = (
            bs.MusicType.BLACKKNIFE
        )
        def getsound(sound):
            # Yeah, call me lazy. i dont wanna type it all the damn time.
            return bs.getsound(f'knight/{sound}')
        self.sfx = {
            'knighthurt1': getsound('knight_hurt1'),
            'knighthurt2': getsound('knight_hurt2'),
            'attack': getsound('hero_slash'),
            'select': getsound('menu_sel'),
            'hurt': getsound('hero_hurt'),
            'heal': getsound('hero_heal'),
            'buster_swing': getsound('rude_bust_swing'),
            'buster_hit': getsound('rude_bust_hit'),
            'swoon1': getsound('swoon1'),
            'swoon2': getsound('swoon2'),

        }
        

        self.non_collide_mat = bs.Material()
        self.non_collide_mat.add_actions(
            conditions=('they_have_material', self.non_collide_mat),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
                ('modify_part_collision', 'use_node_collide', False),
            ),
        )

        pos_top = (-6.3,4.6,-5.9)
        pos_middle=(-6.3,4.6,-2.5)
        pos_bottom=(-6.3,4.6,0.3)
        self.center_position = (0.2,3.5,-2.7)
        self.z_barrier = -7.80
        self.tp = 0
        self.scene: Scene = None
        try:
            self.kris_position = pos_top#pos_middle if len(self.session.sessionplayers) == 1 else pos_top
            self.kris_actor: Spaz = None
            self.kris_hp_max = 160
            self.kris_hp = self.kris_hp_max 
            self.kris_defending = False

            self.susie_position = pos_middle
            self.susie_actor: Spaz = None
            self.susie_hp_max = 190
            self.susie_hp = self.susie_hp_max 
            self.susie_defending = False

            self.ralsei_position = pos_bottom
            self.ralsei_actor: Spaz = None
            self.ralsei_hp_max = 140
            self.ralsei_hp = self.ralsei_hp_max 
            self.ralsei_defending = False
        except Exception as e:
            print(e)

        self.soul_actor: Spaz = None

        self.knight_hp = 7500
        #self.knight_hp = 6001
        self.knight_position = (6.4,4.6,-3.0)
        self.knight_turn = False
        self.hits = 0

        self.attack_pattern = [
            KnightAttackStars,
            KnightHomingAttack,
            KnightSlashBurst,
            KnightSwordWalls,
            KnightCrossShapes,
            KnightAttackStars,
            KnightSlashBurst,
            KnightSwordWallsVariant,
            KnightHomingAttackVariant,
            KnightCrossShapes,
            KnightAttackStarsVariant,
            KnightSlashBurst,
            KnightHomingAttack,
            KnightSwordWalls,
            KnightCrossShapes,
            KnightAttackStarsVariant,
        ]
        
        #self.attack_pattern=[KnightHomingAttackVariant,] # testing
        self.turn_count = 0 
        self.i_frames = {
            'kris': 0.0,
            'susie': 0.0,
            'ralsei': 0.0
        }

        self.kris_checked = False
        self.suise_talked = False
        self.ralsei_talked = False
        self.gameover=False
        self.phase_2 = False
        self.guard_down = False

        self.models = {
            'soul': dict(
                head_mesh = bs.getmesh('ralseiHead'),
                torso_mesh = bs.getmesh('ralseiTorso'),
                pelvis_mesh = bs.getmesh('ralseiPelvis'),
                upper_arm_mesh = bs.getmesh('ralseiUpperArm'),
                forearm_mesh = bs.getmesh('ralseiForeArm'),
                hand_mesh = bs.getmesh('ralseiHand'),
                upper_leg_mesh = bs.getmesh('ralseiUpperLeg'),
                lower_leg_mesh = bs.getmesh('ralseiLowerLeg'),
                toes_mesh = bs.getmesh('ralseiToes'),
            ),
            'kris': dict(
                head_mesh = bs.getmesh('krisHead'),
                torso_mesh = bs.getmesh('krisTorso'),
                pelvis_mesh = bs.getmesh('krisPelvis'),
                upper_arm_mesh = bs.getmesh('krisUpperArm'),
                forearm_mesh = bs.getmesh('krisForeArm'),
                hand_mesh =bs.getmesh( 'krisHand'),
                upper_leg_mesh = bs.getmesh('krisUpperLeg'),
                lower_leg_mesh = bs.getmesh('krisLowerLeg'),
                toes_mesh = bs.getmesh('krisToes'),
                down_prop=bs.getmesh('krisdowned'),
                prop_texture=bs.gettexture('krisColor'),
            ),
            'susie': dict(
                head_mesh = bs.getmesh('susieHead'),
                torso_mesh = bs.getmesh('susieTorso'),
                pelvis_mesh = bs.getmesh('susiePelvis'),
                upper_arm_mesh =bs.getmesh( 'susieUpperArm'),
                forearm_mesh = bs.getmesh('susieForeArm'),
                hand_mesh = bs.getmesh('susieHand'),
                upper_leg_mesh = bs.getmesh('susieUpperLeg'),
                lower_leg_mesh =bs.getmesh( 'susieLowerLeg'),
                toes_mesh = bs.getmesh('susieToes'),
                down_prop=bs.getmesh('susiedead'),
                prop_texture=bs.gettexture('susieColor'),
            ),
            'ralsei': dict(
                head_mesh = bs.getmesh('ralseiHead'),
                torso_mesh = bs.getmesh('ralseiTorso'),
                pelvis_mesh = bs.getmesh('ralseiPelvis'),
                upper_arm_mesh = bs.getmesh('ralseiUpperArm'),
                forearm_mesh = bs.getmesh('ralseiForeArm'),
                hand_mesh = bs.getmesh('ralseiHand'),
                upper_leg_mesh = bs.getmesh('ralseiUpperLeg'),
                lower_leg_mesh = bs.getmesh('ralseiLowerLeg'),
                toes_mesh = bs.getmesh('ralseiToes'),
                down_prop=bs.getmesh('ralseidown'),
                prop_texture=bs.gettexture('ralseiColor'),
            )
        }




        
    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''
    
    def play_sound(self, soundname):
        if self.gameover:
            return
        
        sound = self.sfx.get(soundname)

        if sound:
            sound.play()


    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
 
    
        
    @override
    def on_begin(self) -> None:
        super().on_begin(show_tips_n_stuff=False)
        # First off, prevent leaving and joining. 
        self.session.max_players = len(self.players)
        self.session.minimum = len(self.players)

        # setup the stage
        map = self.map

        map.node.mesh = bs.getmesh('deltafloor')
        map.node.color_texture=bs.gettexture('deltafield')
        map.bottom.mesh = None
        map.background.color_texture = bs.gettexture('black')
        self.globalsnode.tint = (1, 1, 1)

        LoopingImageAnimationModel('deltabg', 'fountain', 4, 0.25)
        #LoopingImageAnimationModel('deltaknightbg', 'tokens', 4, 0.3)

        # snow
        bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': bs.getmesh('deltasnow'),
                'color_texture': bs.gettexture('white'),
            },
        )

        self.group_heals = 6
        self.medium_heals = 8
        self.large_heals = 3
        self.revive_mints = 5

        self.turn = 1

        # Ok define inventory space.
        self.inventory = {
            'kris': {
                bs.InputType.BOMB_PRESS: {
                    'name': 'Defend',
                    'action': self.defend
                },
                bs.InputType.JUMP_PRESS: {
                    'name': 'Act',
                    'action': self.return_act_menu
                },
                bs.InputType.PUNCH_PRESS: {
                    'name': 'Attack',
                    'action': self.attack
                },
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'Item',
                    'action': self.return_item_menu
                },
            },
            'susie': {
                bs.InputType.BOMB_PRESS: {
                    'name': 'Defend',
                    'action': self.defend
                },
                bs.InputType.JUMP_PRESS: {
                    'name': 'Magic',
                    'action': self.return_act_menu
                },
                bs.InputType.PUNCH_PRESS: {
                    'name': 'Attack',
                    'action': self.attack
                },
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'Item',
                    'action': self.return_item_menu
                },
            },
            'ralsei': {
                bs.InputType.BOMB_PRESS: {
                    'name': 'Defend',
                    'action': self.defend
                },
                bs.InputType.JUMP_PRESS: {
                    'name': 'Magic',
                    'action': self.return_act_menu
                },
                bs.InputType.PUNCH_PRESS: {
                    'name': 'Attack',
                    'action': self.attack
                },
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'Item',
                    'action': self.return_item_menu
                },
            }
        }

       
       

        self.knight_actor = Spaz(
            (0,0,0),
            (1,1,1),
            'Roaring Knight',
        ).autoretain()
        self.knight_actor.node.hold_position_pressed = True
        self.knight_actor.node.move_left_right = -1
        l=bs.newnode('light', attrs={
            'color': (0.4, 0.2, 0.8), 
            'radius': 0.15, 
            'intensity': 2.0,
            'volume_intensity_scale': 1.0
        })
        self.knight_actor.node.connectattr('position', l, 'position')
        self.knight_actor.handlemessage(bs.StandMessage(self.knight_position, -90))

        self.text_engine = DialogueEngine()

        if len(self.players) == 1:
            self.susie_actor = Spaz(color=(1, 0.3, 0.6), highlight=(1, 0, 1), character='Susie', 
                            ).autoretain()
            l=bs.newnode('light', attrs={
                'color': self.susie_actor.Dcolor, 
                'radius': 0.3, 
                'intensity': 0.8,
                'volume_intensity_scale': 1.0
            })
            self.susie_actor .node.connectattr('position', l, 'position')
            self.susie_actor.node.name = 'Susie'
            self.susie_actor.node.name_color = (1, 0.3, 0.6)

        
            self.ralsei_actor = Spaz(color=(0.3, 1, 0), highlight=(0, 1, 0), character='Ralsei', 
                                  ).autoretain()
            l=bs.newnode('light', attrs={
                'color': self.ralsei_actor.Dcolor, 
                'radius': 0.15, 
                'intensity': 1.0,
                'volume_intensity_scale': 1.0
            })
            self.ralsei_actor .node.connectattr('position', l, 'position')
            self.ralsei_actor.node.name = 'Ralsei'
            self.ralsei_actor.node.name_color = (0.3, 1, 0)

            self.kris_actor.node.name = 'Kris'
            

        self.create_ui()
        bs.timer(0.1, self.start_turn)
        bs.timer(0.1, self.tick, repeat=True)

    

        for spaz in [self.kris_actor, self.susie_actor, self.ralsei_actor]:
            try:
                spaz.award_xp = False
                spaz.impact_scale = 0.0
                spaz.node.materials += (self.non_collide_mat,)
                spaz.node.roller_materials += (self.non_collide_mat,)
                spaz.node.extras_material += (self.non_collide_mat,)
            except:
                pass
        bs.getsound('knight/attack3').play()
        

    def tick(self):
        dead = 0

        if self.soul_actor:
            if self.soul_actor.node.position[2] < self.z_barrier:
                        self.soul_actor.handlemessage(bs.StandMessage((
                            self.soul_actor.node.position[0], self.soul_actor.node.position[1]-1, self.z_barrier+0.1
                        ),180))

        for character in ['kris', 'ralsei', 'susie']:
            actor: Spaz = getattr(self, f'{character}_actor', None)
            if not actor: 
                continue

            if self.knight_turn:
                if len(self.players) == 1:
                    actor.node.is_area_of_interest = False
                self.knight_actor.node.is_area_of_interest = False
            else:
                actor.node.is_area_of_interest = True
                self.knight_actor.node.is_area_of_interest = True


            
            prop = getattr(self, f'{character}_downed_prop', None)
            if getattr(self, f'{character}_hp', 0) <= 0:
                node = actor.node
                try:
                    actor.disconnect_controls_from_player()
                except: pass
                actor.node.head_mesh = None
                actor.node.torso_mesh = None
                actor.node.pelvis_mesh = None
                actor.node.upper_arm_mesh = None
                actor.node.forearm_mesh = None
                actor.node.hand_mesh = None
                actor.node.upper_leg_mesh = None
                actor.node.lower_leg_mesh = None
                actor.node.toes_mesh = None     
                dead += 1
                
            
            else:
                node = actor.node

                models = self.models[character]
                node.head_mesh = models['head_mesh']
                node.torso_mesh = models['torso_mesh']
                node.pelvis_mesh = models['pelvis_mesh']
                node.upper_arm_mesh = models['upper_arm_mesh']
                node.forearm_mesh = models['forearm_mesh']
                node.hand_mesh = models['hand_mesh']
                node.upper_leg_mesh = models['upper_leg_mesh']
                node.lower_leg_mesh = models['lower_leg_mesh']
                node.toes_mesh = models['toes_mesh']
                if prop:
                    prop.delete()
               
                if not self.knight_turn:
                    node.hold_position_pressed = True
                    node.move_left_right = 1
                else:
                    if not (character in ['susie', 'ralsei'] and len(self.players) == 1):

                        node.hold_position_pressed = False
                    if actor.node.position[2] < self.z_barrier:
                        actor.handlemessage(bs.StandMessage((
                            actor.node.position[0], actor.node.position[1]-1, self.z_barrier+0.1
                        ),180))

        if dead == (len(self.players) if len(self.players) != 1 else 3):
            self.show_game_over()
    
    def knight_punch(self):
        if self.knight_actor:
            self.knight_actor.node.punch_pressed = True
            self.knight_actor.node.punch_pressed = False
    def knight_celebrate(self, duration: float = 1.0):
        if self.knight_actor:
            self.knight_actor.handlemessage(bs.CelebrateMessage(duration=duration))
    
    def create_ui(self):
        self.ui_nodes = {}

        base_y_pos = -160

        x_spacing = 190 
        
        colors = {
            'kris': (0, 0.6, 1), 
            'susie': (1, 0.3, 0.6), 
            'ralsei': (0.3, 1, 0)
        }

        players_present = self.players
        characters = ['kris', 'susie', 'ralsei']


        start_x = -((len(players_present) - 1) * x_spacing) / 2

        for i, char in enumerate(characters):
            if i >= len(players_present) and not len(players_present) == 1:
                continue

            current_x = start_x + (i * x_spacing)

            hp_node = bs.newnode('text', attrs={
                'text': f"{getattr(self, f'{char}_hp')} / {getattr(self, f'{char}_hp_max')}",
                'position': (current_x, base_y_pos), 
                'h_align': 'center',
                'v_align': 'center',
                'scale': 1.0,
                'color': colors[char],
                'in_world': False,
                'shadow': 0.5,
                'flatness': 1.0,
            })
            self.ui_nodes[char] = {'hp': hp_node}
        x=-290
        y=-290

        self.tp_node = bs.newnode('text', attrs={
            'text': f"{int(self.tp)}%",
            'position': (x, y+100), 
            'h_align': 'center',
            'v_align': 'center',
            'scale': 1.2,
            'color': (1, 1, 0),
            'in_world': False,
            'shadow': 0.5,
            'flatness': 1.0,
        })
        self.tp_bar_bg = bs.newnode('image',
            attrs={
                'texture': bs.gettexture('flagColor'),
                'color': (0.8,0.0,0.0),
                'scale': (30,150),
                'position': (x, y),
                'attach': 'center'
            })
        self.tp_bar = bs.newnode('image',
            attrs={
                'texture': bs.gettexture('bar'),
                'color': (1,1,0),
                'scale': (30, 150),
                'position': (x, y),
                'attach': 'center'
            })
        
       
        
    def update_ui(self):
        
        for char, nodes in self.ui_nodes.items():
            hp_node = nodes.get('hp')
            if hp_node:
                hp_node.text = f"{getattr(self, f'{char}_hp', 0)} / {getattr(self, f'{char}_hp_max', 0)}"
                if self.knight_turn:
                    hp_node.opacity = 0.85
                else:
                    hp_node.opacity = 1.0

        if self.tp_node:
            if self.tp == 100: self.tp_node.text = f"MAX%"
            else: self.tp_node.text = f"{int(self.tp)}%"

        if self.knight_turn:
            if self.tp_node: self.tp_node.opacity = 0.35
            if self.tp_bar: self.tp_bar.opacity = 0.35
            if self.tp_bar_bg: self.tp_bar_bg.opacity = 0.35
        else:
            if self.tp_node: self.tp_node.opacity = 1.0
            if self.tp_bar: self.tp_bar.opacity = 1.0
            if self.tp_bar_bg: self.tp_bar_bg.opacity = 1.0
          
        
   

        self.tp_bar.scale = (30, 150 * (min(1.0, self.tp / 100)))

      
        base_y = self.tp_bar_bg.position[1] - 150*0.5 
        self.tp_bar.position = (
            self.tp_bar_bg.position[0],
            base_y + (150 * (min(1.0, self.tp / 100)) / 2.0)
        )

    def teleport_players(self):
        self.knight_actor.handlemessage(bs.StandMessage(self.knight_position, -90))
        for character in ['kris', 'susie', 'ralsei']:
            if not getattr(self, f'{character}_actor', None):
                continue
            pos = getattr(self, f'{character}_position', self.center_position)
            getattr(self, f'{character}_actor').handlemessage(bs.StandMessage((pos[0], pos[1]-1,pos[2]), 90))

    def start_turn(self):
        if self.soul_actor:
            self.soul_actor.handlemessage(bs.DieMessage(True))

        # heal kris a bit if hes downed
        if self.kris_hp <= 0:
            hp = random.randint(21, 26)
            self.kris_hp += hp
            self.play_sound('heal')
            PopupText(
                str(hp),
                position=self.kris_position,
                color=(0,1,0)
            ).autoretain()
       
        for player in self.players:
            player.actor.disconnect_controls_from_player()
        self.kris_defending = False
        self.ralsei_defending = False
        self.susie_defending = False
        self.knight_turn = False
        susiedead =self.susie_hp <= 0 and not getattr(self, 'susiedied', False) and self.susie_actor
        ralseidead= self.ralsei_hp <= 0 and not getattr(self,'ralseidied',False) and self.ralsei_actor
        krisdead = self.kris_hp <= 0 and not getattr(self, 'krisdied', False)

        self.teleport_players()
        self.update_ui()
        
        def start():
            self._process_player_turn(0)

        turn = self.turn_count+1

        def gft(str):
            return bs.gettexture(f'faces/{str}')

        def flavor_then_start(messages):
            duration = self.text_engine.display_sequence(messages)
            start()
        if self.guard_down:
            if self.hits == 0:
                flavor_then_start([
                    ("Kris coughed. The enemy slowly tilted its head...", 0.03, 'default', None),
                ])
            elif self.susie_hp <= 0 and self.susie_actor:
                flavor_then_start([
                    ("Susie struggled to give some kind of warning. ", 0.03, 'default', None),
                ])
            else:
                flavor_then_start([
                    ("The enemy suddenly let their guard down!", 0.03, 'default', None),
                ])
            bs.animate_array(self.knight_actor.node, 'color', 3, {
                    0: (1, 1, 1),
                    1.21: (0, 0, 0)
                })
            return
        elif self.phase_2:
            flavor_then_start([
                ("The Knight's hands glow a strange color...", 0.03, 'default', None),
            ])
            return
        elif self.knight_hp <= 6200 and not getattr(self, 'lowhpknight', False) and self.susie_actor:
            flavor_then_start([
                ("Susie grew pale.", 0.03, 'default', None),
            ])
            self.lowhpknight = True
            return
        

        
        elif susiedead or ralseidead or krisdead:
            text = ''
            text += "Kris kneeled in silence.\n" if krisdead else ''
            text += "Susie was hurt and beaten.\n" if susiedead else ''
            text +="Ralsei became a pile of fluff." if ralseidead else ''
            flavor_then_start([
                (text, 0.03, 'default', None),
            ])
            if susiedead:
                self.susiedied = True
            if ralseidead:
                self.ralseidied = True
            if krisdead:
                self.krisdied = True
            return
     
     

        
        if turn == 1:
            duration = self.text_engine.display_sequence([
                    (f"The Roaring Knight appeared.", 0.03, 'default', None),
                ])
            start()
        
        elif turn == 2:
            duration = self.text_engine.display_sequence([
                    (f"You felt something hovering close behind your head... ", 0.03, 'default', None),
                ])
            start()
        elif turn == 3:
            duration = self.text_engine.display_sequence([
                    (f"Suddenly, the north wind blew fiercely.", 0.03, 'default', None),
                ])
            start()
        elif turn == 4:
            duration = self.text_engine.display_sequence([
                    (f"Your chest feels tight.", 0.03, 'default', None),
                ])
            start()
        elif turn == 5:
            duration = self.text_engine.display_sequence([
                    (f"You felt lightheaded. You saw golden stars...", 0.03, 'default', None),
                ])
            start()
        elif turn == 6:
            duration = self.text_engine.display_sequence([
                    (f"Suddenly, the north and east winds blew fiercely.", 0.03, 'default', None),
                ])
            start()
        elif turn == 7:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* Heheh...", 0.03, 'susie', gft('susface4')),
                    ("* Didn't... think we'd still be standing, did you?", 0.03, 'susie', gft('susface3')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"Your vision narrows. ... Your head is spinning.", 0.03, 'default', None),
                ])
                start()

        elif turn == 8:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* Thing is, you actually..", 0.03, 'susie', gft('susface32')),
                    ("* You actually messed up, picking a fight with US!", 0.03, 'susie', gft('susface34')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"You feel surrounded.", 0.03, 'default', None),
                ])
                start()

        elif turn == 9:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* You? You're all alone...", 0.03, 'susie', gft('susface32')),
                    ("* Me? I got... Kris and Ralsei behind me.", 0.03, 'susie', gft('susface33')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"You felt your chest twisting.", 0.03, 'default', None),
                ])
                start()

        elif turn == 10:
            if not self.susie_hp <= 0 and self.susie_actor:
                
                if self.kris_hp <= 0 and self.ralsei_hp <= 0:
                    duration = self.text_engine.display_sequence([
                        ("* As long as I'm here to lift them back up...", 0.03, 'susie', gft('susface29')),
                        ("* Heh... you're never gonna win, you hear me?!", 0.03, 'susie', gft('susface3')),
                    ])
                else:
                    duration = self.text_engine.display_sequence([
                        ("* Even... even if you knock me down...", 0.03, 'susie', gft('susface28')),
                        ("* As long as Kris, Ralsei, are here...", 0.03, 'susie', gft('susface29')),
                        ("* As long as Kris has got a hand to lift me up with...", 0.03, 'susie', gft('susface29')),
                        ("* Heh... you're never gonna win, you hear me?!", 0.03, 'susie', gft('susface3')),
                    ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"You felt lightheaded. You felt a migraine coming on...", 0.03, 'default', None),
                ])
                start()

        elif turn == 11:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* So... give up.", 0.03, 'susie', gft('susface40')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"Suddenly, a tempest.", 0.03, 'default', None),
                ])
                start()

        elif turn == 12:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* You know you can't win... so... give up!", 0.03, 'susie', gft('susface39')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"Your vision narrows. ... The world revolves around you.", 0.03, 'default', None),
                ])
                start()

        elif turn == 13:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* ... You won't even..", 0.03, 'susie', gft('susface32')),
                    ("* ... say a thing, huh...", 0.03, 'susie', gft('susface33')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"You feel cornered.", 0.03, 'default', None),
                ])
                start()

        elif turn == 14:
            if not self.susie_hp <= 0 and self.susie_actor:
                duration = self.text_engine.display_sequence([
                    ("* ... heh ... heheheh...", 0.03, 'susie', gft('susface33')),
                    ("* Man, I'm done talking,", 0.03, 'susie', gft('susface33')),
                    ("* ... people like you... just piss me off.", 0.03, 'susie', gft('susface34')),
                ])
                bs.timer(duration, start)
            else:
                self.text_engine.display_sequence([
                    (f"Your heartbeat becomes twisted.", 0.03, 'default', None),
                ])
                	
                start()
        else:
            start()
  
    
    def _process_player_turn(self, index: int):

        # nah, downing can handle allat
        #if all(getattr(self, f"{self.get_name_from_player(p)}_hp") <= 0 for p in self.players):
        #    self.show_game_over()
        #    return
        
        self.teleport_players()
        limit = len(self.players) if len(self.players) != 1 else 3
        if index >= limit:
            bs.timer(1.0, self._enemy_turn)
            return
        

        
        if len(self.players) == 1:
            input_target = self.players[0]
        else:
            input_target = self.players[index % len(self.players)]
        self.turn = index + 1

        

        # player dedad
        if getattr(self, f"{self.get_current_name()}_hp") <= 0:
            self._process_player_turn(index + 1)
            return

        current_menu = self.inventory[self.get_current_name()]
        self._handle_menu(input_target, current_menu, index)


    def _handle_menu(self, player: bs.Player, menu: dict, player_index: int):
        # Ok so basically, 
        # Will have 4 text on the character and 
        # will use bs.InputType to go through the menus.

        # What it returns:
        # True: start next turn.
        # dict: another menu
        # None: dont render text + dont do anything
        # False: dont do anything + play an error when selected
        # tuple: (timer, next_action)

        self.option_nodes = []
        current_char_actor = self.get_current_actor()

        for key, value in menu.items():
            if isinstance(value, dict) and 'name' in value:
                label = value['name']
            else:
                label = ''

            x_off, y_off, z_off = 0.0, -1, 0.0
            color = (1, 1, 1)

            if key == bs.InputType.PUNCH_PRESS:
                x_off = -1
                y_off = 0
                color = (0.3, 1, 0.3)  
            elif key == bs.InputType.BOMB_PRESS:
                x_off = 1.0
                y_off = 0
                color = (1, 0.3, 0.3)
            elif key == bs.InputType.JUMP_PRESS:
                y_off = -1
                color = (1, 1, 0.3)  
            elif key == bs.InputType.PICK_UP_PRESS:
                y_off = 1.5
                color = (0.3, 0.6, 1)

            node = bs.newnode(
                'text',
                attrs={
                    'text': label,
                    'in_world': True,
                    'position': (
                        current_char_actor.node.position[0] + x_off,
                        current_char_actor.node.position[1] + y_off,
                        current_char_actor.node.position[2] + z_off
                    ),
                    'scale': 0.012,
                    'color': color,
                    'shadow': 0.5,
                    'flatness': 1.0,
                    'h_align': 'center',
                }
            )
            self.option_nodes.append(node)


        def make_handler(action):
            def handler():

                self.play_sound('select')
                player.resetinput()

                for n in  self.option_nodes:
                    if n: n.delete()

                result = action() if callable(action) else action
                
                if isinstance(result, tuple) and len(result) == 2:
                    duration, next_step = result
                    
                    if duration is None:
                        duration = 1.0
                        
                    if next_step is True:
                        bs.timer(duration, bs.Call(self._process_player_turn, player_index + 1))

                elif result is True:
                    self._process_player_turn(player_index + 1)

                elif isinstance(result, dict):
                    self._handle_menu(player, result, player_index)

                elif result is False:
                    bs.getsound('error').play()
                    self._handle_menu(player, menu, player_index)

                elif result is None:
                    # reopen the menu
                    self._handle_menu(player, menu, player_index)
            return handler

        for key, value in menu.items():
            if isinstance(value, dict) and 'action' in value:
                player.assigninput(key, make_handler(value['action']))
            elif callable(value):
                player.assigninput(key, make_handler(value))
            else:
                pass


    
    def _enemy_turn(self):
        self.knight_turn = True
        self.update_ui()
        self.text_engine.clear()
        self.i_frames = {
            'kris': 0.0,
            'susie': 0.0,
            'ralsei': 0.0
        }
        if len(self.players) == 1:
            # Erm actually make a soul lo
                self.soul_actor = Spaz(color=(1, 0, 0.0),character='Empty', source_player= self.players[0]).    autoretain()
                self.soul_actor.handlemessage(bs.StandMessage(self.center_position))
                models = self.models['soul']
                self.soul_actor.node.head_mesh = models['head_mesh']
                self.soul_actor.node.torso_mesh = models['torso_mesh']
                self.soul_actor.node.pelvis_mesh = models['pelvis_mesh']
                self.soul_actor.node.upper_arm_mesh = models['upper_arm_mesh']
                self.soul_actor.node.forearm_mesh = models['forearm_mesh']
                self.soul_actor.node.hand_mesh = models['hand_mesh']
                self.soul_actor.node.upper_leg_mesh = models['upper_leg_mesh']
                self.soul_actor.node.lower_leg_mesh = models['lower_leg_mesh']
                self.soul_actor.node.toes_mesh = models['toes_mesh']
                self.soul_actor.node.is_area_of_interest = True
                self.players[0].resetinput()
                self.players[0].assigninput(bs.InputType.LEFT_RIGHT, self.soul_actor.on_move_left_right)
                self.players[0].assigninput(bs.InputType.UP_DOWN, self.soul_actor.on_move_up_down)
                self.players[0].assigninput(bs.InputType.RUN, self.soul_actor.on_run)
                    
                
        else:
       
            for player in self.players:
                
                if not getattr(self, f'{self.get_name_from_player(player)}_hp', 0) <= 0:
                    player.actor.handlemessage(bs.StandMessage(self.center_position))
                    player.actor.connect_controls_to_player(
                            enable_jump=False,
                            enable_punch = False,
                            enable_pickup = False,
                            enable_bomb = False,
                            enable_run = True,
                    )
        pattern_index = self.turn_count % len(self.attack_pattern)
        current_attack_class = self.attack_pattern[pattern_index]
        self.turn_count += 1
        if self.guard_down:
            bs.timer(1, self.start_turn)
            return
        if self.knight_hp <= 6000 and not self.phase_2:
            bs.animate_array(
                self.knight_actor.node, 'color', 3, {
                    0: (0, 0, 0),
                    1.21: (10, 10, 10)
                }
            )
            self.knight_actor.handlemessage(bs.CelebrateMessage(5))
            self.phase_2 = True
            self.start_turn()

      
            return

            
        

        if not self.phase_2:
            current_attack_class(self)
        else:
            KnightFinalAttack(self)
    
    def get_main_inventory(self):
        return self.inventory[self.get_current_name()]
        
       
            
    def get_current_actor(self) -> Spaz:
        return getattr(self, f'{self.get_current_name()}_actor', None)

    def get_current_name(self):
        return ['kris', 'susie', 'ralsei'][self.turn-1]
    
    def get_name_from_player(self, player: bs.Player):
        try:
            if player is self.players[0]:
                return 'kris'
                
            if player is self.players[1]:
                return 'susie'
             
            if player is self.players[2]:
                return 'ralsei'
          
        except Exception as e:
            return None
       
       

    def attack(self):
        actor = self.get_current_actor()
        if self.turn == 1:
            damage = int(18 * random.uniform(1.1, 0.9))
            # double for how many are dead
            if not self.susie_actor and not self.ralsei_actor:
                damage *= 6
            if self.ralsei_hp <= 0:
                damage *= 2
            if self.susie_hp <= 0:
                damage *= 2
        if self.turn == 2:
            damage = int(50 * random.uniform(1.1, 0.9))
        if self.turn == 3:
            damage = int(30 * random.uniform(1.1, 0.9))
        actor.node.punch_pressed = True
        actor.node.punch_pressed = False
        if self.phase_2 and not self.guard_down:
            damage  *= 0
        if self.guard_down:
            damage *= 61
        damage = int(damage)
        self.tp =  min(100, self.tp + 4)

        PopupText(
            str(damage),
            position=self.knight_position,
            color=babase.normalized_color(actor.Dcolor)
        ).autoretain()
        self.play_sound('attack')
        self.play_sound(
            'knighthurt' + str(random.randint(1, 2))
        )
        self.knight_hp -= damage
        self.update_ui()
        if not self.guard_down:
            return True
        else:
            self.won()
            return {}


    def defend(self):
        setattr(self, f'{self.get_current_name()}_defending', True)
        self.tp =  min(100, self.tp + 16)
        self.update_ui()
        self.get_current_actor().handlemessage(bs.CelebrateMessage(0.2))
        return True
    
  
    def won(self):
        bs.setmusic(None)
        bs.app.classic.ach.award_local_achievement('Roaring')
        for p in self.players:
            p.resetinput()
        for char, nodes in self.ui_nodes.items():
            hp_node = nodes.get('hp')
            if hp_node:
                hp_node.delete()

        self.tp_node.delete()
        self.text_engine.clear()
        self.tp_bar.delete()
        self.tp_bar_bg.delete()

        for node in self.option_nodes:
                node.delete()
        

    
        self.knight_actor.node.handlemessage('knockout', 2500)
        n=bs.newnode('image', attrs={
            'texture': bs.gettexture('white'),
            'fill_screen': True,
            'color': (1, 1, 1),
        })
        bs.animate(n, 'opacity', {  
            0: 0,
            2.5: 1.0
        })
        bs.timer(2.5, self.end_game)


    def return_act_menu(self):
        def gft(str):
            return bs.gettexture(f'faces/{str}')

        def do_check():

            if not self.kris_checked:
                self.get_current_actor().node.punch_pressed = True
                self.get_current_actor().node.punch_pressed = False
                duration = self.text_engine.display_sequence([
                    (f"Kris analyzed the enemy!", 0.03, 'default', None),
                    (f"But they couldn't learn anything.", 0.03, 'default', None)
                ])
            else:
                duration = self.text_engine.display_sequence([
                    (f"Kris points into the distance. ", 0.03, 'default', None),
                    (f"Nothing happened.", 0.03, 'default', None)
                ])
            self.kris_checked = True
            return (duration, True)
        def s_check():
            self.get_current_actor().node.punch_pressed = True
            self.get_current_actor().node.punch_pressed = False
            self.suise_talked = True
            duration = self.text_engine.display_sequence([
                (f"Susie talked to the Knight!", 0.03, "default", None),
                (f"* I don't know what the hell you are, but...", 0.03, 'susie', gft('susface20')),
                (f"* Leave Toriel alone! You hear me!?", 0.03, 'susie', gft('susface19')),
                (f"* ...", 0.5, 'susie', gft('susface20')),
                (f"* ... Fine, you don't wanna listen?", 0.03, 'susie', gft('susface19')),
                (f"* Then we'll just... Have to do things the hard way.", 0.03, 'susie', gft('susface14')),
                (f"(Susie will not ACT any more.)", 0.03, 'default', None),
                
            ])
            return (duration, True)

        def r_check():
            self.get_current_actor().node.punch_pressed = True
            self.get_current_actor().node.punch_pressed = False
            if not self.ralsei_talked:
            
                duration = self.text_engine.display_sequence([
                    ("Ralsei tried talking...", 0.03, 'default', None),
                    (f"* Please... please don't do this...", 0.03, 'ralsei',  gft('ralface3')),
                    (f"* If the Roaring happens, then... then...", 0.03, 'ralsei', gft('ralface1')),
                    (f"* Please... stop...!", 0.03, 'ralsei', gft('ralface2')),
                    (f"(... but nothing happened.)", 0.03, 'default', None),
                    
                ])
            else:
                duration = self.text_engine.display_sequence([
                    ("Ralsei tried talking...", 0.03, 'default', None),
                    (f"* Please, stop...", 0.03, 'ralsei', gft('ralface2')),
                    (f"(... but nothing happened.)", 0.03, 'default', None),
                    
                ])
            self.ralsei_talked = True
            return (duration, True)
        
        def rude_buster():
            actor = self.susie_actor
            damage = int(140 * random.uniform(1.2, 0.8))
            actor.node.punch_pressed = True
            actor.node.punch_pressed = False
            self.tp -= 50

            
            self.play_sound('buster_swing')
            def hit():
                PopupText(
                    str(damage),
                    position=self.knight_position,
                    color=babase.normalized_color(actor.Dcolor)
                ).autoretain()
                self.play_sound('buster_hit')

                self.play_sound(
                    'knighthurt' + str(random.randint(1, 2))
                )
                self.knight_hp -= damage
                self.update_ui()
            bs.timer(0.2, hit)
            return True
        
        def heal(healing, tp_removal, character):
            def heal_target(char_name, healing, character):
                self.play_sound('heal')
                current_hp = getattr(self, f'{char_name}_hp', 0)
                max_hp = getattr(self, f'{char_name}_hp_max', 0)

                if healing == 'revive':
                    setattr(self, f'{char_name}_hp', max_hp)
                    PopupText('MAX', position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
                else:
                    new_hp = min(current_hp + healing, max_hp)
                    setattr(self, f'{char_name}_hp', new_hp)
                    if new_hp >= max_hp:
                        PopupText('MAX', position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
                    else:
                        PopupText(str(healing), position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
                self.update_ui()
                duration = 0.1
                if character == 'susie':
                    duration = self.text_engine.display_sequence([
                        (f"Susie casts ULTIMATE HEAL!!", 0.03, 'default', None),
                    ])

                elif character == 'ralsei':
                    duration = self.text_engine.display_sequence([
                        (f"Ralsei casts Healing Prayer!", 0.03, 'default', None),
                    ])
                
                

                return (duration, True)
            
            

            self.tp = tp_removal
            
            target_players = [self.get_name_from_player(p) for p in self.players if getattr(self, f'{self.get_name_from_player(p)}_hp', 0) > 0] if len(self.players) != 1 else [c for c in ['kris', 'susie', 'ralsei'] if getattr(self, f'{c}_hp', 0) > 0]

           
            def select_target_menu():
                    menu = {}
                    for p in target_players:
                        menu[
                            bs.InputType.PUNCH_PRESS if p == 'kris'
                            else bs.InputType.BOMB_PRESS if p == 'susie'
                            else bs.InputType.JUMP_PRESS
                        ] = {
                            'name': p.capitalize(),
                            'action': lambda char_name=p, character=character: heal_target(char_name, healing, character=character)
                        }
                        menu[bs.InputType.PICK_UP_PRESS] = {
                            'name': 'Back',
                            'action': self.get_main_inventory()
                        }
                    return menu
            return select_target_menu()

        
        

        if self.turn == 1:
            return {
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'Check',
                    'action': do_check
                },
                bs.InputType.BOMB_PRESS: {
                    'name': 'Back',
                    'action': self.get_main_inventory()
                } 
            
            }
        elif self.turn == 2:
            
            return {
                bs.InputType.PUNCH_PRESS: {
                    'name': 'Rude Buster\n50% TP',
                    'action': (rude_buster if self.tp >= 50 else False)
                },
                bs.InputType.JUMP_PRESS:  {
                    'name': 'S-Action',
                    'action': (False if self.suise_talked else s_check)
                },
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'ULTIMATE\nHEALING!!\n100% TP',
                    'action': (bs.Call(heal, random.randint(21, 29), 100, 'susie') if self.tp >= 100 else False)
                } ,
                 bs.InputType.BOMB_PRESS: {
                    'name': 'Back',
                    'action': self.get_main_inventory()
                } 
            }
            
        elif self.turn == 3:
            def pacify():
                duration = self.text_engine.display_sequence([
                    ("Ralsei tried to pacify the enemy...", 0.03, 'default', None),
                    (f"But the enemy wasnt TIRED.", 0.03, 'default', None),
                    
                ])
                self.tp -= 16
                self.update_ui()
                self.get_current_actor().handlemessage(bs.CelebrateMessage(duration*0.5))
                return (duration, True)
            return {
                bs.InputType.PUNCH_PRESS: {
                    'name': 'Healing Prayer\n32% TP',
                    'action': (bs.Call(heal, random.randint(100, 123), 32, 'ralsei') if self.tp >= 32 else False)
                },
                bs.InputType.JUMP_PRESS: {
                    'name': 'R-Action',
                    'action': r_check
                },
                bs.InputType.PICK_UP_PRESS: {
                    'name': 'Pacify\n16% TP',
                    'action': (pacify if self.tp >= 16 else False)
                },
                 bs.InputType.BOMB_PRESS: {
                    'name': 'Back',
                    'action': self.get_main_inventory()
                } 
            }
            
    
    def return_item_menu(self):
        if (not self.group_heals and
        not self.medium_heals and
        not  self.large_heals and
        not self.revive_mints):
            return False
        
        def heal_target(char_name, healing):
            self.play_sound('heal')
            current_hp = getattr(self, f'{char_name}_hp', 0)
            max_hp = getattr(self, f'{char_name}_hp_max', 0)

            if healing == 'revive':
                setattr(self, f'{char_name}_hp', max_hp)
                PopupText('MAX', position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
            else:
                new_hp = min(current_hp + healing, max_hp)
                setattr(self, f'{char_name}_hp', new_hp)
                if new_hp >= max_hp:
                    PopupText('MAX', position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
                else:
                    PopupText(str(healing), position=getattr(self, f'{char_name}_position'), color=(0,1,0)).autoretain()
            self.update_ui()
           
            return True

        def heal(healing):
            group = False
            if healing == 'revive':
                self.revive_mints -= 1
            elif healing == 'large':
                self.large_heals -= 1
                healing =  140
            elif healing == 'medium':
                self.medium_heals -= 1
                healing = 100
            elif healing == 'small':
                group = True
                self.group_heals -= 1
                healing = 70

           
            if len(self.players) != 1:
                if healing == 'revive':
                    target_players =  [self.get_name_from_player(p) for p in self.players]
                else:
                    target_players = [self.get_name_from_player(p) for p in self.players if getattr(self, f'{self.get_name_from_player(p)}_hp', 0) > 0]
            else:
                if healing == 'revive':
                    target_players = ['kris', 'susie', 'ralsei']
                else:  
                    target_players = [c for c in ['kris', 'susie', 'ralsei'] if getattr(self, f'{c}_hp', 0) > 0]
            
            if group:
                for c in target_players:
                    hp_attr = f'{c}_hp'
                    current = getattr(self, hp_attr, 0)

                    if current != -999: 
                        heal_target(c, healing)

                return True
    
            def select_target_menu():
                    menu = {}
                    for p in target_players:
                        menu[
                            bs.InputType.PUNCH_PRESS if p == 'kris'
                            else bs.InputType.BOMB_PRESS if p == 'susie'
                            else bs.InputType.JUMP_PRESS
                        ] = {
                            'name': p.capitalize(),
                            'action': lambda char_name=p: heal_target(char_name, healing)
                        }
                        menu[bs.InputType.PICK_UP_PRESS] = {
                            'name': 'Back',
                            'action': self.get_main_inventory()
                        }
                    return menu
            return select_target_menu()


        return {
                bs.InputType.BOMB_PRESS:(None if not self.large_heals else {
                    'name': f'Deluxe Dinner\nx{self.large_heals}',
                    'action': bs.Call(heal,'large')
                }),
                bs.InputType.JUMP_PRESS:(None if not self.revive_mints else {
                    'name': f'Revive Mint x{self.revive_mints}',
                    'action': bs.Call(heal,'revive')
                }),
                bs.InputType.PUNCH_PRESS: (None if not self.group_heals else {
                    'name': f'Club Sandwich\nx{self.group_heals}',
                    'action': bs.Call(heal,'small')
                }),
                bs.InputType.PICK_UP_PRESS:(None if not self.medium_heals else {
                    'name': f'TV Dinner x{self.medium_heals}',
                    'action': bs.Call(heal,'medium')
                }),
            }
    def on_expire(self):

        super().on_expire()
        # yes i remember to clear everything after lmfao
        self.inventory = []
        self.text_engine = None
        self.kris_actor = None
        self.susie_actor = None
        self.ralsei_actor = None
        self.kris_downed_prop: bs.Actor = None
        self.susie_downed_prop: bs.Actor = None
        self.ralsei_downed_prop: bs.Actor = None
        self.ui_nodes = {}
        if self.scene:
            self.scene.handlemessage(bs.DieMessage(True))

    def hurt(self, _damage: int, character: str, force: bool = False):

        if getattr(self, f'{character}_hp', 0) <= 0:
            return

        current_time = bs.time()
        if current_time < self.i_frames.get(character, 0.0):
            return
        
        invincible_time = 1.5
        damage = _damage

        if getattr(self, f'{character}_hp', 0) <= 0:
            return

        # Oh wait, were in single player, hurt someone else
        if len(self.players) == 1 and not force:
            
            self.hurt(_damage, random.choice(['kris', 'susie', 'ralsei']), True)
            return
        


        

        if (character == 'kris' and len(self.players) == 1) or len(self.players) != 1:
            
            self.hits += 1


        if character == 'kris':
            # less damage because right hand man
            damage = int(damage * 0.8)

        if getattr(self, f'{character}_defending', False):
            damage = int(damage * 0.66)


        self.i_frames[character] = current_time + invincible_time
        actor = getattr(self, f'{character}_actor', Spaz)
        actor.node.invincible = True
        bs.timer(invincible_time, bs.Call(setattr, actor.node, 'invincible', False))
        # Check if they have an active soul, then animate it
        if self.scene:
            for actor in self.scene.connected_actors:
                if isinstance(actor, ScenePlayer):

                    if self.get_name_from_player(actor.player) == character:
                            n=bs.animate(
                                actor.node, 'opacity', {
                                    0.0: 0.5,
                                    0.1: 1.0,
                                    0.2: 0.5,
                                    0.3: 1.0,
                                    0.4: 0.5,

                                }, loop=True

                            )
                            bs.timer(invincible_time,n.delete)

        PopupText(
            text=str(damage),
            position=getattr(self, f'{character}_actor', Spaz).node.position,
            color=(1,1,1)
        ).autoretain()
        self.play_sound('hurt')
        setattr(self, f'{character}_hp', getattr(self, f'{character}_hp', 0)-damage)
        self.update_ui()

        if getattr(self, f'{character}_hp', 0) <= 0:
            self._down_character(character)

    def _down_character(self, character: str):
        actor = getattr(self, f'{character}_actor', None)
        pos =getattr(self, f'{character}_position', None)
        actor.handlemessage(bs.StandMessage((pos[0],pos[1]-0.5,pos[2]), 90))


        # Check if they have an active soul, then delete it.
        
        # Also, dont delete it if theyre the only one alive in single player, because its the final attack
        # and like... it wont breka lol
        if self.scene and not len(self.players) == 1:
            for actor in self.scene.connected_actors:
                if isinstance(actor, ScenePlayer):

                    if self.get_name_from_player(actor.player) == character:
                            actor.handlemessage(bs.DieMessage())
        

        # If the character is susie or ralsei, swoon.
        if actor is self.susie_actor or actor is self.ralsei_actor:
            setattr(self, f'{character}_hp', -999)
            PopupText(
                'SWOON', 
                position=getattr(self, f'{character}_position', None), 
                color=(1,0,0), 
                random_offset=0
            ).autoretain()
            self.play_sound(f'swoon{random.randint(1,2)}')
        else:
            PopupText(
                'DOWN', 
                position=getattr(self, f'{character}_position', None), 
                color=(1,0,0), 
                random_offset=0
            ).autoretain()
        
        
        # Spawn a prop in their location
        setattr(self, f'{character}_downed_prop', bs.newnode(
            'prop',
            attrs={
                    'position': getattr(self, f'{character}_position'),
                    'velocity': (-0.2,0.2,0),
                    'mesh': self.models[character]['down_prop'],
                    'light_mesh': None,
                    'body': 'box',
                    'body_scale': 0.8,
                    'shadow_size': 0.44,
                    'color_texture': self.models[character]['prop_texture'],
                    'reflection': 'powerup',
                    'reflection_scale': [0.0],
                    'materials': [self.non_collide_mat],
                },
        ))
        


    @override
    def spawn_player(self, player: bs.Player):
       
        try:
           
           
            if player is self.players[0]:
                player.character = 'Kris'
                player.color = bs.app.classic.spaz_appearances[player.character].default_color
                player.highlight = bs.app.classic.spaz_appearances[player.character].default_highlight
                spawn = self.kris_position
                spaz = self.spawn_player_spaz(player, spawn, 90)
                self.kris_actor = spaz
                l=bs.newnode('light', attrs={
                    'color': self.kris_actor.Dcolor, 
                    'radius': 0.1, 
                    'intensity': 1.0,
                    'volume_intensity_scale': 1.0
                })
                self.ralsei_actor .node.connectattr('position', l, 'position')
            if player is self.players[1]:
                player.character = 'Susie'
                # im lazy as fuck lmfao
                player.color = bs.app.classic.spaz_appearances[player.character].default_color
                player.highlight = bs.app.classic.spaz_appearances[player.character].default_highlight
                spawn = self.susie_position
                spaz = self.spawn_player_spaz(player, spawn, 90)
                self.susie_actor = spaz
                l=bs.newnode('light', attrs={
                    'color': self.susie_actor.Dcolor, 
                    'radius': 0.1, 
                    'intensity': 1.0,
                    'volume_intensity_scale': 1.0
                })
                self.susie_actor .node.connectattr('position', l, 'position')
            if player is self.players[2]:
                player.character = 'Ralsei'
                player.color = bs.app.classic.spaz_appearances[player.character].default_color
                player.highlight = bs.app.classic.spaz_appearances[player.character].default_highlight
                spawn = self.ralsei_position
                spaz = self.spawn_player_spaz(player, spawn, 90)
                self.ralsei_actor = spaz
                l=bs.newnode('light', attrs={
                    'color': self.ralsei_actor.Dcolor, 
                    'radius': 0.15, 
                    'intensity': 1.0,
                    'volume_intensity_scale': 1.0
                })
                self.ralsei_actor .node.connectattr('position', l, 'position')
        except Exception as e:
            return None
        
        

    
        return spaz



    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        
        return super().handlemessage(msg)
        return None

    @override
    def end_game(self) -> None:
       
        self.session.return_to_main_menu()
    
    # Game over

    def show_game_over(self):
        if self.gameover:
            return
        self.knight_turn = False
        self.gameover = True
        self.session.max_players = 3
        self.session.minimum = 0
        bs.setmusic(None)
        
        # Disable players
        for player in self.players:
            try: player.actor.disconnect_controls_from_player()
            except: pass

        self.text_engine.clear()

        bs.newnode('image', attrs={
            'texture': bs.gettexture('white'),
            'fill_screen': True,
            'color': (0, 0, 0),
        })

        self.game_over_heart = bs.newnode('text', attrs={
            'text': f'{babase.charstr(babase.SpecialChar.HEART)}',
            'position': (0, 0),
            'scale': 3.0,
            'color': (1, 0, 0),
            'h_align': 'center',
            'v_align': 'center',
            'flatness': 1.0,
        })

        bs.getsound('knight/hero_hurt').play()
        
        for i in range(10):
            offset = (random.uniform(-5, 5), random.uniform(-5, 5))
            bs.timer(0.05 * i, bs.Call(setattr, self.game_over_heart, 'position', (offset[0], offset[1])))

        bs.timer(1.0, self._break_heart)

    def _break_heart(self):
        if self.game_over_heart.exists():
            self.game_over_heart.delete()
        
   

  
        p1 = bs.newnode('text', attrs={
            'text': '/', 'scale': 3.5, 'color': (1, 0, 0),
            'h_align': 'center', 'v_align': 'center', 'position': (-5, 0)
        })
        # Piece 2 (Right)
        p2 = bs.newnode('text', attrs={
            'text': '>', 'scale': 3.5, 'color': (1, 0, 0),
            'h_align': 'center', 'v_align': 'center', 'position': (5, 0)
        })

        for p, side in [(p1, -1), (p2, 1)]:
            bs.animate(p, 'opacity', {0.0: 1.0, 1.5: 0.0})
            bs.animate_array(p, 'position', 2, {
                0.0: (5 * side, 0),
                0.5: (40 * side, 20),
                1.5: (80 * side, -200)
            })
            bs.timer(1.6, p.delete)

        bs.timer(1.5, self._show_game_over_text)

    def _show_game_over_text(self):
        bs.newnode('sound', attrs={
            'sound': bs.getsound('AUDIO_DRONE'),
            'music': True, 'volume': 1.5
        })
        self.game_over_text = bs.newnode('text', attrs={
            'text': 'GAME OVER',
            'position': (0, 0),
            'scale': 2.0,
            'color': (1, 1, 1),
            'h_align': 'center',
            'v_align': 'center',
            'flatness': 1.0,
            'opacity': 0.0
        })
        bs.animate(self.game_over_text, 'opacity', {0.0: 0.0, 2.0: 1.0})
        
        self.menu_options = ['RESTART', 'GIVE UP']
        self.menu_index = 0 
        
        self.opt_restart = bs.newnode('text', attrs={
            'text': 'RESTART', 'position': (-120, -100),
            'scale': 1.2, 'color': (1, 1, 0),
            'h_align': 'center', 'v_align': 'center'
        })
        
        self.opt_giveup = bs.newnode('text', attrs={
            'text': 'GIVE UP', 'position': (120, -100),
            'scale': 1.2, 'color': (1, 1, 1),
            'h_align': 'center', 'v_align': 'center'
        })

        self.selector_heart = bs.newnode('text', attrs={
            'text': f'{babase.charstr(babase.SpecialChar.HEART)}', 'scale': 1.5, 'color': (1, 0, 0),
            'h_align': 'center', 'v_align': 'center',
            'position': (-210, -100)
        })
        self.can_select = True


        def do():
            try:
                p = self.players[0]
        
                p.assigninput(bs.InputType.LEFT_PRESS, bs.Call(self.update_menu_selection, -1))
                p.assigninput(bs.InputType.RIGHT_PRESS, bs.Call(self.update_menu_selection, 1))
                p.assigninput((bs.InputType.BOMB_PRESS,bs.InputType.PUNCH_PRESS, bs.InputType.PICK_UP_PRESS, bs.InputType.JUMP_PRESS), self.accept_selection)
                
            except:
                pass
        bs.timer(0.1, do, repeat=True)
     

    def update_menu_selection(self, direction: int):
        if not self.can_select:
            return

        self.menu_index = (self.menu_index + direction) % 2
        
        bs.getsound('knight/snd_menumove').play()

        target_x = -210 if self.menu_index == 0 else 50
        bs.animate_array(self.selector_heart, 'position', 2, {
            0: self.selector_heart.position,
            0.1: (target_x, -100)
        })
        self.opt_giveup.color = (1,1,1)
        self.opt_restart.color = (1,1,1)
        if self.menu_index: self.opt_giveup.color = (1,1,0)
        else: self.opt_restart.color = (1,1,0)


    def accept_selection(self):
        if not self.can_select:
            return
        
        self.can_select = False
        bs.getsound('knight/menu_sel').play()

        
        if self.menu_index == 0:
            self.session.restart_game() 
        else:
            self.end_game()


class Pellet(bs.Actor):
    def __init__(self, damage: int = 100, size: float = 1.0, delete_on_collision: bool = False):
        super().__init__()
        self.node: bs.NodeVisualizer = bs.newnode(
            'shield',
            attrs={'color': (1,1,1), 'radius': size},
        )
        self.move_timer: bs.Timer = None
        self.radius = size
        self.damage = damage
        self.delete_on_collision = delete_on_collision
        bs.timer(0.5, self.start)
        self.grazed_players = set()

    def start(self):
        if self.is_alive():
            
            self.tick_timer = bs.Timer(0.1, self.tick, repeat=True)

    def is_alive(self):
        return bool(self.node)
    def exists(self):
        return self.node.exists()
    
    def tick(self):
        #  check guys and damge them with
        # self.getactivity().hurt
        if not self.is_alive():
            return
        
        for player in self.getactivity().players:
            actor = player.actor
            if actor and actor.node.exists():
                dist = ((actor.node.position[0]-self.node.position[0])**2 +
                        (actor.node.position[1]-self.node.position[1])**2 +
                        (actor.node.position[2]-self.node.position[2])**2)**0.5
                if dist < self.radius: 
                    char_name = self.getactivity().get_name_from_player(player)
                    final_dmg = self.damage
                    final_dmg = int(final_dmg)
                    
                    self.getactivity().hurt(final_dmg, char_name)
                    if self.delete_on_collision:
                        self.handlemessage(bs.DieMessage())
                        return
                elif dist < self.radius*2.0: 
                  
                    if player not in self.grazed_players:
                        self.getactivity().tp = min(100, self.getactivity().tp + 1)
                        self.getactivity().update_ui()
                        self.grazed_players.add(player)
        # Also, check the soul i guess
        actor = self.getactivity().soul_actor
        char_name = 'kris'
        if actor and actor.node.exists():
                dist = ((actor.node.position[0]-self.node.position[0])**2 +
                        (actor.node.position[1]-self.node.position[1])**2 +
                        (actor.node.position[2]-self.node.position[2])**2)**0.5
                if dist < self.radius: 
                    char_name = self.getactivity().get_name_from_player(player)
                    final_dmg = self.damage
                    final_dmg = int(final_dmg)
                    
                    self.getactivity().hurt(final_dmg, char_name)
                    if self.delete_on_collision:
                        self.handlemessage(bs.DieMessage())
                        return
                elif dist < self.radius*2.0: 
                  
                    if player not in self.grazed_players:
                        self.getactivity().tp = min(100, self.getactivity().tp + 1)
                        self.getactivity().update_ui()
                        self.grazed_players.add(player)
        
                    
            
        

    def on_expire(self):
        super().on_expire()
        self.node.delete()
        self.tick_timer = None
        self.grazed_players = None
        self.move_timer = None


    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
            self.tick_timer = None
            self.move_timer = None
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)

class TwoDPellet(bs.Actor):
    def __init__(self, damage: int = 100, size: float = 1.0, delete_on_collision: bool = False):
        super().__init__() 
        self.node: bs.NodeVisualizer = bs.newnode(
            'image',
            attrs={
                'texture': bs.gettexture('textClearButton'),
                'opacity': 0.5 if SHOW_HITBOXES else 0.0,
                'absolute_scale': True,
                'position': (0, 0),
                'scale': (size,size),
                'attach': 'center',
                'color': HITBOX_COLOR,
            },
        )
        self.damage = damage
        self.delete_on_collision = delete_on_collision
        self.radius = size

    
        self.start()

    def start(self):
        if self.is_alive():
            self.tick_timer = bs.Timer(0.1, self.tick, repeat=True)

    def is_alive(self):
        return bool(self.node)
    def exists(self):
        return self.node.exists()
    
    def tick(self):
        #  check guys and damge them with
        # self.getactivity().hurt
        if not self.is_alive():
            return
        
        for actor in self.getactivity().scene.connected_actors:
            if isinstance(actor, ScenePlayer):
                player = actor.player
            else:
                return
            if actor and actor.node.exists():
                dist = ((actor.node.position[0]-self.node.position[0])**2 +
                        (actor.node.position[1]-self.node.position[1])**2)**0.5
                if dist < self.radius: 
                    char_name = self.getactivity().get_name_from_player(player)
                    final_dmg = self.damage
                    final_dmg = int(final_dmg)
                    
                    self.getactivity().hurt(final_dmg, char_name)
                    if self.delete_on_collision:
                        self.handlemessage(bs.DieMessage())
                        return
              


    def on_expire(self):
        super().on_expire()
        self.node.delete()
        self.tick_timer = None
        self.move_timer = None


    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
            self.tick_timer = None
            self.move_timer = None
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)

        
class KnightAttackStars:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 5.0
        self.sound = bs.getsound('knight/attacksounds/slowed_stardrop')
        self.explode_sound = bs.getsound('knight/attacksounds/snd_explosion_firework')
        self.pellets: list[Pellet] = []
        self.spawn_timer = bs.Timer(0.2, self.spawn_wave, repeat=True)
        bs.getsound( 'knight/attacksounds/knight_powerup').play()
        bs.timer(self.duration, self.end_attack)

    def spawn_wave(self):
        num_pellets = random.randint(1, 2)
        for _ in range(num_pellets):
            x_start = 8.0
            z_start = self.activity.center_position[2] + random.uniform(-3.5, 4.2)
            y_start = 3.5
            pellet_size = random.uniform(0.2, 0.5) 
            pellet_damage = 90

            pellet = Pellet(damage=pellet_damage, size=pellet_size, delete_on_collision=False)
            pellet.node.position = (x_start, y_start, z_start)

            travel_time = random.uniform(2.0, 3.0)
            x_end = -8.0
            z_end = z_start + random.uniform(-1, 1)
            bs.animate_array(pellet.node, 'position', 3, {
                0.0: (x_start, y_start, z_start),
                travel_time: (x_end, y_start, z_end)
            })
            

            self.pellets.append(pellet)
        self.sound.play(0.5)

    def end_attack(self):
        self.spawn_timer = None

        def end():
            self.activity.start_turn()
            self.activity = None
            for pellet in self.pellets:
                pellet.handlemessage(bs.DieMessage())
        for pellet in self.pellets:
            if not pellet.is_alive():
                continue
            x_current, y_current, z_current = pellet.node.position
            x_reverse = x_current + random.uniform(1.0, 4.0)
            z_reverse = z_current + random.uniform(-0.5, 0.5)

            bs.animate_array(pellet.node, 'color', 3, {
                0.0: (1,1,1),
                0.63: (4, 0.5, 0.5)
            })

            bs.animate_array(pellet.node, 'position', 3, {
                0.0: (x_current, y_current, z_current),
                0.63: (x_reverse, y_current, z_reverse)
            })

            def explode_mini(pellet=pellet):
                if not pellet.is_alive():
                    return
                self.explode_sound.play()
                for _ in range(random.randint(1, 3)):
                    mini_size = random.uniform(0.45, 0.5)
                    mini_damage = int(pellet.damage * 0.5)
                    mini = Pellet(damage=mini_damage, size=mini_size, delete_on_collision=True)
                    mini.node.position = pellet.node.position
                    x_off = random.uniform(-55, 55)
                    z_off = random.uniform(-55, 55)
                    bs.animate_array(mini.node, 'position', 3, {
                        0.0: mini.node.position,
                        30: (mini.node.position[0]+x_off, y_current, mini.node.position[2]+z_off)
                    })
                    bs.timer(3.5, bs.Call(mini.handlemessage, bs.DieMessage()))
                pellet.handlemessage(bs.DieMessage())

            bs.timer(random.uniform(0.6, 0.8), explode_mini)
        bs.timer(5, end)


class KnightHomingAttack:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 7
        self.slash_sfx = [
            bs.getsound('knight/attacksounds/knight_slash1'),
            bs.getsound('knight/attacksounds/knight_slash2')
        ]
        self.pellets: list[Pellet] = []
        self.spawn_timer = bs.Timer(0.45, self.spawn_wave, repeat=True)
        bs.timer(self.duration, self.end_attack)

    def spawn_wave(self):
        if not self.activity: return
        
        if len(self.activity.players) != 1:
            alive_players = [p for p in self.activity.players if getattr(self.activity, f'{self.activity.get_name_from_player(p)}_hp', 0) > 0] 
            if not alive_players:
                return
            target_player = random.choice(alive_players)
            target_actor = target_player.actor
            target_pos = target_actor.node.position

            offset_radius = 3.0
            angle = random.uniform(0, 2*math.pi)
            x_start = target_pos[0] + math.cos(angle) * offset_radius
            z_start = target_pos[2] + math.sin(angle) * offset_radius
            y_start = target_pos[1]
            pellet_damage = 70

            pellet = Pellet(damage=pellet_damage, size=0.9, delete_on_collision=True)
            pellet.node.position = (x_start, y_start, z_start)
            colors = {'kris': (0, 1, 1), 'susie': (2, 0.3, 0.6), 'ralsei': (0.3, 1, 0)}
            pellet.node.color = colors[self.activity.get_name_from_player(target_player)]
        else:
            
            target_pos = self.activity.soul_actor.node.position

            offset_radius = 3.0
            angle = random.uniform(0, 2*math.pi)
            x_start = target_pos[0] + math.cos(angle) * offset_radius
            z_start = target_pos[2] + math.sin(angle) * offset_radius
            y_start = target_pos[1]
            pellet_damage = 70

            pellet = Pellet(damage=pellet_damage, size=0.9, delete_on_collision=True)
            pellet.node.position = (x_start, y_start, z_start)
            pellet.node.color = (1, 1, 1)



        self.pellets.append(pellet)

        def home_in():
            if not pellet.exists():
                return
            
            
            random.choice(self.slash_sfx).play()

            dx = target_pos[0] - pellet.node.position[0]
            dy = target_pos[1] - pellet.node.position[1]
            dz = target_pos[2] - pellet.node.position[2]
            dist = (dx**2 + dy**2 + dz**2)**0.5
            speed = 12

            if dist == 0:
                return

            vx, vy, vz = dx/dist * speed * 0.05, dy/dist * speed * 0.05, dz/dist * speed * 0.05

            def move_step():
                if not pellet.exists():
                    return
                x, y, z = pellet.node.position
                pellet.node.position = (x+vx, y+vy, z+vz)
            pellet.move_timer = bs.Timer(0.05, move_step, repeat=True)

            bs.timer(5.0, bs.Call(pellet.handlemessage, bs.DieMessage()))

        bs.timer(1.5, home_in)

    def end_attack(self):
        self.spawn_timer = None
        self.activity.start_turn()
        self.activity = None
        for pellet in self.pellets:
            pellet.handlemessage(bs.DieMessage())

class KnightSlashBurst:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 15
        self.pellets = []
        self.slash_sfx = [
            bs.getsound('knight/attacksounds/knight_slash1'),
            bs.getsound('knight/attacksounds/knight_slash2')
        ]

        bs.timer(2, self.start)
        
      
       
        
       
    def start(self):
        self.spawn()
        self.spawn_timer = bs.Timer(5.5, self.spawn, repeat=True)
        bs.timer(self.duration, self.end_attack)
    def spawn(self):
        self._spawn_burst(angle=0)
        bs.timer(3.0, bs.Call(self._spawn_burst, 90))


    def _spawn_burst(self, angle: float):

        if not self.activity: return
        random.choice(self.slash_sfx).play()
        center = self.activity.center_position
        num_pellets = 12
        spacing = 1.0
        rad = math.radians(angle)
        
        move_dir = (math.cos(rad + math.pi/2), math.sin(rad + math.pi/2))

        for i in range(num_pellets):
            offset = (i - num_pellets/2) * spacing
            p_x = center[0] + offset * math.cos(rad)
            p_z = center[2] + offset * math.sin(rad)
            
      
            red_p = Pellet(damage=150, size=0.5, delete_on_collision=False)
            self.pellets.append(red_p)
            red_p.node.position = (p_x, 3.5, p_z)
            red_p.node.color = (1, 0, 0)
            
            bs.animate(red_p.node, 'radius', {0.0: 1.0, 1.0: 1.0, 1.5: 0.0})
            bs.timer(1.5, bs.Call(red_p.handlemessage, bs.DieMessage()))

            for side in [-1, 1]:
                p = Pellet(damage=60, size=0.6, delete_on_collision=True)
                self.pellets.append(p)
                p.node.position = (p_x, 3.5, p_z)

                speed = random.uniform(0.1, 0.7)
           
                
                vx, vz = move_dir[0] * side * 0.2 * speed, move_dir[1] * side * 0.2 * speed
                
                def move(pellet=p, vel=(vx, vz)):
                    if not pellet.node.exists(): return
                    cur = pellet.node.position
                    pellet.node.position = (cur[0] + vel[0], cur[1], cur[2] + vel[1])
                
                p.move_timer = bs.Timer(0.02, move, repeat=True)
                bs.timer(2.0, bs.Call(p.handlemessage, bs.DieMessage()))

    def end_attack(self):
        self.activity.start_turn()
        self.activity = None
        for pellet in self.pellets:
            pellet.handlemessage(bs.DieMessage())

class KnightSwordWalls:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 12.0
        self.pellets = []
       
        
        self.spawn_timer = bs.Timer(1.5, self.spawn_wave, repeat=True)
        bs.timer(self.duration, self.end_attack)

    def spawn_wave(self):
        bs.getsound('knight/attacksounds/knight_teleport').play()
     
            
        num_pellets = 14
        spacing = 0.6
        start_x = 10.0 
        center_z = self.activity.center_position[2]
        
        hole_index = random.randint(2, num_pellets - 3) 
        hole_index_2 = (hole_index + 1) % num_pellets
        
        for i in range(num_pellets):
            if i == hole_index or i == hole_index_2:
                continue
                
            p_z = (i * spacing) - ((num_pellets * spacing) / 2) + center_z
            
            p = Pellet(damage=35, size=0.5, delete_on_collision=False)
            p.node.position = (start_x + random.uniform(0, 0.3), 3.5, p_z)
            p.node.color = (1, 1, 1)
            
            speed = 0.1
            
            def move_step(pellet=p, s=speed):
                if not pellet.exists(): return
                x, y, z = pellet.node.position
                pellet.node.position = (x - s, y, z)
            
            p.move_timer = bs.Timer(0.02, move_step, repeat=True)
            bs.timer(4.0, bs.Call(p.handlemessage, bs.DieMessage()))
            self.pellets.append(p)

    def end_attack(self):
        self.spawn_timer = None
        self.activity.start_turn()
        self.activity = None
        for pellet in self.pellets:
            pellet.handlemessage(bs.DieMessage())

class KnightCrossShapes:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 16.0
        self.pellets = []
        self.slash_sfx = [
            bs.getsound('knight/attacksounds/knight_slash1'),
            bs.getsound('knight/attacksounds/knight_slash2')
        ]

        
        bs.timer(3, self.start_slashing)
        
    def start_slashing(self):
        self.do_shape(0, 0, shape_type='+')

        self.tick_timer = bs.Timer(1.5, self.random_slash, repeat=True)
        bs.timer(self.duration, self.end_attack)


    def random_slash(self):
        self.do_shape(random.uniform(-2, 2), random.uniform(-2, 2), shape_type=random.choice(['+', 'X', '*']))


    def do_shape(self, offset_x: float, offset_z: float, shape_type: str = '+'):
        center = self.activity.center_position
        pos = (center[0] + offset_x, 3.5, center[2] + offset_z)

        angles = []
        if shape_type == '+': angles = [0, 90]
        elif shape_type == 'X': angles = [45, 135]
        elif shape_type == '*': angles = [0, 45, 90, 135]


        for angle in angles:
            rad = math.radians(angle)
            dir_x, dir_z = math.sin(rad), math.cos(rad)
            
            for i in range(100):
                d = (i - 50) * 0.2
                beam_pos = (pos[0] + dir_x * d, pos[1], pos[2] + dir_z * d)
    
                l = bs.newnode('locator', attrs={
                    'position': beam_pos,
                    'shape': 'box',
                    'size': (0.2, 0.2, 0.2),
                    'color': (1, 0, 0),
                    'draw_beauty': True,
                })
                
                bs.animate_array(l, 'color', 3, {
                    0.0: (1, 0, 0), 
                    0.5: (0.3, 0, 0), 
                    0.8: (1, 0, 0), 
                    1.0: (0, 0, 0)
                })
                bs.timer(1.0, l.delete)

        bs.timer(1.0, bs.Call(self._spawn_pellets, pos, angles))

    def _spawn_pellets(self, pos: tuple, angles: list[int]):
        num_per_line = 18
        random.choice(self.slash_sfx).play()

        spacing = 1.2
        
        for angle in angles:
            rad = math.radians(angle)
            dir_x = math.sin(rad)
            dir_z = math.cos(rad)

            for i in range(num_per_line):
                dist = (i - num_per_line / 2) * spacing
                p_x = pos[0] + dir_x * dist
                p_z = pos[2] + dir_z * dist
                
                p = Pellet(damage=51, size=0.6, delete_on_collision=True)
                p.node.position = (p_x, 3.5, p_z)
                p.node.color = (1, 1, 1)
                
                vx = (p_x - pos[0]) * 0.08
                vz = (p_z - pos[2]) * 0.08
                
                def move(pellet=p, vel=(vx, vz)):
                    if not pellet.node.exists(): return
                    cur = pellet.node.position
                    pellet.node.position = (cur[0] + vel[0], cur[1], cur[2] + vel[1])
                
                p.move_timer = bs.Timer(0.02, move, repeat=True)
                bs.timer(2.0, bs.Call(p.handlemessage, bs.DieMessage()))
                self.pellets.append(p)

    def end_attack(self):
        self.activity.start_turn()
        self.tick_timer =None
        self.activity = None
        for pellet in self.pellets:
            pellet.handlemessage(bs.DieMessage())

class KnightSwordWallsVariant:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 12
        self.pellets = []
        
        self.spawn_timer = bs.Timer(1.5, self.spawn_wave, repeat=True)
        bs.timer(self.duration, self.end_attack)


    def spawn_wave(self):
        if self.activity.gameover: return
        bs.getsound('knight/attacksounds/knight_teleport').play()
        num_pellets = 14
        spacing = 0.6
        center = self.activity.center_position
        
        is_top_wall = random.choice([True, False])
        
        hole_index = random.randint(3, num_pellets - 4) 
        hole_index_2 = hole_index + 1
        
        for i in range(num_pellets):
            if i == hole_index or i == hole_index_2:
                continue
            
            offset = (i * spacing) - ((num_pellets * spacing) / 2)
            
            if is_top_wall:
                start_pos = (center[0] + offset, 3.5, -10.0)
                velocity = (0, 0, 0.12)
            else:
                start_pos = (10.0, 3.5, center[2] + offset)
                velocity = (-0.12, 0, 0)
            
            p = Pellet(damage=35, size=0.5, delete_on_collision=False)
            p.node.position = start_pos
            p.node.color = (1, 1, 1)
            
            def move_step(pellet=p, v=velocity):
                if not pellet.node.exists(): return
                pos = pellet.node.position
                pellet.node.position = (pos[0] + v[0], pos[1], pos[2] + v[2])
            
            p.move_timer = bs.Timer(0.02, move_step, repeat=True)
            bs.timer(5.0, bs.Call(p.handlemessage, bs.DieMessage()))
            self.pellets.append(p)

    def end_attack(self):
        self.spawn_timer = None
        self.activity.start_turn()
        self.activity = None
        for pellet in self.pellets:
            pellet.handlemessage(bs.DieMessage())

class KnightHomingAttackVariant:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 7.0
        self.slash_sfx = [
            bs.getsound('knight/attacksounds/knight_slash1'),
            bs.getsound('knight/attacksounds/knight_slash2')
        ]
        self.pellets: list[Pellet] = []
        
        self._spawn_center_hazard()
        
        self.spawn_timer = bs.Timer(0.45, self.spawn_wave, repeat=True)
        bs.timer(self.duration, self.end_attack)

    def _spawn_center_hazard(self):
        center = self.activity.center_position
        num_pellets = 13
        radius = 2.8
        
        for i in range(num_pellets):
            angle = (i / num_pellets) * math.pi * 2
            x = center[0] + math.cos(angle) * radius
            z = center[2] + math.sin(angle) * radius
            
            p = Pellet(damage=60, size=0.7, delete_on_collision=False)
            p.node.position = (x, 3.5, z)
            p.node.color = (1, 0, 0)
            self.pellets.append(p)

    def spawn_wave(self):
        if len(self.activity.players) != 1:
           

        
            alive_players = [p for p in self.activity.players if getattr(self.activity, f'{self.activity.get_name_from_player(p)}_hp', 0) > 0]
            if not alive_players: return
            random.choice(self.slash_sfx).play()

            target_player = random.choice(alive_players)
            target_pos = target_player.actor.node.position

            offset_radius = 4.0
            angle = random.uniform(0, 2*math.pi)
            x_start = target_pos[0] + math.cos(angle) * offset_radius
            z_start = target_pos[2] + math.sin(angle) * offset_radius
            
            p = Pellet(damage=80, size=0.45, delete_on_collision=True)
            p.node.position = (x_start, 3.5, z_start)
            
            colors = {'kris': (0, 1, 1), 'susie': (2, 0.3, 0.6), 'ralsei': (0.3, 1, 0)}
            p.node.color = colors.get(self.activity.get_name_from_player(target_player), (1, 1, 1))
        else:
            target_pos = self.activity.soul_actor.node.position

            offset_radius = 4.0
            angle = random.uniform(0, 2*math.pi)
            x_start = target_pos[0] + math.cos(angle) * offset_radius
            z_start = target_pos[2] + math.sin(angle) * offset_radius
            

            p = Pellet(damage=80, size=0.45, delete_on_collision=True)
            p.node.position = (x_start, 3.5, z_start)
            p.node.color = (1, 1, 1)
        self.pellets.append(p)

        def home_in():
            if not p.node.exists(): return
            
            bs.getsound('knight/attacksounds/knight_teleport').play()

            curr_pos = p.node.position
            dx, dz = target_pos[0] - curr_pos[0], target_pos[2] - curr_pos[2]
            dist = (dx**2 + dz**2)**0.5
            if dist == 0: return

            speed = 0.55
            vx, vz = (dx/dist) * speed, (dz/dist) * speed

            def move_step():
                if not p.node.exists(): return
                pos = p.node.position
                p.node.position = (pos[0]+vx, pos[1], pos[2]+vz)
            
            p.move_timer = bs.Timer(0.03, move_step, repeat=True)
            bs.timer(4.0, bs.Call(p.handlemessage, bs.DieMessage()))

        bs.timer(1.5, home_in)

    def end_attack(self):
        self.spawn_timer = None
        if self.activity:
            self.activity.start_turn()
        self.activity = None
        for pellet in self.pellets:
            if pellet.node.exists():
                pellet.handlemessage(bs.DieMessage())

class KnightAttackStarsVariant:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        self.duration = 5.0
        self.sound = bs.getsound('knight/attacksounds/slowed_stardrop')
        self.explode_sound = bs.getsound('knight/attacksounds/snd_explosion_firework')
        self.pellets: list[Pellet] = []
        self.spawn_timer = bs.Timer(0.2, self.spawn_wave, repeat=True)
        bs.getsound('knight/attacksounds/knight_powerup').play()
        bs.timer(self.duration, self.end_attack)

    def spawn_wave(self):
        num_pellets = random.randint(1, 2)
        for _ in range(num_pellets):
            x_start = 8.0
            z_start = self.activity.center_position[2] + random.uniform(-3.5, 4.2)
            y_start = 3.5
            
            pellet = Pellet(damage=120, size=0.3, delete_on_collision=False)
            pellet.node.position = (x_start, y_start, z_start)

            travel_time = random.uniform(2.0, 3.0)
            x_end = -8.0
            z_end = z_start + random.uniform(-1, 1)
            
            bs.animate_array(pellet.node, 'position', 3, {
                0.0: (x_start, y_start, z_start),
                travel_time: (x_end, y_start, z_end)
            })
            self.pellets.append(pellet)
        self.sound.play(0.5)

    def end_attack(self):
        self.spawn_timer = None

        def finalize():
            if self.activity:
                self.activity.start_turn()
                self.activity = None

        for pellet in self.pellets:
            if not pellet.node.exists():
                continue
            
            curr = pellet.node.position
            bs.animate_array(pellet.node, 'color', 3, {0.0: (1,1,1), 0.6: (5, 0, 0)})
            bs.animate_array(pellet.node, 'position', 3, {
                0.0: curr, 
                0.6: (curr[0] + 1.5, curr[1], curr[2])
            })

            def explode_and_chase(p=pellet):
                if not p.node.exists(): return
                self.explode_sound.play()
                
                for _ in range(random.randint(2, 3)):
                    mini = Pellet(damage=60, size=0.4, delete_on_collision=True)
                    mini.node.position = p.node.position
                    mini.node.color = (1, 0, 0)
                    
                    self.setup_chase_logic(mini)
                
                p.handlemessage(bs.DieMessage())

            bs.timer(0.6, explode_and_chase)
            
        bs.timer(5.0, finalize)

    def setup_chase_logic(self, mini):
        def chase_step():
            if not mini.exists():
                return
            
            target_pos = None
            min_dist = 9999
            
            alive_players = [p for p in self.activity.players if getattr(self.activity, f'{self.activity.get_name_from_player(p)}_hp', 0) > 0]
            
            for p in alive_players:
                if p.actor and p.actor.exists():
                    p_pos = p.actor.node.position
                    d = math.dist(mini.node.position, p_pos)
                    if d < min_dist:
                        min_dist = d
                        target_pos = p_pos
            
            if target_pos:
                cur = mini.node.position
                dx, dz = target_pos[0] - cur[0], target_pos[2] - cur[2]
                dist = math.sqrt(dx**2 + dz**2)
                
                if dist > 0:
                    speed = 0.04
                    mini.node.position = (cur[0] + (dx/dist)*speed, cur[1], cur[2] + (dz/dist)*speed)

        mini.move_timer = bs.Timer(0.03, chase_step, repeat=True)
        bs.timer(4.0, bs.Call(mini.handlemessage, bs.DieMessage()))




# 2d engine go brr

class Star(TwoDPellet):
    def __init__(self, damage = 100, size = 1, delete_on_collision = False, star_size: bool=True):
        super().__init__(damage, size, delete_on_collision)
        self.image: bs.NodeVisualizer = bs.newnode('image', attrs={
            'texture': bs.gettexture('knight_star'),
            'color': (1, 1, 1),
            'scale': (size, size),
            'position': (0, 0),
        })
        if star_size:
            size *= 0.5
            self.node.scale =(size, size)
            self.radius = size
        self.image.connectattr('position', self.node, 'position')

    
        
    def handlemessage(self, msg):
        super().handlemessage(msg)
        if isinstance(msg, bs.DieMessage):
            self.image.delete()

class LoopingImageAnimationModel(bs.Actor):
    def __init__(
            
        self, 
        mesh: str,
        texture: str,
        frame_count: int,
        frame_delay: int
    ):
        super().__init__()
        self.node: bs.NodeVisualizer = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': bs.getmesh(mesh),
   
            },
        )
        self.image = LoopingImageAnimation(
            texture,
            frame_count,
            frame_delay
            
        )
        self.image.node.opacity = 0.0
        self.tick_timer = bs.Timer(0.01, self.change, repeat=True)
    def change(self):
        try:
            if isinstance(self.image.node.texture, bs.Texture):
                self.node.color_texture =self.image.node.texture
        except:
            pass
        

    

       


    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
            self.image.die()
            self.tick_timer  = None
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)



class RoaringKnight(bs.Actor):
    def __init__(
        self, 
        position = (0, 170), 
        scale = (200, 200),
    ):
        super().__init__()
        self.scale = scale
        self.position = position
        self.image = LoopingImageAnimation(
            'knight_front',
            1,
            0.1,
            scale=self.scale,
            position=self.position,
        )

        # animate in, so it looks nicer
        bs.animate(
            self.image.node, 
            'opacity', 
            {0.0: 0.0, 1.0: 1.0}
        )
       
    def ready(self):
   
        self.image.prefix = 'knight_flourish'
        self.image.frame_count = 7
        self.image.frame_delay = 0.07
        self.image._current_frame = 1
        self.image.loop = False
 
        bs.timer(0.6, self.roar)
    
    def roar(self):
        self.image.prefix = 'knight_roar'
        self.image.frame_count = 2
        self.image.frame_delay = 0.09
        self.image._current_frame = 1
        self.image.loop = True
 
    def slash_done(self):
        # double scale since texture is small
        self.image.node.scale = (300, 300)
        self.image.prefix = 'knight_slash'
        self.image.frame_count = 6
        self.image.frame_delay = 0.08
        self.image._current_frame = 1
        self.image.loop = False

    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage):
            self.image.die()
        return super().handlemessage(msg)
    
    



class KnightFinalAttack:
    def __init__(self, activity: roaryGame):
        self.activity = activity
        # Set up
        scene=Scene(texture='black') 
        self.activity.scene=scene
        scene.node.color=(0, 0, 0)
        
        self.roary = RoaringKnight()
        
        self.pellets: list[TwoDPellet] = []
        self.timers: list[bs.Timer] = []

        # Okay, give players an actor to control.
        if len(self.activity.players) != 1:
       
            for player in self.activity.players:
                if getattr(self, f'{self.activity.get_name_from_player(player)}_hp', 0) <= 0:
                    continue
                sp=ScenePlayer(
                    player,
                    self.activity.scene,
                    position=(0,0),
                    size=(50, 50),
                    scale=0.5,
                )
                sp.max = 450
                colors = {
                    # 'kris': (0, 0.6, 1),
                    'kris': (1, 0, 0), 
                    'susie': (1, 0.3, 0.6), 
                    'ralsei': (0.3, 1, 0)
                }

                sp.node.color = colors[self.activity.get_name_from_player(player)]
                speed = 2.6

            
                player.resetinput()
                player.assigninput(bs.InputType.UP_DOWN, sp.on_move_up_down)
                player.assigninput(bs.InputType.LEFT_RIGHT, sp.on_move_left_right)
                player.assigninput(bs.InputType.RUN, sp.on_run)
                self.timers.append(bs.Timer(0.001, bs.Call(sp.move_by_input, speed), repeat=True))
        else:
            #p1 gets a soul
            player = self.activity.players[0]
            sp=ScenePlayer(
                    player,
                    self.activity.scene,
                    position=(0,0),
                    size=(50, 50),
                    scale=0.5,
                )
            sp.max = 450
       
            sp.node.color = (1,0,0)
            speed = 2.6

            
            player.resetinput()
            player.assigninput(bs.InputType.UP_DOWN, sp.on_move_up_down)
            player.assigninput(bs.InputType.LEFT_RIGHT, sp.on_move_left_right)
            player.assigninput(bs.InputType.RUN, sp.on_run)
            self.timers.append(bs.Timer(0.001, bs.Call(sp.move_by_input, speed), repeat=True))
        bs.timer(1, self.start_attack)


    def start_attack(self):
        self.circle_angle_offset = 0.0
      
        
        def spawn_random_absorb():
            if not self.activity or self.activity.scene is None: return
            knight_pos = self.roary.position
            angle = random.uniform(0, math.pi * 2)
            dist = 1300
            start_x = knight_pos[0] + math.cos(angle) * dist
            start_y = knight_pos[1] + math.sin(angle) * dist
            
            s = Star(damage=110, size=170.0, delete_on_collision=False)

            duration = random.uniform(1.5, 2.0)
            bs.animate_array(s.image, 'position', 2, {
                0.0: (start_x, start_y),
                duration: knight_pos
            })
            bs.timer(duration, bs.Call(s.handlemessage, bs.DieMessage()))

        # --- PHASE 2: Circular Sweep (Starts at 2.5s) ---
        def spawn_sweeping_star(index, total_in_ring):
            if not self.activity or self.activity.scene is None: return
            knight_pos = self.roary.position
            start_radius = 1300
            base_angle = (index / total_in_ring) * math.pi * 2
            
            s = Star(damage=120, size=120.0, delete_on_collision=False, star_size=False).autoretain()
          
            # put this star offscreen so its not shitty lookin'
            s.node.position = (-999,9999)
            
            # Local state for this specific star so they don't sync up
            state = {'step': 0}
            duration_secs = 4.0 # Balanced speed
            total_steps = duration_secs * 60

            def update_star_pos():
                if not s.image: return
                state['step'] += 1
                ratio = min(1.0, state['step'] / total_steps)
                
                # The Sweep: Shrink radius + Rotate angle
                current_radius = start_radius * (1.0 - ratio)
                current_angle = base_angle + (ratio * 3.0) 
                
                new_x = knight_pos[0] + math.cos(current_angle) * current_radius
                new_y = knight_pos[1] + math.sin(current_angle) * current_radius
                s.image.position = (new_x, new_y)

                if ratio >= 1.0:
                    s.handlemessage(bs.DieMessage())

            # High-frequency timer for smooth 60fps movement
            self.timers.append(bs.Timer(0.01, update_star_pos, repeat=True))

        for i in range(25):
            bs.timer(i * 0.08, spawn_random_absorb)
            
   
        circle_start_delay = 2.7
        for ring_index in range(5): 
            ring_offset = ring_index * 0.8
            num_stars = 14
            for i in range(num_stars):
                bs.timer(circle_start_delay + ring_offset + (i * 0.04), 
                         bs.Call(spawn_sweeping_star, i, num_stars))


        bs.timer(12.0, self.ready)

    def ready(self):
        if self.activity.gameover: return
        self.roary.ready() 

        def staggered_burst(batch_index):
            num_stars = 20 # 20 stars per "pop"
            knight_pos = self.roary.position
            
            for i in range(num_stars):
                # Randomize angles so it's not a perfect circle
                angle = random.uniform(0, math.pi * 2)
                dist = 1500 
                
                end_x = knight_pos[0] + math.cos(angle) * dist
                end_y = knight_pos[1] + math.sin(angle) * dist
                
                s = Star(damage=130, size=110.0, delete_on_collision=False)
                s.image.position = knight_pos
                
                # Vary the speeds so some stars "zip" and some "float"
                duration = random.uniform(0.8, 3.0)
                
                bs.animate_array(s.image, 'position', 2, {
                    0.0: knight_pos,
                    duration: (end_x, end_y)
                })
                bs.timer(duration, bs.Call(s.handlemessage, bs.DieMessage()))

        # Fire off 4 staggered bursts for a "constant explosion" feel
        for batch in range(4):
            bs.timer(batch * 0.4, bs.Call(staggered_burst, batch))
        
        bs.timer(4.5, self.end)

    def end(self):
        self.roary.slash_done()
        def h():
            bs.animate_array(self.roary.image.node, 'position', 2, {
                        0.0: self.roary.position,
                        0.2: (self.roary.position[0], self.roary.position[1] + 400)
            })
            bs.timer(0.4, self.end_attack)
        bs.timer(0.6, h)
       
    
    def end_attack(self):
        self.timers.clear()
        self.roary.handlemessage(bs.DieMessage())
        
        self.activity.guard_down = True
        self.activity.start_turn()
        
        if self.activity.scene:
            self.activity.scene.handlemessage(bs.DieMessage(True))
        self.activity = None
        self.roary = None
