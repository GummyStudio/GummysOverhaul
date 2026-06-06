# Thanks mell for letting me use this, it makes my life 1 million times easier

"""ultimate jank hell (testing too)"""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)
from __future__ import annotations
from typing import TYPE_CHECKING, Any, override
import bascenev1 as bs
import weakref

# utils for showing hitbox
SHOW_HITBOXES = True
COLBOX_COLOR = (1, 0, 0.5)
HITBOX_COLOR = (1, 0, 0)

# Messages are often a safe 
# way to communicate so use that, 
# instead of directly running a function.
class MoveMessage:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

class DummyCharacterActor(bs.Actor):
    """A dummy actor that does nothing. This should ALWAYS be 
    used as a parent-class (subclass?) so we can check for it's instance."""
    def __init__(self):
        super().__init__()

class Scene(bs.Actor):
    """A 2D Scene. Any actors should be attached to it, 
    whether moving around if not static, or just connected when static."""
    def __init__(
        self, 
        texture: str, 
        size: tuple[float, float] = (2048, 1024),
        scale: int | float = 2.2,
        position = (0.0, 0.0),
    ):
        super().__init__()
        self.connected_actors: list[bs.Actor] = []
        self.walls: list[CollisionBox] = []
        self.texture = texture
        self.scale = (size[0] * scale, size[1] * scale)
        self.node = bs.newnode(
            'image',
            attrs={
                'texture': bs.gettexture(self.texture),
                'opacity': 1.0,
                'absolute_scale': True,
                'position': position,
                'scale': self.scale,
                'attach': 'center',
            },
        )
        
    def _move(self, x: int = 0, y: int = 0):
        px, py = self.node.position
        self.node.position = (px + x, py + y)
    
    @override
    def handlemessage(self, msg: Any):
        if isinstance(msg, bs.DieMessage):
            for actor in self.connected_actors:
                actor.handlemessage(bs.DieMessage())
            self.node.delete()
        else:
            super().handlemessage(msg) # Augment standard behavior.
    
class CollisionBox(bs.Actor):
    """A wall or something that can be collided with. 
    This should tell actors to push themselves back 
    from the direction they pointed at when they collide 
    with us. There is no special things that can be done with this; 
    this is meant to be used as a simple collision object."""
    def __init__(
        self, 
        position: tuple[float, float], 
        scale: tuple[float, float] = (50.0, 50.0),
    ):
        super().__init__()
        self.node = bs.newnode(
            'image',
            delegate=self,
            attrs={
                'texture': bs.gettexture('white'),
                'opacity': 0.5 if SHOW_HITBOXES else 0.0,
                'absolute_scale': True,
                'position': position,
                'scale': scale,
                'attach': 'center',
                'color': COLBOX_COLOR,
            },
        )
        # Connect to the scene so we can move along with the map
        # sprite and ACTUALLY act like proper collision
        self._activity().scene.connected_actors.append(self)
        scene = self._activity().scene
        scene.walls.append(self)
    
    def _move(self, x: int = 0, y: int = 0):
        px, py = self.node.position
        self.node.position = (px + x, py + y)
    
    @override
    def handlemessage(self, msg: Any):
        if isinstance(msg, bs.DieMessage):
            self.node.delete()
        elif isinstance(msg, MoveMessage):
            self._move(msg.x, msg.y)
        else:
            super().handlemessage(msg) # Augment standard behavior.

class ScenePlayer(DummyCharacterActor):
    """player n shi"""
    @override
    def on_expire(self):
        self.xTimer = None
        self.yTimer = None
    
    def __init__(
        self, 
        player: bs.Player, 
        scene: Scene,
        position: tuple[float, float] = (0.0, 0.0),
        size: tuple[float, float] = (50.0, 50.0),
        scale: int | float = 1.6,
    ):
        # code was simplified here, since it's controlled
        # anyways in roaryingknite.py
        super().__init__()
        self.player = player
        self.scene = scene
        self._last_facing = None
        self._anim_timer: bs.Timer | None = None
        self.scale = (size[0] * scale, size[1] * scale)
        self._size = scale
        self.run = 0
        self.input_x = 0
        self.input_y = 0
        self.mult = 1

        # Our node. Control it like a sprite.
        self.node = bs.newnode(
            'image',
            attrs={
                'texture': bs.gettexture('soul'),
                'opacity': 1.0,
                'absolute_scale': True,
                'position': position,
                'scale': self.scale,
                'attach': 'center',
            },
        )
        self.hitbox = bs.newnode(
            'image',
            delegate=self,
            attrs={
                'texture': bs.gettexture('white'),
                'opacity': 0.5 if SHOW_HITBOXES else 0.0,
                'absolute_scale': True,
                'position': position,
                'scale': self.scale,
                'attach': 'center',
                'color': HITBOX_COLOR,
            },
        )
        self.scene.connected_actors.append(self)
        # we can just simply connect, assuming we don't need to do math
        # to get a offset and different scale... and shi
        self.node.connectattr('position', self.hitbox, 'position')
        self.max = 300
    
    def _would_collide(self, actor, wall, dx, dy):
        future_x = actor.hitbox.position[0] - dx
        future_y = actor.hitbox.position[1] - dy
        ax, ay = future_x, future_y
        bx, by = wall.node.position
        aw = actor.hitbox.scale[0] / 2
        ah = actor.hitbox.scale[1] / 2
        bw = wall.node.scale[0] / 2
        bh = wall.node.scale[1] / 2
        return (
            abs(ax - bx) < aw + bw and
            abs(ay - by) < ah + bh
        )
    def move_by_input(self, multiplier=1):
        # ok clamp so they cant move sideways faster
        self.mult = multiplier
        
        self._move(self.input_x*multiplier*(1+self.run*0.5),self.input_y*multiplier*(1+self.run*0.5),)
    def on_run(self, value):
        self.run = value
    
    def on_move_left_right(self, value):
        self.input_x = value
    def on_move_up_down(self, value):
        self.input_y = value

    def _move(self, x=0, y=0):
        if not self.node:
            return
        px, py = self.node.position
        self.node.position = (
            min(self.max, max(-self.max,px+x)), 
            min(self.max, max(-self.max,py+y))
        )
     
        

    @override
    def handlemessage(self, msg: Any):
        if isinstance(msg, bs.DieMessage):
            if msg.immediate:
                self.node.delete()
                self.hitbox.delete()
            else:
                # cool animation...
                pass
                self.node.delete()
                self.hitbox.delete()
        elif isinstance(msg, MoveMessage):
            self._move(msg.x, msg.y)
        else:
            super().handlemessage(msg) # Augment standard behavior.
        return super().handlemessage(msg) # Augment standard behavior.



  