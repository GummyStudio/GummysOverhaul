# Released under the MIT License. See LICENSE for details.
#
"""Defines the spaz actor."""
# pylint: disable=too-many-lines

from __future__ import annotations

import math
import random
import logging
from typing import TYPE_CHECKING
import babase
import bauiv1 as bui
from bascenev1lib.actor.popuptext import PopupText

from typing_extensions import override
import bascenev1 as bs
from bascenev1lib.actor.bomb import Bomb, Blast
from bascenev1lib.actor.powerupbox import PowerupBoxFactory, PowerupBox
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.gameutils import SharedObjects
from gummyoverhaul.nodevisualizer import NodeVisualizer


if TYPE_CHECKING:
    from typing import Any, Sequence, Callable

POWERUP_WEAR_OFF_TIME = 20000

# Obsolete - just used for demo guy now.
BASE_PUNCH_POWER_SCALE = 1.2
BASE_PUNCH_COOLDOWN = 400


class PickupMessage:
    """We wanna pick something up."""

class FootingMessage:
    """ we are standing?"""
    def __init__(self, footing):
        self.footing = footing


class PunchHitMessage:
    """Message saying an object was hit."""


class CurseExplodeMessage:
    """We are cursed and should blow up now."""


class BombDiedMessage:
    """A bomb has died and thus can be recycled."""

class SpikeText(bs.Actor):
    """Text that pops up for combos or special events with scaling/flashing."""

    def __init__(
        self,
        text: str | bs.Lstr,
        *,
        position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        was_big: bool = False,
        was_bigger: bool = False
    ):
        super().__init__()
        
        # Determine base scale and lifespan
        lifespan = 2.0 if (was_big or was_bigger) else 1.2
        
     
        base_size = 0.02
        if was_bigger:
            final_scale = base_size * 2.0
        elif was_big:
            final_scale = base_size * 1.2
        else:
            final_scale = base_size

        self.node = bs.newnode(
            'text',
            attrs={
                'text': text,
                'in_world': True,
                'shadow': 1.0,
                'flatness': 1.0,
                'h_align': 'center',
                'position': position,
                'color': (1, 1, 1, 1)
            },
            delegate=self,
        )

        bs.animate(self.node, 'scale', {
            0.0: 0.0,
            0.1: final_scale * 1.2, 
            0.15: final_scale
        })

        # 2. Color/Flash Logic
        if was_big or was_bigger:
            flash_duration = 0.2 if was_bigger else 0.1
            
            color_anim = bs.animate_array(self.node, 'color', 4, {
                0.0: (1, 1, 1, 1),
                0.05: (0,0, 0, 1),
                0.1: (1, 1, 1, 1)
            }, loop=True)

            def stop_flash(anim):
                if anim:
                    anim.delete()
                if self.node:
                    self.node.color = (1, 1, 1, 1)

            bs.timer(flash_duration, bs.Call(stop_flash, color_anim))

        bs.animate(self.node, 'opacity', {
            0.0: 1.0,
            lifespan * 0.8: 1.0,
            lifespan: 0.0
        })

        self._die_timer = bs.Timer(
            lifespan, bs.WeakCall(self.handlemessage, bs.DieMessage())
        )

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()
        else:
            super().handlemessage(msg)

