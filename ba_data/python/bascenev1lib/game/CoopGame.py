# Released under the MIT License. See LICENSE for details.
#
"""Defines the runaround co-op game."""

# We wear the cone of shame.
# pylint: disable=too-many-lines

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast, Sequence

from typing_extensions import override
import bascenev1 as bs


from bascenev1lib.actor.bomb import TNTSpawner
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.respawnicon import RespawnIcon
from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.spazbot import (
    SpazBotSet,
    SpazBot,
    SpazBotDiedMessage,
    BomberBot,
    BrawlerBot,
    TriggerBot,
    TriggerBotPro,
    BomberBotProShielded,
    TriggerBotProShielded,
    ChargerBot,
    ChargerBotProShielded,
    StickyBot,
    ExplodeyBot,
    BrawlerBotProShielded,
    BomberBotPro,
    BrawlerBotPro,
)

if TYPE_CHECKING:
    from typing import Any

class Point(Enum):
    """Where we can spawn stuff and the corresponding map attr name."""

    BOTTOM_LEFT = 'bot_spawn_bottom_left'
    BOTTOM_RIGHT = 'bot_spawn_bottom_right'
    START = 'bot_spawn_start'
    START2 = 'bot_spawn_start2'

@dataclass
class Delay:
    """A delay between events in a wave."""

    duration: float


class Preset(Enum):
    """Game presets we support."""

    TRAINING = 'training'
    TRAINING_EASY = 'training_easy'
    ROOKIE = 'rookie'
    ROOKIE_EASY = 'rookie_easy'
    PRO = 'pro'
    PRO_EASY = 'pro_easy'
    UBER = 'uber'
    UBER_EASY = 'uber_easy'
    ENDLESS = 'endless'
    ENDLESS_TOURNAMENT = 'endless_tournament'
    ENDLESS_GUMMY = 'endless_gummy'
    TOWER = 'tower'

@dataclass
class Spawn:
    """Defines a bot spawn event."""

    # noinspection PyUnresolvedReferences
    type: type[SpazBot]
    path: int = 0
    point: Point | None = None


@dataclass
class SpawnO:
    """A bot spawn event in a wave."""

    bottype: type[SpazBot] | str
    point: Point | None = None
    spacing: float = 5.0

@dataclass
class Spacing:
    """Defines spacing between spawns."""

    duration: float

@dataclass
class SpacingO:
    """Empty space in a wave."""

    spacing: float = 5.0


@dataclass
class Wave:
    """Defines a wave of enemies."""

    entries: list[Spawn | Spacing | None]

@dataclass
class WaveO:
    """A wave of enemies."""

    entries: list[SpawnO | SpacingO | Delay | None]
    base_angle: float = 0.0



class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.respawn_timer: bs.Timer | None = None
        self.respawn_icon: RespawnIcon | None = None


class Team(bs.Team[Player]):
    """Our team type for this game."""


