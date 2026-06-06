# To learn more, see https://ballistica.net/wiki/meta-tag-system
# ba_meta require api 9

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence, override

import babase
import bascenev1 as bs
import random
from bascenev1lib.actor.spazfactory import SpazFactory
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.game.elimination import EliminationGame, Icon, Player
from bascenev1lib.game.deathmatch import DeathMatchGame
from bascenev1lib.actor.bomb import Bomb, Blast
from bascenev1lib.actor.playerspaz import PlayerSpaz, PlayerSpazHurtMessage

if TYPE_CHECKING:
	from typing import Any, Sequence


class ModLang:
	lang = babase.app.lang.language
	if lang == 'Spanish':
		description = (
			'Golpea a todos fuera del mapa.\n'
			'El último en sobrevivir gana.'
		)
		descriptionshort = 'El último en sobrevivir gana.'
		descriptiondm = (
			'Golpea a todos fuera del mapa.\n'
			'Mata a enemigos para ganar.'
		)
		lives = 'Vidas (0 = Ilimitadas)'
		boxing_gloves = 'Guantes de Boxeo'
		ice_explosion = 'Explosion de Hielo'
		enable_powerups = 'Habilitar Potenciadores'
	elif lang == 'Chinese':
		description = (
			'击中所有人。\n'
			'最后一个胜利的人。'
		)
		descriptionshort = '最后一个胜利的人。'
		descriptiondm = (
			'击中所有人。\n'
			'杀死敌人以获胜。'
		)
		lives = '生活 (0 = 无限)'
		boxing_gloves = '拳击手套'
		ice_explosion = '冰爆炸'
		enable_powerups = '启用电位'
	elif lang == 'Portuguese':
		description = (
			'Atinge todos fora do mapa.\n'
			'O último a sobreviver a vitórias.'
		)
		descriptionshort = 'O último a sobreviver a vitórias.'
		descriptiondm = (
			'Atinge todos fora do mapa.\n'
			'Mate os inimigos para vencer.'
		)
		lives = 'Vidas (0 = ilimitado)'
		boxing_gloves = 'Luvas de boxe'
		ice_explosion = 'Explosão de gelo'
		enable_powerups = 'Ativar potenciais'
	elif lang == 'French':
		description = (
			'Fait tout le monde hors de la carte.\n'
			'Le dernier à survivre gagne.'
		)
		descriptionshort = 'Le dernier à survivre gagne.'
		descriptiondm = (
			'Fait tout le monde hors de la carte.\n'
			'Tuez les ennemis pour gagner.'
		)
		lives = 'Lives (0 = illimité)'
		boxing_gloves = 'Gants de boxe'
		ice_explosion = 'Explosion de glace'
		enable_powerups = 'Activer les potentiaires'
	elif lang == 'Russian':
		description = (
			'Ударяет всех из карты.\n'
			'Последний, чтобы выжить, победа.'
		)
		descriptionshort = 'Последний, чтобы выжить, победа.'
		descriptiondm = (
			'Ударяет всех из карты.\n'
			'Убейте врагов, чтобы победить.'
		)
		lives = 'Жизнь (0 = неограниченный)'
		boxing_gloves = 'Боксерские перчатки'
		ice_explosion = 'Ледяной взрыв'
		enable_powerups = 'Включить потенциар'
	else:
		description = (
			'Hits everyone out of the map.\n'
			'The last to survive wins.'
		)
		descriptionshort = 'The last to survive wins.'
		descriptiondm = (
			'Hits everyone out of the map.\n'
			'Kill enemies to win.'
		)
		lives = 'Lives (0 = Unlimited)'
		boxing_gloves = 'Boxing Gloves'
		ice_explosion = 'Ice Explosion'
		enable_powerups = 'Enable Power-ups'


