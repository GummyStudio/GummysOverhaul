# Released under the MIT License. See LICENSE for details.
#
"""FUCKING CHAOTIC FREE FOR ALL CAPTURE THE FLAG

has been my dream gamemode ever since i created overhaul, FINALLY DOING IT!!

By GummyBoiYT <3

also im kinda mad that i had to get help from chatgpt, even though  i did work..

Enjoy!
"""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import weakref
from enum import Enum
from typing import TYPE_CHECKING
import babase

from typing_extensions import override
import bascenev1 as bs

from bascenev1lib.actor.flag import Flag, FlagDiedMessage
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence


class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.time_at_flag = 0


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self, _score_: int) -> None:
        self._score_ = _score_


# ba_meta export bascenev1.GameActivity
class FreeForAllCTFByGUMMYBOIYT(bs.TeamGameActivity[Player, Team]):
    """Game where a team wins by holding a 'hill' for a set amount of time."""

    name = 'FFA Capture The Flag'
    description = 'Fight and capture the singular flag.'
    available_settings = [
        bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=3,
            increment=1,
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
                ('Shorter', 0.25),
                ('Short', 0.5),
                ('Normal', 1.0),
                ('Long', 2.0),
                ('Longer', 4.0),
            ],
            default=1.0,
        ),
        bs.BoolSetting('Epic Mode', default=False),
    ]

    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(
            sessiontype, bs.FreeForAllSession
        )

    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        assert bs.app.classic is not None
        return bs.app.classic.getmaps('team_flag')

    def __init__(self, settings: dict):
        super().__init__(settings)
        shared = SharedObjects.get()
        self._scoreboard = Scoreboard()
        self._swipsound = bs.getsound('swip')
        self._score_sound = bs.getsound('score')
        self._scoring_team: weakref.ref[Team] | None = None
        self._hold_time = 0
        self._time_limit = float(settings['Time Limit'])
        self.score_to_win = int(settings['Score to Win'])
        self._epic_mode = bool(settings['Epic Mode'])
        self._last_home_flag_notice_print_time = 0

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = (
            bs.MusicType.EPIC if self._epic_mode else bs.MusicType.FLAG_CATCHER
        )

    @override
    def get_instance_description(self) -> str | Sequence:
            return 'Fight for the singular flag.'


    @override
    def get_instance_description_short(self) -> str | Sequence:
        if self.score_to_win == 1:
            return 'return 1 flag'
        return 'return ${ARG1} flags', self.score_to_win

    @override
    def create_team(self, sessionteam: bs.SessionTeam) -> Team:
        return Team(_score_=self.score_to_win)

    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._update_scoreboard()
        self.last_holder = None
        self.make_flags()
        self._flag2_pos = self.map.get_flag_position(1)
        self._flagCAP = Flag(
            position=self._flag2_pos, 
            touchable=False, 
            color=(1, 0, 0),
        )
        self._flag_light = bs.newnode(
            'light',
            owner=self._flagCAP.node,
            attrs={'intensity': 0.2, 'radius': 0.3, 'color': (0.2, 0.2, 0.2)},
        )
        assert self._flagCAP.node
        self._flagCAP.node.connectattr('position', self._flag_light, 'position')

        def check_flag_collision():
            if self._flagFFA and self._flagCAP and self._flagFFA.node and self._flagCAP.node:
                pos1 = self._flagFFA.node.position
                pos2 = self._flagCAP.node.position

                distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2) ** 0.5
        
                if distance < 1.0:  # Adjust threshold based on flag size
                    self._handle_flag_entered_base()      
  
        bs.timer(0.1, self.check_flag_holder, repeat=True)
        bs.timer(0.11, check_flag_collision, repeat=True)
    
    def check_flag_holder(self):
        if self._flagFFA and self._flagFFA.node and self._flagCAP and self._flagCAP.node:
            new_holders = set()
            for player in self.players:
                if player.actor and player.actor.node:
                    # Check if the player is holding the flag
                    if player.actor.node.hold_node == self._flagFFA.node:
                        new_holders.add(player)
                        self.killme = player

            self.last_holder = new_holders
    
    def get_holders(self):
        return [p for p in self.last_holder]
    
    def get_last_holder(self):
        return self.killme

    def delete_flags(self):
        self._flagFFA.node.delete()
        self.make_flags()
    
    def make_flags(self):
        self._flag1_pos = self.map.get_flag_position(0)
        Flag.project_stand(self._flag1_pos)
        self._swipsound.play()
        self._flagFFA = Flag(
            position=self._flag1_pos, touchable=True, color=(1, 1, 1)
        )

    
    def _flash_flag_spawn(self, color: tuple[float, float, float]) -> None:
        light = bs.newnode(
            'light',
            attrs={
                'position': self.map.get_flag_position(1),
                'color': color,
                'radius': 0.3,
                'height_attenuated': False,
            },
        )
        bs.animate(light, 'intensity', {0.0: 0, 0.25: 0.5, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)
    
    def _score(self, player: Player) -> None:
        player.team._score_ += 1
        self._flash_flag_spawn(player.color)
        self._score_sound.play()
        self._update_scoreboard()
        self.delete_flags()
        player.actor.handlemessage(bs.CelebrateMessage(2.0))
        self.show_zoom_message(
                    bs.Lstr(
                        resource='nameScoresText', subs=[('${NAME}', player.getname())]
                    ),
                    color=player.color,
                )
        if player.team._score_ >= self.score_to_win:
                self.end_game()


    def _handle_flag_entered_base(self) -> None:
        holders = len(self.get_holders())
        if holders == 1 or holders == 0:

            if holders == 0:
                player = self.get_last_holder()
            else:
                player = self.get_holders()[0]

            if player is not None:
                self.stats.player_scored(
                    player, 10, screenmessage=True, display=True
                )
                self._score(player)
        else:
            # Don't want slo-mo affecting this

                curtime = bs.basetime()
                if curtime - self._last_home_flag_notice_print_time > 5.0:
                    self._last_home_flag_notice_print_time = curtime
                    bpos = self.map.get_flag_position(1)
                    tval = 'Only one person can score at a time.'
                    tnode = bs.newnode(
                        'text',
                        attrs={
                            'text': tval,
                            'in_world': True,
                            'scale': 0.013,
                            'color': (1, 1, 0, 1),
                            'h_align': 'center',
                            'position': (bpos[0], bpos[1] + 3.2, bpos[2]),
                        },
                    )
                    bs.timer(5.1, tnode.delete)
                    bs.animate(
                        tnode, 'scale', {0.0: 0, 0.2: 0.013, 4.8: 0.013, 5.0: 0}
                    )
        
    @override
    def on_team_join(self, team: Team) -> None:
        team._score_ = 0
        self._update_scoreboard()
    
    @override
    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team._score_)
        self.end(results=results, announce_delay=0)

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team._score_, self.score_to_win, countdown=False
            )

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)  # Augment default.
            player = msg.getplayer(Player)
            self.respawn_player(player)
        elif isinstance(msg, FlagDiedMessage):
            self.make_flags()