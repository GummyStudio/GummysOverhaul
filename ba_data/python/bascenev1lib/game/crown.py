# Released under the MIT License. See LICENSE for details.
#
"""Provides the chosen-one mini-game.

    lol untitled tag game go brrr

    by GUMMYBOYT

    
    also dont mind the comments... i just liked doin' it for some reason....

"""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import logging
import math
import babase
import random
from typing import TYPE_CHECKING

from typing_extensions import override
import bascenev1 as bs

from bascenev1lib.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence


class Player(bs.Player['Team']):
    """Our player type for this game."""

    def __init__(self) -> None:
        self.chosen_light: bs.NodeActor | None = None


class Team(bs.Team[Player]):
    """Our team type for this game."""

    def __init__(self, score: int) -> None:
        self.score = score

class Icon(bs.Actor):
    """Creates in in-game icon on screen."""

    def __init__(
        self,
        player: Player,
        position: tuple[float, float],
        scale: float,
        show_lives: bool = True,
        show_death: bool = True,
        name_scale: float = 1.0,
        name_maxwidth: float = 115.0,
        flatness: float = 1.0,
        shadow: float = 1.0,
    ):
        super().__init__()

        self._player = player
        self._show_lives = show_lives
        self._show_death = show_death
        self._name_scale = name_scale
        self._outline_tex = bs.gettexture('characterIconMask')

        icon = player.get_icon()
        self.node = bs.newnode(
            'image',
            delegate=self,
            attrs={
                'texture': icon['texture'],
                'tint_texture': icon['tint_texture'],
                'tint_color': icon['tint_color'],
                'vr_depth': 400,
                'tint2_color': icon['tint2_color'],
                'mask_texture': self._outline_tex,
                'opacity': 1.0,
                'absolute_scale': True,
                'attach': 'bottomCenter',
            },
        )
        self._name_text = bs.newnode(
            'text',
            owner=self.node,
            attrs={
                'text': bs.Lstr(value=player.getname()),
                'color': bs.safecolor(player.team.color),
                'h_align': 'center',
                'v_align': 'center',
                'vr_depth': 410,
                'maxwidth': name_maxwidth,
                'shadow': shadow,
                'flatness': flatness,
                'h_attach': 'center',
                'v_attach': 'bottom',
            },
        )
        self.set_position_and_scale(position, scale)

    def set_position_and_scale(
        self, position: tuple[float, float], scale: float
    ) -> None:
        """(Re)position the icon."""
        assert self.node
        self.node.position = position
        self.node.scale = [70.0 * scale]
        self._name_text.position = (position[0], position[1] + scale * 52.0)
        self._name_text.scale = 1.0 * scale * self._name_scale


    def handle_player_spawned(self) -> None:
        """Our player spawned; hooray!"""
        if not self.node:
            return
        self.node.opacity = 1.0


    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
            return None
        return super().handlemessage(msg)