class NewIcon(Icon):
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
		unlimited: bool = False,
	):
		self.animating_text = False
		self.animate_it = False
		super().__init__(
			player=player,
			position=position,
			scale=scale,
			show_lives=show_lives,
			show_death=show_death,
			name_scale=name_scale,
			name_maxwidth=name_maxwidth,
			flatness=flatness,
			shadow=shadow,
		)
		self.unlimited = unlimited
		
		self._bg = bs.newnode(
			'image',
			owner=self.node,
			attrs={
				'texture': bs.gettexture('logo'),
				'color': player.color,
				'opacity': 0.6,
				'scale': (200, 200),
				'attach': 'bottomCenter',
			}
		)
		self._percent_text = bs.newnode(
			'text',
			owner=self.node,
			attrs={
				'text': '0%', 
				'in_world': False,
				'color': (1, 1, 1, 1),
				'shadow': 1.2,
				'flatness': 0.7,
				'h_align': 'center',
				'v_align': 'center',
				'scale': 0.6,
				'h_attach': 'center',
				'v_attach': 'bottom',
			}
		)
	
	def set_position_and_scale(
        self, position: tuple[float, float], scale: float
    ) -> None:
		"""(Re)position the icon."""
		super().set_position_and_scale(position=position, scale=scale)
		try:

			# Move percent text above the icon
			if not self.animating_text:
				self._percent_text.position = (
					self.node.position[0] + 55,
					self.node.position[1]
				)
			self._percent_text.scale = scale
			# Move background to match node
			self._bg.position = (
				self.node.position[0] + 65,
				self.node.position[1] + 12
			)
			
			self._bg.scale = (scale * 70.5, scale * 70.5)
			self._name_text.position = (self._name_text.position[0]+25,self._name_text.position[1])
		except AttributeError:
			pass
			

		
	def set_percent(self, percent: int):
		if not self._percent_text:
			return
		self._percent_text.text = f"{percent}%"
		if percent < 100:
			color = (1, 1, 0, 1)
		elif percent < 200:
			color = (1, 0.6, 0, 1)
		else:
			color = (1, 0, 0, 1)
		self._percent_text.color = (1,1,1)
		bs.timer(0.12, lambda: setattr(self._percent_text, 'color', color))


		pos = self._percent_text.position 

		jiggle_x = random.uniform(-1.7, 1.7)
		jiggle_y = random.uniform(-1.7, 1.7)

		# Animate the text position for a jiggle effect
		bs.animate_array(self._percent_text, 'position', 2, {
			0.0: (pos[0] + jiggle_x, pos[1] + jiggle_y),
			0.1: (pos[0] - jiggle_x, pos[1] - jiggle_y),
			0.2: (pos[0] + jiggle_x * 0.5, pos[1] + jiggle_y * 0.5),
			0.3: pos
		})
	
	def handle_player_spawned(self) -> None:
		"""Our player spawned; hooray!"""
		super().handle_player_spawned()

		
		if self.animate_it:
			self.animate_it = False
			self.animating_text = True
			time = 1
			self._percent_text.color = (1,1,0)
			self._percent_text.text = '0%'
			bs.animate_array(self._percent_text, 'position', 2,
					{   
						0.0: (self._percent_text.position[0], self._percent_text.position[1]-66),
						time: (self._percent_text.position[0],self._percent_text.position[1]),
					}
				)
			bs.timer(time, lambda: setattr(self, 'animating_text', False))
		

      
      
	def handle_player_died(self) -> None:
		"""Well poo; our player died."""
		self.animate_it = True
		super().handle_player_died()
		

		self._percent_text.color = (1,1,1)
		bs.timer(0.3, lambda: setattr(self._percent_text, 'text', ''))

		

	def update_for_lives(self) -> None:
		"""Update for the target player's current lives."""
		
		
		if self._player:
			try:
				lives = self._player.lives
			except:
				lives = 1
		else:
			lives = 0

		if self._show_lives:
			if lives > 0:
				self._lives_text.text = 'x' + str(lives - 1)
			else:
				self._lives_text.text = ''
		if lives == 0:
			if not self.unlimited:
				self._percent_text.opacity = 1.0
				self._name_text.opacity = 0.2
				assert self.node
				self.node.color = (0.7, 0.3, 0.3)
				self.node.opacity = 0.2
				self.die = bs.newnode(
					'image',
					delegate=self,
					attrs={
						'texture': bs.gettexture('crossOut'),
						'position': self.node.position,
						'vr_depth': 400,
						'scale': self.node.scale,
						'opacity': 1.0,
						'absolute_scale': True,
						'attach': 'bottomCenter',
					},
				)
				


class PowBoxDieMessage:
    def __init__(self, pow: PowBox):
        self.pow = pow


