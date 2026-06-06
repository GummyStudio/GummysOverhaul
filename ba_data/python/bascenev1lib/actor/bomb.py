# Released under the MIT License. See LICENSE for details.
#
"""Various classes for bombs, mines, tnt, etc."""

# FIXME
# pylint: disable=too-many-lines

from __future__ import annotations

import random
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import override
import bascenev1 as bs
import babase
import bauiv1 as bui

from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.popuptext import PopupText
from gummyoverhaul.nodevisualizer import NodeVisualizer
if TYPE_CHECKING:
    from typing import Any, Sequence, Callable

PlayerT = TypeVar('PlayerT', bound='bs.Player')
    

class BombFactory:
    """Wraps up media and other resources used by bs.Bombs.

    Category: **Gameplay Classes**

    A single instance of this is shared between all bombs
    and can be retrieved via bascenev1lib.actor.bomb.get_factory().
    """

    bomb_mesh: bs.Mesh
    """The bs.Mesh of a standard or ice bomb."""

    sticky_bomb_mesh: bs.Mesh
    """The bs.Mesh of a sticky-bomb."""

    impact_bomb_mesh: bs.Mesh
    """The bs.Mesh of an impact-bomb."""

    land_mine_mesh: bs.Mesh
    """The bs.Mesh of a land-mine."""

    tnt_mesh: bs.Mesh
    """The bs.Mesh of a tnt box."""

    regular_tex: bs.Texture
    """The bs.Texture for regular bombs."""

    ice_tex: bs.Texture
    """The bs.Texture for ice bombs."""

    sticky_tex: bs.Texture
    """The bs.Texture for sticky bombs."""

    impact_tex: bs.Texture
    """The bs.Texture for impact bombs."""

    impact_lit_tex: bs.Texture
    """The bs.Texture for impact bombs with lights lit."""

    land_mine_tex: bs.Texture
    """The bs.Texture for land-mines."""

    land_mine_lit_tex: bs.Texture
    """The bs.Texture for land-mines with the light lit."""

    rock_lit_tex: bs.Texture
    """The bs.Texture for Stone blocks tat are damaged."""

    tnt_tex: bs.Texture
    """The bs.Texture for tnt boxes."""

    hiss_sound: bs.Sound
    """The bs.Sound for the hiss sound an ice bomb makes."""

    debris_fall_sound: bs.Sound
    """The bs.Sound for random falling debris after an explosion."""

    wood_debris_fall_sound: bs.Sound
    """A bs.Sound for random wood debris falling after an explosion."""

    explode_sounds: Sequence[bs.Sound]
    """A tuple of bs.Sound-s for explosions."""

    freeze_sound: bs.Sound
    """A bs.Sound of an ice bomb freezing something."""

    fuse_sound: bs.Sound
    """A bs.Sound of a burning fuse."""

    activate_sound: bs.Sound
    """A bs.Sound for an activating impact bomb."""

    warn_sound: bs.Sound
    """A bs.Sound for an impact bomb about to explode due to time-out."""

    bomb_material: bs.Material
    """A bs.Material applied to all bombs."""

    normal_sound_material: bs.Material
    """A bs.Material that generates standard bomb noises on impacts, etc."""

    sticky_material: bs.Material
    """A bs.Material that makes 'splat' sounds and makes collisions softer."""

    land_mine_no_explode_material: bs.Material
    """A bs.Material that keeps land-mines from blowing up.
       Applied to land-mines when they are created to allow land-mines to
       touch without exploding."""

    land_mine_blast_material: bs.Material
    """A bs.Material applied to activated land-mines that causes them to
       explode on impact."""

    impact_blast_material: bs.Material
    """A bs.Material applied to activated impact-bombs that causes them to
       explode on impact."""

    blast_material: bs.Material
    """A bs.Material applied to bomb blast geometry which triggers impact
       events with what it touches."""

    dink_sounds: Sequence[bs.Sound]
    """A tuple of bs.Sound-s for when bombs hit the ground."""

    sticky_impact_sound: bs.Sound
    """The bs.Sound for a squish made by a sticky bomb hitting something."""

    roll_sound: bs.Sound
    """bs.Sound for a rolling bomb."""

    _STORENAME = bs.storagename()

    @classmethod
    def get(cls) -> BombFactory:
        """Get/create a shared bascenev1lib.actor.bomb.BombFactory object."""
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = BombFactory()
            activity.customdata[cls._STORENAME] = factory
        assert isinstance(factory, BombFactory)
        return factory

    def random_explode_sound(self) -> bs.Sound:
        """Return a random explosion bs.Sound from the factory."""
        return self.explode_sounds[random.randrange(len(self.explode_sounds))]
    
    def random_cardboard_explode_sound(self) -> bs.Sound:
        """Return a random explosion bs.Sound from the factory."""
        return self.cardboardExplode[random.randrange(len(self.cardboardExplode))]
    
    def random_breaker_sound(self) -> bs.Sound:
        """Return a random  breaker explosion bs.Sound from the factory."""
        return self.breakerex_sounds[random.randrange(len(self.breakerex_sounds))]

    def random_meow_sound(self) -> bs.Sound:
        """Return a random meow explosion bs.Sound from the factory."""
        return self.meow[random.randrange(len(self.meow))]

    def __init__(self) -> None:
        """Instantiate a BombFactory.

        You shouldn't need to do this; call
        bascenev1lib.actor.bomb.get_factory() to get a shared instance.
        """
        shared = SharedObjects.get()

        self.bomb_mesh = bs.getmesh('bomb')
        self.sticky_bomb_mesh = bs.getmesh('bombSticky')
        self.impact_bomb_mesh = bs.getmesh('impactBomb')
        self.land_mine_mesh = bs.getmesh('landMine')
        self.promine_mesh = bs.getmesh('proLandMine')
        self.tnt_mesh = bs.getmesh('tnt')
        self.rock_mesh = bs.getmesh('tnt')
        self.egg_mesh = bs.getmesh('eggBomb')
        self.impulse_mesh = bs.getmesh('impulse')
        self.mini_mesh = bs.getmesh('miniBomb')
        self.boogie_mesh = bs.getmesh('boogieBomb')
        self.star_mesh = bs.getmesh('starMine')
        self.boom_mesh = bs.getmesh('boomBox')
        self.bed_mesh = bs.getmesh('Bed')

        self.regular_tex = bs.gettexture('bombColor')
        self.gold_tex = bs.gettexture('goldBombColor')
        self.lightning_tex = bs.gettexture('white')
        self.bed_tex = bs.gettexture('bedColor')
        self.ice_tex = bs.gettexture('bombColorIce')
        self.sticky_tex = bs.gettexture('bombStickyColor')
        self.impact_tex = bs.gettexture('impactBombColor')
        self.impact_lit_tex = bs.gettexture('impactBombColorLit')
        self.land_mine_tex = bs.gettexture('landMine')
        self.land_mine_lit_tex = bs.gettexture('landMineLit')
        self.promine_tex = bs.gettexture('prolandMine')
        self.promine_lit_tex = bs.gettexture('prolandMineLit')
        self.tnt_tex = bs.gettexture('tnt')
        self.random_tex = bs.gettexture('bombRandom')
        self.rock_tex = bs.gettexture('rock')
        self.rock_lit_tex = bs.gettexture('rocky')
        self.negative_tex = bs.gettexture('negativeZone')
        self.egg_tex = bs.gettexture('eggTexBomb')
        self.impulse_tex = bs.gettexture('ImpulseColor')
        self.impulse_lit_tex = bs.gettexture('ImpulseColorLit')
        self.package_tex = bs.gettexture('cardboard')
        self.mini_tex = bs.gettexture('miniBombColor')
        self.boogie_tex = bs.gettexture('boogieBombColor')
        self.breaker_tex = bs.gettexture('shieldBreakerColor')
        self.star_tex = bs.gettexture('starColor')
        self.star_lit_tex = bs.gettexture('white')
        self.heart_tex = bs.gettexture('hplandMine')
        self.heart_lit_tex = bs.gettexture('hplandMineLit')
        self.boom_text = bs.gettexture('boomboxColor')

        self.hiss_sound = bs.getsound('hiss')
        self.debris_fall_sound = bs.getsound('debrisFall')
        self.wood_debris_fall_sound = bs.getsound('woodDebrisFall')

        self.explode_sounds = (
            bs.getsound('explosion01'),
            bs.getsound('explosion02'),
            bs.getsound('explosion03'),
            bs.getsound('explosion04'),
            bs.getsound('explosion05'),
        )
        self.breakerex_sounds = (
            bs.getsound('eletricBlast1'),
            bs.getsound('eletricBlast2'),
            bs.getsound('eletricBlast3'),
            bs.getsound('eletricBlast4'),
        )

        self.meow = (
            bs.getsound('meow1'),
            bs.getsound('meow2'),
            bs.getsound('meow3'),
            bs.getsound('meow4'),
            bs.getsound('meow5'),
        )

        self.cardboardExplode = (
            bs.getsound('coardboardExplode1'),
            bs.getsound('coardboardExplode2'),
            bs.getsound('coardboardExplode3'),
            bs.getsound('coardboardExplode4'),
        )

        self.freeze_sound = bs.getsound('freeze')
        self.fuse_sound = bs.getsound('fuse01')
        self.breaker_sound = bs.getsound('eletricIDLE')
        self.activate_sound = bs.getsound('activateBeep')
        self.warn_sound = bs.getsound('warnBeep')

        # Set up our material so new bombs don't collide with objects
        # that they are initially overlapping.
        self.bomb_material = bs.Material()
        self.normal_sound_material = bs.Material()
        self.sticky_material = bs.Material()

        self.bomb_material.add_actions(
            conditions=(
                (
                    ('we_are_younger_than', 100),
                    'or',
                    ('they_are_younger_than', 100),
                ),
                'and',
                ('they_have_material', shared.object_material),
            ),
            actions=('modify_node_collision', 'collide', False),
        )

        # We want pickup materials to always hit us even if we're currently
        # not colliding with their node. (generally due to the above rule)
        self.bomb_material.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=('modify_part_collision', 'use_node_collide', False),
        )

        self.bomb_material.add_actions(
            actions=('modify_part_collision', 'friction', 0.3)
        )

        self.land_mine_no_explode_material = bs.Material()
        self.land_mine_blast_material = bs.Material()
        self.land_mine_blast_material.add_actions(
            conditions=(
                ('we_are_older_than', 200),
                'and',
                ('they_are_older_than', 200),
                'and',
                ('eval_colliding',),
                'and',
                (
                    (
                        'they_dont_have_material',
                        self.land_mine_no_explode_material,
                    ),
                    'and',
                    (
                        ('they_have_material', shared.object_material),
                        'or',
                        ('they_have_material', shared.player_material),
                    ),
                ),
            ),
            actions=('message', 'our_node', 'at_connect', ImpactMessage()),
        )

        self.impact_blast_material = bs.Material()
        self.impact_blast_material.add_actions(
            conditions=(
                ('we_are_older_than', 200),
                'and',
                ('they_are_older_than', 200),
                'and',
                ('eval_colliding',),
                'and',
                (
                    ('they_have_material', shared.footing_material),
                    'or',
                    ('they_have_material', shared.object_material),
                ),
            ),
            actions=('message', 'our_node', 'at_connect', ImpactMessage()),
        )

        self.blast_material = bs.Material()
        self.blast_material.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(
                ('modify_part_collision', 'collide', True),
                ('modify_part_collision', 'physical', False),
                ('message', 'our_node', 'at_connect', ExplodeHitMessage()),
            ),
        )

        self.dink_sounds = (
            bs.getsound('bombDrop01'),
        )
        self.sticky_impact_sound = bs.getsound('stickyImpact')
        self.roll_sound = bs.getsound('bombRoll01')

        # Collision sounds.
        self.normal_sound_material.add_actions(
            conditions=('they_have_material', shared.footing_material),
            actions=(
                ('impact_sound', self.dink_sounds, 2, 0.8),
                ('roll_sound', self.roll_sound, 3, 6),
            ),
        )

        self.sticky_material.add_actions(
            actions=(
                ('modify_part_collision', 'stiffness', 0.1),
                ('modify_part_collision', 'damping', 1.0),
            )
        )

        self.sticky_material.add_actions(
            conditions=(
                ('they_have_material', shared.player_material),
                'or',
                ('they_have_material', shared.footing_material),
            ),
            actions=('message', 'our_node', 'at_connect', SplatMessage()),
        )


