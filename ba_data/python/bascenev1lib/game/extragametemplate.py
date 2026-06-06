# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence




# ba_meta export bascenev1.GameActivity
class TemplateGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'GameName'
    description = ''

    @override
    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        settings = [
        ]



        return settings



    @override
    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        # (Pylint Bug?) pylint: disable=missing-function-docstring
        return []

    def __init__(self, settings: dict):
        settings['map'] = 'The Pad'
        super().__init__(settings)
        
 
        


        self.default_music = (
            bs.MusicType.WII
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

       

    @override
    def spawn_player(self, player: bs.Player):

    
        return



    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring

        
        return super().handlemessage(msg)
        return None

    @override
    def end_game(self) -> None:
        from gummyoverhaul._singleplayergame import SinglePlayerSession  
        assert isinstance(self.session, SinglePlayerSession)
        self.session.return_to_main_menu()
