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

from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.actor.bomb import TNTSpawner
from bascenev1lib.actor.playerspaz import PlayerSpazHurtMessage
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.gameutils import SharedObjects

from bascenev1lib.actor.flag import Flag
from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory
from bascenev1lib.actor.spaz import Spaz
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
from bascenev1lib.actor.respawnicon import RespawnIcon


if TYPE_CHECKING:
    from typing import Any, Sequence
    from bascenev1lib.actor.spazbot import SpazBot


class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.has_been_hurt = False
        self.respawn_timer: bs.Timer | None = None
        self.respawn_icon: RespawnIcon | None = None



class Team(bs.Team[Player]):
    """Our team type for this game."""

# im not even gonna lie idk why i did this its kinda  a waste of space ;-;
class CaptureFlag(Flag):

    def __init__(self, *, size: float= 2.5,position = ..., color = ..., materials = None, touchable = True, dropped_timeout = None):
        super().__init__(position=position, color=color, materials=materials, touchable=touchable, dropped_timeout=dropped_timeout)
        
        Flag.project_stand(position)
        self.capturing_sound =bs.newnode('sound',attrs={'sound': bs.getsound('ticking'),'volume':0})
        
        self._flag_text = bs.newnode('text'
                                     ,attrs={
                "text": f"0%",
                "in_world": True,
                "shadow": 1.0,
                "flatness": 1.0,
                "position": (
                    position[0],
                    position[1]+2,
                    position[2],
                ),
                "color": (1, 1, 1),
                "scale": 0.01,
                "h_align": "center",
            },
                                     )


       
        self._flag_light = bs.newnode(
            'light',
            attrs={
                'position': position,
                'intensity': 0.2,
                'height_attenuated': False,
                'radius': 0.4,
                'color': (0.2, 0.2, 0.2),
            },
        )
        self._flag_ring: bs.Node = bs.newnode(
            'locator',
            attrs={
                'position': position,
                'shape': 'circleOutline',
                'size':[size *2],
                'color': (1, 1, 1),
                'opacity': 0.55,
                'draw_beauty': True,
                'additive': False
        })
       
        