class SplatMessage:
    """Tells an object to make a splat noise."""


class ExplodeMessage:
    """Tells an object to explode."""


class ImpactMessage:
    """Tell an object it touched something."""


class ArmMessage:
    """Tell an object to become armed."""


class WarnMessage:
    """Tell an object to issue a warning sound."""


class ExplodeHitMessage:
    """Tell an object it was hit by an explosion."""


class Blast(bs.Actor):
    """An explosion, as generated by a bomb or some other object.

    category: Gameplay Classes
    """

    def __init__(
        self,
        position: Sequence[float] = (0.0, 1.0, 0.0),
        velocity: Sequence[float] = (0.0, 0.0, 0.0),
        blast_radius: float = 2.0,
        blast_type: str = 'normal',
        source_player: bs.Player | None = None,
        hit_type: str = 'explosion',
        hit_subtype: str = 'normal',
        crit_boosted: bool = False,
        crit_type: str = 'normal'
    ):
        """Instantiate with given values."""

        # bah; get off my lawn!
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        super().__init__()

        shared = SharedObjects.get()
        factory = BombFactory.get()
        if blast_type == 'random':
            if random.randrange(1, 6) == 1:
                blast_type = 'tnt'
            elif random.randrange(1, 4) == 1:
                blast_type = 'ice'
            elif random.randrange(1, 4) == 1:
                blast_type = 'normal'
            else:
                blast_type = 'nothing'
    
        self.blast_type = blast_type
        self._source_player = source_player
        self.hit_type = hit_type
        self.hit_subtype = blast_type
        self.radius = blast_radius

        self.crit_boosted = crit_boosted
        self.crit_type = crit_type

        if self.crit_boosted:
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('crit_start').play()

        # Set our position a bit lower so we throw more things upward.
        rmats = (factory.blast_material, shared.attack_material)
        self.node: NodeVisualizer = bs.newnode(
            'region',
            delegate=self,
            attrs={
                'position': (position[0], position[1] - 0.1, position[2]),
                'scale': (self.radius, self.radius, self.radius),
                'type': 'sphere',
                'materials': rmats,
            },
        )

        bs.timer(0.05, self.node.delete)
        def playlightningsfx():
            
            bs.getsound('lightningBlast').play()
            try:
                self.getactivity().map.lightning_strike()
            except: pass

        # basically ripped from bombdash.
        def lightningBolt(pos):
            bs.camerashake(intensity = 5)


            Blast(
                position=pos,
                velocity=(0, 0, 0),
                blast_radius=2,
                blast_type='strike',
                source_player=bs.existing(self._source_player),
                hit_type=self.hit_type,
                hit_subtype='strike',
                crit_boosted=self.crit_boosted,
                crit_type=self.crit_type
            ).autoretain()

            light = bs.newnode('light', attrs={
                'position': pos,
                'color': (1, 1, 1),
                'radius': 1.4})
            bs.animate(
                light, 'intensity',
                {0: 1, 0.1: 3, 0.2: 0})
            
        # Throw in an explosion and flash.
        evel = (velocity[0], max(-1.0, velocity[1]), velocity[2])
        if blast_type == 'nothing':
            bs.emitfx(
                position=position,
                velocity=velocity,
                count=int(1.0 + random.random() * 4),
                emit_type='tendrils',
                tendril_type='thin_smoke',
            )
            bs.emitfx(
                position=position,
                velocity=velocity,
                count=random.randrange(20, 40),
                emit_type='tendrils',
                tendril_type='smoke',
            )
            # have a chance to blow out some gumcoins :3
            if random.randrange(1, 5) == 1:
                    
                    bs.getsound('cash').play()
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=random.randrange(2, 5),
                    spread=0.6,
                    scale=2,
                    chunk_type='ice',
                    emit_type='stickers',
                )
                    
                    elrandom = random.randrange(3, 5) * random.randrange(1, 9)
                    cfg = bui.app.config
                    PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(elrandom), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = position
                                ).autoretain()
                    cfg['GUMMY_gumcoins'] += elrandom
                    cfg.apply_and_commit()

            else:
                bs.getsound('boowomp').play()



            

    
        else:

            explosion = bs.newnode(
            'explosion',
            attrs={
                'position': position,
                'velocity': evel,
                'radius': self.radius,
                'big': (self.blast_type == 'tnt'),
            },
            )
            if self.blast_type == 'lightning':
                loc = bs.newnode(
                    'locator',
                    attrs={
                        'position': self.node.position,
                        'shape': 'circleOutline',
                        'size':[(2) * 2.1],
                        'color': (1, 1, 1),
                        'opacity': 0.55,
                        'draw_beauty': False,
                        'additive': False
                    })

                
                bs.getsound('lightningStartup').play(),
                bs.timer(1.2, bs.Call(playlightningsfx))
                bs.timer(1.3, loc.delete)
                bs.timer(1.3, bs.Call(lightningBolt, position)),


            if self.blast_type == 'boogie':
                bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=random.randrange(2, 5),
                    spread=2,
                    scale=0.5,
                    chunk_type='ice',
                    emit_type='stickers',
                )
                bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(4.0 + random.random() * 8),
                    spread=0.7,
                    chunk_type='slime',
                )
                bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=3,
                    spread=2.0,
                    scale=1,
                    chunk_type='rock',
                    emit_type='stickers',
                )
                light = bs.newnode('light', attrs={
                        'position': position,
                        'color': (0.25, 0.125, 0.5),
                        'radius': 0.5})
                bs.animate(
                        light, 'intensity',
                        {0: 0.5, 0.1: 1, 0.15: 1.2, 0.2: 0})

            if self.blast_type == 'ice':
                explosion.color = (0, 0.05, 0.4)
            
            if self.blast_type == 'gold':
                explosion.color = (1, 1, 0)

            

            if self.crit_boosted:
                explosion.color = (0, 0.8, 2)

            if blast_type == 'rock':    
                  
                bs.timer(0.05, self.node.delete)
                bs.emitfx(
                position=position,
                velocity=velocity,
                count=5,
                emit_type='stickers',
                tendril_type='thin_smoke',
             ),
                # little easter egg: let it produce diamonds sometimes. (will give gumcoins)
                if random.randrange(1, 5) == 1:
                    bs.getsound('cash').play()
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=random.randrange(2, 5),
                    spread=0.6,
                    scale=2,
                    chunk_type='ice',
                    emit_type='stickers',
                )
                    
                    elrandom = random.randrange(3, 5) * random.randrange(1, 9)
                    cfg = bui.app.config
                    PopupText('+ ' + bui.charstr(bui.SpecialChar.OUYA_BUTTON_U) + " " + str(elrandom), 
                                color=(0, 1, 1, 1),
                                scale=1,
                                position = position
                                ).autoretain()
                    cfg['GUMMY_gumcoins'] += elrandom
                    cfg.apply_and_commit()
                
        

            bs.timer(1.0, explosion.delete)


            if self.blast_type != 'ice':
                bs.emitfx(
                position=position,
                velocity=velocity,
                count=int(1.0 + random.random() * 4),
                emit_type='tendrils',
                tendril_type='thin_smoke',
            )
            if self.blast_type != 'gold':
                bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(4.0 + random.random() * 4),
                    emit_type='tendrils',
                    tendril_type='ice' if self.blast_type == 'ice' else 'smoke',
                )
                bs.emitfx(
                    position=position,
                    emit_type='distortion',
                    spread=1.0 if self.blast_type == 'tnt' else 2.0,
                )

        # And emit some shrapnel.
            if self.blast_type == 'ice':

                def emit() -> None:
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=30,
                    spread=2.0,
                    scale=0.4,
                    chunk_type='ice',
                    emit_type='stickers',
                )

            # It looks better if we delay a bit.
                bs.timer(0.05, emit)

            elif self.blast_type == 'sticky':

                def emit() -> None:
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        spread=0.7,
                        chunk_type='slime',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        scale=0.5,
                        spread=0.7,
                        chunk_type='slime',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=15,
                        scale=0.6,
                        chunk_type='slime',
                        emit_type='stickers',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=20,
                        scale=0.7,
                        chunk_type='spark',
                        emit_type='stickers',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(6.0 + random.random() * 12),
                        scale=0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )

            # It looks better if we delay a bit.
                bs.timer(0.05, emit)
            elif self.blast_type == 'negative':

                def emit() -> None:
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=40,
                    spread=2.0,
                    scale=1,
                    chunk_type='rock',
                    emit_type='stickers',
                )
                # It looks better if we delay a bit.
                bs.timer(0.05, emit)
                    
            elif self.blast_type == 'egg':

                def emit() -> None:
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(4.0 + random.random() * 8),
                    spread=0.2,
                    scale=0.5,
                    chunk_type='slime',
                )
            # It looks better if we delay a bit.
                bs.timer(0.05, emit)

            elif self.blast_type == 'impulse':

                def emit() -> None:
                    light = bs.newnode('light', attrs={
                        'position': position,
                        'color': (0.25, 0.125, 0.5),
                        'radius': 0.5})
                    bs.animate(
                        light, 'intensity',
                        {0: 0.5, 0.1: 1, 0.15: 1.2, 0.2: 0})
            # It looks better if we delay a bit.
                bs.timer(0.05, emit)

            elif self.blast_type == 'impact':

                def emit() -> None:
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        scale=0.8,
                        chunk_type='metal',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        scale=0.4,
                        chunk_type='metal',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=20,
                        scale=0.7,
                        chunk_type='spark',
                        emit_type='stickers',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(8.0 + random.random() * 15),
                        scale=0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )

            # It looks better if we delay a bit.
                bs.timer(0.05, emit)

            elif blast_type == 'gold':
                def emit():
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=30,
                        scale=1.0 if self.blast_type == 'tnt' else 0.7,
                        chunk_type='spark',
                        emit_type='stickers',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(18.0 + random.random() * 20),
                        scale=1.0 if self.blast_type == 'tnt' else 0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )
            

            else:  # Regular or land mine bomb shrapnel.

                def emit() -> None:
                    if self.blast_type != 'tnt':
                        bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        chunk_type='rock',
                    )
                    bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(4.0 + random.random() * 8),
                        scale=0.5,
                        chunk_type='rock',
                    )
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=30,
                    scale=1.0 if self.blast_type == 'tnt' else 0.7,
                    chunk_type='spark',
                    emit_type='stickers',
                )
                    bs.emitfx(
                    position=position,
                    velocity=velocity,
                    count=int(18.0 + random.random() * 20),
                    scale=1.0 if self.blast_type == 'tnt' else 0.8,
                    spread=1.5,
                    chunk_type='spark',
                )

                # TNT throws splintery chunks.
                if self.blast_type == 'tnt':

                    def emit_splinters() -> None:
                        bs.emitfx(
                            position=position,
                            velocity=velocity,
                            count=int(20.0 + random.random() * 25),
                            scale=0.8,
                            spread=1.0,
                            chunk_type='splinter',
                        )

                    bs.timer(0.01, emit_splinters)

                # Every now and then do a sparky one.
                if self.blast_type == 'tnt' or random.random() < 0.1:

                    def emit_extra_sparks() -> None:
                        bs.emitfx(
                            position=position,
                            velocity=velocity,
                            count=int(10.0 + random.random() * 20),
                            scale=0.8,
                            spread=1.5,
                            chunk_type='spark',
                        )

                    bs.timer(0.02, emit_extra_sparks)

            # It looks better if we delay a bit.
            bs.timer(0.05, emit)
            if crit_boosted:
                bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(6.0 + random.random() * 12),
                        scale=0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )
                bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(6.0 + random.random() * 12),
                        scale=0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )
                bs.emitfx(
                        position=position,
                        velocity=velocity,
                        count=int(6.0 + random.random() * 12),
                        scale=0.8,
                        spread=1.5,
                        chunk_type='spark',
                    )
            lcolor = (0.6, 0.6, 1.0) if self.blast_type == 'ice' else (1, 0.3, 0.1)
            light = bs.newnode(
            'light',
            attrs={
                'position': position,
                'volume_intensity_scale': 10.0,
                'color': lcolor,
            },
            )

            scl = random.uniform(0.6, 0.9)
            scorch_radius = light_radius = self.radius
            if self.blast_type == 'tnt':
                light_radius *= 1.4
                scorch_radius *= 1.15
                scl *= 3.0

            iscale = 1.6
            bs.animate(
            light,
            'intensity',
            {
                0: 2.0 * iscale,
                scl * 0.02: 0.1 * iscale,
                scl * 0.025: 0.2 * iscale,
                scl * 0.05: 17.0 * iscale,
                scl * 0.06: 5.0 * iscale,
                scl * 0.08: 4.0 * iscale,
                scl * 0.2: 0.6 * iscale,
                scl * 2.0: 0.00 * iscale,
                scl * 3.0: 0.0,
            },
            )
            bs.animate(
            light,
            'radius',
            {
                0: light_radius * 0.2,
                scl * 0.05: light_radius * 0.55,
                scl * 0.1: light_radius * 0.3,
                scl * 0.3: light_radius * 0.15,
                scl * 1.0: light_radius * 0.05,
            },
            )
            bs.timer(scl * 3.0, light.delete)

            # Make a scorch that fades over time.
            scorch = bs.newnode(
            'scorch',
            attrs={
                'position': position,
                'size': scorch_radius * 0.5 if self.blast_type != 'gold' else 0.1,
                'big': (self.blast_type == 'tnt'),
            },
            )
            if self.blast_type == 'ice':
                scorch.color = (1, 1, 1.5)
            elif self.blast_type == 'promine':
                scorch.color = (1, 0, 0)
            elif self.blast_type == 'egg':
                scorch.color = (1, 0.8, 0.55)
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('tap').play(),
            elif self.blast_type == 'strike':
                scorch.color = (1, 1, 1)
            elif self.blast_type == 'mini':
                scorch.color = (0.2, 1, 0.2)
            elif self.blast_type == 'gold':
                scorch.color = (1, 1, 0.2)

            bs.animate(scorch, 'presence', {3.000: 1, 13.000: 0})
            bs.timer(13.0, scorch.delete)

            if self.blast_type == 'ice':
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    factory.hiss_sound.play(position=light.position)

            lpos = light.position
            
            if self.blast_type == 'negative':
                scorch.color = (0.1, 0.1, 0.5)
                bs.getsound('negativeBlowup').play(),
            elif self.blast_type == 'impulse':
                scorch.color = (0.3, 0, 1)
                bs.getsound('shockwaveBlast').play(),
            elif self.blast_type == 'heart':
                scorch.color = (1, 0, 0.5)
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('healingExplosion').play()
            elif self.blast_type == 'egg':
                scorch.color = (1, 0.8, 0.55)
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('eggBlast').play(),
            elif self.blast_type == 'boogie':
                scorch.color = (0, 0.2, 1)
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    bs.getsound('boogieBlast').play(),
            elif self.blast_type == 'strike':
                'i dont want an explosion sfx.'
            elif self.blast_type == 'breaker':
                scorch.color = (1, 1, 2)
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    factory.random_breaker_sound().play(position=lpos)
            elif self.blast_type == 'boom' or  self.blast_type == 'boom2' or  self.blast_type == 'boom3':
                scorch_radius = 0
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    factory.random_meow_sound().play(position=lpos)
                    bs.getsound('boomboxBlast').play()
            elif self.blast_type == 'package':
                factory.random_cardboard_explode_sound().play(position=lpos)
                factory.debris_fall_sound.play(position=lpos)
                scorch.color = (1, 0.7, 0)
            elif self.blast_type == 'gold':
                bs.getsound('gold').play(1.2, position=lpos)
            elif self.blast_type == 'bed':
                bs.getsound('bedExplode').play(5.0, position=lpos)
            else:    
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    factory.random_explode_sound().play(position=lpos)
                    factory.debris_fall_sound.play(position=lpos)

            bs.camerashake(intensity=5.0 if self.blast_type == 'tnt' else 1.0)

            # TNT is more epic.
            if self.blast_type == 'tnt':
                factory.random_explode_sound().play(position=lpos)

            def _extra_boom() -> None:
                factory.random_explode_sound().play(position=lpos)

                bs.timer(0.25, _extra_boom)

            def _extra_debris_sound() -> None:
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    factory.debris_fall_sound.play(position=lpos)
                    factory.wood_debris_fall_sound.play(position=lpos)
            if self.blast_type in ['tnt']:
                bs.timer(0.4, _extra_debris_sound)

        

        # Beds spawn in fire
        if self.blast_type == 'bed':
            for _ in range(random.randint(3, 5)):
                pos = (
                    self.node.position[0] + random.uniform(-2.2, 2.2),
                    self.node.position[1],
                    self.node.position[2] + random.uniform(-2.2, 2.2),

                )
                Fire(pos, random.randint(12, 20))
          
    @override
    def handlemessage(self, msg: Any) -> Any:
        assert not self.expired

        if isinstance(msg, bs.DieMessage):
            if self.node:
                self.node.delete()

        elif isinstance(msg, ExplodeHitMessage):
            node = bs.getcollision().opposingnode
            assert self.node
            nodepos = self.node.position
            mag = 2000
            velocity = (0, 0, 0)
            if self.blast_type == 'sticky':
                mag *= 1
            elif self.blast_type == 'impact':
                mag *= 1
            elif self.blast_type == 'ice':
                mag *= 0.5
            elif self.blast_type == 'land_mine':
                mag *= 2.5
            elif self.blast_type == 'heart':
                mag *= 0.8
            elif self.blast_type == 'promine':
                mag *= 3
            elif self.blast_type == 'tnt':
                mag *= 2.0
            elif self.blast_type == 'nothing':
                mag *= 0
            elif self.blast_type == 'rock':
                mag *= 2.7
            elif self.blast_type == 'negative':
                mag *= 2.7
            elif self.blast_type == 'egg':
                mag *= 0.1
            elif self.blast_type == 'impulse':
                mag *= 2
            elif self.blast_type == 'mini':
                mag *= 0.93
            elif self.blast_type == 'lightning':
                mag *= 0.30
            elif self.blast_type == 'strike':
                mag *= 5
            elif self.blast_type == 'boogie':
                mag *= 0
            elif self.blast_type == 'breaker':
                mag *= 0.363
            elif self.blast_type == 'star':
                mag *= 0.87
            elif self.blast_type == 'boom':
                mag *= 1
            elif self.blast_type == 'boom2':
                mag *= 1.5
            elif self.blast_type == 'boom3':
                mag *= 2.2
            elif self.blast_type == 'package':
                mag *= 0.2
            elif self.blast_type == 'gold':
                mag *= 0.76
            elif self.blast_type == 'bed':
                mag *= 0.6

            from bascenev1lib.actor.spaz import Spaz
            is_spaz = node.getdelegate(Spaz)
            boogie = False
            

            # keep the boogieing stuff consistant
            if is_spaz:
                boogie = is_spaz.boogieing
            
            if self.crit_boosted or boogie:
                if self.crit_type == 'normal' or boogie:
                    mag *= 3.0
                else:
                   
                    mag *= 1.35



            node.handlemessage(
            bs.HitMessage(
                    pos=nodepos,
                    velocity=velocity,
                    magnitude=mag,
                    hit_type=self.hit_type,
                    hit_subtype=self.hit_subtype,
                    radius=self.radius,
                    source_player=bs.existing(self._source_player),
                    crit_boosted=self.crit_boosted,
                    crit_type=self.crit_type,
                    
                )
            )
            if self.blast_type == 'ice':
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    BombFactory.get().freeze_sound.play(1, position=nodepos)
                node.handlemessage(bs.FreezeMessage())

        else:
            return super().handlemessage(msg)
        return None


