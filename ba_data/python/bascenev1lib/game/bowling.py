# To learn more, see https://ballistica.net/wiki/meta-tag-system
# ba_meta require api 9

from __future__ import annotations

from typing import TYPE_CHECKING

import babase # type: ignore
import bascenev1 as bs # type: ignore
from bascenev1lib.actor.playerspaz import PlayerSpaz # type: ignore
from bascenev1lib.actor.scoreboard import Scoreboard # type: ignore
from bascenev1lib.game.elimination import Icon # type: ignore
from bascenev1lib.actor.spazbot import ( # type: ignore
	SpazBotDiedMessage,
	SpazBotSet,
	SpazBot,
	)


if TYPE_CHECKING:
	from typing import Any, Sequence

class BowlingPin(SpazBot):
    
    character = 'Spaz'
    color = (1, 1, 1)
    highlight = (1, 0, 0)
    punchiness = 0
    throwiness = 0
    default_bomb_count = 0
    run = False
    static = True
    charge_speed_max = 0
    charge_speed_min = 0

    def __init__(self) -> None:
        super().__init__()
        self.impact_scale = 1.3

class Player(bs.Player['Team']):
	"""Our player type for this game."""
	def __init__(self) -> None:
		self.icons: list[Icon] = []
		self.in_game: bool = False
		self.playervs1: bool = False
		self.playervs2: bool = False


class Team(bs.Team[Player]):
	"""Our team type for this game."""
	def __init__(self) -> None:
		self.score = 0


