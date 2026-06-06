# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import random
import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects
import math

if TYPE_CHECKING:
    from typing import Any, Sequence

class ImpactMessage:
    """e"""



# ba_meta export bascenev1.GameActivity
class LimboGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'Limbo'
    description = ''
    allow_pausing = False

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
        settings['map'] = 'Doom Shroom'
        super().__init__(settings)
        
 
        


        self.default_music = (
            bs.MusicType.LIMBO
        )
        self.ended = False
        self.touched = False
        self.bruh_timer: bs.Timer | None = None
        self.color = (0, 0, 0)
        

        self.shields = []
        self.correct_index = 0
        self.max_shuffles = 30
        self.shuffles = 0 
        self._shield_positions: list[tuple[float, float, float]] = []




        
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
 
    

    def on_begin(self):
        super().on_begin()
        bs.timer(0.1, self.tick, repeat=True)

        count = 8#10
        self.correct_index = random.randrange(count)

        # spawn in a circle
        radius = 4.0
        center = (0, 2.5, -4)

        for i in range(count):
            angle = (360.0 / count) * i
            rad = angle * (3.14159 / 180.0)

            pos = (
                center[0] + radius * (math.cos(rad)),
                center[1],
                center[2] + radius * (math.sin(rad)),
            )

            n = bs.newnode(
                "shield",
                attrs=dict(
                    color=(0.2, 1, 0.2) if i == self.correct_index else (1, 0.2, 0.2),
                    radius=1.0,
                ),
            )

            n.position = pos
            self.shields.append(n)
            self._shield_positions.append(pos)

       
        bs.timer(4.5, self._start_shuffle)
        self.players[0].actor.on_hold_position_press()
    
    def tick(self):
        if not self.players[0].actor.is_alive():
            self.end_game()

    
       

    def _start_shuffle(self):
        """Continuously shuffle shield positions."""
        for s in self.shields:
            bs.animate_array(
                s,
                "color",
                3,
                {
                    0.0: s.color, 
                    0.3: (0.5, 0.5, 0.5)
                }
            )
            
        bs.timer(0.3, bs.WeakCall(self._shuffle_once), repeat=True)

    def _shuffle_once(self):
        if not self.shields or not all(s.exists() for s in self.shields):
            return
        
        if self.shuffles == self.max_shuffles:
            if not self.ended:

                self.ending()
            self.ended = True
            return
        self.shuffles += 1

        new_positions = list(self._shield_positions)
        random.shuffle(new_positions)

       

        for shield, new_pos in zip(self.shields, new_positions):
            bs.animate_array(
                shield,
                "position",
                3,
                {
                    0.0: shield.position, 
                    0.2: new_pos
                }
            )

        self._shield_positions = new_positions

    
    
        
    
    def ending(self):
        for s in self.shields:
            bs.animate_array(
                s,
                "color",
                3,
                {
                    0.0: s.color, 
                    0.3: tuple([random.random() for _ in range(3)])
                }
            )
        self.players[0].actor.on_hold_position_release()
        self._start_distance_check()
        self.bruh_timer = bs.Timer(16, self._on_wrong)
        
    
    def _start_distance_check(self):
        # check every 0.1s
        bs.timer(0.1, bs.WeakCall(self._check_player_distance), repeat=True)

    def _check_player_distance(self):

        # get player spaz node
        if not self.players or not self.players[0].actor:
            return

        pnode = self.players[0].actor.node
        if not pnode or not pnode.exists():
            return

        ppos = pnode.position

        for i, shield in enumerate(self.shields):
            if not shield.exists():
                continue

            spos = shield.position

            dx = ppos[0] - spos[0]
            dy = ppos[1] - spos[1]
            dz = ppos[2] - spos[2]

            dist = math.sqrt(dx*dx + dy*dy + dz*dz)

            if dist <= 1.0 and not self.touched: 
                self.touched = True
                for s in self.shields:
                    if shield == s:
                        self.color = s.color
                        #continue
                    s.delete()
                if i == self.correct_index:
                    self._on_correct()
                else:
                    self._on_wrong()
                return
 
    def _on_correct(self):
        self.bruh_timer = None
        bs.cameraflash()
        self.players[0].actor.handlemessage(bs.CelebrateMessage(14))
        bs.getsound('score').play()
        self.players[0].actor.equip_shields(color=self.color)


        bs.timer(5, self.end_game)

    def _on_wrong(self):
        self.players[0].actor._cursed = True
        self.players[0].actor.curse_explode()


       

    @override
    def spawn_player(self, player: bs.Player):
        spaz = self.spawn_player_spaz(player, (0, 2.5, -4))
        spaz.connect_controls_to_player(enable_bomb=False, enable_punch=False)
        spaz.award_xp = False
       
        

    
        return spaz


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
