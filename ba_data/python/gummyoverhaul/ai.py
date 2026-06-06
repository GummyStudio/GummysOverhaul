"""2026 March 28: JEESUS this is old as FUCK. im so glad i get to fix this bugy ai"""

""" Ai guy idk"""
import math
import random
from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
import babase
from bascenev1lib.mainmenu import MainMenuActivity

from bascenev1lib.actor import (
    powerupbox, bomb, flag
)

#to spawn these mfs copy and paste this into console or any scripts
# from gummyoverhaul.ai import AIBot; AIBot()
# spam from gummyoverhaul.ai import AIBot; AIBot(); 
# 8 player from gummyoverhaul.ai import AIBot; AIBot();AIBot();AIBot();AIBot();AIBot();AIBot();AIBot();AIBot(); 
# from gummyoverhaul.ai import AIBot;AIBot(team='Red');AIBot(team='Blue');AIBot(team='Red');AIBot(team='Blue');AIBot(team='Red');AIBot(team='Blue');AIBot(team='Red');AIBot(team='Blue')


# from gummyoverhaul.ai import AIBot; AIBot(team='Red')
#from gummyoverhaul.ai import AIBot; AIBot(team='Red');



# little warning: you're gonna have to restart your game if u put them in a
# multiplayer game

# this doesnt work because expire() lol, you can put them anywhere now

max_fall = -1.72