# ba_meta export bascenev1.GameActivity
class BowlingGame(bs.TeamGameActivity[Player, Team]):
	"""A game type based on throwing bombs at 'pins' to knock them down. (the pints are just spazzes)"""

	name = 'Bowling'
	description = 'Knock down the most spazes to win!'

	@classmethod
	def get_available_settings(
			cls, sessiontype: type[bs.Session]) -> list[bs.Setting]:
		settings = [
			bs.IntSetting(
            'Score to Win',
            min_value=6,
            default=18,
            increment=6,
        ),
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
		return issubclass(sessiontype, bs.DualTeamSession) or issubclass(
            sessiontype, bs.FreeForAllSession
        )

	@classmethod
	def get_supported_maps(cls, sessiontype: type[bs.Session]) -> bool:
		return ['Rampage']

	def __init__(self, settings: dict):
		super().__init__(settings)
		self._scoreboard = Scoreboard()
		self._score_to_win: int | None = None
		self._vs_text: bs.Actor | None = None
		self.spawn_order: list[Player] = []
		self._dingsound = bs.getsound('dingSmall')
		self._time_limit = 0
		self._allow_negative_scores = False
		self._players_vs_1: bool = False
		self._players_vs_2: bool = False
		self._count_1 = bs.getsound('announceOne')
		self._count_2 = bs.getsound('announceTwo')
		self._count_3 = bs.getsound('announceThree')
		self._boxing_bell = bs.getsound('boxingBell')
		self._heart_tex = bs.gettexture('heart')
		self._heart_mesh_opaque = bs.getmesh('heartOpaque')
		self._heart_mesh_transparent = bs.getmesh('heartTransparent')
		self._epic_mode = False
		self._kills_to_win_per_player = int(
			settings['Score to Win'])
		self._enable_powerups = False
		self._boxing_gloves = False
		self._bots = SpazBotSet()
		self.already = False

		# Base class overrides.
		self.slow_motion = self._epic_mode
		self.default_music = bs.MusicType.BOWLING # bs.MusicType.FORWARD_MARCH <-- Vanilla Port.
	def get_instance_description(self) -> str | Sequence:
		return 'Knock down ${ARG1} Spazes with bombs!', self._score_to_win

	def get_instance_description_short(self) -> str | Sequence:
		return 'Knock down ${ARG1} Spazes.', self._score_to_win

	def on_player_join(self, player: Player) -> None:
		self.spawn_order.append(player)
		self._update_order()

	def on_player_leave(self, player: Player) -> None:
		super().on_player_leave(player)
		player.icons = []
		if player.playervs1:
			player.playervs1 = False
			self._players_vs_1 = False
			player.in_game = False
		elif player.playervs2:
			player.playervs2 = False
			self._players_vs_2 = False
			player.in_game = False
		if player in self.spawn_order:
			self.spawn_order.remove(player)
		self._update_order()

	def on_team_join(self, team: Team) -> None:
		if self.has_begun():
			self._update_scoreboard()

	def on_begin(self) -> None:
		super().on_begin()
		self._timer = 0
		uiscale = bs.app.ui_v1.uiscale
		l_offs = (
            -80
            if uiscale is bs.UIScale.SMALL
            else -40 if uiscale is bs.UIScale.MEDIUM else 0
        )
		self._timer_bg = bs.NodeActor(
            bs.newnode(
                'image',
                attrs={
                    'texture': self._heart_tex,
                    'mesh_opaque': self._heart_mesh_opaque,
                    'mesh_transparent': self._heart_mesh_transparent,
                    'attach': 'topRight',
                    'scale': (60, 60),
                    'position': (-200 + l_offs, -60),
                    'color': (0.4, 1, 1),
                },
            )
        )
		self._timer_text = bs.NodeActor(
            bs.newnode(
                'text',
                attrs={
                    'v_attach': 'top',
                    'h_attach': 'right',
                    'h_align': 'center',
                    'color': (1, 1, 1, 1),
                    'flatness': 1.0,
                    'shadow': 1.0,
                    'vr_depth': 10,
                    'position': (-200 + l_offs, -79),
                    'scale': 1,
                    'text': str(self._timer),
                },
            )
        )
		bs.getactivity().globalsnode.tint = (1.2, 1.2, 1.2)
		self.setup_standard_time_limit(self._time_limit)
		self._vs_text = bs.NodeActor(
		bs.newnode('text',
				   attrs={
					   'position': (0, 105),
					   'h_attach': 'center',
					   'h_align': 'center',
					   'maxwidth': 200,
					   'shadow': 0.5,
					   'vr_depth': 390,
					   'scale': 0.6,
					   'v_attach': 'bottom',
					   'color': (0.8, 0.8, 0.3, 1.0),
					   'text': '',
				   }))

		# Base kills needed to win on the size of the largest team.
		self._score_to_win = (self._kills_to_win_per_player *
							  max(1, max(len(t.players) for t in self.teams)))
		self._update_scoreboard()
		bs.timer(5, self.ihatemyself)
	
	def spawn_bowling_pins(self):

		assert self._bots is not None
		self.already_did_it = False
		self.score = 0
		self._bots.spawn_bot(BowlingPin, pos=(2, 5, -4), spawn_time=1)
		self._bots.spawn_bot(BowlingPin, pos=(3, 5, -3), spawn_time=1.2)
		self._bots.spawn_bot(BowlingPin, pos=(3, 5, -5), spawn_time=1.4)
		self._bots.spawn_bot(BowlingPin, pos=(4, 5, -4), spawn_time=1.6)
		self._bots.spawn_bot(BowlingPin, pos=(4, 5, -5.5), spawn_time=1.8)
		self._bots.spawn_bot(BowlingPin, pos=(4, 5, -2.5), spawn_time=2)
		def change():
			self.allow_new_round = True
		bs.timer(2, change)
	
	def ihatemyself(self):

		def timer():
			self._timer -= 1
			assert self._timer_text is not None
			assert self._timer_text.node
			self._timer_text.node.text = str(self._timer)
			if self._timer == 3:
				bs.getsound('tick').play()
				bs.getsound('timer1').play()
			elif self._timer == 2:
				bs.getsound('tick').play()
				bs.getsound('timer2').play()
			elif self._timer == 1:    
				bs.getsound('tick').play()
				bs.getsound('timer3').play()
			elif self._timer == 0:
				for player in self.players:
					if player.is_alive():
						player.actor.handlemessage(bs.DieMessage())
			else:
				if '-' in str(self._timer):
					self._timer = 0
				else:
					bs.getsound('tick').play()
			
		bs.timer(1, timer, repeat=True)

	def spawn_player(self, player: Player) -> bs.Actor:
		self._timer = 15
		spaz = self.spawn_player_spaz(player, (-3, 5, -3))
		bs.timer(0.1, lambda: self.check_position(player), repeat=True)
		spaz.set_bomb_count(3)
		spaz.impact_scale = 0
		spaz.connect_controls_to_player(
            enable_punch=True, enable_bomb=True, enable_pickup=True, enable_jump=True
            )
		self.delete_pins()
		bs.timer(0.2, self.spawn_bowling_pins)
		return spaz
	
	def check_position(self, player):
		"Check if they arent cheating!"
		if player.is_alive() and player.actor and player.actor.node:
			pos = player.actor.node.position
			
			if pos[0] > 0.4:
				self.push_back(player)

	def push_back(self, player):
		node = player.actor.node
		node.handlemessage(
    	"impulse",
        	node.position[0],  # X position
            node.position[1] + 0.3,  # Y position
            node.position[2],  # Z position
            -55,  # X force (push back)
            0,  # Y force (no vertical push)
            0,  # Z force (no sideways push)
			-55,
            25,
            0,
            0,
            -55,
            0,
           	0,
        )
	def delete_pins(self):
		self._bots.clear()

	def reset_for_next_player(self):
		self.allow_new_round = False
		for player in self.players:
			if player.is_alive():
				if self.score == 6:
					self.show_zoom_message(
                    'STRIKE!',
                    color=player.color,
                )
				self.delete_pins()
				player.actor.handlemessage(bs.DieMessage())

	
	def _update_spawn(self, player: Player) -> None:
		if player.exists():
			if self._players_vs_1:
				if not player.is_alive():
					bs.timer(2.5, lambda: self.spawn_player(player))
			else:
				if not player.is_alive():
					bs.timer(0.2, lambda: self.spawn_player(player))

	def _update_order(self) -> None:
		for player in self.spawn_order:
			assert isinstance(player, Player)
			if not player.is_alive():
				if not self._players_vs_1:
					self._players_vs_1 = True
					player.playervs1 = True
					player.in_game = True
					self.spawn_order.remove(player)
					self._update_spawn(player)
				self._update_icons()

	def _update_icons(self) -> None:
		# pylint: disable=too-many-branches

		for player in self.players:
			player.icons = []

			if player.in_game:
				if player.playervs1:
					xval = -60
					x_offs = -78
				player.icons.append(
					Icon(player,
						 position=(xval, 40),
						 scale=1.0,
						 name_maxwidth=130,
						 name_scale=0.8,
						 flatness=0.0,
						 shadow=0.5,
						 show_death=True,
						 show_lives=False))
			else:
				xval = 125
				xval2 = -125
				x_offs = 78
				for player in self.spawn_order:
					player.icons.append(
						Icon(player,
							 position=(xval2, 25),
							 scale=0.5,
							 name_maxwidth=75,
							 name_scale=1.0,
							 flatness=1.0,
							 shadow=1.0,
							 show_death=False,
							 show_lives=False))
					xval2 -= x_offs * 0.56

	def handlemessage(self, msg: Any) -> Any:

		if isinstance(msg, bs.PlayerDiedMessage):

			# Augment standard behavior.
			super().handlemessage(msg)

			player = msg.getplayer(Player)

			if player.playervs1:
				player.playervs1 = False
				self._players_vs_1 = False
				player.in_game = False
				self.spawn_order.append(player)
			bs.timer(0.1, self._update_order)

			killer = msg.getkillerplayer(Player)
			if killer is None:
				return None

			self._update_scoreboard()

			# If someone has won, set a timer to end shortly.
			# (allows the dust to clear and draws to occur if deaths are
			# close enough)
			assert self._score_to_win is not None
			if any(team.score >= self._score_to_win for team in self.teams):
				bs.timer(0.5, self.end_game)
			
		if isinstance(msg, SpazBotDiedMessage):
			self._dingsound.play()
			self.score += 1
			self._update_scoreboard()
			if any(team.score >= self._score_to_win for team in self.teams):
				bs.timer(0.5, self.end_game)
			killer = msg.killerplayer
			killer.team.score += 1
			for player in self.players:
				if player.is_alive():
					player.actor.connect_controls_to_player(
            enable_punch=False, enable_bomb=False, enable_pickup=False, enable_jump=False
            )
			if self.allow_new_round and not self.already_did_it:
				self.already_did_it = True
				bs.timer(2, self.reset_for_next_player)

		else:
			return super().handlemessage(msg)
		return None

	def _update_scoreboard(self) -> None:
		for team in self.teams:
			self._scoreboard.set_team_value(team, team.score,
											self._score_to_win)

	def end_game(self) -> None:
		results = bs.GameResults()
		for team in self.teams:
			results.set_team_score(team, team.score)
		self.end(results=results)
