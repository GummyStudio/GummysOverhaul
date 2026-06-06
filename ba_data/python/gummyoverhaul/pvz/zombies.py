
import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz
from typing import Any
from bascenev1lib.gameutils import SharedObjects
import random
from bascenev1lib.actor.popuptext import PopupText


class Limb(bs.Actor):
    """ zombie libm lol """
    def __init__(self, position: tuple[float, float, float], arm_mesh: bs.Mesh, color_texture: bs.Texture):
        super().__init__()
        self.node: bs.NodeVisualizer=bs.newnode(
            'prop',
            delegate=self,
            attrs={
                    'position': position,
                    'velocity': (random.uniform(-3, 3),12,random.uniform(-3, 3)),
                    'mesh': arm_mesh,
                    'light_mesh': None,
                    'body': 'sphere',
                    'body_scale': 0.2,
                    'mesh_scale': 1,
                    'shadow_size': 0.44,
                    'color_texture': color_texture,
                    'reflection': 'powerup',
                    'reflection_scale': [0.0],
                    'gravity_scale': 2,
                     'materials': [self.getactivity().non_collide_mat], 
                },
        )
        self.lifetime = 12
        bs.getsound('pvz/limbs_pop').play(position=self.node.position)   
      
        bs.timer(self.lifetime, bs.Call(self.handlemessage, bs.DieMessage()))
    
    def handlemessage(self, msg: Any) -> Any:

        if isinstance(msg, bs.DieMessage):
            if not self.node:
                return
            if msg.immediate:
                self.node.delete()
            else:
                bs.animate(self.node, 'mesh_scale', {0: 0.0, 0.6: 0.1,1: 0})
                bs.timer(1, self.node.delete)
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage(True))
        else:
            return super().handlemessage(msg)     
        return None 