class Spaz(bs.Actor):
    """
    Base class for various Spazzes.

    Category: **Gameplay Classes**

    A Spaz is the standard little humanoid character in the game.
    It can be controlled by a player or by AI, and can have
    various different appearances.  The name 'Spaz' is not to be
    confused with the 'Spaz' character in the game, which is just
    one of the skins available for instances of this class.
    """

    # pylint: disable=too-many-public-methods
    # pylint: disable=too-many-locals

    node: bs.Node
    """The 'spaz' bs.Node."""

    points_mult = 1
    curse_time: float | None = 5.0
    default_bomb_count = 1
    default_bomb_type = 'normal'
    default_boxing_gloves = False
    default_shields = False

    def __init__(
        self,
        color: Sequence[float] = (1.0, 1.0, 1.0),
        highlight: Sequence[float] = (0.5, 0.5, 0.5),
        character: str = 'Spaz',
        source_player: bs.Player | None = None,
        start_invincible: bool = True,
        can_accept_powerups: bool = True,
        powerups_expire: bool = False,
        demo_mode: bool = False,
        cosmetic: str | None = None
    ):
        """Create a spaz with the requested color, character, etc."""
        # pylint: disable=too-many-statements

        super().__init__()
        self.powerupvalue = False
        shared = SharedObjects.get()
        activity = self.activity
        self.standing = False
        self.attempted_screen_ko = False
        self.award_xp = False
        self.can_accept_powerups = can_accept_powerups  
        self.abilities = [None, None, None]

        # Woah, are we an amiibo?
        try:
            self.is_amiibo = hasattr(source_player.sessionplayer, 'amiibo')
            if self.is_amiibo:
                self.abilities = source_player.sessionplayer.data['abilities']
                
        except:
            self.is_amiibo = False

        if source_player:
            self.award_xp = True

        factory = SpazFactory.get()

        # We need to behave slightly different in the tutorial.
        self._demo_mode = demo_mode

        self.play_big_death_sound = False

        # Scales how much impacts affect us (most damage calcs).
        self.impact_scale = 1.0

        self.source_player = source_player
        self._dead = False
        self.cloaked = False
        if self._demo_mode:  # Preserve old behavior.
            self._punch_power_scale = BASE_PUNCH_POWER_SCALE
        else:
            self._punch_power_scale = factory.punch_power_scale
        self.fly = self.getactivity().globalsnode.happy_thoughts_mode
        if isinstance(activity, bs.GameActivity):
            self._hockey = activity.map.is_hockey
        else:
            self._hockey = False
        self._punched_nodes: set[bs.Node] = set()
        self._cursed = False
        self._connected_to_player: bs.Player | None = None
        materials = [
            factory.spaz_material,
            shared.object_material,
            shared.player_material,
        ]
        roller_materials = [factory.roller_material, shared.player_material]
        extras_material = []

        if can_accept_powerups:
            pam = PowerupBoxFactory.get().powerup_accept_material
            materials.append(pam)
            roller_materials.append(pam)
            extras_material.append(pam)

        media = factory.get_media(character)
        punchmats = (factory.punch_material, shared.attack_material)
        pickupmats = (factory.pickup_material, shared.pickup_material)
        self.node: NodeVisualizer = bs.newnode(
            type='spaz',
            delegate=self,
            attrs={
                'color': color,
                'behavior_version': 0 if demo_mode else 1,
                'demo_mode': demo_mode,
                'highlight': highlight,
                'jump_sounds': media['jump_sounds'],
                'attack_sounds': media['attack_sounds'],
                'impact_sounds': media['impact_sounds'],
                'death_sounds': media['death_sounds'],
                'pickup_sounds': media['pickup_sounds'],
                'fall_sounds': media['fall_sounds'],
                'color_texture': media['color_texture'],
                'color_mask_texture': media['color_mask_texture'],
                'head_mesh': media['head_mesh'],
                'torso_mesh': media['torso_mesh'],
                'pelvis_mesh': media['pelvis_mesh'],
                'upper_arm_mesh': media['upper_arm_mesh'],
                'forearm_mesh': media['forearm_mesh'],
                'hand_mesh': media['hand_mesh'],
                'upper_leg_mesh': media['upper_leg_mesh'],
                'lower_leg_mesh': media['lower_leg_mesh'],
                'toes_mesh': media['toes_mesh'],
                'style': factory.get_style(character),
                'fly': self.fly,
                'hockey': self._hockey,
                'materials': materials,
                'roller_materials': roller_materials,
                'extras_material': extras_material,
                'punch_materials': punchmats,
                'pickup_materials': pickupmats,
                'invincible': start_invincible,
                'source_player': None, # we dont NEED this right??? 
                # getting in the way of figure players 
                
            },
        )
     
        
        assert isinstance(self.node, NodeVisualizer)

        self.shield: bs.NodeVisualizer | None = None
        
        if start_invincible:

            

            bs.timer(
                    (3.0 if  self.every_instance_in_abilities(
                         'Longer Invincibility Respawn'
                     ) else 1.0), lambda: self._safesetattr(self.node, 'invincible', False))
        self.every_instance_in_abilities
        self.default_color = color
        self.default_highlight = highlight
        self.hitpoints = 1000
        self.enablegamerpoints = False
        self._r = 'GUMMYgameplay'
        self.beds = 0
        self.hitpoints_max = 1000
        self.shield_hitpoints: int | None = None
        self.shield_hitpoints_max = 650
        self.shield_decay_rate = 0
        self.ass_bomb = False
        self.speed_mult = 1
        self.cosmetic = cosmetic
        self.character = character
        self.shield_decay_timer: bs.Timer | None = None
        self._boxing_gloves_wear_off_timer: bs.Timer | None = None
        self._boxing_gloves_wear_off_flash_timer: bs.Timer | None = None
        self._bomb_wear_off_timer: bs.Timer | None = None
        self._bomb_wear_off_flash_timer: bs.Timer | None = None
        self._multi_bomb_wear_off_timer: bs.Timer | None = None
        self._multi_bomb_wear_off_flash_timer: bs.Timer | None = None
        self._curse_timer: bs.Timer | None = None
        self.boogie_timer: bs.Timer | None = None
        self.bomb_count = self.default_bomb_count
        self._max_bomb_count = self.default_bomb_count
        self.bomb_type_default = self.default_bomb_type
        self.bomb_type = self.bomb_type_default
        self.land_mine_count = 0
        
        self.rock_count = 0
        self.egg_count = 0
        self.mini_count = 0
        self.star_count = 0
        self.breaker_count = 0
        self.boogie_count = 0
        self.promine_count = 0
        self.heart_count = 0
        self.boom_count = 0
        self.overdose = 0
        self.blast_radius = 2.0
        self.boogieing = False
        self.shieldbroken = False
        self.eletricuted = False
        self.Dcolor = color
        self.powerups_expire = powerups_expire
        if self._demo_mode:  # Preserve old behavior.
            self._punch_cooldown = BASE_PUNCH_COOLDOWN
        else:
            self._punch_cooldown = factory.punch_cooldown
        self._jump_cooldown = 250
        self._pickup_cooldown = 0
        self._bomb_cooldown = 0
        self._has_boxing_gloves = False
        if self.default_boxing_gloves:
            self.equip_boxing_gloves()
        self.last_punch_time_ms = -9999
        self.last_pickup_time_ms = -9999
        self.last_jump_time_ms = -9999
        self.last_run_time_ms = -9999
        self._last_run_value = 0.0
        self.last_bomb_time_ms = -9999
        self._turbo_filter_times: dict[str, int] = {}
        self._turbo_filter_time_bucket = 0
        self._turbo_filter_counts: dict[str, int] = {}
        self.frozen = False
        self.shattered = False
        self._last_hit_time: int | None = None
        self._num_times_hit = 0
        self._bomb_held = False
        if self.default_shields:
            self.equip_shields()
        


        
        
        
        
        self.getanother = False
        self._dropped_bomb_callbacks: list[Callable[[Spaz, bs.Actor], Any]] = []

        self._score_text: bs.Node | None = None
        self._charge: bs.Node | None = None
        self._score_text_hide_timer: bs.Timer | None = None
        self._last_stand_pos: Sequence[float] | None = None
        self.is_gold = False
        self._fire_state = {}

        # Deprecated stuff.. should make these into lists.
        self.punch_callback: Callable[[Spaz], Any] | None = None
        self.pick_up_powerup_callback: Callable[[Spaz], Any] | None = None
        #self.equip_shields()
        #self.equip_boxing_gloves()
        self.allow_new_charge = True

        self.DMGcharge = 0
        self.spike = 0
        self.updateCharge = False
        #if self.source_player:
        #    self.add_charge(value=6)

        # For the spike stuff
        self.releasing_charge = False

        self.last_damage_count = 0
        
        self.slowness = 0
        self._input_x = 0
        self._input_y = 0

        self.spike_actors: list[SpikeText] = []
        self.spiking = False
        self.spike_timer: bs.Timer = None
        self.went_critical = False

        self.totem = 0
    
        if self.apply_cosmetic(character, cosmetic) is False:
            logging.debug(f'{character} has no cosmetic named {cosmetic}')

        bs.timer(0.1, self.tick, repeat=True)
        self.effects = []
        bs.timer(0.001, self.apply_slowness, repeat=True)
        
        self.force_crit = isinstance(self.getactivity().session, bs.CoopSession)
        self.force_crit_chance = 25
        bs.timer(1, self.auto_b2b, repeat=True)

        # We spawned, check for any auto powerups
        if self.every_instance_in_abilities('Auto Negative Bombs'):
            self.handlemessage(bs.PowerupMessage('negative'))
        if self.every_instance_in_abilities('Auto Sticky Bombs'):
            self.handlemessage(bs.PowerupMessage('sticky_bombsd'))
        if self.every_instance_in_abilities('Auto Impact-Bombs'):
            self.handlemessage(bs.PowerupMessage('impact_bombs'))
        if self.every_instance_in_abilities('Auto Ice Bombs'):
            self.handlemessage(bs.PowerupMessage('ice_bombs'))
        if self.every_instance_in_abilities('Auto Totem of Undying'):
            self.handlemessage(bs.PowerupMessage('totem'))
        if self.every_instance_in_abilities('Auto Impulse-Grendades'):
            self.handlemessage(bs.PowerupMessage('impulse'))
        if self.every_instance_in_abilities('Auto Electric-Bombs'):
            self.handlemessage(bs.PowerupMessage('breaker'))
        if self.every_instance_in_abilities('Auto Lightning Bombs'):
            self.handlemessage(bs.PowerupMessage('lightning'))
        if self.every_instance_in_abilities('Auto Random Bombs'):
            self.handlemessage(bs.PowerupMessage('random'))

        # easy changing
        
        self._punch_power_scale *= 1 + (1.5*self.every_instance_in_abilities('Punch Scale ↑'))
        self.impact_scale /= 1 + (1.15*self.every_instance_in_abilities('Impact Scale ↓'))
        self.hitpoints_max *= 1 + (2.5*self.every_instance_in_abilities('Max Health ↑↑'))
        self.hitpoints = self.hitpoints_max
        self.shield_decay_rate /= 1 + (1.5*self.every_instance_in_abilities('Shield Decay ↓'))
        

        

    def auto_b2b(self):
        if not self.is_alive():
            return
        if self.every_instance_in_abilities('Great Auto B2B Charger'):
            self.add_charge(2)
        if self.every_instance_in_abilities('Auto B2B Charger'):
            self.add_charge(1)
    
    def critical_hp(self):
        if self.went_critical:
            return
        self.went_critical = True
        if self.every_instance_in_abilities('Critical-Health Invincibility'):
            self.node.invincible = True
            bs.timer(2, self._safesetattr(
                self.node, 'invincible', False
            ))
        if self.every_instance_in_abilities('Critical-Health Defense'):
            self.impact_scale *= 0.5
            def unset():
                self.impact_scale *= 1.5

            bs.timer(2,unset)
        if self.every_instance_in_abilities('Critical-Health Shields'):
            self.handlemessage(bs.PowerupMessage('shield'))
        
        if self.every_instance_in_abilities('Critical-Health Gloves'):
            self.handlemessage(bs.PowerupMessage('punch'))

        # DEBUG
        self.award_xp = False
       


    
    def every_instance_in_abilities(self, ability_name: str):
        if not self.is_amiibo:
            return 0
            

        count = 0

        # remove the arrows cuz they're annoying
        # e.g., "Punch Scale ↑ (1)" or "Punch Scale" -> "punchscale(1)"
        target_cleaned = ability_name.replace('down', '').replace('down', '').replace(' ', '').lower()

        for instance in self.abilities:
            if instance is None or instance == "Eaten":
                continue
                
            # Clean the current slot item the exact same way
            instance_cleaned = instance.replace('up', '').replace('down', '').replace(' ', '').lower()
            
            if instance_cleaned == target_cleaned:
                count += 1

        return count
    
    def delete_spike_actors(self):
        for actor in self.spike_actors:
            actor.handlemessage(bs.DieMessage(True))
        self.spike_actors = []
    def end_spike(self):
        self.spiking = False
        self.spike_timer = None
        self.spike = 0
    def show_spike_text(self, amount):
        #bs.getplayers()[0].actor.add_charge(10)
        if not self.node:
            return
        play_sfx = True
        if not self.spiking:
            self.spike = 0
            play_sfx = False
        
  
        if play_sfx:
            b2b_S = bs.getsound('spikeS')
            b2b_M = bs.getsound('spikeM')
            b2b_L =bs.getsound('spikeL')
         

        
            if 1 <= amount <= 29:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_S.play()
            elif 30 <= amount <= 59:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_M.play()
            else:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_L.play()
            
        
        self.delete_spike_actors()
        self.spiking = True
        self.spike += amount
        
        was_big = 10 <= self.spike < 20
        was_bigger = self.spike >= 20

        base_pos = self.node.position
        char_spacing = 0.35
        if was_big:
            char_spacing *= 1.2
        if was_bigger:
            char_spacing *= 2.4
        
        
        spike_str =f'-{int(self.spike)}%'
        
        
        start_x = base_pos[0] - ((len(spike_str) - 1) * char_spacing) / 2.0

        for i, digit in enumerate(spike_str):
            pos = (
                start_x + (i * char_spacing), 
                base_pos[1]+2,
                base_pos[2]
            )
            
            text_actor = SpikeText(
                digit, 
                position=pos, 
                was_big=was_big, 
                was_bigger=was_bigger
            ).autoretain()
            
            self.spike_actors.append(text_actor)

        self.spike_timer = None
        self.spike_timer = bs.Timer(2.0, self.end_spike)

              

    def tick(self):
        self.update_fire()
        self.apply_slowness()
        self.b2b_eletricity()
        self.apply_effects()
        if self.node:
            self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
            )
            if self.node.hurt > 0.75:
                self.critical_hp()

    def apply_effects(self):

        for effect in self.effects:

            if effect == 'fire_resistance':
                
                self.clear_fire()

    def update_fire(self):
        # Check any fire states for in_fire or remaining_ticks is true
        # Tjhen show visuals that we on fireee
        if not self.node:
            return

        if self.shield:
            # We should not be on fire anymore. (Shields block fire)
            self.clear_fire()
        
        show_fire = False

        for fire in self._fire_state:
            
            if self._fire_state[fire]['in_fire'] or bool(self._fire_state[fire]['remaining_ticks']):
                show_fire = True
        
        if show_fire:
                # burn
                bs.emitfx(position=self.node.position,
                      velocity=(0,10,0),
                      count=int(12+random.random()*12),
                      scale=random.random()*3,
                      spread=random.random()*0.3* 1.2,
                      chunk_type='sweat')
                bs.emitfx(position=self.node.position,
                            velocity=(0,10,0),
                            count=int(12+random.random()*12),
                            scale=random.random()*6,
                            spread=random.random()*0.3* 1.2,
                            chunk_type='sweat')
                bs.emitfx(position=self.node.position,
                            velocity=(0,10,0),
                            count=int(12+random.random()*4),
                            scale=random.random()*2,
                            spread=random.random()*0.3 * 1.2,
                            chunk_type='sweat')
                bs.emitfx(position=self.node.position,
                            velocity=(0,10,0),
                            count=int(12+random.random()*6),
                            scale=random.random()*4.6,
                            spread=random.random()*0.3 * 9,
                            chunk_type='sweat')

    
    def apply_slowness(self):
        
       
        if self.slowness > 0:
            
            decrease = 0.1 * int(self.slowness)  # 10% per slowness point
            self.speed_mult = max(0.35, 1.0 - decrease)
        else:
            self.speed_mult = 1.0 



        # Only apply this to players. (Bots have their own way of moving. and still use self.speed_multi)
        if not self.node or not self.source_player:
            return
        
        
        
        self.node.move_left_right = self._input_x * self.speed_mult
        self.node.move_up_down =  self._input_y * self.speed_mult
    
    def add_slowness(self, value: int = 1, time: float = 3.0):
        self.slowness += value

        def remove():
            self.slowness -= value

        bs.timer(time, remove)

    


    def apply_cosmetic(self, character, cosmetic):
       # print(f'Applying cosmetic {cosmetic} to {character}')

        if not self.node:
            return None
        
        if cosmetic == 'None' or cosmetic is None:
            return None

        if character == 'Orange Cap':
            if cosmetic == 'Blue Cap':
                self.node.color_mask_texture = bs.gettexture('orangeCapColorMask')
                self.node.pelvis_mesh = bs.getmesh('orangeCapPelvis')
                self.node.upper_arm_mesh = bs.getmesh('orangeCapUpperArm')
                self.node.hand_mesh = bs.getmesh('orangeCapHand')
                self.node.upper_leg_mesh = bs.getmesh('orangeCapUpperLeg')
                self.node.lower_leg_mesh = bs.getmesh('orangeCapLowerLeg')
                self.node.toes_mesh = bs.getmesh('orangeCapToes')

            
                
                self.node.color_texture = bs.gettexture('blueCapColor')
                self.node.head_mesh = bs.getmesh('blueCapHead')
                
                self.node.torso_mesh = bs.getmesh('blueCapTorso')
            
                self.node.forearm_mesh = bs.getmesh('blueCapForeArm')
               
                return True

        elif character == 'Spaz':
            if cosmetic == 'Spaz.EXE':
                self.node.style = 'agent'
                self.node.color_texture = bs.gettexture('neoSpazEXECosmetic')
                return True

            elif cosmetic == 'Spazling':
                self.node.style = 'agent'
                self.node.color_texture = bs.gettexture('spazingaColor')
                self.node.color_mask_texture = bs.gettexture('spazingaColorMask')
                self.node.forearm_mesh = bs.getmesh('spazingaForeArm')
                self.node.hand_mesh = bs.getmesh('spazingaHand')
                self.node.head_mesh = bs.getmesh('spazingaHead')
                self.node.lower_leg_mesh = bs.getmesh('spazingaLowerLeg')
                self.node.pelvis_mesh = bs.getmesh('spazingaPelvis')
                self.node.toes_mesh = bs.getmesh('spazingaToes')
                self.node.torso_mesh = bs.getmesh('spazingaTorso')
                self.node.upper_arm_mesh = bs.getmesh('spazingaUpperArm')
                self.node.upper_leg_mesh = bs.getmesh('spazingaUpperLeg')
                
                self.node.jump_sounds = self.node.jump_sounds + (bs.getsound('spazlingJump01'),)
                self.node.jump_sounds = self.node.jump_sounds + (bs.getsound('spazlingJump02'),)
                self.node.jump_sounds = self.node.jump_sounds + (bs.getsound('spazlingJump03'),)
                self.node.jump_sounds = self.node.jump_sounds + (bs.getsound('spazlingJump04'),)

                self.node.attack_sounds = self.node.attack_sounds + (bs.getsound('spazlingAttack03'),)

                self.node.death_sounds = self.node.death_sounds + (
                bs.getsound('spazlingDeath01'),
                bs.getsound('spazlingDeath04'),
                )

                self.node.fall_sounds = self.node.fall_sounds + (bs.getsound('spazlingFall01'),)

                self.node.impact_sounds = self.node.impact_sounds + (
                bs.getsound('spazlingImpact02'),
                bs.getsound('spazlingImpact04'),
                )

                self.node.pickup_sounds = self.node.pickup_sounds + (bs.getsound('spazlingPickup01'),)
                return True
            
            elif cosmetic == 'Salvatore':
                self.node.color_texture = bs.gettexture('salColor')
                self.node.head_mesh = bs.getmesh('salHead')
                self.node.torso_mesh = bs.getmesh('salTorso')
                #sounds = [
                #    bs.getsound('sal1'),
                #    bs.getsound('sal2'),
                #    bs.getsound('sal3'),
                #]


                #self.node.jump_sounds = sounds.copy() + [bs.getsound('salJump')]
                #self.node.attack_sounds = sounds
                #self.node.impact_sounds = [bs.getsound('salImpact1'), bs.getsound('salImpact2'), bs.getsound('salImpact3')]
                #self.node.death_sounds = [bs.getsound('salDeath')]
                #self.node.pickup_sounds = [bs.getsound('salPickup')]
                #self.node.fall_sounds = [bs.getsound('salFall')]

                
                return True

            elif cosmetic == 'Sal but with a voice':
                self.node.color_texture = bs.gettexture('salColor')
                self.node.head_mesh = bs.getmesh('salHead')
                self.node.torso_mesh = bs.getmesh('salTorso')
                sounds = [
                    bs.getsound('sal1'),
                    bs.getsound('sal2'),
                    bs.getsound('sal3'),
                ]


                self.node.jump_sounds = sounds.copy() + [bs.getsound('salJump')]
                self.node.attack_sounds = sounds
                self.node.impact_sounds = [bs.getsound('salImpact1'), bs.getsound('salImpact2'), bs.getsound('salImpact3')]
                self.node.death_sounds = [bs.getsound('salDeath')]
                self.node.pickup_sounds = [bs.getsound('salPickup')]
                self.node.fall_sounds = [bs.getsound('salFall')]

                
                return True
        
            elif cosmetic == 'Scoldy':
                    self.node.style = 'spaz'
                    self.node.color_texture = bs.gettexture('scoldyColor')
                    self.node.color_mask_texture = bs.gettexture('scoldyColorMask')
                    self.node.forearm_mesh = bs.getmesh('scoldyForeArm')
                    self.node.hand_mesh = bs.getmesh('invisible')
                    self.node.head_mesh = bs.getmesh('scoldyHead')
                    self.node.lower_leg_mesh = bs.getmesh('scoldyLowerLeg')
                    self.node.pelvis_mesh = bs.getmesh('scoldyPelvis')
                    self.node.toes_mesh = bs.getmesh('scoldyToes')
                    self.node.torso_mesh = bs.getmesh('scoldyTorso')
                    self.node.upper_arm_mesh = bs.getmesh('scoldyUpperArm')
                    self.node.upper_leg_mesh = bs.getmesh('scoldyUpperLeg')
                    scoldy_sounds = [bs.getsound('scoldy'), bs.getsound('scoldy2'), bs.getsound('scoldy3')]
                    scoldy_hit = [bs.getsound('scoldyHit'), bs.getsound('scoldyHit2')]
                    scoldy_jump = [bs.getsound('scoldyJump'), bs.getsound('scoldyJump2'), bs.getsound('scoldyJump3')]
                    self.node.jump_sounds = scoldy_jump
                    self.node.attack_sounds = scoldy_sounds
                    self.node.impact_sounds = scoldy_hit
                    self.node.death_sounds = [bs.getsound('scoldyDeath')]
                    self.node.pickup_sounds = [bs.getsound('scoldyPickup')]
                    self.node.fall_sounds = [bs.getsound('scoldyFall')]

                    
                    return True
            elif cosmetic == 'Gummy Voice Spaz':
                    
                    self.node.jump_sounds = [bs.getsound('gummyspazJump01'), bs.getsound('gummyspazJump02'), bs.getsound('gummyspazJump03'), bs.getsound('gummyspazJump04')]
                    self.node.attack_sounds = [
                        bs.getsound('gummyspazAttack01'),
                        bs.getsound('gummyspazAttack02'),
                        bs.getsound('gummyspazAttack03'),
                        bs.getsound('gummyspazAttack04'),
                    ]
                    self.node.impact_sounds = [
                        bs.getsound('gummyspazImpact01'),
                        bs.getsound('gummyspazImpact02'),
                        bs.getsound('gummyspazImpact03'),
                        bs.getsound('gummyspazImpact04'),
                    ]
                    self.node.death_sounds = [bs.getsound('gummyspazDeath01')]
                    self.node.pickup_sounds = [bs.getsound('gummyspazPickup01')]
                    self.node.fall_sounds = [bs.getsound('gummyspazFall01')]

                    
                    return True
            elif cosmetic == 'YBS16':
                    self.node.jump_sounds = [bs.getsound('robloxnoobJump')]
                    self.node.attack_sounds = [
                        bs.getsound('robloxnoobAttack'),
                    ]
                    self.node.impact_sounds = [
                        bs.getsound('robloxnoobHurt'),
                  
                    ]
                    self.node.death_sounds = [bs.getsound('robloxianDeath')]
                    self.node.pickup_sounds = [bs.getsound('robloxnoobGrab')]
                    self.node.fall_sounds = [bs.getsound('robloxnoobFall')]

                    self.node.head_mesh = bs.getmesh('YBS16Head')
                    self.node.torso_mesh = bs.getmesh('robloxnoobTorso')
                    self.node.upper_arm_mesh = bs.getmesh('robloxnoobArm')
                    self.node.upper_leg_mesh = bs.getmesh('robloxnoobLeg')
                    self.node.style = 'agent'
                    self.node.color_texture = bs.gettexture('YBS16Color')
                    self.node.color_mask_texture = bs.gettexture('YBS16ColorMask')
                    self.node.forearm_mesh = None
                    self.node.hand_mesh = None
                    self.node.lower_leg_mesh = None
                    self.node.pelvis_mesh = None
                    self.node.toes_mesh = None
                    
                    return True
        
        elif character == 'Snake Shadow':
            if cosmetic == 'Ninjaling':
                self.node.style = 'agent'
                self.node.color_texture = bs.gettexture('ninjalingColor')
                self.node.color_mask_texture = bs.gettexture('ninjalingColorMask')
                self.node.forearm_mesh = bs.getmesh('ninjalingForeArm')
                self.node.hand_mesh = bs.getmesh('ninjalingHand')
                self.node.head_mesh = bs.getmesh('ninjalingHead')
                self.node.lower_leg_mesh = bs.getmesh('ninjalingLowerLeg')
                self.node.pelvis_mesh = bs.getmesh('ninjalingPelvis')
                self.node.toes_mesh = bs.getmesh('ninjalingToes')
                self.node.torso_mesh = bs.getmesh('ninjalingTorso')
                self.node.upper_arm_mesh = bs.getmesh('ninjalingUpperArm')
                self.node.upper_leg_mesh = bs.getmesh('ninjalingUpperLeg')
                return True
            elif cosmetic == 'Jolly':
                    self.node.color_texture = bs.gettexture('santaNinjaColor')
                    self.node.color_mask_texture = bs.gettexture('santaNinjaColorMask')
                    self.node.forearm_mesh = bs.getmesh('santaNinjaForeArm')
                    self.node.hand_mesh = bs.getmesh('santaNinjaHand')
                    self.node.head_mesh = bs.getmesh('santaNinjaHead')
                    self.node.lower_leg_mesh = bs.getmesh('santaNinjaLowerLeg')
                    self.node.pelvis_mesh = bs.getmesh('santaNinjaPelvis')
                    self.node.toes_mesh = bs.getmesh('santaNinjaToes')
                    self.node.torso_mesh = bs.getmesh('santaNinjaTorso')
                    self.node.upper_arm_mesh = bs.getmesh('santaNinjaUpperArm')
                    self.node.upper_leg_mesh = bs.getmesh('santaNinjaUpperLeg')
                    

                    
                    return True
        
        elif character == 'Mel':
            if cosmetic == 'Melling':
                self.node.style = 'mel'
                self.node.color_texture = bs.gettexture('fatassColor')
                self.node.color_mask_texture = bs.gettexture('fatassColorMask')
                self.node.forearm_mesh = bs.getmesh('fatassForeArm')
                self.node.hand_mesh = bs.getmesh('fatassHand')
                self.node.head_mesh =bs.getmesh('fatassHead')
                self.node.lower_leg_mesh = bs.getmesh('fatassLowerLeg')
                self.node.pelvis_mesh = bs.getmesh('invisible')
                self.node.toes_mesh = bs.getmesh('fatassToes')
                self.node.torso_mesh = bs.getmesh('fatassTorso')
                self.node.upper_arm_mesh =bs.getmesh('fatassUpperArm')
                self.node.upper_leg_mesh = bs.getmesh('fatassUpperLeg')

                sounds = [
                    bs.getsound('melling01'),
                    bs.getsound('melling02'),
                    bs.getsound('melling03'),
                    bs.getsound('melling04'),
                    bs.getsound('melling05'),
                    bs.getsound('melling06'),
                    bs.getsound('melling07'),
                ]


                self.node.jump_sounds = sounds
                self.node.attack_sounds = sounds
                self.node.impact_sounds = sounds
                self.node.death_sounds = [bs.getsound('mellingDeath')]
                self.node.pickup_sounds = sounds
                self.node.fall_sounds = [bs.getsound('mellingFall01'), bs.getsound('mellingFall02')]
                return True
        
        elif character == 'Amar':
            if cosmetic == 'Full-Insanity':
                self.node.torso_mesh = bs.getmesh('amarInsaneCosmeticTorso')
                self.node.color_texture = bs.gettexture('amarInsaneCosmeticColor')
                self.node.color_mask_texture = bs.gettexture('amarInsaneCosmeticColor')
                return True
            elif cosmetic == 'Horseless Headless Horseman':
                self.node.head_mesh = bs.getmesh('amarPumpkinHead')
                self.node.color_texture = bs.gettexture('amarPumpkinHeadColor')
                self.node.color_mask_texture = bs.gettexture('amarPumpkinHeadColorMask')
        elif character == 'Penny':
            if cosmetic == 'Star Hoodie':               
                self.node.color_texture = bs.gettexture('hoppiStarHoodieCosmeticColor')     
                return True
        elif character == 'Jack Morgan':
            if cosmetic == 'Gummy Voice Jack':
                    
                    hit_sounds = [
                        bs.getsound('gummyjackHit01'),
                        bs.getsound('gummyjackHit02'),
                        bs.getsound('gummyjackHit03'),
                        bs.getsound('gummyjackHit04'),
                        bs.getsound('gummyjackHit05'),
                        bs.getsound('gummyjackHit06'),
                        bs.getsound('gummyjackHit07'),
                    ]
                    sounds = [bs.getsound('gummyjack01'), bs.getsound('gummyjack02'), bs.getsound('gummyjack03'), bs.getsound('gummyjack04'), bs.getsound('gummyjack05'), bs.getsound('gummyjack06')]
                    self.node.jump_sounds = sounds
                    self.node.attack_sounds = sounds
                    self.node.impact_sounds = hit_sounds
                    self.node.death_sounds = [bs.getsound('gummyjackDeath01')]
                    self.node.pickup_sounds = sounds
                    self.node.fall_sounds = [bs.getsound('gummyjackFall01')]
        elif character == 'Agent Johnson':
            if cosmetic == 'Gummy Voice Agent':
                    
                    agent_sounds = [bs.getsound('gummyagent1'), bs.getsound('gummyagent2'),bs.getsound('gummyagent3'), bs.getsound('gummyagent4')]
                    agent_hit_sounds = [bs.getsound('gummyagentHit1'), bs.getsound('gummyagentHit2')]
                    self.node.jump_sounds = agent_sounds
                    self.node.attack_sounds = agent_sounds
                    self.node.impact_sounds = agent_hit_sounds
                    self.node.death_sounds = [bs.getsound('gummyagentDeath')]
                    self.node.pickup_sounds = agent_sounds
                    self.node.fall_sounds = [bs.getsound('gummyagentFall')]
        elif character == 'Easter Bunny':
            if cosmetic == 'Tophat':
                self.node.color_texture = bs.gettexture('tophatColorCosmetic')
                self.node.color_mask_texture = bs.gettexture('tophatColorCosmeticMask')
                self.node.forearm_mesh = bs.getmesh('IlyichForeArm')
                self.node.hand_mesh = bs.getmesh('IlyichHand')
                self.node.head_mesh =bs.getmesh('IlyichHead')
                self.node.lower_leg_mesh = bs.getmesh('IlyichLowerLeg')
                self.node.toes_mesh = bs.getmesh('IlyichToes')
                self.node.torso_mesh = bs.getmesh('IlyichTorso')
                self.node.upper_arm_mesh =bs.getmesh('IlyichUpperArm')
                self.node.upper_leg_mesh = bs.getmesh('IlyichUpperLeg')
                return True
        return False

    
    def b2b_eletricity(self):
        if self.DMGcharge == 0:
            return
        elif 1 <= self.DMGcharge <= 4:
            color = (0, 0.6, 0)
            count = random.randrange(1, 3)
        elif 5 <= self.DMGcharge <= 6:
            color = (0, 1, 0)
            count = random.randrange(5, 8)
        elif 7 <= self.DMGcharge <= 9:
            color = (1, 1, 0)
            count = random.randrange(12, 23)
        elif 10 <= self.DMGcharge <= 15:
            color = (1, 0.5, 0)
            count = random.randrange(29, 39)
        else:   
            color = (0.5, 0, 0.8)
            count = random.randrange(40, 70)
        
        if self.node:
            
            bs.emitfx(
                    position=(self.node.position),
                    velocity=self.node.velocity,
                    count=count,
                    scale=0.6,
                    spread=3,
                    chunk_type='spark',
                    #color=color
                    ),


        


    @override
    def exists(self) -> bool:
        return bool(self.node)

    @override
    def on_expire(self) -> None:
        super().on_expire()

        # Release callbacks/refs so we don't wind up with dependency loops.
        self._dropped_bomb_callbacks = []
        self.punch_callback = None
        self.pick_up_powerup_callback = None

    def add_dropped_bomb_callback(
        self, call: Callable[[Spaz, bs.Actor], Any]
    ) -> None:
        """
        Add a call to be run whenever this Spaz drops a bomb.
        The spaz and the newly-dropped bomb are passed as arguments.
        """
        assert not self.expired
        self._dropped_bomb_callbacks.append(call)
    
    def _safesetattr(self, node: bs.Node | None, attr: str, val: Any) -> None:
                if node:
                    setattr(node, attr, val)

    @override
    def is_alive(self) -> bool:
        """
        Method override; returns whether ol' spaz is still kickin'.
        """
        return not self._dead

    def _hide_score_text(self) -> None:
        if self._score_text:
            assert isinstance(self._score_text.scale, float)
            bs.animate(
                self._score_text,
                'scale',
                {0.0: self._score_text.scale, 0.2: 0.0},
            )

    def _turbo_filter_add_press(self, source: str) -> None:
        """
        Can pass all button presses through here; if we see an obscene number
        of them in a short time let's shame/pushish this guy for using turbo.
        """
        if self.is_amiibo:
            # ignore for amiibo because cmon bruh
            return
        t_ms = int(bs.basetime() * 1000.0)
        assert isinstance(t_ms, int)
        t_bucket = int(t_ms / 1000)
        if t_bucket == self._turbo_filter_time_bucket:
            # Add only once per timestep (filter out buttons triggering
            # multiple actions).
            if t_ms != self._turbo_filter_times.get(source, 0):
                self._turbo_filter_counts[source] = (
                    self._turbo_filter_counts.get(source, 0) + 1
                )

                self._turbo_filter_times[source] = t_ms
                # (uncomment to debug; prints what this count is at)
                # bs.broadcastmessage( str(source) + " "
                #                   + str(self._turbo_filter_counts[source]))
                if self._turbo_filter_counts[source] == 15:
                    # Knock 'em out.  That'll learn 'em.
                    assert self.node
                    self.node.handlemessage('knockout', 500.0)

                    # Also issue periodic notices about who is turbo-ing.
                    now = bs.apptime()
                    assert bs.app.classic is not None
                    if now > bs.app.classic.last_spaz_turbo_warn_time + 30.0:
                        bs.app.classic.last_spaz_turbo_warn_time = now
                        bs.broadcastmessage(
                            bs.Lstr(
                                translate=(
                                    'statements',
                                    (
                                        'Warning to ${NAME}:  '
                                        'turbo / button-spamming knocks'
                                        ' you out.'
                                    ),
                                ),
                                subs=[('${NAME}', self.node.name)],
                            ),
                            color=(1, 0.5, 0),
                        )
                        bs.getsound('error').play()
        else:
            self._turbo_filter_times = {}
            self._turbo_filter_time_bucket = t_bucket
            self._turbo_filter_counts = {source: 1}

    def set_score_text(
        self,
        text: str | bs.Lstr,
        color: Sequence[float] = (1.0, 1.0, 0.4),
        flash: bool = False,
    ) -> None:
        """
        Utility func to show a message momentarily over our spaz that follows
        him around; Handy for score updates and things.
        """
        color_fin = bs.safecolor(color)[:3]
        if not self.node:
            return
        if not self._score_text:
            start_scale = 0.0
            mnode = bs.newnode(
                'math',
                owner=self.node,
                attrs={'input1': (0, 1.4, 0), 'operation': 'add'},
            )
            self.node.connectattr('torso_position', mnode, 'input2')
            self._score_text = bs.newnode(
                'text',
                owner=self.node,
                attrs={
                    'text': text,
                    'in_world': True,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'color': color_fin,
                    'scale': 0.02,
                    'h_align': 'center',
                },
            )
            mnode.connectattr('output', self._score_text, 'position')
        else:
            self._score_text.color = color_fin
            assert isinstance(self._score_text.scale, float)
            start_scale = self._score_text.scale
            self._score_text.text = text
        if flash:
            combine = bs.newnode(
                'combine', owner=self._score_text, attrs={'size': 3}
            )
            scl = 1.8
            offs = 0.5
            tval = 0.300
            for i in range(3):
                cl1 = offs + scl * color_fin[i]
                cl2 = color_fin[i]
                bs.animate(
                    combine,
                    'input' + str(i),
                    {0.5 * tval: cl2, 0.75 * tval: cl1, 1.0 * tval: cl2},
                )
            combine.connectattr('output', self._score_text, 'color')

        bs.animate(self._score_text, 'scale', {0.0: start_scale, 0.2: 0.02})
        self._score_text_hide_timer = bs.Timer(
            1.0, bs.WeakCall(self._hide_score_text)
        )

    def on_jump_press(self) -> None:
        """
        Called to 'press jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node:
            return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        if t_ms - self.last_jump_time_ms >= self._jump_cooldown:
            self.node.jump_pressed = True
            self.last_jump_time_ms = t_ms
        self._turbo_filter_add_press('jump')

    def on_jump_release(self) -> None:
        """
        Called to 'release jump' on this spaz;
        used by player or AI connections.
        """
        if not self.node:
            return
        self.node.jump_pressed = False

    def on_pickup_press(self) -> None:
        """
        Called to 'press pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node:
            return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        if t_ms - self.last_pickup_time_ms >= self._pickup_cooldown:
            self.node.pickup_pressed = True
            self.last_pickup_time_ms = t_ms
        self._turbo_filter_add_press('pickup')

    def on_pickup_release(self) -> None:
        """
        Called to 'release pick-up' on this spaz;
        used by player or AI connections.
        """
        if not self.node:
            return
        self.node.pickup_pressed = False

    def on_hold_position_press(self) -> None:
        """
        Called to 'press hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.hold_position_pressed = True
        self._turbo_filter_add_press('holdposition')

    def on_hold_position_release(self) -> None:
        """
        Called to 'release hold-position' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.hold_position_pressed = False

    def on_punch_press(self) -> None:
        """
        Called to 'press punch' on this spaz;
        used for player or AI connections.
        """
        if not self.node or self.frozen or self.node.knockout > 0.0:
            return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        if t_ms - self.last_punch_time_ms >= self._punch_cooldown:
            if self.punch_callback is not None:
                self.punch_callback(self)
            self._punched_nodes = set()  # Reset this.
            self.last_punch_time_ms = t_ms
            self.node.punch_pressed = True
            if not self.node.hold_node:
                bs.timer(
                    0.1,
                    bs.WeakCall(
                        self._safe_play_sound,
                        SpazFactory.get().swish_sound,
                        0.8,
                    ),
                )
        self._turbo_filter_add_press('punch')

    def _safe_play_sound(self, sound: bs.Sound, volume: float) -> None:
        """Plays a sound at our position if we exist."""
        if self.node:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                sound.play(volume, self.node.position)

    def on_punch_release(self) -> None:
        """
        Called to 'release punch' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.punch_pressed = False

    def on_bomb_press(self) -> None:
        """
        Called to 'press bomb' on this spaz;
        used for player or AI connections.
        """
        # if we have an ass bomb, dont even do this check cuz we're gonna die:
        if  self.ass_bomb:
            if (
                not self.node
                or self._dead
                #or self.frozen
                #or self.node.knockout > 0.0
                
            ):
                return
        else:
            if (
                not self.node
                or self._dead
                or self.frozen
                or self.node.knockout > 0.0
                
            ):
                return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        if t_ms - self.last_bomb_time_ms >= self._bomb_cooldown:
            self.last_bomb_time_ms = t_ms
            self.node.bomb_pressed = True
            if not self.node.hold_node:
                self.drop_bomb()
        self._turbo_filter_add_press('bomb')

    def on_bomb_release(self) -> None:
        """
        Called to 'release bomb' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.bomb_pressed = False

    def on_run(self, value: float) -> None:
        """
        Called to 'press run' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        t_ms = int(bs.time() * 1000.0)
        assert isinstance(t_ms, int)
        self.last_run_time_ms = t_ms
        self.node.run = value * self.speed_mult

        # Filtering these events would be tough since its an analog
        # value, but lets still pass full 0-to-1 presses along to
        # the turbo filter to punish players if it looks like they're turbo-ing.
        if self._last_run_value < 0.01 and value > 0.99:
            self._turbo_filter_add_press('run')

        self._last_run_value = value

    def on_fly_press(self) -> None:
        """
        Called to 'press fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        # Not adding a cooldown time here for now; slightly worried
        # input events get clustered up during net-games and we'd wind up
        # killing a lot and making it hard to fly.. should look into this.
        self.node.fly_pressed = True
        self._turbo_filter_add_press('fly')

    def on_fly_release(self) -> None:
        """
        Called to 'release fly' on this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.fly_pressed = False

    def on_move(self, x: float, y: float) -> None:
        """
        Called to set the joystick amount for this spaz;
        used for player or AI connections.
        """
        if not self.node:
            return
        self.node.handlemessage('move', x, y)

    def on_move_up_down(self, value: float) -> None:
        """
        Called to set the up/down joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use on_move instead.
        """
        if not self.node:
            return
        self._input_y = value
        #self.node.move_up_down = value * self.speed_mult

    def on_move_left_right(self, value: float) -> None:
        """
        Called to set the left/right joystick amount on this spaz;
        used for player or AI connections.
        value will be between -32768 to 32767
        WARNING: deprecated; use on_move instead.
        """
        if not self.node:
            return
        self._input_x = value
        #self.node.move_left_right = value * self.speed_mult

    def on_punched(self, damage: int) -> None:
        """Called when this spaz gets punched."""
    
    def give_spaz_ass_bomb_lmfao(self):
        PopupText('!!!',
                    color=(1, 0, 0, 1),
                    scale=0.8,
                    position = self.node.position
                                ).autoretain()
        self.ass_bomb = True
    
    def _smoke_puff(self, scale=1.0):
        """Spawn a smoke puff at the Spaz's position."""
        if not self.node:
            return
        pos = self.node.position

        # Create an overlay effect node (smoke)
        smoke = bs.newnode(
            'flash',
            attrs={
                'position': pos,
                'size': scale,
                'color': (1, 1, 1)
            }
        )

        # Auto-remove
        bs.timer(0.25, smoke.delete)
    def perma_cloak(self):

        if not self.node:
            return
    
       
        
        def cloak():
            if not self.node:
                return
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('CloakUse').play()
            self.on_hold_position_release()

            self.node.counter_text = ''
            self.node.counter_texture = None
            self.node.head_mesh = None
            self.node.torso_mesh = None
            self.node.pelvis_mesh = None
            self.node.upper_arm_mesh = None
            self.node.forearm_mesh = None
            self.node.hand_mesh = None
            self.node.upper_leg_mesh = None
            self.node.lower_leg_mesh = None
            self.node.toes_mesh = None
            self.node.name = ''
            self.node.style = 'ali'
            self.node.is_area_of_interest = False
            self.node.boxing_gloves = False

        # Alrigjt, start it!
        self.handlemessage(bs.CelebrateMessage(1, 'left'))
        self.on_hold_position_press()
        bs.timer(0.8, lambda: self._smoke_puff(scale=2.1))
        bs.timer(1, cloak)

        
 
    def cloak(self):
        if self.cloaked:
            return
        
        if not self.node:
            return
        
        self.cloaked = True
        self.effects.append('undetectable')

        # Save our meshes
        head_mesh = self.node.head_mesh
        torso_mesh = self.node.torso_mesh
        pelvis_mesh = self.node.pelvis_mesh
        upper_arm_mesh = self.node.upper_arm_mesh
        forearm_mesh = self.node.forearm_mesh
        hand_mesh = self.node.hand_mesh
        upper_leg_mesh = self.node.upper_leg_mesh
        lower_leg_mesh = self.node.lower_leg_mesh
        toes_mesh = self.node.toes_mesh
        name = self.node.name
        style = self.node.style
        hitpoints = self.hitpoints
        was_area_of_interest = self.node.is_area_of_interest

        
        
        def cloak():
            if not self.node:
                return
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('CloakUse').play()
            self.on_hold_position_release()
            # hide billboard stuff
            self.node.mini_billboard_1_start_time = 1
            self.node.mini_billboard_1_end_time = 2
            self.node.mini_billboard_2_start_time = 1
            self.node.mini_billboard_2_end_time = 2
            self.node.mini_billboard_3_start_time = 1
            self.node.mini_billboard_3_end_time = 2
            # we are NOT reverting this lol
            self.reset_counts()
            self.node.counter_text = ''
            self.node.counter_texture = None
            self.node.head_mesh = None
            self.node.torso_mesh = None
            self.node.pelvis_mesh = None
            self.node.upper_arm_mesh = None
            self.node.forearm_mesh = None
            self.node.hand_mesh = None
            self.node.upper_leg_mesh = None
            self.node.lower_leg_mesh = None
            self.node.toes_mesh = None
            self.node.name = ''
            self.node.style = 'ali'
            self.node.is_area_of_interest = False
            self.node.boxing_gloves = False

                   

        def uncloak():
            if not self.node:
                return
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('CloakUse').play(1.5)
            self.on_hold_position_press()
            self.handlemessage(bs.CelebrateMessage(0.3, 'right'))
            bs.timer(0.25, lambda: self._smoke_puff(scale=1.5))
            bs.timer(0.3, self.on_hold_position_release)
            self.uncloak_timer = None
            self.uncloak_tick_timer = None
            bs.timer(0.31, lambda: setattr(self, 'cloaked', False))
            try:
                self.effects.remove('undetectable')
            except: pass
            self.node.head_mesh = head_mesh
            self.node.torso_mesh = torso_mesh
            self.node.pelvis_mesh = pelvis_mesh 
            self.node.upper_arm_mesh = upper_arm_mesh
            self.node.forearm_mesh = forearm_mesh
            self.node.hand_mesh = hand_mesh
            self.node.upper_leg_mesh = upper_leg_mesh
            self.node.lower_leg_mesh = lower_leg_mesh
            self.node.toes_mesh = toes_mesh
            self.node.name = name
            self.node.style = style
            self.node.boxing_gloves = self._has_boxing_gloves
            self.node.is_area_of_interest = was_area_of_interest
        
        # Alrigjt, start it!
        self.handlemessage(bs.CelebrateMessage(1, 'left'))
        self.on_hold_position_press()
        bs.timer(0.8, lambda: self._smoke_puff(scale=2.1))
        bs.timer(1, cloak)

        self.uncloak_timer = bs.Timer(13, uncloak)
        

        def cloak_tick():
            # Um, why are we knocked out?
            if self.node.knockout != 0:
                uncloak()
            
            if not self.is_alive():
                uncloak()

        
        self.uncloak_tick_timer = bs.Timer(0.1, cloak_tick, repeat=True)



    def get_death_points(self, how: bs.DeathType) -> tuple[int, int]:
        """Get the points awarded for killing this spaz."""
        del how  # Unused.
        num_hits = float(max(1, self._num_times_hit))

        # Base points is simply 10 for 1-hit-kills and 5 otherwise.
        importance = 2 if num_hits < 2 else 1
        return (10 if num_hits < 2 else 5) * self.points_mult, importance
    
    def uneletric(self):
        "uneletric the spaz."
        if self.eletricuted and self.node:
            self.eletricuted = False
            self.impact_scale *= 2
            timer = 0.5
            timer2 = 10
            bs.animate_array(self.node,'color', 3,
                        {
                        timer:(0.005, 0.15, 0.5),
                        timer2: self.default_color
                        }
                    )
        

    def eletric(self):
        "the actual damage from eletricity."
        if self.eletricuted and self.node:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('eletricHurt').play(),
            timer = 0.8
            self.handlemessage(
                bs.HitMessage(
                pos=self.node.position,
                force_direction=self.node.velocity,
                )
            )
            bs.emitfx(
                    position=(self.node.position),
                    velocity=self.node.velocity,
                    count=random.randrange(40, 70),
                    scale=4.0,
                    spread=0.2,
                    chunk_type='sweat'
                    ),
            if self.shield:
                self.shield_hitpoints -= 21 / 2
                self.hitpoints -= 21 / 2
                self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )
            else:
                self.hitpoints -= 21
                self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )
            bs.animate_array(self.node,'color', 3,
                        {
                        0:(0.1, 0.7, 2),
                        timer: (0.005, 0.15, 0.5),
                        }
                    )
            if self.hitpoints <= 0:
                if self.totem < 1:
                    self.shatter(extreme=True),
                    from bascenev1lib.mainmenu import MainMenuActivity
                    if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        bs.getsound('eletricKill').play(),
                    self.eletricuted = False
                    self.node.color = (1, 1, 3)
                    self.node.highlight = (1, 1, 3)
                    bs.emitfx(
                        position=(self.node.position),
                        velocity=self.node.velocity,
                        count=100,
                        scale=4.0,
                        spread=1.2,
                        chunk_type='sweat'
                    ),
                
                    

                    self.handlemessage(bs.DieMessage())
                else:
                    self.totem_effect()


    def handleeletric(self):
        """ the handles the damage and effects of being eletricuted. """
        if not self.node:
            return
        self.impact_scale /= 2
        self.eletricuted = True
        timer = 0.5
        bs.timer(timer, bs.Call(self.eletric))
        for i in range(35):
            if self.eletricuted == True:
                timer += 0.5
                bs.timer(timer, bs.Call(self.eletric))
        
        bs.timer (18, bs.Call(self.uneletric))

        
    def handleshieldbreaker(self):
        """ see if the spaz is vulnarable to eletricity, also a shield  break."""
        if self.shield and self.is_alive():
            self.shield_hitpoints -= 450
            if self.eletricuted == False:
                self.handleeletric()
        else:
            if self.is_alive() and self.eletricuted == False:
                self.handleeletric()

    def unboogie(self):
        """Allow our spaz to be boogied again."""
        self.boogieing = False

        
    def boogie(self):
        """Do a little dance, and make our spaz fall over"""
        if not self.boogieing and not self.shield:
            if self.node.invincible:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    SpazFactory.get().block_sound.play(
                        1.0,
                        position=self.node.position,
                    )
            else:
                self.boogieing = True
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('boogieHit').play()
                self.boogieing = True
                bs.timer(5, bs.Call(self.unboogie))
                self.node.handlemessage('celebrate', 5000.0)
                self.node.handlemessage('knockout', 1000.0)

    def curse(self) -> None:
        """
        Give this poor spaz a curse;
        he will explode in 5 seconds.
        """
        if not self._cursed:
            factory = SpazFactory.get()
            self._cursed = True

            # Add the curse material.
            for attr in ['materials', 'roller_materials']:
                materials = getattr(self.node, attr)
                if factory.curse_material not in materials:
                    setattr(
                        self.node, attr, materials + (factory.curse_material,)
                    )

            # None specifies no time limit.
            assert self.node
            self.curse_time = 8
            if self.curse_time is None:
                self.node.curse_death_time = -1
            else:
                # Note: curse-death-time takes milliseconds.
                tval = bs.time()
                assert isinstance(tval, (float, int))
                self.node.curse_death_time = int(
                    1000.0 * (tval + self.curse_time)
                )
                self._curse_timer = bs.Timer(
                    self.curse_time,
                    bs.WeakCall(self.handlemessage, CurseExplodeMessage()),
                )
    def funnycurse(self) -> None:
        """
        Give this dumbass a 30 second curse.
        """
        self.node.color = (1, 0, 0)
        self.node.highlight = (1, 0, 0)
        bs.timer(0.302, lambda: self._safe_play_sound(bs.getsound('nga_moove'), 5))
        bs.timer(2, bs.Call(self.lightninglol))
        bs.timer(2, bs.Call(self.lightninglol))
        if not self._cursed:
            self.curse_time = 30
            factory = SpazFactory.get()
            self._cursed = True

            # Add the curse material.
            for attr in ['materials', 'roller_materials']:
                materials = getattr(self.node, attr)
                if factory.curse_material not in materials:
                    setattr(
                        self.node, attr, materials + (factory.curse_material,)
                    )

            # None specifies no time limit.
            assert self.node
            self.curse_time = 30
            if self.curse_time is None:
                self.node.curse_death_time = -1
            else:
                # Note: curse-death-time takes milliseconds.
                tval = bs.time()
                assert isinstance(tval, (float, int))
                self.node.curse_death_time = int(
                    1000.0 * (tval + self.curse_time)
                )
                self._curse_timer = bs.Timer(
                    self.curse_time,
                    bs.WeakCall(self.handlemessage, CurseExplodeMessage()),
                )

    def wafflecurse(self) -> None:
        """
        0 second curse. specifically for the waffle overdose.
        """
        if not self._cursed:
            self.curse_time = 30
            factory = SpazFactory.get()
            self._cursed = True

            # Add the curse material.
            for attr in ['materials', 'roller_materials']:
                materials = getattr(self.node, attr)
                if factory.curse_material not in materials:
                    setattr(
                        self.node, attr, materials + (factory.curse_material,)
                    )

            # None specifies no time limit.
            assert self.node
            self.curse_time = 0
            if self.curse_time is None:
                self.node.curse_death_time = -1
            else:
                # Note: curse-death-time takes milliseconds.
                tval = bs.time()
                assert isinstance(tval, (float, int))
                self.node.curse_death_time = int(
                    1000.0 * (tval + self.curse_time)
                )
                self._curse_timer = bs.Timer(
                    self.curse_time,
                    bs.WeakCall(self.handlemessage, CurseExplodeMessage()),
                )

    def unwaffle(self):
        """ unbuff our spaz :(
        
        """
        # multiply the value so we can get our original ones back.
        self._jump_cooldown *= 2.3
        self.impact_scale *= 1.5
        # take 1 overdose point away so we dont overdose when we dont need to
        self.overdose -= 1
        # show the spaz they just lost a buff.
        if self.node:
            PopupText('-1',
                    color=(1, 0.58, 0, 1),
                    scale=1.2,
                    # lets move this so it doesnt get in the way of the actual number.
                    position = (self.node.position[0] + 1, self.node.position[1], self.node.position[2])
                    ).autoretain()
            PopupText(str(self.overdose),
                    color=(1, 1, 1, 1),
                    scale=1.2,
                    position = self.node.position
                    ).autoretain()
        # if they didnt notice, this color changing effect would.
        timer = 0.85
        if self.node:
            bs.animate_array(self.node,'color', 3,
                        {
                        0:(0.8, 0.6, 0.2),
                        timer: self.default_color,
                        }
            )
        # and if they STILL didnt notice, this partical effect would.
        if self.node:
            bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=1,
                    spread=0,
                    scale=3,
                    chunk_type='slime',
                )


    def waffle(self):
        """Give our spaz a delicious waffle! (and some buffs)


        but if they overdose... they'll be knocked out and then spontaneously combust.
        """
        self.overdose += 1
        if self.overdose <= 3:
            timer = 0.85
            bs.animate_array(self.node,'color', 3,
                        {
                        0:(1, 0.8, 0.4),
                        timer: self.default_color,
                        }
                    )
            if not self.overdose == 3:
                PopupText(str(self.overdose),
                    color=(1, 1, 1, 1),
                    scale=1.2,
                    position = self.node.position
                                ).autoretain()
            else:
                PopupText(str(self.overdose),
                    color=(1, 0.5, 0, 1),
                    scale=1.5,
                    position = self.node.position
                    ).autoretain()
                npos = self.node.position
                bs.emitfx(
                        position=(npos[0], npos[1] + 0.9, npos[2]),
                        velocity=self.node.velocity,
                        count=random.randrange(40, 70),
                        scale=4.0,
                        spread=0.2,
                        chunk_type='sweat'
                    ),
            bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=1,
                    spread=0,
                    scale=3,
                    chunk_type='slime',
                )
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('yummers').play()
            # add some da buffs.
            self.hitpoints += self.hitpoints_max * 0.15
            self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )
            self._jump_cooldown /= 2.3
            self.impact_scale /= 1.5
            # now we put a timer to debuff
            bs.timer(45, bs.Call(self.unwaffle))


        else:
            # oops! too much. knock this spaz out forever then blow him up.
            PopupText(str(self.overdose),
                    color=(1, 0, 0, 1),
                    scale=1.8,
                    position = self.node.position
                                ).autoretain()
            self.node.handlemessage('knockout', 999999999)
            # hehe jrmp callback
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('hijumped').play()
            bs.timer(1.7, bs.Call(self.wafflecurse))
    
    def equip_boxing_gloves(self) -> None:
        """
        Give this spaz some boxing gloves.
        """
        assert self.node
        self.node.boxing_gloves = True
        self._has_boxing_gloves = True
        if self._demo_mode:  # Preserve old behavior.
            self._punch_power_scale = 1.7
            self._punch_cooldown = 300
        else:
            # fukc it dawg, idc
            factory = SpazFactory.get()
            self._punch_power_scale *= 1.25 #= factory.punch_power_scale_gloves
            self._punch_cooldown /= 1.33 #=factory.punch_cooldown_gloves

    def equip_shields(self, decay: bool = False, color: tuple = None) -> None:
        """
        Give this spaz a nice energy shield.
        """

        if not self.node:
            logging.exception('Can\'t equip shields; no node.')
            return
        


        factory = SpazFactory.get()
        
        if self.shield:
            self.shield.delete()
        self.shield = bs.newnode(
            'shield',
            owner=self.node,
            attrs={'color': bs.safecolor(self.Dcolor) if not color else color, 'radius': 1.3},
        )
        self.node.connectattr('position_center', self.shield, 'position')
        self.shield_hitpoints = self.shield_hitpoints_max = (650 * (1 + (1.25*self.every_instance_in_abilities('Shield Health ↑'))))
        
        
        self.shield_decay_rate = factory.shield_decay_rate if decay else 0
        self.shield.hurt = 0
        from bascenev1lib.mainmenu import MainMenuActivity
        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
            factory.shield_up_sound.play(1.0, position=self.node.position)

        if self.shield_decay_rate > 0:
            self.shield_decay_timer = bs.Timer(
                0.5, bs.WeakCall(self.shield_decay), repeat=True
            )
            # So user can see the decay.
            self.shield.always_show_health_bar = True


    def shield_decay(self) -> None:
        """Called repeatedly to decay shield HP over time."""
        if self.shield:
            assert self.shield_hitpoints is not None
            self.shield_hitpoints = max(
                0, self.shield_hitpoints - self.shield_decay_rate
            )
            assert self.shield_hitpoints is not None
            self.shield.hurt = (
                1.0 - float(self.shield_hitpoints) / self.shield_hitpoints_max
            )
            if self.shield_hitpoints <= 0:
                self.shield.delete()
                self.shield = None
                self.shield_decay_timer = None
                assert self.node
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    SpazFactory.get().shield_down_sound.play(
                    1.0,
                    position=self.node.position,
                )
        else:
            self.shield_decay_timer = None

    def start_swirling_icon(self) -> None:
        """
            Creates a swirling icon that orbits around a given node.
    
            :param node: The node around which the icon will swirl.
        """
        if not self.node:
            return

        # Create the swirling icon
        self.swirl_icon = bs.newnode(
        'text',
        owner=self.node,
        attrs={
            'text': '⭑',
            'in_world': True,
            'position': (0, 1.4, 0),
            'shadow': 1.0,
            'flatness': 1.0,
            'color': (0, 1, 0),
            'scale': 0.025,
            'h_align': 'center',
        },
    )

        mnode = bs.newnode(
        'math',
        owner=self.node,
        attrs={'input1': (0, 0, 0), 'operation': 'add'},
    )
        self.node.connectattr('torso_position', mnode, 'input2')
        mnode.connectattr('output', self.swirl_icon, 'position')


        speed = 1
        t = bs.time() % 360  # Loop time
        angle = 30 * math.sin(t)  # Rotate between -30 and +30 degrees
        bs.animate(self.swirl_icon, 'rotate', {0: angle, speed: angle + 360}, loop=True)
        self.updateCharge = True
        bs.timer(0.1, self.update_icon, repeat=True)


    def update_icon(self):
        if self.swirl_icon and self.updateCharge:
            icon = self.swirl_icon

            if 1 <= self.DMGcharge <= 4:
                icon.color = (0, 0.6, 0)
                icon.scale = 0.025
                icon.text = '✦'
            elif 5 <= self.DMGcharge <= 6:
                icon.color = (0, 1, 0)
                icon.text = '★'
            
            elif 7 <= self.DMGcharge <= 9:
                icon.color = (1, 1, 0)
                icon.text = '✪'

            elif 10 <= self.DMGcharge <= 15:
                icon.color = (1, 0.5, 0)
                icon.text = '❂'

            else:   
                icon.color = (0.5, 0, 0.8)
                icon.text = '𖣔'





    def remove_swirling_icon(self) -> None:
        """
        Removes the swirling icon if it exists.
        """
        if self.swirl_icon:
            self.swirl_icon.delete()
            self.swirl_icon = None
    
    def show_charge_text(
        self,
        flash: bool = False,
    ) -> None:
        """
        """
        b2b_1 = bs.getsound('b2b_1')
        b2b_2 = bs.getsound('b2b_2')
        b2b_3 = bs.getsound('b2b_3')
        b2b_4 = bs.getsound('b2b_4')
        b2b_warn = bs.getsound('b2b_5')

        if 1 <= self.DMGcharge <= 4:
            color = (0, 0.6, 0)
            marks = ''
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_1.play()
        elif 5 <= self.DMGcharge <= 6:
            color = (0, 1, 0)
            marks = '!'
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_2.play()
        elif 7 <= self.DMGcharge <= 9:
            color = (1, 1, 0)
            marks = '!!'
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_3.play()
        elif 10 <= self.DMGcharge <= 15:
            color = (1, 0.5, 0) 
            marks = '!!!'
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_4.play()
        else:
            color = (0.5, 0, 0.8)
            marks = '!!!!'
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_4.play()

        if self.DMGcharge == 16:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                b2b_warn.play()

    
        # Idk bout the marks
        marks = ''

        text = '*' + str(self.DMGcharge) + marks
        color_fin = color
        if not self.node:
            return
        if not self._charge:
            self.start_swirling_icon()
            mnode = bs.newnode(
                'math',
                owner=self.node,
                attrs={'input1': (0, 1.4, 0), 'operation': 'add'},
            )
            self.node.connectattr('torso_position', mnode, 'input2')
            self._charge = bs.newnode(
                'text',
                owner=self.node,
                attrs={
                    'text': text,
                    'in_world': True,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'color': color_fin,
                    'scale': 0.02,
                    'h_align': 'center',
                },
            )
            mnode.connectattr('output', self._charge, 'position')
        else:
            self._charge.color = color_fin
            assert isinstance(self._charge.scale, float)
            self._charge.text = text
        if True:
            combine = bs.newnode(
                'combine', owner=self._charge, attrs={'size': 3}
            )
            scl = 1.8
            offs = 0.5
            tval = 0.300
            for i in range(3):
                cl1 = offs + scl * color_fin[i]
                cl2 = color_fin[i]
                bs.animate(
                    combine,
                    'input' + str(i),
                    {0.5 * tval: cl2, 0.75 * tval: cl1, 1.0 * tval: cl2},
                )
            combine.connectattr('output', self._charge, 'color')


    def _hide_charge_text(self, fake: bool = False) -> None:
        self.updateCharge = False
        self.allow_new_charge = False
        b2b_S = bs.getsound('b2b_releaseS')
        b2b_M = bs.getsound('b2b_releaseM')
        b2b_L = bs.getsound('b2b_releaseL')
        b2b_XL = bs.getsound('b2b_releaseXL')

        
        
        if self._charge:
            if 1 <= self.DMGcharge <= 2:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_S.play()
            elif 3 <= self.DMGcharge <= 4:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_M.play()
            elif 5 <= self.DMGcharge <= 6:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_L.play()
            elif 7 <= self.DMGcharge <= 8:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_XL.play()
            else:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    b2b_XL.play()
            
        
            assert isinstance(self._charge.scale, float)
            self._charge.color = (1, 1, 1)
            bs.animate(
                self._charge,
                'scale',
                {0.0: self._charge.scale, 0.12: self._charge.scale * 2, 0.4: 0},
            )
            if self.swirl_icon:
                bs.animate(
                self.swirl_icon,
                'scale',
                {0.0: self.swirl_icon.scale, 0.12: 0},
                )
            def delete():
                self._charge.delete()

                if self.is_alive():
                    self.DMGcharge = 0
                self.allow_new_charge = True

                if self.swirl_icon:
                    self.remove_swirling_icon()
                # Make sure we have no charge
                
            bs.timer(0.41, delete)

    def add_charge(self, value: int = 1): 
        if not self.allow_new_charge:
            return
        self.DMGcharge += value
        self.show_charge_text()

        # if we're starting the charge, play a neat sfx.
        if self.DMGcharge == 1:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('b2b_start').play()
    
    def fuckyou(self):
        self._cursed = True
        self.curse_explode()
    def flybitch(self):
        if self.node:
            for _ in range(50):
                                self.node.handlemessage('impulse', self.node.position[0], self.node.position[1], self.node.position[2],
                                                                0, 25, 0,
                                                                6000, 0.05, 0, 0,
                                                                0, 250, 0)
    def fake_screen_ko(self):
        self.getactivity().session.do_screen_ko(self.character, self.node.position[0], self.default_color, self.default_highlight)
    def screen_ko(self):
        if not self.node:
            return
        if self.attempted_screen_ko:
            return
        self.attempted_screen_ko = True
        # Tell the session to handle a screen ko
        self.getactivity().session.do_screen_ko(self.character, self.node.position[0], self.default_color, self.default_highlight)
        # Kill our node so a body doesnt come down from the sky and no sounds

        # die normally first??
        self.handlemessage(bs.DieMessage(how=bs.DeathType.FALL))
        self.handlemessage(bs.DieMessage(immediate=True, how=bs.DeathType.OUT_OF_BOUNDS))
    @override
    def handlemessage(self, msg: Any) -> Any:
        # pylint: disable=too-many-return-statements
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        assert not self.expired

        if isinstance(msg, bs.PickedUpMessage):
            if self.node:
                self.node.handlemessage('hurt_sound')
                self.node.handlemessage('picked_up')

            # This counts as a hit.
            self._num_times_hit += 1

        elif isinstance(msg, FootingMessage):
     
            self.standing = msg.footing == 1

        elif isinstance(msg, bs.ShouldShatterMessage):
            # Eww; seems we have to do this in a timer or it wont work right.
            # (since we're getting called from within update() perhaps?..)
            # NOTE: should test to see if that's still the case.
            bs.timer(0.001, bs.WeakCall(self.shatter))

        elif isinstance(msg, bs.ImpactDamageMessage):
            # Eww; seems we have to do this in a timer or it wont work right.
            # (since we're getting called from within update() perhaps?..)
            bs.timer(0.001, bs.WeakCall(self._hit_self, msg.intensity))

        elif isinstance(msg, bs.PowerupMessage):
            if self._dead or not self.node:
                return True
            
            if not self.can_accept_powerups:
                return False
            if self.pick_up_powerup_callback is not None:
                self.pick_up_powerup_callback(self)

            if 'undetectable' in self.effects:
                return True
            
            
            

            if msg.poweruptype == 'cloak':
                self.cloak()
            elif msg.poweruptype == 'kys':
                self.give_spaz_ass_bomb_lmfao()
            elif msg.poweruptype == 'triple_bombs':
                tex = PowerupBoxFactory.get().tex_bomb
                self._flash_billboard(tex)
                self.set_bomb_count(3)
                if self.powerups_expire:
                    self.node.mini_billboard_1_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_1_start_time = t_ms
                    self.node.mini_billboard_1_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._multi_bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._multi_bomb_wear_off_flash),
                    )
                    self._multi_bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._multi_bomb_wear_off),
                    )
            elif msg.poweruptype == 'stack':
                tex = PowerupBoxFactory.get().tex_stack
                self._flash_billboard(tex)
                self.set_bomb_count(self._max_bomb_count + 5)
                if self.powerups_expire:
                    self.node.mini_billboard_1_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_1_start_time = t_ms
                    self.node.mini_billboard_1_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._multi_bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._multi_bomb_wear_off_flash),
                    )
                    self._multi_bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._multi_bomb_wear_off),
                    )
            elif msg.poweruptype == 'land_mines':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_land_mine_count(min(self.land_mine_count + 3, 5))
            elif msg.poweruptype == 'promine':
                self.set_rock_count(min(0, 5))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_promine_count(min(self.promine_count + 1, 3))
            elif msg.poweruptype == 'rock':
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_land_mine_count(0)
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_rock_count(min(self.rock_count + 1, 3))
            elif msg.poweruptype == 'egg':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_egg_count(min(self.egg_count + 12, 20))
            elif msg.poweruptype == 'mini':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_boogie_count(min(0, 2))
                self.set_land_mine_count(0)
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_mini_count(min(self.mini_count + 10, 25))
            elif msg.poweruptype == 'boogie':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_boogie_count(min(self.boogie_count + 1, 2))
            elif msg.poweruptype == 'star':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_star_count(min(self.star_count + 2, 4))
            elif msg.poweruptype == 'heart':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_land_mine_count(0)
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_heart_count(min(self.heart_count + 1, 3))
            elif msg.poweruptype == "boom":
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_totem_count(0)
                self.set_bed_count(0)
                self.set_boom_count(min(self.boom_count + 1, 3))
            elif msg.poweruptype == 'totem':
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_land_mine_count(0)
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_bed_count(0)
                
                self.set_totem_count(min(self.totem + 1, 2))
            elif msg.poweruptype == 'bed':
                
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_land_mine_count(0)
                self.set_totem_count(0)
                self.set_bed_count(min(self.beds + 1, 5))
            elif msg.poweruptype == 'breaker':
                self.bomb_type = 'breaker'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'impact_bombs':
                self.bomb_type = 'impact'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'sticky_bombs':
                self.bomb_type = 'sticky'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'impulse':
                self.bomb_type = 'impulse'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'lightning':
                self.bomb_type = 'lightning'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'random':
                self.bomb_type = 'random'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'faker':
                self.node.handlemessage('knockout', 500.0),
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('boowomp').play(),

            elif msg.poweruptype == 'negative':
                self.bomb_type = 'negative'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'punch':
                tex = PowerupBoxFactory.get().tex_punch
                self._flash_billboard(tex)
                self.equip_boxing_gloves()
                if self.powerups_expire and not self.default_boxing_gloves:
                    self.node.boxing_gloves_flashing = False
                    self.node.mini_billboard_3_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_3_start_time = t_ms
                    self.node.mini_billboard_3_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._boxing_gloves_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._gloves_wear_off_flash),
                    )
                    self._boxing_gloves_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._gloves_wear_off),
                    )
            elif msg.poweruptype == 'shield':
                factory = SpazFactory.get()
                # Let's allow powerup-equipped shields to lose hp over time.
                self.equip_shields(decay=factory.shield_decay_rate > 0)
            elif msg.poweruptype == 'curse':
                self.curse()
            elif msg.poweruptype == 'waffle':
                self.waffle()
            elif msg.poweruptype == 'what':
                self.funnycurse()
                self.equip_shields()
                self.frozen = True
                self.node.frozen = True
            elif msg.poweruptype == 'ice_bombs':
                self.bomb_type = 'ice'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            elif msg.poweruptype == 'health':
                if self._cursed:
                    self._cursed = False

                    # Remove cursed material.
                    factory = SpazFactory.get()
                    for attr in ['materials', 'roller_materials']:
                        materials = getattr(self.node, attr)
                        if factory.curse_material in materials:
                            setattr(
                                self.node,
                                attr,
                                tuple(
                                    m
                                    for m in materials
                                    if m != factory.curse_material
                                ),
                            )
                    self.node.curse_death_time = 0
                self.hitpoints = self.hitpoints_max
                self.ass_bomb = False
                # Remove any type of charge.
                self._hide_charge_text()
                self.DMGcharge = 0
                self.clear_fire()

                
                self._flash_billboard(PowerupBoxFactory.get().tex_health)
                self.node.hurt = 0
                self._last_hit_time = None
                self._num_times_hit = 0
            
            elif msg.poweruptype == 'gold':
                self.bomb_type = 'gold'
                tex = self._get_bomb_type_tex()
                self._flash_billboard(tex)
                if self.powerups_expire:
                    self.node.mini_billboard_2_texture = tex
                    t_ms = int(bs.time() * 1000.0)
                    assert isinstance(t_ms, int)
                    self.node.mini_billboard_2_start_time = t_ms
                    self.node.mini_billboard_2_end_time = (
                        t_ms + POWERUP_WEAR_OFF_TIME
                    )
                    self._bomb_wear_off_flash_timer = bs.Timer(
                        (POWERUP_WEAR_OFF_TIME - 2000) / 1000.0,
                        bs.WeakCall(self._bomb_wear_off_flash),
                    )
                    self._bomb_wear_off_timer = bs.Timer(
                        POWERUP_WEAR_OFF_TIME / 1000.0,
                        bs.WeakCall(self._bomb_wear_off),
                    )
            

            self.node.handlemessage('flash')
            if msg.sourcenode:
                msg.sourcenode.handlemessage(bs.PowerupAcceptMessage())
            return True   

        elif isinstance(msg, bs.FreezeMessage):
            if not self.node:
                return None

            if self.is_gold:
                # Lets not freeze gold people..
                return None
            if self.node.invincible:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    SpazFactory.get().block_sound.play(
                    1.0,
                    position=self.node.position,
                )
                return None
            if self.shield:
                return None
            if not self.frozen:
                self.frozen = True
                self.node.frozen = True
                # Originally 5.0 Seconds, but it sucks.
                bs.timer(3.5, bs.WeakCall(self.handlemessage, bs.ThawMessage()))
                # Instantly shatter if we're already dead.
                # (otherwise its hard to tell we're dead).
                if self.hitpoints <= 0:
                    self.shatter()
        elif isinstance(msg, bs.ThawMessage):
            if self.frozen and not self.shattered and self.node and not self.is_gold:
                self.frozen = False
                self.node.frozen = False
        elif isinstance(msg, bs.HitMessage):
            if not self.node:
                return None
            
        


            if self.node.invincible:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    SpazFactory.get().block_sound.play(
                    1.0,
                    position=self.node.position,
                )
                return True
            

           

            # If we were recently hit, don't count this as another.
            # (so punch flurries and bomb pileups essentially count as 1 hit).
            local_time = int(bs.time() * 1000.0)
            assert isinstance(local_time, int)
            if (
                self._last_hit_time is None
                or local_time - self._last_hit_time > 1000
            ):
                self._num_times_hit += 1
                self._last_hit_time = local_time


            mag = msg.magnitude * self.impact_scale
            velocity_mag = msg.velocity_magnitude * self.impact_scale
            damage_scale = 0.22   

            if self.cloaked:
                damage_scale *= 1.5
            

            if msg.hit_subtype == 'heart':
                damage_scale = 0.0
            

            if msg.hit_subtype == 'gold':

                # Make bots slower
                self.add_slowness(2 if self.source_player else 5, 7)
            
           
                
                                
            
            



            # Gold Statues
            if self.is_gold:
                # When we're golden we only accept explosions as our hit type (because gold is that durable)
                if msg.hit_type != 'explosion':
                    mag *= 0
                    velocity_mag *= 0
                    damage_scale = 0

            

            if msg.crit_boosted or self.boogieing:
                if msg.crit_type == 'normal' or self.boogieing:
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            SpazFactory.get().crit_sound.play()
                        npos = self.node.position
                        bs.emitfx(
                            position=(npos[0], npos[1] + 0.9, npos[2]),
                            velocity=self.node.velocity,
                            count=random.randrange(40, 70),
                            scale=4.0,
                            spread=0.2,
                            chunk_type='sweat'
                        ),
                        if self.is_alive():
                            bs.timer(0.01, lambda: PopupText('CRITICAL\nHIT!', color=(0.2, 1, 0.2),
                            scale=1.0,
                            position = self.node.position
                            ).autoretain())
                        timer = 1
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(0, 1, 0),
                        timer: self.default_color,
                        }
                        )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(0, 1, 0),
                        timer: self.default_highlight,
                        }
                        )

                        cfg = bui.app.config
                        cfg['GUMMY_statscrit'] = babase.app.config.get('GUMMY_statscrit', 0) + 1
                        cfg.apply_and_commit()
                elif msg.crit_type == 'mini':
                        npos = self.node.position
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            SpazFactory.get().minicrit_sound.play()
                        bs.emitfx(
                            position=(npos[0], npos[1] + 0.9, npos[2]),
                            velocity=self.node.velocity,
                            count=random.randrange(40, 70),
                            scale=4.0,
                            spread=0.2,
                            chunk_type='sweat'
                        ),
                        if self.is_alive():
                            bs.timer(0.01, lambda: PopupText('MINI\nCRIT!', color=(1, 1, 0),
                            scale=0.7,
                            position = self.node.position
                            ).autoretain())
                        timer = 0.6
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(1, 1, 0),
                        timer: self.default_color,
                        }
                        )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(1, 1, 0),
                        timer: self.default_highlight
                        }
                        )
                        cfg = bui.app.config
                        cfg['GUMMY_statsminicrit'] = babase.app.config.get('GUMMY_statsminicrit', 0) + 1
                        cfg.apply_and_commit()

            

            # If they've got a shield, deliver it to that instead.
            if self.shield:
                if msg.flat_damage:
                    damage = msg.flat_damage * self.impact_scale
                else:
                    # Hit our spaz with an impulse but tell it to only return
                    # theoretical damage; not apply the impulse.
                    assert msg.force_direction is not None
                    self.node.handlemessage(
                        'impulse',
                        msg.pos[0],
                        msg.pos[1],
                        msg.pos[2],
                        msg.velocity[0],
                        msg.velocity[1],
                        msg.velocity[2],
                        mag,
                        velocity_mag,
                        msg.radius,
                        1,
                        msg.force_direction[0],
                        msg.force_direction[1],
                        msg.force_direction[2],
                    )
                    damage = damage_scale * self.node.damage

                assert self.shield_hitpoints is not None
                self.shield_hitpoints -= int(damage)
                self.shield.hurt = (
                    1.0
                    - float(self.shield_hitpoints) / self.shield_hitpoints_max
                )
                # shield breaker
                if msg.hit_subtype == 'breaker':
                    self.handleshieldbreaker()

                # Its a cleaner event if a hit just kills the shield
                # without damaging the player.
                # However, massive damage events should still be able to
                # damage the player. This hopefully gives us a happy medium.
                max_spillover = SpazFactory.get().max_shield_spillover_damage
                if self.shield_hitpoints <= 0: 
                    spillover = self.shield_hitpoints * -1
                    # FIXME: Transition out perhaps?
                    self.shield.delete()
                    self.shield = None
                    from bascenev1lib.mainmenu import MainMenuActivity
                    if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        SpazFactory.get().shield_down_sound.play(
                        1.0,
                        position=self.node.position,
                    )
                    
                    # Emit some cool looking sparks when the shield dies.
                    npos = self.node.position
                    bs.emitfx(
                        position=(npos[0], npos[1] + 0.9, npos[2]),
                        velocity=self.node.velocity,
                        count=random.randrange(20, 30),
                        scale=1.0,
                        spread=0.6,
                        chunk_type='spark',
                    )
                     # shield break fuction.
                    #if shield spillover in greater than 300, we do the shield break knockout.
                    if spillover > 300 or self.shieldbroken:
                        self.shieldbroken = False
                        bs.camerashake(intensity = 5)
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            
                            SpazFactory.get().shieldbreak_sound.play()
                        bs.emitfx(
                    position=(npos[0], npos[1] + 0.9, npos[2]),
                        velocity=self.node.velocity,
                        count=random.randrange(80, 90),
                        scale=0.3,
                        spread=0.1,
                        chunk_type='spark',
                    )
                        bs.emitfx(
                        position=(npos[0], npos[1] + 0.9, npos[2]),
                        velocity=self.node.velocity,
                        count=random.randrange(70, 100),
                        scale=5.0,
                        spread=0.6,
                        chunk_type='sweat',
                    )
                        PopupText('SHIELD\nBREAK!', color=(0.2, 1, 1),
                            scale=1.3,
                            position = self.node.position
                            ).autoretain()
                        
                        if self.award_xp:
                            babase.app.plus.xp_sys.award_xp(12, True, self.node.position)
                        timer = 0.6
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(0.2, 0.2, 1),
                        timer: self.default_color,
                        }
                        )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(0.2, 0.2, 1),
                        timer: self.default_highlight,
                        }
                        )
                        bs.show_damage_count(
                        '(' + str(spillover / 10) + '%)',
                        msg.pos,
                        (msg.force_direction[1], msg.force_direction[1] + 15, 2),
                        (0.20, 1, 1, 1)
                    )   
                        self.node.handlemessage('knockout', max(0.0, 50.0 * spillover))
                        cfg = bui.app.config
                        cfg['GUMMY_statsshieldbreaks'] = babase.app.config.get('GUMMY_statsshieldbreaks', 0) + 1
                        cfg.apply_and_commit()
                        if cfg["GUMMY_statsshieldbreaks"] > 1000:
                            bs.app.classic.ach.award_local_achievement('ShieldBreaker')
                        #if babase.app.config.get('GUMMY_statsshieldbreaks', 0) >= 1000:
                        #    if babase.app.classic is not None:
                        #        babase.app.classic.ach.award_local_achievement(
                        #        'ShieldBreaker'
                        #        )

                    # end of shield break fuction. 
                    if self.getanother:
                        bs.timer(1, self.equip_shields)


                else:
                    from bascenev1lib.mainmenu import MainMenuActivity
                    if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        SpazFactory.get().shield_hit_sound.play(
                        0.5,
                        position=self.node.position,
                    )

                # Emit some cool looking sparks on shield hit.
                assert msg.force_direction is not None
                bs.emitfx(
                    position=msg.pos,
                    velocity=(
                        msg.force_direction[0] * 1.0,
                        msg.force_direction[1] * 1.0,
                        msg.force_direction[2] * 1.0,
                    ),
                    count=min(30, 5 + int(damage * 0.005)),
                    scale=0.5,
                    spread=0.3,
                    chunk_type='spark',
                )

                # If they passed our spillover threshold,
                # pass damage along to spaz.
                if self.shield_hitpoints <= -max_spillover:
                    leftover_damage = -max_spillover - self.shield_hitpoints
                    shield_leftover_ratio = leftover_damage / damage

                    # Scale down the magnitudes applied to spaz accordingly.
                    mag *= shield_leftover_ratio
                    velocity_mag *= shield_leftover_ratio
                else:
                    return True  # Good job shield!
            else:
                shield_leftover_ratio = 1.0

            if msg.flat_damage:
                damage = int(
                    msg.flat_damage * self.impact_scale * shield_leftover_ratio
                )
            else:
                # Hit it with an impulse and get the resulting damage.
                assert msg.force_direction is not None
                self.node.handlemessage(
                    'impulse',
                    msg.pos[0],
                    msg.pos[1],
                    msg.pos[2],
                    msg.velocity[0],
                    msg.velocity[1],
                    msg.velocity[2],
                    mag,
                    velocity_mag,
                    msg.radius,
                    0,
                    msg.force_direction[0],
                    msg.force_direction[1],
                    msg.force_direction[2],
                )

                damage = int(damage_scale * self.node.damage)
            self.node.handlemessage('hurt_sound')
        
            # Play punch impact sound based on damage if it was a punch
            
            
            if msg.hit_type == 'punch':
                
                self.on_punched(damage)
                
                # we use spikes now
                if msg.hit_subtype == 'b2b_charge' and False:

                    # If damage came from a b2b_charge, show it.
                    assert msg.force_direction is not None
                    bs.show_damage_count(
                    '-' + str(int(damage / 10)) + '%',
                    msg.pos,
                    msg.force_direction,
                        (1, 1, 1, 1),
                        
                    )
                elif damage >= 350:
                    assert msg.force_direction is not None
                    bs.show_damage_count(
                        '-' + str(int(damage / 10)) + '%',
                        msg.pos,
                        msg.force_direction,
                        (1, 0, 0) if self.is_alive() else (0.2, 0.2, 0.2) 
                    )
                        
            

                # Let's always add in a super-punch sound with boxing
                # gloves just to differentiate them.
                if msg.hit_subtype == 'super_punch':
                    from bascenev1lib.mainmenu import MainMenuActivity
                    if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        SpazFactory.get().punch_sound_stronger.play(
                        1.0,
                        position=self.node.position,
                    )
                if damage >= 500:
                    sounds = SpazFactory.get().punch_sound_strong
                    sound = sounds[random.randrange(len(sounds))]
                elif damage >= 100:
                    sound = SpazFactory.get().punch_sound
                else:
                    sound = SpazFactory.get().punch_sound_weak
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    sound.play(1.0, position=self.node.position)

                # Throw up some chunks.
                assert msg.force_direction is not None
                bs.emitfx(
                    position=msg.pos,
                    velocity=(
                        msg.force_direction[0] * 0.5,
                        msg.force_direction[1] * 0.5,
                        msg.force_direction[2] * 0.5,
                    ),
                    count=min(10, 1 + int(damage * 0.0025)),
                    scale=0.3,
                    spread=0.03,
                )

                bs.emitfx(
                    position=msg.pos,
                    chunk_type='sweat',
                    velocity=(
                        msg.force_direction[0] * 1.3,
                        msg.force_direction[1] * 1.3 + 5.0,
                        msg.force_direction[2] * 1.3,
                    ),
                    count=min(30, 1 + int(damage * 0.04)),
                    scale=0.9,
                    spread=0.28,
                )

                # Momentary flash.
                hurtiness = damage * 0.003
                punchpos = (
                    msg.pos[0] + msg.force_direction[0] * 0.02,
                    msg.pos[1] + msg.force_direction[1] * 0.02,
                    msg.pos[2] + msg.force_direction[2] * 0.02,
                )
                flash_color = (1.0, 0.8, 0.4)
                light = bs.newnode(
                    'light',
                    attrs={
                        'position': punchpos,
                        'radius': 0.12 + hurtiness * 0.12,
                        'intensity': 0.3 * (1.0 + 1.0 * hurtiness),
                        'height_attenuated': False,
                        'color': flash_color,
                    },
                )
                bs.timer(0.06, light.delete)

                flash = bs.newnode(
                    'flash',
                    attrs={
                        'position': punchpos,
                        'size': 0.17 + 0.17 * hurtiness,
                        'color': flash_color,
                    },
                )
                bs.timer(0.06, flash.delete)

            if msg.hit_type == 'impact':
                assert msg.force_direction is not None
                bs.emitfx(
                    position=msg.pos,
                    velocity=(
                        msg.force_direction[0] * 2.0,
                        msg.force_direction[1] * 2.0,
                        msg.force_direction[2] * 2.0,
                    ),
                    count=min(10, 1 + int(damage * 0.01)),
                    scale=0.4,
                    spread=0.1,
                )

            
            GUUU_GUU = (random.randint(0, 4)==0 and damage >= 250 and msg.hit_type == 'punch') and self.is_alive()
    
            if self.hitpoints > 0:
                # It's kinda crappy to die from impacts, so lets reduce
                # impact damage by a reasonable amount *if* it'll keep us alive.
                if msg.hit_type == 'impact' and damage >= self.hitpoints:
                    # Drop damage to whatever puts us at 10 hit points,
                    # or 200 less than it used to be whichever is greater
                    # (so it *can* still kill us if its high enough).
                    newdamage = max(damage - 200, self.hitpoints - 10)
                    damage = newdamage
                self.node.handlemessage('flash')

                # If we're holding something, drop it.
                if damage > 0.0 and self.node.hold_node:
                    self.node.hold_node = None
                self.hitpoints -= damage
                self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )

                

                # If we're cursed, *any* damage blows us up.
                if self._cursed and damage > 0:
                    bs.timer(
                        0.05,
                        bs.WeakCall(
                            self.curse_explode, msg.get_source_player(bs.Player)
                        ),
                    )

                # If we're frozen, shatter.. otherwise die if we hit zero
                if self.frozen and (damage > 200 or self.hitpoints <= 0):
                    if self.totem < 1:
                        self.shatter()
                    else:
                        self.totem_effect()

                   
                elif self.hitpoints <= 0 and not GUUU_GUU:
                    if self.totem < 1:
                        # turn into gold statues if being killed by a gold bomb
                        if msg.hit_subtype == 'gold':
                            self.turn_gold()
                        self.node.handlemessage(
                            bs.DieMessage(how=bs.DeathType.IMPACT)
                        )
                        # We dont want them to shatter that easily...
                        if msg.hit_subtype == 'gold':
                            return
                        
                    else:
                        self.totem_effect()

            # If we're dead, take a look at the smoothed damage value
            # (which gives us a smoothed average of recent damage) and shatter
            # us if its grown high enough.
            if self.hitpoints <= 0:
                damage_avg = self.node.damage_smoothed * damage_scale
                
                if GUUU_GUU and self.totem < 1: # make sure we dont have a totem
                    # Kill them (so the player will respawn), but revive the node again so we can do our funny DAYUM
                    self.handlemessage(bs.DieMessage(delete_node=False))
                    # We dont wana move
                    if self.source_player:
                        self.source_player.actor.disconnect_controls_from_player()
                    # Dont delete the node though
                    self.node.dead = False
                    self.node.hurt = 0.0
                    
                    self._safe_play_sound(bs.getsound('TOCUH_OF_MIDAS_sparkles'), 1.3)
                    
                    self.impact_scale = 0.0
                    # NOTE: why is this on a timer??
                    bs.timer(0.1, lambda: self.node.handlemessage('knockout', 2500))
                    bs.timer(1.2, lambda: self.node.handlemessage('knockout', 5000))

                    def MIDAS():
                        if self.node:
                            for _ in range(18):
                                self.node.handlemessage('impulse', self.node.position[0], self.node.position[1], self.node.position[2],
                                                                0, 25, 0,
                                                                45, 0.05, 0, 0,
                                                                0, 250, 0)

                            self.turn_gold()
                            self.shatter(True)
                    
                    bs.timer(2.3, MIDAS)

                else:
                    if damage_avg >= 1150:
                        self.shatter(extreme=True)
                    elif damage_avg >= 1000:
                        self.shatter()
                
                    # If the attack came from a b2b charge, shatter if charge damamge is high enough.
                    elif msg.hit_subtype == 'b2b_charge':
                        if damage >= 500:
                            self.shatter(extreme=True)
                        elif damage >= 250:
                            self.shatter()
                    
                    #turn into gold statues if being attacked by a gold bomb if dead
                    if msg.hit_subtype == 'gold':
                        self.turn_gold()
                            
        
            if msg.hit_type == 'explosion':

                
        
                        
                

                if (msg.hit_subtype == 'land_mine' or msg.hit_subtype == 'promine' or msg.hit_subtype == 'star' or msg.hit_subtype == 'heart') and not self.character == 'Land-Mine':
                    if damage > 1000 and self.hitpoints == 0:
                        gumcoins = math.ceil(damage / 30)
                        self.enablegamerpoints = True
                        if msg.hit_subtype == 'promine':
                            timer = 1.4
                            bs.animate_array(self.node,'color', 3,
                        {
                        0:(10, 0, 0),
                        timer: self.default_color,
                        }
                    )
                            bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(10, 0, 0),
                        timer: self.default_highlight,
                        }
                    )
                        if msg.hit_subtype == 'heart':
                            # lol, this is just funny. minexecuting someone with a healing mine.
                            timer = 1.1
                            bs.getsound('love').play()
                            #if babase.app.classic is not None:
                            #    babase.app.classic.ach.award_local_achievement(
                            #    'Lover'
                            #    )
                            for i in range(12):
                                PopupText("\ue047",
                                   scale=1.4,
                                   position=(self.node.position[0] + random.randrange(-1, 1), self.node.position[1]+ random.randrange(-1, 1), self.node.position[2])
                            ).autoretain()
                            bs.animate_array(self.node,'color', 3,
                        {
                        0:(10, 0, 5),
                        timer: self.default_color,
                        }
                    )
                            bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(10, 0, 5),
                        timer: self.default_highlight,
                        }
                    )
                        if msg.hit_subtype == 'star':
                            self.enablegamerpoints = True
                            timer = 1.2
                            bs.animate_array(self.node,'color', 3,
                        {
                        0:(10, 10, 0),
                        timer: self.default_color,
                        }
                    )
                            bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(10, 10, 0),
                        timer: self.default_highlight,
                        }
                    )
                        bs.getsound('landMineKill').play()
                        PopupText('MINEXECUTION',
                                color=(1, 0.5, 0, 1),
                                scale=2,
                                position = self.node.position
                                ).autoretain()
                        if self.award_xp: babase.app.plus.xp_sys.award_xp(3, True, self.node.position)

                        cfg = bui.app.config
                        PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(gumcoins), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = self.node.position
                                ).autoretain()
                        cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 0
                        cfg['GUMMY_statsminexecutions'] = babase.app.config.get('GUMMY_statsminexecutions', 0) + 1
                        cfg.apply_and_commit()
                        #if babase.app.config.get('GUMMY_statsminexecutions', 0) >= 1000:
                        #    if babase.app.classic is not None:
                        #        babase.app.classic.ach.award_local_achievement(
                        #        'Minexecutioner'
                        #            )

                elif msg.hit_subtype == 'strike':
                    if damage > 1000 and self.hitpoints == 0:
                        gumcoins = math.ceil(damage / 10)
                        self.enablegamerpoints = True
                        timer = 1.1
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(10, 10, 10),
                        timer: self.default_color,
                        }
                    )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(10, 10, 10),
                        timer: self.default_highlight,
                        }
                    )
                        bs.getsound('strikeKill').play()

                        PopupText('BOLTED!', 
                                color=(1, 1, 1, 1),
                                scale=2,
                                position = self.node.position
                                ).autoretain()
                        if self.award_xp: babase.app.plus.xp_sys.award_xp(2, True, self.node.position)
                        
                        cfg = bui.app.config
                        PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(gumcoins), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = self.node.position
                                ).autoretain()
                        cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 0
                        cfg['GUMMY_statsbolteds'] = babase.app.config.get('GUMMY_statsbolteds', 0) + 1
                        cfg.apply_and_commit()
                        if cfg["GUMMY_statsbolteds"] > 1000:
                            bs.app.classic.ach.award_local_achievement('Zeus')
                        #if babase.app.config.get('GUMMY_statsbolteds', 0) >= 1000:
                        #    if babase.app.classic is not None:
                        #        babase.app.classic.ach.award_local_achievement(
                        #        'Zeus'
                        #        )
                    cfg = bui.app.config
                    if cfg["GUMMY_statsminexecutions"] > 1000:
                        bs.app.classic.ach.award_local_achievement('Minexecutioner')
                        
                elif msg.hit_subtype == 'impulse':
                    gumcoins = math.ceil(damage / 10)
                    if damage > 1000 and self.hitpoints == 0:
                        self.enablegamerpoints = True
                        timer = 1.2
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(1, 1, 5),
                        timer: self.default_color,
                        }
                    )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(1, 1, 5),
                        timer: self.default_highlight,
                        }
                    )
                        bs.getsound('impulseKill').play()
                        PopupText('IMPULS\'D', 
                                color=(0.5, 0.25, 1, 1),
                                scale=2,
                                position = self.node.position
                                ).autoretain()
                        if self.award_xp: babase.app.plus.xp_sys.award_xp(2, True, self.node.position)
                        cfg = bui.app.config
                        PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(gumcoins), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = self.node.position
                                ).autoretain()
                        cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 0
                        cfg['GUMMY_statsimpulsd'] = babase.app.config.get('GUMMY_statsimpulsd', 0) + 1
                        cfg.apply_and_commit()
                        if cfg["GUMMY_statsimpulsd"] > 1000:
                            bs.app.classic.ach.award_local_achievement('Sniper')
                        #if babase.app.config.get('GUMMY_statsimpulsd', 0) >= 1000:
                        #    if babase.app.classic is not None:
                        #        babase.app.classic.ach.award_local_achievement(
                        #        'Sniper'
                        #        )
                    else:
                        timer = 0.87
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(0.1, 0.1, 0.3),
                        timer: self.default_color,
                        }
                    )
                        bs.animate_array(self.node,'highlight', 3,
                        {
                        0:(0.1, 0.1, 0.3),
                        timer: self.default_highlight,
                        }
                    )
                
                elif msg.hit_subtype == 'negative':
                    # the negative bomb's explosion is so BIG that if it insta-kills we change our colors to a blowing purple.
                    if damage > 1000 and self.hitpoints == 0:
                        gumcoins = 5
                        self.enablegamerpoints = True
                        self.node.color = (1, 0, 5)
                        self.node.highlight = (1, 0, 5)
                        PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(gumcoins), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = self.node.position
                                ).autoretain()
                        cfg = bui.app.config
                        cfg['GUMMY_gumcoins'] = babase.app.config.get('GUMMY_gumcoins', False) + 0
                        cfg.apply_and_commit()
                
                elif msg.hit_subtype == 'boogie':
                       self.boogie()
                elif msg.hit_subtype == 'breaker':
                       self.handleshieldbreaker()
                elif msg.hit_subtype == 'mini':
                        timer = 0.3
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(0.35, 0.5, 0),
                        timer: self.default_color,
                        }
                    )    
                elif msg.hit_subtype == 'lightning':
                        timer = 0.3
                        bs.animate_array(self.node,'color', 3,
                        {
                        0:(1, 1, 1),
                        timer: self.default_color,
                        }
                    ) 
                        
                if msg.hit_subtype == 'heart':
                    # NOTE: err... i tried setting the hitpoints to be 9999 but it causes graphical issues to the hp bar so uhm.. 
                    # we'll increase it to 1500 (150hp) as we still can increase our hp higher than the limit.
                    # then back to max, because the mine still.. """ technically """ does damage.
                    # so if you survive well, ya get healed depending how much damage the mine did to ya
                    # also you cant get healed if you have a shield, so its a basically a mine (fuck you shields)

                    # 11/16/25 It does no damage now so no need for any-o that
                    if not self.shield:
                    
                        self.hitpoints = self.hitpoints_max
                        if self.node:
                            self.node.hurt = (
                                1.0 - float(self.hitpoints) / self.hitpoints_max
                            )   
                        
                
            
            
            # bj park make it rainnn
            if self.source_player and self.getactivity().map.name == 'Bomb Jump Park':
                if msg._source_player:
                    if msg._source_player != self.source_player and self.getactivity().globalsnode.music != bs.MusicType.BJPARKCOMBAT.value:
                        bs.setmusic(bs.MusicType.BJPARKCOMBAT)
            self.last_damage_count = damage


            
    

        elif isinstance(msg, BombDiedMessage):
            self.bomb_count += 1

        elif isinstance(msg, bs.DieMessage):
            if self.node:
                wasdead = self._dead
                self._dead = True
                self.hitpoints = 0
                if msg.immediate:
                    if self.node:
                        self.node.delete()
                elif self.node:

                    
                
                    if self.character == 'Land-Mine':
                            Blast(
                                position=self.node.position,
                                velocity=self.node.velocity,
                                blast_type='land_mine',
                                source_player=(
                                self.node
                                ),
                    ).autoretain()
                    self.node.dead = True


                    # Cosmetic Lore-Accure causes Space Guy to break.
                    if self.character == 'Space Guy' and not wasdead:
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            bs.getsound('lego_break').play()
                        
                        self.shatter(True)
                    self.node.hurt = 1.0
                    if self.play_big_death_sound and not wasdead:
                    
                        SpazFactory.get().single_player_death_sound.play()
                    
                    if msg.delete_node is True:
                        # Make sure the node is dead (so custom animations who "revive" the node back will have their things play.)
                        bs.timer(2.0, self.node.delete)
                    bs.timer(0.1, self._hide_charge_text)

                    if not wasdead and msg.how is not bs.DeathType.LEFT_GAME:
                        # Deaths give us some XP.
                        if self.award_xp: babase.app.plus.xp_sys.award_xp(2 if self.source_player else 1, True, self.node.position)
                        
                
                    

            
                

        elif isinstance(msg, bs.OutOfBoundsMessage):

            if not self.totem < 1:
                # Not even totems can save you from the void
                self.totem_effect()


      
            self.handlemessage(bs.DieMessage(how=bs.DeathType.FALL))
            # Herm.. exessive velocty upward. Probably from the top. Cue screen KO!
            if self.node.velocity[1] > 3:
                self.screen_ko()
                
            
            if True:
                try:
                    

                    vel = self.node.velocity if self.node else (0, 0, 0)
                    horiz_speed = abs(vel[1])
                    
                    # we need to be fast if this is a 'ankle breaker'
                    if horiz_speed < 1.8:
                        return
                    
                    
                    
                    
                    for s in bs.getplayers():
                            spaz = s.actor
                           
                            if spaz and spaz.is_alive() and spaz is not self:
                              
                                node = spaz.node
                                
                                if node:
                                    
                                    try:
                                        pos1 = node.position
                                        pos2 = self.node.position
                                        dist = ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2) ** 0.5
                                    except Exception:
                                        dist = 9999

                                    # Originally 10.5 but some maps just dont dont detect it
                                    # from 21.67 > 13.67
                                    threshold = 13.67

                                    
                                    if dist < threshold and spaz.standing and node.knockout == 0 and spaz.is_alive() and spaz.source_player and random.randint(0, 1) == 0:
                                        bs.getsound('ankleBreaker').play(1.0)
                                        bs.timer(0.2, lambda: bs.getsound('whereareyougoing').play())
                                        bs.timer(0.65, lambda: bs.getsound('iDunno').play(2))
                                        PopupText('ANKLES BROKEN', 
                                            color=(0.8, 0.8, 0.8, 1),
                                            scale=1.56,
                                            position = pos1
                                        ).autoretain()
                                        if self.award_xp: babase.app.plus.xp_sys.award_xp(2, True, node.position)
                                        bui.app.config["GUMMY_statsbrokenankles"] += 1
                                        bui.app.config.apply_and_commit()
                                        break
                    activity = None
                except Exception as e:
                    print(e)
                    activity = None

        
       
           


        elif isinstance(msg, bs.StandMessage):
            self._last_stand_pos = (
                msg.position[0],
                msg.position[1],
                msg.position[2],
            )
            if self.node:
                self.node.handlemessage(
                    'stand',
                    msg.position[0],
                    msg.position[1],
                    msg.position[2],
                    msg.angle,
                )

        elif isinstance(msg, CurseExplodeMessage):
            self.curse_explode()

        elif isinstance(msg, PunchHitMessage):
            if not self.node:
                return None
            node = bs.getcollision().opposingnode

            # Don't want to physically affect powerups.
            if node.getdelegate(PowerupBox):
                return None

            # Only allow one hit per node per punch.
            if node and (node not in self._punched_nodes):
                punch_momentum_angular = (
                    self.node.punch_momentum_angular * self._punch_power_scale
                )
                punch_power = self.node.punch_power * self._punch_power_scale

                # Ok here's the deal:  we pass along our base velocity for use
                # in the impulse damage calculations since that is a more
                # predictable value than our fist velocity, which is rather
                # erratic. However, we want to actually apply force in the
                # direction our fist is moving so it looks better. So we still
                # pass that along as a direction. Perhaps a time-averaged
                # fist-velocity would work too?.. perhaps should try that.

                is_a_spaz = True
                # If its something besides another spaz, just do a muffled
                # punch sound.
                if node.getnodetype() != 'spaz':
                    sounds = SpazFactory.get().impact_sounds_medium
                    sound = sounds[random.randrange(len(sounds))]
                    from bascenev1lib.mainmenu import MainMenuActivity
                    if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        sound.play(1.0, position=self.node.position)
                    is_a_spaz = False


                ppos = self.node.punch_position
                punchdir = self.node.punch_velocity
                vel = self.node.punch_momentum_linear

                self._punched_nodes.add(node)

                crit_boosted = False
                crit_type = 'normal`'
                crit_damage = 1.0

                boogie = False

                if node.getdelegate(Spaz):
                    boogie = node.getdelegate(Spaz).boogieing

                if babase.app.config.get('GUMMY_RandomCritChance', "(1/9))") == "(1/24)":
                    randomVAR = 25
                else:
                    if babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "(1/4)":
                        randomVAR = 5
                    else:
                        if babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "100%":
                            randomVAR = 2
                        else:
                            randomVAR = 10
                if self.force_crit:
                    randomVAR = self.force_crit_chance

                if (random.randrange(1, randomVAR) == 1 and bui.app.config.get("GUMMY_disablerandomcrit", False) == False) or boogie:
                    if random.randrange(1, 4) == 1 or boogie:
                        crit_boosted = True
                        crit_type = 'normal'
                        crit_damage = 3
                        
                        
                        
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            SpazFactory.get().crit_start.play(
                                0.8,
                                position=self.node.position,
                            ),
                        
                    else:
                        crit_boosted = True
                        crit_type = 'mini'
                        crit_damage = 1.35
                        
                        
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                        
                            SpazFactory.get().crit_start.play(
                                0.8,
                                position=self.node.position,
                            ),
                        
                

                node.handlemessage(
                    bs.HitMessage(
                        pos=ppos,
                        velocity=vel,
                        magnitude=punch_power * punch_momentum_angular * 110.0 * crit_damage,
                        velocity_magnitude=punch_power * 40 * crit_damage,
                        radius=0,
                        srcnode=self.node,
                        source_player=self.source_player,
                        force_direction=punchdir,
                        hit_type='punch',
                        hit_subtype=(
                            'super_punch'
                            if self._has_boxing_gloves
                            else 'default'
                        ),
                        crit_boosted=crit_boosted,
                        crit_type=crit_type
                    )
                )

                if is_a_spaz:
                    dmg = int(0.22 * node.damage)
                else:
                    dmg = 0
                

                # Uh, if we already released our shi... if we deal any damage in the time frame we add into the spike.
                if self.spiking and dmg  != 0:
                    self.show_spike_text(dmg/10)


                # Charge Mechanic
                # also say no if we critted them, we dont wanna award rng!
                

                # Check if damage is 60%+
                if dmg >= 600 and self.node and is_a_spaz and not crit_boosted:
                    # Add a charge!


                    # We should be getting charges no?
                    self.allow_new_charge = True
                    self.add_charge()

                    
                

                # Else, we have a charge, our punch wasnt 0 damage, and they're alive release it and do extra damage.
                elif not self.DMGcharge == 0 and dmg != 0 and is_a_spaz and not crit_boosted and not node.dead:
                    
                    b2b_dmg = dmg * (self.DMGcharge * 0.1)
                    # This is in no way overpowered!
                    b2b_dmg * (1 + self.every_instance_in_abilities(
                        'B2B Damage ↑'
                    ))
                    b2b_dmg * (4 + self.every_instance_in_abilities(
                        'B2B Damage ↑↑'
                    ))
                    b2b_dmg * (7 + self.every_instance_in_abilities(
                        'B2B Damage ↑↑↑↑'
                    ))
                    self._hide_charge_text()
                    #int(42 * ( 24* 0.1) * 10)
                    

                    # Give the activity some score.
                    if self.source_player:
                        self.getactivity().handlemessage(bs.PlayerScoredMessage(int(b2b_dmg*15)))
                    if 1 <= self.DMGcharge <= 4:
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            bs.getsound('spikeS').play()
                    elif 5 <= self.DMGcharge <= 6:
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            bs.getsound('spikeM').play()
                    else:    
                        from bascenev1lib.mainmenu import MainMenuActivity
                        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                            bs.getsound('spikeL').play()
                    

                    # Achievements..
                    if self.source_player and not crit_boosted:
                        if self.DMGcharge >= 4:
                                babase.app.classic.ach.award_local_achievement(
                                'Charger'
                                   )
                        if self.DMGcharge >= 15:                              
                                babase.app.classic.ach.award_local_achievement(
                                'Charger2'
                                    )
                        if self.DMGcharge >= 30:
                                babase.app.classic.ach.award_local_achievement(
                                'Charger3'
                                    )
                    
                    self.show_spike_text(b2b_dmg/10)

                     

                    self.DMGcharge = 0
                    # Say we're releasing it so we can spike.
                    self.releasing_charge = True
                    node.handlemessage(
                        bs.HitMessage(
                            flat_damage=b2b_dmg,
                            pos=ppos,
                        radius=0,
                        srcnode=self.node,
                        source_player=self.source_player,
                        force_direction=punchdir,
                            hit_type='punch',
                            hit_subtype = 'b2b_charge',
                            )
                        )

                    def nomore():
                        self.releasing_charge = False
                    
                    bs.timer(0.5, nomore)
                    
                    
                    
                    
                        
                


                # Also apply opposite to ourself for the first punch only.
                # This is given as a constant force so that it is more
                # noticeable for slower punches where it matters. For fast
                # awesome looking punches its ok if we punch 'through'
                # the target.
                mag = -400.0
                if self._hockey:
                    mag *= 0.5
                if len(self._punched_nodes) == 1:
                    self.node.handlemessage(
                        'kick_back',
                        ppos[0],
                        ppos[1],
                        ppos[2],
                        punchdir[0],
                        punchdir[1],
                        punchdir[2],
                        mag,
                    )
        elif isinstance(msg, PickupMessage):
            if not self.node:
                return None

            try:
                collision = bs.getcollision()
                opposingnode = collision.opposingnode
                opposingbody = collision.opposingbody
            except bs.NotFoundError:
                return True
            
            assert isinstance(opposingnode, NodeVisualizer)

            from bascenev1lib.game.bossfight import Boss

            # This is a special class where you shouldnt be able to pick them up
            if opposingnode.getdelegate(Boss):
                return

            

            # Dont allow picking up of golden dudes. (they're gonna disappear anyway)
            if opposingnode.getdelegate(Spaz):
                if opposingnode.getdelegate(Spaz).is_gold:
                    return
            
            # Dont allow picking up cloaked dudes. (Status effect)
            if opposingnode.getdelegate(Spaz):
                if 'undetectable' in opposingnode.getdelegate(Spaz).effects:
                    return
            


            # Don't allow picking up of invincible dudes.
            try:
                if opposingnode.invincible:
                    return True
            except Exception:
                pass

            # If we're grabbing the pelvis of a non-shattered spaz, we wanna
            # grab the torso instead.
            if (
                opposingnode.getnodetype() == 'spaz'
                and not opposingnode.shattered
                and opposingbody == 4
            ):
                opposingbody = 1

            # Special case - if we're holding a flag, don't replace it
            # (hmm - should make this customizable or more low level).
            held = self.node.hold_node
            if held and held.getnodetype() == 'flag':
                return True

            # Note: hold_body needs to be set before hold_node.
            self.node.hold_body = opposingbody
            self.node.hold_node = opposingnode
        elif isinstance(msg, bs.CelebrateMessage):
            if self.node:
                if msg.type == 'center':
                    self.node.handlemessage('celebrate', int(msg.duration * 1000))
                elif msg.type == 'left':
                    self.node.handlemessage('celebrate_l', int(msg.duration * 1000))
                elif msg.type == 'right':
                    self.node.handlemessage('celebrate_r', int(msg.duration * 1000))
                else:
                    self.node.handlemessage('celebrate', int(msg.duration * 1000))
        else:
            return super().handlemessage(msg)
        return None
            
    


    def drop_bomb(self) -> Bomb | None:
        """
        Tell the spaz to drop one of his bombs, and returns
        the resulting bomb object.
        If the spaz has no bombs or is otherwise unable to
        drop a bomb, returns None.
        """

        if self.ass_bomb:
            if babase.app.config.get('GUMMY_RandomCritChance', "(1/9))") == "(1/24)":
                randomVAR = 25
            elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "(1/4)":
                    randomVAR = 5
            elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "100%":
                    randomVAR = 2
            else:
                randomVAR = 10
            if self.force_crit:
                    randomVAR = self.force_crit_chance
            
            crit_boosted = False
            crit_type = 'normal'
            if (random.randrange(1, randomVAR) == 1 and bui.app.config.get("GUMMY_disablerandomcrit", False) == False):
                crit_boosted = True
            
                if random.randint(1, 4) == 1:
                    crit_type = 'normal'
                else:
                    crit_type = 'mini'
            self.hitpoints = 1
            Blast(
            position=self.node.position,
            velocity=self.node.velocity,
            blast_radius=3.5,
            blast_type='normal',
            source_player=self.source_player,
            crit_boosted=crit_boosted,
            crit_type=crit_type
        ).autoretain()
            self.ass_bomb = False
            return

        if (self.land_mine_count <= 0 and self.bomb_count <= 0 and self.rock_count <= 0 and self.egg_count <= 0 and self.boogie_count <= 0 and self.mini_count <= 0 and self.promine_count <= 0 and self.star_count <= 0 and self.heart_count <= 0 and self.boom_count <= 0 and self.beds <= 0 ) or self.frozen:
            return None
        assert self.node
        pos = self.node.position_forward
        vel = self.node.velocity

        if self.land_mine_count > 0:
            dropping_bomb = False
            self.set_land_mine_count(self.land_mine_count -  1)
            bomb_type = 'land_mine'
        elif self.rock_count > 0:
            dropping_bomb = False
            self.set_rock_count(self.rock_count - 1)
            bomb_type = 'rock'
        elif self.egg_count > 0:
            dropping_bomb = False
            self.set_egg_count(self.egg_count - 1)
            bomb_type = 'egg'
        elif self.beds > 0:
            dropping_bomb = False
            self.set_bed_count(self.beds - 1)
            bomb_type = 'bed'
        elif self.mini_count > 0:
            dropping_bomb = False
            self.set_mini_count(self.mini_count - 1)
            bomb_type = 'mini'
        elif self.boogie_count > 0:
            dropping_bomb = False
            self.set_boogie_count(self.boogie_count - 1)
            bomb_type = 'boogie'
        elif self.promine_count > 0:
            dropping_bomb = False
            self.set_promine_count(self.promine_count - 1)
            bomb_type = 'promine'
        elif self.star_count > 0:
            dropping_bomb = False
            self.set_star_count(self.star_count - 1)
            bomb_type = 'star'
        elif self.heart_count > 0:
            dropping_bomb = False
            self.set_heart_count(self.heart_count - 1)
            bomb_type = 'heart'
        elif self.boom_count > 0:
            dropping_bomb = False
            self.set_boom_count(self.boom_count - 1)
            bomb_type = 'boom'
        else:
            dropping_bomb = True
            bomb_type = self.bomb_type
        if babase.app.config.get('GUMMY_RandomCritChance', "(1/9))") == "(1/24)":
            randomVAR = 25
        elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "(1/4)":
                randomVAR = 5
        elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "100%":
                randomVAR = 2
        else:
              randomVAR = 10
        if self.force_crit:
                    randomVAR = self.force_crit_chance
        
        crit_boosted = False
        crit_type = 'normal'
        if (random.randrange(1, randomVAR) == 1 and bui.app.config.get("GUMMY_disablerandomcrit", False) == False):
            crit_boosted = True
        
            if random.randint(1, 4) == 1:
                crit_type = 'normal'
            else:
                crit_type = 'mini'

        

        bomb = Bomb(
            position=(pos[0], pos[1] - 0.0, pos[2]),
            velocity=(vel[0], vel[1], vel[2]),
            bomb_type=bomb_type,
            blast_radius=self.blast_radius,
            source_player=self.source_player,
            owner=self.node,
            crit_boosted=crit_boosted,
            crit_type=crit_type

        ).autoretain()
        bomb.blast_radius *=(1 + (1.2*self.every_instance_in_abilities('Bomb Radius ↑')))

        assert bomb.node
        if dropping_bomb:
            self.bomb_count -= 1
            bomb.node.add_death_action(
                bs.WeakCall(self.handlemessage, BombDiedMessage())
            )
        self._pick_up(bomb.node)

        for clb in self._dropped_bomb_callbacks:
            clb(self, bomb)

        return bomb

    def _pick_up(self, node: bs.Node) -> None:
        if self.node:
            # Note: hold_body needs to be set before hold_node.
            self.node.hold_body = 0
            self.node.hold_node = node

            

    def set_land_mine_count(self, count: int) -> None:
        """Set the number of land-mines this spaz is carrying."""
        self.land_mine_count = count
        if self.node:
            if self.land_mine_count != 0:
                self.node.counter_text = 'x' + str(self.land_mine_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_land_mines
                )
            else:
                self.node.counter_text = ''

    def set_promine_count(self, count: int) -> None:
        """Set the number of pro-mines this spaz is carrying."""
        self.promine_count = count
        if self.node:
            if self.promine_count != 0:
                self.node.counter_text = 'x' + str(self.promine_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_promine
                )
            else:
                self.node.counter_text = ''

    def set_rock_count(self, count: int) -> None:
        """Set the number of rocks this spaz is carrying."""
        self.rock_count = count
        if self.node:
            if self.rock_count != 0:
                self.node.counter_text = 'x' + str(self.rock_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_rock
                )
            else:
                self.node.counter_text = ''

    def set_egg_count(self, count: int) -> None:
        """Set the number of eggs this spaz is carrying."""
        self.egg_count = count
        if self.node:
            if self.egg_count != 0:
                self.node.counter_text = 'x' + str(self.egg_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_egg
                )
            else:
                self.node.counter_text = ''

    def set_mini_count(self, count: int) -> None:
        """Set the number of mini bombs this spaz is carrying."""
        self.mini_count = count
        if self.node:
            if self.mini_count != 0:
                self.node.counter_text = 'x' + str(self.mini_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_minibomb
                )
            else:
                self.node.counter_text = ''
    
    def set_boogie_count(self, count: int) -> None:
        """Set the number of boogie bombs this spaz is carrying."""
        self.boogie_count = count
        if self.node:
            if self.boogie_count != 0:
                self.node.counter_text = 'x' + str(self.boogie_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_boogie
                )
            else:
                self.node.counter_text = ''

    def set_star_count(self, count: int) -> None:
        """Set the number of star mines this spaz is carrying."""
        self.star_count = count
        if self.node:
            if self.star_count != 0:
                self.node.counter_text = 'x' + str(self.star_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_star
                )
            else:
                self.node.counter_text = ''
    
    def set_heart_count(self, count: int) -> None:
        """Set the number of health mines this spaz is carrying."""
        self.heart_count = count
        if self.node:
            if self.heart_count != 0:
                self.node.counter_text = 'x' + str(self.heart_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_heart
                )
            else:
                self.node.counter_text = ''
    
    def set_boom_count(self, count: int) -> None:
        """Set the number of boom boxes this spaz is carrying."""
        self.boom_count = count
        if self.node:
            if self.boom_count != 0:
                self.node.counter_text = 'x' + str(self.boom_count)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_boom
                )
            else:
                self.node.counter_text = ''
    
    def set_totem_count(self, count: int) -> None:
        """Set the number of boom boxes this spaz is carrying."""
        self.totem = count
        if self.node:
            if self.totem != 0:
                self.node.counter_text = 'x' + str(self.totem)
                self.node.counter_texture = (
                    bs.gettexture('totem')
                )
            else:
                self.node.counter_text = ''
    
    def set_bed_count(self, count: int) -> None:
        """Set the number of boom boxes this spaz is carrying."""
        self.beds = count
        if self.node:
            if self.beds != 0:
                self.node.counter_text = 'x' + str(self.beds)
                self.node.counter_texture = (
                    PowerupBoxFactory.get().tex_bed
                )
            else:
                self.node.counter_text = ''

    def reset_counts(self):
                self.set_rock_count(min(0, 5))
                self.set_promine_count(min(0, 2))
                self.set_egg_count(min(0, 15))
                self.set_mini_count(min(0, 25))
                self.set_boogie_count(min(0, 2))
                self.set_star_count(min(0, 4))
                self.set_heart_count(min(0, 3))
                self.set_boom_count(min(0, 3))
                self.set_totem_count(0)
                self.set_bed_count(0)

    def totem_effect(self):
        if not self.node:
            return

        if not self.is_alive():
            return

        if self.source_player:
            if self.award_xp: babase.app.plus.xp_sys.award_xp(15, True, self.node.position)

        #self.node.invincible = True

        self.set_totem_count(max(self.totem - 1,0))

        # Set us invincible for ~frame so we dont insta-insta die. (we still wanna die if we're being spammed tho.)
        self.node.invincible = True
        def safe():
            if self.node:
                self.node.invincible = False
        
        bs.timer(0.25, safe)

        


        self.hitpoints = self.hitpoints_max / 1.7
        self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )
        self._cursed = False

        # Remove cursed material.
        factory = SpazFactory.get()
        for attr in ['materials', 'roller_materials']:
            materials = getattr(self.node, attr)
            if factory.curse_material in materials:
                setattr(
                    self.node,
                    attr,
                        tuple(
                            m
                            for m in materials
                            if m != factory.curse_material
                        ),
                )
        self.node.curse_death_time = 0
        self.ass_bomb = False


        # We're fire resistance for a bit
        self.effects.append('fire_resistance')
        # And should no longer in a bit
        try:
            bs.timer(8, lambda: self.effects.remove('fire_resistance'))
        except:
            pass

    
        from bascenev1lib.mainmenu import MainMenuActivity
        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                
            bs.getsound('totemPop').play()
        # give it a sec before teleporting
       #bs.timer(0.1, lambda: self.handlemessage(bs.StandMessage((self.node.position[0], self.node.position[1] - 1.1, self.node.position[2]))))
       
        bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=int(4.0 + random.random() * 8),
                    spread=0.7,
                    chunk_type='slime',
                )
        bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=int(4.0 + random.random() * 8),
                    scale=0.5,
                    spread=0.7,
                    chunk_type='slime',
                )
        bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=15,
                    scale=0.6,
                    chunk_type='slime',
                    emit_type='stickers',
                )
        bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=20,
                    scale=0.7,
                    chunk_type='spark',
                    emit_type='stickers',
                )
        bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=int(6.0 + random.random() * 12),
                    scale=0.8,
                    spread=1.5,
                    chunk_type='spark',
                )
        bs.emitfx(
                    position=self.node.position,
                    velocity=(self.node.velocity[0] * 2, self.node.velocity[1] * 2, self.node.velocity[2] * 2),
                    count=int(6.0 + random.random() * 12),
                    scale=0.8,
                    spread=1.5,
                    chunk_type='spark',
                )

        #def set_invicible_safe():
        #    if self.node:
        #        self.node.invincible = False
        
        # And then finally, give 'absorption hearts' 
        self.equip_shields(color=(2,2,0))
        self.shield_hitpoints = 250
        # Set at 1 HP, and then regenerate.
        self.hitpoints = 10

        def add():
            if not self.node:
                return
            
            self.hitpoints = min(self.hitpoints_max, self.hitpoints + 20)
            self.node.hurt = (
                    1.0 - float(self.hitpoints) / self.hitpoints_max
                )

        i = 0.1

        for _ in range(36):

            bs.timer(i, add)
            i += 0.31

        #bs.timer(4, set_invicible_safe)


        def back():
            n = self.node
            if not n:
                return

            mass = 0.5

            # fuckin calcualtiaotn idk
            v = n.velocity
            vx, vy, vz = v

            ix = -vx * mass
            iy = -vy * mass
            iz = -vz * mass

            xforce = -vx
            yforce = -vy

            for _ in range(50):

                n.handlemessage(
                    'impulse',
                    n.position[0], n.position[1], n.position[2],
                    0, 25, 0,         
                    yforce, 0.05, 0, 0,
                    0, 20 * 400, 0      
                )

                n.handlemessage(
                    'impulse',
                    n.position[0], n.position[1], n.position[2],
                    0, 25, 0,
                    xforce, 0.05, 0, 0,
                    ix, iy, iz 
                )

                #self.node.handlemessag( 'impulse', msg.pos[0], msg.pos[1], msg.pos[2], msg.velocity[0],
                #        msg.velocity[1], msg.velocity[2],
                #        mag, velocity_mag, msg.radius, 0,
                #        msg.force_direction[0], msg.force_direction[1], msg.force_direction[2],
                #    )
        
        # We have to do this on a delay, or else it wont work right.
        bs.timer(0.14, back)
        
            



    def lightninglol(self, source_player: bs.Player | None = None):
        bs.getsound('GETOUT').play()
        self.shatter(extreme=True)
        Blast(
            position=self.node.position,
            velocity=self.node.velocity,
            blast_radius=2.0,
            blast_type='strike',
            source_player=(
                source_player if source_player else self.source_player
            ),
        ).autoretain()

    def curse_explode(self, source_player: bs.Player | None = None) -> None:
        """Explode the poor spaz spectacularly."""
        if self._cursed and self.node:
            if self.totem < 1:
                self.shatter(extreme=True)

                if babase.app.config.get('GUMMY_RandomCritChance', "(1/9))") == "(1/24)":
                    randomVAR = 25
                elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "(1/4)":
                        randomVAR = 5
                elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "100%":
                        randomVAR = 2
                else:
                    randomVAR = 10
                if self.force_crit:
                    randomVAR = self.force_crit_chance
                
                crit_boosted = False
                crit_type = 'normal'
                if (random.randrange(1, randomVAR) == 1 and bui.app.config.get("GUMMY_disablerandomcrit", False) == False):
                    crit_boosted = True
                
                    if random.randint(1, 4) == 1:
                        crit_type = 'normal'
                    else:
                        crit_type = 'mini'
            
                    

                self.handlemessage(bs.DieMessage())
            


                activity = self._activity()
                if activity:
                    if random.randrange(1 ,3) == 1:
                        Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blast_radius=3.0,
                        blast_type='normal',
                        source_player=(
                            source_player if source_player else self.source_player
                        ),
                        crit_boosted=crit_boosted,
                        crit_type=crit_type
                    ).autoretain()
                    else:
                        Blast(
                            position=self.node.position,
                            velocity=self.node.velocity,
                            blast_radius=2.0,
                            blast_type='strike',
                             source_player=(
                                source_player if source_player else self.source_player
                                ),
                            crit_boosted=crit_boosted,
                        crit_type=crit_type
                        ).autoretain()
            else:
                
                self.totem_effect()
                if babase.app.config.get('GUMMY_RandomCritChance', "(1/9))") == "(1/24)":
                    randomVAR = 25
                elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "(1/4)":
                        randomVAR = 5
                elif babase.app.config.get('GUMMY_RandomCritChance', "(1/10)") == "100%":
                        randomVAR = 2
                else:
                    randomVAR = 10
                if self.force_crit:
                    randomVAR = self.force_crit_chance
                
                crit_boosted = False
                crit_type = 'normal'
                if (random.randrange(1, randomVAR) == 1 and bui.app.config.get("GUMMY_disablerandomcrit", False) == False):
                    crit_boosted = True
                
                    if random.randint(1, 4) == 1:
                        crit_type = 'normal'
                    else:
                        crit_type = 'mini'
            
                            


                activity = self._activity()
                if activity:
                    if random.randrange(1 ,3) == 1:
                        Blast(
                        position=self.node.position,
                        velocity=self.node.velocity,
                        blast_radius=3.0,
                        blast_type='normal',
                        source_player=(
                            source_player if source_player else self.source_player
                        ),
                        crit_boosted=crit_boosted,
                        crit_type=crit_type
                    ).autoretain()
                    else:
                        Blast(
                            position=self.node.position,
                            velocity=self.node.velocity,
                            blast_radius=2.0,
                            blast_type='strike',
                             source_player=(
                                source_player if source_player else self.source_player
                                ),
                            crit_boosted=crit_boosted,
                        crit_type=crit_type
                        ).autoretain()
            self._cursed = False


    def shatter(self, extreme: bool = False) -> None:
        """Break the poor spaz into little bits."""
        if self.shattered:
            return
        
        has_totem = not self.totem < 1
        
        if not has_totem:
            self.shattered = True
        assert self.node
        if not has_totem:

            if self.frozen:
                
                # Momentary flash of light.
                light = bs.newnode(
                'light',
                attrs={
                    'position': self.node.position,
                    'radius': 0.5,
                    'height_attenuated': False,
                    'color': (0.8, 0.8, 1.0),
                },
                )

                bs.animate(
                light, 'intensity', {0.0: 3.0, 0.04: 0.5, 0.08: 0.07, 0.3: 0}
                )
                bs.timer(0.3, light.delete)

                # Emit ice chunks.
                bs.emitfx(
                position=self.node.position,
                velocity=self.node.velocity,
                count=int(random.random() * 10.0 + 10.0),
                scale=0.6,
                spread=0.2,
                chunk_type='ice',
                )
                bs.emitfx(
                position=self.node.position,
                velocity=self.node.velocity,
                count=int(random.random() * 10.0 + 10.0),
                scale=0.3,
                spread=0.2,
                chunk_type='ice',
                )
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    SpazFactory.get().shatter_sound.play(
                1.0,
                    position=self.node.position,
            )

            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                SpazFactory.get().splatter_sound.play(
                        10.0,
                        position=self.node.position,
                    )
        
            self.handlemessage(bs.DieMessage())
       


            self.node.shattered = 2 if extreme else 1
        else:  
            self.totem_effect()

    def _hit_self(self, intensity: float) -> None:
        if not self.node:
            return
        pos = self.node.position
        self.handlemessage(
            bs.HitMessage(
                flat_damage=50.0 * intensity,
                pos=pos,
                force_direction=self.node.velocity,
                hit_type='impact',
            )
        )
        self.node.handlemessage('knockout', max(0.0, 50.0 * intensity))
        sounds: Sequence[bs.Sound]
        if intensity >= 5.0:
            sounds = SpazFactory.get().impact_sounds_harder
        elif intensity >= 3.0:
            sounds = SpazFactory.get().impact_sounds_hard
        else:
            sounds = SpazFactory.get().impact_sounds_medium
        sound = sounds[random.randrange(len(sounds))]
        from bascenev1lib.mainmenu import MainMenuActivity
        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
            sound.play(position=pos, volume=5.0)

    def _get_bomb_type_tex(self) -> bs.Texture:
        factory = PowerupBoxFactory.get()
        if self.bomb_type == 'sticky':
            return factory.tex_sticky_bombs
        if self.bomb_type == 'ice':
            return factory.tex_ice_bombs
        if self.bomb_type == 'impact':
            return factory.tex_impact_bombs
        if self.bomb_type == 'random':
            return factory.tex_random
        if self.bomb_type == 'negative':
            return factory.tex_negative
        if self.bomb_type == 'lightning':
            return factory.tex_lightning
        if self.bomb_type == 'impulse':
            return factory.tex_impulse
        if self.bomb_type == 'boogie':
            return factory.tex_boogie
        if self.bomb_type == 'breaker':
            return factory.tex_breaker
        if self.bomb_type == 'gold':
            return factory.tex_gold
        raise ValueError('invalid bomb type')

    def _flash_billboard(self, tex: bs.Texture) -> None:
        assert self.node
        self.node.billboard_texture = tex
        self.node.billboard_cross_out = False
        bs.animate(
            self.node,
            'billboard_opacity',
            {0.0: 0.0, 0.1: 1.0, 0.4: 1.0, 0.5: 0.0},
        )

    def set_bomb_count(self, count: int) -> None:
        """Sets the number of bombs this Spaz has."""
        # We can't just set bomb_count because some bombs may be laid currently
        # so we have to do a relative diff based on max.
        diff = count - self._max_bomb_count
        self._max_bomb_count += diff
        self.bomb_count += diff

    def _gloves_wear_off_flash(self) -> None:
        if self.node:
            self.node.boxing_gloves_flashing = True
            self.node.billboard_texture = PowerupBoxFactory.get().tex_punch
            self.node.billboard_opacity = 1.0
            self.node.billboard_cross_out = True

    def _gloves_wear_off(self) -> None:
        if self._demo_mode:  # Preserve old behavior.
            self._punch_power_scale = 1.2
            self._punch_cooldown = BASE_PUNCH_COOLDOWN
        else:
            factory = SpazFactory.get()
            # fuck it dawg idc
            self._punch_power_scale /= 1.25 #factory.punch_power_scale
            self._punch_cooldown *= 1.33 #factory.punch_cooldown
        self._has_boxing_gloves = False
        if self.node:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                PowerupBoxFactory.get().powerdown_sound.play(
                position=self.node.position,
            )
            self.node.boxing_gloves = False
            self.node.billboard_opacity = 0.0


    def _multi_bomb_wear_off_flash(self) -> None:
        if self.node:
            self.node.billboard_texture = PowerupBoxFactory.get().tex_bomb
            self.node.billboard_opacity = 1.0
            self.node.billboard_cross_out = True

    def _multi_bomb_wear_off(self) -> None:
        self.set_bomb_count(self.default_bomb_count)
        if self.node:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                PowerupBoxFactory.get().powerdown_sound.play(
                position=self.node.position,
            )
            self.node.billboard_opacity = 0.0

    def _bomb_wear_off_flash(self) -> None:
        if self.node:
            self.node.billboard_texture = self._get_bomb_type_tex()
            self.node.billboard_opacity = 1.0
            self.node.billboard_cross_out = True

    def _bomb_wear_off(self) -> None:
        self.bomb_type = self.bomb_type_default
        if self.node:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                PowerupBoxFactory.get().powerdown_sound.play(
                position=self.node.position,
            )
            self.node.billboard_opacity = 0.0
    
    def turn_gold(self):
        """ Turns the spaz into a gold statue. """
        

        
        

        if not self.node or self.is_gold:
            return
        
        # Dont turn into a statue if we're already dead, it'll be weird.
        #if not self.is_alive():
        #    return
        # NOTE: Dont do this anymore, i like it now. 
        # ensure that we're dead
        self.handlemessage(bs.DieMessage())
        
        # getting gold'd while being frozen doesnt really sound ideal, is it?
        if self.frozen:
            return
        
        self.is_gold = True

        # Freeze them and make sure they take little damage (i want it possible for high damage explosions to still break us)
        self.impact_scale = 0.15



        # Mark as gold
        self.node.frozen = True
        # Change their texture
        #bs.getsound('gold').play(1.2)
        self.node.color_texture = bs.gettexture('goldColor')
        self.node.color_mask_texture = bs.gettexture('black')
        if self.award_xp:
            babase.app.plus.xp_sys.award_xp(5, True, self.node.position)
        cfg = babase.app.config
        cfg['GUMMY_statsgoldstatue'] += 1
        cfg.apply_and_commit()
        # import bascenev1 as bs;bs.getactivity().players[1].actor.turn_gold()

        


    
    def touched_fire(self, fire_id):
        state = self._fire_state.get(fire_id)
        if not state:
            state = {
                'in_fire': False,
                'active_timer': None,
                'lingering_timer': None,
                'remaining_ticks': 0
            }
            self._fire_state[fire_id] = state

        if state['in_fire']:
            return  # already burning

        state['in_fire'] = True
        state['remaining_ticks'] = 0

        # stop lingering
        state['lingering_timer'] = None

        def burn_tick():
            if not state['in_fire'] or not self.is_alive():
                state['active_timer'] = None
                return

            self.handlemessage(bs.HitMessage(flat_damage=10))
            bs.emitfx(position=self.node.position, count=5,
                    chunk_type='spark', scale=5)
            self._safe_play_sound(bs.getsound('Firehurt'), 1.5)

        if not state['active_timer']:
            state['active_timer'] = bs.Timer(0.5, burn_tick, repeat=True)


    def leave_fire(self, fire_id):
        state = self._fire_state.get(fire_id)
        if not state or not state['in_fire']:
            return

        state['in_fire'] = False
        state['remaining_ticks'] = 4

        def lingering_tick():
            if state['remaining_ticks'] <= 0 or not self.is_alive():
                state['lingering_timer'] = None
                self._fire_state.pop(fire_id, None)
                return

            self.handlemessage(bs.HitMessage(flat_damage=5))
            bs.emitfx(position=self.node.position, count=5,
                    chunk_type='spark', scale=5)
            self._safe_play_sound(bs.getsound('Firehurt'), 1.5)
            state['remaining_ticks'] -= 1

        state['lingering_timer'] = bs.Timer(1.0, lingering_tick, repeat=True)
    
    def clear_fire(self):
        for state in self._fire_state.values():
            state['in_fire'] = False
            state['remaining_ticks'] = 0
            state['lingering_timer'] = None
            state['active_timer'] = None
        