class DefendGame(bs.CoopGameActivity[Player, Team]):
    """Co-op game where players try to survive attacking waves of enemies from a flag."""

    name = 'Defender'
    description = 'Defend all enemies.'
    default_music = bs.MusicType.DEFEND

    tips: list[str | bs.GameTip] = [
        'Hold any button to run.'
        '  (Trigger buttons work well if you have them)',
        'Try tricking enemies into killing eachother or running off cliffs.',
        'Try \'Cooking off\' bombs for a second or two before throwing them.',
        'It\'s easier to win with a friend or two helping.',
        'If you stay in one place, you\'re toast. Run and dodge to survive..',
        'Practice using your momentum to throw bombs more accurately.',
        'Your punches do much more damage if you are running or spinning.',
    ]

    # Show messages when players die since it matters here.
    announce_player_deaths = True

    def __init__(self, settings: dict):
        settings['map'] = 'Doom Shroom'
        super().__init__(settings)
        self._game_over = False

        self._spawn_center = (0, 3, -5)
        self._powerup_center = (0, 5, -3.6)
        self._powerup_spread = (6.0, 4.0)

        self.player_remove_capture = 0.1
        self.bot_add_capture = 0.06
        self._active_powerup_drops = 0
        self._max_powerup_drops = 3
        
       
        self.survival_time = 0
        self.bots_alive = 0
        self.max_bots = 2
        
        self.initial_spawn_interval = 6.5
        self.spawn_interval = self.initial_spawn_interval 
        self.spawner_timer: bs.Timer = None
        self._score = 0
        self.flag_owner = 'nobody'
        self._scoreboard: Scoreboard | None = None
        self.base_respawn_time = 3.2
        self.contesting_players: list[tuple[bool, Spaz]] = []
        self._bots: SpazBotSet | None = None
        self.shared = SharedObjects.get()
        self._dingsound = bs.getsound('dingSmall')
        self._dingsoundhigh = bs.getsound('dingSmallHigh')
        self.flag_capture_progress = 0.0
        self._flag_region_material = bs.Material()
        self._flag_region_material.add_actions(
            conditions=('they_have_material', self.shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                (
                    'call',
                    'at_connect',
                    bs.Call(self._handle, True),
                ),
                (
                    'call',
                    'at_disconnect',
                    bs.Call(self._handle, False),
                ),
            ),
        )

    def on_begin(self) -> None:
        super().on_begin() 

        
        self._tntspawner = TNTSpawner(position=(0.0, 3.0, -5.0))

        size = 2.5
        self._flag_pos = self.map.get_flag_position(None)
        self._flag = CaptureFlag(
            size=size, position=self._flag_pos, touchable=False, color=(1, 1, 1)
        )
        flagmats = [self._flag_region_material, self.shared.region_material]
        bs.newnode(
            'region',
            attrs={
                'position': self._flag_pos,
                'scale': tuple([size for _ in range(3)]),
                'type': 'sphere',
                'materials': flagmats,
            },
        )
        self._scoreboard = Scoreboard(label=bs.Lstr(resource='scoreText'))
        self._bots = SpazBotSet()
        bs.timer(1.0, self._time_tick, repeat=True)
        self.spawner_timer = bs.Timer(self.initial_spawn_interval, self._spawn_tick)
        bs.timer(0.1, self._flag_tick, repeat=True)
        self._drop_powerups(
            standard_points=True,
        )
        bs.timer(4.0, self._start_powerup_drops)
    
    def _flag_tick(self):
        self.contesting_players = [
            s for s in self.contesting_players if s[1].is_alive()
        ]

        players_in_zone = sum(1 for p in self.contesting_players if p[0] is True)
        bots_in_zone = sum(1 for p in self.contesting_players if p[0] is False)

        previous_owner = self.flag_owner
        if players_in_zone > 0:
            # Players have priority
            self.flag_capture_progress = max(0, self.flag_capture_progress - self.player_remove_capture * players_in_zone)
            self.flag_owner = 'player'
            self._flag._flag_light.color = (0, 0.2, 1)
            self._flag._flag_ring.color = (0, 0.2, 1)
            self._flag.node.color = (0, 0.2, 1)
        elif bots_in_zone > 0:
            self.flag_capture_progress += self.bot_add_capture * bots_in_zone
            self.flag_capture_progress = min(self.flag_capture_progress, 100)
            self.flag_owner = 'bot'
            self._flag._flag_light.color = (1, 0, 0)
            self._flag._flag_ring.color = (1, 0, 0)
            self._flag.node.color = (1, 0, 0)

            if self.flag_capture_progress >= 100:
                self.bot_capture_loss()
        else:
            self.flag_owner = 'nobody'
            self._flag._flag_light.color = (1, 1, 1)
            self._flag._flag_ring.color = (1, 1, 1)
            self._flag.node.color = (1, 1, 1)

        self._flag._flag_text.text = f"{int(self.flag_capture_progress)}%"
        if previous_owner != self.flag_owner:
            bs.getsound('swip').play()

    def _handle(self, colliding: bool) -> None:
        try:
            spaz = bs.getcollision().opposingnode.getdelegate(Spaz, True)
        except bs.NotFoundError:
            return

        assert isinstance(spaz, Spaz)
        is_player = bool(spaz.source_player)

        if colliding and spaz.is_alive():
            self.contesting_players.append((is_player, spaz))

        if not colliding:
            for entry in self.contesting_players:
                if entry[1] is spaz:
                    try:
                        self.contesting_players.remove(entry)
                    except ValueError:
                        pass
                    break
        
    def _start_another_powerup_drop(self):
        if self._active_powerup_drops >= self._max_powerup_drops:
            return
        self._active_powerup_drops += 1
        bs.Timer(
            2.0, lambda: self._drop_powerups_excluding(['curse', 'what']), repeat=True
        )

    def _drop_powerups_excluding(
        self, exclude: list
    ) -> None:
            """Generic powerup drop."""
       
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
                excludetypes=exclude
                ),
            ).autoretain()
 

    def _drop_powerup(self, index: int, poweruptype: str | None = None) -> None:
        poweruptype = PowerupBoxFactory.get().get_random_powerup_type(
            forcetype=poweruptype
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
                   
                ),
            ).autoretain()

    def _time_tick(self):
        survival_time_score = 10
        self.survival_time += 1
        self._score += survival_time_score
        self._update_scores()
        bs.getsound('tick').play()
        self.max_bots = 4 + int(self.survival_time * 0.05)
        self.spawn_interval = max(0.8, 3.0 - self.survival_time * 0.01)
        # every 40 seconds add more powerups
        if int(self.survival_time) % 40 == 0:
            self._start_another_powerup_drop()

    def _spawn_tick(self):
        self.spawner_timer = bs.Timer(self.spawn_interval, self._spawn_tick)

        if self.bots_alive >= self.max_bots:
            return

        # (80s per level) 🤑
        level = min(self.survival_time // 80 + 1, 7)

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
        elif level == 2:
            bot_types = [
                StoneBot,
                BomberBot,
                BrawlerBot,
                StoneBot,
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
        elif level == 3:
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
                BoogieBot,
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
        elif level == 4:
            bot_types = [
                TriggerBotPro,
                TriggerBotPro,
                ProStoneBot,
                BomberBot,
                BrawlerBot,
                #ExplodeyBotShielded,
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
                BoogieBot,
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
        elif level == 5:
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
                #ExplodeyBotShielded,
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
                BoogieBot,
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
        elif level == 6:
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
        elif level == 7:
            bot_types = [
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

        chosen_type = random.choice(bot_types)
        self.add_bot_at_angle(random.uniform(255, -255), chosen_type, 1)

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
        self._bots.spawn_bot(spaz_type, pos=point, spawn_time=spawn_time,on_spawn_call=bs.Call(self._on_bot_spawn))
        
        

    def _on_bot_spawn(self, spaz: SpazBot) -> None:
        spaz_type = type(spaz)
        assert spaz is not None
        spaz.update_callback = self._update_bot
        self.bots_alive += 1

    def _update_bot(self, bot: SpazBot) -> bool:
        # Yup; that's a lot of return statements right there.
        # pylint: disable=too-many-return-statements
        if self._game_over:
            return True
        if not bool(bot):
            return True
        any_players_alive = any(player.is_alive() for team in self.teams for player in team.players)
        if not any_players_alive:
            # Nearest player
            my_pos = bot.node.position
        

            target_pos = self._flag.node.position
            

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

            movement_speed = 0.8

            
            bot.node.move_left_right = move_x * movement_speed
            bot.node.move_up_down = -move_z * movement_speed

            return True 
        else:
            return False
   
        
        

        
        
        
     
        

        
    
       

        



    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(Player)
   
            assert self.initialplayerinfos is not None
            respawn_time = self.base_respawn_time + len(self.initialplayerinfos) * 1.2
            player.respawn_timer = bs.Timer(
                respawn_time, bs.Call(self.spawn_player_if_exists, player)
            )
            player.respawn_icon = RespawnIcon(player, respawn_time)

        elif isinstance(msg, SpazBotDiedMessage):
            self.bots_alive -= 1
            pts, importance = msg.spazbot.get_death_points(msg.how)
            if msg.killerplayer is not None:
                target: Sequence[float] | None
                if msg.spazbot.node:
                    target = msg.spazbot.node.position
                else:
                    target = None

                killerplayer = msg.killerplayer
                self.stats.player_scored(
                    killerplayer,
                    pts,
                    target=target,
                    kill=True,
                    screenmessage=False,
                    importance=importance,
                )
                
                dingsound = (
                    self._dingsound if importance == 1 else self._dingsoundhigh
                )
                self._score += int(pts * (1 if importance == 1 else 2.3) )
                dingsound.play(volume=0.6)

            # Normally we pull scores from the score-set, but if there's
            # no player lets be explicit.
            else:
                self._score += pts
            self._update_scores()

        else:
            super().handlemessage(msg)

    def _update_scores(self) -> None:
        if self._game_over:
            return
        score = self._score
       
        assert self._scoreboard is not None
        self._scoreboard.set_team_value(self.teams[0], int(score), max_score=None)



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
        return spaz
    
    def do_end(self, outcome: str, delay: float = 0.0) -> None:
        """End the game with the specified outcome."""
        self.fade_to_red()
        score = self._score
        self._game_over = True
        fail_message = None
    
  
        self.end(
            {
                'outcome': outcome,
                'score': score,
                'fail_message': fail_message,
                'playerinfos': self.initialplayerinfos,
            },
            delay=delay,
        )

    def bot_capture_loss(self):
        if not self._game_over:
            self.do_end('defeat', 3.0)
            bs.getsound('boo').play()
            bs.getsound('hiss').play()
            bs.getsound('playerDeath').play()
            bs.setmusic(None)