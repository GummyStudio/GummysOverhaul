"""Provides the coop game for The Tower."""
# please gummy PLEASE FIX THE FUCKING DOCSTRINGS OH MY GGROGORGJRHGHORHOGHOHUgr

# Yes this is a long one..
# pylint: disable=too-many-lines

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations
from bascenev1lib.game.tetris import TetrisBoard, AiTetrisPlayer


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
from bascenev1lib.actor.bomb import Blast, Fire
from bascenev1lib.actor.spazbot import (
    GarbageBotInvincible,
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
    RandomBot,
    ProRandomBot,
    ProRandomBotShielded,
    BouncyBot,
    IceBot,
    ProIceBot,
    ProIceBotShielded,
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
    RandomBotLite,
    Boss1,
    Boss2,
    Boss3,
    LandMine,
    B2BBot,
    ProB2BBot,
    ProB2BBotShielded,
    DumbassBot,
    GarbageBot1,
    GarbageBot2,
    GarbageBot3,
    GarbageBot4,
    TotemBot,
    TotemBotPro,
    TotemBotProShielded,
    GoldenBot,
    ProGoldenBot,
    ProGoldenBotShielded,
    BedBot,
    BedBotPro,
    BedBotProShielded,

)

if TYPE_CHECKING:
    from typing import Any, Sequence
    from bascenev1lib.actor.spazbot import SpazBot

from bascenev1lib.gameutils import SharedObjects

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


@dataclass
class Delay:
    """A delay between events in a wave."""

    duration: float


class Preset(Enum):
    """Game presets we support."""


    ENDLESS = 'endless'
    





class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.has_been_hurt = False
        self.respawn_wave = 0
        self.respawn_timer: bs.Timer | None = None
        self.respawn_icon: RespawnIcon | None = None
        self.board: TetrisBoard = None


class Team(bs.Team[Player]):
    """Our team type for this game."""

# This will be a long one.

# SNOWWW
class Snow(bs.Actor):
    def __init__(self):
        super().__init__()
        self.node = bs.newnode('prop', delegate=self, attrs={
            
            'mesh': bs.getmesh('shield'),
            'light_mesh': None,
            'mesh_scale': random.uniform(0.05, 0.1),
            'velocity': (0, 
                         -random.uniform(0.5, 1), 0),
            'color_texture': bs.gettexture('white'),
            'position': (random.uniform(-9, 9), 6, random.uniform(-9, 9)),
            'gravity_scale': 0.0,
            'shadow_size': 0.0, 
            'reflection': 'soft',
            'reflection_scale': [0.3],
            'body': 'landMine',
            'materials': [SharedObjects.get().never_collide_material],
        })
        bs.timer(0.1, self.check, repeat=True)

    def check(self):
        if not self.node:
            return

        # can you die???
        if self.node.position[1] < -1.5:
            self.node.delete()
    
    
    def handlemessage(self, msg):
        if isinstance(msg, bs.OutOfBoundsMessage): 
            self.handlemessage(bs.DieMessage())

        elif isinstance(msg, bs.DieMessage): 
            self.node.delete()
        
        else: return super().handlemessage(msg)
        return None
    
# This will be a long one.


class MovingProp(bs.Actor):
    def __init__(self, position, model, texture, size=1.0):
        super().__init__()
        self.node = bs.newnode('prop', 
                               delegate=self,
                               attrs={
            'mesh': bs.getmesh(model),
            'light_mesh': None,
            'mesh_scale': size,
            'color_texture': bs.gettexture(texture),
            'position': position,
            'gravity_scale': 0.0,
            'shadow_size': 0.0, 
            'reflection': 'soft',
            'reflection_scale': [0.1],
            'body': 'landMine',
            'materials': [SharedObjects.get().never_collide_material],
        })
        bs.timer(0.1, self.check, repeat=True)
        self.mult = random.uniform(0.8, 1.2)
        # background heeeheh

        # always slightly be moving down
        bs.timer(0.1, bs.Call(self.move_down, 0.5), repeat=True)

    def check(self):
        if not self.node:
            return

        # can you die???
        if self.node.position[1] < -1.5:
            self.node.delete()
        

    def move_down(self, amount):
        if self.node.exists():
            p = self.node.position
            bs.animate_array(self.node, 'position', 3, {
                0: p,
                1.0: (p[0], p[1] - (amount*self.mult), p[2])
                })
            
      
    
    def handlemessage(self, msg):
        if isinstance(msg, bs.OutOfBoundsMessage): 
            self.handlemessage(bs.DieMessage())

        elif isinstance(msg, bs.DieMessage): 
            self.node.delete()
        
        else: return super().handlemessage(msg)
        return None
    
    

class TowerBackgroundManager:
    def __init__(self, activity: TheTowerGame):
        self._activity = activity
        self.last_score = 0
        self.props: list[MovingProp] = []
        
        self._update_timer = bs.Timer(0.1, self._update, repeat=True)

    def _get_current_props(self):
        level = self._activity.towerlevel
        
        if level == 1:
            return [
                # Basic tree looking 
                ('aliTorso', 'null', random.uniform(1.4, 1.6)),
            ]
        elif level == 2 or level == 3:
            # Okay.. rocks?
            return [
                ('tnt', 'rock', random.uniform(1.0, 1.3)),
                ('tnt', 'rocky', random.uniform(1.0, 1.3))
             ]
        elif level == 4:
            # Library Objects
            return [
                ('tnt', 'cardboard', random.uniform(1.2, 1.6)),
             ]
        elif level == 5:
            # Fire
            return [
                ('spiritHead', 'bonesColorMask', random.uniform(2, 6)),
                ('hairTuft1', 'black', random.uniform(0.6, 0.8)),
                ('hairTuft1b', 'black', random.uniform(0.6, 0.8)),
                ('hairTuft2', 'black', random.uniform(0.6, 0.8)),
                ('hairTuft3', 'black', random.uniform(0.6, 0.8)),
             ]
        elif level == 6:
            # weird lookin things
            return [
                ('locator', 'field', random.uniform(1.0, 1.3)),
                ('flagPole', 'field', random.uniform(1.0, 1.3)),
             ]
        elif level == 7:
            # stars
            return [
                ('shield', 'white', random.uniform(0.1, 0.2),),
             ]
                
                
                
                
                
    
    def expire(self):
        self._activity = None
        self._update_timer = None
        for prop in self.props:
            prop.handlemessage(bs.DieMessage())

    def _update(self):
        current_score = self._activity._score
        
        score_delta = current_score - self.last_score
        
        if score_delta > 0:
        
            move_amount = score_delta
            
            self.props = [p for p in self.props if p.node.exists()]
            for prop in self.props:
                prop.move_down(move_amount)
                
            if random.random() > 0.18:
                self._spawn_prop()

        self.last_score = current_score

    def _spawn_prop(self):
        choices = self._get_current_props()
        x = random.uniform(-8, 8)

        info = random.choice(choices)
        
        new_prop = MovingProp(
            position=(x, 6, -13),
            model=info[0],
            texture=info[1],
            size=info[2]
                            )
        self.props.append(new_prop)

