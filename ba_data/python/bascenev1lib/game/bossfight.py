# Released under the MIT License. See LICENSE for details.
#
"""Provides Onslaught Co-op game."""

# Yes this is a long one..
# pylint: disable=too-many-lines

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import math
import random
import logging
from enum import Enum, unique
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

import bascenev1 as bs
import babase


from bascenev1lib.actor.respawnicon import RespawnIcon

from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.actor.bomb import TNTSpawner
from bascenev1lib.actor.playerspaz import PlayerSpazHurtMessage
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.controlsguide import ControlsGuide
from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory
import weakref
from bascenev1lib.actor.bomb import Bomb, Blast
from bascenev1lib.actor.spazbot import (
    SpazBotDiedMessage,
    SpazBotSet,
    ChargerBot,
    StickyBot,
    BomberBot,
    BomberBotLite,
    BrawlerBot,
    BrawlerBotLite,
    TriggerBot,
    BomberBotStaticLite,
    TriggerBotStatic,
    BomberBotProStatic,
    TriggerBotPro,
    ExplodeyBot,
    ExplodeyBotShielded,
    ExplodeyBotNoTimeLimit,
    BrawlerBotProShielded,
    ChargerBotProShielded,
    BomberBotPro,
    TriggerBotProShielded,
    BrawlerBotPro,
    BomberBotProShielded,
    # custom bots start here! wow... thats a hefty lot.
    StoneBot,
    ProStoneBot,
    ProStoneBotShielded,
    BouncyBot,
    MineBot,
    SlowBot,
    BouncySlowBot,
    AggroMineBot,
    AggroMineBotShielded,
    StickyBotLite,
    ProStickyBotShielded,
    ProStickyBot,
    PlayerBot,
    PlayerBotShielded,
    NegativeBot,
    ProNegativeBot,
    ProNegativeBotShielded,
    EggBot,
    EggBotShielded,
    ZeusBot,
    ImpulseBot,
    ProImpulseBot,
    ProImpulseBotShielded,
    MiniBot,
    ProMiniBot,
    ProMiniBotShielded,
    BoogieBot,
    EletricBot,
    StarBot,
    ProStarBot,
    ProStarBotShielded,
    LoveBot,
    BoomBot,
    ProBoomBot,
    ProBoomBotShielded,
    ImpulseBotLite,
    MiniBotLite,
    LandMine,
    B2BBot,
    ProB2BBot,
    ProB2BBotShielded,
    DumbassBot,
    GarbageBot1,
    GarbageBot2,
    GarbageBot3,
    GarbageBot4,
    GoldenBot,
    ProGoldenBot,
    ProGoldenBotShielded,

)

if TYPE_CHECKING:
    from typing import Any, Sequence
    from bascenev1lib.actor.spazbot import SpazBot

from bascenev1lib.actor.spaz import Spaz



