import bascenev1 as bs
from typing import Any
import random
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.spazfactory import SpazFactory
from gummyoverhaul.pvz.zombies import Zombie
from bascenev1lib.actor.popuptext import PopupText


class ZombieFreezeMessage:
    """ ouw .. THE SEQUEL"""
    def __init__(self, zombie: Zombie, damage: int = 10, duration: float = 1.0):
        self.zombie = zombie
        self.damage = damage
        self.duration = duration


def safesetattr(node: bs.Node, attr: str, value: Any):
        if node.exists():
            setattr(node, attr, value)

class Bullet(bs.Actor):
    damage = 20
    def __init__(self, position: tuple[float, float, float]):
        super().__init__()
       
        self.node: bs.NodeVisualizer = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                    'position': (
                        position[0],
                        position[1]+0.25,
                        position[2]
                    ),
                    'mesh': bs.getmesh('shield'),
                    'velocity': (2, 0, 0),
                    'light_mesh': None,
                    'body': 'crate',
                    'body_scale': 0.1,
                    'gravity_scale': 0.0,
                    'mesh_scale': 0.1,
                    'color_texture': bs.gettexture('miniBombColor'),
                    'reflection': 'powerup',
                    'reflection_scale': [0.2],
                     'materials': [self.getactivity().non_collide_mat]
                },
        )
        bs.getsound('pvz/throw'+str(random.randint(1, 2))).play(position=self.node.position)   
        from bascenev1lib.game.pvz import ZombieAttackMessage

        self.attack_message = ZombieAttackMessage
        self.tick_timer = bs.Timer(0.1,self._tick, repeat=True)

    
    def _tick(self):
        if not self.node:
            return
        from gummyoverhaul.pvz.zombies import Zombie
        try:
            for zombie in bs.getactivity().zombies:
                    

                if not zombie:
                        continue     
                if not zombie.node:
                    continue
                        
                dist = ((zombie.node.position[0]-self.node.position[0])**2 +
                        
                            (zombie.node.position[2]-self.node.position[2])**2)**0.5
                if dist < 0.5 and zombie.is_alive(): 
                 
                    # kill
                    zombie.handlemessage(self.attack_message(zombie, self.damage))
                    # and die
                    bs.getsound('pvz/splat'+str(random.randint(1, 3))).play(position=self.node.position)
                    self.handlemessage(bs.DieMessage())


        except:pass
                
                    


    def handlemessage(self, msg: Any) -> Any:


        if isinstance(msg, bs.DieMessage):
            if not self.node:
                return
            if not msg.immediate:
                bs.emitfx(position=self.node.position, scale=0.4, count=5, spread=0.1, chunk_type='slime')
            self.tick_timer = None


            self.node.delete()
            
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)     
        return None

class IceBullet(Bullet):
    def __init__(self, position):
        super().__init__(position)
        # Okay, lets turn blue
        self.node.color_texture = bs.gettexture('shieldBreakerColor')  
        # And, our message is a freeze one
        self.attack_message = ZombieFreezeMessage
    
class Sun(bs.Actor):
    sun = 25
    """ a prop that just sits there and then expires, and if the activity curser comes near it, collect it."""
    def __init__(self, position: tuple[float, float, float]):
        super().__init__()
        self.node: bs.NodeVisualizer=bs.newnode(
            'prop',
            delegate=self,
            attrs={
                    'position': position,
                    'velocity': (0,-1,0),
                    'mesh': bs.getmesh('shield'),
                    'light_mesh': None,
                    'body': 'crate',
                    'body_scale': 0.2,
                    'mesh_scale': 0.2,
                    'shadow_size': 0.44,
                    'gravity_scale': 0.35,
                    'color_texture': bs.gettexture('goldColor'),
                    'reflection': 'powerup',
                    'reflection_scale': [1.0],
                     'materials': [self.getactivity().non_collide_mat], 
                },
        )
        self.lifetime = 60
        self.collectable = True
        
        
        try: # Juuuust in case it gets deleted early.
            bs.timer(self.lifetime-1, bs.Call(safesetattr, self.node, 'flashing', True))
        except: pass
        bs.timer(self.lifetime, bs.Call(self.handlemessage, bs.DieMessage()))

    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.DieMessage):
            if not self.node:
                return
            self.collectable = False
            if msg.immediate:
                self.node.delete()
            else:
                
                bs.animate(self.node, 'mesh_scale', {0: 0.2, 0.14: 0.1, 0.2: 0})
                bs.timer(0.2, self.node.delete)
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)     
        return None 
