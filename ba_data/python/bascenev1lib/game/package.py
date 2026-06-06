# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from typing_extensions import override
import bascenev1 as bs

from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.actor.flag import Flag

if TYPE_CHECKING:
    from typing import Any, Sequence


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.score = 0


class Package(Bomb):

    def __init__(
		self,
		position: Sequence[float] = (0.0, 1.0, 0.0),
		velocity: Sequence[float] = (0.0, 0.0, 0.0),
	) -> None:
        Bomb.__init__(
			self,
			position,
			velocity,
			bomb_type='package',
			blast_radius=0,
			source_player=None,
            owner=None,
        )
        self.startingpos = self.node.position
        self.holders = []
        bs.timer(0.1, (self.tick))
        
    def tick(self):
        # Remove dead people from holders.
        for player in self.holders:
            if not player.is_alive():
                self.holders.remove(player)


    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PickedUpMessage):
            player = msg.node.getdelegate(PlayerSpaz, True)._player
            if player not in self.holders:
                self.holders.append(player)  # Add new holder
        elif isinstance(msg, bs.DroppedMessage):
            player = msg.node.getdelegate(PlayerSpaz, True)._player
            if player in self.holders:
                self.holders.remove(player)
        elif isinstance(msg, bs.DieMessage):
            self.node.delete()
            activity = self._activity()
            if activity and not msg.immediate:
                activity.handlemessage(PackageDieMessage())
        else:
            super().handlemessage(msg)

class PackageDieMessage:
    "Gets called whenever a package dies."

# ba_meta export bascenev1.GameActivity
class PackageCollectorGame(bs.TeamGameActivity[Player, Team]):
    """A game type based on acquiring packages."""

    name = 'Package Collector'
    description = 'Collect packages to score points!'

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
            bs.IntSetting(
            'Score to Win',
            min_value=1,
            default=10,
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
        assert bs.app.classic is not None
        return bs.app.classic.getmaps('package')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.settings = settings
        self._scoreboard = Scoreboard()
        self._score_to_win: int | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._epic_mode = False
        self._kills_to_win_per_player = int(settings['Score to Win'])
        self._score_to_win = self._kills_to_win_per_player
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = False
        self._last_home_flag_notice_print_time = 0

        # Base class overrides.
        self.slow_motion = self._epic_mode
        self.default_music = bs.MusicType.PACKAGE

    @override
    def get_instance_description(self) -> str | Sequence:
        return 'Deliver ${ARG1} packages to the flag.', self._score_to_win

    @override
    def get_instance_description_short(self) -> str | Sequence:
        return 'Deliver ${ARG1} packages to the flag.', self._score_to_win

    @override
    def on_team_join(self, team: Team) -> None:
        if self.has_begun():
            self._update_scoreboard()

    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_time_limit(self._time_limit)
        self.setup_standard_powerup_drops()
        self._flagSCORE = Flag(
            position=self.map.get_flag_position(None), 
            touchable=False, 
            color=(1, 1, 1),
        )
        self._flag_light = bs.newnode(
            'light',
            owner=self._flagSCORE.node,
            attrs={'intensity': 0.2, 'radius': 0.3, 'color': (0.2, 0.2, 0.2)},
        )
        assert self._flagSCORE.node
        self._flagSCORE.node.connectattr('position', self._flag_light, 'position')
        self.packages = []
        self._score_to_win = self._score_to_win
        self._update_scoreboard()
        self.set_up_default_packages()

        bs.timer(0.13, self.tick, repeat=True)
    
    def _flash_flag_spawn(self, color: tuple[float, float, float]) -> None:
        light = bs.newnode(
            'light',
            attrs={
                'position': self.map.get_flag_position(None),
                'color': color,
                'radius': 0.3,
                'height_attenuated': False,
            },
        )
        bs.animate(light, 'intensity', {0.0: 0, 0.25: 0.5, 0.5: 0}, loop=True)
        bs.timer(1.0, light.delete)
    
    def tick(self) -> None:
        for package in self.packages:
            self.check_scores(package)

    def spawn_package(self, position: tuple[float, float, float]) -> None:
        package = Package(position=position, velocity=(0.0, 1.0, 0.0)).autoretain()
        self.packages.append(package)
    
    def _is_near_flag(self, package: Package) -> bool:
        """Returns True if the package is close to the scoring flag."""
        """Checks if the package is near the flag using Euclidean distance."""
        if not package.node.exists():
            return False
        distance = math.dist(package.node.position, self.map.get_flag_position(None))  # Calculate the distance
        return distance < 1.5

    def check_scores(self, package: Package):
        """Check if any package is near the scoring flag and update the score."""
        if self._is_near_flag(package):
            self.score(package)
                

    def score(self, package: Package):
        current = package.holders
        if current:
            if not len(current) == 1:
                curtime = bs.basetime()
                if curtime - self._last_home_flag_notice_print_time > 5.0:
                    self._last_home_flag_notice_print_time = curtime
                    bpos = self.map.get_flag_position(None)
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
                return
            else:
                if len(current) == 0:
                    return

                for player in current:
                    player.team.score += 1
                    self.stats.player_scored(
                    player, 1, screenmessage=True, display=True
                    )
                    player.actor.handlemessage(bs.CelebrateMessage(2.0))
                    bs.getsound('score').play()
                    self._update_scoreboard()
                
                    if player.team.score == self._score_to_win:
                        self.end_game()
                    
                    package_respawn_pos = package.startingpos
                    self.packages.remove(package)  # Ensure it's removed from tracking
                    timer = 0.1
                    timer2 = 2
                    bs.animate_array(self._flagSCORE.node,'color', 3,
                        {
                        timer: player.actor.Dcolor,
                        timer2: (1, 1, 1)
                        }
                    )
                    self._flash_flag_spawn(player.actor.Dcolor)
                    if isinstance(player.actor, PlayerSpaz) and player.actor:
                        player.actor.set_score_text(
                        str(player.team.score) + '/' + str(self._score_to_win),
                        color=player.team.color,
                        flash=True,
                    )
                    bs.timer(int(random.randint(10, 17) * random.random()), lambda: self.spawn_package(position=package_respawn_pos))
                    package.handlemessage(bs.DieMessage())

    def spawn_package_random_location(self):     
        self.spawn_package(position=(random.randint(-7, 7), 10, random.uniform(0.7, -8)))

    def set_up_default_packages(self):
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(-6, 6, -7.8)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(-4, 5.5, -4)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(0, 5, -6)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(-2, 5, -5.4)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(2, 4, -2)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(4, 5, -7.3)))
        bs.timer(random.randint(2, 5), lambda: self.spawn_package(position=(4, 5, -2)))
        bs.timer(random.randint(2, 5), self.spawn_package_random_location)

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            self.respawn_player(player)
            return

        if isinstance(msg, PackageDieMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            bs.timer(random.randint(2, 8), self.spawn_package_random_location)
            
        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.score, self._score_to_win
            )

    @override
    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.score)

        bs.timer(0.23, lambda: self.end(results=results))

    