class Boss(Spaz):

    def __init__(self, pos=(0,0,0), color = ..., highlight = ..., character = 'Spaz', source_player = None, start_invincible =False, can_accept_powerups = True, powerups_expire = False, demo_mode = False, cosmetic = None):
        super().__init__(color, highlight, character, None, True, False, True, False, cosmetic=cosmetic)

        self.starting_pos = pos

        """

        modes:

        aura farming: stand and aura farm

        fight: go and fight people

        
        
        
        """

        self.mode = 'aura farming'
        

        self.handlemessage(bs.StandMessage(self.starting_pos))
        # No knockback, we calculate damage on our own.
        self.impact_scale = 0.2
        self.real_impact = 0.1

        self.hitpoints_max =  6700 * 10
        self.hitpoints = self.hitpoints_max
        self.node.name = self.getactivity()._boss_name
        self.node.name_color = color
    def start(self):
        bs.timer(0.1, self.boss_tick, repeat=True)

        
        bs.timer(10.0, self.bomb_rain, repeat=True)
        bs.timer(13.0, self.targeted_projectile, repeat=True)
        bs.timer(20.0, self.shockwave_slam, repeat=True)
        bs.timer(12, self.spawn_reinforcement, repeat=True)
    
    def spawn_reinforcement(self):
        if not self.is_alive():
            return
        

       
        spawn_points = [getattr(Point, p) for p in dir(Point) if not p.startswith('__')]
        ALL_BOTS = (
            ChargerBot,
            StickyBot,
            BomberBot,
            BomberBotLite,
            BrawlerBot,
            BrawlerBotLite,
            TriggerBot,
            BomberBotStaticLite,
            TriggerBotStatic,
            BomberBotProStatic,
            TriggerBotPro,
            ExplodeyBot,
            ExplodeyBotShielded,
            ExplodeyBotNoTimeLimit,
            BrawlerBotProShielded,
            ChargerBotProShielded,
            BomberBotPro,
            TriggerBotProShielded,
            BrawlerBotPro,
            BomberBotProShielded,
            # custom bots
            StoneBot,
            ProStoneBot,
            ProStoneBotShielded,
            BouncyBot,
            MineBot,
            SlowBot,
            BouncySlowBot,
            AggroMineBot,
            AggroMineBotShielded,
            StickyBotLite,
            ProStickyBotShielded,
            ProStickyBot,
            PlayerBot,
            PlayerBotShielded,
            NegativeBot,
            ProNegativeBot,
            ProNegativeBotShielded,
            EggBot,
            EggBotShielded,
            ZeusBot,
            ImpulseBot,
            ProImpulseBot,
            ProImpulseBotShielded,
            MiniBot,
            ProMiniBot,
            ProMiniBotShielded,
            BoogieBot,
            EletricBot,
            StarBot,
            ProStarBot,
            ProStarBotShielded,
            LoveBot,
            BoomBot,
            ProBoomBot,
            ProBoomBotShielded,
            ImpulseBotLite,
            MiniBotLite,
            LandMine,
            B2BBot,
            ProB2BBot,
            ProB2BBotShielded,
            DumbassBot,
            GarbageBot1,
            GarbageBot2,
            GarbageBot3,
            GarbageBot4,
            GoldenBot,
            ProGoldenBot,
            ProGoldenBotShielded,
        )
        bots = self.getactivity()._bots
        assert isinstance(bots, SpazBotSet)
        for i in range(random.randint(2, 3)):
            bot_class = random.choice(ALL_BOTS)
            pos = random.choice(spawn_points)

            bots.spawn_bot(bot_class, self.getactivity().map.defs.points[pos.value], 3)


    def bomb_rain(self):
        if not self.is_alive():
            return
        self.celebrate(0.4)
        for _ in range(5): 
            
            
            x = random.uniform(-10, 10)
            z = random.uniform(-3, 3)
            pos = (x, 5, z)  # drop from above
            Bomb(position=pos).autoretain()

   
    def targeted_projectile(self):

        if not self.is_alive():
            return
        self.celebrate(4)
        players = [p.actor for p in self.getactivity().players if hasattr(p, 'actor')]
        if not players:
            return
        target = random.choice(players)
        if not target.node.exists():
            return
        boss_pos = self.node.position
        target_pos = target.node.position
        #direction = (target_pos[0]-boss_pos[0],
        #             target_pos[1]-boss_pos[1],
        #             target_pos[2]-boss_pos[2])
        #magnitude = 15.0
        
        proj = Bomb(position=boss_pos).autoretain()
        
        def haha():
            
            assert isinstance(proj.node, bs.NodeVisualizer)
            if proj.node.exists():
                proj.node.position = (target_pos[0], target_pos[1] + 1.1, target_pos[2])
        bs.timer(2, haha)
        

   
    def shockwave_slam(self):
        if not self.is_alive():
            return
        self.celebrate(1)
       
        players = [p.actor for p in self.getactivity().players if hasattr(p, 'actor')]
        if not players:
            return
        target = random.choice(players)
        if not target.node.exists():
            return

        target_pos = target.node.position
        warning_light = bs.newnode('light',
            attrs={
                'position': (target_pos[0], target_pos[1]-0.5, target_pos[2]), 
                'color': (1, 0, 0),            
                'radius': 2.0,                  
                'height_attenuated': True,
                'volume_intensity_scale': 1.0
            })

        # Animate radius pulsing for 1 second
        bs.animate(warning_light, 'radius', {
            0.0: 0.0,    
            0.5: 5.0,      
            1.0: 0.0    
        })

        
        bs.animate_array(warning_light, 'color', 3, {
            0.0: (1, 0, 0),
            0.5: (1, 0.3, 0.3),
            1.0: (1, 0, 0)
        })

        # Remove the light after 1 second
        bs.timer(1.0, warning_light.delete)

        # Delay shockwave to give players time to react
        bs.timer(1.0, lambda target_pos=target_pos: self._execute_shockwave(pos=target_pos))

    def _execute_shockwave(self, pos):
        Blast(position=pos, blast_radius=2).autoretain()
        

    def immune(self):
        if not self.node:
            return
        PopupText('IMMUNE', color=(0, 0.9, 1),
                            scale=0.5,
                            position = self.node.position,
                          
                            ).autoretain()

    def boogie(self):
        # We dont get boogied.
        self.immune()
    
    def handleshieldbreaker(self):
        # We dont take electric damage.
        self.immune()
    
    def add_slowness(self, value, time):
        # We dont go slow.
        self.slowness = 0
        self.immune()
       
    
    def _hit_self(self, intensity):
        """ No """

    
    
    
    
    def boss_tick(self):
        if not self.node:
            return
        
        self.on_hold_position_release()
        self.node.move_left_right = 0
        self.node.move_up_down = 0
        
        

        if self.mode == 'aura farming':
            
            self.node.move_left_right = 0
            self.node.move_up_down = -1
            self.on_hold_position_press()
            
            
            

            if self.hitpoints <= self.hitpoints_max * 0.5:
                self.start_phase_two()
            
        elif self.mode == 'fight':
            
            self.follow_nearest_player()

        
            
    
    def celebrate(self, duration: float = 3.0):
        self.handlemessage(bs.CelebrateMessage(duration=duration))
    
    def follow_nearest_player(self):
        players = [p.actor for p in self.getactivity().players if hasattr(p, 'actor') and p.actor and p.actor.node and p.actor.node.exists()]
        if not players:
            return
        
        

        
        
        # Nearest player
        my_pos = self.node.position
        nearest = min(players, key=lambda p: (p.node.position[0]-my_pos[0])**2 + (p.node.position[2]-my_pos[2])**2)
        assert isinstance(nearest, Spaz)
      

        target_pos = nearest.node.position
        

        dx = target_pos[0] - my_pos[0]
        dz = target_pos[2] - my_pos[2]

        
        length = (dx**2 + dz**2) ** 0.5
        if length > 0.001:
            move_x = dx / length
            move_z = dz / length
        else:
            move_x, move_z = 0, 0

        move_x = max(-1, min(1, move_x))
        move_z = max(-1, min(1, move_z))

        movement_speed = 0.85

        
        self.node.move_left_right = move_x * movement_speed
        self.node.move_up_down = -move_z * movement_speed

          
        if length < 1.0 and random.randint(0, 4) == 0:  
           
            self.on_punch_press()
            self.on_punch_release()
                
  

    def start_phase_two(self):
        self.mode = 'fight'
        bs.broadcastmessage("The Boss Descends!", color=(1, 0, 0))

    
        light = bs.newnode('light', attrs={
            'position': self.node.position,
            'color': (1, 0, 0),
            'radius': 0.5,
            'intensity': 2.0
        })
        bs.animate(light, 'intensity', {0.0: 1, 0.5: 5, 1.0: 0})
        bs.timer(1.0, light.delete)

        
        self.handlemessage(bs.StandMessage(self.getactivity()._spawn_center)) # center of courtyard
        bs.emitfx(position=(0, 1.5, 0), count=30, scale=1.5,
                spread=1.0, chunk_type='spark')

        
        self.node.handlemessage('knockout', 500.0)



    def handlemessage(self, msg):
        if isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.StandMessage(self.starting_pos))
        
        elif isinstance(msg, bs.HitMessage):
            # First let the original handle it (for effects)
          
            self.impact_scale = 0

            # So it doesnt say 'CRITICAL HIT!'
            # and adding it to the counter
            crit_boosted = msg.crit_boosted
            msg.crit_boosted = False
            if msg.hit_subtype == 'heart':
                self.immune()
                return 
            super().handlemessage(msg)
            if not self.node:
                return
            
            acceptable_hit_types = ['explosion']

            if self.mode == 'fight':
                acceptable_hit_types.append('punch')
            
            if msg.hit_type not in acceptable_hit_types:
                return
            
            
            
            #self.node.handlemessage(
            #        'impulse',
            #        msg.pos[0],
            #        msg.pos[1],
            #        msg.pos[2],
            #        msg.velocity[0],
            #        msg.velocity[1],
            #        msg.velocity[2],
            #        mag,
            #        velocity_mag,
            #        msg.radius,
            #        0,
            #        msg.force_direction[0],
            #        msg.force_direction[1],
            #        msg.force_direction[2],
            #    )
            mag = msg.magnitude * self.real_impact
            velocity_mag = msg.velocity_magnitude * self.real_impact
            damage_scale = 0.22 
            if msg.hit_type == 'punch':
                # letem take more damage to punches
                damage_scale *= 1.7
            
            self.node.handlemessage(
                    'impulse',
                    msg.pos[0],
                    msg.pos[1],
                    msg.pos[2],
                    0,
                    0,
                    0,
                    mag,
                    velocity_mag,
                    msg.radius,
                    1,
                    0,
                    0,
                    0,
                )
            complete_damage = damage_scale * self.node.damage / self.real_impact


            self.hitpoints -= complete_damage
            if crit_boosted:
                # We dont take critical damage.
                self.immune()
            
            if self.hitpoints < 1:
                self.handlemessage(bs.DieMessage())
            
        
        elif isinstance(msg, bs.FreezeMessage):
            # We dont freeze.
            self.immune()
            return None


        else:
            return super().handlemessage(msg)