class Bomb(bs.Actor):
    """A standard bomb and its variants such as land-mines and tnt-boxes.

    category: Gameplay Classes
    """

    # Ew; should try to clean this up later.
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    def __init__(
        self,
        position: Sequence[float] = (0.0, 1.0, 0.0),
        velocity: Sequence[float] = (0.0, 0.0, 0.0),
        bomb_type: str = 'normal',
        blast_radius: float = 2.0,
        bomb_scale: float = 1.0,
        source_player: bs.Player | None = None,
        owner: bs.Node | None = None,
        crit_boosted: bool = False,
        crit_type: str = 'normal'
    ):
        """Create a new Bomb.

        bomb_type can be 'ice','impact','land_mine','normal','sticky', or
        'tnt'. Note that for impact or land_mine bombs you have to call arm()
        before they will go off.
        """
        super().__init__()

        shared = SharedObjects.get()
        factory = BombFactory.get()


        if bomb_type not in (
            'ice',
            'impact',
            'land_mine',
            'normal',
            'sticky',
            'tnt',
            'random',
            'rock',
            'negative',
            'promine',
            'egg',
            'lightning',
            'impulse',
            'mini',
            'strike',
            'star',
            'boogie',
            'breaker',
            'heart',
            'boom',
            'package',
            'gold',
            'bed'
        ):
            raise ValueError('invalid bomb type: ' + bomb_type)
        self.bomb_type = bomb_type

        self._exploded = False
        self.scale = bomb_scale

        self.crit_boosted = crit_boosted
        self.crit_type = crit_type

        self.texture_sequence: bs.Node | None = None

        if self.bomb_type == 'sticky':
            self._last_sticky_sound_time = 0.0
        if self.bomb_type == 'impulse':
            self._last_sticky_sound_time = 0.0

        self.blast_radius = blast_radius
        if self.bomb_type == 'ice':
            self.blast_radius *= 1.2
        elif self.bomb_type == 'impact':
            self.blast_radius *= 0.7
        elif self.bomb_type == 'land_mine':
            self.blast_radius *= 0.7
        elif self.bomb_type == 'heart':
            self.blast_radius *= 1.5
        elif self.bomb_type == 'promine':
            self.blast_radius *= 1
        elif self.bomb_type == 'tnt':
            self.blast_radius *= 1.45
        elif self.bomb_type == 'negative':
            self.blast_radius *= 1.8
        elif self.bomb_type == 'egg':
            self.blast_radius *= 0.5
        elif self.bomb_type == 'impulse':
            self.blast_radius *= 0.5
        elif self.bomb_type == 'mini':
            self.blast_radius *= 0.8
        elif self.bomb_type == 'strike':
            self.blast_radius *= 3
        elif self.bomb_type == 'boogie':
            self.blast_radius *= 0.7
        elif self.bomb_type == 'breaker':
            self.blast_radius *= 1.1
        elif self.bomb_type == 'star':
            self.blast_radius *= 1.65
        elif self.bomb_type == 'boom':
            self.blast_radius *= 1.3
        elif self.bomb_type == 'boom2':
            self.blast_radius *= 1.7
        elif self.bomb_type == 'boom3':
            self.blast_radius *= 2
        elif self.bomb_type == 'package':
            self.blast_radius *= 1.2
        elif self.bomb_type == 'gold':
            self.blast_radius *= 1.45
        elif self.bomb_type == 'bed':
            self.blast_radius *= 2

        if self.crit_boosted:
            self.blast_radius *= 1.2

        self._explode_callbacks: list[Callable[[Bomb, Blast], Any]] = []

        # The player this came from.
        self._source_player = source_player

        # By default our hit type/subtype is our own, but we pick up types of
        # whoever sets us off so we know what caused a chain reaction.
        # UPDATE (July 2020): not inheriting hit-types anymore; this causes
        # weird effects such as land-mines inheriting 'punch' hit types and
        # then not being able to destroy certain things they normally could,
        # etc. Inheriting owner/source-node from things that set us off
        # should be all we need I think...
        self.hit_type = 'explosion'
        self.hit_subtype = self.bomb_type

        # The node this came from.
        # FIXME: can we unify this and source_player?
        self.owner = owner

        if self.bomb_type == 'bed':
            self.times_hit = 0

        # Adding footing-materials to things can screw up jumping and flying
        # since players carrying those things and thus touching footing
        # objects will think they're on solid ground.. perhaps we don't
        # wanna add this even in the tnt case?
        materials: tuple[bs.Material, ...]
        if self.bomb_type in ['tnt', 'rock', 'bed']:
            materials = (
                factory.bomb_material,
                shared.footing_material,
                shared.object_material,
            )
        else:
            materials = (factory.bomb_material, shared.object_material)

        if self.bomb_type == 'impact':
            materials = materials + (factory.impact_blast_material,)
        elif self.bomb_type == 'impulse':
            materials = materials + (factory.sticky_material,)
        elif self.bomb_type == 'boogie':
            materials = materials + (factory.sticky_material,)
        elif self.bomb_type == 'egg':
            materials = materials + (factory.impact_blast_material,)
        elif self.bomb_type == 'land_mine':
            materials = materials + (factory.land_mine_no_explode_material,)
        elif self.bomb_type == 'heart':
            materials = materials + (factory.land_mine_no_explode_material,)
        elif self.bomb_type == 'star':
            materials = materials + (factory.land_mine_no_explode_material,)
        elif self.bomb_type == 'promine':
            materials = materials + (factory.land_mine_no_explode_material,)

        if self.bomb_type == 'sticky':
            materials = materials + (factory.sticky_material,)
        else:
            materials = materials + (factory.normal_sound_material,)

        if self.bomb_type == 'land_mine':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.land_mine_mesh,
                    'light_mesh': factory.land_mine_mesh,
                    'body': 'landMine',
                    'body_scale': self.scale,
                    'shadow_size': 0.44,
                    'color_texture': factory.land_mine_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                    'materials': materials,
                },
            )
        
        elif self.bomb_type == 'heart':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.land_mine_mesh,
                    'light_mesh': factory.land_mine_mesh,
                    'body': 'landMine',
                    'body_scale': self.scale,
                    'shadow_size': 0.44,
                    'color_texture': factory.heart_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                    'materials': materials,
                },
            )
        
        elif self.bomb_type == 'boom':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.boom_mesh,
                    'light_mesh': factory.boom_mesh,
                    'body': 'landMine',
                    'body_scale': self.scale,
                    'shadow_size': 0.44,
                    'color_texture': factory.boom_text,
                    'reflection': 'soft',
                    'reflection_scale': [2.0],
                    'materials': materials,
                },
            )
        
        elif self.bomb_type == 'promine':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.promine_mesh,
                    'light_mesh': factory.promine_mesh,
                    'body': 'landMine',
                    'body_scale': 1.2,
                    'shadow_size': 0.44,
                    'color_texture': factory.promine_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                    'materials': materials,
                },
            )


        elif self.bomb_type == 'rock':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.rock_mesh,
                    'light_mesh': factory.rock_mesh,
                    'body': 'crate',
                    'body_scale': 1,
                    'shadow_size': 0.44,
                    'color_texture': factory.rock_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [0],
                    'materials': materials,
                },
            )

        elif self.bomb_type == 'negative':
            fuse_time = random.randrange(2, 9)
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.bomb_mesh,
                    'light_mesh': factory.bomb_mesh,
                    'body': 'sphere',
                    'body_scale': self.scale,
                    'shadow_size': 0.44,
                    'color_texture': factory.negative_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [-2],
                    'materials': materials,
                },
            )
            
        elif self.bomb_type == 'tnt':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.tnt_mesh,
                    'light_mesh': factory.tnt_mesh,
                    'body': 'crate',
                    'body_scale': self.scale,
                    'shadow_size': 0.5,
                    'color_texture': factory.tnt_tex,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': materials,
                },
            )

        elif self.bomb_type == 'bed':
            fuse_time = None
            self.scale = 1.15
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.bed_mesh,
                    'light_mesh': factory.bed_mesh,
                    'body': 'landMine',
                    'body_scale': self.scale,
                    'shadow_size': 0.5,
                    'color_texture': factory.bed_tex,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': materials,
                },
            )

        elif self.bomb_type == 'impact':
            fuse_time = 20.0
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'body': 'sphere',
                    'body_scale': self.scale,
                    'mesh': factory.impact_bomb_mesh,
                    'shadow_size': 0.3,
                    'color_texture': factory.impact_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [1.5],
                    'materials': materials,
                },
            )
            self.arm_timer = bs.Timer(
                0.2, bs.WeakCall(self.handlemessage, ArmMessage())
            )
            self.warn_timer = bs.Timer(
                fuse_time - 1.7, bs.WeakCall(self.handlemessage, WarnMessage())
            )
            self.arm_timer = bs.Timer(
                0.2, bs.WeakCall(self.handlemessage, ArmMessage())
            )
            self.warn_timer = bs.Timer(
                fuse_time - 1.7, bs.WeakCall(self.handlemessage, WarnMessage())
            )

        elif self.bomb_type == 'boogie':
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                bs.getsound('boogieDeploy').play(),
            fuse_time = 60 # Eventually explode
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'body': 'sphere',
                    'body_scale': self.scale,
                    'mesh': factory.boogie_mesh,
                    'sticky': False,
                    'owner': self.owner,
                    'shadow_size': 0.3,
                    'color_texture': factory.boogie_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [0],
                    'materials': materials,
                },
            )
            self.node.stick_to_owner = False


        elif self.bomb_type == 'impulse':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'body': 'sphere',
                    'body_scale': self.scale,
                    'mesh': factory.impulse_mesh,
                    'shadow_size': 0.3,
                    'sticky': True,
                    'color_texture': factory.impulse_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [-5],
                    'materials': materials,
                    'owner': owner,
                },
            )
            self.node.stick_to_owner = False

            # Sometimes impulse grenades get stuck and dont explode so the user
            # cant throw another bomb, lets add a failsafe

            bs.timer(15, self.arm)

        elif self.bomb_type == 'egg':
            fuse_time = 20.0
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'body': 'sphere',
                    'body_scale': 1,
                    'mesh': factory.egg_mesh,
                    'shadow_size': 0.44,
                    'color_texture': factory.egg_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [0],
                    'materials': materials,
                },
            )
        
        elif self.bomb_type == 'package':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.tnt_mesh,
                    'light_mesh': factory.tnt_mesh,
                    'body': 'crate',
                    'body_scale': self.scale,
                    'shadow_size': 0.5,
                    'color_texture': factory.package_tex,
                    'reflection': 'soft',
                    'reflection_scale': [0.23],
                    'materials': materials,
                },
            )
        
        elif self.bomb_type == 'star':
            fuse_time = None
            self.node: NodeVisualizer = bs.newnode(
                'prop',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': factory.star_mesh,
                    'light_mesh': factory.land_mine_mesh,
                    'body': 'landMine',
                    'body_scale': self.scale,
                    'shadow_size': 0.44,
                    'color_texture': factory.star_tex,
                    'reflection': 'powerup',
                    'reflection_scale': [2],
                    'materials': materials,
                },
            )

        else:
            fuse_time = 3.0
            if self.bomb_type == 'sticky':
                sticky = True
                mesh = factory.sticky_bomb_mesh
                rtype = 'sharper'
                rscale = 1.8
            else:
                sticky = False
                mesh = factory.bomb_mesh
                rtype = 'sharper'
                rscale = 1.8
            if self.bomb_type == 'ice':
                tex = factory.ice_tex
            elif self.bomb_type == 'sticky':
                tex = factory.sticky_tex
            elif self.bomb_type == 'sticky':
                tex = factory.sticky_tex
            elif self.bomb_type == 'random':
                tex = factory.random_tex
                if random.randrange(1, 4) == 1:
                    sticky = True
                else: sticky = False
            elif self.bomb_type == 'gold':
                tex = factory.gold_tex
                fuse_time = 3.5
                rtype = 'powerup'
            elif self.bomb_type == 'mini':
                tex = factory.mini_tex
                mesh = factory.mini_mesh
                self.scale = 1
                fuse_time = 1.5
            elif self.bomb_type == 'impulse':
                mesh = factory.impulse_mesh
                tex = factory.impulse_tex
                rtype = 'powerup'
                rscale = -5
            elif self.bomb_type == 'lightning':
                tex = factory.lightning_tex
                rtype = 'powerup'
                rscale = -2
            elif self.bomb_type == 'strike':
                fuse_time = 0.000001
            elif self.bomb_type == 'breaker':
                tex = factory.breaker_tex
                rscale = -0.3
            else:
                tex = factory.regular_tex

            self.node: NodeVisualizer = bs.newnode(
                'bomb',
                delegate=self,
                attrs={
                    'position': position,
                    'velocity': velocity,
                    'mesh': mesh,
                    'body_scale': self.scale,
                    'shadow_size': 0.3,
                    'color_texture': tex,
                    'sticky': sticky,
                    'owner': owner,
                    'reflection': rtype,
                    'reflection_scale': [rscale],
                    'materials': materials,
                },
            )   
            if self.bomb_type == 'breaker':
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                    sound = bs.newnode(
                'sound',
                owner=self.node,
                attrs={'sound': factory.breaker_sound, 'volume': 0.25},
            )
            else: 
                from bascenev1lib.mainmenu import MainMenuActivity
                if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):  
                    sound = bs.newnode(
                'sound',
                owner=self.node,
                attrs={'sound': factory.fuse_sound, 'volume': 0.25},
            )
                    self.node.connectattr('position', sound, 'position')
            bs.animate(self.node, 'fuse_length', {0.0: 1.0, fuse_time: 0.0})

        # Light the fuse!!! come bac kto this gummy
        if self.bomb_type not in ('land_mine', 'tnt', 'rock', 'promine', 'egg', 'impulse', 'star', 'heart', 'boom', 'package', 'bed'):
            assert fuse_time is not None
            bs.timer(
                fuse_time, bs.WeakCall(self.handlemessage, ExplodeMessage())
            )

        bs.animate(
            self.node,
            'mesh_scale',
            {0: 0, 0.2: 1.3 * self.scale, 0.26: self.scale},
        )
        self.glow = None
        self.sound = None
        if self.crit_boosted:
            
            self.glow: NodeVisualizer = bs.newnode('light',
                attrs={
                    'position': position,
                    'radius': 0.2,
                    'intensity': self.scale,
                    'color': (0.2, 0.6, 1.0) if self.crit_type == 'normal' else (1, 1, 0),
                    'volume_intensity_scale': 0.7
                }
            )
            self.node.connectattr('position', self.glow, 'position')

            

            # Zap sound
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                self.sound: NodeVisualizer = bs.newnode('sound', attrs={'sound': bs.getsound('crit_powered'),
                                        'volume': 0.58})
                self.node.connectattr('position', self.sound, 'position')

            else:
                self.sound =bs.Node(None)
            
            bs.timer(0.1, self.crit_effects, repeat=True)
    
    def crit_effects(self):
        if random.randint(0, 2) == 0 and self.node:
            bs.emitfx(
                    position=self.node.position,
                    velocity=self.node.velocity,
                    count=int(6.0 + random.random() * 40),
                    scale=0.5,
                    spread=0.5,
                    chunk_type='spark',
                )

    def get_source_player(self, playertype: type[PlayerT]) -> PlayerT | None:
        """Return the source-player if one exists and is the provided type."""
        player: Any = self._source_player
        return (
            player
            if isinstance(player, playertype) and player.exists()
            else None
        )

    @override
    def on_expire(self) -> None:
        super().on_expire()

        # Release callbacks/refs so we don't wind up with dependency loops.
        self._explode_callbacks = []

    def _handle_die(self) -> None:
        if self.node:
            self.node.delete()

        if self.sound:
            self.sound.delete()
        if self.glow:
            self.glow.delete()

    def _handle_oob(self) -> None:
        self.handlemessage(bs.DieMessage())

    def _handle_impact(self) -> None:
        node = bs.getcollision().opposingnode
        # If we're an impact bomb and we came from this node, don't explode.
        # (otherwise we blow up on our own head when jumping).
        # Alternately if we're hitting another impact-bomb from the same
        # source, don't explode. (can cause accidental explosions if rapidly
        # throwing/etc.)
        node_delegate = node.getdelegate(object)

        
        if node:
            if self.bomb_type == 'impact' and (
                node is self.owner
                or (
                    isinstance(node_delegate, Bomb)
                    and node_delegate.bomb_type == 'impact'
                    and node_delegate.owner is self.owner
                )
            ):
                return
            self.handlemessage(ExplodeMessage())

            if self.bomb_type == 'egg':
                self.handlemessage(ExplodeMessage())
        




        

    def _handle_dropped(self) -> None:
        if self.bomb_type == 'land_mine' or self.bomb_type == 'promine' or self.bomb_type == 'heart':
            self.arm_timer = bs.Timer(
                1.25, bs.WeakCall(self.handlemessage, ArmMessage())
            )

        elif self.bomb_type == 'star':
            bs.getsound('starArm').play()
            self.arm_timer = bs.Timer(
                3, bs.WeakCall(self.handlemessage, ArmMessage())
            )
        
        elif self.bomb_type == 'boom':
            self.arm_timer = bs.Timer(
                1, bs.WeakCall(self.handlemessage, ExplodeMessage())
            )

        

        # Once we've thrown a sticky bomb we can stick to it.
        elif self.bomb_type == 'sticky':

            def _setsticky(node: bs.Node) -> None:
                if node:
                    node.stick_to_owner = True

            bs.timer(0.25, lambda: _setsticky(self.node))

        elif self.bomb_type == 'impulse':
                
            def _setsticky(node: bs.Node) -> None:
                if node:
                    node.stick_to_owner = True

            bs.timer(0.3, lambda: _setsticky(self.node))
        
        elif self.bomb_type == 'boogie':
                
            def _setsticky(node: bs.Node) -> None:
                if node:
                    node.stick_to_owner = True

            bs.timer(0.3, lambda: _setsticky(self.node))

        elif self.bomb_type == 'bed':
            bs.timer(0.1, self.handle_bed, repeat=True)

    def handle_bed(self):
        if not self.node:
            return

        for player in self.getactivity().players:

            if not player.is_alive():
                continue

            if player.actor.node.hold_node is self.node:
                self.explode()
                return

        
    
    def remainstatic(self, node: bs.Node):
        if node:
            node.velocity = (0, 0, 0)

    def _handle_splat(self) -> None:
        if self.bomb_type == 'sticky':

            node = bs.getcollision().opposingnode
            if (
            node is not self.owner
            and bs.time() - self._last_sticky_sound_time > 1.0
            ):
                self._last_sticky_sound_time = bs.time()
            assert self.node
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                BombFactory.get().sticky_impact_sound.play(
                2.0,
                position=self.node.position,
            )

        elif self.bomb_type == 'impulse':
            if self.node.stick_to_owner:
                self.handlemessage(ArmMessage())
        elif self.bomb_type == 'boogie':
            if self.node.stick_to_owner:
                self.handlemessage(ExplodeMessage())

    def add_explode_callback(self, call: Callable[[Bomb, Blast], Any]) -> None:
        """Add a call to be run when the bomb has exploded.

        The bomb and the new blast object are passed as arguments.
        """
        self._explode_callbacks.append(call)

    def explode(self) -> None:
        """Explode the bomb now."""
        if self._exploded:
            return
        self._exploded = True
        if self.node:
            if self.bomb_type == 'boom':
                
                if self.node:
                    self.iwantos = self.node.position

                self.um = 1

                def elblast():
                    blasttype = 'boom'
                    if self.um == 2:
                        blasttype = 'boom2'
                    if self.um == 3:
                        blasttype = 'boom3'
                    self.um += 1

                    if self.node:
                        blast = Blast(
                    position=self.node.position,
                    velocity=(0, 0, 0),
                    blast_radius=self.blast_radius,
                    blast_type=blasttype,
                    source_player=bs.existing(self._source_player),
                    hit_type=self.hit_type,
                    hit_subtype=self.hit_subtype,
                crit_boosted=self.crit_boosted,
                crit_type=self.crit_type
                        ).autoretain()
                        bs.timer(0.02, bs.Call(self.remainstatic, self.node))

                        for callback in self._explode_callbacks:
                            callback(self, blast)
            
                        if self.um == 3 and self.node:
                            bs.timer(1, bs.WeakCall(self.handlemessage, bs.DieMessage()))

                um2 = 1
                for i in range(3):

                    bs.timer(um2, elblast)
                    um2 += 1

            else:
                blast = Blast(
                position=self.node.position,
                velocity=self.node.velocity,
                blast_radius=self.blast_radius,
                blast_type=self.bomb_type,
                source_player=bs.existing(self._source_player),
                hit_type=self.hit_type,
                hit_subtype=self.hit_subtype,
                crit_boosted=self.crit_boosted,
                crit_type=self.crit_type
                ).autoretain()
                for callback in self._explode_callbacks:
                        callback(self, blast)

        if not self.bomb_type == 'boom':
            # We blew up so we need to go away.
            # NOTE TO SELF: do we actually need this delay?
            bs.timer(0.001, bs.WeakCall(self.handlemessage, bs.DieMessage()))
        
        

    def _handle_warn(self) -> None:
        if self.texture_sequence and self.node:
            self.texture_sequence.rate = 30
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                BombFactory.get().warn_sound.play(0.5, position=self.node.position)

    def _add_material(self, material: bs.Material) -> None:
        if not self.node:
            return
        materials = self.node.materials
        if material not in materials:
            assert isinstance(materials, tuple)
            self.node.materials = materials + (material,)

    def arm(self) -> None:
        """Arm the bomb (for land-mines and impact-bombs).

        These types of bombs will not explode until they have been armed.
        """
        if not self.node:
            return
        factory = BombFactory.get()
        intex: Sequence[bs.Texture]
        if self.bomb_type == 'land_mine':
            intex = (factory.land_mine_lit_tex, factory.land_mine_tex)
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 30, 'input_textures': intex},
            )
            bs.timer(0.5, self.texture_sequence.delete)

            # We now make it explodable.
            bs.timer(
                0.25,
                bs.WeakCall(
                    self._add_material, factory.land_mine_blast_material
                ),
            )
        elif self.bomb_type == 'heart':
            intex = (factory.heart_lit_tex, factory.heart_tex)
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 30, 'input_textures': intex},
            )
            bs.timer(0.5, self.texture_sequence.delete)

            # We now make it explodable.
            bs.timer(
                0.25,
                bs.WeakCall(
                    self._add_material, factory.land_mine_blast_material
                ),
            )
        elif self.bomb_type == 'impact':
            intex = (
                factory.impact_lit_tex,
                factory.impact_tex,
                factory.impact_tex,
            )
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 100, 'input_textures': intex},
            )
            bs.timer(
                1,
                bs.WeakCall(
                    self._add_material, factory.land_mine_blast_material
                ),
            )
        elif self.bomb_type == 'impulse':
            bs.getsound('shockwaveActivate').play(),
            intex = (
                factory.impulse_lit_tex,
                factory.impulse_tex,
                factory.impulse_lit_tex,
                factory.impulse_tex,
                factory.impulse_lit_tex,
                factory.impulse_tex,
                factory.impulse_lit_tex,
                factory.impulse_tex,
                factory.impulse_lit_tex,
                factory.impulse_tex,
                factory.impulse_lit_tex,
                factory.impulse_tex,

            )
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 25, 'input_textures': intex},
            )
            bs.timer(
                0.6,
                bs.WeakCall(
                    self.handlemessage, ExplodeMessage(),
                ),
            )
        elif self.bomb_type == 'rock':
            intex = (factory.rock_lit_tex, factory.rock_lit_tex)
            self. texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 10, 'input_textures': intex},
            )
        
        elif self.bomb_type == 'egg':
            'i dunno im just here.'
        
        elif self.bomb_type == 'promine':
            intex = (factory.promine_lit_tex, factory.promine_tex)
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 30, 'input_textures': intex},
            )
            bs.timer(0.5, self.texture_sequence.delete)

            # We now make it explodable.
            bs.timer(
                0.25,
                bs.WeakCall(
                    self._add_material, factory.land_mine_blast_material
                ),
            )
        elif self.bomb_type == 'boogie':
            intex = (
                factory.boogie_tex,
                factory.boogie_tex,
            )
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 100, 'input_textures': intex},
            )
            bs.timer(
                0.001,
                bs.WeakCall(
                    self.handlemessage, ExplodeMessage()
                ),
            )
        elif self.bomb_type == 'star':
            intex = (
                factory.star_tex,
                factory.star_lit_tex,
            )
            self.texture_sequence = bs.newnode(
                'texture_sequence',
                owner=self.node,
                attrs={'rate': 70, 'input_textures': intex},
            )
            self.node.velocity = (self.node.velocity[0] + 999, self.node.velocity[1] + 100, self.node.velocity[2])
            bs.timer(1, bs.WeakCall(
                self.handlemessage, ExplodeMessage()
                )
            )
            
        else:
                raise RuntimeError(
                'arm() should only be called on land-mines or impact bombs'
            )
        self.texture_sequence.connectattr(
            'output_texture', self.node, 'color_texture'
            )
        
        if self.bomb_type == 'land_mine' or self.bomb_type == 'impact' or self.bomb_type == 'heart':
            from bascenev1lib.mainmenu import MainMenuActivity
            if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
                factory.activate_sound.play(0.5, position=self.node.position)

        if self.bomb_type == 'promine':
            bs.camerashake(intensity = 5)
            bs.getsound('activateBeepstrong').play(),
        elif self.bomb_type == 'impulse':
            bs.getsound('shockwaveActivate').play(),
        


    def _handle_hit(self, msg: bs.HitMessage) -> None:
        ispunched = msg.srcnode and msg.srcnode.getnodetype() == 'spaz'




        # Normal bombs are triggered by non-punch impacts;
        # impact-bombs by all impacts.
        if not self._exploded and (
            not ispunched or self.bomb_type in ['impact', 'land_mine', 'rock', 'promine', 'egg', 'impulse', 'star', 'heart']
        ):
            # Also lets change the owner of the bomb to whoever is setting
            # us off. (this way points for big chain reactions go to the
            # person causing them).
            source_player = msg.get_source_player(bs.Player)
            if source_player is not None:
                self._source_player = source_player

                # Also inherit the hit type (if a landmine sets off by a bomb,
                # the credit should go to the mine)
                # the exception is TNT.  TNT always gets credit.
                # UPDATE (July 2020): not doing this anymore. Causes too much
                # weird logic such as bombs acting like punches. Holler if
                # anything is noticeably broken due to this.
                # if self.bomb_type != 'tnt':
                #     self.hit_type = msg.hit_type
                #     self.hit_subtype = msg.hit_subtype
            if self.bomb_type == 'rock':
                self.arm()
                bs.timer(
                1 + random.random() * 0.1,
                bs.WeakCall(self.handlemessage, ExplodeMessage()),
            )
            else:

                if self.bomb_type == 'bed':
                    self.times_hit += 1

                    if self.times_hit > 3:
                        bs.timer(
                            0.1 + random.random() * 0.1,
                                bs.WeakCall(self.handlemessage, ExplodeMessage()),
                        )

                if not self.bomb_type in ['bed']:
                    bs.timer(
                        0.1 + random.random() * 0.1,
                            bs.WeakCall(self.handlemessage, ExplodeMessage()),
                    )

        assert self.node
        self.node.handlemessage(
            'impulse',
            msg.pos[0],
            msg.pos[1],
            msg.pos[2],
            msg.velocity[0],
            msg.velocity[1],
            msg.velocity[2],
            msg.magnitude,
            msg.velocity_magnitude,
            msg.radius,
            0,
            msg.velocity[0],
            msg.velocity[1],
            msg.velocity[2],
        )

        if msg.srcnode:
            pass

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ExplodeMessage):
            self.explode()
        elif isinstance(msg, ImpactMessage):
            self._handle_impact()
        elif isinstance(msg, bs.PickedUpMessage):
            # Change our source to whoever just picked us up *only* if it
            # is None. This way we can get points for killing bots with their
            # own bombs. Hmm would there be a downside to this?
            if self._source_player is None:
                self._source_player = msg.node.source_player
        elif isinstance(msg, SplatMessage):
            self._handle_splat()
        elif isinstance(msg, bs.DroppedMessage):
            self._handle_dropped()
        elif isinstance(msg, bs.HitMessage):
            self._handle_hit(msg)
        elif isinstance(msg, bs.DieMessage):
            self._handle_die()
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self._handle_oob()
        elif isinstance(msg, ArmMessage):
            self.arm()
        elif isinstance(msg, WarnMessage):
            self._handle_warn()
        else:
            super().handlemessage(msg)