class AIBot(Spaz):
    """ Cool lil ai thing to kill people"""
    def __init__(self, respawn_time: int = 3, target_only_players: bool = False, sight: int = 3, team: str = None, character: str = None, color=None, highlight=None, name=None):


        # NOTE: If you're using teams mode, no players are allowed to join or else they break.
        if team is None:
            self.team = None
        else:
            if not team == 'Red' and not team == 'Blue':
                self.team = None
                print("Team must be either 'Red' or 'Blue'")
            else:
                self.team = team

        self.restime = respawn_time
        self.sight = sight
        self.onlyp = target_only_players
        if self.team == 'Red':
            self.color = (1, 0, 0)
        elif self.team == 'Blue':
            self.color = (0, 0, 1)
        else:
            self.color = (random.random(), random.random(), random.random()) if color is None else color
        self.highlight = (random.random(), random.random(), random.random())  if highlight is None else highlight
        self.node = False
        from bascenev1lib.actor.spazappearance import get_appearances
        characters = get_appearances()

        self.name = random.choice(bs.get_random_names()) if name is None else name
        self.character = random.choice(characters) if character is None else character
        self.respawning = False
        self.ishedead = False
        activity = self.getactivity()
        if not activity:
            return
        
        from bascenev1lib.mainmenu import MainMenuActivity

        
        
        
       
        self.epicactivity = activity

        self.map = activity.map
        self.def_pos = self.map.get_flag_position(None)
        if self.team == 'Red':
            start_position = self.map.get_start_position(1)
        elif self.team == 'Blue':
            start_position = self.map.get_start_position(0)
        else:
            pos_box = random.choice(self.map.ffa_spawn_points)
            
            try:
                start_position = (random.randrange(int(pos_box[0]),int(pos_box[1])), random.randrange(int(pos_box[2]),int(pos_box[3])) + 5, random.randrange(int(pos_box[4]),int(pos_box[5]))) 
            except: 
                
                start_position = self.map.get_start_position(random.randint(1, 8))
        if not isinstance(bs.get_foreground_host_activity(), MainMenuActivity):
            bs.getsound('spawn').play()
        super().__init__(
                        color=self.color,
                        highlight=self.highlight,
                        character=self.character,
                        demo_mode=True,
                        )

        
        
        self.set_bomb_count(1)
        self.fake_team = self.team
        self.handlemessage(bs.StandMessage(start_position, 90))
        self.bomb_type = self.default_bomb_type ='normal'

        # Remove sounds if its the main menu
        if isinstance(self.epicactivity, MainMenuActivity):

            self.node.jump_sounds = [bs.getsound('nothing')]
            self.node.attack_sounds = [bs.getsound('nothing')]
            self.node.impact_sounds = [bs.getsound('nothing')]
            self.node.death_sounds = [bs.getsound('nothing')]
            self.node.pickup_sounds = [bs.getsound('nothing')]
            self.node.fall_sounds = [bs.getsound('nothing')]
        else:
            self.node.name = 'AI ' + self.name
            self.node.name_color = self.color

        # Momentary flash of light.
        light = bs.newnode(
                'light',
                attrs={
                    'position': self.node.position,
                    'radius': 0.5,
                    'height_attenuated': False,
                    'color': self.color,
                },
            )

        bs.animate(
                light, 'intensity', {0.0: 3.0, 
                                     0.2: 0.5, 
                                     0.5: 0.07, 
                                     0.8: 0}
            )
        bs.timer(0.3, light.delete)

           
        self.target = None
        self.mode = None

        self.respawning = False
        # Allow this spaz to do actions
        self.ishedead = False
        
        #if self.epicactivity is None:

        # literally no need for this lfmao
        #self.handlemessage = self.handlemessage_override
        
        bs.timer(0.1, self.action, repeat=True)
        self.award_xp = False
    
    def on_expire(self):
        super().on_expire()
        # i wish i knew about on expire back thne LMFAO
        self.epicactivity = None
        self.map = None

    
        

        

    def handlemessage(self, msg):
        """ Thing to set our target to be someone else! """
        if isinstance(msg, bs.HitMessage):

            node = msg.srcnode

            if node is not None:
            # get spaz object from node
                attacker = node.getdelegate(type=Spaz)
            else:
                attacker = False
            if attacker:
                self.target = attacker

        elif isinstance(msg, bs.PickedUpMessage):

            bs.timer(0.5, self.panic)
            bs.timer(0.7, self.punch)
        elif isinstance(msg, bs.DroppedMessage):
            'I want a use for this.'
        elif isinstance(msg, bs.DieMessage):
            # Thats just the way to tell us to fuck off and never return lol
            if msg.immediate:
                return
            if self.respawning or not self.epicactivity:
                return
            self.respawn()
            # make sure we die (The touch of midas fucking hate you)
            bs.timer(0.2, bs.Call(setattr, self.node, 'dead', True))
            bs.timer(3, self.node.delete)

        super().handlemessage(msg)
        
    

    def get_alive_viable_targets(self):

        spazes = []
        if not self.onlyp:
            for node in bs.getnodes():
                if node.getnodetype() == 'spaz':  # Check if it's a Spaz node
                    spaz = node.getdelegate(object, False)  # Get th e Spaz object
                    if spaz is not None and spaz != self and spaz.is_alive() and (spaz.fake_team != self.team if self.team else True) and not spaz.node.velocity[2] < max_fall:
                        spazes.append(spaz)
        else:
            for player in self.players:
                if player.is_alive():
                    spazes.append(player)

        return spazes

    def get_closest_alive_viable_target(self, radius: int = 2):

        target = []
        if not self.onlyp:
            for node in bs.getnodes():
                if node.getnodetype() == 'spaz':  # Check if it's a Spaz node
                    spaz = node.getdelegate(object, False)  # Get the Spaz object
                    if spaz is not None and spaz != self and spaz.is_alive() and math.dist(self.node.position, spaz.node.position) <= radius and (spaz.fake_team != self.team if self.team else True) and not spaz.node.velocity[2] < max_fall:
                        target = spaz
        else:
            for player in self.players:
                if player.is_alive() and math.dist(self.node.position, player.actor.node.position) <= radius and not spaz.node.velocity[2] < max_fall:
                    target.append(player)
        return target


    def action(self):
        if not self.epicactivity or not self.is_alive() or self.node is None:
            return

      
        if random.random() < 0.08:
            return 

        self.players = self.epicactivity.players
        alive_players = self.get_alive_viable_targets()
        
       
        if (self.target is None or not self.target.is_alive() or 
                self.target == self or random.random() < 0.05):
            self.target = random.choice(alive_players) if alive_players else None

        # human like wobbyel because why not
        wobble_x = math.sin(bs.time() * 5.0) * 0.2
        wobble_z = math.cos(bs.time() * 5.0) * 0.2

        
        
        if self.will_spaz_fall():
            self.move_to_target(self.get_target_by_pos(self.def_pos))
            if random.random() < 0.5: self.jump()
            self.on_run(value=1.0)
            return

        # we have an ass thingy or,  cursed go kill em
        if (self._cursed or self.ass_bomb) and self.target:
            self.move_to_target(self.get_target_by_pos(self.target.node.position))
            self.on_run(value=1.0)
            self.node.move_left_right += wobble_x 
            if random.random() < 0.1: self.punch()
            if self.get_target_dist() < 2.0: self.bomb()
            return

        
        is_holding_flag = (self.node.hold_node and self.node.hold_node.getdelegate(flag.Flag))

        if self.target:
            t_pos = self.target.node.position
            dist = self.get_target_dist()

           
            
            # wher are  you going
            if random.random() < 0.2:
                    self.node.move_left_right = wobble_x * 5
                    self.node.move_up_down = wobble_z * 5
            else:
                self.move_to_target(self.get_target_by_pos(t_pos))
            self.node.move_left_right += wobble_x
            self.node.move_up_down += wobble_z

            # press anyhihtng
            if dist < 2.0:
                if random.random() < 0.8: self.punch()
                if random.random() < 0.6: self.jump()
                if random.random() < 0.1: self.grab()
            
            # bomba
            if random.random() < 0.03 and not self.node.hold_node and not is_holding_flag:
                self.bomb()
            
                delay = 0.1 if random.random() < 0.75 else 2.5 
                bs.timer(delay, self.throw)

        # Powerup nearby? dont mind if i do
        if random.random() < 0.9:
            pu_pos = self.get_nearby_powerups(range=self.sight*1.2)
            if pu_pos and not is_holding_flag:
                self.move_to_target(self.get_target_by_pos(pu_pos))

        self.on_run(value=1.0 if random.random() < 0.4 else 0.3)


        if self.node.hold_node and not is_holding_flag and random.random() < 0.02:
            self.throw()

    def will_spaz_fall(self):
        # Get the Spaz's current position
        current_position = self.node.position
        velocity = self.node.velocity
    
        # Simulate the next position based on the vertical component of the velocity

        # We only care about the Y position.
        next_position = current_position[1] + velocity[1] + (velocity[1] * 30 if self.get_flag_position() is not None else 12)

        

        # Check if the next position will lead us to fall.
        if next_position < 0: 
            return True 
        else:
            return False
        
    def mine_punch(self):
        bs.timer(0.1, self.jump)
        bs.timer(0.16, self.throw)
        bs.timer(0.21, self.punch)

    def throw(self):
        if self:
            if self.node.hold_node:
                self.jump()
                self.bomb()
                    
    def grab(self): 
        if self:
            self.on_pickup_press()
            self.on_pickup_release()
    def bomb(self):
        if self:
            self.on_bomb_press()
            self.on_bomb_release()

    def panic(self):
            self.on_run(value=0)
            self.move_to_target(self.get_target_by_pos(self.def_pos))
            bs.timer(2.2, self.punch)

    def punch(self):
        if self:
            self.on_punch_press()
            self.on_punch_release()
    
    def jump(self):
        if self:
            self.on_jump_press()
            self.on_jump_release()
        
    def get_flag_node(self):
        for node in bs.getnodes():
            # ficed!
            if node.getdelegate(flag.Flag):  # Check if it's a flag node
                return node  # Return the flag node
        return None

    def get_flag_position(self):
        for node in bs.getnodes():
            # fixed!
            if node.getdelegate(flag.Flag): # Check if it's a flag node
                return node.position  # Return the flag's position

        return None  # No flag found

    
    def get_nearby_powerups(self, range: float = 3):
        closest_powerup = None
        for node in bs.getnodes():

                # fixed!
                if node.getdelegate(powerupbox.PowerupBox):  # Check if it's a powerup node
                    powerup_position = node.position # Get the powerup's position
                    spaz_position = self.node.position  # Get the spaz's position
            
                    # Calculate the distance between the Spaz and the powerup
                    distance = math.dist(spaz_position, powerup_position)
            
                    if distance <= range:
                        closest_powerup = powerup_position
              
        return closest_powerup
    
    def get_nearby_bomb(self, radius=2.0):
        """Returns the position of the nearest bomb within the given radius, or None if none are found."""
        spaz_pos = self.node.position if self.node else None
        if spaz_pos is None:
            return None

        for node in bs.getnodes():
            if node.getdelegate(bomb.Bomb):  # Check if it's a bomb node
                bomb_pos = node.position
                if math.dist(spaz_pos, bomb_pos) <= radius:
                    return bomb_pos  # Return position of the first bomb found

        return None  # No bombs within the radius

    def time_jump(self):
        self.jump()

        bs.timer(0.28, self.jump)
        

    def get_target(self):
        if self.ishedead or self.node is None:
            pos = self.def_pos
        else:
            pos = self.node.position

        if self.target is None or not self.target.is_alive():
            tpos = self.def_pos
        else:
            if self.target.node is None:
                tpos = self.def_pos
            else:
                tpos = self.target.node.position

        our_pos = bs.Vec3(pos[0], 0, pos[2])
        target_pt_raw = bs.Vec3(*tpos)
        diff = target_pt_raw - our_pos
        diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
        val = diff.normalized()
        return val
    
    def get_target_by_pos(self, tpos):
        if self.ishedead or self.node is None:
            pos = self.def_pos
        else:
            pos = self.node.position

        our_pos = bs.Vec3(pos[0], 0, pos[2])
        target_pt_raw = bs.Vec3(*tpos)
        diff = target_pt_raw - our_pos
        diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
        val = diff.normalized()
        return val
    
    def get_target_dist(self):
        if self.ishedead or self.node is None:
            pos = self.def_pos
        else:
            pos = self.node.position

        if self.target is None or not self.target.is_alive():
            tpos = self.def_pos
        else:
            if self.target is None or not self.target.is_alive():
                tpos = self.def_pos
            else:
                tpos = self.target.node.position

        our_pos = bs.Vec3(pos[0], 0, pos[2])
        target_pt_raw = bs.Vec3(*tpos)
        diff = target_pt_raw - our_pos
        diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
        val = diff.length()
        return val
    
    def get_0x0(self):
        if self.ishedead or self.node is None:
            pos = self.def_pos
        else:
            pos = self.node.position
        
        our_pos = bs.Vec3(pos[0], 0, pos[2])
        target_pt_raw = bs.Vec3(*self.def_pos) # our target is the flag default position.
        diff = target_pt_raw - our_pos
        diff = bs.Vec3(diff[0], 0, diff[2])  # Don't care about y.
        val = diff.normalized()
        return val

    def move_to_target(self, target):
        if target is None:
            self.node.move_left_right = 0
            self.node.move_up_down = 0
        else:
            if random.random() < 0.04:
                if self:
                    self.node.move_left_right = self.get_0x0().x
                    self.node.move_up_down = -self.get_0x0().z 
            else:
                if self:
                    self.node.move_left_right = target.x
                    self.node.move_up_down = -target.z 
    
    def flee_from_target(self, target):

        if target is None:
            self.node.move_left_right = 0
            self.node.move_up_down = 0
        else:
            if self:
                self.node.move_left_right = target.x * -1
                self.node.move_up_down = -target.z  * -1
    
    def respawn(self):
        try:
            self.getactivity()
        except: return
        if not self.epicactivity:
            if self.node:
                self.node.delete()
                self.node = None

            return

        if not self.respawning:
            time = self.restime
            self.ishedead = True
            self.respawning = True
            self._dead = True
            def s():
                AIBot(name=self.name, color=self.color, highlight=self.highlight, character=self.character)

            if self.epicactivity:
               
                bs.timer(time, s)
            # alright and uh.. just die.
            self.on_expire()
            
    
    def _activity(self):
        return bs.get_foreground_host_activity()
    




# from gummyoverhaul.ai import AISpawnSystem; AISpawnSystem.spawn_teams()
class AISpawnSystem:

    def spawn_teams():
        for i in range(4):
            AIBot(team='Red')
            AIBot(team='Blue')
