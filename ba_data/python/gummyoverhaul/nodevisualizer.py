
#from gummyoverhaul.startup import Node
#assert isinstance(self.node, Node)

class NodeVisualizer:
    """ Simply a visualizer, does nothing. """

    def __init__(self):
        self.position: tuple = (0, 0, 0)
        self.velocity: tuple = (0, 0, 0)

        self.text = ''
        self.attach = ''
        self.flashing = False
        self.color: tuple = (0, 0, 0)
        self.behavior_version = 1
        self.density = 0.0
        self.damping = 0.0
        self.body=None
        self.owner=None
        self.max_speed=None
        self.shadow_size=0
        self.body_scale = 0.0
        self.mesh_scale=0.0
        self.mesh = None
        self.demo_mode = False
        self.highlight: tuple = (0, 0, 0)
        self.jump_sounds: tuple = []
        self.attack_sounds: tuple = []
        self.impact_sounds: tuple = []
        self.death_sounds: tuple = []
        self.pickup_sounds: tuple = []
        self.fall_sounds: tuple = []
        self.color_texture = None
        self.color_mask_texture = None 
        self.head_mesh = None 
        self.torso_mesh = None 
        self.pelvis_mesh = None 
        self.upper_arm_mesh = None 
        self.forearm_mesh = None 
        self.hand_mesh = None
        self.upper_leg_mesh = None 
        self.lower_leg_mesh = None 
        self.toes_mesh = None 
        self.style = ''
        self.fly = False
        self.hockey = False
        self.materials: list = []
        self.roller_materials: list = []
        self.extras_material: list =  []
        self.punch_materials: list =  []
        self.pickup_materials: list = []
        self.invincible = False
        self.shattered = False
        self.source_player = None
        self.stick_to_owner = False
        self.sound  = None
        self.radius = 0.0
        self.intensity = 0.0
        self.volume_intensity_scale = 0.0
        self.volume = 0.0
        self.boxing_gloves = False
        self.billboard_opacity = 0.0
        self.billboard_texture = None
        self.boxing_gloves_flashing = False
        self.curse_death_time = 0
        self.frozen = False
        self.dead = False
        self.hurt = 0.0
        self.counter_text = ''
        self.counter_texture = None
        self.hold_body = 0
        self.hold_node: NodeVisualizer | None = None
        self.position_forward: tuple = (0, 0, 0)
        self.hold_position_pressed = False
        self.pickup_pressed = False
        self.jump_pressed = False
        self.punch_pressed = False
        self.move_left_right = 0.0
        self.move_up_down = 0.0
        self.bomb_pressed = False
        self.scale = 0.0

        self.name = ''
        self.name_color: tuple = (0, 0, 0)
        self.host_only = False
        self.client_only = False
        
        self.billboard_cross_out = True
        self.is_area_of_interest: bool
    def add_death_action(self, action):
        """ Stuff that happens when you die? Shrug"""
    def connectattr(self, myattr, their_node, their_attr):
        """ Connect others values to change to ours all the time."""
    def delete(self):
        """ Stop existing in the world. """
    def exists(self) -> bool:
        """ Is our node in existance? """
    def getdelegate(self, delegate, truefalseidk=False):
        """ Returns the class delegate the node is assiosiated with. """
        return delegate()
    def getname(self) -> str:
        """get the name of the node..."""
    def getnodetype(self) -> str:
        """ Get the node type we we're assigned. """
    def handlemessage(self, msg, *args):
        """ Do something, lol! """