class Plant(bs.Actor):

    name = 'Plant'
    toughness = 300
    recharge = 7.6
    shoot_delay = 1.0
    cost = 50
    care_if_zombie_in_lane = True


    def __init__(self, position: tuple[float, float, float]):
        super().__init__()
        self.node: bs.NodeVisualizer =bs.newnode(
            
            'prop',
            delegate=self,
            attrs={
                    'position': position,
                    'velocity': (0,-1,0),
                    'mesh': bs.getmesh('box'),
                    'light_mesh': None,
                    'body': 'puck',
                    'body_scale': 0.8,
                    'shadow_size': 0.44,
                    'color_texture': bs.gettexture('white'),
                    'reflection': 'powerup',
                    'reflection_scale': [0.5],
                    'materials': [self.getactivity().non_collide_mat], 
                },
        )
        self.last_shot_time = bs.time()

        self.tick_timer = bs.Timer(0.1, self._tick, repeat=True)
        self.active = True
        

    def _tick(self):
        if not self.active or not self.node:
            return # no, tell the plant to NOt (game is paused or something)
        
        if self.can_shoot() and self._zombie_in_lane():
            self.on_shot()
            
    def can_shoot(self):
        return bs.time() - self.last_shot_time >= self.shoot_delay
    
    def on_shot(self):
        if not self.node: return
        # class will handle this
        self.last_shot_time = bs.time()

    def _zombie_in_lane(self) -> bool:
        # if we dont care if a zombie is in our lane, just return true.
        if not self.care_if_zombie_in_lane:
            return True
        my_pos = self.node.position
        from gummyoverhaul.pvz.zombies import Zombie
        
   
        zombies_list =self.getactivity().zombies.copy()
        
        for zombie in zombies_list:
            if not zombie or not zombie.node:
                continue
            
            z_pos = zombie.node.position

            if abs(z_pos[2] - my_pos[2]) < 0.4:
         
                if z_pos[0] > my_pos[0]:
                    return True
        return False

    
    
    def handlemessage(self, msg: Any) -> Any:
        from bascenev1lib.game.pvz import PlantAttackMessage

        if isinstance(msg, bs.DieMessage):
            if not self.node:
                return
            self.tick_timer = None
            if not msg.immediate:
                bs.getsound('pvz/gulp').play()
            self.node.delete()
        elif isinstance(msg, PlantAttackMessage):
            if not self.node: return
            self.toughness -= msg.damage
            self.node.flashing =True
            bs.timer(0.1, bs.Call(safesetattr, self.node, 'flashing', False))
        
            if self.toughness <= 0:
                self.handlemessage(bs.DieMessage())
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        else:
            return super().handlemessage(msg)     
        return None 
    
class PeaShooter(Plant):
    name = 'PeaShooter'
    cost = 100
    shoot_delay = 1.5
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position)
        # set prop attributes
        self.node.mesh = bs.getmesh('pvz/peashooter')
        self.node.color_texture = bs.gettexture('pvz/peashooterColor')
        self.node.mesh_scale = 0.5

    def on_shot(self):
        super().on_shot()
        Bullet(self.node.position).autoretain()
  
class Sunflower(Plant):
    name = 'Sunflower'
    cost = 50
    shoot_delay = 12
    recharge = 10

    care_if_zombie_in_lane = False # We dont care if a zombie is not in our lane, were just makin sun
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position)
        self.node.mesh = bs.getmesh('pvz/sunflower')
        self.node.color_texture = bs.gettexture('pvz/sunflowerColor')
        self.node.mesh_scale = 0.5

    def on_shot(self):
        super().on_shot()
        # Sun!
        pos = (
                self.node.position[0]+random.uniform(-1, 1),
                self.node.position[1],
                self.node.position[2]+random.uniform(-1, 1)
            )
           
        s=Sun(pos).autoretain()
        s.node.velocity = (0, 2, 0)
    


class Wallnut(Plant):
    name = 'Wallnut'
    toughness = 4000
    cost = 50
    recharge = 30
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position)
        self.node.mesh = bs.getmesh('pvz/wallnut')
        self.node.color_texture = bs.gettexture('pvz/wallnutColor')
        self.node.mesh_scale = 0.5

    
    def on_shot(self):
        # dont do anythin
        return


