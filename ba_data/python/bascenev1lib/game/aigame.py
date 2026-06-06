# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
from gummyoverhaul.ai import AIBot
import random
if TYPE_CHECKING:
    from typing import Any, Sequence
from bascenev1lib.actor.flag import (
    Flag,

)




# ba_meta export bascenev1.GameActivity
class BotGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'Bots'
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
        settings['map'] = random.choice(['Doom Shroom', 'Courtyard', 'Rampage'])
        super().__init__(settings)
        
 
        


        self.default_music = (
            bs.MusicType.DEFEND
        )
        self.flag: Flag = None

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
    def spawn_flag(self):
        if self.flag:
            return
        self.flag = Flag()
        self.flag = None
    @override
    def on_begin(self) -> None:
        super().on_begin()
        self.setup_standard_powerup_drops()
        for _ in range(5):
            b=AIBot(respawn_time=0.5, character=None)
            # whatever
            b.award_xp = True

    def spawn_player(self, player):
        pos_box = random.choice(self.map.ffa_spawn_points)
        try:
                start_position = (random.randrange(int(pos_box[0]),int(pos_box[1])), random.randrange(int(pos_box[2]),int(pos_box[3])) + 5, random.randrange(int(pos_box[4]),int(pos_box[5]))) 
        except: start_position = self.map.get_start_position(random.randint(1, 8))

        spaz = self.spawn_player_spaz(player, start_position)
        return spaz




    @override
    def handlemessage(self, msg: Any) -> Any:
        # (Pylint Bug?) pylint: disable=missing-function-docstring
        if isinstance(msg, bs.PlayerDiedMessage):
  
            self.respawn_player(msg.getplayer(bs.Player), 3.0)
        else:
            return super().handlemessage(msg)
        return None

    @override
    def end_game(self) -> None:
        from gummyoverhaul._singleplayergame import SinglePlayerSession  
        assert isinstance(self.session, SinglePlayerSession)
        self.session.return_to_main_menu()