class Zombie(Spaz):

    max_hp = 190
    max_armor = 0

    speed = 0.15
    dmg = 100
    

    def __init__(self,position: tuple[float, float, float], character: str = 'Spaz'):
        super().__init__((0, 0.8, 0), (0, 0.2, 0), character, None, False, False, False, True, None)
        self.node.handlemessage(bs.StandMessage(position, -90))
        self.node.is_area_of_interest = False
        self.hp = self.max_hp    
        self.armor = self.max_armor     
        from gummyoverhaul.pvz.plants import Plant
        # Used for hitsounds if u got armor
        self.hit_sound = None
        self.eat_sounds =  [
                bs.getsound('pvz/chomp'),
                bs.getsound('pvz/chomp2'),
            ]
        self.movement_mult = 1.0


        

        self.is_eating = False
        self.allow_eating = True
        self.target_plant:Plant = None
        self.bite_timer = None
        

        self.node.materials += (self.getactivity().non_collide_mat,)
        self.node.roller_materials += (self.getactivity().non_collide_mat,)
        self.node.extras_material += (self.getactivity().non_collide_mat, )   
        # we dont have armor so like no
        if self.max_armor:
            self.armor_hp = bs.newnode(
                    'shield',
                    owner=self.node,
                    attrs={'radius': 0},
            )
            self.node.connectattr('position_center', self.armor_hp, 'position')
            self.armor_hp.always_show_health_bar = True
        else:
            self.armor_hp = bs.Node(None)
       
        

        self.impact_scale = 0.0
        self.no_armor_head: bs.Mesh = None
        self.armor_head: bs.Mesh = None

        # uh no
        self.award_xp = False
        self.no_more_limb = False
        self.no_more_hat = False
        self.already_eating = False
        self.force_crit = True
        self.force_crit_chance  = 9999099999
        self.tick_timer = bs.Timer(0.1, self._tick, repeat=True)

    def _tick(self) -> None:
        if not self.is_alive():
            return
        
        if self.is_eating:
            if not self.target_plant or not self.target_plant.node:
                self._stop_eating()
            else:
                self.node.move_left_right = 0 
                return

        self._check_for_plants()
        
        if not self.is_eating:
            self.node.move_left_right = -self.speed * self.movement_mult

    def eat(self):
        if not self.node:
            return
        
        from bascenev1lib.game.pvz import PlantAttackMessage
        self.node.pickup_pressed =True
        self.node.pickup_pressed=False
        random.choice(self.eat_sounds).play(position=self.node.position, volume=0.5)

        if self.target_plant:
            self.target_plant.handlemessage(PlantAttackMessage(self.target_plant, self.dmg))

    def _check_for_plants(self) -> None:
        if not self.is_alive():
            return
        if  not self.allow_eating:
            self._stop_eating()
            return
        z_pos = self.node.position
        
        for plant in self.getactivity().plants:
         
            

            if not plant:
                return
            

        
            if not plant.node:
                continue
                
            p_pos = plant.node.position
            dist_x = z_pos[0] - p_pos[0]
            dist_z = abs(z_pos[2] - p_pos[2])

            if 0.0 < dist_x < 1.0 and dist_z < 0.5:
                self.target_plant = plant
                self._start_eating_loop()
                self.is_eating = True
                break

    def _start_eating_loop(self) -> None:
        if self.is_eating or not self.target_plant:
            return
        self.bite_timer = bs.Timer(0.68, bs.WeakCall(self.eat), repeat=True)

    def _stop_eating(self) -> None:
        self.target_plant = None
        self.bite_timer = None
        self.is_eating = False
        

    def handlemessage(self, msg: Any) -> Any:
        from bascenev1lib.game.pvz import ZombieAttackMessage
        from bascenev1lib.actor.spaz import PickupMessage
        from gummyoverhaul.pvz.plants import ZombieFreezeMessage

        if isinstance(msg, bs.DieMessage):
            # stop it brah.
            self._stop_eating()
            self.armor_hp.delete()
            return super().handlemessage(msg)   

        elif isinstance(msg, ZombieFreezeMessage):
            # Ow.. we have to go slower.
            bs.animate_array(self.node,'color', 3,
                        {
                        0.0:(0,0, 3),
                        msg.duration: self.Dcolor
                        }
                    )
            self.handlemessage(ZombieAttackMessage(msg.zombie, msg.damage))
            self.movement_mult = 0.75
            bs.timer(msg.duration, bs.Call(setattr, self, 'movement_mult', 1))
            

        
        elif isinstance(msg, ZombieAttackMessage):
            if not self.node:
                return
            
            damage_to_apply = msg.damage

            if self.armor > 0:
                if damage_to_apply > self.armor:
                    damage_to_apply -= self.armor
                    self.armor = 0
                else:
                    self.armor -= damage_to_apply
                    damage_to_apply = 0
                
                if self.armor_hp:
                    self.armor_hp.hurt = (
                        1.0 - float(self.armor) / self.max_armor
                    )
            if damage_to_apply > 0:
                self.hp -= damage_to_apply

            
            self.node.handlemessage('flash')
            self.node.hurt = (1.0 - float(self.hp) / self.max_hp)

            if self.armor:
                if isinstance(self.hit_sound, bs.Sound):
                    self.hit_sound.play(position=self.node.position)
                elif isinstance(self.hit_sound, list):
                    random.choice(self.hit_sound).play()

            if self.hp <= self.max_hp * 0.5 and not self.no_more_limb:
                Limb(self.node.position, self.node.forearm_mesh, self.node.color_texture).autoretain()
                self.node.hand_mesh = None
                self.node.forearm_mesh = None
                self.no_more_limb = True

            if self.armor <= 0 and not self.no_more_hat and self.max_armor:
                Limb(self.node.position, self.armor_head, self.node.color_texture).autoretain()
                self.node.head_mesh = self.no_armor_head
                self.no_more_hat = True
                if self.armor_hp:
                    self.armor_hp.delete()
                
            if self.hp <= 0:
                Limb(self.node.position, self.node.head_mesh, self.node.color_texture).autoretain()
                self.node.head_mesh = None
                self.node.style = 'agent'
                self.handlemessage(bs.DieMessage())
        elif isinstance(msg, PickupMessage):
            # ok so the zombies were picking eachohter up lmfao
            return None
        elif isinstance(msg, bs.HitMessage):
            return None
  
        return super().handlemessage(msg)      

# OK define zombies

class BrownCoat(Zombie):
    def __init__(self, position: tuple[float, float, float], character = 'Spaz'):
        # Standard stats
        super().__init__(position=position, character=character)
        self.node.color = (0.6, 0.4, 0.2)

class Conehead(BrownCoat):
    max_armor = 380
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position)
        # a little orange
        self.node.color = (1, 0.5, 0)
        # we have armor, so define it.
        self.no_armor_head = bs.getmesh('neoSpazHead')
        self.armor_head =   bs.getmesh('spiritHead')
        self.node.head_mesh = self.armor_head
        self.hit_sound = [
                bs.getsound('pvz/plastichit'),
                bs.getsound('pvz/plastichit2'),
            ]
        
    
class FlagZombie(BrownCoat):
    # Faster to lead the pack
    speed = 0.2
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position, character='Agent Spaz')
        
