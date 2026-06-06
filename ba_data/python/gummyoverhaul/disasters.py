import bascenev1 as bs
import random

# These are disasters that'll be used in bascenev1lib.game.thedisasters.DisasterGame
# They are intendeed to be used at the same time, based on intensity (if intensity reaches max, no more can spawn)
class Disaster:
    """ An event to happen in game, yknow? """

    intensity: int = 1 # Should be ranked on how much resources this event can take, like a shit ton of nodes? around a 4, some props? a 2. etc etc
    timelapse: float = 0.1
    name: str = 'Disaster'

    def __init__(self):
        
        # Load stuff, i dunno
        pass
        
        
    def activate(self):
        pass

    def stop(self):
        """ Stop ticking or idk"""

class PowerupRainDisaster(Disaster):
    """ Rains powerups over time """

    intensity = 2
    timelapse = random.uniform(9, 13)
    name = 'Powerup Rain'
    from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory
    
 
    def __init__(self):
        
        self.running = False
        self._timer = None
        self.timelapse = random.uniform(9, 13)
        

    def _rain_tick(self):
        """One rain event"""
        if not self.running:
            return

        activity = bs.get_foreground_host_activity()
        assert isinstance(activity, bs.Activity)
        if activity is None or activity.expired:
            self.running = False
            return
        

        count = random.randint(5, 9)
        try:
            pos = random.choice(bs.getactivity().players).actor.node.position
        except:
            bs.timer(1.5, self._rain_tick)
            return

        for _ in range(count):
            x = random.uniform(-1, 1)
            z = random.uniform(-1, 1)

            p = self.PowerupBox(
                position=(pos[0]+x, pos[1]+2.5, pos[2]+z),
                poweruptype=self.PowerupBoxFactory().get_random_powerup_type(excludetypes=['what', 'curse']) # insta kills arent fun
            ).autoretain()
            p.node.velocity = (
                random.uniform(-1, 1),
                -3,
                random.uniform(-1, 1)
            )

        self._timer = bs.Timer(random.uniform(1, 3), self._rain_tick)

    def activate(self):
        """Start raining powerups"""
        if self.running:
            return

        self.running = True
        self._rain_tick()

     

    def stop(self):
        """Stops the disaster"""
        self.running = False
        self._timer = None


class MeteorShowerDisaster(Disaster):
    """ Rains explosive meteors (bombs) """
    intensity = 3
    timelapse = random.uniform(10, 15)
    name = 'Meteor Shower'
    from bascenev1lib.actor.bomb import Bomb

    def __init__(self):
       
        self.running = False

    def _tick(self):
        if not self.running:
            return
        
        activity = bs.get_foreground_host_activity()
        
        if activity is None or activity.expired:
            self.running = False
            return
        
        count = random.randint(3, 6)

        for _ in range(count):
            x = random.uniform(-5, 5)
            z = random.uniform(-5, 5)

            b = self.Bomb(
                position=(x, 5.67, z),
                bomb_type='impact',
                velocity=(random.uniform(-2, 2), -5, random.uniform(-2, 2)),
            ).autoretain()
        
        bs.timer(random.uniform(1.0, 2.2), self._tick)

    def activate(self):
        if self.running:
            return
        self.running = True
        self._tick()

    def stop(self):
        self.running = False


class LightningStormDisaster(Disaster):
    """ Random lightning strikes that zap players """
    intensity = 2
    timelapse = random.uniform(10, 14)
    name = 'Lightning Storm'

    from bascenev1lib.actor.bomb import Blast

    def __init__(self):
        self.running = False

    def _strike(self):
        if not self.running:
            return
        
        # reused from ma map
        try:
            y = random.choice(bs.getactivity().players).actor.node.position[1]
         
        except:
            y = random.uniform(6, 4)


            
        
        if random.randint(0, 2) == 0 and len(bs.getactivity().players) != 0:
                    try:
                        playerpos = random.choice(bs.getactivity().players).actor.node.position
                    except:
                       playerpos = (random.uniform(5, -5), y, random.uniform(2, -8))
                    pos = (
                        playerpos[0] + random.uniform(-1.7, 1.7),
                        playerpos[1],
                        playerpos[2] + random.uniform(-1.7, 1.7)
                    )
        else:
            pos = (random.uniform(5, -5), y, random.uniform(2, -8))
            self.Blast(pos, blast_radius=1.5, blast_type='lightning')
           
        bs.timer(random.uniform(2, 4.5), self._strike)

    def activate(self):
        if self.running:
            return
        self.running = True
        self._strike()

    def stop(self):
        self.running = False

