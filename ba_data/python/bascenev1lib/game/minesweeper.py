# Released under the MIT License. See LICENSE for details.
#
"""DeathMatch game and support classes."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

from typing import TYPE_CHECKING, override

from bascenev1lib.actor.spaz import Spaz
import bascenev1 as bs
import random
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.popuptext import PopupText
import babase

if TYPE_CHECKING:
    from typing import Any, Sequence




# ba_meta export bascenev1.GameActivity
class MinesweeperGame(bs.GameActivity[bs.Player, bs.Team]):
    """A game type based on acquiring kills."""

    name = 'Minesweeper'
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
        settings['map'] = 'MineSweeper'
        super().__init__(settings)
        
 
        


        self.default_music = (
           bs.MusicType.BJPARKCALM
        )
        
        #bs.newnode('sound', attrs=dict(sound=bs.getsound('rain'), volume=8))
        self.board_size = 18
        self.mine_count = random.randint(28, 35)
        self.revealed: set[tuple[int,int]] = set()
        self.mines: set[tuple[int,int]] = set()
        self.tiles: dict[tuple[int,int], bs.Node] = {}
        self.labels: dict[tuple[int,int], bs.Node] = {}
        self.flag_labels: dict[tuple[int,int], bs.Node] = {}
        self.shields: dict[tuple[int,int], bs.Node] = {}
        self.cursor_x = 0
        self.cursor_y = 0
        self.flagged: set[tuple[int,int]] = set()
        self.start_x = -8
        self.start_y = 1
        self.start_z = -10
        self.spacing = 1.0
        self.player_spaz: bs.Actor | None = None
        self.game_over = False
        self.first_click = True


        
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
        size = self.board_size
        self.globalsnode.tint = (0.6, .6 ,.6)


        for gx in range(size):
            for gy in range(size):
                pos = (
                    self.start_x + gx * self.spacing,
                    self.start_y,
                    self.start_z + gy * self.spacing,
                )
                # this isnt evne used, i just wanna have stiles
                node = bs.newnode(
                    'region',
                    attrs={
                        'scale': (0.8, 0.2, 0.8),
                        'type': 'box',
                        'position': pos,
                    },
                )
                shield = bs.newnode(
                    'shield',
                    attrs={
                        'radius': 0.5,
                        'color': (0.23, 0.2, 1.5)
                    },
                )
                node.connectattr('position', shield, 'position')
                self.tiles[(gx, gy)] = node
                self.shields[(gx, gy)] = shield



    def _get_safe_cluster(self, coord: tuple[int,int], max_size: int) -> set[tuple[int,int]]:
        cx, cy = coord
        cluster = {(cx, cy)}
        frontier = [(cx, cy)]
        while len(cluster) < max_size and frontier:
            x, y = frontier.pop(0)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < self.board_size
                        and 0 <= ny < self.board_size
                        and (nx, ny) not in cluster
                    ):
                        cluster.add((nx, ny))
                        frontier.append((nx, ny))
                        if len(cluster) >= max_size:
                            break
        return cluster


    def _reveal_tile(self, coord: tuple[int,int]) -> None:
        if self.game_over:
            return
        if self.first_click:
            self.first_click = False

            # Generate a safe cluster around first click (up to 2 tiles)
            safe_tiles = self._get_safe_cluster(coord, max_size=2)

            # Place mines outside the safe cluster
            available_positions = [
                (x, y)
                for x in range(self.board_size)
                for y in range(self.board_size)
                if (x, y) not in safe_tiles
            ]
            random.shuffle(available_positions)
            self.mines = set(available_positions[: self.mine_count])

        if coord in self.flagged:
            return
        if coord in self.revealed:
            return
        self.revealed.add(coord)

        if coord in self.mines:
            # mark this mine visually
            shield = self.shields.get(coord)
            if shield is not None:
                shield.color = (1.0, 0.2, 0.2)

            if coord not in self.labels:
                tile_node = self.tiles.get(coord)
                if tile_node is not None:
                    textnode = bs.newnode(
                        'text',
                        attrs={
                            'text': 'M',
                            'in_world': True,
                            'color': (1, 0.2, 0.2),
                            'scale': 0.02,
                            'h_align': 'center'
                        },
                    )
                    tile_node.connectattr('position', textnode, 'position')
                    self.labels[coord] = textnode

            PopupText('BOOM!', color=(1, 0, 0), scale=1.8, position=self.player_spaz.node.position, random_offset=1).autoretain()
            self._fail()
            return

        count = self._adjacent_mine_count(coord)

        # change shield color for revealed safe tile
        shield = self.shields.get(coord)
        if shield is not None:
            shield.color = (1, 1, 1)

        # create permanent text label once
        if coord not in self.labels:
            tile_node = self.tiles.get(coord)
            if tile_node is not None:
                if count != 0:
                    textnode = bs.newnode(
                        'text',
                        attrs={
                            'text': str(count),
                            'in_world': True,
                            'scale': 0.02,
                            'color': (
                                (0.2, 0.8, 1.0) if count == 1 else
                                (0.2, 0.8, 0.2) if count == 2 else
                                (1.0, 0.2, 0.2) if count == 3 else
                                (0.6, 0.2, 0.8) if count == 4 else
                                (1.0, 1.0, 0.2)
                            ),
                            'h_align': 'center'
                        },
                    )
                    tile_node.connectattr('position', textnode, 'position')
                    self.labels[coord] = textnode

        # flood-reveal adjacent tiles if count is 0 and neighbor is not a mine
        if count == 0:
            cx, cy = coord
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (cx + dx, cy + dy)
                    if (
                        0 <= neighbor[0] < self.board_size
                        and 0 <= neighbor[1] < self.board_size
                        and neighbor not in self.mines
                    ):
                        self._reveal_tile(neighbor)

        # win check: all safe tiles revealed and all mines flagged
        total_tiles = self.board_size * self.board_size
        safe_tiles_revealed = len(self.revealed) >= total_tiles - len(self.mines)
        all_mines_flagged = all(mine in self.flagged for mine in self.mines)

        if safe_tiles_revealed and all_mines_flagged:
            self._win()

    def _adjacent_mine_count(self, coord: tuple[int,int]) -> int:
        cx, cy = coord
        total = 0
        for dx in (-1, 1, 0):
            for dy in (-1, 1, 0):
                if dx == 0 and dy == 0:
                    continue
                check = (cx + dx, cy + dy)
                if check in self.mines:
                    total += 1
        return total

    def _reveal_all_mines(self) -> None:
        for coord in self.mines:
            if coord in self.revealed:
                continue
            self.revealed.add(coord)

            shield = self.shields.get(coord)
            if shield is not None:
                shield.color = (1.0, 0.2, 0.2)

            if coord not in self.labels:
                tile_node = self.tiles.get(coord)
                if tile_node is not None:
                    textnode = bs.newnode(
                        'text',
                        attrs={
                            'text': 'M',
                            'in_world': True,
                            'color': (1, 0.2, 0.2),
                            'scale': 0.01,
                            'h_align': 'center'
                        },
                    )
                    tile_node.connectattr('position', textnode, 'position')
                    self.labels[coord] = textnode

    def _fail(self) -> None:
        self.game_over = True
        if self.player_spaz:
            self.player_spaz._cursed = True
            self.player_spaz.curse_explode()
            self._reveal_all_mines()
        bs.timer(12, lambda: bs.newnode('text' , attrs={'text': 'Exit the game with the menu...', 'in_world': False, 'position': (0, 0)}))

    def _win(self) -> None:
        self.game_over = True
        bs.cameraflash()
        bs.getsound('score').play()
        self._reveal_all_mines()

        if self.player_spaz:
            self.player_spaz.handlemessage(bs.CelebrateMessage(999))
        bs.timer(5,self.end_game)


    def _move_cursor(self) -> None:
        if self.player_spaz is None or self.game_over:
            return
        x = self.start_x + self.cursor_x * self.spacing
        z = self.start_z + self.cursor_y * self.spacing
        self.player_spaz.handlemessage(bs.StandMessage((x, self.start_y -0.8, z), 1))

    def _cursor_left(self) -> None:
        if self.cursor_x > 0:
            self.cursor_x -= 1
            self._move_cursor()

    def _cursor_right(self) -> None:
        if self.cursor_x < self.board_size - 1:
            self.cursor_x += 1
            self._move_cursor()

    def _cursor_up(self) -> None:
        if self.cursor_y > 0:
            self.cursor_y -= 1
            self._move_cursor()

    def _cursor_down(self) -> None:
        if self.cursor_y < self.board_size - 1:
            self.cursor_y += 1
            self._move_cursor()

    def _reveal_current(self) -> None:
        self._reveal_tile((self.cursor_x, self.cursor_y))

    def _flag_current(self) -> None:
        if self.game_over:
            return
        coord = (self.cursor_x, self.cursor_y)

        # cannot flag revealed tiles
        if coord in self.revealed:
            return

        # UNFLAG
        if coord in self.flagged:
            self.flagged.remove(coord)

            label = self.flag_labels.get(coord)
            if label is not None:
                label.delete()
                del self.flag_labels[coord]

            return

        # FLAG
        self.flagged.add(coord)

        tile_node = self.tiles.get(coord)
        if tile_node is not None and coord not in self.flag_labels:
            t = bs.newnode(
                'text',
                attrs={
                    'text': f'{babase.charstr(babase.SpecialChar.FLAG_CHINA)}',
                    'in_world': True,
                    'color': (1, 1, 0),
                    'scale': 0.02,
                    'h_align': 'center'
                },
            )
            tile_node.connectattr('position', t, 'position')
            self.flag_labels[coord] = t


       

    @override
    def spawn_player(self, player: bs.Player):
        #player.character = 'Spaz'
        #try:
        #    self.session.customdata[player.sessionplayer]['cosmetic'] = None
       # except:
       #     pass
        spaz = self.spawn_player_spaz(player, position=(0, 1, 2.5))
        spaz.node.is_area_of_interest = False


        if player is self.players[0]:

            
            self.player_spaz = spaz
            spaz.award_xp = False
            spaz.node.name = ''
    
            self.cursor_x = 0
            self.cursor_y = 0
            self._move_cursor()

            player.resetinput()
            player.assigninput(bs.InputType.LEFT_PRESS, self._cursor_left)
            player.assigninput(bs.InputType.RIGHT_PRESS, self._cursor_right)
            player.assigninput(bs.InputType.UP_PRESS, self._cursor_up)
            player.assigninput(bs.InputType.DOWN_PRESS, self._cursor_down)
            player.assigninput(bs.InputType.JUMP_PRESS, self._reveal_current)
            player.assigninput(bs.InputType.BOMB_PRESS, self._flag_current)

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
