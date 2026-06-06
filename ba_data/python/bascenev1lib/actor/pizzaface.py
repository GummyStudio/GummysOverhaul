"""Module for the Pizzaface thingy"""
import bascenev1 as bs
ok lol
class PizzaFace(bs.Actor):
    def __init__(self):
        super().__init__()
        # im getting code hollon

    def move_tick(self):
        # check distance between us and spaz.
        our_pos = self.node.position
        spaz_pos = self.actor().node.position
        dx = spaz_pos[0] - our_pos[0]
        dy = spaz_pos[1] - our_pos[1]
        dz = spaz_pos[2] - our_pos[2]

        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        # our strength is based on distance, 
        # so we get stronger far away.
        strength = dist / 5
        # just always move towards spaz
        self.node.handlemessage(
            'impulse',
            our_pos[0],
            our_pos[1],
            our_pos[2],
            0, 0, 0,
            80, 80, 0,
            0,
            dx * strength,
            dy * strength,
            dz * strength,
        )
        self.update_target