class PowBox(Bomb):

	def __init__(
		self,
		position: Sequence[float] = (0.0, 1.0, 0.0),
		velocity: Sequence[float] = (0.0, 0.0, 0.0),
	) -> None:
		Bomb.__init__(
			self,
			position,
			velocity,
			bomb_type='tnt',
			blast_radius=2.5,
			source_player=None,
			owner=None,
		)
		self.set_pow_text()

	def set_pow_text(self) -> None:
		m = bs.newnode(
			'math',
			owner=self.node,
			attrs={
				'input1': (0, 0.7, 0),
				'operation': 'add',
			},
		)
		self.node.connectattr('position', m, 'input2')
		self._pow_text = bs.newnode(
			'text',
			owner=self.node,
			attrs={
				'text':'POW!',
				'in_world': True,
				'shadow': 1.0,
				'flatness': 1.0,
				'color': (1, 1, 0.4),
				'scale':0.0,
				'h_align':'center',
			},
		)
		m.connectattr('output', self._pow_text, 'position')
		bs.animate(self._pow_text, 'scale', {0: 0.0, 1.0: 0.01})

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, bs.PickedUpMessage):
			self._heldBy = msg.node
		elif isinstance(msg, bs.DroppedMessage):
			if not self.node:
				return
			bs.timer(0.05, lambda:
				bs.animate(self._pow_text, 'scale', {0: 0.01, 0.6: 0.03})
			)
			bs.timer(0.6, self.explode)
		elif isinstance(msg, bs.DieMessage):
			self.node.delete()
			activity = self._activity()
			if activity and not msg.immediate:
				activity.handlemessage(PowBoxDieMessage(self))
		else:
			super().handlemessage(msg)