class Buckethead(BrownCoat):
    max_armor = 1100
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position)
        self.node.color = (0.5, 0.5, 0.5)
        self.no_armor_head = bs.getmesh('neoSpazHead')
        self.armor_head = bs.getmesh('vrHead')
        self.node.head_mesh = self.armor_head
        self.hit_sound = [
                bs.getsound('pvz/shieldhit'),
                bs.getsound('pvz/shieldhit2'),
            ]

# Custom zombie.
class PoleVaulter(Zombie):
    speed = 0.65
    max_hp = 335
    def __init__(self, position, character = 'Spaz'):

        super().__init__(position, character)
        self.node.color = (1,1,1)
        self.jumped = False
    def _tick(self):

        super()._tick()
        # oh we are eating, fly and stop
        if self.is_eating and not self.jumped:
            self.jumped = True
            bs.getsound('pvz/polevault').play(position=self.node.position)
            self.allow_eating=False
            def eat():
                self.allow_eating=True
            bs.timer(0.5, eat)
            node = self.node
            self.speed = 0.15
            for _ in range(18):
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                    0, 25, 0,
                                                    45, 0.05, 0, 0,
                                                    0, 250, 0)
               
            for _ in range(50):
                    v = (-5, 0, 0)
           
                    
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                            0, 25, 0,
                                            21, 0.05, 0, 0,
                                            v[0]*15*2, 0, v[2]*15*2)
                
class NewsPaper(Zombie):
    speed = 0.14
    max_armor = 150
    def __init__(self, position, character = 'Jack Morgan'):

        super().__init__(position, character)
        self.node.color = (0,0,0)
        self.node.highlight=(1,1,1)
        self.grrr = False
        self.no_armor_head = bs.getmesh('jackHead')
        self.armor_head = None
        self.anger_noises = [
            bs.getsound('pvz/newspaper_rarrgh'),
            bs.getsound('pvz/newspaper_rarrgh2')
        ]
    def _tick(self):

        super()._tick()
        # Uh oh, we lost our armor. time to get angry!
        if not self.armor and not self.grrr:
            self.allow_eating=False
            def GOOO():
                self.speed = 0.65 
                self.allow_eating=True

            PopupText('?', position=self.node.position).autoretain()
            self.speed = 0.0
            self.grrr = True
            self.handlemessage(bs.CelebrateMessage(0.5))
            random.choice(self.anger_noises).play(position=self.node.position)
            bs.getsound('pvz/newspaper_rip').play(position=self.node.position)
            bs.timer(0.5, GOOO)
           
class FootballZombie(BrownCoat):
    max_armor = 1500
    speed = 0.35
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position, character='Kronk')
        self.node.color = (1, 0, 0)
        self.no_armor_head = bs.getmesh('kronkHead')
        self.armor_head = bs.getmesh('bomb')
        self.node.head_mesh = self.armor_head
        self.hit_sound = [
                bs.getsound('pvz/shieldhit'),
                bs.getsound('pvz/shieldhit2'),
            ]
    
class JackinTheBox(Zombie):
    max_hp = 340
    speed = 0.2
    def __init__(self, position: tuple[float, float, float]):
        super().__init__(position=position, character='Mel')
        self.node.color = (1, 1, 1)
        # celebrate forever
        explode_time = random.uniform(5, 7)
        self.uh_oh_sounds =  [
                bs.getsound('pvz/jack_surprise'),
                bs.getsound('pvz/jack_surprise2'),
        ]
        
        
        self.handlemessage(bs.CelebrateMessage(explode_time+0.5))
        bs.timer(explode_time, self.explode)

    
    def explode(self):
        # were dead so no go.
        if not self.is_alive():
            return
        random.choice(self.uh_oh_sounds).play()
        self.speed = 0.0
        def ka_BOOM():
            if not self.node: return
            
            z_pos = self.node.position
            bs.emitfx(position=z_pos, scale=2.0, count=20, spread=0.5, chunk_type='spark')
            bs.getsound('pvz/explosion').play(position=z_pos)
        
            for plant in self.getactivity().plants:
                if not plant or not plant.node:
                    continue
                
                p_pos = plant.node.position
                dist = ((z_pos[0]-p_pos[0])**2 + (z_pos[2]-p_pos[2])**2)**0.5
                
                if dist < 1.8:
                    plant.handlemessage(bs.DieMessage(True))
            
            self.handlemessage(bs.DieMessage())
        self.handlemessage(bs.CelebrateMessage(0.5, 'left'))
        bs.timer(0.5, ka_BOOM)

    