# ba_meta export bascenev1.GameActivity
class RunaroundFFAGame(bs.TeamGameActivity[Player, Team]):
    """Game involving trying to bomb bots as they walk through the map."""

    name = 'Runaround'
    description = 'Prevent enemies from reaching the exit.'
    tips = [
        'Jump just as you\'re throwing to get bombs up to the highest levels.',
        'No, you can\'t get up on the ledge. You have to throw bombs.',
        'Whip back and forth to get more distance on your throws..',
    ]
    
    default_music = bs.MusicType.MARCHING

    # How fast our various bot types walk.
    _bot_speed_map: dict[type[SpazBot], float] = {
        BomberBot: 0.48,
        BomberBotPro: 0.48,
        BomberBotProShielded: 0.48,
        BrawlerBot: 0.57,
        BrawlerBotPro: 0.57,
        BrawlerBotProShielded: 0.57,
        TriggerBot: 0.73,
        TriggerBotPro: 0.78,
        TriggerBotProShielded: 0.78,
        ChargerBot: 1.0,
        ChargerBotProShielded: 1.0,
        ExplodeyBot: 1.0,
        StickyBot: 0.5,
    }

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
            bs.IntSetting(
                'Score to Win',
                min_value=50,
                default=250,
                increment=50,
            ),
            bs.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('None', 0),
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                    ('20 Minutes', 1200),
                ],
                default=0,
            ),
            bs.FloatChoiceSetting(
                'Respawn Times',
                choices=[
                    ('Shorter', 1),
                    ('Short', 2),
                    ('Normal', 4),
                    ('Long', 6),
                    ('Longer', 8),
                ],
                default=4,
            ),
        ]

        return settings
    
    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession) or issubclass(
            sessiontype, bs.FreeForAllSession
        )

    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return ['Tower D']

    @override
    def get_instance_description(self) -> str | Sequence:
        return 'Prevent enemies from reaching the exit'

    
    def __init__(self, settings: dict):



        super().__init__(settings)
        shared = SharedObjects.get()

        self._player_death_sound = bs.getsound('playerDeath')
        self._new_wave_sound = bs.getsound('scoreHit01')
        self._winsound = bs.getsound('score')
        self._cashregistersound = bs.getsound('cashRegister')
        self._bad_guy_score_sound = bs.getsound('shieldDown')
        self._heart_tex = bs.gettexture('heart')
        self._heart_mesh_opaque = bs.getmesh('heartOpaque')
        self._heart_mesh_transparent = bs.getmesh('heartTransparent')

        self._a_player_has_been_killed = False
        self._spawn_center = self._map_type.defs.points['spawn1'][0:3]
        self._tntspawnpos = self._map_type.defs.points['tnt_loc'][0:3]
        self._powerup_center = self._map_type.defs.boxes['powerup_region'][0:3]
        self._powerup_spread = (
            self._map_type.defs.boxes['powerup_region'][6] * 0.5,
            self._map_type.defs.boxes['powerup_region'][8] * 0.5,
        )

        self._score_region_material = bs.Material()
        self._score_region_material.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._handle_reached_end),
            ),
        )

        self._last_wave_end_time = bs.time()
        self._scoreboard: Scoreboard | None = None
        self._game_over = False
        self._wavenum = 0
        self._can_end_wave = True
        self.nextwavepossible = True
        self._time_bonus = 0
        self._score_region: bs.Actor | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._dingsoundhigh = bs.getsound('dingSmallHigh')
        self._exclude_powerups: list[str] | None = None
        self._have_tnt: bool | None = None
        self._waves: list[Wave] | None = None
        self._bots = SpazBotSet()
        self._tntspawner: TNTSpawner | None = None
        self._lives_bg: bs.NodeActor | None = None
    
        self._start_lives = 10
        self._scoreboard = Scoreboard()

        self._timer = 0
        self._lives = self._start_lives
        self._lives_text: bs.NodeActor | None = None
        self._flawless = True
        self._lives_hbtime: bs.Timer | None = None
        self._time_bonus_mult: float | None = None
        self._wave_text: bs.NodeActor | None = None
        self._flawless_bonus: int | None = None
        self._wave_update_timer: bs.Timer | None = None


        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])
        self._res_time = float(settings['Respawn Times'])

    @override
    def on_transition_in(self) -> None:
        super().on_transition_in()
        self._score_region = bs.NodeActor(
            bs.newnode(
                'region',
                attrs={
                    'position': self.map.defs.boxes['score_region'][0:3],
                    'scale': self.map.defs.boxes['score_region'][6:9],
                    'type': 'box',
                    'materials': [self._score_region_material],
                },
            )
        )
    
    @override
    def on_team_join(self, team: Team) -> None:
        team.score = 0
        self._update_scores()

    @override
    def on_begin(self) -> None:
        super().on_begin()

        self._exclude_powerups = []
        self._have_tnt = True
        self.setup_standard_time_limit(self._time_limit)

        # Spit out a few powerups and start dropping more shortly.
        self._drop_powerups(standard_points=True)
        bs.timer(4.0, self._start_powerup_drops)
        self._update_scores()

        # Our TNT spawner (if applicable).
        if self._have_tnt:
            self._tntspawner = TNTSpawner(position=self._tntspawnpos)

        # Make sure to stay out of the way of menu/party buttons in the corner.
        assert bs.app.classic is not None
        uiscale = bs.app.ui_v1.uiscale
        l_offs = (
            -80
            if uiscale is bs.UIScale.SMALL
            else -40 if uiscale is bs.UIScale.MEDIUM else 0
        )

        self._lives_bg = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'texture': self._heart_tex,
                    'mesh_opaque': self._heart_mesh_opaque,
                    'mesh_transparent': self._heart_mesh_transparent,
                    'attach': 'topRight',
                    'scale': (90, 90),
                    'position': (-110 + l_offs, -50),
                    'color': (1, 0.2, 0.2),
                },
            )
        )
            
        # FIXME; should not set things based on vr mode.
        #  (won't look right to non-vr connected clients, etc)
        vrmode = bs.app.env.vr
        self._lives_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'right',
                    'h_align': 'center',
                    'color': (1, 1, 1, 1) if vrmode else (0.8, 0.8, 0.8, 1.0),
                    'flatness': 1.0 if vrmode else 0.5,
                    'shadow': 1.0 if vrmode else 0.5,
                    'vr_depth': 10,
                    'position': (-113 + l_offs, -69),
                    'scale': 1.3,
                    'text': str(self._lives),
                },
            )
        )
           

        bs.timer(2.0, self._start_updating_waves)

    def _handle_reached_end(self) -> None:
        spaz = bs.getcollision().opposingnode.getdelegate(SpazBot, True)
        if not spaz.is_alive():
            return  # Ignore bodies flying in.

        pos = spaz.node.position
        light = bs.newnode(
            'light', attrs={'position': pos, 'radius': 0.5, 'color': (1, 0, 0)}
        )
        bs.animate(light, 'intensity', {0.0: 0, 0.1: 1, 0.5: 0}, loop=False)
        bs.timer(1.0, light.delete)

        if True:
            spaz.handlemessage(
            bs.DieMessage(immediate=True, how=bs.DeathType.REACHED_GOAL)
            )
            self._bad_guy_score_sound.play(position=pos)
            self._flawless = False

            if self._lives >= 0:
                self._lives -= 1
                if self._lives == 0:
                    self._bots.stop_moving()
                    self.end_game()
                # Heartbeat behavior
                if self._lives < 5:
                    hbtime = 0.39 + (0.21 * self._lives)
                    self._lives_hbtime = bs.Timer(
                    hbtime, lambda: self.heart_dyin(True, hbtime), repeat=True
                )
                    self.heart_dyin(True)
                else:
                    self._lives_hbtime = None
                    self.heart_dyin(False)

                assert self._lives_text is not None
                assert self._lives_text.node
                self._lives_text.node.text = str(self._lives)
                delay = 0.0

                def _safesetattr(node: bs.Node, attr: str, value: Any) -> None:
                    if node:
                        setattr(node, attr, value)

                for _i in range(4):
                    bs.timer(
                        delay,
                        bs.Call(
                        _safesetattr,
                        self._lives_text.node,
                        'color',
                        (1, 0, 0, 1.0),
                    ),
                )
                    assert self._lives_bg is not None
                    assert self._lives_bg.node
                    bs.timer(
                        delay,
                        bs.Call(_safesetattr, self._lives_bg.node, 'opacity', 0.5),
                )
                    delay += 0.125
                    bs.timer(
                        delay,
                        bs.Call(
                        _safesetattr,
                        self._lives_text.node,
                        'color',
                        (1.0, 1.0, 0.0, 1.0),
                    ),
                )
                    bs.timer(
                    delay,
                    bs.Call(_safesetattr, self._lives_bg.node, 'opacity', 1.0),
                )
                delay += 0.125
                bs.timer(
                delay,
                bs.Call(
                    _safesetattr,
                    self._lives_text.node,
                    'color',
                    (0.8, 0.8, 0.8, 1.0),
                ),
            )

    @override
    def spawn_player(self, player: Player) -> bs.Actor:
        pos = (
            self._spawn_center[0] + random.uniform(-1.5, 1.5),
            self._spawn_center[1],
            self._spawn_center[2] + random.uniform(-1.5, 1.5),
        )
        spaz = self.spawn_player_spaz(player, position=pos)

        # Add the material that causes us to hit the player-wall.
        gamemap = self.map

        spaz.node.materials += (gamemap.preloaddata['collide_with_wall_material'],)

        return spaz

    def _drop_powerup(self, index: int, poweruptype: str | None = None) -> None:
        if poweruptype is None:
            poweruptype = PowerupBoxFactory.get().get_random_powerup_type(
                excludetypes=self._exclude_powerups
            )
        PowerupBox(
            position=self.map.powerup_spawn_points[index],
            poweruptype=poweruptype,
        ).autoretain()

    def _start_powerup_drops(self) -> None:
        bs.timer(3.0, self._drop_powerups, repeat=True)

    def _drop_powerups(
        self, standard_points: bool = False, force_first: str | None = None
    ) -> None:
        """Generic powerup drop."""

        # If its been a minute since our last wave finished emerging, stop
        # giving out land-mine powerups. (prevents players from waiting
        # around for them on purpose and filling the map up)
        if bs.time() - self._last_wave_end_time > 60.0:
            extra_excludes = ['land_mines']
        else:
            extra_excludes = []

        if standard_points:
            points = self.map.powerup_spawn_points
            for i in range(len(points)):
                bs.timer(
                    1.0 + i * 0.5,
                    bs.Call(
                        self._drop_powerup, i, force_first if i == 0 else None
                    ),
                )
        else:
            pos = (
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

            # drop one random one somewhere..
            assert self._exclude_powerups is not None
            PowerupBox(
                position=pos,
                poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
                    excludetypes=self._exclude_powerups + extra_excludes
                ),
            ).autoretain()

    @override
    def end_game(self) -> None:
        results = bs.GameResults()

        for team in self.teams:
            results.set_team_score(team, team.score)
        self._player_death_sound.play()
        self.end(results=results)



    def do_end(self, outcome: str) -> None:
        """End the game now with the provided outcome."""

        self.end_game()

    def _update_waves(self) -> None:
        # pylint: disable=too-many-branches

        # If we have no living bots, go to the next wave.
        if (
            self._can_end_wave
            and not self._bots.have_living_bots()
            and not self._game_over
            and self._lives >= 0
        ):
            self._can_end_wave = False

            self._wavenum += 1


            bs.timer(1, self._start_next_wave)




    def _start_next_wave(self) -> None:
        # FIXME: Need to split this up.
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-statements
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
        bs.timer(0.4, self._new_wave_sound.play)
        t_sec = 0.0
        base_delay = 0.5
        delay = 0.0
        bot_types: list[Spawn | Spacing | None] = []
        if True:
            level = self._wavenum
            target_points = (level + 1) * 8.0
            group_count = random.randint(1, 3)
            entries: list[Spawn | Spacing | None] = []
            spaz_types: list[tuple[type[SpazBot], float]] = []
            if level < 6:
                spaz_types += [(BomberBot, 5.0)]
            if level < 10:
                spaz_types += [(BrawlerBot, 5.0)]
            if level < 15:
                spaz_types += [(TriggerBot, 6.0)]
            if level > 5:
                spaz_types += [(TriggerBotPro, 7.5)] * (1 + (level - 5) // 7)
            if level > 2:
                spaz_types += [(BomberBotProShielded, 8.0)] * (
                    1 + (level - 2) // 6
                )
            if level > 6:
                spaz_types += [(TriggerBotProShielded, 12.0)] * (
                    1 + (level - 6) // 5
                )
            if level > 1:
                spaz_types += [(ChargerBot, 10.0)] * (1 + (level - 1) // 4)
            if level > 7:
                spaz_types += [(ChargerBotProShielded, 15.0)] * (
                    1 + (level - 7) // 3
                )

            # Bot type, their effect on target points.
            defender_types: list[tuple[type[SpazBot], float]] = [
                (BomberBot, 0.9),
                (BrawlerBot, 0.9),
                (TriggerBot, 0.85),
            ]
            if level > 2:
                defender_types += [(ChargerBot, 0.75)]
            if level > 4:
                defender_types += [(StickyBot, 0.7)] * (1 + (level - 5) // 6)
            if level > 6:
                defender_types += [(ExplodeyBot, 0.7)] * (1 + (level - 5) // 5)
            if level > 8:
                defender_types += [(BrawlerBotProShielded, 0.65)] * (
                    1 + (level - 5) // 4
                )
            if level > 10:
                defender_types += [(TriggerBotProShielded, 0.6)] * (
                    1 + (level - 6) // 3
                )

            for group in range(group_count):
                this_target_point_s = target_points / group_count

                # Adding spacing makes things slightly harder.
                rval = random.random()
                if rval < 0.07:
                    spacing = 1.5
                    this_target_point_s *= 0.85
                elif rval < 0.15:
                    spacing = 1.0
                    this_target_point_s *= 0.9
                else:
                    spacing = 0.0

                path = random.randint(1, 3)

                # Don't allow hard paths on early levels.
                if level < 3:
                    if path == 1:
                        path = 3

                # Easy path.
                if path == 3:
                    pass

                # Harder path.
                elif path == 2:
                    this_target_point_s *= 0.8

                # Even harder path.
                elif path == 1:
                    this_target_point_s *= 0.7

                # Looping forward.
                elif path == 4:
                    this_target_point_s *= 0.7

                # Looping backward.
                elif path == 5:
                    this_target_point_s *= 0.7

                # Random.
                elif path == 6:
                    this_target_point_s *= 0.7

                def _add_defender(
                    defender_type: tuple[type[SpazBot], float], pnt: Point
                ) -> tuple[float, Spawn]:
                    # This is ok because we call it immediately.
                    # pylint: disable=cell-var-from-loop
                    return this_target_point_s * defender_type[1], Spawn(
                        defender_type[0], point=pnt
                    )

                # Add defenders.
                defender_type1 = defender_types[
                    random.randrange(len(defender_types))
                ]
                defender_type2 = defender_types[
                    random.randrange(len(defender_types))
                ]
                defender1 = defender2 = None
                if (
                    (group == 0)
                    or (group == 1 and level > 3)
                    or (group == 2 and level > 5)
                ):
                    if random.random() < min(0.75, (level - 1) * 0.11):
                        this_target_point_s, defender1 = _add_defender(
                            defender_type1, Point.BOTTOM_LEFT
                        )
                    if random.random() < min(0.75, (level - 1) * 0.04):
                        this_target_point_s, defender2 = _add_defender(
                            defender_type2, Point.BOTTOM_RIGHT
                        )

                spaz_type = spaz_types[random.randrange(len(spaz_types))]
                member_count = max(
                    1, int(round(this_target_point_s / spaz_type[1]))
                )
                for i, _member in enumerate(range(member_count)):
                    if path == 4:
                        this_path = i % 3  # Looping forward.
                    elif path == 5:
                        this_path = 3 - (i % 3)  # Looping backward.
                    elif path == 6:
                        this_path = random.randint(1, 3)  # Random.
                    else:
                        this_path = path
                    entries.append(Spawn(spaz_type[0], path=this_path))
                    if spacing != 0.0:
                        entries.append(Spacing(duration=spacing))

                if defender1 is not None:
                    entries.append(defender1)
                if defender2 is not None:
                    entries.append(defender2)

                # Some spacing between groups.
                rval = random.random()
                if rval < 0.1:
                    spacing = 5.0
                elif rval < 0.5:
                    spacing = 1.0
                else:
                    spacing = 1.0
                entries.append(Spacing(duration=spacing))

            wave = Wave(entries=entries)


        bot_types += wave.entries
        self._time_bonus_mult = 1.0
        this_flawless_bonus = 0
        non_runner_spawn_time = 1.0

        for info in bot_types:
            if info is None:
                continue
            if isinstance(info, Spacing):
                t_sec += info.duration
                continue
            bot_type = info.type
            path = info.path
            self._time_bonus_mult += bot_type.points_mult * 0.02
            this_flawless_bonus += bot_type.points_mult * 5

            # If its got a position, use that.
            if info.point is not None:
                point = info.point
            else:
                point = Point.START

            # Space our our slower bots.
            delay = base_delay
            delay /= self._get_bot_speed(bot_type)
            t_sec += delay * 0.5
            tcall = bs.Call(
                self.add_bot_at_point,
                point,
                bot_type,
                path,
                0.1 if point is Point else non_runner_spawn_time,
            )
            bs.timer(t_sec, tcall)
            t_sec += delay * 0.5

        # We can end the wave after all the spawning happens.
        bs.timer(
            t_sec - delay * 0.5 + non_runner_spawn_time + 0.01,
            self._set_can_end_wave,
        )

        # Reset our time bonus.
        # In this game we use a constant time bonus so it erodes away in
        # roughly the same time (since the time limit a wave can take is
        # relatively constant) ..we then post-multiply a modifier to adjust
        # points.
        self._time_bonus = 150
        self._flawless_bonus = this_flawless_bonus
        assert self._time_bonus_mult is not None
        txtval = bs.Lstr(
            value='${A}: ${B}',
            subs=[
                ('${A}', bs.Lstr(resource='timeBonusText')),
                ('${B}', str(int(self._time_bonus * self._time_bonus_mult))),
            ],
        )


        # Keep track of when this wave finishes emerging. We wanna stop
        # dropping land-mines powerups at some point (otherwise a crafty
        # player could fill the whole map with them)
        self._last_wave_end_time = bs.Time(bs.time() + t_sec)

        txtval = bs.Lstr(
            value='${A} ${B}',
            subs=[
                ('${A}', bs.Lstr(resource='waveText')),
                (
                    '${B}',
                    str(self._wavenum),
                ),
            ],
        )
        self._wave_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'bottom',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'vr_depth': -10,
                    'color': (1, 1, 1, 1),
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'position': (0, -15),
                    'scale': 1.3,
                    'text': txtval,
                },
            )
        )

    def _on_bot_spawn(self, path: int, spaz: SpazBot) -> None:
        # Add our custom update callback and set some info for this bot.
        spaz_type = type(spaz)
        assert spaz is not None
        spaz.update_callback = self._update_bot

        # Tack some custom attrs onto the spaz.
        setattr(spaz, 'r_walk_row', path)
        setattr(spaz, 'r_walk_speed', self._get_bot_speed(spaz_type))

    def add_bot_at_point(
        self,
        point: Point,
        spaztype: type[SpazBot],
        path: int,
        spawn_time: float = 0.1,
    ) -> None:
        """Add the given type bot with the given delay (in seconds)."""

        # Don't add if the game has ended.
        if self._game_over:
            return
        pos = self.map.defs.points[point.value][:3]
        self._bots.spawn_bot(
            spaztype,
            pos=pos,
            spawn_time=spawn_time,
            on_spawn_call=bs.Call(self._on_bot_spawn, path),
        )

    def _start_updating_waves(self) -> None:
        self._wave_update_timer = bs.Timer(2.0, self._update_waves, repeat=True)

    def _update_scores(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._score_to_win
            )
            # Check if we won.
            if team.score >= self._score_to_win:
                self.end_game()

    def _update_bot(self, bot: SpazBot) -> bool:
        # Yup; that's a lot of return statements right there.
        # pylint: disable=too-many-return-statements

        if not bool(bot):
            return True

        assert bot.node

        # FIXME: Do this in a type safe way.
        r_walk_speed: float = getattr(bot, 'r_walk_speed')
        r_walk_row: int = getattr(bot, 'r_walk_row')

        speed = r_walk_speed
        pos = bot.node.position
        boxes = self.map.defs.boxes

        if True:

            # Bots in row 1 attempt the high road..
            if r_walk_row == 1:
                if bs.is_point_in_box(pos, boxes['b4']):
                    bot.node.move_up_down = speed * bot.speed_mult
                    bot.node.move_left_right = 0
                    bot.node.run = 0.0
                    return True
                if bs.is_point_in_box(pos, boxes['b5']):
                    bot.node.move_up_down = -speed * bot.speed_mult
                    bot.node.move_left_right = 0
                    bot.node.run = 0.0
                    return True

            # Row 1 and 2 bots attempt the middle road..
            if r_walk_row in [1, 2]:
                if bs.is_point_in_box(pos, boxes['b1']):
                    bot.node.move_up_down = speed * bot.speed_mult
                    bot.node.move_left_right = 0
                    bot.node.run = 0.0
                    return True


            # All bots settle for the third row.
            if bs.is_point_in_box(pos, boxes['b7']):
                bot.node.move_up_down = speed * bot.speed_mult
                bot.node.move_left_right = 0
                bot.node.run = 0.0
                return True
            if bs.is_point_in_box(pos, boxes['b2']):
                bot.node.move_up_down = -speed * bot.speed_mult
                bot.node.move_left_right = 0
                bot.node.run = 0.0
                return True
            if bs.is_point_in_box(pos, boxes['b3']):
                bot.node.move_up_down = -speed * bot.speed_mult
                bot.node.move_left_right = 0
                bot.node.run = 0.0
                return True
            if bs.is_point_in_box(pos, boxes['b6']):
                bot.node.move_up_down = speed * bot.speed_mult
                bot.node.move_left_right = 0
                bot.node.run = 0.0
                return True
            if (
                bs.is_point_in_box(pos, boxes['b8'])
                and not bs.is_point_in_box(pos, boxes['b9'])
            ) or pos == (0.0, 0.0, 0.0):
                # Default to walking right if we're still in the walking area.
                bot.node.move_left_right = speed * bot.speed_mult
                bot.node.move_up_down = 0
                bot.node.run = 0.0
                return True
            


        # Revert to normal bot behavior otherwise..
        return False

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerScoredMessage):
            
            self._update_scores()

        elif isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)

            self._a_player_has_been_killed = True

            # Respawn them shortly.

            player = msg.getplayer(Player)
            player.respawn_timer = bs.Timer(
                self._res_time, bs.Call(self.spawn_player_if_exists, player)
            )
            player.respawn_icon = RespawnIcon(player, self._res_time)

        elif isinstance(msg, SpazBotDiedMessage):
            if msg.how is bs.DeathType.REACHED_GOAL:
                return None
            pts, importance = msg.spazbot.get_death_points(msg.how)
            if msg.killerplayer:
                    msg.killerplayer.team.score += pts
                    dingsound = (
                            self._dingsound
                            if importance == 1
                            else self._dingsoundhigh
                        )
                    dingsound.play(volume=0.6)
            else:
                # Suicide.
                pass
            self._update_scores()

        else:
            return super().handlemessage(msg)
        return None

    def _get_bot_speed(self, bot_type: type[SpazBot]) -> float:
        speed = self._bot_speed_map.get(bot_type)
        if speed is None:
            raise TypeError(
                'Invalid bot type to _get_bot_speed(): ' + str(bot_type)
            )
        return speed

    def _set_can_end_wave(self) -> None:
        self._can_end_wave = True

    def heart_dyin(self, status: bool, time: float = 1.22) -> None:
        """Makes the UI heart beat at low health."""
        assert self._lives_bg is not None
        if self._lives_bg.node.exists():
            return
        heart = self._lives_bg.node

        # Make the heart beat intensely!
        if status:
            bs.animate_array(
                heart,
                'scale',
                2,
                {
                    0: (90, 90),
                    time * 0.1: (105, 105),
                    time * 0.21: (88, 88),
                    time * 0.42: (90, 90),
                    time * 0.52: (105, 105),
                    time * 0.63: (88, 88),
                    time: (90, 90),
                },
            )

        # Neutralize heartbeat (Done did when dead.)
        else:
            # Ew; janky old scenev1 has a single 'Node' Python type so
            # it thinks heart.scale could be a few different things
            # (float, Sequence[float], etc.). So we have to force the
            # issue with a cast(). This should go away with scenev2/etc.
            bs.animate_array(
                heart,
                'scale',
                2,
                {
                    0.0: cast(Sequence[float], heart.scale),
                    time: (90, 90),
                },
            )