class TheTowerGame(bs.CoopGameActivity[Player, Team]):
    """Co-op game where players must advance floors
    by defeating bots and gaining score (altitude)."""

    name = 'The Tower'
    description = 'Climb the tower to win.'

    

    # Show messages when players die since it matters here.
    announce_player_deaths = True

    def __init__(self, settings: dict):
        self._preset = Preset.ENDLESS
        
        settings['map'] = 'The Tower'

        super().__init__(settings)

        self._new_wave_sound = bs.getsound('scoreHit01')
        self._winsound = bs.getsound('score')
        self.bleedinghearts = False
        
        self._cashregistersound = bs.getsound('cashRegister')
        self._a_player_has_been_hurt = False
        self._player_has_dropped_bomb = False

        # FIXME: should use standard map defs.
        
        self._spawn_center = (0, 3, -5)
        self._tntspawnpos = (0.0, 3.0, -5.0)
        self._powerup_center = (0, 5, -3.6)
        self._powerup_spread = (6.0, 4.0)
        self.reversed = False
        self.pizza_face_exists = False
        self.selecting = True

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
        self._boss_bots = SpazBotSet()
        self._garbage_bots = SpazBotSet()
        self._powerup_drop_timer: bs.Timer | None = None
        self._time_bonus_timer: bs.Timer | None = None
        self._time_bonus_text: bs.NodeActor | None = None
        self._flawless_bonus: int | None = None
        self._wave_text: bs.NodeActor | None = None
        self._wave_update_timer: bs.Timer | None = None
        self._throw_off_kills = 0
        self._land_mine_kills = 0
        self._tnt_kills = 0
        self.label: bs.Node = None
        self.floor_timer_nodes=[]
        self.boards: list[TetrisBoard] = []
        self.garbage_multiplier = 1.0
        self.last_tower  =1

        self.towerlevel = 1
        self.hyperspeed = False
        # use cards now
        #if babase.app.config.get('GUMMY_expertmode', False):
        #    self.expertmode = True
        #else:
        #    self.expertmode = False
        self.expertmode = False
       
        self.dmg = 0
        babase.app.config['GUMMY_ex'] = self.expertmode

       
        self.dmg_board = None
        self.max_dmg = 35
        self.currentdebuff = 0
        self.garbage_windingup=False
      
        
        self.floor_times: list[float] = [0.0] * 7
        self.cards: list[dict] = []

        # cards
        self.glasscanon = False
        self.permadeath = False
        self.gambler = False
        self.sgarbage = False
        self.lowgravity = False
        self.explosiveenemies = False
        self.timer_enabled = False
        self.fool = False
        self.snowballer = False
        self._total_kills = 0
        self.max_hp = 300
        self.tetris = False
        self.sharedhp = False

        # ok now reverse everything
        self.fool_reversed = False
        self.snowballer_reversed = False
        self.expertmode_reversed = False
        self.sgarbage_reversed = False
        self.glasscanon_reversed = False
        self.permadeath_reversed = False
        self.gambler_reversed = False
        self.lowgravity_reversed = False
        self.explosiveenemies_reversed = False
        self.uhh_reversed = False 
        self.timer_enabled_reversed = False # not done
        self.cloaked_enemies_reversed = False
        self.bleedinghearts = False
               




        self.bleedinghearts_damage_multiplier = 1.0

        self.timer_value = 60.0 
        self.timer_max = 180.0
        self.timer_node = None
        self.timer_deaths = 0
        self.old_score = 0
        self.bg_manager: TowerBackgroundManager = None
           
    


       

    def spawn_enemies_based_on_fill(self):
        """Spawn enemies based on self.dmg (board fill)."""

        if not self.expertmode:
            return

        garbage_bots = [
            GarbageBot1,
            GarbageBot2,
            GarbageBot3,
            GarbageBot4
        ]

        if True:
            if self.dmg >= 10:
                spawn_count = 10
            elif self.dmg >= 5:
                spawn_count = 5
            else:
                if not self.dmg == 0:
                    spawn_count = self.dmg if self.dmg >= 1 else 1
                else:
                    return

            if self.sgarbage_reversed:
                spawn_count = 3
                # Less frequent
            # We wont use self.remove_damage_to_board(damage=spawn_count)
            # Because it'll play a cool sfx and add score. (This is a punishment)
            self.dmg -= spawn_count
            self._update_scores()



            for _ in range(math.ceil(spawn_count)):
                angle = random.randrange(0, 360)
                self.add_bot_at_angle(angle, random.choice(garbage_bots) , 0, is_garbage=True)
    
    def towerparticalsfall(self) -> None:
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=3,
            spread=0.6,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1.7,
            spread=0.9,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=2.3,
            spread=0.9,
            chunk_type='rock',
            )
    def towerparticalsfallS(self) -> None:
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1.7,
            spread=0.9,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1,
            spread=0.9,
            chunk_type='rock',
            )
    
    def spawn_boss1(self):
        # no
        if self.tetris:
            return

        self.add_bot_at_angle(random.randrange(0, 360), Boss1, 0.2, True)
        bs.timer(12, self._bots.boss1_power, repeat=True)
        PopupText(
                    "Cyrpto-Boss Appears!",
            color=(1, 0.5, 0.5),
            scale=2.0,
            position=(0, 1, -1),
                        ).autoretain()


    def spawn_boss2(self):
        # no
        if self.tetris:
            return

        self.add_bot_at_angle(random.randrange(0, 360), Boss2, 0.2, True)
        bs.timer(9, self._bots.boss2_power, repeat=True)
        PopupText(
                   "The library lady woke up!",
            color=(1, 0, 0),
            scale=2.0,
            position=(0, 1, -1),
                        ).autoretain()
    
    def spawn_boss3(self):
        # no
        if self.tetris:
            return
        self.add_bot_at_angle(random.randrange(0, 360), Boss3, 0.2, True)
        bs.timer(10, self._bots.boss3_power, repeat=True)
        PopupText(
                    "The Guardian blocks your way.",
            color=(0.3, 0.9, 0.3),
            scale=2.0,
            position=(0, 1, -1),
                        ).autoretain()
        
    def debuff1(self):
        # no
        if self.tetris:
            return
        for player in self.players:
            if player.is_alive():
                player.actor._jump_cooldown *= 2
        self.currentdebuff = 1
        PopupText(
                    bs.Lstr(
                value='${A}...\n${B}',
                subs=[
                    ('${A}', 'Your Legs feel heavier.'),
                    ('${B}', 'Jump delay is multiplied by 2'),
                ],
            ),
            color=(1, 0.8, 0.8),
            scale=2,
            position=(0, 1, 0),
        ).autoretain()
        
    def debuff2(self):
        if not self.expertmode:
            return # uhh..... i didnt think about this one
        def spawn():
            
            self.garbage_windup(random.choice(['S', 'M', 'L']))
        
        bs.timer(25, spawn, repeat=True)
        self.currentdebuff = 2
        PopupText(
                    bs.Lstr(
                value='${A}...\n${B}',
                subs=[
                    ('${A}', 'Garbagle piles.'),
                    ('${B}', "Garbage Windups starts every 25 seconds."),
                ],
            ),
            color=(1, 0.8, 0.8),
            scale=2,
            position=(0, 1, 0),
        ).autoretain()
    def debuff3(self):
        for player in self.players:
            if player.is_alive():
                player.actor.impact_scale *= 1.2

        self.currentdebuff = 3
        PopupText(
                    bs.Lstr(
                value='${A}...\n${B}',
                subs=[
                    ('${A}', "Your Body grows weak."),
                    ('${B}', "Impact Scale multiplied by 1.2."),
                ],
            ),
            color=(1, 0.8, 0.8),
            scale=2,
            position=(0, 1, 0),
        ).autoretain()
    def debuff4(self):
        for player in self.players:
            if player.is_alive():
                player.actor.shield_decay_rate *= 2.5
        self.currentdebuff = 4
        PopupText(
                    bs.Lstr(
                value='${A}...\n${B}',
                subs=[
                    ('${A}', "Shields Weaken"),
                    ('${B}',  "Shield decay rate multiplied by 2.5."),
                ],
            ),
            color=(1, 0.8, 0.8),
            scale=2,
            position=(0, 1, 0),
        ).autoretain()
    def debuff5(self):
        def spawn():
            self.add_bot_at_angle(random.randrange(0, 360), BrawlerBotLite, 0.2)
            self.add_bot_at_angle(random.randrange(0, 360), BrawlerBotLite, 0.2)

            self.add_damage_to_board(damage=2)
        self.currentdebuff = 5
        PopupText(
                    bs.Lstr(
                value='${A}...\n${B}',
                subs=[
                    ('${A}', "They're running out of strategy."),
                    ('${B}', "2 BrawlerBotLites spawn every 30 seconds."),
                ],
            ),
            color=(1, 0.8, 0.8),
            scale=2,
            position=(0, 1, 0),
        ).autoretain()

        bs.timer(30, spawn, repeat=True)
    
    def create_floor_timers(self):


        colors = [
            (0.8, 0.8, 0.8),  
            (0.5, 0.5, 0.5),   
            (1, 1, 0.3),    
            (0, 0.6, 0), 
            (1, 0, 0),
            (0.424, 0.823, 0.61),
             (0, 0.5, 1)
        ]

        self.floor_timer_nodes = []

        for i in range(7):

            x = -300 + i * 100   # spreads across bottom So cooL!

            node = bs.newnode(
                'text',
                attrs={
                    'text': f'F{i+1}: 0.00',
                    'position': (x, 55),
                    'scale': 0.7,
                    'h_align': 'center',
                    'v_align': 'center',
                    'v_attach': 'bottom',
                    'color': colors[i],
                    'opacity': 0,
                }
            )

            self.floor_timer_nodes.append(node)
    def start_floor1_music(self):
                bs.setmusic(None)
                self.sfx= bs.Node(None)
                def set_music():
                    self.sfx.delete()
                    if self.globalsnode.music == '':
                        
                        if not self.hyperspeed:
                            if self.snowballer:
                        
                                bs.setmusic(bs.MusicType.FLOOR1_FESTIVE_EXPERT)
                                bs.animate_array(self.globalsnode, 'tint', 3, {   
                                    0: self.globalsnode.tint,
                                    0.5: (0.8, 0.8, 1),
                                } 
                                    )
                                
                            elif self.reversed:
                                bs.setmusic(bs.MusicType.BLEEDING)
                            elif self.expertmode:
                                bs.setmusic(bs.MusicType.EXPERT)
                            else:
                                bs.setmusic(bs.MusicType.FLOOR1)
                
                intro_sfx = [
                    {
                        'sound': bs.getsound('f1start1'),
                        'interval': 1.437
                    },
                    {
                        'sound': bs.getsound('f1start2'),
                        'interval': 1.323
                    },
                ]
                reversed_sfx = [
                    {
                        'sound': bs.getsound('f1exstart1'),
                        'interval': 1.636
                    },
                    {
                        'sound': bs.getsound('f1exstart2'),
                        'interval': 1.324
                    },
                ]
                
                
                selected = random.choice(reversed_sfx if self.expertmode or self.reversed else intro_sfx) 
                self.sfx = bs.newnode('sound', attrs={'sound': selected['sound'], 'music': True, 'volume': 105.0})
                #
                bs.timer(float(selected['interval']), set_music)

                


    def towercheck(self):

            
            
            
            
            if self._game_over or self.is_transitioning_out():
                return
            
             # uh idk where to put htis
            self.refresh_cards()
            for card in self.cards:
                if getattr(self, card['reversed_variable']):
                    for req, msg in card['reversed_requirements']:
                        if not req:
                            bs.getsound('error').play()

                            bs.broadcastmessage(
                                    f"{card['reversed']}'s rules were broken.\n{msg}",
                                    color=(1, 0, 0)
                            )
                            self.end_game()
                            return
                if getattr(self, card['variable']):
                    for req, msg in card['requirements']:
                        if not req:
                            bs.getsound('error').play()

                            bs.broadcastmessage(
                                    f"{card['name']}'s rules were broken.\n{msg}",
                                    color=(1, 0, 0)
                            )
                            self.end_game()
                            return
                
                    
            
            # we handle tetris a little differently (waves techincally dont exist)
            if not self.tetris:
                
                
            
                if (self._score > 250 or self._wavenum >= 5 and (not self._game_over )) and not self.alreadyfloor2d:
                    self.towerlevel = 2
                elif (self._score > 700 and (not self._game_over)) and not self.alreadyfloor3d:
                    self.towerlevel = 3
                    if not self.gambler_reversed:
                        bs.app.classic.ach.award_local_achievement('NightShift')
                elif (self._score > 1200 and (not self._game_over) and not self._boss_bots.have_living_bots()) and not self.alreadyfloor4d: # Theres was a boss a few waves back, make sure they're all dead before moving on the next.:
                    self.towerlevel = 4
                elif (self._score > 2100 and (not self._game_over)) and not self.alreadyfloor5d:
                    self.towerlevel = 5
                    if not self.gambler_reversed:
                        bs.app.classic.ach.award_local_achievement('HellsGate')
                elif (self._score > 3300 and (not self._game_over) and not self._boss_bots.have_living_bots()) and not self.alreadyfloor6d: # Theres was a boss a few waves back, make sure they're all dead before moving on the next.
                    self.towerlevel = 6
                elif (self._score > 3900 and self._wavenum >= 15 and (not self._game_over) and not self._boss_bots.have_living_bots()) and not self.alreadyfloor7d: # Kill that guy before moving on
                    self.towerlevel = 7
                    if not self.gambler_reversed:
                        bs.app.classic.ach.award_local_achievement('TowerofTheGods')
                    if self.expertmode or self.reversed:
                        if not self.gambler_reversed:
                            bs.app.classic.ach.award_local_achievement('TowerofTheGodsEX')
            else:
                if (self._score > 250) and not self.alreadyfloor2d and (not self._game_over):
                    self.towerlevel = 2
                elif (self._score > 700) and not self.alreadyfloor3d and (not self._game_over):
                    self.towerlevel = 3
                elif (self._score > 1200) and not self.alreadyfloor4d and (not self._game_over):
                    self.towerlevel = 4
                elif (self._score > 2100) and not self.alreadyfloor5d and (not self._game_over):
                    self.towerlevel = 5
                elif (self._score > 3300) and not self.alreadyfloor6d and (not self._game_over): 
                    self.towerlevel = 6
                elif (self._score > 3900) and not self.alreadyfloor7d and (not self._game_over): 
                    self.towerlevel = 7
            

        
            
            gnode = self.globalsnode
            # import bascenev1 as bs; bs.getactivity()._score  +=250
           
                
            if self.towerlevel == 1 and not self.alreadyfloor1d and (not self._game_over):
                self.alreadyfloor1d = True
                self.show_zoom_message(
                    "Floor of Beginners", scale=0.5, duration=2.0, color=(1, 0.8, 0.5)
                )
                self.start_floor1_music()
                bs.getsound('tower1').play()
                self.towerparticalsfall()
                bs.getsound('towermoveL').play()
                bs.camerashake(intensity = 1)
                self.label.text =  "Floor of Beginners"
                self.label.color =  (1.5, 1.3, 1)
                
            elif self.towerlevel == 2 and not self.alreadyfloor2d and (not self._game_over):
                self.alreadyfloor2d = True
                self.label.text = "The Cracked Walls"
                self.label.color = (0.8, 0.8, 0.8)
                self.show_zoom_message(
                    "The Cracked Walls", scale=0.5, duration=2.0, color=(0.8, 0.8, 0.8)
                )
                # too easy.
                if not self.tetris:
                    # First player alive gets the popup

                     bs.app.plus.xp_sys.award_xp(2, True, (0, 3, -1))
               
                gnode.tint = (0.8, 0.8, 0.8)
                if not self.hyperspeed:
                    bs.setmusic(bs.MusicType.FLOOR2)
                else:
                    if self.reversed:
                        bs.setmusic(bs.MusicType.OVERDRIVE, continuous=True)
                    else:
                        bs.setmusic(bs.MusicType.HYPERSPEED, continuous=True)
                bs.getsound('tower2').play()
                bs.getsound('towermoveL').play()
                bs.getsound('crank').play()
                
                bs.camerashake(intensity = 3)
                
                self.garbage_windup('S')
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(100)),
                    ('${B}',"The Cracked Walls"),
                ],
            ),
            color=(0.8, 0.8, 0.8),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self.towerparticalsfall()
                self._score += 100
                self._update_scores()
                self.spawn_boss1()
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[0] = elapsed
                self.floor_start_time = bs.time()
                def check_because_i_hate_my_life_and_this_is_so_unoptimized():
                    if self.hyperspeed:
                        

                        self.floor_timer_nodes[0].text = f'F1: {elapsed:.2f}'
                        for node in self.floor_timer_nodes:
                            bs.animate(node, 'opacity', {
                                0: 0,
                                3: 1
                            })
                            
                        bs.animate(self._time_text.node, 'opacity', {
                                0: 0,
                                3: 1
                            })
                bs.timer(1.1, check_because_i_hate_my_life_and_this_is_so_unoptimized)
                        
                
            elif self.towerlevel == 3 and not self.alreadyfloor3d and (not self._game_over):
                self.alreadyfloor3d = True
                self.show_zoom_message(
                    "Night Shift", scale=0.5, duration=2.0, color=(0.5, 0.5, 0.5)
                )
                self.label.text =  "Night Shift"
                self.label.color = (0.5, 0.5, 0.5)
                # too easy.
                if not self.tetris:
                    bs.app.plus.xp_sys.award_xp(3, True, (0, 3, -1))
                gnode.tint = (0.5, 0.5, 0.5)
                if not self.hyperspeed:
                    bs.setmusic(bs.MusicType.FLOOR3)
                else:
                    if self.reversed:
                        bs.setmusic(bs.MusicType.OVERDRIVE, continuous=True)
                    else:
                        bs.setmusic(bs.MusicType.HYPERSPEED, continuous=True)
                bs.getsound('tower3').play()
                bs.getsound('crank').play()
                bs.getsound('towermoveL').play()
                bs.camerashake(intensity = 3)
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(120)),
                    ('${B}', "Night Shift"),
                ],
            ),
            color=(0.5, 0.5, 0.5),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self._score += 120
                self._update_scores()
                self.towerparticalsfall()
                self.garbage_windup('S')
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[1] = elapsed
                self.floor_start_time = bs.time()

                if self.hyperspeed:
                    

                    self.floor_timer_nodes[1].text = f'F2: {elapsed:.2f}'
                # Spawn a moon!
                def spawn_moon():
                    prop =MovingProp(
                            position=(5, 6, -13),
                            model='shield',
                            texture='white',
                            size=0.8,
                    )
                    # We wanna move more slowly since we are technically in the sky
                    prop.mult = 0.7
                    self.bg_manager.props.append(prop)
                # give it a sec. we get points so we dont wanna instantly breeze through the moon
                bs.timer(0.5, spawn_moon)
                self.map.background.color_texture = bs.gettexture('black')
                    
                
            elif self.towerlevel == 4 and not self.alreadyfloor4d and (not self._game_over):
                self.alreadyfloor4d = True
                self.show_zoom_message(
                    "The Library", scale=0.5, duration=2.0, color=(1, 1, 1)
                )
                # too easy.
                if not self.tetris:
                    bs.app.plus.xp_sys.award_xp(7, True, (0, 3, -1))
                gnode.tint = (1.5, 1.5, 1.5)
                self.label.text = "The Library"
                self.label.color =(1.5, 1.5, 1.5)
                if not self.hyperspeed:
                    if self.reversed:    bs.setmusic(bs.MusicType.FLOOR4_BLEEDING)
                    else:
                        bs.setmusic(bs.MusicType.FLOOR4)
                else:
                    if self.reversed:
                        bs.setmusic(bs.MusicType.OVERDRIVE, continuous=True)
                    else:
                        bs.setmusic(bs.MusicType.HYPERSPEED, continuous=True)
                bs.getsound('tower4').play()
                bs.camerashake(intensity = 3)
                bs.getsound('crank').play()
                bs.getsound('towermoveL').play()
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(150)),
                    ('${B}', "The Library"),
                ],
            ),
            color=(1, 1, 1),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self._score += 150
                self._update_scores()
                self.towerparticalsfall()
                self.spawn_boss2()
                self.garbage_windup('M')
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[2] = elapsed
                self.floor_start_time = bs.time()
                if self.hyperspeed:
                    

                    self.floor_timer_nodes[2].text = f'F3: {elapsed:.2f}'
                self.map.background.color_texture = bs.gettexture('gray')
                    

                    
                
            elif self.towerlevel == 5 and not self.alreadyfloor5d and (not self._game_over):
                self.alreadyfloor5d = True
                self.show_zoom_message(
                    "Hells Gate", scale=0.5, duration=2.0, color=(1.3, 0, 0)
                )
                self.label.text = "Hells Gate"
                self.label.color =(2, 1, 1)
                # too easy.
                if not self.tetris:
                    bs.app.plus.xp_sys.award_xp(20, True, (0, 3, -1))
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(200)),
                    ('${B}', "Hells Gate"),
                ],
            ),
            color=(1.3, 0, 0, 1),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self.towerparticalsfall()
                gnode.tint = (2, 1, 1)
                self.add_damage_to_board(damage=20)
                if self.bleedinghearts and self.hyperspeed:
                    bs.setmusic(bs.MusicType.OVERDRIVE, continuous=True)
                else:
                    bs.setmusic(bs.MusicType.FLOOR5)

                bs.getsound('tower5').play()
                bs.camerashake(intensity = 3)
                bs.getsound('crank').play()
                bs.getsound('towermoveL').play()
                self.garbage_windup('L')
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[3] = elapsed
                self.floor_start_time = bs.time()
                if self.hyperspeed:
                   

                    self.floor_timer_nodes[3].text = f'F4: {elapsed:.2f}'
                self.map.background.color_texture = bs.gettexture('bonesColorMask')
                    
                    
            elif self.towerlevel == 6 and not self.alreadyfloor6d and (not self._game_over):
                self.alreadyfloor6d = True
                self.show_zoom_message(
                    "The Border", scale=0.5, duration=2.0, color=(0.424, 0.823, 0.61)
                )
                self.label.text = "The Border"
                self.label.color = (0.424, 0.823, 0.61)
                # too easy.
                if not self.tetris:
                    bs.app.plus.xp_sys.award_xp(112, True, (0, 3, -1))
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(220)),
                    ('${B}', "The Border"),
                ],
            ),
            color=(0.424, 0.823, 0.61),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self.towerparticalsfall()
                gnode.tint = (0.424, 0.823, 0.61)
                if self.bleedinghearts and self.hyperspeed:
                    bs.setmusic(bs.MusicType.OVERDRIVE, continuous=True)
                else:
                    bs.setmusic(bs.MusicType.FLOOR6)
                
                bs.getsound('tower5').play()
                self._score += 200
                self._update_scores()
                bs.camerashake(intensity = 3)
                bs.getsound('crank').play()
                bs.getsound('towermoveL').play()
                self._score += 220
                self._update_scores()
                self.garbage_windup('L')
                self.spawn_boss3()
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[4] = elapsed
                self.floor_start_time = bs.time()
                if self.hyperspeed:
                    

                    self.floor_timer_nodes[4].text = f'F5: {elapsed:.2f}'
                self.map.background.color_texture = bs.gettexture('doomShroomBGColor')
                    
            elif self.towerlevel == 7 and not self.alreadyfloor7d and (not self._game_over):
                self.alreadyfloor7d = True
                self.label.text = "Floor of The Gods"
                self.label.color = (0, 0.5, 1)
                self.show_zoom_message(
                    "Floor of The Gods", scale=0.5, duration=2.0, color=(0, 0.4, 1)
                )
                # too easy.
                if not self.tetris:
                    bs.app.plus.xp_sys.award_xp(500, True, (0, 3, -1))
                PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(300)),
                    ('${B}', "Floor of The Gods"),
                ],
            ),
            color=(0, 0.6, 1.1),
            scale=2.0,
            position=(0, 3, -1),
        ).autoretain()
                self.towerparticalsfall()
                gnode.tint = (0, 0.5, 1)
                bs.setmusic(bs.MusicType.FLOOR7)
                bs.getsound('tower5').play()
                self._score += 300
                bs.camerashake(intensity = 3)
                bs.getsound('crank').play()
                bs.getsound('towermoveL').play()
                self._update_scores()
                self.garbage_windup('L')
                bs.timer(5, lambda: self.garbage_windup('L'))
                elapsed = bs.time() - self.floor_start_time
                self.floor_times[5] = elapsed
                self.floor_start_time = bs.time()

                if self.hyperspeed:
                    

                    self.floor_timer_nodes[5].text = f'F6: {elapsed:.2f}'
                    
                    for node in self.floor_timer_nodes:
                        bs.animate(node, 'opacity', {
                            0: 1,
                            3: 0
                        })
                    bs.animate(self._time_text.node, 'opacity', {
                                0: 1,
                                3: 0
                            })
                self.map.background.color_texture = bs.gettexture('DSspace')
                # Spawn a moon!
                #bs.getactivity().towerlevel = 7
                def spawn_eartg():
                    prop =MovingProp(
                            position=(5, 6, -13),
                            model='earth',
                            texture='earthColor',
                            size=1.2,
                    )
                    # We wanna move more slowly since we are technically in the sky
                    prop.mult = 0.3
                    self.bg_manager.props.append(prop)
                # give it a sec. we get points so we dont wanna instantly breeze through the moon
                bs.timer(0.5, spawn_eartg)

    def towerstuff(self):
        """ the tower stuff, how it handles and such. """
        self.alreadyfloor1d = False
        self.alreadyfloor2d = False
        self.alreadyfloor3d = False
        self.alreadyfloor4d = False
        self.alreadyfloor5d = False
        self.alreadyfloor6d = False
        self.alreadyfloor7d = False
        self.alreadyhyperspeeded = False

        um = 0

        # setup our debuff timers.
        # Dont want this in tetris mode.
        if not self.tetris:
            bs.timer(72, self.debuff1)
            bs.timer(180, self.debuff2)
            bs.timer(258, self.debuff3)
            bs.timer(418, self.debuff4)
            bs.timer(520, self.debuff5)
        def hyperspeedcheck():
            def dohypertext():
                if not self.reversed:
                    self.show_zoom_message(
                        'HYPERSPEED!', scale=1.4, duration=2.5, color=(0, 0, 1), trail=True,
                    )
                    PopupText(
                        bs.Lstr(
                    value='+${A} ${B}',
                    subs=[
                        ('${A}', str(300)),
                        ('${B}', 'HYPERSPEED!'),
                    ],
                    ),
                    color=(0, 0, 1, 1),
                    scale=2.0,
                    position=(0, 3, 0),
                    ).autoretain()
                else:
                    self.show_zoom_message(
                        'OVERDRIVE!', scale=1.4, duration=2.5, color=(1, 0, 0), trail=True,
                    )
                    PopupText(
                        bs.Lstr(
                    value='+${A} ${B}',
                    subs=[
                        ('${A}', str(300)),
                        ('${B}', 'OVERDRIVE!'),
                    ],
                    ),
                    color=(1, 0, 0, 1),
                    scale=2.0,
                    position=(0, 3, 0),
                    ).autoretain()

                bs.camerashake(intensity = 2)
                self._score += 130
                bs.getsound('towermoveM').play()
                bs.getsound('crank').play()
                self.towerparticalsfallS()
                self._update_scores()
                
              
            if self.towerlevel == 2 and not self.alreadyhyperspeeded:
                self.hyperspeed = True
                self.create_floor_timers()
               

                bs.cameraflash(10)
                # too easy.
                if not self.tetris or not self.gambler_reversed:
                    bs.app.classic.ach.award_local_achievement('Hyperspeed')
                
                self.alreadyhyperspeeded = True
                if self.reversed:
                    bs.setmusic(bs.MusicType.OVERDRIVE)
                else:
                    bs.setmusic(bs.MusicType.HYPERSPEED)
                
                bs.timer(1.5, bs.Call(dohypertext))
                self.towerparticalsfallS()
                self._time_text = bs.NodeActor(
                    bs.newnode(
                        'text',
                        attrs={
                            'v_attach': 'bottom',
                            'h_attach': 'center',
                            'h_align': 'center',
                            'color': (0.5, 0.8, 1),
                            'flatness': 0.5,
                            'shadow': 0.5,
                            'position': (0, 0),
                            'scale': 1.3,
                            'text': '',
                            'opacity': 0,
                        },
                    )
                )
                self._time_text_input = bs.NodeActor(
                bs.newnode('timedisplay', attrs={'showsubseconds': True,})
                )
                self.globalsnode.connectattr(
                'time', self._time_text_input.node, 'time2'
                )   
                assert self._time_text_input.node
                assert self._time_text.node
                self._time_text_input.node.connectattr(
                'output', self._time_text.node, 'text'
                )
                
                
        # timer based stuff
        um = 1
        for i in range(45):
            bs.timer(um, bs.Call(hyperspeedcheck))
            um += 1
        
        bs.timer(0.8, bs.Call(self.towercheck), repeat=True)


    @override
    def on_transition_in(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        super().on_transition_in()
    
    def handle_tetris(self):
        p1 = self.players[0]
        if not p1.board.active:
            self.end_game()
            return
        
        delay_mapping = {
            1: 6.0, 
            2: 5.0, 
            3: 4.0, 
            4: 3.5, 
            5: 2.5, 
            6: 1.7, 
            7: 0.8
        }
        towerlevel = self.towerlevel
        if towerlevel != self.last_tower:
            # New, make way for better guys
            ai_boards = [b for b in self.boards if b != self.players[0].board]
            for board in ai_boards:
                if not board.active:

                    self.boards.remove(board)
        self.last_tower = self.towerlevel
        
        
        current_delay = delay_mapping.get(self.towerlevel, 1.0)
        
        for board in self.boards:
            board.garbage_delay = current_delay
            
        new_score = int(p1.board.score / 10)
    
        if new_score != self.old_score:
            self._score += new_score - self.old_score
            self.old_score = new_score
            self._update_scores()

        difficulty_map = {1: 1, 2: 1, 3: 2, 4: 3, 5: 3, 6: 4, 7: 5}
        diff = difficulty_map.get(self.towerlevel, 1)

        MAX_AI = 12
        current_ai_count = len([b for b in self.boards if b != p1.board])

        if current_ai_count < MAX_AI:
            if random.randint(0, 5) == 0: 
                self._spawn_ai(diff)


        
        self.delete_dead_ai()

    def _spawn_ai(self, diff):
        ai = AiTetrisPlayer(diff)
        ai.name = f'Goober{random.randint(1, 900000)}'
        
        ai.board.render = False
        ai.board.simple = True 
        
        self.boards.append(ai.board)

    def delete_dead_ai(self):
        # kill everoye whos dead
        ai_boards = [b for b in self.boards if b != self.players[0].board]
        for board in ai_boards:
            if not board.active:

                self.boards.remove(board)
        
    def _show_info(self) -> None:
        """Show the game description."""
        from bascenev1._gameutils import animate
        from bascenev1lib.actor.zoomtext import ZoomText

        name = self.get_instance_display_string()
        ZoomText(
            name,
            maxwidth=800,
            lifespan=2.5,
            jitter=2.0,
            position=(0, 180),
            flash=False,
            color=(0.93 * 1.25, 0.9 * 1.25, 1.0 * 1.25),
            trailcolor=(0.15, 0.05, 1.0, 0.0),
        ).autoretain()
        bs.timer(0.2, bs.getsound('gong').play)
        # _bascenev1.timer(
        #     0.2, Call(_bascenev1.playsound, _bascenev1.getsound('gong'))
        # )

        # The description can be either a string or a sequence with args
        # to swap in post-translation.
        desc_in = self.get_instance_description()
        desc_l: Sequence
        if isinstance(desc_in, str):
            desc_l = [desc_in]  # handle simple string case
        else:
            desc_l = desc_in
        if not isinstance(desc_l[0], str):
            raise TypeError('Invalid format for instance description')
        subs = []
        for i in range(len(desc_l) - 1):
            subs.append(('${ARG' + str(i + 1) + '}', str(desc_l[i + 1])))
        translation = babase.Lstr(
            translate=('gameDescriptions', desc_l[0]), subs=subs
        )

        # Do some standard filters (epic mode, etc).
        if self.settings_raw.get('Epic Mode', False):
            translation = babase.Lstr(
                resource='epicDescriptionFilterText',
                subs=[('${DESCRIPTION}', translation)],
            )
        active_mods = []
        reverse = False
        for card in self.cards:
            if getattr(self, card['reversed_variable']):
                # ignore
                if card['reversed_variable'] == 'placeholder':
                    continue
                active_mods.append(card['reversed'])
                reverse = True
        if not reverse:
            for card in self.cards:
                if getattr(self, card['variable']):
                    active_mods.append(card['name'])
            
        if active_mods:
            mod_text = "Modifiers: " + ", ".join(active_mods)
        else:
            mod_text = ""
        
     
        vrmode = babase.app.env.vr
        dnode = bs.newnode(
            'text',
            attrs={
                'v_attach': 'center',
                'h_attach': 'center',
                'h_align': 'center',
                'color': (1, 1, 1, 1),
                'shadow': 1.0 if vrmode else 0.5,
                'flatness': 1.0 if vrmode else 0.5,
                'vr_depth': -30,
                'position': (0, 80),
                'scale': 1.2,
                'maxwidth': 700,
                'text': translation.evaluate() + '\n' + mod_text.replace(',', '\n'),
            },
        )
        cnode = bs.newnode(
            'combine',
            owner=dnode,
            attrs={'input0': 1.0, 'input1': 1.0, 'input2': 1.0, 'size': 4},
        )
        cnode.connectattr('output', dnode, 'color')
        keys = {0.5: 0, 1.0: 1.0, 2.5: 1.0, 4.0: 0.0}
        animate(cnode, 'input3', keys)
        bs.timer(4.0, dnode.delete)


    def change_face_buttons(self):
        if not self.fool:
            return
        for player in self.players:
            if not player.actor.is_alive():
                continue
            face_buttons = [
                [bs.InputType.PUNCH_PRESS, bs.InputType.PUNCH_RELEASE],
                [bs.InputType.JUMP_PRESS, bs.InputType.JUMP_RELEASE],
                [bs.InputType.BOMB_PRESS, bs.InputType.BOMB_RELEASE],
                [bs.InputType.PICK_UP_PRESS, bs.InputType.PICK_UP_RELEASE],
            ]
            actions = [
                [player.actor.on_punch_press, player.actor.on_punch_release],
                [player.actor.on_jump_press, player.actor.on_jump_release],
                [player.actor.on_bomb_press, player.actor.on_bomb_release],
                [player.actor.on_pickup_press, player.actor.on_pickup_release],
            ]
            random.shuffle(actions)
            # Okay now assign them randomly
          
            for buttons, action_pair in zip(face_buttons, actions):
                player.assigninput(buttons[0], action_pair[0])
                player.assigninput(buttons[1], action_pair[1])

            # Reversed, so randomize input too
            if self.fool_reversed:
                input = [
                    bs.InputType.LEFT_RIGHT,bs.InputType.UP_DOWN,
                ]
                random.shuffle(input)  
                player.assigninput(input[0], player.actor.on_move_left_right)
                player.assigninput(input[1], player.actor.on_move_up_down)
                

                
            bs.getsound('cardFool').play()
            PopupText(
                        f"!!!",
                        color=(0, 1, 0, 1),
                        scale=1.5,
                        position=player.actor.node.position,
                    ).autoretain()
                

    def setup_active_mod_icons(self):
        
        active_textures = []
        for card in self.cards:
            # Check normal or reversed status
            if getattr(self, card['variable'], False) or getattr(self, card['reversed_variable'], False):
                # ignore
                if card['reversed_variable'] == 'placeholder':
                    continue
                is_reversed = getattr(self, card['reversed_variable'], False)
                active_textures.append({
                    'tex': card['icontexture'],
                    'reversed': is_reversed
                })

        count = len(active_textures)
        if count == 0:
            return

        # One? big
        # multiple ? amal
        if count == 1:
            icon_size = 90
            spacing = 0
            columns = 1
        else:
            icon_size = 70
            spacing = 45
            columns = 3 

        

        # Base corner position (Bottom Right)
        base_x = 550 
        base_y = -200

        for i, icon_data in enumerate(active_textures):
            icn_size = icon_size * (1.2 if icon_data['reversed'] else 1.0)
            row = i // columns
            col = i % columns
            
            pos_x = base_x - (col * spacing)
            pos_y = base_y + (row * spacing)
            
            node = bs.newnode('image', attrs={
                'texture': bs.gettexture(('evil' if icon_data['reversed'] else '' )+icon_data['tex']),
                'position': (pos_x, pos_y),
                'scale': (icn_size, icn_size),
                'opacity': 1.0,
                'color': (1, 1, 1),
            })
            
            bs.animate(node, 'opacity', {0: 0, 0.3: 1.0})

    def start(self): 
        from bascenev1._player import PlayerInfo

        # Refresh initial player list.
        self.initialplayerinfos = [
            PlayerInfo(name=p.getname(full=True), character=p.character)
            for p in self.players
        ]

        # Sort this by name so high score lists/etc will be consistent
        # regardless of player join order.
        self.initialplayerinfos.sort(key=lambda x: x.name)

        self.bg_manager = TowerBackgroundManager(self)  
        active_mods = []
        self.selecting = False
        bs.timer(0.001, self._show_scoreboard_info)
        bs.timer(1.0, self._show_info)
        bs.timer(2.5, self._show_tip)
        self.label = bs.newnode(
                'text',
                attrs={
                    'text': '',
                    'position': (0, -120),
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'color': (1, 1, 1),
                }
            ) 
        
        
        for player in self.players:
            player.actor.connect_controls_to_player()
            player.actor.node.is_area_of_interest = True
        self._spawn_info_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'position': (15, -130 * (1.4 if self.expertmode else 1)),
                    'h_attach': 'left',
                    'v_attach': 'top',
                    'scale': 0.55,
                    'color': (0.3, 0.8, 0.3, 1.0),
                    'text': '',
                },
            )
        )
       

        if len(self.players) == 1:
            bs.getsound('towerStart').play()
        else:
            bs.getsound('towerStartGroup').play()
      
        
        self._scoreboard = Scoreboard(
            score_split=0.5
        )
        self.pizza_tower =  babase.app.config.get("GUMMY_blockvanillaplayers", False)
        # Dont want this in tetris mode.
        if not self.tetris:
            if self.pizza_tower:
                self.combo_system = GlobalComboSystem( )
        if self.expertmode:
           
            self.garbage_team = Team()
            self.garbage_team.manual_init(9912931931923, 'Garbage', (1,0,0))
         
         # hhyper speed stuf
        self.floor_start_time = bs.time()
        self.starttime_ms = int(bs.time() * 1000.0)
        
        
       
        
    

        # We generate these on the fly in endless.
        
        self._have_tnt = True
        self._excluded_powerups = []
        self._waves = []

        # FIXME: Should migrate to use setup_standard_powerup_drops().

        # Spit out a few powerups and start dropping more shortly.
        # Dont want this in tetris mode.
        if not self.tetris:
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
            self._bots = SpazBotSet()
            bs.timer(4.0, self._start_updating_waves)
        self._update_scores()

        if self.expertmode or self.tetris:
            bs.timer(0.1, self.garbage_tick, repeat=True)
        bs.timer(3.5, self.towerstuff)
        bs.timer(0.1, self.update_floor_timer, repeat=True)

        # Ok! Give card stuff
        if self.glasscanon:
            for player in self.players:
                player.actor.impact_scale *= 5 if self.glasscanon_reversed else 2.5
                player.actor._punch_power_scale *= 5 if self.glasscanon_reversed else  1.5
        # eable low gravity
        if self.lowgravity:
            
            bs.timer(0.1, bs.Call(self.map.apply_low_gravity, -8 if self.lowgravity_reversed else 1), repeat=True)
        if self.fool:
            bs.timer(15, self.change_face_buttons, repeat=True)
        if self.snowballer:
            def spawn_snow():
                if self.towerlevel == 5:
                    # hot and scary
                    return
                Snow().autoretain()
            bs.timer(0.4, spawn_snow, repeat=True)
            for player in self.players:
                player.actor.hitpoints_max = self.max_hp
                player.actor.hitpoints = self.max_hp
        # Lazy asf today
        if getattr(self, 'cloaked_enemies', False):
            for player in self.players:
                player.actor.perma_cloak()
            # Exclude the cloak powerup.
            self._excluded_powerups.append('cloak')

        if self.timer_enabled:
            
            self.timer_node = bs.newnode(
                'text',
                attrs={
                    'text': '00:00',
                    'position': (0, -100),
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'color': (1, 1, 1),
                }
            ) 
            bs.timer(0.1, self._update_timer, repeat=True)
        
        # Okay time to set up
        if self.tetris:
            # Kill off actors
            for player in self.players:
                player.actor.handlemessage(bs.DieMessage(True))
                # Spawn in a tetris board.

                board =TetrisBoard(player, 10, 20) #AiTetrisPlayer(5).board#
                # Okay set this guy in the middle
                board.position = (60, -75)
                board.scale = 1.0
                board.garbage_entry_mode = 'continuous'
                board.garbage_entry_wait_time = 0.1

                player.board = board

                # Continouous to make it easier
                # Oookay lets handle some stuf!
                bs.timer(0.1, self.handle_tetris, repeat=True)

                self.boards.append(board)
        
        if self.snowballer_reversed:
            self.max_hp = 1
            for player in self.players:
                player.actor.hitpoints_max = self.max_hp
                player.actor.hitpoints = self.max_hp

        if self.cloaked_enemies_reversed:
            for player in self.players:
                player.actor.can_accept_powerups = False

        if self.sgarbage_reversed:
            i = 3
            for _ in range(25):
                bs.timer(i*_, bs.Call(self.add_damage_to_board, 1))
            self.garbage_windup('M')
            # and spawn invinciboyt
            self._garbage_bots.spawn_bot(GarbageBotInvincible, pos=self._spawn_center, spawn_time=5)
        

        # Argument sequence
        self.bleedinghearts_damage_multiplier = 1.0
        if self.bleedinghearts:
            
            
            names = [player.getname() for player in self.players]
            name1 = random.choice(names)
            names.remove(name1)
            try:
                name2 = random.choice(names)
            except:
                name2 = names[0]
                
            self.argument_sequence = [
                {
                    "time": 30,
                    "message": f"{name2} starts an argument.",
                    "effect_message": "Shared damage increases.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 1.5),
                    "color": (1,0,0)
                },
                {
                    "time": 60,
                    "message": f"{name2} apologizes.",
                    "effect_message": "damage is decreased.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 1),
                    "color": (1,1,1)
                },
                {
                    "time": 90,
                    "message": f"{name1} feels neglected...",
                    "effect_message": "Shared damage increases exponentionally.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 2.15),
                    "color": (1,0,0)
                },
                {
                    "time": 120,
                    "message": f"{name2} makes {name1} feel better.",
                    "effect_message": "Shared damage is below than normal.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 0.75),
                    "color": (0.4,1,.4)
                },
                {
                    "time": 150,
                    "message": f"You grow weak together.",
                    "effect_message": "Shared damage is below than normal.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 1.25),
                    "color": (1,0.2,0)
                },
                {
                    "time": 180,
                    "message": f"{name1} Doesnt want this anymore.",
                    "effect_message": "Shared damage is doubled.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 2),
                    "color": (1,0,0)
                },
                {
                    "time": 210,
                    "message": f"{name2} reaffirms.",
                    "effect_message": "Shared damage is finally normalized.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 1),
                    "color": (1,1,1)
                },
                {
                    "time": 240,
                    "message": f"{name1} and {name2} finally calm down.",
                    "effect_message": "Shared damage is now less than normal.",
                    "effect": bs.Call(setattr, self, 'bleedinghearts_damage_multiplier', 0.6),
                    "color": (0,1,0)
                },
            ]
            
            self.start_argument_sequence()
        self.setup_active_mod_icons()
        

            

    def start_argument_sequence(self):
      
        self._argument_running = True
        def show(msg, effmsg, color, effect):
            effect()
            PopupText(
                text=f'{msg}\n{effmsg}',
                position=(0,2,0),
                color=color,
                scale=2,
                lifespan=3
            ).autoretain()
            
        for event in self.argument_sequence:
            bs.timer(event['time'], 
                     bs.Call(
                         show,
                         event["message"],
                         event["effect_message"],
                         event["color"],
                         event["effect"],
                     )
                     )
            

    def _update_timer(self):
        # fuck youo mell bruh
        def _format_time(seconds: int) -> str:
                m = seconds // 60
                s = seconds % 60
                return f"{m:02d}:{s:02d}"
        if not self.timer_enabled or self._game_over:
            return
        
        self.timer_value = min(self.timer_max, self.timer_value)
        
        if self.timer_node:
            if self.timer_value <= 5:
                self.timer_node.color = (1, 0.2, 0.2)
                self.timer_node.scale = 1.4 + (0.2 * math.sin(bs.time() * 15))
            elif self.timer_value <= 15:
                self.timer_node.color = (1, 0.6, 0.2)
                self.timer_node.scale = 1.25
            else:
                
                self.timer_node.color = (1, 1, 1)
                self.timer_node.scale = 1.2

        self.timer_value -= 0.1
        if self.timer_value <= 0:
            self.timer_value = 0
            if self.timer_node:
                self.timer_node.text = '00:00'
            if not self._game_over:
                if not self.timer_enabled_reversed:
                    self.end_game()
                    bs.getsound('playerDeath').play()
                else:
                    if not self.pizza_face_exists:
                        self.pizza_face_exists = True
                        self.spawn_pizza_face()
                        self.timer_node.opacity = 0.0
            return
        

        if self.timer_node:
            self.timer_node.text = _format_time(max(0, int(self.timer_value)))

    def spawn_pizza_face(self):
        # im not putting the whole fucking code here fuck you
        from bascenev1lib.actor.pizzaface import PizzaFace
        self.pizzaface = PizzaFace()
       

        
    def update_floor_timer(self):
        if self._game_over:
            return 

        if self.floor_start_time is None:
            return

        floor_index = self.towerlevel - 1
        

        # make sure the timer exists
        if floor_index < 0 or floor_index >= len(self.floor_timer_nodes):
            return

        node = self.floor_timer_nodes[floor_index]

        if not node:
            return

        elapsed = bs.time() - self.floor_start_time
        if self.towerlevel == 7: node.text = f'F7: Nice :)'
        else:
            node.text = f'F{self.towerlevel}: {elapsed:.2f}'
            
    def garbage_windup(self, size: str = 'M'):
        #import bascenev1 as bs;bs.getactivity().garbage_windup('L')

        if size == 'S':
            count = 1
        elif size == 'M':
            count = 2
        elif size == 'L':
            count = 3
        else:
            print('idiot')
            return
        if self.expertmode or self.tetris:
            pass
        else:
            return
        if self.garbage_windingup:
            return
        self.garbage_windingup=True

        # bruh
        self.stringy = ''   

        bs.getsound('garbageWindup' + size).play(2.5)
        actor = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'bottom',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'vr_depth': -30,
                    'color': (1, 0, 0),
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'position': (0, -120 if self.tetris else 120),
                    'scale': 1.5,
                    'text': '',
                },
            )
        )
        def add_():
            self.stringy = '!' + self.stringy
            actor.node.text = f'<> {self.stringy} <>'
            actor.node.scale *= 1.3
            self.add_damage_to_board(1.5, True)

        def send():
            actor.node.delete()
            self.add_damage_to_board(4.6*count)
            self.garbage_windingup = False
           
            
        times = 0.27
        for i in range(count):
            bs.timer(times*i, add_)
        bs.timer((times*count)+(times*1.2), send)
     

    def refresh_cards(self):
        import datetime

        is_april = datetime.datetime.now().month == 4
        is_december = datetime.datetime.now().month == 12

        self.cards = []

        if is_april or bs.app.config.get("GUMMY_showevents", False):
            self.cards.append({
                'texture': 'thefoolcard',
                'name': 'The Fool',
                'selectsound': 'cardFool',
                'description': '<APRIL FOOLS EVENT>\nControls are changed every 15 seconds.',
                'variable': 'fool',
                'icontexture': 'fool',
                'requirements': [
                     # They arent normally together so like
                    (not self.snowballer, 'disable Snowballer'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],
                # Reversed, the evil version.  auto enables the regular variable when selected
                'reversed': 'A FOOL\'s ERRAND', 
                'reversed_description': '"You cannot run away from who you are."',
                'reversed_variable': 'fool_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': [] # eg 'expoert' or 'sgarbage', the reversed card will auto enable these
            })
        if is_december or bs.app.config.get("GUMMY_showevents", False):
            self.cards.append({
                'texture': 'snowballerCard',
                'name': 'Snowballer',
                'icontexture': 'snowballer',
                'selectsound': 'bell',
                'description': '<CHRISTMAS EVENT>\nStart with less HP than normal.\nYour MaxHP Increases for every 20 enemies you kill',
                'variable': 'snowballer',
                'requirements': [
                    (not self.timer_enabled, 'disable Timer'),
                    (self.sgarbage, 'enable Stronger Garbage'),
                    # They arent normally together so like
                    (not self.fool, 'disable The Fool'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'ABSOLUTE ZERO', 
                'reversed_description': '"Even in a storm, can you see the light?"',
                'reversed_variable': 'snowballer_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': ['expertmode', 'sgarbage']
            })

        self.cards.extend([
            {
                'texture': 'cardExpert',
                'name': 'Expert Mode',
                'selectsound': 'cardExpert',
                'icontexture': 'expert',
                'description': "Harder challenge. are you up for it?",
                'variable': 'expertmode',
                'requirements': [
                    (not self.tetris, 'disable Tetris mode.'),
                ],
                'reversed': 'TYRANNY', 
                'reversed_description': '"Fear, oppression and limitless ambition."',
                'reversed_variable': 'expertmode_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardStronger',
                'name': 'Stronger Garbage',
                'icontexture': 'stronger',
                'selectsound': 'card4',
                'description': 'Garbage is stronger than usual.',
                'variable': 'sgarbage',
                'requirements': [
                    (self.expertmode, 'enable Expert Mode.'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'DAMNATION', 
                'reversed_description': '"From the depths of hell, they seek revenge."',
                'reversed_variable': 'sgarbage_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': ['expertmode']
            },
            {
                'texture': 'cardGlass',
                'icontexture': 'glass',
                'name': 'Glass Cannon',
                'selectsound': 'card1',
                'description': "Stronger hits, at the cost of your health.",
                'variable': 'glasscanon',
                'requirements': [
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'GLASS HOUSE', 
                'reversed_description': '"Those in glass houses shouldn\'t throw stones."',
                'reversed_variable': 'glasscanon_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardPerma',
                'name': 'Perma-Death',
                'icontexture': 'permadeath',
                'selectsound': 'card2',
                'description': 'No respawning',
                'variable': 'permadeath',
                'requirements': [
                    (len(self.players) > 1, '2+ Players'),
                    (not self.timer_enabled, 'disable Timer'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'LINKED SOULS', 
                'reversed_description': '"Curse’d to be alike."',
                'reversed_variable': 'permadeath_reversed',
                'reversed_requirements': [
                     (len(self.players) > 1, '2+ Players'),
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardGambler',
                'name': 'Gambler',
                'icontexture': 'gambler',
                'selectsound': 'card3',
                'description': 'Gain double the score for killing enemies, or nothing.',
                'variable': 'gambler',
                'requirements': [
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'WHEEL OF FORTUNE', 
                'reversed_description': '"Fortune favors the bold, but fate punishes the greedy."',
                'reversed_variable': 'gambler_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardLowGravity',
                'name': 'Low Gravity',
                'selectsound': 'card5',
                'icontexture': 'lowgravity',
                'description': 'Gravity is reduced',
                'variable': 'lowgravity',
                'requirements': [
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'JUPITER', 
                'reversed_description': '"Discovering planets may have consequences."',
                'reversed_variable': 'lowgravity_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardEE',
                'name': 'Explosive Enemies',
                'selectsound': 'card6',
                'icontexture': 'explodingenemies',
                'description': 'Enemies explode on death!',
                'variable': 'explosiveenemies',
                'requirements': [
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'UPHEAVAL', 
                'reversed_description': '"A meltdown."',
                'reversed_variable': 'explosiveenemies_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardPrank',
                'name': 'P Rank Only',
                'icontexture': 'prank',
                'selectsound': 'card7',
                'description': 'Keep your combo, or explode lmao',
                'variable': 'uhh',
                'requirements': [
                    (babase.app.config.get("GUMMY_blockvanillaplayers", False), 'Enable the pizza tower in settings'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'T RANK ONLY', 
                'reversed_description': '"Mr (ant) Tenna’s TV TIME!"',
                'reversed_variable': 'uhh_reversed',
                'reversed_requirements': [
                    (babase.app.config.get("GUMMY_blockvanillaplayers", False), 'Enable the pizza tower in settings'),

                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'cardTimer',
                'name': 'Timer',
                'selectsound': 'card8',
                'icontexture': 'timed',
                'description': 'Adds a timer.',
                'variable': 'timer_enabled',
                'requirements': [
                    (not self.permadeath, 'disable Perma-Death.'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'LAP 3', 
                'reversed_description': '"THE DEATH THAT I DESERVIOLI"',
                'reversed_variable': 'timer_enabled_reversed',
                'reversed_requirements': [
                   (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'permainviscard',
                'name': 'Global Cloak',
                'icontexture': 'cloaked',
                'selectsound': 'card2',
                'description': 'Enemies and Allies are forever invisible.',
                'variable': 'cloaked_enemies',
                'requirements': [
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'THE HERMIT', 
                'reversed_description': '"Loneliness and isolation can, will, and has broken someone"',
                'reversed_variable': 'cloaked_enemies_reversed',
                'reversed_requirements': [
                    (True, '')
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'tetrioCard',
                'name': 'TETR.IO',
                'icontexture': 'tetrigrid',
                'selectsound': 'card2',
                'description': "Quick Play 2 Ahh..\nWARNING: Will spawn AI's so PLEASE have a good device\nBefore running this card.",
                'variable': 'tetris',
                'requirements': [
                    (len(self.players) == 1, '1 Player'),
                ],
                # Wont have a reversed mode.
                'reversed': '',
                'reversed_description': '',
                'reversed_variable': '',
                'reversed_requirements': [
                    (False, 'Doesnt have one'),
                ],
                'reversed_auto_turn_on': []
            },
            {
                'texture': 'bleeding_hearts',
                'name': 'Shared HP',
                'icontexture': 'sharedhp',
                'selectsound': 'card6',
                'description': "Share your health with others!",
                'variable': 'sharedhp',
                'requirements': [
                    (len(self.players) > 1, '2+ Players'),
                     (not self.tetris, 'disable Tetris mode.'),
                ],

                'reversed': 'BLEEDING HEARTS', 
                'reversed_description': '"Even as we bleed, we continue to hold hands."',
                'reversed_variable': 'bleedinghearts',
                'reversed_requirements': [
                    (len(self.players) > 1, '2+ Players'),
                ],
                'reversed_auto_turn_on': []
            },
            {
                # doesnt have a regular veersion
                'texture': 'cataclysmcard',
                'name': '',
                'icontexture': '',
                'selectsound': 'cardExpert',
                'description': "",
                'variable': 'placeholder',
                'requirements': [
                    (not self.selecting, 'Only the worthy can take a glance.')
                ],

                'reversed': 'CATACLYSM', 
                'reversed_description': '"Do you dare take the same steps as many others?"',
                'reversed_variable': 'placeholder',
                'reversed_requirements': [
                    (len(self.players) > 1, '2+ Players'),
                ],
                'reversed_auto_turn_on': [
                    'expertmode_reversed', 'expertmode', 
                    'sgarbage_reversed', 'sgarbage',
                    'glasscanon_reversed', 'glasscanon',
                    'permadeath_reversed', 'permadeath',
                    'lowgravity_reversed', 'lowgravity',
                    'explosiveenemies_reversed', 'explosiveenemies',
                    'cloaked_enemies_reversed', 'cloaked_enemies',
                    'sharedhp', 'bleedinghearts',
                ]
            }
        ])
        if not self.inited_cards:
                for card in self.cards:
                    setattr(self, card['variable'], False)
                    setattr(self, card['reversed_variable'], False)
                self.inited_cards=True
    @override
    def on_begin(self) -> None:
        super().on_begin(show_tips_n_stuff=False)
        # uhhhhh yeha
        self.teams[0].name = 'Altitude'

        gnode = self.globalsnode
        gnode.tint = (1.5, 1.3, 1)
        bs.setmusic(bs.MusicType.SPECTATE, continuous=True)
        
        # this is gonna be a DOOSSYY
        # lets get it

        # cards
        self.inited_cards = False

        self.refresh_cards()
        self.card_nodes = []
        self.card_texts = []
        modifier_order = [
            ('tetris', 'Original Quick Play 2 Experience'),
            ( 'sharedhp', 'Shared'),
             ('fool', 'Fooled'),
             ('snowballer', 'Snowballer'),
            ('timer_enabled', 'Timed'),
            ('cloaked_enemies', 'Cloaked'),
            ('uhh', 'P-Rank Only'),
            
            ('permadeath', 'Perma-Death'),
            ('gambler', 'Gambler'),
           

            
                
             
           
            ('glasscanon', 'Glass Cannon'),
             ('explosiveenemies', 'Explosive Enemies'),
           

           
            ('expertmode', 'Expert Mode'), 
            ('sgarbage', 'with stronger garbage'),
             ('lowgravity', 'in low gravity'),
           
        ]
        
        #They wanna skip, so.. okay.
        if babase.app.config.get("GUMMY_expertmode", False):
            self.start()
            return
        self._last_desc_node = None  # track last selected description!

        def update_modifiers_text():
            

            active = []

            for var, name in modifier_order:
                if getattr(self, var, False):
                    active.append(name)

            self.mini_mods_node.text = " ".join(active)
            if self.mini_mods_node.text == '':
                self.mini_mods_node.text = 'Normal Mode'
        # this is so cool such eye candy
        self._bh_nodes = []
        self._bh_time = 0
        self._bh_timer: bs.Timer = None
        self._bh_description= bs.Node(None)
        def remove_bleeding_hearts_logo():

    
            for node, _ in self._bh_nodes:
                if node.exists():
                    bs.animate(node, 'opacity', {0:1, 0.4:0})
                    bs.timer(0.4, node.delete)
            if self._bh_description.exists():
                 self._bh_description.delete()
            self._bh_nodes = []
        def spawn_bleeding_hearts_logo(name: str, description: str):
            # Im so tough

            text = name.upper()
            spacing = 35
            start_x = -spacing * (len(text)-1) / 2
            y = 220
            scale = 2
            self._bh_time = 0

            self._bh_description = bs.newnode(
                    'text',
                    attrs={
                        'text': description,
                        'position': (0, y-100),
                        'h_align': 'center',
                        'v_align': 'center',
                        'scale': scale*0.5,
                        'color': (1, 0.2, 0.2),
                        'shadow': 2
                    }
                )
            bs.animate(self._bh_description, 'opacity', {0:0, 0.4:1})

           
            for i, char in enumerate(text):

                node = bs.newnode(
                    'text',
                    attrs={
                        'text': char,
                        'position': (start_x + i*spacing, y),
                        'h_align': 'center',
                        'v_align': 'center',
                        'scale': scale,
                        'color': (1, 0.2, 0.2),
                        'shadow': 2,
                    }
                )
                bs.animate(node, 'opacity', {0:0, 0.4:1})

                self._bh_nodes.append((node, i))

                

                

                def animate():

                    if not self._bh_nodes:
                        return

                    self._bh_time += random.uniform(0.003, 0.03)

                    for node, i in self._bh_nodes:
                        if not node.exists():
                            continue

                        wave = math.sin(self._bh_time*3 + i*0.6)



                        node.position = (
                            node.position [0],
                            y + wave * 15
                        )

                        node.rotate = wave * 12

                self._bh_timer = bs.Timer(
                    0.03,
                    animate,
                    repeat=True
                )

        def requirements_met(card, use_reverse: bool = False):
            for req, msg in card['reversed_requirements' if use_reverse else 'requirements']:
                if not req:
                    return False, msg
            return True, ''

        def draw_card(card, i, start_x, spacing, selected):
            met, _ = requirements_met(card)
            active = getattr(self, card['variable'])

            if not met:
                color = tuple([0.5] * 3)
            elif active:
                color = (0, 1, 0)
            else:
                color = (1,1,1)

         

            node = bs.newnode(
                'image',
                attrs={
                    'texture': bs.gettexture(card['texture']),
                    'position': (start_x + i*spacing, 1.4 if selected else 1.2),
                    'scale': (160, 160) if selected else (120, 120),
                    'color': color
                }
            )
            self.card_nodes.append(node)
            if selected:
                bs.animate_array(node, 'scale', 2, {
                                    0: (120, 120),
                                    0.0823: (160, 160) ,
                                    
                                }
                                )

            if met:
                text_str = card['description']
                
          
            else:
                # show locked and all unmet requirements
                unmet_reqs = [msg for req, msg in card['requirements'] if not req and msg]
                text_str = "<LOCKED>"
                if unmet_reqs:
                    text_str += "\n" + ", ".join(unmet_reqs)
                # and deactivate their thing
                setattr(self, card['variable'], False)

            text_node = bs.newnode(
                'text',
                attrs={
                    'text': text_str,
                    'position': (start_x + i*spacing, -130),
                    'h_align': 'center',
                    'v_align': 'center',
                    'scale': 1.2,
                    'maxwidth': 150,
                    'color': (1, 1, 1) if met else (0.5, 0.5, 0.5),
                    'opacity': 1.0 if selected else 0.0
                }
            )
            self.card_texts.append(text_node)
            card = None
            return node if selected else None
        def animate_card_pop(node):
            if not node.exists():
                return
            bs.animate_array(node, 'scale', 2, {0: (110, 110), 0.1: (150,150), 0.2: (170,170)})
   
        def update_selection():
            self.refresh_cards()
            

            for node in self.card_nodes:
                node.delete()
            for text_node in self.card_texts:
                text_node.delete()

            self.card_nodes = []
            self.card_texts = []

            spacing = 75
            start_x = -spacing * (len(self.cards) - 1) / 2

            # draw all unselected cards first
            for i, card in enumerate(self.cards):
                if i == self.selected_index:
                    continue
                draw_card(card, i, start_x, spacing, selected=False)

            return draw_card(self.cards[self.selected_index], self.selected_index, start_x, spacing, selected=True)

        def fade_node(node, duration: int = 3):

            
            if node.exists():
                # if the node was already transparent, ignore it
                if node.opacity == 0:
                    return
                bs.animate(node, 'opacity',
                                  {
                    0:1,
                    duration:0

                    })

        def _left(player: Player):
            if self.reversed:
                return
            # i tried
            if self._last_desc_node is not None:
                fade_node(self._last_desc_node)

            self.selected_index = (self.selected_index - 1) % len(self.cards)
            update_selection()
            self._last_desc_node = self.card_texts[self.selected_index]
            bs.getsound('cardSwipe' + str(random.randint(1, 3))
            ).play()
            self.controler_node.text = f'{player.getname(True, True)} is controlling.'

        def _right(player: Player):
            if self.reversed:
                return
            if self._last_desc_node is not None:
                fade_node(self._last_desc_node)

            self.selected_index = (self.selected_index + 1) % len(self.cards)
            update_selection()
            self._last_desc_node = self.card_texts[self.selected_index]
            bs.getsound('cardSwipe' + str(random.randint(1, 3))
            ).play()
            self.controler_node.text = f'{player.getname(True, True)} is controlling.'

        def _select(player):
            if self.reversed:
                return
            card = self.cards[self.selected_index]
            current_value = getattr(self, card['variable'])
            self.controler_node.text = f'{player.getname(True, True)} is controlling.'
          
            

            if current_value:
                setattr(self, card['variable'], False)
              
                    
            else:
                met, msg = requirements_met(card)
                
                if met:
                    bs.getsound(card['selectsound']).play()
                    setattr(self, card['variable'], True)
                    
                        
                        
                    if card['variable'] == 'gambler':
                        bs.broadcastmessage('Gambler card disables leaderboards, rng isnt that fun.', color=(1,0,0))
                else:
                    bs.getsound('error').play()
            animate_card_pop(update_selection())
            update_modifiers_text()
            
            if card['variable'] == 'fool' and getattr(self, 'fool'): pass
            else: bs.getsound('cardSelect').play()
            


        def _start():
            self.start()
         
            # KILL THEM ALL!
            for node in self.card_nodes + self.card_texts:
                fade_node(node, duration=0.5)

            if self.controls_node.exists():
                fade_node(self.controls_node, duration=0.5)
            if self.controler_node.exists():
                fade_node(self.controler_node, duration=0.5)
            if self.cards_title.exists():
                fade_node(self.cards_title, duration=.5)
            if self.mini_mods_node.exists():
                fade_node( self.mini_mods_node, duration=0.5)
                
            remove_bleeding_hearts_logo()
            # Wow! Fuck you
            bs.timer(.5, self._bh_description.delete)
        
        def _reverse_card(player):
            bs.getsound('cardSelectEcho').play()
            if self.reversed:
                
                # cut it
                remove_bleeding_hearts_logo()
                
                for c in self.cards:
                    setattr(self, c['variable'], False)
                    setattr(self, c['reversed_variable'], False)
                update_modifiers_text()
                bs.setmusic(bs.MusicType.SPECTATE, continuous=True)
                self.mini_mods_node.opacity = 1.0

                bs.animate_array(self.globalsnode, 'vignette_outer', 3, {
                                    0: (1, 0.6, 0.6),
                                    1: (0.76, 0.76, 0.76),
                                    
                                }
                                )
                bs.animate_array(self.controls_node, 'color', 3, {
                                    0: (1, 0.6, 0.6),
                                    1:(1, 1, 1),
                                
                                }
                                )
                bs.animate_array(self.cards_title , 'position', 2, {
                            0: (0, 220),
                            1: (0, 130),
                           
                        })
                self.controls_node.text = (f"{babase.charstr(babase.SpecialChar.LEFT_ARROW)} {babase.charstr(babase.SpecialChar.LEFT_BUTTON)} {babase.charstr(babase.SpecialChar.RIGHT_ARROW)}"
                                f" Start: {babase.charstr(babase.SpecialChar.BOTTOM_BUTTON)}\nPress {babase.charstr(babase.SpecialChar.TOP_BUTTON)} for a new challenge...")
                update_selection()
                self.reversed = False
                return
            
            self.controler_node.text = f'{player.getname(True, True)} is controlling.'
            selected_node = update_selection()
            animate_card_pop(selected_node)
           
            card = self.cards[self.selected_index]
            met, msg = requirements_met(card, True)
            
            if not met:
                bs.getsound('error').play()
                return
            
            self.controls_node.text = (f"{babase.charstr(babase.SpecialChar.BACK)} !?! {babase.charstr(babase.SpecialChar.BACK)}"
            f" START: {babase.charstr(babase.SpecialChar.BOTTOM_BUTTON)}\nYou wanted this.")
            if card['variable'] == 'fool': bs.getsound(card['selectsound']).play(2)
            else: bs.getsound(card['selectsound']+'evil').play(2)
            bs.setmusic(bs.MusicType.YOURECOOKEDBRO)
            spawn_bleeding_hearts_logo(
                card['reversed'],
                card['reversed_description']
            )
            if card['reversed'] == 'WHEEL OF FORTUNE':
                bs.broadcastmessage('Gambler card disables leaderboards, rng isnt that fun.', color=(1,0,0))
            
            bs.getsound('cardSelectEcho').play()
            bs.animate_array(self.globalsnode, 'vignette_outer', 3, {
                            0:(0.76, 0.76, 0.76),
                            0.5: (1, 0.6, 0.6),
                        }
                        )
                        
            bs.animate_array(self.controls_node, 'color', 3, {
                            0:(1, 1, 1),
                            0.5: (1, 0.6, 0.6),
            }
            )
            bs.animate_array(self.cards_title , 'position', 2, {
                            0: (0, 130),
                            0.1: (0, 129),
                            0.6: (0, 220)
            })

            # kill
            for c in self.cards:
                setattr(self, c['variable'], False)
                setattr(self, c['reversed_variable'], False)

            # dont kill
            setattr(self, card['variable'], True)
            setattr(self, card['reversed_variable'], True)
            target_pos = (0, -40)
            for auto_var in card.get('reversed_auto_turn_on', []):
                setattr(self, auto_var, True)

            for card_text in self.card_texts:
                card_text.delete()

            fade_node( self.mini_mods_node, duration=0.5)

            for node in self.card_nodes:
                if node != selected_node:
                    fade_node(node, duration=0.5)


            if card['reversed'] == 'CATACLYSM':
                for node in self.card_nodes:
                    fade_node(node, duration=0.5)
               

            
                affected_vars = set(card.get('reversed_auto_turn_on', []))
                affected_cards = [c for c in self.cards if c['variable'] in affected_vars]

                num_cards = len(affected_cards)
                fan_arc_degrees = 100
                fan_center_y_offset = -280
                fan_center_x_offset = 0
                fan_radius = 300
                
                

                for i, aff_card in enumerate(affected_cards):
                    norm_i = (i / (num_cards - 1.0)) * 2.0 - 1.0
                    

                    angle_deg = norm_i * (fan_arc_degrees / 2.0)
                    angle_rad = math.radians(angle_deg)

                
                    target_x = fan_center_x_offset + fan_radius * math.sin(angle_rad)
                    target_y = fan_center_y_offset + fan_radius * math.cos(angle_rad)
                    # Ok lets find this cards node
                    
                    mod_node = bs.newnode('image', attrs={
                        'texture': bs.gettexture(aff_card['texture']),
                        'position': self.card_nodes[self.cards.index(aff_card)].position, 
                        'scale': (110, 110),
                        'color': (1.5, 0.5, 0.5), 
                    })
                    # list
                    self.card_nodes.append(mod_node)
                    def animate(node, pos, angle):
                        # took me 2 hours fuck yeah
                        duration = 3.5 
                        steps = 50 # sm oo th
                        
                        pos_keys = {}
                        rot_keys = {}

                        for i in range(steps + 1):
                            t = i / steps
                            time_point = t * duration
                            

                            curr_x = pos[0] + 8 * math.sin(2 * math.pi * t)
                            curr_y = pos[1] - 5 + 5 * math.cos(2 * math.pi * t)
                            
                            curr_angle = angle + 3 * math.sin(2 * math.pi * t)

                            pos_keys[time_point] = (curr_x, curr_y)
                            rot_keys[time_point] = curr_angle

                        bs.animate_array(node, 'position', 2, pos_keys, loop=True)
                        bs.animate(node, 'rotate', rot_keys, loop=True)

                    bs.animate_array(mod_node, 'position', 2, {
                        0.0: (mod_node.position),
                        0.1: (mod_node.position[0], mod_node.position[1] +50),
                        0.35: (target_x, target_y)
                    })
                    scl = mod_node.scale
                    bs.animate_array(mod_node, 'scale', 2, {
                        0.0: (scl[0], scl[1]),
                        0.25: (scl[0]*4.0, scl[1]*4.0),
                        0.35: (scl[0]*1.3, scl[1]*1.3)
                    })
                    bs.animate(mod_node, 'rotate', {
                        0.1: 0,
                        0.35: -angle_deg + 180
                    })
                    bs.timer(0.35+(0.1*i), bs.Call(animate, mod_node, (target_x, target_y), (-angle_deg + 180)))
                    bs.timer(0.35, bs.Call(bs.getsound('cardBH2').play, 2.5))
                    

                
            else:
                
                # animate
                if selected_node.exists():
                    
                    bs.animate_array(selected_node, 'position', 2, {
                        0: selected_node.position,
                        0.122: (selected_node.position[0], 5), 
                        0.13: (selected_node.position[0]+15, 5.6), 
                        0.3: target_pos
                    })
                    scl = selected_node.scale
                    bs.animate_array(selected_node, 'scale', 2, {
                        0: scl,
                        0.1231: (scl[0]*3.5, scl[1]*2.5), 
                        0.21: (scl[0]*4, scl[1]*4), 
                        0.3:  (scl[0]*2, scl[1]*2), 
                    })
                    bs.animate_array(selected_node, 'color', 3, {
                        0: (1, 1, 1),
                        0.2: (1, 0.6, 0.6),
                    })
                    def anim():
                        if not selected_node.exists():
                            return
                    
                        bs.animate_array(selected_node, 'position', 2, {
                            0.0: target_pos,
                            1.5: (target_pos[0] + 0.4, target_pos[1] + 0.6),
                            3.0: target_pos,
                            4.5: (target_pos[0] - 0.3, target_pos[1] - 0.5), 
                            6.0: target_pos,
                        }, loop=True)

                    
                        bs.animate(selected_node, 'rotate', {
                            0.0: 180,
                            1.5: 181,
                            3.0: 179,
                            6.0: 180,
                        }, loop=True)
                    bs.animate(selected_node, 'rotate', {
                        0: 0,
                        0.25: 80,
                        0.3: 180
                    })
                    bs.timer(0.35, bs.Call(bs.getsound('cardBH2').play, 2.5))
                    bs.timer(0.35, anim)


                                        
                
                
               
                

            

            bs.animate_array(self.globalsnode, 'vignette_outer', 3, {
                0: self.globalsnode.vignette_outer,
                1.0: (1, 0.2, 0.2)
            })
            # ok aura farm
            self.reversed = True
       
                

        for player in self.players:
            player.actor.disconnect_controls_from_player()
            player.actor.node.is_area_of_interest = False
            player.assigninput(bs.InputType.LEFT_PRESS, lambda player=player: _left(player))
            player.assigninput(bs.InputType.RIGHT_PRESS, lambda player=player: _right(player))
            player.assigninput(bs.InputType.PUNCH_PRESS, lambda player=player: _select(player))
            player.assigninput(bs.InputType.PICK_UP_PRESS, lambda player=player: _reverse_card(player))
            player.assigninput(bs.InputType.JUMP_PRESS, _start)

        self.selected_index = 0
        update_selection()
        self._last_desc_node = self.card_texts[self.selected_index]
        self.controls_node = bs.newnode(
            'text',
            attrs={
                'text':  (f"{babase.charstr(babase.SpecialChar.LEFT_ARROW)} {babase.charstr(babase.SpecialChar.LEFT_BUTTON)} {babase.charstr(babase.SpecialChar.RIGHT_ARROW)}"
                                f" Start: {babase.charstr(babase.SpecialChar.BOTTOM_BUTTON)}\nPress {babase.charstr(babase.SpecialChar.TOP_BUTTON)} for a new challenge..."),
            
                'position': (0, -300),
                'h_align': 'center',
                'v_align': 'center',
                'color': (1, 1, 0),
                'scale': 1.2
            }
        )
        self.controler_node = bs.newnode(
            'text',
            attrs={
                'text': f"{self.players[0].getname(True, True)} is controlling.",
            
                'position': (0, -240),
                'h_align': 'center',
                'v_align': 'center',
                'color': (1, 1, 1),
                'scale': 0.6
            }
        )
        self.cards_title = bs.newnode(
            'text',
            attrs={
                'text': f"the tower:",
    
                'position': (0, 130),
                'h_align': 'center',
                'v_align': 'center',
                'color': (1, 1, 1),
                'scale': 0.6,
                'big': True
            }
        )
        self.mini_mods_node = bs.newnode(
            'text',
            attrs={
                'text': 'Normal Mode',
                'position': (0, 150),
                'h_align': 'center',
                'v_align': 'center',
                'color': (0.8, 0.8, 0.8),
                'scale':  0.6
            }
        )
    def on_expire(self):
        super().on_expire()
        if self.bg_manager:
            self.bg_manager.expire()
        self.bg_manager = None
        self.card_nodes = []
        self.card_texts = []
        self._bh_nodes = []
        self._bh_timer  = None
        self.argument_sequence =[]
        self.boards = []
     
    def on_player_leave(self, player):
        super().on_player_leave(player)
        self._checkroundover()
     

        
    def add_damage_to_board(self, damage: int = 1, instant: bool = False):
        # kek, evil
        if self.sgarbage_reversed:
                damage = int(damage*2)
        #bs.getactivity().add_damage_to_board(2)
        # Were in tetris mode, its different
        if not self.tetris:
            if not self.expertmode:
                return
            
            if self._game_over:
                return
            
            def add_():
                self.dmg += damage
                self._update_scores()

                if damage <= 5:
                    bs.getsound('boardfillS').play()
                elif damage <= 10:
                    bs.getsound('boardfillM').play()
                else:
                    bs.getsound('boardfillL').play()
            if instant:
                add_()
            else:
                if damage <= 5:
                    bs.getsound('spikeS').play(1.5)
                elif damage <= 10:
                    bs.getsound('spikeM').play(1.5)
                else:
                    bs.getsound('spikeL').play(1.5)
                # add on a delay
                bs.timer(0.2, add_)
        else:
            if self.players[0].board:
                self.players[0].board.queue_garbage(int(damage*0.35))

        
    
    def remove_damage_to_board(self, damage: int = 1):
        if not self.expertmode:
            return
        
        # Dont play the sfx if the board was already at 0 or below.
        no = False
        if self.dmg <= 0:
            no = True
        self.dmg -= damage
        self._update_scores()
        if self.dmg <= 0 and not no:
            bs.getsound('boardClear').play(0.4)
            # and add some scooore!
            bs.getsound('crank').play()
            self._score += 25
            self._update_scores()
            PopupText(
                    bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(25)),
                    ('${B}', 'Board Clear!'),
                ],
                ),
                color=(0, 1, 1, 1),
                scale=1.0,
                position=(0, 3, 0),
                ).autoretain()

    def garbage_tick(self):

        if self.expertmode_reversed:
            self._score = max(0, self._score-0.1)
            self._update_scores()
       

        if self.expertmode:

            if random.random() <= 0.0032:
                if random.random() <= 0.8:
                    self.add_damage_to_board(damage=2)
                if random.random() <= 0.5:
                    self.add_damage_to_board(damage=4)
                if random.random() <= 0.3:
                    self.add_damage_to_board(damage=6)
                if random.random() <= 0.2:
                    self.add_damage_to_board(damage=9)
                if random.random() <= 0.01:
                    self.add_damage_to_board(damage=13)
                else:
                    self.add_damage_to_board(damage=1)
                if random.random() <= 0.008:
                    self.spawn_enemies_based_on_fill()
            if self.dmg <= -1:
                self.dmg = 0
            self.old_dmg = self.dmg
            

    def _get_dist_grp_totals(self, grps: list[Any]) -> tuple[int, int]:
        totalpts = 0
        totaldudes = 0
        for grp in grps:
            for grpentry in grp:
                dudes = grpentry[1]
                totalpts += grpentry[0] * dudes
                totaldudes += dudes
        return totalpts, totaldudes

    def _get_distribution(
        self,
        target_points: int,
        min_dudes: int,
        max_dudes: int,
        group_count: int,
        max_level: int,
    ) -> list[list[tuple[int, int]]]:
        """Calculate a distribution of bad guys given some params."""
        # pylint: disable=too-many-positional-arguments
        max_iterations = 10 + max_dudes * 2

        groups: list[list[tuple[int, int]]] = []
        for _g in range(group_count):
            groups.append([])
        types = [1]
        if max_level > 1:
            types.append(2)
        if max_level > 2:
            types.append(3)
        if max_level > 3:
            types.append(4)
        for iteration in range(max_iterations):
            diff = self._add_dist_entry_if_possible(
                groups, max_dudes, target_points, types
            )

            total_points, total_dudes = self._get_dist_grp_totals(groups)
            full = total_points >= target_points

            if full:
                # Every so often, delete a random entry just to
                # shake up our distribution.
                if random.random() < 0.2 and iteration != max_iterations - 1:
                    self._delete_random_dist_entry(groups)

                # If we don't have enough dudes, kill the group with
                # the biggest point value.
                elif (
                    total_dudes < min_dudes and iteration != max_iterations - 1
                ):
                    self._delete_biggest_dist_entry(groups)

                # If we've got too many dudes, kill the group with the
                # smallest point value.
                elif (
                    total_dudes > max_dudes and iteration != max_iterations - 1
                ):
                    self._delete_smallest_dist_entry(groups)

                # Close enough.. we're done.
                else:
                    if diff == 0:
                        break

        return groups

    def _add_dist_entry_if_possible(
        self,
        groups: list[list[tuple[int, int]]],
        max_dudes: int,
        target_points: int,
        types: list[int],
    ) -> int:
        # See how much we're off our target by.
        total_points, total_dudes = self._get_dist_grp_totals(groups)
        diff = target_points - total_points
        dudes_diff = max_dudes - total_dudes

        # Add an entry if one will fit.
        value = types[random.randrange(len(types))]
        group = groups[random.randrange(len(groups))]
        if not group:
            max_count = random.randint(1, 6)
        else:
            max_count = 2 * random.randint(1, 3)
        max_count = min(max_count, dudes_diff)
        count = min(max_count, diff // value)
        if count > 0:
            group.append((value, count))
            total_points += value * count
            total_dudes += count
            diff = target_points - total_points
        return diff

    def _delete_smallest_dist_entry(
        self, groups: list[list[tuple[int, int]]]
    ) -> None:
        smallest_value = 9999
        smallest_entry = None
        smallest_entry_group = None
        for group in groups:
            for entry in group:
                if entry[0] < smallest_value or smallest_entry is None:
                    smallest_value = entry[0]
                    smallest_entry = entry
                    smallest_entry_group = group
        assert smallest_entry is not None
        assert smallest_entry_group is not None
        smallest_entry_group.remove(smallest_entry)

    def _delete_biggest_dist_entry(
        self, groups: list[list[tuple[int, int]]]
    ) -> None:
        biggest_value = 9999
        biggest_entry = None
        biggest_entry_group = None
        for group in groups:
            for entry in group:
                if entry[0] > biggest_value or biggest_entry is None:
                    biggest_value = entry[0]
                    biggest_entry = entry
                    biggest_entry_group = group
        if biggest_entry is not None:
            assert biggest_entry_group is not None
            biggest_entry_group.remove(biggest_entry)

    def _delete_random_dist_entry(
        self, groups: list[list[tuple[int, int]]]
    ) -> None:
        entry_count = 0
        for group in groups:
            for _ in group:
                entry_count += 1
        if entry_count > 1:
            del_entry = random.randrange(entry_count)
            entry_count = 0
            for group in groups:
                for entry in group:
                    if entry_count == del_entry:
                        group.remove(entry)
                        break
                    entry_count += 1


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
        spaz.can_accept_powerups = not self.cloaked_enemies_reversed
        spaz.impact_scale = 0.695
        if self.expertmode:
            spaz.impact_scale = 1.0
            spaz.shield_hitpoints_max = 300
            spaz._jump_cooldown = 500
            spaz._pickup_cooldown = 50
        else:
            self.currentdebuff = None
        if self.currentdebuff == 1:
            spaz._jump_cooldown *= 2
        if self.currentdebuff == 3:
            spaz.impact_scale *= 1.2
        if self.currentdebuff == 4:
            spaz.shield_decay_rate *= 2.5
        

        # Ok! Give card stuff
        if self.glasscanon:
            spaz.impact_scale *= 5 if self.glasscanon_reversed else 2.5
            spaz._punch_power_scale *= 5 if self.glasscanon_reversed else 1.5
        if self.snowballer:
            PopupText(
                    f"new hp.... {self.max_hp}",
                    color=(0.5, 0.5, 1.0, 1),
                    scale=1.0,
                    position=spaz.node.position,
                ).autoretain()
            spaz.hitpoints_max = self.max_hp
            spaz.hitpoints = self.max_hp
        
        # Lazy asf today
        if getattr(self, 'cloaked_enemies', False):
            spaz.perma_cloak()

        
       
        return spaz

    

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
        self._game_over = True
        if outcome == 'defeat':
            self.fade_to_red()
        score: int | None
        if self._wavenum >= 2:
            score = int(self._score)
            fail_message = None
        else:
            score = None
            fail_message = bs.Lstr(resource='reachWave2Text')
        from gummyoverhaul.overhaul_chests import give_chest

        if self.gambler:
            fail_message = 'disable the Gambler card.'
            score = None
   

        if score:
            if score > random.randint(1500, 2000):
                babase.app.plus.xp_sys.award_xp(34, True, scrnmessage=True)

                if random.randint(0, 12) == 0 and score:
                    give_chest(
                            {
                                "type": "both",
                                "color":  (0.1, 1, 0.8),
                                "name": "The Tower Chest", 
                                "tint": (1, 2, 2),
                                "tint2": (1, 1, 1), 
                                "coins": min(random.randint(score - 520, score + 1120), 9000),
                                "dollars": random.randint(3, 4)
                        })
                    

                if random.randint(0, 5) == 0 and score:
                        give_chest(
                            {
                                "type": "dollars",
                                "color": (0.1, 1, 0.8),
                                "name": "The Tower Chest", 
                                "tint": (1, 2, 2),
                                "tint2": (1, 1, 1), 
                                "rewards":  random.randint(2, 6)
                        })
                else:
                    if score:

                        give_chest(
                            {
                                "type": "coins",
                                "color": (0.1, 1, 0.8),
                                "name": "The Tower Chest", 
                                "tint": (1, 2, 2),
                                "tint2": (1, 1, 1), 
                                "rewards":  min(random.randint(score - 1620, score + 620), 9000)
                        })
        
        # i hate my life
        self.session.expert = self.expertmode
        self.session.bleedinghearts = self.bleedinghearts
        self.session.fool_reversed = self.fool_reversed
        self.session.snowballer_reversed = self.snowballer_reversed
        self.session.expertmode_reversed = self.expertmode_reversed
        self.session.sgarbage_reversed = self.sgarbage_reversed
        self.session.glasscanon_reversed = self.glasscanon_reversed
        self.session.permadeath_reversed = self.permadeath_reversed
        self.session.lowgravity_reversed = self.lowgravity_reversed
        self.session.explosiveenemies_reversed = self.explosiveenemies_reversed
        self.session.uhh_reversed = self.uhh_reversed
        self.session.timer_enabled_reversed = self.timer_enabled_reversed
        self.session.cloaked_enemies_reversed = self.cloaked_enemies_reversed
               
        self.end(
            {
                'outcome': outcome,
                'score': score,
                'fail_message': fail_message,
                'playerinfos': self.initialplayerinfos,
                
            },
            delay=delay,
        )

    

    def _update_waves(self) -> None:
        # If we have no living bots, go to the next wave.
        assert self._bots is not None
        if (
            self._can_end_wave
            and not self._bots.have_living_bots()
            and not self._game_over
        ):
            self._can_end_wave = False
            self._time_bonus_timer = None
            self._time_bonus_text = None
            
            won = False
            if self._wavenum != 0:
                # First player alive gets the popup
                for player in self.players:
                    xp = 7
                    if player.is_alive():
                        bs.app.plus.xp_sys.award_xp(xp, True, player.actor.node.position)
                        break
                    # No one is alive to see it lol
                    bs.app.plus.xp_sys.award_xp(xp, False)
                #bs.app.plus.xp_sys.award_xp(2, True, scrnmessage=True)
            

            base_delay = 4.0 if won else 0.0

            # Reward time bonus.
            if self._time_bonus > 0:
                bs.timer(0, self._cashregistersound.play)
                bs.timer(
                    base_delay,
                    bs.WeakCall(self._award_time_bonus, self._time_bonus),
                )
                base_delay += 1.0

            # Reward flawless bonus.
            if self._wavenum > 0:
                have_flawless = False
                for player in self.players:
                    if player.is_alive() and not player.has_been_hurt:
                        have_flawless = True
                        bs.timer(
                            base_delay,
                            bs.WeakCall(self._award_flawless_bonus, player),
                        )
                    player.has_been_hurt = False  # reset
                if have_flawless:
                    base_delay += 1.0

            

            self._wavenum += 1

            # Short celebration after waves.
            if self._wavenum > 1:
                self.celebrate(0.5)
            bs.timer(base_delay, bs.WeakCall(self._start_next_wave))

    def _award_completion_bonus(self) -> None:
        self._cashregistersound.play()
        for player in self.players:
            try:
                if player.is_alive():
                    assert self.initialplayerinfos is not None
                    self.stats.player_scored(
                        player,
                        int(100 / len(self.initialplayerinfos)),
                        scale=1.4,
                        color=(0.6, 0.6, 1.0, 1.0),
                        title=bs.Lstr(resource='completionBonusText'),
                        screenmessage=False,
                    )
            except Exception:
                logging.exception('error in _award_completion_bonus')

    def _award_time_bonus(self, bonus: int) -> None:
        self._cashregistersound.play()
        bs.getsound('crank').play()
        PopupText(
            bs.Lstr(
                value='+${A} ${B}',
                subs=[
                    ('${A}', str(bonus)),
                    ('${B}', bs.Lstr(resource='timeBonusText')),
                ],
            ),
            color=(1, 1, 0.5, 1),
            scale=1.0,
            position=(0, 3, -1),
        ).autoretain()
        self._score += self._time_bonus
        self._update_scores()

    def _award_flawless_bonus(self, player: Player) -> None:
        self._cashregistersound.play()
        bs.getsound('crank').play()
        try:
            if player.is_alive():
                assert self._flawless_bonus is not None
                bs.app.plus.xp_sys.award_xp(12, True, player.actor.node.position)
                self.stats.player_scored(
                    player,
                    self._flawless_bonus,
                    scale=1.2,
                    color=(0.6, 1.0, 0.6, 1.0),
                    title=bs.Lstr(resource='flawlessWaveText'),
                    screenmessage=False,
                )
        except Exception:
            logging.exception('error in _award_flawless_bonus')

    def _start_time_bonus_timer(self) -> None:
        self._time_bonus_timer = bs.Timer(
            1.0, bs.WeakCall(self._update_time_bonus), repeat=True
        )

    def _update_player_spawn_info(self) -> None:
        # If we have no living players lets just blank this.
        assert self._spawn_info_text is not None
        assert self._spawn_info_text.node
        if not any(player.is_alive() for player in self.teams[0].players) or self.permadeath:
            self._spawn_info_text.node.text = ''
        else:
            text: str | bs.Lstr = ''
            for player in self.players:
                if not player.is_alive() and (
                    self._preset in [Preset.ENDLESS]
                    or (player.respawn_wave <= len(self._waves))
                ):
                    rtxt = bs.Lstr(
                        resource='onslaughtRespawnText',
                        subs=[
                            ('${PLAYER}', player.getname()),
                            ('${WAVE}', str(player.respawn_wave)),
                        ],
                    )
                    text = bs.Lstr(
                        value='${A}${B}\n',
                        subs=[
                            ('${A}', text),
                            ('${B}', rtxt),
                        ],
                    )
            self._spawn_info_text.node.text = text

    def _respawn_players_for_wave(self) -> None:

        # no respawning
        if self.permadeath or self.timer_enabled:
            return
        # Respawn applicable players.

        for player in self.players:
                if (
                    not player.is_alive()
                    and player.respawn_wave == self._wavenum

                ):
                    self.spawn_player(player)
        self._update_player_spawn_info()

    def _setup_wave_spawns(self, wave: Wave) -> None:
        tval = 0.0
        dtime = 0.2
        if self._wavenum == 1:
            spawn_time = 3.973
            tval += 0.5
        else:
            spawn_time = 2.648

        bot_angle = wave.base_angle
        self._time_bonus = 0
        self._flawless_bonus = 0
        for info in wave.entries:
            if info is None:
                continue
            if isinstance(info, Delay):
                spawn_time += info.duration
                continue
            if isinstance(info, Spacing):
                bot_angle += info.spacing
                continue
            bot_type_2 = info.bottype
            if bot_type_2 is not None:
                assert not isinstance(bot_type_2, str)
                self._time_bonus += bot_type_2.points_mult * 20
                self._flawless_bonus += bot_type_2.points_mult * 5

            # If its got a position, use that.
            point = None
            if point is not None:
                assert bot_type_2 is not None
                spcall = bs.WeakCall(
                    self.add_bot_at_point, point, bot_type_2, spawn_time
                )
                bs.timer(tval, spcall)
                tval += dtime
            else:
                spacing = info.spacing
                bot_angle += spacing * 0.5
                if bot_type_2 is not None:
                    tcall = bs.WeakCall(
                        self.add_bot_at_angle, bot_angle, bot_type_2, spawn_time
                    )
                    bs.timer(tval, tcall)
                    tval += dtime
                bot_angle += spacing * 0.5

        # We can end the wave after all the spawning happens.
        bs.timer(
            tval + spawn_time - dtime + 0.01,
            bs.WeakCall(self._set_can_end_wave),
        )

    def _start_next_wave(self) -> None:
        # This can happen if we beat a wave as we die.
        # We don't wanna respawn players and whatnot if this happens.
        if self._game_over:
            return

        self._respawn_players_for_wave()
        if self._preset in {Preset.ENDLESS}:
            wave = self._generate_random_wave()
        else:
            wave = self._waves[self._wavenum - 1]
        self._setup_wave_spawns(wave)
        self._update_wave_ui_and_bonuses()
        bs.timer(0.4, self._new_wave_sound.play)
        self.spawn_enemies_based_on_fill()

    def _update_wave_ui_and_bonuses(self) -> None:
        if self.reversed:
            self.show_zoom_message(
            bs.Lstr(
                value='${A} ${B}',
                subs=[
                    ('${A}', bs.Lstr(resource='waveText')),
                    ('${B}', str(self._wavenum)),
                ],
            ),
            scale=1.0,
            duration=1.0,
            color = (3, 0, 0),
            trail=True,
        )
        elif self.expertmode:
            self.show_zoom_message(
            bs.Lstr(
                value='${A} ${B}',
                subs=[
                    ('${A}', bs.Lstr(resource='waveText')),
                    ('${B}', str(self._wavenum)),
                ],
            ),
            scale=1.0,
            duration=1.0,
            color = (0, 0.4, 1),
            trail=True,
        )
        else:
            self.show_zoom_message(
            bs.Lstr(
                value='${A} ${B}',
                subs=[
                    ('${A}', bs.Lstr(resource='waveText')),
                    ('${B}', str(self._wavenum)),
                ],
            ),
            scale=1.0,
            duration=1.0,
            trail=True,
        )
        # Reset our time bonus.
        tbtcolor = (1, 1, 0, 1)
        tbttxt = bs.Lstr(
            value='${A}: ${B}',
            subs=[
                ('${A}', bs.Lstr(resource='timeBonusText')),
                ('${B}', str(self._time_bonus)),
            ],
        )
        self._time_bonus_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'vr_depth': -30,
                    'color': tbtcolor,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'position': (0, -60),
                    'scale': 0.8,
                    'text': tbttxt,
                },
            )
        )

        bs.timer(5.0, bs.WeakCall(self._start_time_bonus_timer))
        wtcolor = (1, 1, 1, 1)
        wttxt = bs.Lstr(
            value='${A} ${B}',
            subs=[
                ('${A}', bs.Lstr(resource='waveText')),
                (
                    '${B}',
                    str(self._wavenum)
                    + (
                        ''
                        if self._preset
                        in [Preset.ENDLESS]
                        else ('/' + str(len(self._waves)))
                    ),
                ),
            ],
        )
        self._wave_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'vr_depth': -10,
                    'color': wtcolor,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'position': (0, -40),
                    'scale': 1.3,
                    'text': wttxt,
                },
            )
        )

    def _bot_levels_for_wave(self) -> list[list[type[SpazBot]]]:
        
        level = self.towerlevel

        if level == 1:
            bot_types = [
            BomberBotLite,
            BrawlerBotLite,
            BomberBotStaticLite,
            ImpulseBotLite,
            MiniBotLite,
            RandomBotLite,
            TriggerBot,
            EggBot,
            EggBotShielded,
            SlowBot,
            RandomBot,
            StickyBotLite,
            ImpulseBot,
            MiniBot,
            LoveBot,
            StarBot,
            StickyBotLite,
            LandMine,
            B2BBot,
            DumbassBot,
            GoldenBot,
        ]
        if level == 2:
            bot_types = [
                StoneBot,
                BomberBot,
                BrawlerBot,
                StoneBot,
                ExplodeyBotNoTimeLimit,
                RandomBot,
                RandomBot,
                MineBot,
                SlowBot,
                BouncySlowBot,
                SlowBot,
                BouncySlowBot,
                AggroMineBot,
                StickyBotLite,
                StickyBot,
                PlayerBot,
                NegativeBot,
                ProNegativeBot,
                EggBot,
                ProImpulseBot,
                ProMiniBot,
                ZeusBot,
                EletricBot,
                StarBot,
                ProStarBot,
                LoveBot,
                LandMine,
                B2BBot,
                DumbassBot,
                GoldenBot,
                BedBot,
            ]
        if level == 3:
            bot_types = [
                BomberBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                ChargerBot,
                StoneBot,
                StoneBot,
                StoneBot,
                MineBot,
                SlowBot,
                BouncySlowBot,
                SlowBot,
                BouncySlowBot,
                AggroMineBot,
                PlayerBotShielded,
                ProNegativeBot,
                NegativeBot,
                ProImpulseBot,
                ZeusBot,
                EletricBot,
                ProStarBot,
                ProStarBot,
                LoveBot,
                BoomBot,
                ProBoomBot,
                LandMine,
                B2BBot,
                ProB2BBot,
                DumbassBot,
                TotemBot,
                BouncyBot,
                IceBot,
                GoldenBot,
                BedBot,
                BedBot,
                BedBot,
                BedBot,
                BedBot,
                BedBot,
            ]
        if level == 4:
            bot_types = [
                TriggerBotPro,
                TriggerBotPro,
                ProStoneBot,
                BomberBot,
                BrawlerBot,
                ExplodeyBotShielded,
                ProIceBot,
                MineBot,
                SlowBot,
                BouncySlowBot,
                AggroMineBot,
                AggroMineBot,
                AggroMineBot,
                StickyBotLite,
                StickyBotLite,
                StickyBotLite,
                ProStickyBot,
                ProStickyBot,
                PlayerBot,
                ProNegativeBot,
                ProNegativeBot,
                ProImpulseBot,
                ProMiniBot,
                ZeusBot,
                ProStarBot,
                ProBoomBot,
                ProBoomBot,
                LandMine,
                ProB2BBot,
                ProB2BBotShielded,
                TotemBotPro,
                TotemBotProShielded,
                BouncyBot,
                IceBot,
                BouncyBot,
                IceBot,
                GoldenBot,
                ProGoldenBot,
                ProGoldenBot,
                BedBotPro,
                BedBotPro,
                BedBotPro,
                BedBotPro,
            ]
        if level == 5:
            bot_types = [
                BomberBot,
                BrawlerBot,
                TriggerBotProShielded,
                TriggerBotProShielded,
                BomberBotPro,
                BomberBotProShielded,
                BrawlerBotPro,
                BrawlerBotProShielded,
                ChargerBotProShielded,
                ProStoneBot,
                ExplodeyBotShielded,
                ProRandomBot,
                ProRandomBotShielded,
                ProIceBot,
                ProIceBotShielded,
                MineBot,
                AggroMineBot,
                AggroMineBotShielded,
                BouncySlowBot,
                AggroMineBotShielded,
                StickyBotLite,
                ProStickyBotShielded,
                ProStickyBot,
                PlayerBotShielded,
                ProNegativeBot,
                ProNegativeBotShielded,
                ProImpulseBot,
                ProImpulseBotShielded,
                ProMiniBot,
                ProMiniBotShielded,
                EletricBot,
                ProStarBot,
                ProStarBotShielded,
                ProBoomBot,
                ProBoomBotShielded,
                LandMine,
                ProB2BBot,
                ProB2BBotShielded,
                TotemBotPro,
                TotemBotProShielded,
                BouncyBot,
                IceBot,
                BouncyBot,
                IceBot,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                GoldenBot,
                ProGoldenBot,
                ProGoldenBot,
                ProGoldenBot,
                ProGoldenBotShielded,
                BedBotPro,
                BedBotPro,
                BedBotProShielded,
                BedBotPro,
                BedBotPro,
                BedBotProShielded,
                BedBotPro,
                BedBotPro,
                BedBotProShielded,
            ]
        if level == 6:
            bot_types = [
                BomberBot,
                BrawlerBot,
                TriggerBotPro,
                BomberBotPro,
                BrawlerBotPro,
                ChargerBot,
                ProStoneBot,
                ExplodeyBot,
                ProRandomBot,
                ProIceBot,
                AggroMineBotShielded,
                BouncySlowBot,
                AggroMineBotShielded,
                StickyBotLite,
                ProStickyBotShielded,
                ProNegativeBotShielded,
                ProImpulseBotShielded,
                ProMiniBotShielded,
                EletricBot,
                ZeusBot,
                ProStarBotShielded,
                ProBoomBotShielded,
                BoogieBot,
                TriggerBotPro,
                BomberBotPro,
                BrawlerBotPro,
                ChargerBot,
                ProStoneBot,
                ExplodeyBot,
                ProRandomBot,
                ProIceBot,
                LandMine,
                ProB2BBot,
                ProB2BBotShielded,
                TotemBotPro,
                TotemBotProShielded,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                TriggerBotStatic,
                BomberBotProStatic,
                ProGoldenBot,
                ProGoldenBot,
                ProGoldenBot,
                ProGoldenBot,
                ProGoldenBotShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
            ]
        if level == 7:
            bot_types = [
                # Gotta keep these in or it breaks lol
                BomberBot,
                BrawlerBot,
                TriggerBotPro,
                BomberBotPro,

                TriggerBotProShielded,
                TriggerBotProShielded,
                TriggerBotProShielded,
                BrawlerBotProShielded,
                BrawlerBotProShielded,
                BrawlerBotProShielded,
                ProStoneBotShielded,
                ProRandomBotShielded,
                ProIceBotShielded,
                AggroMineBotShielded,
                StickyBotLite,
                ProStickyBotShielded,
                ProNegativeBotShielded,
                ProImpulseBotShielded,
                EletricBot,
                BoogieBot,
                ZeusBot,
                ProStarBotShielded,
                LoveBot,
                ProBoomBotShielded,
                LandMine,
                ProB2BBotShielded,
                ProB2BBotShielded,
                ProB2BBotShielded,
                ProB2BBotShielded,
                TotemBotProShielded,
                ProGoldenBotShielded,
                ProGoldenBotShielded,
                ProGoldenBotShielded,
                ProGoldenBotShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
                BedBotProShielded,
            ]

        
        bot_levels = [
            [b for b in bot_types if b.points_mult == 1],
            [b for b in bot_types if b.points_mult == 2],
            [b for b in bot_types if b.points_mult == 3],
            [b for b in bot_types if b.points_mult == 4],
        ]

        # Make sure all lists have something in them
        if not all(bot_levels):
            raise RuntimeError('Got empty bot level')
        return bot_levels

    def _add_entries_for_distribution_group(
        self,
        group: list[tuple[int, int]],
        bot_levels: list[list[type[SpazBot]]],
        all_entries: list[Spawn | Spacing | Delay | None],
    ) -> None:
        entries: list[Spawn | Spacing | Delay | None] = []
        for entry in group:
            bot_level = bot_levels[entry[0] - 1]
            bot_type = bot_level[random.randrange(len(bot_level))]
            rval = random.random()
            if rval < 0.5:
                spacing = 10.0
            elif rval < 0.9:
                spacing = 20.0
            else:
                spacing = 40.0
            split = random.random() > 0.3
            for i in range(entry[1]):
                if split and i % 2 == 0:
                    entries.insert(0, Spawn(bot_type, spacing=spacing))
                else:
                    entries.append(Spawn(bot_type, spacing=spacing))
        if entries:
            all_entries += entries
            all_entries.append(Spacing(40.0 if random.random() < 0.5 else 80.0))

    def _generate_random_wave(self) -> Wave:
        level = self._wavenum
        bot_levels = self._bot_levels_for_wave()

        target_points = level * 3 - 2
        min_dudes = min(1 + level // 3, 10)
        max_dudes = min(10, level + 1)
        max_level = (
            4 if level > 6 else (3 if level > 3 else (2 if level > 2 else 1))
        )
        group_count = 3
        distribution = self._get_distribution(
            target_points, min_dudes, max_dudes, group_count, max_level
        )
        all_entries: list[Spawn | Spacing | Delay | None] = []
        for group in distribution:
            self._add_entries_for_distribution_group(
                group, bot_levels, all_entries
            )
        angle_rand = random.random()
        if angle_rand > 0.75:
            base_angle = 130.0
        elif angle_rand > 0.5:
            base_angle = 210.0
        elif angle_rand > 0.25:
            base_angle = 20.0
        else:
            base_angle = -30.0
        base_angle += (0.5 - random.random()) * 20.0
        wave = Wave(base_angle=base_angle, entries=all_entries)
        return wave

    def add_bot_at_point(
        self, point: Any, spaz_type: type[SpazBot], spawn_time: float = 1.0
    ) -> None:
        """Add a new bot at a specified named point."""
        if self._game_over:
            return
       
        pointpos = (0,0,0)
        assert self._bots is not None
        self._bots.spawn_bot(spaz_type, pos=pointpos, spawn_time=spawn_time)

    def add_bot_at_angle(
        self, angle: float, spaz_type: type[SpazBot], spawn_time: float = 1.0, is_boss: bool = False, is_garbage: bool = False
    ) -> None:
        """Add a new bot at a specified angle (for circular maps)."""
        if self._game_over:
            return
        angle_radians = angle / 57.2957795
        xval = math.sin(angle_radians) * 1.06
        zval = math.cos(angle_radians) * 1.06
        point = (xval / 0.125, 2.3, (zval / 0.2) - 3.7)
        assert self._bots is not None
        if is_garbage:
            def stronger(bot: SpazBot):
                if self.sgarbage:
                    bot.impact_scale *= 0.5
                    bot._punch_power_scale *= 1.2
                    if self.sgarbage_reversed:
                        bot.hitpoints_max = (1000) * 10
                        bot.hitpoints = bot.hitpoints_max
                        bot._punch_power_scale *= 0.25
            self._garbage_bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time, on_spawn_call=stronger)
        elif is_boss:
            self._boss_bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time)
        else:
            self._bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time)

    def _update_time_bonus(self) -> None:
        self._time_bonus = int(self._time_bonus * 0.93)
        if self._time_bonus > 0 and self._time_bonus_text is not None:
            assert self._time_bonus_text.node
            self._time_bonus_text.node.text = bs.Lstr(
                value='${A}: ${B}',
                subs=[
                    ('${A}', bs.Lstr(resource='timeBonusText')),
                    ('${B}', str(self._time_bonus)),
                ],
            )
        else:
            self._time_bonus_text = None

    def _start_updating_waves(self) -> None:
        self._wave_update_timer = bs.Timer(
            2.0, bs.WeakCall(self._update_waves), repeat=True
        )

    def _update_scores(self) -> None:
        score = int(self._score)
        
        assert self._scoreboard is not None
        self._scoreboard.set_team_value(self.teams[0], score, max_score=None)
        if self.expertmode:
            self._scoreboard.set_team_value(self.garbage_team, max(0, int(self.dmg)), max_score=20, flash=False)
            #import bascenev1 as bs;bs.getactivity().garbage_windup('L')
            self._scoreboard._entries[self.garbage_team.id]._width  = 20 * 8
    
    def apply_bleeding_hearts(self,damage: int ,player_activating: bs.Player):
        # recursion error bruh!
        if self.sharedhp:
            for p in self.players:
                if p == player_activating:
                        continue

                if p.actor.is_alive() and not p.actor.node.invincible:
                    
                 
                    # Ok hurt everyone
                    p.actor.hitpoints -=  damage * p.actor.impact_scale * self.bleedinghearts_damage_multiplier
                    p.actor.last_player_attacked_by =  player_activating
                    p.actor.node.hurt = (
                            1.0 - float(p.actor.hitpoints) / p.actor.hitpoints_max
                    )
                
                    p.actor.node.handlemessage('hurt_sound')
                    has_totem = not p.actor.totem < 1
                    if  p.actor.hitpoints <= 0:
                        if not has_totem:

                            p.actor.handlemessage(bs.DieMessage(False, bs.DeathType.BLEEDING_HEARTS))
                        
                        else:
                         p.actor.totem_effect()
    
    

    def apply_snowballer_buff(self):
        for player in self.players:
            if player.actor and player.actor.is_alive():
                increase = 110 if self.snowballer_reversed  else 250 
                self.max_hp += increase
                player.actor.hitpoints_max += increase
                player.actor.hitpoints += increase

           
                bs.getsound('tetris/KO').play()
                
                bs.emitfx(position=player.actor.node.position, scale=2.0, count=10, chunk_type='ice')
        # anyway show a message that you got the buff
        for player in self.players:
            if player.actor.is_alive():
                PopupText(
                    f"new hp.... {self.max_hp}",
                    color=(0.5, 0.5, 1.0, 1),
                    scale=1.0,
                    position=player.actor.node.position,
                ).autoretain()
                
               



    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        if isinstance(msg, PlayerSpazHurtMessage):
            msg.spaz.getplayer(Player, True).has_been_hurt = True
            self._a_player_has_been_hurt = True

            
            # here it comes lol
            if msg.spaz.is_alive(): # ignore the dead bodies (thats just not fair)
                bs.timer(0.1, bs.Call(
                    self.apply_bleeding_hearts,
                    (msg.damage*0.5) ,
                    msg.spaz.getplayer(Player, True)
                ))
                

        elif isinstance(msg, bs.PlayerScoredMessage):
            self._score += msg.score * ( (3 if random.random() > 0.5 else -3) if self.gambler_reversed else (2 if random.random() > 0.5 else 0) )if self.gambler else 1
            self._update_scores()

        elif isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment standard behavior.

           
            player = msg.getplayer(Player)
            self._a_player_has_been_hurt = True

            # Uh-huh 1 died so kill everynun
            if self.permadeath_reversed and msg.how is not bs.DeathType.OUT_OF_BOUNDS:
                for p in self.players:
                    # w reaccursion nerror
                    if p.actor.is_alive() and p != player:
                        p.actor.handlemessage(bs.DieMessage(how=bs.DeathType.OUT_OF_BOUNDS))
                self.end_game()

            
            player.respawn_wave = self._wavenum + 1
            self.add_damage_to_board(damage=5)
            if not self.timer_enabled:
                
      
                bs.timer(0.1, self._update_player_spawn_info)
                bs.timer(0.1, self._checkroundover)
            else:
                respawn_time = 5
                if self.pizza_face_exists:
                    # Pizza exists so no
                    bs.timer(0.1, self._checkroundover)
                    
                    
                else:
                    
                     
                    player.respawn_timer = bs.Timer(
                            respawn_time, bs.Call(self.spawn_player_if_exists, player)
                    )
                    player.respawn_icon = RespawnIcon(player, respawn_time)
                        
                    self.timer_value -= 20.7 * (self.timer_deaths * (1.25 if self.timer_enabled_reversed else 1))
                self.timer_deaths += 1
               



                
            # If we died from bleeding hearts dont attack others, (itll cause a chain reaction that just isnt fun)
            if msg.how is bs.DeathType.BLEEDING_HEARTS:
                return
            
            #here it comes 2
            bs.timer(0.1, bs.Call(
                    self.apply_bleeding_hearts,
                    (player.actor.hitpoints_max*0.5) ,
                    player
                ))
            
           
                

        elif isinstance(msg, SpazBotDiedMessage):
            # Small epxlosion here
            if self.explosiveenemies:
                if self.explosiveenemies_reversed:
                    Fire(msg.spazbot.node.position, 6)
                Blast(
                    msg.spazbot.node.position,
                    (0,0,0),
                    2.0 if self.explosiveenemies_reversed else 1.7,
                    source_player=None,

                )
            self.timer_value += 3.5 * (0.8 if self.timer_enabled_reversed else 1)
            pts, importance = msg.spazbot.get_death_points(msg.how)
            # lets go gambling!
            if self.gambler:
                pts *= (3 if random.random() > 0.5 else -3) if self.gambler_reversed else (2 if random.random() > 0.5 else 0)
            if msg.killerplayer is not None:
                if self.pizza_tower:
                    bs.getsound('sfx_killenemy').play()
                    bs.getsound('sfx_killingblow').play()
                    if self.combo_system.active:
                        self.combo_system.extend_combo()
                    else:
                        self.combo_system.start_combo()
                
                target: Sequence[float] | None
                if msg.spazbot.node:
                    target = msg.spazbot.node.position
                else:
                    target = None

                killerplayer = msg.killerplayer
                self.stats.player_scored(
                    killerplayer,
                    math.ceil(pts / 2) * (2 if self.hyperspeed else 1),
                    target=target,
                    kill=True,
                    screenmessage=False,
                    importance=importance,
                )
                dingsound = (
                    self._dingsound if importance == 1 else self._dingsoundhigh
                )
                dingsound.play(volume=0.6)


            
            # Normally we pull scores from the score-set, but if there's
            # no player lets be explicit.
            else:
                self._score += pts
            self._update_scores()
            if msg.killerplayer is not None:  
                self.remove_damage_to_board(damage=pts / 3)
                # Make sure we actually died to a player
                self._total_kills += 1
                if self.snowballer:
                    PopupText(
                        f"{self._total_kills % 20}/{(10 if self.snowballer_reversed else 20)}",
                        color=(0.5, 0.5, 1.0, 1),
                        scale=1.0,
                        position=msg.killerplayer.actor.node.position,
                    ).autoretain()
                    if self._total_kills % (10 if self.snowballer_reversed else 20) == 0:
                        self.apply_snowballer_buff()
            else:
                        # i always come back
                self.add_damage_to_board(damage=1)
                bs.camerashake(intensity = 1)
                bs.getsound('towermoveS').play()
                self.towerparticalsfallS()
        else:
            super().handlemessage(msg)

    

    

    def _set_can_end_wave(self) -> None:
        self._can_end_wave = True

    @override
    def end_game(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring
        if self._game_over:
            return

        # Tell our bots to celebrate just to rub it in.
        assert self._bots is not None
        if self.towerlevel == 7:
            bs.setmusic(bs.MusicType.SPECTATEFLOOR7, continuous=True)

        else:
            bs.setmusic(bs.MusicType.SPECTATE, continuous=True)
        if self._bots:
            self._bots.final_celebrate()
        self._game_over = True
        self.do_end('defeat', delay=4.0 if self.hyperspeed else 2.0)
        if self.hyperspeed:
            self._final_time_ms = int(
                                int(bs.time() * 1000.0) - self.starttime_ms
                            )
            
            self._time_text_input.node.timemax = self._final_time_ms
            
        


    def _checkroundover(self) -> None:
        """Potentially end the round based on the state of the game."""
        if self.has_ended():
            return
        # We dont care about this stuff in tetris mode (handled in the board)
        if self.tetris:
            return
        if not any(player.is_alive() for player in self.teams[0].players):
            self.end_game()




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
        
        self.combo_time -= 0.2 if bs.getactivity().uhh_reversed else 0.1 
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

        if bs.getactivity().uhh:
            for p in bs.getplayers():
                p.actor.handlemessage(bs.DieMessage())
                p.actor._cursed = True
                p.actor.curse_explode()
            bs.getactivity().end_game()


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