@dataclass
class Wave:
    """A wave of enemies."""

    entries: list[Spawn | Spacing | Delay | None]
    base_angle: float = 0.0


@dataclass
class Spawn:
    """A bot spawn event in a wave."""

    bottype: type[SpazBot] | str
    spacing: float = 5.0


@dataclass
class Spacing:
    """Empty space in a wave."""

    spacing: float = 5.0


@unique
class Point(Enum):
    """Points on the map we can spawn at."""

    LEFT_UPPER_MORE = 'bot_spawn_left_upper_more'
    LEFT_UPPER = 'bot_spawn_left_upper'
    TURRET_TOP_RIGHT = 'bot_spawn_turret_top_right'
    RIGHT_UPPER = 'bot_spawn_right_upper'
    TURRET_TOP_MIDDLE_LEFT = 'bot_spawn_turret_top_middle_left'
    TURRET_TOP_MIDDLE_RIGHT = 'bot_spawn_turret_top_middle_right'
    TURRET_TOP_LEFT = 'bot_spawn_turret_top_left'
    TOP_RIGHT = 'bot_spawn_top_right'
    TOP_LEFT = 'bot_spawn_top_left'
    TOP = 'bot_spawn_top'
    BOTTOM = 'bot_spawn_bottom'
    LEFT = 'bot_spawn_left'
    RIGHT = 'bot_spawn_right'
    RIGHT_UPPER_MORE = 'bot_spawn_right_upper_more'
    RIGHT_LOWER = 'bot_spawn_right_lower'
    RIGHT_LOWER_MORE = 'bot_spawn_right_lower_more'
    BOTTOM_RIGHT = 'bot_spawn_bottom_right'
    BOTTOM_LEFT = 'bot_spawn_bottom_left'
    TURRET_BOTTOM_RIGHT = 'bot_spawn_turret_bottom_right'
    TURRET_BOTTOM_LEFT = 'bot_spawn_turret_bottom_left'
    LEFT_LOWER = 'bot_spawn_left_lower'
    LEFT_LOWER_MORE = 'bot_spawn_left_lower_more'
    TURRET_TOP_MIDDLE = 'bot_spawn_turret_top_middle'
    BOTTOM_HALF_RIGHT = 'bot_spawn_bottom_half_right'
    BOTTOM_HALF_LEFT = 'bot_spawn_bottom_half_left'
    TOP_HALF_RIGHT = 'bot_spawn_top_half_right'
    TOP_HALF_LEFT = 'bot_spawn_top_half_left'

@dataclass
class Delay:
    """A delay between events in a wave."""

    duration: float








class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.has_been_hurt = False
        self.respawn_wave = 0
        self.respawn_timer: bs.Timer | None = None
        self.respawn_icon: RespawnIcon | None = None
        self.lives: int = 3


class Team(bs.Team[Player]):
    """Our team type for this game."""


