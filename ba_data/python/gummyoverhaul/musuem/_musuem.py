from typing import override, Any
import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects


class MusuemActivity(bs.Activity[bs.Player, bs.Team]):
    """Activity showing the rotating main menu bg stuff."""

    _stdassets = bs.Dependency(bs.AssetPackage, 'stdassets@1')



    def __init__(self, settings: dict):
        super().__init__(settings)
        
        
        
        self._host_is_navigating_text: bs.NodeActor | None = None
        self._room_actors: list[bs.Actor] = []
        self.terrain_nodes = []
        self.show_hitboxes = False
        self.shared = SharedObjects.get()
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))
     
       
        self.rooms = {

            'entrance': {
                'load_objects_call': self.load_entrance_objects,
                'meshes': [
                    {
                        'mesh': bs.getmesh,
                        'collidemesh': bs.getcollisionmesh,
                        'materials': [],
                        'color_texture': bs.gettexture,
                        'background': False,
                    }
                ],
                'entrances': {
                    'exit': {
                        'position': (0, 0, 0),
                        'size': (5, 5, 5),
                        'call': self.session.end,
                    }
                },
            },
        }
    def on_expire(self):
        super().on_expire()
        self.rooms = None
    def on_transition_in(self):
        super().on_transition_in()
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': bs.getmesh('tipTopBG'),
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture('tipTopBGColor')})
        self.load_room('entrance')

        

    def load_entrance_objects(self):
        pass
        
            
    def load_room(self, room_name: str, entrance: str = None):
        for actor in self._room_actors:
            actor.handlemessage(bs.DieMessage())
        for terrain in self.terrain_nodes:
            terrain.delete()
        self._room_actors = []
        self.terrain_nodes = []

        room = self.rooms.get(room_name)
        if room:
            # call loader
            room['load_objects_call']()
        # Kay now make terrain
        for terrain in room['meshes']:
        
            self.terrain_nodes.append(bs.newnode('terrain',
                attrs={
                    'mesh': terrain['mesh'],
                    'collidemesh': terrain['collidemesh'],
                    'materials':  terrain['materials'] + [self.shared.footing_material, self.collision],
                    'color_texture': terrain['color_texture'],
                    'background': terrain['background'],
                }
            ))

        # And now hitboxes
        for entrance_name, entry in room['entrances'].items():
            if entrance == entrance_name:
                # Teleport players here
                pass
            material = bs.Material()
            material.add_actions(
                conditions=('they_have_material', self.shared.player_material),
                actions=(
                    ('modify_part_collision', 'collide', True),
                    ('modify_part_collision', 'physical', False),
                    ('call', 'at_connect', entry['call']),
                ),
            )
            self.terrain_nodes.append(bs.newnode('region',
                attrs={
                    'position': entry['position'],
                    'scale': entry['size'],
                    'type': 'box',
                    'materials': [material],
                }
            ))

            if self.show_hitboxes:
                self.terrain_nodes.append(
                bs.newnode('locator',
                    attrs={'shape': 'box',
                           'position': entry['position'],
                           'color': (1,1,1),
                           'opacity': 1.0,
                           'draw_beauty': True,
                           'size': entry['size'],
                           'additive': False}))
         
    def on_begin(self):
        super().on_begin()
        


        bs.setmusic(None)
    


class MusuemSession(bs.Session):
    """Session that runs the main menu environment."""

    def __init__(self) -> None:
        # Gather dependencies we'll need (just our activity).
        self._activity_deps = bs.DependencySet(bs.Dependency(MusuemActivity))

        super().__init__([self._activity_deps])
        self.setactivity(bs.newactivity(MusuemActivity))
        self.max_players = 1

        



    
        

    @override
    def on_activity_end(self, activity: bs.Activity, results: Any) -> None:
        
        self.end()


     