class SSPlayerSpaz(PlayerSpaz):
	
	def __init__(
		self,
		player: bs.Player,
		color: Sequence[float] = (1.0, 1.0, 1.0),
		highlight: Sequence[float] = (0.5, 0.5, 0.5),
		character: str = 'Spaz',
		cosmetic: str = None,
		powerups_expire: bool = True,
		ice_explosion: bool = True,
	):
		super().__init__(
			player=player,
			color=color,
			highlight=highlight,
			character=character,
			cosmetic=cosmetic,
			powerups_expire=powerups_expire)
		
		self.multiplier = 1
		self.ice_explosion = ice_explosion
		#self._pickup_cooldown = (0.8) * 1000
		self._percent_text_node = None
		bs.timer(0.1, self._create_percent_text_node)

	def _create_percent_text_node(self):
		""" Create the percent display text node above the Spaz's head. """
		if not self.node or self._percent_text_node is not None:
			return
		math_node = bs.newnode(
			'math',
			owner=None,
			attrs={
				'input1': (0, 1.6, 0),
				'operation': 'add',
			},
		)
		self.node.connectattr('position', math_node, 'input2')
		self._percent_text_node = bs.newnode(
			'text',
			owner=None,
			attrs={
				'text': '0%',
				'in_world': True,
				'shadow': 1.3,
				'flatness': 0.7,
				'color': (1, 1, 0, 1),
				'scale': 0.015,
				'h_align': 'center',
				'v_align': 'center'
			},
		)
		math_node.connectattr('output', self._percent_text_node, 'position')
		self.update_percent_display()

	def update_percent_display(self):
		# Updates the percent display above the Spaz's head.
		if self._percent_text_node is None:
			return
		percent = int((self.multiplier - 1) * 100)
		self._percent_text_node.text = f"{percent}%"
		# Color changes as percent increases.
		if percent < 100:
			color = (1, 1, 0, 1)
		elif percent < 200:
			color = (1, 0.6, 0, 1)
		else:
			color = (1, 0, 0, 1)
		self._percent_text_node.color=(1,1,1)
		bs.timer(0.12, lambda: setattr(self._percent_text_node, 'color', color))

		

	def oob_effect(self) -> None:
		if not self.is_alive():
			return
		bs.getsound('smashDied').play()
		if self.ice_explosion:
			if self.multiplier > 1.25:
				blast_type = 'tnt'
				blast_radius = min(self.multiplier * 5, 20)
			else:
				# penalty for killing people with low multiplier
				blast_type = 'ice'
				blast_radius = 7.5
		else:
			blast_type = 'tnt'
			blast_radius = min(self.multiplier * 5, 20)
		Blast(
			position=self.node.position,
			blast_radius=blast_radius,
			blast_type=blast_type,
		).autoretain()
		 

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, bs.HitMessage):
			source_player = msg.get_source_player(type(self._player))
			if source_player:
				self.last_player_attacked_by = source_player
				self.last_attacked_time = babase.apptime()
				self.last_attacked_type = (msg.hit_type, msg.hit_subtype)
		
			if not self.node:
				return None
			if self.node.invincible:
				SpazFactory.get().block_sound.play(
					1.0,
					position=self.node.position,
				)
				return True

			# If we were recently hit, don't count this as another.
			# (so punch flurries and bomb pileups essentially count as 1 hit)
			local_time = int(bs.time() * 1000.0)
			assert isinstance(local_time, int)
			if (
				self._last_hit_time is None
				or local_time - self._last_hit_time > 1000
			):
				self._num_times_hit += 1
				self._last_hit_time = local_time

			multi_calc = (self.multiplier - 1) * 100
			base_knockback = 0.01
			scaling = 0.0025                # how steeply it rises

			multi = base_knockback + (multi_calc ** 1.35) * scaling
			
			# Cap extremely high knockback to prevent runaway / inf
			if multi > 30:
				# Scale it down smoothly
				factor = 20 / multi
				multi *= factor

			multi = max(0.001, multi)
			impulse_scale = multi

			mag = msg.magnitude * self.impact_scale
			velocity_mag = msg.velocity_magnitude * self.impact_scale
			damage_scale = 0.22
			

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

				# Its a cleaner event if a hit just kills the shield
				# without damaging the player.
				# However, massive damage events should still be able to
				# damage the player. This hopefully gives us a happy medium.
				max_spillover = SpazFactory.get().max_shield_spillover_damage
				if self.shield_hitpoints <= 0:
					# FIXME: Transition out perhaps?
					self.shield.delete()
					self.shield = None
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

				else:
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
				# another, but knockback
				self.node.handlemessage(
                        'impulse',
                        msg.pos[0],
                        msg.pos[1],
                        msg.pos[2],
                        msg.velocity[0],
                        msg.velocity[1],
                        msg.velocity[2],
                        mag * impulse_scale,
                        velocity_mag * impulse_scale,
                        msg.radius,
                        0,
                        msg.force_direction[0],
                        msg.force_direction[1],
                        msg.force_direction[2],
                    )

				
			self.node.handlemessage('hurt_sound')

			# Play punch impact sound based on damage if it was a punch.
			if msg.hit_type == 'punch':
				self.on_punched(damage)

				# If damage was significant, lets show it.
				# if damage >= 350:
				#     assert msg.force_direction is not None
				#     bs.show_damage_count(
				#         '-' + str(int(damage / 10)) + '%',
				#         msg.pos,
				#         msg.force_direction,
				#     )

				# Let's always add in a super-punch sound with boxing
				# gloves just to differentiate them.
				if msg.hit_subtype == 'super_punch':
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
			if self.hitpoints > 0:
				# It's kinda crappy to die from impacts, so lets reduce
				# impact damage by a reasonable amount *if* it'll keep us alive
				if msg.hit_type == 'impact' and damage > self.hitpoints:
					# Drop damage to whatever puts us at 10 hit points,
					# or 200 less than it used to be whichever is greater
					# (so it *can* still kill us if its high enough)
					newdamage = max(damage - 200, self.hitpoints - 10)
					damage = newdamage
				self.node.handlemessage('flash')

				# If we're holding something, drop it.
				if damage > 0.0 and self.node.hold_node:
					self.node.hold_node = None
			
				# self.hitpoints -= damage
				# self.node.hurt = (
				#     1.0 - float(self.hitpoints) / self.hitpoints_max
				# )
				damage /= 1.45
				if msg.hit_type == 'punch':
					damage /= 1.45
				self.multiplier += min(damage / 2000, 0.25)
				if damage/2000 > 0.05:
					self.multiplier += min(damage / 2000, 0.25)
				self.update_percent_display()
				if self.source_player:
					for icon in self._player.icons:
						icon.set_percent(int((self.multiplier - 1) * 100))

				# If we're cursed, *any* damage blows us up.
				if self._cursed and damage > 0:
					bs.timer(
						0.05,
						bs.WeakCall(
							self.curse_explode, msg.get_source_player(bs.Player)
						),
					)
			
				# If we're frozen, shatter.. otherwise die if we hit zero
				# if self.frozen and (damage > 200 or self.hitpoints <= 0):
				#     self.shatter()
				# elif self.hitpoints <= 0:
				#     self.node.handlemessage(
				#         bs.DieMessage(how=bs.DeathType.IMPACT)
				#     )

			# If we're dead, take a look at the smoothed damage value
			# (which gives us a smoothed average of recent damage) and shatter
			# us if its grown high enough.
			# if self.hitpoints <= 0:
			#     damage_avg = self.node.damage_smoothed * damage_scale
			#     if damage_avg >= 1000:
			#         self.shatter()

			activity = self._activity()
			if activity is not None and self._player.exists():
				activity.handlemessage(PlayerSpazHurtMessage(self))
			
			
			activity = self.getactivity()
			if activity and self.last_player_attacked_by and msg.hit_type in ['punch', 'explosion'] and self.is_alive():

				bounds = activity.map.defs.boxes['map_bounds']
				cx, cy, cz, nx, ny, nz, sx, sy, sz = bounds

				# Half-size
				hx = sx * 0.5
				hy = sy * 0.5
				hz = sz * 0.5

				# Real edges
				min_x = cx - hx
				max_x = cx + hx
				min_y = cy - hy
				max_y = cy + hy
				min_z = cz - hz
				max_z = cz + hz

				# Predict knockback position
				pos = self.node.position
				vel = self.node.velocity

				dt = 2.85  # future prediction window
				pred_x = pos[0] + vel[0] * dt 
				pred_y = pos[1] + vel[1] * dt * 0.5
				pred_z = pos[2] + vel[2] * dt

				# True OOB detection
				will_fall_oob = (
					pred_x < min_x or pred_x > max_x or
					pred_y < min_y or pred_y > max_y or
					pred_z < min_z or pred_z > max_z
				)
				if isinstance(activity, SuperSmash):

					# Only trigger on last stock
					if self.source_player.lives == 1 and will_fall_oob:

						alive_players = [
							p for p in activity.players
							if p.lives == 1
						]

						# If only 2 players left, this KO ends the match
						# I dont wanna bother with teams
						if len(alive_players) == 2:
							activity.final_hit()

				elif isinstance(activity, SuperSmashDM):

					# Will this KO give the attacker the winning kill?
					if self.last_player_attacked_by.team.score + 1 == activity._score_to_win:

						if will_fall_oob:
							activity.final_hit()

			activity = None

		elif isinstance(msg, bs.DieMessage):
			self.oob_effect()
			self._percent_text_node.delete()
			super().handlemessage(msg)
		elif isinstance(msg, bs.PowerupMessage):
			if msg.poweruptype == 'health':
				super().handlemessage(msg)
				if self.multiplier > 2:
					self.multiplier *= 0.5
				else:
					self.multiplier *= 0.75
				self.multiplier = max(1, self.multiplier)
				self.update_percent_display()
				if self.source_player:
					for icon in self._player.icons:
						icon.set_percent(int((self.multiplier - 1) * 100))
			else:
				super().handlemessage(msg)
		else:
			super().handlemessage(msg)