# ba_meta export bascenev1.GameActivity
class CrownGame(bs.TeamGameActivity[Player, Team]):
    """
    Game involving trying to remain the the crown bearer and win when time runs out.
    """

    name = 'Crowned'
    description = (
        'Grab and keep your crown from the peasents!\n'
        'Last player with the crown when time ends wins.'
    )
    available_settings = [
        bs.IntChoiceSetting(
            'Time Limit',
            choices=[
                ('1 Minute', 60),
                ('2 Minutes', 120),
                ('5 Minutes', 300),
            ],
            default=120,
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

    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        assert bs.app.classic is not None
        return ['Bridgit', 'Rampage', 'Monkey Face', 'Happy Thoughts', 'Doom Shroom', 'Courtyard', 'Nintendo DS']

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._chosen_one_player: Player | None = None
        self._swipsound = bs.getsound('swip')
        self._epic_mode = False
        self._chosen_one_time = 300
        self._crownsounds = {
            1: bs.getsound('crown01'),
            2: bs.getsound('crown02'),
            3: bs.getsound('crown03'),
        }
        self._countdownsounds = {
            10: bs.getsound('announceTen'),
            9: bs.getsound('announceNine'),
            8: bs.getsound('announceEight'),
            7: bs.getsound('announceSeven'),
            6: bs.getsound('announceSix'),
            5: bs.getsound('announceFive'),
            4: bs.getsound('announceFour'),
            3: bs.getsound('announceThree'),
            2: bs.getsound('announceTwo'),
            1: bs.getsound('announceOne'),
        }
        self._time_limit = float(settings['Time Limit'])

        # Base class overrides
        self.slow_motion = self._epic_mode
        self.default_music = bs.MusicType.CROWN

    @override
    def get_instance_description(self) -> str | Sequence:
        return 'Keep the crown when time runs out!'
    
    def get_instance_description_short(self) -> str | Sequence:
        return 'Keep the crown when time runs out!'

    @override
    def create_team(self, sessionteam: bs.SessionTeam) -> Team:
        return Team(score=0)


    @override
    def on_player_leave(self, player: Player) -> None:
        super().on_player_leave(player)
       
        # If the crown bearer leaves, pick a new one.
        if self._get_crown_bearer() is player:
            self._set_crown_bearer(None)
            self.pick_new_crown_bearer()
        
        self.update_icon()


    @override
    def on_begin(self) -> None:
        super().on_begin()
        shared = SharedObjects.get()
        self.setup_standard_time_limit(0)
        self.setup_standard_powerup_drops()
        bs.timer(0.01, self.tick, repeat=True)
        bs.newnode('text',
				   attrs={
					   'position': (0, 80),
					   'h_attach': 'center',
					   'h_align': 'center',
					   'maxwidth': 200,
					   'shadow': 2,
					   'vr_depth': 390,
					   'scale': 2,
					   'v_attach': 'bottom',
					   'color': (1, 1, 0, 1.0),
					   'text': babase.charstr(babase.SpecialChar.CROWN)
				   })
        self._timer = self._time_limit
        self._timer_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'center',
                    'h_align': 'center',
                    'color': (0.85, 0.85, 0.85, 1),
                    'flatness': 1.0,
                    'shadow': 3,
                    'vr_depth': 10,
                    'position': (0, -79),
                    'scale': 1,
                    'text': str(math.ceil(self._timer)),
                },
            )
        )
        bs.timer(1, lambda: self.timer(), repeat=True)
    
    def timer(self):
            if not self._timer == 0:
                self._timer -= 1
            self.update_timer()
            if self._timer == 10 or self._timer == 9 or self._timer == 8 or self._timer == 7 or self._timer == 6 or self._timer == 5 or self._timer == 4 or self._timer == 3 or self._timer == 2 or self._timer == 1:   
                bs.getsound('tick').play()
                self._timer_text.node.scale = 2
                self.timer_flash()
                self._countdownsounds[self._timer].play()
            elif self._timer == 0:
                bs.timer(0.1, self.end_game)
    
    def update_timer(self):
            assert self._timer_text is not None
            assert self._timer_text.node
            self._timer_text.node.text = str(math.ceil(self._timer))
    
    def timer_flash(self):
            assert self._timer_text is not None
            assert self._timer_text.node

            def flash():
                self._timer_text.node.color = (1, 1, 0, 1)
            def flash2():
                self._timer_text.node.color = (1, 1, 0.5, 1)

            timer = 0.05
            for i in range(10):
                bs.timer(timer, flash2)
                bs.timer(timer + 0.05, flash)
                timer += 0.05
                
    

    def del_icon(self):
        if self.crown_icon:
            self.crown_icon.delete()  # Properly remove the icon
            self.crown_icon = None  # Reset reference

    def update_icon(self):
        crown_bearer = self._get_crown_bearer()
        self.crown_icon = None

        if crown_bearer:
            # If icon exists, update it
            if self.crown_icon:
                return
            else:
                # Create a new icon if it doesn't exist
                self.crown_icon = Icon(
                crown_bearer,
                position=(0, 40),
                scale=1.0,
                name_maxwidth=130,
                name_scale=0.8,
                flatness=0.0,
                shadow=0.5,
                show_death=True,
                show_lives=False
                        )
        else:
           self.del_icon()


    def pick_new_crown_bearer(self) -> None:
        # Pick a random alive player to become the crown bearer.
        curplayers = []
        for player in self.players:
            if player.is_alive():
                curplayers += [player]
            
            # If there are no alive players, or none existing, set the crown bearer to None.
            if len(curplayers) == 0:
                self._set_crown_bearer(None)
                
            else:
                self._set_crown_bearer(random.choice(curplayers))

        
    def _get_crown_bearer(self) -> Player | None:
        # Should never return invalid references; return None in that case.
        if self._chosen_one_player:
            return self._chosen_one_player
        return None
    
    @override
    def spawn_player(self, player: Player) -> bs.Actor:
        actor = self.spawn_player_spaz(player)

        # What the hell! No crown bearer? Guess we're it!
        if self._get_crown_bearer() == None:
            self._set_crown_bearer(player)
        
        return actor


    def tick(self) -> None:
        for player in self.players:
            crown_bearer = player == self._get_crown_bearer()
            if crown_bearer and (player.is_alive()):
                player.team.score = 1
            else:
                player.team.score = 0
            
            # wait... we're the crown bearer, but we're dead?
            # Nonono... we must forfeit our crown! 
            # (Prevents people glitching themselves dead with the crown, especially with long respawn times)
            if crown_bearer and not player.is_alive():
                self.pick_new_crown_bearer()
                # if an icon still exists if no players are alive....
                # remove it.
                # Or just update it i dunno
                self.update_icon()
            
            # Alright, after all those checks we are verified the crown bearer.
            # Let's slow down our crown bearer to make it an easy target.
            if crown_bearer:
                if player.actor:
                    player.actor.speed_mult = 0.662
                    player.actor.node.color = (1, 1, 0)
                    # Show a crown over their head
                    if isinstance(player.actor, PlayerSpaz) and player.actor:
                        player.actor.set_score_text(
                            babase.charstr(babase.SpecialChar.CROWN)
                        )
            else:
                if player.actor:
                    player.actor.speed_mult = 1.0
                    player.actor.node.color = (0.4, 0, 0)
            


    @override
    def end_game(self) -> None:
        results = bs.GameResults()
        for team in self.teams:
            results.set_team_score(
                team, team.score
            )

        # Ties happen when there is no crown bearer. Hence everyone having the same score.
        self.end(results=results, announce_delay=0)

    def _set_crown_bearer(self, player: Player | None) -> None:
        # If the game has ended, we don't want to set a new crown bearer. The winner wants to know they did it!
        if self.has_ended():
            return
        existing = self._get_crown_bearer()
        self._chosen_one_player = None
        if existing:
            existing.chosen_light = None
        self._swipsound.play()
        if not player == None:
            if player.actor:
                self._chosen_one_player = player
                self._crownsounds[random.randint(1, 3)].play()

                light = player.chosen_light = bs.NodeActor(
                    bs.newnode(
                        'light',
                        attrs={
                            'intensity': 0.6,
                            'height_attenuated': False,
                            'volume_intensity_scale': 0.1,
                            'radius': 0.13,
                            'color': (1, 1, 0),
                        },
                    )
                )
                

                assert light.node
                bs.animate(
                    light.node,
                    'intensity',
                    {0: 1.0, 0.2: 0.4, 0.4: 1.0},
                    loop=True,
                )
                assert isinstance(player.actor, PlayerSpaz)
                player.actor.node.connectattr(
                    'position', light.node, 'position'
                )
                self.update_icon()
    
    def decrease_timer(self, alot: bool = False):
        if alot:
            self._timer = math.ceil(self._timer / 1.162329)
        else:
            self._timer = math.ceil(self._timer / 1.1)
        self.update_timer()
    
    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            # Augment standard behavior.
            super().handlemessage(msg)
            player = msg.getplayer(Player)
            crown = player is self._get_crown_bearer()
            
            killer = msg.getkillerplayer(Player)
            if killer.team is player.team:
                if crown:
                    # Aw damn. We died with the crown. Lets give it to a new player!
                    bs.timer(0.1, lambda: self.pick_new_crown_bearer())
            else:
                if crown:
                    # Get the killer a crown if we have it.
                    self._set_crown_bearer(killer)
            
            if crown:
                # if we had the crown, lets decrease the timer.
                self.decrease_timer(alot=True)

            self.respawn_player(player)

        elif isinstance(msg, PlayerSpazHurtMessage):
            super().handlemessage(msg)
            caller = msg.spaz
        
            victim = caller._player
            attacker = caller.last_player_attacked_by

            # Make sure the attacker exists.
            if attacker is None:
                return
            
            # if we're hurting ourselves, lets not give the crown to ourselves.
            if victim == attacker:
                return
            
            # Check if we're the current crown bearer.
            if victim == self._get_crown_bearer():
                if not victim.actor.shield: # Also... lets NOT give them the crown if we're shielded.
                    if attacker.is_alive(): # Make sure our attacker is alive
                        self._set_crown_bearer(attacker) # Give the crown to the attacker.
                        self.decrease_timer(alot=False) # Decrease the timer.
                    else:
                        return # Give it to noone.

        else:
            super().handlemessage(msg)