# ba_meta export bascenev1.GameActivity
class OnslaughtFFAGame(bs.TeamGameActivity[Player, Team]):
    """Co-op game where players try to survive attacking waves of enemies."""

    name = 'Onslaught'
    description = 'Defeat all enemies.'

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

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
            bs.IntSetting(
                'Score to Win',
                min_value=50,
                default=250,
                increment=50,
            ),
            bs.IntChoiceSetting(
                'Time Limit',
                choices=[
                    ('1 Minute', 60),
                    ('2 Minutes', 120),
                    ('5 Minutes', 300),
                    ('10 Minutes', 600),
                    ('20 Minutes', 1200),
                ],
                default=0,
            ),
            bs.FloatChoiceSetting(
                'Respawn Times',
                choices=[
                    ('Normal', 4),
                    ('Long', 6),
                    ('Longer', 8),
                ],
                default=4,
            ),
        ]

        return settings
    
    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, bs.DualTeamSession) or issubclass(
            sessiontype, bs.FreeForAllSession
        )

    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return ['Doom Shroom']

    @override
    def get_instance_description(self) -> str | Sequence:
        return 'Defeat all enemies.'

    @override
    def get_instance_description_short(self) -> str | Sequence:
        return 'get ${ARG1} points', self._score_to_win


    def __init__(self, settings: dict):
        self._preset = Preset.ENDLESS
        if self._preset in {
            Preset.TRAINING,
            Preset.TRAINING_EASY,
            Preset.PRO,
            Preset.PRO_EASY,
            Preset.ENDLESS,
            Preset.ENDLESS_TOURNAMENT,
        }:
            settings['map'] = 'Doom Shroom'
        else:
            settings['map'] = 'Courtyard'

        super().__init__(settings)

        self._new_wave_sound = bs.getsound('scoreHit01')
        self._winsound = bs.getsound('score')
        self._cashregistersound = bs.getsound('cashRegister')
        self._a_player_has_been_hurt = False
        self._player_has_dropped_bomb = False

        # FIXME: should use standard map defs.
        if settings['map'] == 'Doom Shroom':
            self._spawn_center = (0, 3, -5)
            self._tntspawnpos = (0.0, 3.0, -5.0)
            self._powerup_center = (0, 5, -3.6)
            self._powerup_spread = (6.0, 4.0)

        self._scoreboard: Scoreboard | None = None
        self._game_over = False
        self._wavenum = 0
        self._can_end_wave = True
        self._score = 0
        self._time_bonus = 0
        self._dingsound = bs.getsound('dingSmall')
        self._dingsoundhigh = bs.getsound('dingSmallHigh')
        self._have_tnt = False
        self._excluded_powerups: list[str] | None = None
        self._waves: list[WaveO] = []
        self._tntspawner: TNTSpawner | None = None
        self._bots: SpazBotSet | None = None
        self._powerup_drop_timer: bs.Timer | None = None
        self._time_bonus_timer: bs.Timer | None = None
        self._flawless_bonus: int | None = None
        self._wave_text: bs.NodeActor | None = None
        self._wave_update_timer: bs.Timer | None = None
        self._throw_off_kills = 0
        self._land_mine_kills = 0
        self._tnt_kills = 0

        self._score_to_win = int(settings['Score to Win'])
        self._time_limit = float(settings['Time Limit'])
        self._res_time = float(settings['Respawn Times'])

    @override
    def on_transition_in(self) -> None:
        super().on_transition_in()
        customdata = bs.getsession().customdata

        self._scoreboard = Scoreboard()
        bs.setmusic(bs.MusicType.ONSLAUGHT)

        self._update_scores()

    @override
    def on_begin(self) -> None:
        super().on_begin()

        self.setup_standard_time_limit(self._time_limit)
        self._have_tnt = True
        self._excluded_powerups = []
        self._waves = []


        # FIXME: Should migrate to use setup_standard_powerup_drops().

        bs.timer(4.0, self._start_powerup_drops)

        # Our TNT spawner (if applicable).
        if self._have_tnt:
            self._tntspawner = TNTSpawner(position=self._tntspawnpos)

        self._update_scores()
        self._bots = SpazBotSet()
        bs.timer(4.0, self._start_updating_waves)

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
        pos = (
            self._spawn_center[0] + random.uniform(-1.5, 1.5),
            self._spawn_center[1],
            self._spawn_center[2] + random.uniform(-1.5, 1.5),
        )
        spaz = self.spawn_player_spaz(player, position=pos)
        
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
        self.end_game()

    def _update_waves(self) -> None:
        # If we have no living bots, go to the next wave.
        assert self._bots is not None
        if (
            self._can_end_wave
            and not self._bots.have_living_bots()
            and not self._game_over
        ):
            self._can_end_wave = False

            if self._preset in {Preset.ENDLESS, Preset.ENDLESS_TOURNAMENT}:
                won = False
            else:
                won = self._wavenum == len(self._waves)

            base_delay = 4.0 if won else 0.0

            self._wavenum += 1


            bs.timer(base_delay, bs.WeakCall(self._start_next_wave))


    def _setup_wave_spawns(self, wave: WaveO) -> None:
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
            if isinstance(info, SpacingO):
                bot_angle += info.spacing
                continue
            bot_type_2 = info.bottype
            if bot_type_2 is not None:
                assert not isinstance(bot_type_2, str)
                self._time_bonus += bot_type_2.points_mult * 20
                self._flawless_bonus += bot_type_2.points_mult * 5

            # If its got a position, use that.
            point = info.point
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
        
        if self._preset in {Preset.ENDLESS, Preset.ENDLESS_TOURNAMENT}:
            wave = self._generate_random_wave()
        else:
            wave = self._waves[self._wavenum - 1]
        self._setup_wave_spawns(wave)
        self._update_wave_ui_and_bonuses()
        bs.timer(0.4, self._new_wave_sound.play)

    def _update_wave_ui_and_bonuses(self) -> None:
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
                        in [Preset.ENDLESS, Preset.ENDLESS_TOURNAMENT]
                        else ('/' + str(len(self._waves)))
                    ),
                ),
            ],
        )
        self._wave_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'bottom',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'vr_depth': -10,
                    'color': wtcolor,
                    'shadow': 1.0,
                    'flatness': 1.0,
                    'position': (0, -15),
                    'scale': 1.3,
                    'text': wttxt,
                },
            )
        )

    def _bot_levels_for_wave(self) -> list[list[type[SpazBot]]]:
        level = self._wavenum
        bot_types = [
            BomberBot,
            BrawlerBot,
            TriggerBot,
            ChargerBot,
            BomberBotPro,
            BrawlerBotPro,
            TriggerBotPro,
            BomberBotProShielded,
            ExplodeyBot,
            ChargerBotProShielded,
            StickyBot,
            BrawlerBotProShielded,
            TriggerBotProShielded,
        ]
        if level > 5:
            bot_types += [
                ExplodeyBot,
                TriggerBotProShielded,
                BrawlerBotProShielded,
                ChargerBotProShielded,
            ]
        if level > 7:
            bot_types += [
                ExplodeyBot,
                TriggerBotProShielded,
                BrawlerBotProShielded,
                ChargerBotProShielded,
            ]
        if level > 10:
            bot_types += [
                TriggerBotProShielded,
                TriggerBotProShielded,
                TriggerBotProShielded,
                TriggerBotProShielded,
            ]
        if level > 13:
            bot_types += [
                TriggerBotProShielded,
                TriggerBotProShielded,
                TriggerBotProShielded,
                TriggerBotProShielded,
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
        all_entries: list[SpawnO | SpacingO | Delay | None],
    ) -> None:
        entries: list[SpawnO | SpacingO | Delay | None] = []
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
                    entries.insert(0, SpawnO(bot_type, spacing=spacing))
                else:
                    entries.append(SpawnO(bot_type, spacing=spacing))
        if entries:
            all_entries += entries
            all_entries.append(SpacingO(40.0 if random.random() < 0.5 else 80.0))

    def _generate_random_wave(self) -> WaveO:
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
        all_entries: list[SpawnO | SpacingO | Delay | None] = []
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
        wave = WaveO(base_angle=base_angle, entries=all_entries)
        return wave

    def add_bot_at_point(
        self, point: Point, spaz_type: type[SpazBot], spawn_time: float = 1.0
    ) -> None:
        """Add a new bot at a specified named point."""
        if self._game_over:
            return
        assert isinstance(point.value, str)
        pointpos = self.map.defs.points[point.value]
        assert self._bots is not None
        self._bots.spawn_bot(spaz_type, pos=pointpos, spawn_time=spawn_time)

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

    def _start_updating_waves(self) -> None:
        self._wave_update_timer = bs.Timer(
            2.0, bs.WeakCall(self._update_waves), repeat=True
        )

    def _update_scores(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._score_to_win
            )
            # Check if we won.
            if team.score >= self._score_to_win:
                self.end_game()
    @override
    def on_team_join(self, team: Team) -> None:
        team.score = 0
        self._update_scores()

    @override
    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment standard behavior.
            player = msg.getplayer(Player)
            # Respawn them shortly.

            player = msg.getplayer(Player)
            player.respawn_timer = bs.Timer(
                self._res_time, bs.Call(self.spawn_player_if_exists, player)
            )
            player.respawn_icon = RespawnIcon(player, self._res_time)

        elif isinstance(msg, SpazBotDiedMessage):
            pts, importance = msg.spazbot.get_death_points(msg.how)
            if msg.killerplayer is not None:


                killerplayer = msg.killerplayer
                killerplayer.team.score += pts
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
        results = bs.GameResults()

        for team in self.teams:
            results.set_team_score(team, team.score)
        self.end(results=results)