# ba_meta export bascenev1.GameActivity
class SuperSmash(EliminationGame):

	name = 'Super Smash'
	description = ModLang.description

	@classmethod
	def get_available_settings(
		cls, sessiontype: type[bs.Session]
	) -> list[bs.Setting]:
		settings = [
			bs.IntSetting(
				ModLang.lives,
				min_value=0,
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
			bs.BoolSetting(ModLang.boxing_gloves, default=True),
			bs.BoolSetting(ModLang.ice_explosion, default=True),
			bs.BoolSetting(ModLang.enable_powerups, default=True),
			bs.BoolSetting('Epic Mode', default=False),
		]
		return settings

	@classmethod
	def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
		maps = bs.app.classic.getmaps('melee')
		for m in ['Lake Frigid', 'Hockey Stadium', 'Football Stadium']:
			# remove maps without bounds
			maps.remove(m)
		return maps

	def __init__(self, settings: dict):
		bs.TeamGameActivity.__init__(self,settings)
		self._scoreboard = Scoreboard()
		self._start_time: float | None = None
		self._vs_text: bs.Actor | None = None
		self._round_end_timer: bs.Timer | None = None
		self._epic_mode = bool(settings['Epic Mode'])
		self._lives_per_player = int(settings[ModLang.lives])
		self._unlimited = True if self._lives_per_player == 0 else False
		self._time_limit = float(settings['Time Limit'])
		self._balance_total_lives = bool(
			settings.get('Balance Total Lives', False)
		)
		self._solo_mode = bool(settings.get('Solo Mode', False))

		# Base class overrides:
		self.slow_motion = self._epic_mode
		self.default_music = (
			bs.MusicType.EPIC if self._epic_mode else bs.MusicType.SURVIVAL
		)
		self._pow: PowBox | None = None
		self._boxing_gloves = bool(settings[ModLang.boxing_gloves])
		self._ice_explosion = bool(settings[ModLang.ice_explosion])
		self._enable_powerups = bool(settings[ModLang.enable_powerups])

	def get_instance_description(self) -> str | Sequence:
		return 'welcome to gummy tortue'

	def get_instance_description_short(self) -> str | Sequence:
		return 'sex dungeon'
	
	
	def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

        # In free-for-all mode, everyone is just lined up along the bottom.
		if isinstance(self.session, bs.FreeForAllSession):
			count = len(self.teams)
			x_offs = 120
			xval = x_offs * (count - 1) * -0.5
			for team in self.teams:
				if len(team.players) == 1:
					player = team.players[0]
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs
		else:
			count = len(self.players)
			x_offs = 120
			xval = x_offs * (count - 1) * -0.5
			for player in self.players:
			
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs

	def on_begin(self) -> None:
		self.doing_final_hit = False
		bs.TeamGameActivity.on_begin(self)
		self._start_time = bs.time()
		self.setup_standard_time_limit(self._time_limit)
		if self._enable_powerups:
			self.setup_standard_powerup_drops(enable_tnt=False)
		self._drop_pow_box()
		self._update_icons()
		

		# We could check game-over conditions at explicit trigger points,
		# but lets just do the simple thing and poll it.
		if not self._unlimited:
			bs.timer(1.0, self._update, repeat=True)
	
	def final_hit(self):

		now = bs.apptime()

		# Prevent triggering again until cooldown expires
		if now < getattr(self, 'final_hit_cooldown', 0):
			return

		self.final_hit_cooldown = now + 3

		if getattr(self, 'doing_final_hit', False):
			return

		self.doing_final_hit = True

		bs.getsound('finishingHit').play()

		gnode = self.globalsnode
		old_tint = gnode.tint

		# Smash-style freeze + flash
		gnode.tint = (1, 0, 0)
		gnode.paused = True

		def undo():
			gnode.paused = False
			gnode.tint = old_tint
			self.doing_final_hit = False

		bs.apptimer(1.2, undo)


		



	def on_player_join(self, player: Player) -> None:
		player.lives = self._lives_per_player

		# Create our icon and spawn.
		if self._unlimited:
			player.icons = [NewIcon(player, position=(0, 50), scale=0.8, unlimited=True, show_lives=False)]
		else:
			player.icons = [NewIcon(player, position=(0, 50), scale=0.8)]
		if self._unlimited:
			self.spawn_player(player)
		else:
			if player.lives > 0:
				self.spawn_player(player)

		# Don't waste time doing this until begin.
		if self.has_begun():
			self._update_icons()

	def _print_lives(self, player: Player) -> None:
		from bascenev1lib.actor import popuptext

		# We get called in a timer so it's possible our player has left/etc.
		if not player or not player.is_alive() or not player.node:
			return

		popuptext.PopupText(
			'x' + str(player.lives),
			color=(1, 1, 0, 1),
			offset=(0, -0.8, 0),
			random_offset=0.0,
			scale=1.8,
			position=player.node.position,
		).autoretain()
		
	def _drop_pow_box(self) -> None:
		if len(self.map.tnt_points) == 0:
			return
		pos = random.choice(self.map.tnt_points)
		pos = (pos[0], pos[1] + 1, pos[2])
		self._pow = PowBox(position=pos, velocity=(0.0, 1.0, 0.0)).autoretain()

	# overriding the default character spawning..
	def spawn_player(self, player: Player) -> bs.Actor:
		if isinstance(self.session, bs.DualTeamSession):
			position = self.map.get_start_position(player.team.id)
		else:
			# otherwise do free-for-all spawn locations
			position = self.map.get_ffa_start_position(self.players)
		angle = None

		name = player.getname()
		light_color = bs.normalized_color(player.color)
		display_color = bs.safecolor(player.color, target_intensity=0.75)

		spaz = SSPlayerSpaz(
			color=player.color,
			highlight=player.highlight,
			character=player.character,
			cosmetic=self.session.customdata[player.sessionplayer]['cosmetic'],
			player=player,
			ice_explosion=self._ice_explosion,
		)

		player.actor = spaz
		assert spaz.node

		# If this is co-op and we're on Courtyard or Runaround, add the
		# material that allows us to collide with the player-walls.
		# FIXME: Need to generalize this.
		if isinstance(self.session, bs.CoopSession) and self.map.getname() in [
				'Courtyard', 'Tower D'
		]:
			mat = self.map.preloaddata['collide_with_wall_material']
			assert isinstance(spaz.node.materials, tuple)
			assert isinstance(spaz.node.roller_materials, tuple)
			spaz.node.materials += (mat, )
			spaz.node.roller_materials += (mat, )

		spaz.node.name = name
		spaz.node.name_color = display_color
		spaz.connect_controls_to_player()

		# Move to the stand position and add a flash of light.
		spaz.handlemessage(
			bs.StandMessage(
				position,
				angle if angle is not None else random.uniform(0, 360)))
		self._spawn_sound.play(1, position=spaz.node.position)
		light = bs.newnode('light', attrs={'color': light_color})
		spaz.node.connectattr('position', light, 'position')
		bs.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
		bs.timer(0.5, light.delete)

		# If we have any icons, update their state.
		for icon in player.icons:
			icon.handle_player_spawned()
		self._update_icons()

		if self._boxing_gloves:
			spaz.equip_boxing_gloves()

		if not self._unlimited:
			bs.timer(0.3, bs.Call(self._print_lives, player))

		# If we have any icons, update their state.
		for icon in player.icons:
			icon.handle_player_spawned()
		self._update_icons()

		return spaz

	def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
		# pylint: disable=cyclic-import
		from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory

		PowerupBox(
			position=self.map.powerup_spawn_points[index],
			poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
				excludetypes=['punch'] if self._boxing_gloves else []
			),
			expire=expire,
		).autoretain()
		
	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, bs.PlayerDiedMessage):
			if self._unlimited:
				player: Player = msg.getplayer(Player)
				self.respawn_player(player)
			else:
				super().handlemessage(msg)
		elif isinstance(msg, PowBoxDieMessage):
			bs.timer(10.0, self._drop_pow_box)
		else:
			return super().handlemessage(msg)
		


