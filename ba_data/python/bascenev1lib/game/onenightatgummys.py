
""" 
i am getting to it (eventually... ):eyes: 
Single-player gamemode where you survive animatronics.
"""
from __future__ import annotations

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)


from typing import TYPE_CHECKING, override
import bascenev1 as bs
import random
from enum import Enum
if TYPE_CHECKING:
    from typing import Any, Sequence


class RenderEngine(bs.Actor):
    """The render engine. This is used to render the game. 
    It is also used to handle the camera and other visual aspects of the game."""
    def __init__(self):
        super().__init__()
        self.active = True
        self.nodes: list[bs.NodeVisualizer] = []
        self.gamestate: GameState = None
    
    def start_game(self):
        self.gamestate = GameState.IN_GAME
    
        self.background = bs.newnode('image', attrs=dict(
            texture=bs.gettexture('black'),
            fill_screen=True,

        ))
        
        



    def handlemessage(self, msg):
        if isinstance(msg, AnimatronicMoved):
            print(f"{msg.who.name} moved to room {msg.room}")
        elif isinstance(msg, bs.DieMessage):
            for node in self.nodes:
                node.delete()
        return super().handlemessage(msg)

class GameState(Enum):
    MAIN_MENU = 0
    IN_GAME = 1
    LOADING = 2

class AnimatronicMoved:
    """Message sent when an animatronic moves."""
    def __init__(self, who: Animatronic, room: int):
        self.who = who
        self.room = room
    
    
class Animatronic(bs.Actor):
    def __init__(self, name: str, difficulty: int = 10):
        super().__init__()
        self.name = name
        self.active = True
        self.difficulty = difficulty
    
        # for now we don't create a node.
        # we'll create a node when visible in the cameras, and delete it when not visible.
        self.node: bs.Node | None = None
        self.tick_timer = bs.Timer(0.1, self._tick, repeat=True)
    
    # Make it visual lol
    def getactivity(self) -> OneNightAtGummysGame:
        return super().getactivity()
    
    def _tick(self):
        if not self.active: 
            return
        rand = 20 / random.random()
        a = self.difficulty
        
        if a >= rand:
            self.getactivity().handlemessage(
                AnimatronicMoved(self, 5)
            )
        pass

    def delete(self):
        self.tick_timer=None
        self.node.delete()
        self.active = False
    
    def handlemessage(self, msg):
        if isinstance(msg, bs.DieMessage): 
            self.delete()
        else: 
            return super().handlemessage(msg)
        return None
    
        
        




# ba_meta export bascenev1.GameActivity
class OneNightAtGummysGame(bs.GameActivity[bs.Player, bs.Team]):
    """A single-player gametype where a 
    player has to survive moving animatronics."""

    name = 'One Night at Gummy\'s'
    description = ''

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = []
        return settings



    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # (Pylint Bug?) pylint: disable=missing-function-docstring
        return []

    def __init__(self, settings: dict, twoplayer: bool = False):
        settings['map'] = 'The Pad'
        super().__init__(settings)
        
 
        


        self.default_music = (
            bs.MusicType.MENU
        )
        

        self.non_collide_mat = bs.Material()
        self.non_collide_mat.add_actions(
            conditions=('they_have_material', self.non_collide_mat),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
                ('modify_part_collision', 'use_node_collide', False),
            ),
        )
        # One night (at gummy's)
        self.night = 1
        self.gamestate = GameState.IN_GAME


        
    @override
    def get_instance_description(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''

    @override
    def get_instance_description_short(self) -> str | Sequence:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        return ''


    @override
    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return False
 
    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.render_engine = RenderEngine()
        self.assign_menu_controls()
    

    def assign_menu_controls(self):
        player = self.players[0]
        player.resetinput()
        player.assigninput(bs.InputType.LEFT_PRESS, self.menu_move_left)
        player.assigninput(bs.InputType.RIGHT_PRESS, self.menu_move_right)
        player.assigninput(bs.InputType.UP_PRESS, self.menu_move_up)
        player.assigninput(bs.InputType.DOWN_PRESS, self.menu_move_down)

    def assign_gameplay_controls(self):
        player = self.players[0]
        player.resetinput()
        player.assigninput(bs.InputType.PUNCH_PRESS, self.interact_left_door)
        player.assigninput(bs.InputType.RIGHT_PRESS, self.interact_right_door)
        player.assigninput(bs.InputType.DOWN_PRESS, self.interact_camera)
        
    def interact_left_door(self):
        pass
    def interact_right_door(self):
        pass
    def interact_camera(self):
        pass

    def menu_move_left(self):
        pass
    def menu_move_right(self):
        pass
    def menu_move_up(self):
        pass
    def menu_move_down(self):
        pass

       

    @override
    def spawn_player(self, player: bs.Player):
        return None 

    @override
    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, AnimatronicMoved):
            # we can also move over the message to the render
            # engine, where it'll handle that visually 
            if self.render_engine:
                self.render_engine.handlemessage(msg)
        return super().handlemessage(msg)


    @override
    def end_game(self) -> None:
        from gummyoverhaul._singleplayergame import SinglePlayerSession  
        assert isinstance(self.session, SinglePlayerSession)
        self.session.return_to_main_menu()