class Repeater(Plant):
    name = 'Repeater'
    cost = 200
    shoot_delay = 1.5
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position)
        # set prop attributes
        self.node.mesh = bs.getmesh('pvz/repeater')
        self.node.color_texture = bs.gettexture('pvz/repeaterColor')
        self.node.mesh_scale = 0.5
    def shoot_if_exists(self):
        # hah i knew it
        if self.node:
            Bullet(self.node.position).autoretain()
    def on_shot(self):
        super().on_shot()
        
        Bullet(self.node.position).autoretain()
        bs.timer(0.2, self.shoot_if_exists)

    
class IcePea(Plant):
    name = 'IcePea'
    cost = 175
    shoot_delay = 1.5
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position)
        # set prop attributes
        self.node.mesh = bs.getmesh('pvz/icepea')
        self.node.color_texture = bs.gettexture('pvz/icepeaColor')
        self.node.mesh_scale = 0.5

    def on_shot(self):
        super().on_shot()
        IceBullet(self.node.position).autoretain()

class PotatoMine(Plant):
    name = 'PotatoMine'
    toughness = 300
    cost = 25
    recharge = 30

    def __init__(self, position):
        super().__init__(position)
        self.arm_sound = bs.getsound('pvz/dirt_rise')
        self.explode_sound = bs.getsound('pvz/potato_mine')
        # We start unarmed.
        self.armed = False
        self.armed_mesh = bs.getmesh('pvz/potatomineArmed')
        self.node.mesh = bs.getmesh('pvz/potatomineUnarmed')
        self.node.color_texture = bs.gettexture('pvz/potatomineColor')
        self.node.mesh_scale = 0.5
        bs.timer(15, self.arm)

    def arm(self):
        if not self.node:
            return
        self.armed = True
        self.node.mesh = self.armed_mesh
        self.arm_sound.play(position=self.node.position)
        
    def explode(self):
        if not self.node:
            return
        pos = self.node.position
        self.handlemessage(bs.DieMessage(True))
        PopupText(
            'SPUDOW!', position=pos, color=(1, 0.5, 0), scale=1.5
        ).autoretain()
        # Explode
        self.explode_sound.play(position=pos)
        from bascenev1lib.game.pvz import ZombieAttackMessage
        for zombie in self.getactivity().zombies:
            if not zombie or not zombie.node: continue
            
            z_dist = ((zombie.node.position[0]-pos[0])**2 + 
                      (zombie.node.position[2]-pos[2])**2)**0.5
            
            if z_dist < 1.2: # Kill everoyne around us
                zombie.handlemessage(ZombieAttackMessage(zombie, 1800))
        
    def _tick(self):
        super()._tick()
        if self.armed: 
            my_pos = self.node.position

            for zombie in self.getactivity().zombies:
                if not zombie or not zombie.node or not zombie.is_alive():
                    continue
                
                z_pos = zombie.node.position
                dist_x = abs(z_pos[0] - my_pos[0])
                dist_z = abs(z_pos[2] - my_pos[2])

                if dist_z < 0.4 and dist_x < 1.2:
                    self.explode()
                    break
    def on_shot(self):
        pass
        # we handle our own thing.
  
class CherryBomb(Plant):
    # we dont care about toughness since we explode instantly
    name = 'CherryBomb'
    cost = 150
    recharge = 50
    def __init__(self, position):
        super().__init__(position)
        self.explode_sound = bs.getsound('pvz/cherrybomb')
        # We start unarmed.
        self.node.mesh = bs.getmesh('pvz/cherrybomb')
        self.node.color_texture = bs.gettexture('pvz/cherrybombColor')
        self.node.mesh_scale = 0.5
        bs.animate(self.node, 'mesh_scale', {0: 0.5, 0.14: 0.6, 0.3: 0.76}) 
        bs.timer(0.3, self.explode)
    
    def explode(self):
        if not self.node:
            return
        pos = self.node.position
        self.handlemessage(bs.DieMessage(True))
        PopupText(
            'KABOOM!', position=pos, color=(1, 0, 0), scale=1.5
        ).autoretain()
        # Explode
        self.explode_sound.play(position=pos)
        from bascenev1lib.game.pvz import ZombieAttackMessage
        for zombie in self.getactivity().zombies:
            if not zombie or not zombie.node: continue
            
            z_dist = ((zombie.node.position[0]-pos[0])**2 + 
                      (zombie.node.position[2]-pos[2])**2)**0.5
            
            if z_dist < 2: # Kill everoyne around us
                zombie.handlemessage(ZombieAttackMessage(zombie, 1800))
        