class TNTSpawner:
    """Regenerates TNT at a given point in space every now and then.

    category: Gameplay Classes
    """

    def __init__(self, position: Sequence[float], respawn_time: float = 20.0):
        """Instantiate with given position and respawn_time (in seconds)."""
        self._position = position
        self._tnt: Bomb | None = None
        self._respawn_time = random.uniform(0.8, 1.2) * respawn_time
        self._wait_time = 0.0
        self._update()

        # Go with slightly more than 1 second to avoid timer stacking.
        self._update_timer = bs.Timer(
            1.1, bs.WeakCall(self._update), repeat=True
        )

    def _update(self) -> None:
        tnt_alive = self._tnt is not None and self._tnt.node
        if not tnt_alive:
            # Respawn if its been long enough.. otherwise just increment our
            # how-long-since-we-died value.
            if self._tnt is None or self._wait_time >= self._respawn_time:
                self._tnt = Bomb(position=self._position, bomb_type='tnt')
                self._wait_time = 0.0
            else:
                self._wait_time += 1.1




class Fire:
    def __init__(self, position, duration=3.0, radius=0.8):
        self.position = position
        self.duration = duration
        self.radius = radius
        self.dead = False
        try:
            if len(bs.getactivity().fires) > 18:
                return
        except: pass # Not a valid activity, probably the main menu.  We dont want to add fires there.
        bs.getactivity().fires.append(self)

      
        self.light = bs.newnode('light', attrs={
                'position': position,
                'color': (0.8, 0.2, 0),
                'intensity': radius})
        self.animate = bs.animate(
                self.light, 'radius',
                {0: 0.2, 0.1: 0.3, 0.2: 0.2}, True)
        
            

        

        # Lifetime timer
        bs.timer(duration, self.die)

        # Tick timer to check Spazes in radius
        self._tick_timer = bs.Timer(0.1, self.tick, repeat=True)

    def tick(self):
        if self.dead:
            return
        from bascenev1lib.actor.spaz import Spaz

        x, y, z = self.position

        for node in bs.getnodes():
            if not node.exists() or node.getnodetype() not in ['spaz', 'prop', 'bomb']:
                continue

            spaz = node.getdelegate(Spaz)
            bomb = node.getdelegate(Bomb)
            px, py, pz = node.position
            dist = ((px - x)**2 + (py - y)**2 + (pz - z)**2)**0.5
            if spaz:
                

            

                if dist < self.radius:
                    spaz.touched_fire(id(self))
                    bs.emitfx(position=(px, py, pz), count=5, chunk_type='spark')
                else:
                    spaz.leave_fire(id(self))

            
            if bomb:
                if dist < self.radius*2:
                    bomb.handlemessage(ExplodeMessage())

        # Fire particle effect
        for _ in range(2):
            bs.emitfx(
                position=self.position,
                velocity=(0, 19, 0),
                count=13 + int(12 + random.random() * 12),
                scale=random.random() * 6,
                spread=random.random() * 0.76,
                chunk_type='sweat'
            )

    def die(self):
            from bascenev1lib.actor.spaz import Spaz

            if hasattr(self, '_tick_timer') and self._tick_timer:
                self._tick_timer = None
            self.dead = True

            try:
                bs.getactivity().fires.remove(self)
            except:
                pass

            bs.getsound('Fizz').play(2)

  
            if self.animate:
                self.animate.delete()
            if self.light:
                bs.timer(0.5, self.light.delete)
            bs.animate(
                self.light, 'radius',
                {0: 0.8, 0.5:0}, True)

            # Tell all Spazes that this fire is gone
            for node in bs.getnodes():
                if not node.exists() or node.getnodetype() != 'spaz':
                    continue
                spaz = node.getdelegate(Spaz)
                if spaz:
                    spaz.leave_fire(id(self))

       