class EarthquakeDisaster(Disaster):
    """ Shakes the world and knocks players around """
    intensity = 2
    timelapse = random.uniform(8, 12)
    name = 'Earthquake'
    from bascenev1lib.actor.spaz import Spaz

    def __init__(self):
        self.running = False      
        
    
    def towerparticalsfall(self) -> None:
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=3,
            spread=0.6,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1.7,
            spread=0.9,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=2.3,
            spread=0.9,
            chunk_type='rock',
            )
    def towerparticalsfallS(self) -> None:
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1.7,
            spread=0.9,
            chunk_type='rock',
            )
        bs.emitfx(
            position=(0, 15, 0),
            velocity=(0, -0.3, 0),
            count=int(4.0 + random.random() * 8),
            scale=1,
            spread=0.9,
            chunk_type='rock',
            )

    def _shake(self):
        if not self.running:
            return
        
        activity = bs.get_foreground_host_activity()
        if activity is None or activity.expired:
            self.running = False
            return
        
        bs.camerashake(2)
        self.towerparticalsfall()
        self.towerparticalsfallS()
        
        for node in bs.getnodes():
            assert isinstance(node, bs.NodeVisualizer)
            if not node or not node.exists():
                continue
            
            if node.getnodetype() not in ['prop', 'spaz', 'bomb', 'flag']:
                continue
            

                        
            xforce = 13
            yforce = 2

            if node.getdelegate(self.Spaz):
                if node.getdelegate(self.Spaz).standing:
                    node.handlemessage('knockout', 200)
                    for _ in range(50):
                        v = (random.uniform(-3, 3), random.uniform(1, 3), random.uniform(-3, 3))
                        node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                    0, 25, 0,
                                                    yforce, 0.05, 0, 0,
                                                    0, 20*400, 0)
                            
                        node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                    0, 25, 0,
                                                    xforce, 0.05, 0, 0,
                                                    v[0]*15*2, 0, v[2]*15*2)
            else:
                xforce = 5
                yforce = 0.5
                for _ in range(50):
                    v = (random.uniform(-3, 3), random.uniform(1, 3), random.uniform(-3, 3))
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                0, 25, 0,
                                                yforce, 0.05, 0, 0,
                                                0, 20*400, 0)
                        
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                0, 25, 0,
                                                xforce, 0.05, 0, 0,
                                                v[0]*15*2, 0, v[2]*15*2)
                

        bs.timer(1.6, self._shake)

    def activate(self):
        if self.running:
            return
        self.running = True
        self._shake()

    def stop(self):
        self.running = False



class SpazJumpScareDisaster(Disaster):
    """ Shakes the world and knocks players around """
    intensity = 3
    timelapse = 18
    name = 'Spaz Jumpscare'
    from bascenev1lib.actor.spazbot import SpazBotSet, BomberBot

    def __init__(self):
        from bascenev1lib.actor.spazbot import SpazBot

    
        self.running = False     
        self.spazes: list[SpazBot] = []
        self.set = self.SpazBotSet()

       

    def _tick(self):
        if not self.running:
            return
        
        activity = bs.get_foreground_host_activity()
        if activity is None or activity.expired:
            self.running = False
            return
        
        players = [p for p in activity.players if p.is_alive()]
        if not players:
            bs.timer(0.2, self._tick)
            return

        for spaz in self.spazes:
            if not spaz or not spaz.is_alive() or not spaz.node.exists():
                self.spazes.remove(spaz)
                continue


            spaz.update_ai()

        bs.timer(0.2, self._tick)

    def activate(self):
        if self.running:
            return
        
        for _ in range(random.randint(5, 9)):

            try:
                pos = random.choice(bs.getactivity().players).actor.node.position
            except:
                self.timelapse = 2
                return
            
            self.set._spawn_bot(self.BomberBot, pos=pos)

            spaz = self.set.get_living_bots()[-1]

            
           

            

            self.spazes.append(spaz)


        self.running = True
        self._tick()

    def stop(self):
        self.running = False

        for spaz in self.spazes:
            spaz.handlemessage(bs.DieMessage(True))

        self.spazes.clear()

class FirestormDisaster(Disaster):
    """Spawns multiple fires randomly over the map, creating a firestorm."""

    from bascenev1lib.actor.bomb import Fire
    name = 'Firestorm'
    intensity = 4
    timelapse = 2 + random.uniform(2, 4)
    
    def __init__(self):
        super().__init__()
    
        self._active = False
        self._timer = None
        self._spawn_timer = None

    def _spawn_fire(self):
        
        try:
            pos = random.choice(bs.getactivity().players).actor.node.position
        except:
            self._spawn_timer = bs.Timer(1.5, self._spawn_fire)
            return
        
        x = random.uniform(-2, 2)
        z = random.uniform(-2, 2)
        position = (pos[0]+x, pos[1], pos[2]+z)
        self.Fire(position, duration=random.uniform(1, 2))
        
        self._spawn_timer = bs.Timer(1.5, self._spawn_fire)

    def activate(self):
        if self._active:
            return
        self._active = True
        self._spawn_fire()
        

    def stop(self):
        self._active = False
        self._spawn_timer = None
        self._timer = None