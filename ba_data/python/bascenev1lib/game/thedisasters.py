# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

import bascenev1 as bs

from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from gummyoverhaul.disasters import (
    Disaster
)

import random

if TYPE_CHECKING:
    from typing import Any, Sequence


class Player(bs.Player['Team']):
    """Our player type for this game."""


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self) -> None:
        self.disasters_survived = 0






# ba_meta export bascenev1.GameActivity
class DisasterGame(bs.TeamGameActivity[Player, Team]):
    """A game type based on acquiring kills."""

    name = 'The Disasters'
    description = 'Survive the disasters!'

    # Print messages when players die since it matters here.
    announce_player_deaths = True

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
            bs.IntSetting(
                'Points to win',
                min_value=5,
                default=15,
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
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        assert bs.app.classic is not None
        return bs.app.classic.getmaps('melee')

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._score_to_win: int | None = None
        self._dingsound = bs.getsound('dingSmall')
        self._kills_to_win_per_player = int(settings['Points to win'])
        self._time_limit = float(settings['Time Limit'])
        self._allow_negative_scores = bool(
            settings.get('Allow Negative Scores', False)
        )

        self._active_disasters: list[Disaster] = []
        self._current_disaster_points = 0
        self._max_disaster_points = 6
        
        # Tracks players who have not died during each active disaster
        self._disaster_survivors: dict[Disaster, set[Player]] = {}

        self.default_music = (
            bs.MusicType.DISASTER
        )

    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return 'Survive ${ARG1} disasters.', self._score_to_win

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return 'survive ${ARG1} disasters', self._score_to_win

    @override
    def on_team_join(self, team: Team) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        if self.has_begun():
            self._update_scoreboard()

    @override
    def on_begin(self) -> None:
        super().on_begin()

        self.setup_standard_powerup_drops()
        self.setup_standard_time_limit(self._time_limit)
  

        # Base kills needed to win on the size of the largest team.
        self._score_to_win = self._kills_to_win_per_player
        self._update_scoreboard()

        bs.timer(4.0, self._begin_disaster_cycle)

    def _begin_disaster_cycle(self):
        # Start first disaster
        self._start_disaster()

    def _start_disaster(self):

        from gummyoverhaul.disasters import (
            PowerupRainDisaster,
            EarthquakeDisaster,
            MeteorShowerDisaster,
            LightningStormDisaster,
            SpazJumpScareDisaster,
            FirestormDisaster
        )

        disasters: list[Disaster] = [         
            PowerupRainDisaster,
            EarthquakeDisaster,
            MeteorShowerDisaster,
            LightningStormDisaster,
            SpazJumpScareDisaster,
            FirestormDisaster
        ]
        # Filter disasters that still fit into point budget
        candidates = []
        for dcls in disasters:
            pts = dcls.intensity
            if self._current_disaster_points + pts <= self._max_disaster_points:
                candidates.append(dcls)

        # No room right now; try again shortly
        if not candidates:
            bs.timer(3.0, self._start_disaster)
            return

        disaster_class = random.choice(candidates)
        disaster = disaster_class()
        assert isinstance(disaster, Disaster)

        pts = disaster.intensity
        self._current_disaster_points += pts
        self._active_disasters.append(disaster)

        # Track players who have not died during this specific disaster
        survivors = set()
        for team in self.teams:
            for player in team.players:
                if player.is_alive():
                    survivors.add(player)
        self._disaster_survivors[disaster] = survivors

        name = disaster.name
        bs.broadcastmessage(f"Disaster Incoming: {name}")

        disaster.activate()

        duration = disaster.timelapse

        bs.timer(duration, lambda: self._end_disaster(disaster))
        bs.timer(duration*(random.uniform(0.67, 1.5)), self._start_disaster)

    def _end_disaster(self, disaster: Disaster):
        if disaster is None:
            return

        try:
            disaster.stop()
        except Exception as e:
            print('Unable to stop disaster')
            return

        bs.broadcastmessage(f"{disaster.name} ended!")

        # Remove from active list + refund points
        if disaster in self._active_disasters:
            self._active_disasters.remove(disaster)
            self._current_disaster_points -= getattr(disaster, "intensity", 1)
            if self._current_disaster_points < 0:
                self._current_disaster_points = 0

        survivors = self._disaster_survivors.get(disaster, set())

        rewarded_any = False
        for team in self.teams:
            if any(p in survivors for p in team.players):
                team.disasters_survived += 1
                rewarded_any = True

        if rewarded_any:
            self._dingsound.play()
            self._update_scoreboard()

        # Cleanup tracking data
        if disaster in self._disaster_survivors:
            del self._disaster_survivors[disaster]

        # Win check
        if any(team.disasters_survived >= self._score_to_win for team in self.teams):
            bs.timer(1.0, self.end_game)
            return

  

    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)

            player = msg.getplayer(Player)
            self.respawn_player(player)

            # Player died -> they are no longer a perfect survivor for ANY active disaster
            for d, survivors in list(self._disaster_survivors.items()):
                if player in survivors:
                    survivors.remove(player)

            killer = msg.getkillerplayer(Player)
            if killer is None:
                return None

       

            self._update_scoreboard()

            
            if any(team.disasters_survived >= self._score_to_win for team in self.teams):
                bs.timer(0.5, self.end_game)

        else:
            return super().handlemessage(msg)
        return None

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, team.disasters_survived, self._score_to_win
            )

    @override
    def end_game(self) -> None:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(team, team.disasters_survived)
        self.end(results=results)