# ba_meta export bascenev1.GameActivity
class SuperSmashDM(DeathMatchGame):

	name = 'Super Smash DM'
	description = ModLang.descriptiondm
	
	@classmethod
	def get_available_settings(
		cls, sessiontype: type[bs.Session]
	) -> list[bs.Setting]:
		settings = [
			bs.IntSetting(
				'Kills to Win Per Player',
				min_value=1,
				default=5,
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
			bs.BoolSetting(ModLang.boxing_gloves, default=True),
			bs.BoolSetting(ModLang.ice_explosion, default=True),
			bs.BoolSetting(ModLang.enable_powerups, default=True),
			bs.BoolSetting('Epic Mode', default=False),
		]

		# In teams mode, a suicide gives a point to the other team, but in
		# free-for-all it subtracts from your own score. By default we clamp
		# this at zero to benefit new players, but pro players might like to
		# be able to go negative. (to avoid a strategy of just
		# suiciding until you get a good drop)
		if issubclass(sessiontype, bs.FreeForAllSession):
			settings.append(
				bs.BoolSetting('Allow Negative Scores', default=False)
			)

		return settings
	
	@classmethod
	def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
		maps = bs.app.classic.getmaps('melee')
		for m in ['Lake Frigid', 'Hockey Stadium', 'Football Stadium']:
			# remove maps without bounds
			maps.remove(m)
		return maps
	
	def __init__(self, settings: dict):
		super().__init__(settings)
		self._pow: PowBox | None = None
		self._boxing_gloves = bool(settings[ModLang.boxing_gloves])
		self._ice_explosion = bool(settings[ModLang.ice_explosion])
		self._enable_powerups = bool(settings[ModLang.enable_powerups])
	
	def final_hit(self):

		now = bs.apptime()

		# Prevent triggering again until cooldown expires
		if now < getattr(self, 'final_hit_cooldown', 0):
			return

		self.final_hit_cooldown = now + 3

		if getattr(self, 'doing_final_hit', False):
			return

		self.doing_final_hit = True

		bs.getsound('finishingHit').play()

		gnode = self.globalsnode
		old_tint = gnode.tint

		# Smash-style freeze + flash
		gnode.tint = (1, 0, 0)
		gnode.paused = True

		def undo():
			gnode.paused = False
			gnode.tint = old_tint
			self.doing_final_hit = False

		bs.apptimer(1.2, undo)

	def get_instance_description(self) -> str | Sequence:
		return ModLang.descriptiondm

	def _update_icons(self) -> None:
        # pylint: disable=too-many-branches

		

        # In free-for-all mode, everyone is just lined up along the bottom.
		if isinstance(self.session, bs.FreeForAllSession):
			count = len(self.teams)
			x_offs = 120
			xval = x_offs * (count - 1) * -0.5
			for team in self.teams:
				if len(team.players) == 1:
					player = team.players[0]
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs
		else:
			count = len(self.players)
			x_offs = 120
			xval = x_offs * (count - 1) * -0.5
			for player in self.players:
			
					for icon in player.icons:
						icon.set_position_and_scale((xval, 30), 0.7)
						icon.update_for_lives()
					xval += x_offs
	
	def on_transition_in(self):
		super().on_transition_in()
		for p in self.players:
			try: p.icons
			except: p.icons = []
	
	def on_begin(self) -> None:
		self.doing_final_hit = False
		bs.TeamGameActivity.on_begin(self)
		self.setup_standard_time_limit(self._time_limit)
		if self._enable_powerups:
			self.setup_standard_powerup_drops(enable_tnt=False)
		self._drop_pow_box()

		# Base kills needed to win on the size of the largest team.
		self._score_to_win = self._kills_to_win_per_player * max(
			1, max((len(t.players) for t in self.teams), default=0)
		)
		self._update_scoreboard()
		self._update_icons()
		
	


	def _drop_pow_box(self) -> None:
		if len(self.map.tnt_points) == 0:
			return
		pos = random.choice(self.map.tnt_points)
		pos = (pos[0], pos[1] + 1, pos[2])
		self._pow = PowBox(position=pos, velocity=(0.0, 1.0, 0.0)).autoretain()
	
	def on_player_join(self, player):
		super().on_player_join(player)
		player.icons = [NewIcon(player, position=(0, 50), scale=0.8, unlimited=True, show_lives=False)]
		self._update_icons()
	
	def on_player_leave(self, player):
		player.icons = []
		self._update_icons()
	
	




	# overriding the default character spawning..
	def spawn_player(self, player: Player) -> bs.Actor:
		try: player.icons
		except: player.icons = []

		for icon in player.icons:
			icon.handle_player_spawned()
		self._update_icons()
		

		
		
		if isinstance(self.session, bs.DualTeamSession):
			position = self.map.get_start_position(player.team.id)
		else:
			# otherwise do free-for-all spawn locations
			position = self.map.get_ffa_start_position(self.players)
		angle = None

		name = player.getname()
		light_color = bs.normalized_color(player.color)
		display_color = bs.safecolor(player.color, target_intensity=0.75)

		spaz = SSPlayerSpaz(
			color=player.color,
			highlight=player.highlight,
			character=player.character,
			cosmetic=self.session.customdata[player.sessionplayer]['cosmetic'],
			player=player,
			ice_explosion=self._ice_explosion,
		)

		player.actor = spaz
		assert spaz.node

		# If this is co-op and we're on Courtyard or Runaround, add the
		# material that allows us to collide with the player-walls.
		# FIXME: Need to generalize this.
		if isinstance(self.session, bs.CoopSession) and self.map.getname() in [
				'Courtyard', 'Tower D'
		]:
			mat = self.map.preloaddata['collide_with_wall_material']
			assert isinstance(spaz.node.materials, tuple)
			assert isinstance(spaz.node.roller_materials, tuple)
			spaz.node.materials += (mat, )
			spaz.node.roller_materials += (mat, )

		spaz.node.name = name
		spaz.node.name_color = display_color
		spaz.connect_controls_to_player()

		# Move to the stand position and add a flash of light.
		spaz.handlemessage(
			bs.StandMessage(
				position,
				angle if angle is not None else random.uniform(0, 360)))
		self._spawn_sound.play(1, position=spaz.node.position)
		light = bs.newnode('light', attrs={'color': light_color})
		spaz.node.connectattr('position', light, 'position')
		bs.animate(light, 'intensity', {0: 0, 0.25: 1, 0.5: 0})
		bs.timer(0.5, light.delete)

		if self._boxing_gloves:
			spaz.equip_boxing_gloves()

		return spaz
	
	def _standard_drop_powerup(self, index: int, expire: bool = True) -> None:
		# pylint: disable=cyclic-import
		from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory

		PowerupBox(
			position=self.map.powerup_spawn_points[index],
			poweruptype=PowerupBoxFactory.get().get_random_powerup_type(
				excludetypes=['punch'] if self._boxing_gloves else []
			),
			expire=expire,
		).autoretain()

	def handlemessage(self, msg: Any) -> Any:
		if isinstance(msg, PowBoxDieMessage):
			bs.timer(10.0, self._drop_pow_box)
		elif isinstance(msg, bs.PlayerDiedMessage):
			player = msg.getplayer(Player)
			for icon in player.icons:
				icon.handle_player_died()
			self._update_icons()
			super().handlemessage(msg)
		else:
			return super().handlemessage(msg)