class BossFightGame(bs.CoopGameActivity[Player, Team]):
    """Co-op game where players try to survive and kill a boss."""

    name = 'The Finale'
    description = 'Kill the boss to win.'
    scoreconfig = bs.ScoreConfig(
        scoretype=bs.ScoreType.MILLISECONDS, version='B'
    )

    

    # Show messages when players die since it matters here.
    announce_player_deaths = True

    @override
    def get_score_type(self) -> str:
        return 'time'
    
    def __init__(self, settings: dict):
       
        
        settings['map'] = 'Courtyard'

        super().__init__(settings)

        self._new_wave_sound = bs.getsound('scoreHit01')
        self._winsound = bs.getsound('score')
        self._cashregistersound = bs.getsound('cashRegister')
    
        

        # FIXME: should use standard map defs.
        
        self._spawn_center = (0, 3, -2)
        self._tntspawnpos = (0.0, 3.0, 2.1)
        self._powerup_center = (0, 5, -1.6)
        self._powerup_spread = (4.6, 2.7)
       

        self._scoreboard: Scoreboard | None = None
        self._game_over = False
        self._wavenum = 0
        self._can_end_wave = True
        self._score = 0
        self._time_bonus = 0
        self._spawn_info_text: bs.NodeActor | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._dingsoundhigh = bs.getsound('dingSmallHigh')
        self._have_tnt = False
        self._excluded_powerups: list[str] | None = None
        self._waves: list[Wave] = []
        self._tntspawner: TNTSpawner | None = None
        self._bots: SpazBotSet | None = None
        self._powerup_drop_timer: bs.Timer | None = None
        self._time_bonus_timer: bs.Timer | None = None
        self._time_bonus_text: bs.NodeActor | None = None
        self._flawless_bonus: int | None = None
        self._wave_text: bs.NodeActor | None = None
        self._wave_update_timer: bs.Timer | None = None
        self._final_time_ms: int | None = None
        self._starttime_ms: int | None = None
        self._boss_text: bs.NodeVisualizer | None = None

        self._boss_name = 'Ultimate Spaz'
        


        
     

        self.pizza_tower =  babase.app.config.get("GUMMY_blockvanillaplayers", False)
       

        if self.pizza_tower:
            self.combo_system = GlobalComboSystem( )
        
           


    @override
    def on_transition_in(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        super().on_transition_in()
        
        self._spawn_info_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'position': (15, -130),
                    'h_attach': 'left',
                    'v_attach': 'top',
                    'scale': 0.55,
                    'color': (0.3, 0.8, 0.3, 1.0),
                    'text': '',
                },
            )
        )

       

        gnode = self.globalsnode
        gnode.tint = (0.5, 0.3, 0.72)
        bs.setmusic(bs.MusicType.BOSSFIGHT)
       

    def boss_taunt(self, taunt: str = 'text line lalala'):
        """Show a taunt at the bottom of the screen with twist & fade."""
        # import bascenev1 as bs;bs.getactivity().boss_taunt()
        
        self._boss_text = bs.newnode('text',
            attrs={
                'text': f"\"{taunt}\"",
                'scale': 1.0,
                'maxwidth': 800,
                'position': (-250, -200),
                'h_align': 'left',
                'v_align': 'bottom',
                'shadow': 1.0,
                'flatness': 1.0,
                'color': (1, 0.2, 0.2),
                'in_world': False
            }
        )

        bs.animate(self._boss_text, 'opacity', {
                0.0: 0,
                0.3: 0.8,
                3: 1.0
        })

        def delete():


            bs.animate(self._boss_text, 'opacity', {
                0.0: 1.0,
                3.0: 1.0,
                3.5: 0.0
            })

            bs.animate(self._boss_text, 'rotate', {
                0.0: 0,   
                0.242: -1.2, 
                0.253: -0.34,
                2.0: 0.0,
                3.5: 3.4 
            })

            bs.timer(4.0, self._boss_text.delete)
        bs.timer(2, delete)

    def start(self):
        starttime_ms = int(bs.time() * 1000.0)
        assert isinstance(starttime_ms, int)
        self._starttime_ms = starttime_ms
        
        self._time_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'color': (1, 1, 0.5, 1),
                    'flatness': 0.5,
                    'shadow': 0.5,
                    'position': (0, -50),
                    'scale': 1.3,
                    'text': '',
                },
            )
        )
        self._time_text_input = bs.NodeActor(
            bs.newnode('timedisplay', attrs={'showsubseconds': True})
        )
        self.globalsnode.connectattr(
            'time', self._time_text_input.node, 'time2'
        )
        assert self._time_text_input.node
        assert self._time_text.node
        self._time_text_input.node.connectattr(
            'output', self._time_text.node, 'text'
        )
         # We generate these on the fly in endless.
        
        self._have_tnt = True
        self._excluded_powerups = []
        self._excluded_powerups.append('cloak')
        # FIXME: Should migrate to use setup_standard_powerup_drops().

        # Spit out a few powerups and start dropping more shortly.
        self._drop_powerups(
            standard_points=True,
            poweruptype=(
                None
            ),
        )
        bs.timer(4.0, self._start_powerup_drops)

        # Our TNT spawner (if applicable).
        if self._have_tnt:
            self._tntspawner = TNTSpawner(position=self._tntspawnpos)

        self.setup_low_life_warning_sound()
        self._update_scores()
        self._bots = SpazBotSet()
        self.boss.start()
        for p in self.players:
            p.actor.connect_controls_to_player()
        bs.timer(3.63, self.start_ticking, repeat=True)
        bs.getsound('score').play(1.5)

    @override
    def on_begin(self) -> None:
        super().on_begin()
        
        tintcolor = self.globalsnode.tint

        bs.animate_array(self.globalsnode, 'tint', 3, {
            0.0: (5, 5, 0),
            3.0: tintcolor
        })

        
        
        

       
    

        
        
        self.boss = Boss(pos=(-0.07, 4.288, -8.056), color=(1,0,0), highlight=(1,1,1), cosmetic='Spaz.EXE')

        if len(self.players) == 1:
            self.boss.hitpoints_max =  5700 * 10
            self.boss.hitpoints = self.boss.hitpoints_max
        yoffs = -80
       
        self.hp_bg = bs.newnode('image',
            attrs={
                'texture': bs.gettexture('flagColor'),
                'color': (0.3,0.3, 0.3),
                'opacity': 0.7,
                'scale': (600, 30),  
                'position': (0, -200+yoffs),
                'attach': 'center',
             
            })

        
        self.hp_bar = bs.newnode('image',
            attrs={
                'texture': bs.gettexture('bar'),
                'color': (1,0,0),
                'scale': (600, 30),
                'position': (0, -200+yoffs),
                'attach': 'center'
            })

    
        self.hp_text = bs.newnode('text',
            attrs={
                'text': self._boss_name,
                'position': (0, -175+yoffs),
                'scale': 1.3,
                'h_align': 'center',
                'v_attach': 'center',
                'color': (1,1,1),
                'in_world': False
            })
        
        self.boss_hp_text = bs.newnode(
            'text',
            attrs={
                'text': f"{int(self.boss.hitpoints/10)}/{int(self.boss.hitpoints_max/10)}",
                'position':  (0, -265+yoffs),
                'h_align': 'center',
                'v_attach': 'center',
                'color': (1, 0.4, 0.4),
                'scale': 1.0
            }
        )
        
        # animate it all in :>

        delay = 3.5

        self.hp_bar.scale = (0, 30)
        bs.animate_array(self.hp_bar, 'scale', 2, {
            0.0: (0, 30),
            delay: (600, 30)
        })



        
        self.hp_text.opacity = 0.0
        bs.animate(self.hp_text, 'opacity', {
            0.0: 0.0,
            delay-delay*0.1: 1.0
        })
        self.entries = {} 
        spacing = 35  
        i = 0

        for player in self.players:
            pos_x = 50
            pos_y = -50 - i * spacing
            i += 1

            # Text (lives count)
            text = bs.newnode('text',
                attrs={
                    'text': f"{player.getname()} x{player.lives}",
                    'position': (pos_x + 50, pos_y),
                    'h_align': 'left',
                    'v_attach': 'top',
                    'color': (1, 1, 1),
                    'scale': 1.0
                })

            self.entries[player] = {
                'text': text,
                'dead': False
            }

        self.start()
       

        
    
    def update_lives(self, player, lives: int, leaving_game: bool = False):
        """Update one player's lives UI."""



        entry = self.entries[player]
        entry['text'].text = f"{player.getname()} x{lives}"
        bs.animate(entry['text'], 'rotate', {
                0.0: 0,
                0.1: 5,   
                1.3141: 0    
            })

        # If we're dead, animate red and go transparent.
        if lives < 1 and not entry['dead'] or leaving_game:
            bs.animate_array(entry['text'], 'color', 3, {
                0.0: (1, 1, 1),
                0.2: (0.5, 0.5, 0.5) if leaving_game else (1, 0, 0)
            })

            things_lmao = [
                'LOST',
                'GAVE UP',
                'QUITTER',
                '?@!&',
                'RAGEQUIT',
                'SEE YA',
                'FLED',
                'DROPPED OUT',
                'NOOB MOVE',
                'COWARD',
                'I WIN.'

            ]
            if leaving_game:
                entry['text'].text = f"{player.getname()} x{random.choice(things_lmao)}"
            
            # Fade out text and icon
            bs.animate(entry['text'], 'opacity', {
                0.0: 1.0,
                1.0: 0.0
            })
            entry['dead'] = True

            death_sounds = [
                bs.getsound('finalLifeLost01'),
                bs.getsound('finalLifeLost02'),
                bs.getsound('finalLifeLost03'),
                bs.getsound('finalLifeLost04'),
            ]

            random.choice(death_sounds).play(2)
           


        
    
    def start_ticking(self):
        bs.timer(0.1, self.tick, repeat=True)



    def tick(self):
        if self.boss:
            if not self.boss.is_alive():
                self.do_end('victory', 4.0)
                return

        else:
           self.do_end('victory', 4.0)
           return
        self.hp_bar.scale = (
            600 * (self.boss.hitpoints/ self.boss.hitpoints_max),
            30
        )
        if self.boss_hp_text:
            self.boss_hp_text.text = f"{int(self.boss.hitpoints/10)}/{int(self.boss.hitpoints_max/10)}"

    
    @override
    def spawn_player(self, player: Player) -> bs.Actor:
        # We keep track of who got hurt each wave for score purposes.
        player.has_been_hurt = False
        pos = (
            self._spawn_center[0] + random.uniform(-1.5, 1.5),
            self._spawn_center[1],
            self._spawn_center[2] + random.uniform(-1.5, 1.5),
        )
        spaz = self.spawn_player_spaz(player, position=pos)

        # Give them double hp and less damage / knockback due to to the sheer amount spawning.
        spaz.impact_scale = 0.53
        spaz.hitpoints_max = 220 * 10
        spaz.hitpoints = spaz.hitpoints_max
        
        
        
       
        return spaz

    def on_player_leave(self, player):
        self.update_lives(player, 0, leaving_game=True)
        return super().on_player_leave(player)
    

    def _drop_powerup(self, index: int, poweruptype: str | None = None) -> None:
        poweruptype = PowerupBoxFactory.get().get_random_powerup_type(
            forcetype=poweruptype, excludetypes=self._excluded_powerups
        )
        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=poweruptype,
        ).autoretain()

    def _start_powerup_drops(self) -> None:
        self._powerup_drop_timer = bs.Timer(
            3.0, bs.WeakCall(self._drop_powerups), repeat=True
        )

    def _drop_powerups(
        self, standard_points: bool = False, poweruptype: str | None = None
    ) -> None:
        """Generic powerup drop."""
        if standard_points:
            points = self.map.powerup_spawn_points
            for i in range(len(points)):
                bs.timer(
                    1.0 + i * 0.5,
                    bs.WeakCall(
                        self._drop_powerup, i, poweruptype if i == 0 else None
                    ),
                )
        else:
            point = (
                self._powerup_center[0]
                + random.uniform(
                    -1.0 * self._powerup_spread[0],
                    1.0 * self._powerup_spread[0],
                ),
                self._powerup_center[1],
                self._powerup_center[2]
                + random.uniform(
                    -self._powerup_spread[1], self._powerup_spread[1]
                ),
            )

            # Drop one random one somewhere.
            PowerupBox(
                position=point,
                poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
                    excludetypes=self._excluded_powerups
                ),
            ).autoretain()

    def do_end(self, outcome: str, delay: float = 0.0) -> None:
        """End the game with the specified outcome."""
        if self._game_over:
            return
        self._game_over = True
        self._final_time_ms = int(
                            int(bs.time() * 1000.0) - self._starttime_ms
                        )
        self._time_text_timer = None
        
        assert (
                            self._time_text_input is not None
                            and self._time_text_input.node
                        )
        self._time_text_input.node.timemax = self._final_time_ms
        if outcome == 'victory':
            bs.setmusic(bs.MusicType.VICTORY)
            self._bots.stop_moving()
            self.show_zoom_message(
                                bs.Lstr(resource='victoryText'),
                                scale=1.0,
                                duration=4.0,
                            )
            self.celebrate(10.0)
            # Per person.
            for p in self.initialplayerinfos:
                bs.app.plus.xp_sys.award_xp(1000, True, scrnmessage=True)

       
        if outcome == 'defeat':
            self.fade_to_red()
            bs.setmusic(None)
        assert self._final_time_ms is not None
        scoreval = (
            None if outcome == 'defeat' else int(self._final_time_ms // 10)
        )
        
                        
        self.end(
            
            results={
                'outcome': outcome,
                'score': scoreval,
                'score_order': 'decreasing',
                'playerinfos': self.initialplayerinfos,
            },
            delay=delay,
        )
        
    def do_end_old(self, outcome: str, delay: float = 0.0) -> None:
        """End the game with the specified outcome."""
        if outcome == 'defeat':
            self.fade_to_red()
        score: int | None
        if self._wavenum >= 2:
            score = self._score
            fail_message = None
        else:
            score = None
            fail_message = bs.Lstr(resource='reachWave2Text')
        
        
        self.end(
            {
                'outcome': outcome,
                'score': score,
                'fail_message': fail_message,
                'playerinfos': self.initialplayerinfos,
                
            },
            delay=delay,
        )

    
    def add_bot_at_point(
        self, point: tuple[float, float, float], spaz_type: type[SpazBot], spawn_time: float = 1.0
    ) -> None:
        """Add a new bot at a specified named point."""
        if self._game_over:
            return
       
      
        assert self._bots is not None
        self._bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time)

    def add_bot_at_angle(
        self, angle: float, spaz_type: type[SpazBot], spawn_time: float = 1.0
    ) -> None:
        """Add a new bot at a specified angle (for circular maps)."""
        if self._game_over:
            return
        angle_radians = angle / 57.2957795
        xval = math.sin(angle_radians) * 1.06
        zval = math.cos(angle_radians) * 1.06
        point = (xval / 0.125, 2.3, (zval / 0.2) - 3.7)
        assert self._bots is not None
        self._bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time)

    
    def _update_scores(self) -> None:
        return
        score = self._score
        
        assert self._scoreboard is not None
        self._scoreboard.set_team_value(self.teams[0], score, max_score=None)

    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        if isinstance(msg, PlayerSpazHurtMessage):
            msg.spaz.getplayer(Player, True).has_been_hurt = True
            self._a_player_has_been_hurt = True

        elif isinstance(msg, bs.PlayerScoredMessage):
            self._score += msg.score
            self._update_scores()

        elif isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment standard behavior.
            player = msg.getplayer(Player)
            self._a_player_has_been_hurt = True

            player.lives -= 1

            can_respawn = not player.lives < 1

            if can_respawn:
                players_not_perm_ded = []

                for p in self.players:
                    if not p.lives < 1:
                        players_not_perm_ded.append(p)


            
                respawn_time = int(2.0 + len(players_not_perm_ded) * 4.8)
                if len(players_not_perm_ded) == 1:
                    respawn_time = 2
                player.respawn_timer = bs.Timer(
                    respawn_time, bs.Call(self.spawn_player_if_exists, player)
                )
                player.respawn_icon = RespawnIcon(player, respawn_time)
            else:

                taunt = None
                character = player.actor.character
                cosmetic = player.actor.cosmetic
               

                if character == 'Spaz':
                    taunt = 'Newbie? I can agree.'
                    if cosmetic == 'Spaz.EXE':
                        taunt = 'I\'m the better EXE.'
                    elif cosmetic == 'Sal':
                        taunt = 'Child of Spaz and Zoe? So underdeveloped.'
                elif character == 'Kronk':
                    taunt = 'All those muscles... and for what?'
                elif character == 'Zoe':
                    taunt = 'Let it happen....'
                elif character == 'Jack Morgan':
                    taunt = 'Heh.'
                elif character == 'Mel':
                    taunt = 'Fatass.'
                elif character == 'Snake Shadow':
                    taunt = 'Not worth my time.'
                elif character == 'Bones':
                    taunt = 'Back to the grave to you!'
                elif character == 'Bernard':
                    taunt = 'You\'re annoying.'
                elif character == 'Agent Johnson':
                    taunt = 'Mission failed.'
                elif character == 'Frosty':
                    taunt = 'Who brought a snowman here?'
                elif character == 'Pascal':
                    taunt = 'Why are you here? Back to antartica.'
                elif character == 'Pixel':
                    taunt = 'I outta rip your wings out.'
                elif character == 'Santa Claus':
                    taunt = 'Arent you fake?'
                elif character == 'Easter Bunny':
                    taunt = 'I feel bad.'
                    if cosmetic == 'Tophat':
                        taunt = 'Stupid hat, lol'
                elif character == 'Taobao Mascot':
                    taunt = 'Who are you?'
                elif character == 'Grumbledorf':
                    taunt = 'No magic can save you from me.'
                elif character == 'B-9000':
                    taunt = 'Your Body is no match for me.'
                elif character == 'Agent Spaz':
                    taunt = 'What a knock off.'
                elif character == 'Amar':
                    taunt = 'Such a looie knockoff.'
                    if cosmetic == 'Full-Insanity':
                        taunt = 'You\'re insane? Me too.'
                elif character == 'Bob':
                    taunt = 'AI voice...'
                elif character == 'Watory':
                    taunt = 'Is that water?'
                elif character == 'Space Guy':
                    taunt = 'I used to play with Legos.'
                elif character == 'VR-Cache':
                    taunt = 'Nice VR Headset. Its mine.'
                elif character == 'Peppino Spaghetti':
                    taunt = 'I\'m faster. And Better.'
                elif character == 'Theodore Noise':
                    taunt = 'GOD. SHUT UP!'
                elif character == 'Penny':
                    taunt = '...'
                elif character == 'Orange Cap':
                    taunt = 'Easy trash, you\'re so bad get outta my game.'
                    if cosmetic == 'Blue Cap':
                        taunt = 'Who the fuck are you?'
                elif character == 'Betty':
                    taunt = 'Old Lady.'
                elif character == 'ire':
                    taunt = 'Who??'
                elif character == 'Rem':
                    taunt = 'Girly!'
                elif character == 'Fennekin':
                    taunt = 'Chespin will never see you again...'



                if taunt is None: self.boss_taunt()
                else: self.boss_taunt(taunt)
            self.update_lives(player=player, lives=player.lives)
            self._checkroundover()
           
            

        elif isinstance(msg, SpazBotDiedMessage):
            pts, importance = msg.spazbot.get_death_points(msg.how)
            if msg.killerplayer is not None:
                if self.pizza_tower:
                    bs.getsound('sfx_killenemy').play()
                    bs.getsound('sfx_killingblow').play()
                    if self.combo_system.active:
                        self.combo_system.extend_combo()
                    else:
                        self.combo_system.start_combo()
                
                
                
                
                dingsound = (
                    self._dingsound if importance == 1 else self._dingsoundhigh
                )
                dingsound.play(volume=0.6)

            # Normally we pull scores from the score-set, but if there's
            # no player lets be explicit.
            else:
                self._score += pts
            self._update_scores()
        else:
            super().handlemessage(msg)

    

    

    def _set_can_end_wave(self) -> None:
        self._can_end_wave = True

    @override
    def end_game(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        # Tell our bots to celebrate just to rub it in.
        assert self._bots is not None
        self._bots.final_celebrate()
       
        self.do_end('defeat', delay=2.0)
        
        


    def _checkroundover(self) -> None:
        """Potentially end the round based on the state of the game."""
        if self.has_ended():
            return
        
        alive = []
        
        # If no one has lives, end the game.
        for player in self.players:
            if not player.lives < 1:
                alive.append(player)
        if not alive:
            self.end_game()

class Scoreboard_Dmg:
    """A display for player or team scores during a game.

    category: Gameplay Classes
    """

    _ENTRYSTORENAME = bs.storagename('entry')

    def __init__(self, label: bs.Lstr | None = None, score_split: float = 0.7):
        """Instantiate a scoreboard.

        Label can be something like 'points' and will
        show up on boards if provided.
        """
        self._flat_tex = bs.gettexture('null')
        self._entries: dict[int, _Entry2] = {}
        self._label = label
        self.score_split = score_split

        self._pos: Sequence[float]
        self._do_cover = False
        self._spacing = 35.0
        self._pos = (1100, -200)
        self._scale = 1
        self._flash_length = 0.5

    def set_team_value(
        self,
        team: bs.Team,
        score: float,
        max_score: float | None = None,
        countdown: bool = False,
        flash: bool = True,
        show_value: bool = True,
    ) -> None:
        """Update the score-board display for the given bs.Team."""
        if team.id not in self._entries:
            self._add_team(team)

            # Create a proxy in the team which will kill
            # our entry when it dies (for convenience)
            assert self._ENTRYSTORENAME not in team.customdata
            team.customdata[self._ENTRYSTORENAME] = _EntryProxy2(self, team)

        # Now set the entry.
        self._entries[team.id].set_value(
            score=score,
            max_score=max_score,
            countdown=countdown,
            flash=flash,
            show_value=show_value,
        )

    def _add_team(self, team: bs.Team) -> None:
        if team.id in self._entries:
            raise RuntimeError('Duplicate team add')
        self._entries[team.id] = _Entry2(
            self,
            team,
            do_cover=self._do_cover,
            scale=self._scale,
            label=self._label,
            flash_length=self._flash_length,
        )
        self._update_teams()

    def remove_team(self, team_id: int) -> None:
        """Remove the team with the given id from the scoreboard."""
        del self._entries[team_id]
        self._update_teams()

    def _update_teams(self) -> None:
        pos = list(self._pos)
        for entry in list(self._entries.values()):
            entry.set_position(pos)
            pos[1] -= self._spacing * self._scale

class GlobalComboSystem:
    def __init__(self):
        self.active = False
        self.combo_count = 0
        self.combo_max_time = 15
        self.combo_time = self.combo_max_time
        self._combo_name_text = None
        self.last_threshold_passed = 0
        self.pos =  (400, 230)
        bs.timer(0.1, self._update_timer, repeat=True)
    
    def _create_ui(self):
        """Creates the combo UI elements."""

        self._combo_text = bs.newnode(
            'text',
            attrs={
                'text': 'Combo!',
                'scale': 1.0,
                'position': (self.pos[0], self.pos[1] + 25),  # Move to visible location
                'color': (1, 1, 1, 1),
                'h_align': 'left',
                'v_align': 'center',
                'shadow': 1.0,
            },
        )

        self._combo_num = bs.newnode(
            'text',
            attrs={
                'text': f'{self.combo_count}',
                'scale': 1.0,
                'position': (self.pos[0] - 10, self.pos[1] + 25),
                'color': (0, 0.7, 1, 1),
                'h_align': 'right',
                'v_align': 'center',
                'shadow': 1.0,
            },
        )
        
        
        self._combo_bar = bs.newnode(
            'image',
            attrs={
                'texture': bs.gettexture('bar'),
                'tint_color': (1, 0, 0),
                'opacity': 1.0,
                'absolute_scale': True,
                'position': self.pos,
                'scale': (200, 20),
            },
        )

    def start_combo(self):
        """Starts the combo mode and displays the UI."""
        if self.active:
            return  # Already active
        
        self.active = True
        self.combo_time = self.combo_max_time
        self.combo_count = 1
        self._combo_name_text = None
        self.last_threshold_passed = 0
        self._create_ui()
        self.update_ui()

    
    def update_ui(self):
        """Updates the UI text and bar width."""
        if self._combo_text and self._combo_bar:
            self._combo_num.text = f'{self.combo_count}'
            self._combo_bar.scale = (200 * (self.combo_time / self.combo_max_time), 20)
        combo_name = self.get_combo_name(self.combo_count)

        if self.combo_count > self.last_threshold_passed:
                next_threshold = self.get_next_threshold(self.combo_count)
                if next_threshold and self.combo_count <= next_threshold:
                    self._show_combo_name_text(combo_name)
                    self.last_threshold_passed = next_threshold

    def _update_timer(self):
        """Decreases the timer every second and updates the UI."""
        if not self.active:
            return
        
        self.combo_time -= 0.1
        self.update_ui()
        
        if self.combo_time <= 0:
            self.end_combo()
    
    def extend_combo_by_time(self, amount=2.0):
        """Extends the combo time."""
        if not self.active:
            return
        self.combo_time = min(self.combo_max_time, self.combo_time + amount)
        

        self.update_ui()

    def extend_combo(self, amount: float = 14.0):
        """Extends the combo time and increases count."""
        if not self.active:
            return
        self.combo_time = min(self.combo_max_time, self.combo_time + amount)
        self.combo_count += 1
        
        

        self.update_ui()

    def end_combo(self):
        """Ends the combo and hides UI."""
        self.active = False
        if self._combo_text:
            self._combo_text.delete()
        if self._combo_bar:
            self._combo_bar.delete()
        if self._combo_num:
            self._combo_num.delete()

        combo_name = self.get_combo_name(self.combo_count)
        self._end_combo_text(combo_name)

    def get_combo_color(self, combo_value):
        """Returns the combo name based on the combo value."""
        if combo_value < 5 or combo_value == 1 or combo_value == 0 or combo_value == 2 or combo_value == 3 or combo_value == 4 or combo_value == 5:
            return (1, 1, 1)
        elif combo_value < 10:
            return (0.8, 0.76, 0.57)
        elif combo_value < 15:
            return (0.5, 0.5, 0.5)
        elif combo_value < 20:
            return (0,1,0)
        elif combo_value < 25:
            return (0.98, 0.6, 0)
        elif combo_value < 30:
            return (0.97, 0.98, 0.78)
        elif combo_value < 35:
            return (0.93, 0.24, 0.13)
        elif combo_value < 40:
            return (1, 0, 0)
        elif combo_value < 45:
            return (0.36, 0.11, 0.07)
        elif combo_value < 50:
            return (0.1, 0.11, 0.1)
        elif combo_value < 55:
            return (0.88, 0.85, 0.58)
        elif combo_value < 60:
            return (1, 0, 0)
        elif combo_value < 65:
            return (0, 0, 0)
        elif combo_value < 70:
            return (0.73, 0.09, 0.02)
        elif combo_value < 75:
            return (0.89, 1, 0.94)
        elif combo_value < 80:
            return (0.04, 0.33, 0.45)
        elif combo_value < 160:
            return self.get_combo_color(combo_value % 80)
        else:
            return (1, 1, 1)

    def get_combo_name(self, combo_value):
        """Returns the combo name based on the combo value."""
        if combo_value < 5 or combo_value == 1 or combo_value == 0 or combo_value == 2 or combo_value == 3 or combo_value == 4 or combo_value == 5:
            return "Lame..."
        elif combo_value < 10:
            return "Cheesy"
        elif combo_value < 15:
            return "Not bad but\nnot great\neither"
        elif combo_value < 20:
            return "Getting\nsomewhere!"
        elif combo_value < 25:
            return "Nice, :)\nGood job"
        elif combo_value < 30:
            return "Cheflike"
        elif combo_value < 35:
            return "Brutal!"
        elif combo_value < 40:
            return "EVIL"
        elif combo_value < 45:
            return "UNCLEAN"
        elif combo_value < 50:
            return "disturbing"
        elif combo_value < 55:
            return "Twisted"
        elif combo_value < 60:
            return "PSYCHOTIC"
        elif combo_value < 65:
            return "ILL-WILLED"
        elif combo_value < 70:
            return "CRUSHING"
        elif combo_value < 75:
            return "Funny!"
        elif combo_value < 80:
            return "Unfunny"
        elif combo_value < 160:
            base_combo_name = self.get_combo_name(combo_value % 80)
            return f"Very {base_combo_name}"
        else:
            base_combo_name = self.get_combo_name(combo_value % 80)
            return f"Very {base_combo_name}"

    def _show_combo_name_text(self, combo_name):
        """Displays the special combo name text when the threshold is met."""

        # Ignore if its lame.
        if combo_name == 'Lame...':
            return
        pos = (self.pos[0], self.pos[1] - 30)  # Position the new text below the combo count text
        self._combo_name_text = bs.newnode(
            'text',
            attrs={
                'text': combo_name,
                'scale': 1.0,
                'position': (pos[0], pos[1]),
                'color': self.get_combo_color(self.combo_count),
                'h_align': 'center',
                'v_align': 'top',
                'shadow': 1.0,
            },
        )
        def delete():
            if self._combo_name_text:
                self._combo_name_text.delete()

        
        bs.timer(2, delete)
        # epic sound
        bs.getsound('comboup' + str(random.randint(1, 2))).play()

    
    def _end_combo_text(self, combo_name):
        """Displays the special combo name text when the threshold is met."""
        pos = (self.pos[0], self.pos[1] - 30)  # Position the new text below the combo count text
        self._combo_name_text_lose = bs.newnode(
            'text',
            attrs={
                'text': "That combo was\n" + combo_name,
                'scale': 1.0,
                'position': pos,
                'color': self.get_combo_color(self.combo_count),
                'h_align': 'center',
                'v_align': 'top',
                'shadow': 1.0,
            },
        )
        def delete():
            if self._combo_name_text_lose:
                self._combo_name_text_lose.delete()
        
        bs.timer(2, delete)
        # epic sound
        bs.getsound('Kashing').play()

    def get_next_threshold(self, combo_count):
        """Returns the next threshold to trigger the special combo name text."""
        thresholds = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        for threshold in thresholds:
            if combo_count < threshold:
                return threshold
        return max(thresholds)
    
class _Entry2:
    def __init__(
        self,
        scoreboard: Scoreboard,
        team: bs.Team,
        do_cover: bool,
        scale: float,
        label: bs.Lstr | None,
        flash_length: float,
    ):
        # pylint: disable=too-many-statements
        self._scoreboard = weakref.ref(scoreboard)
        self._do_cover = do_cover
        self._scale = scale
        self._flash_length = flash_length
        self._width = 32.0 * self._scale
        self._height = 300 * self._scale
        self._bar_width = 32.0 * self._scale
        self._bar_height = 2.0 * self._scale
        self._bar_tex = self._backing_tex = bs.gettexture('bar')
        self._cover_tex = bs.gettexture('uiAtlas')
        self._mesh = bs.getmesh('meterTransparent')
        self._pos: Sequence[float] | None = None
        self._flash_timer: bs.Timer | None = None
        self._flash_counter: int | None = None
        self._flash_colors: bool | None = None
        self._score: float | None = None

        safe_team_color = (1, 0, 0)

        # FIXME: Should not do things conditionally for vr-mode, as there may
        #  be non-vr clients connected which will also get these value.
        vrmode = bs.app.env.vr

        
        #self._backing_color = [0.05 + c * 0.5 for c in safe_team_color]
        self._backing_color = (0.2, 0.2, 0.2)

        opacity = (0.8 if vrmode else 0.8) if self._do_cover else 0.5
        self._backing = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'scale': (self._width, self._height),
                    'opacity': opacity,
                    'color': self._backing_color,
                    'vr_depth': -3,
                    'attach': 'topLeft',
                    'texture': self._backing_tex,
                },
            )
        )

        self._barcolor = safe_team_color
        self._bar = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'opacity': 0.7,
                    'color': self._barcolor,
                    'attach': 'topLeft',
                    'texture': self._bar_tex,
                },
            )
        )

        self._bar_scale = bs.newnode(
            'combine',
            owner=self._bar.node,
            attrs={
                'size': 2,
                'input0': self._bar_width,
                'input1': self._bar_height,
            },
        )
        assert self._bar.node
        self._bar_scale.connectattr('output', self._bar.node, 'scale')
        self._bar_position = bs.newnode(
            'combine',
            owner=self._bar.node,
            attrs={'size': 2, 'input0': 0, 'input1': 0},
        )
        self._bar_position.connectattr('output', self._bar.node, 'position')
        self._cover_color = safe_team_color
        if self._do_cover:
            self._cover = bs.NodeActor(
                bs.newnode(
                    'image',
                    attrs={
                        'scale': (self._width * 1.15, self._height * 1.6),
                        'opacity': 1.0,
                        'color': self._cover_color,
                        'vr_depth': 2,
                        'attach': 'topLeft',
                        'texture': self._cover_tex,
                        'mesh_transparent': self._mesh,
                    },
                )
            )

        clr = safe_team_color
        maxwidth = 130.0 * (1.0 - scoreboard.score_split)
        flatness = (1.0 if vrmode else 0.5) if self._do_cover else 1.0

        clr = safe_team_color

        team_name_label: str | bs.Lstr
        if label is not None:
            team_name_label = label
        else:
            team_name_label = team.name

            # We do our own clipping here; should probably try to tap into some
            # existing functionality.
            if isinstance(team_name_label, bs.Lstr):
                # Hmmm; if the team-name is a non-translatable value lets go
                # ahead and clip it otherwise we leave it as-is so
                # translation can occur..
                if team_name_label.is_flat_value():
                    val = team_name_label.evaluate()
                    if len(val) > 10:
                        team_name_label = bs.Lstr(value=val[:10] + '...')
            else:
                if len(team_name_label) > 10:
                    team_name_label = team_name_label[:10] + '...'
                team_name_label = bs.Lstr(value=team_name_label)

        flatness = (1.0 if vrmode else 0.5) if self._do_cover else 1.0
        self._name_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'h_attach': 'left',
                    'v_attach': 'top',
                    'h_align': 'left',
                    'v_align': 'center',
                    'vr_depth': 2,
                    'scale': self._scale * 0.9,
                    'shadow': 1.0 if vrmode else 0.5,
                    'flatness': flatness,
                    'maxwidth': 130 * scoreboard.score_split,
                    'text': team_name_label,
                    'color': clr + (1.0,),
                },
            )
        )

    def flash(self, countdown: bool, extra_flash: bool) -> None:
        pass

    def set_position(self, position: Sequence[float]) -> None:
        """Set the entry's position."""

        # Abort if we've been killed
        if not self._backing.node:
            return

        self._pos = tuple(position)
        self._backing.node.position = (
            position[0] + self._width / 2,
            position[1] - self._height / 2,
        )
        if self._do_cover:
            assert self._cover.node
            self._cover.node.position = (
                position[0] + self._width / 2,
                position[1] - self._height / 2,
            )
        self._bar_position.input0 = self._pos[0] + self._bar_width / 2
        self._bar_position.input1 = self._pos[1] - self._bar_height / 2
        assert self._name_text.node
        self._name_text.node.position = (
            self._pos[0] + 7.0 * self._scale,
            self._pos[1] - self._bar_height + 16.0 * self._scale,
        )

    def _set_flash_colors(self, flash: bool) -> None:
        pass

    def _do_flash(self) -> None:
        pass
        

    def set_value(
        self,
        score: float,
        max_score: float | None = None,
        countdown: bool = False,
        flash: bool = True,
        show_value: bool = True,
    ) -> None:
        """Set the value for the scoreboard entry."""

        # If we have no score yet, just set it.. otherwise compare
        # and see if we should flash.
        if self._score is None:
            self._score = score
        else:
            if score > self._score or (countdown and score < self._score):
                extra_flash = (
                    max_score is not None
                    and score >= max_score
                    and not countdown
                ) or (countdown and score == 0)
                if flash:
                    self.flash(countdown, extra_flash)
            self._score = score

        if bs.getactivity().dmg == 0:
            self._bar_height = 0.0
        else:
            self._bar_height = max(
                    2.0 * self._scale,
                    self._height * (min(1.0, float(score) / max_score)) * 99,
                )
        

        cur_width = self._bar_scale.input0
        bs.animate(
            self._bar_scale, 'input0', {0.0: cur_width, 0.25: self._bar_width}
        )
        self._bar_scale.input1 = self._bar_height
        cur_x = self._bar_position.input0
        assert self._pos is not None
        bs.animate(
            self._bar_position,
            'input0',
            {0.0: cur_x, 0.25: self._pos[0] + self._bar_width / 2},
        )
        self._bar_position.input1 = (self._pos[1] - 300)- (self._bar_height * -1) / 2

class _EntryProxy2:
    """Encapsulates adding/removing of a scoreboard Entry."""

    def __init__(self, scoreboard: Scoreboard, team: bs.Team):
        self._scoreboard = weakref.ref(scoreboard)

        # Have to store ID here instead of a weak-ref since the team will be
        # dead when we die and need to remove it.
        self._team_id = team.id

    def __del__(self) -> None:
        scoreboard = self._scoreboard()

        # Remove our team from the scoreboard if its still around.
        # (but deferred, in case we die in a sim step or something where
        # its illegal to modify nodes)
        if scoreboard is None:
            return

        try:
            bs.pushcall(bs.Call(scoreboard.remove_team, self._team_id))
        except bs.ContextError:
            # This happens if we fire after the activity expires.
            # In that case we don't need to do anything.
            pass