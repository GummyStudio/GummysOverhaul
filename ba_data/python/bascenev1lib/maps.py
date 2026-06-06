# Released under the MIT License. See LICENSE for details.
#
"""Standard maps."""
# pylint: disable=too-many-lines

from __future__ import annotations

from typing import TYPE_CHECKING, override

import bascenev1 as bs
import random    


from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any


def register_all_maps() -> None:
    """Registering all maps."""
    for maptype in [
        HockeyStadium,
        FootballStadium,
        Bridgit,
        BigG,
        Roundabout,
        MonkeyFace,
        ZigZag,
        ThePad,
        DoomShroom,
        LakeFrigid,
        TipTop,
        CragCastle,
        TowerD,
        HappyThoughts,
        StepRightUp,
        Courtyard,
        Rampage,
        #Infi8 the map got corrupted bruh im lazy as shit im not doing tha tagian
        GummyStage,
        Table,
        TowerG,
        TheTower,
        StepRightUpMINIGAME,
        NintendoDS,
        SpaceStation,
        PitPass,
        Melee,
        GreatBritian,
        BJPark,
        MinesweeperMap,
        PacManMap,
        EmptyMap,
        MainMenuStage,
        Theater
    ]:
        bs.register_map(maptype)


class HockeyStadium(bs.Map):
    """Stadium map used for ice hockey games."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import hockey_stadium as defs

    name = 'Hockey Stadium'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'hockey', 'team_flag', 'keep_away']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'hockeyStadiumPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'meshes': (
                bs.getmesh('hockeyStadiumOuter'),
                bs.getmesh('hockeyStadiumInner'),
                bs.getmesh('hockeyStadiumStands'),
            ),
            'vr_fill_mesh': bs.getmesh('footballStadiumVRFill'),
            'collision_mesh': bs.getcollisionmesh('hockeyStadiumCollide'),
            'tex': bs.gettexture('hockeyStadium'),
            'stands_tex': bs.gettexture('footballStadium'),
        }
        mat = bs.Material()
        mat.add_actions(actions=('modify_part_collision', 'friction', 0.01))
        data['ice_material'] = mat
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['meshes'][0],
                'collision_mesh': self.preloaddata['collision_mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['ice_material'],
                ],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'vr_only': True,
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['stands_tex'],
            },
        )
        mats = [shared.footing_material, self.preloaddata['ice_material']]
        self.floor = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['meshes'][1],
                'color_texture': self.preloaddata['tex'],
                'opacity': 0.92,
                'opacity_in_low_or_medium_quality': 1.0,
                'materials': mats,
            },
        )
        self.stands = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['meshes'][2],
                'visible_in_reflections': False,
                'color_texture': self.preloaddata['stands_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.floor_reflection = True
        gnode.debris_friction = 0.3
        gnode.debris_kill_height = -0.3
        gnode.tint = (1.2, 1.3, 1.33)
        gnode.ambient_color = (1.15, 1.25, 1.6)
        gnode.vignette_outer = (0.66, 0.67, 0.73)
        gnode.vignette_inner = (0.93, 0.93, 0.95)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5
        self.is_hockey = True


class FootballStadium(bs.Map):
    """Stadium map for football games."""

    from bascenev1lib.mapdata import football_stadium as defs

    name = 'Football Stadium'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'football', 'team_flag', 'keep_away', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'footballStadiumPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('footballStadium'),
            'vr_fill_mesh': bs.getmesh('footballStadiumVRFill'),
            'collision_mesh': bs.getcollisionmesh('footballStadiumCollide'),
            'tex': bs.gettexture('footballStadium'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['mesh'],
                'collision_mesh': self.preloaddata['collision_mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.3, 1.2, 1.0)
        gnode.ambient_color = (1.3, 1.2, 1.0)
        gnode.vignette_outer = (0.57, 0.57, 0.57)
        gnode.vignette_inner = (0.9, 0.9, 0.9)
        gnode.vr_camera_offset = (0, -0.8, -1.1)
        gnode.vr_near_clip = 0.5

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5


class Bridgit(bs.Map):
    """Map with a narrow bridge in the middle."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import bridgit as defs

    name = 'Bridgit'
    dataname = 'bridgit'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        # print('getting playtypes', cls._getdata()['play_types'])
        return ['melee', 'team_flag', 'keep_away']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'bridgitPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh_top': bs.getmesh('bridgitLevelTop'),
            'mesh_bottom': bs.getmesh('bridgitLevelBottom'),
            'mesh_bg': bs.getmesh('natureBackground'),
            'bg_vr_fill_mesh': bs.getmesh('natureBackgroundVRFill'),
            'collision_mesh': bs.getcollisionmesh('bridgitLevelCollide'),
            'tex': bs.gettexture('bridgitLevelColor'),
            'mesh_bg_tex': bs.gettexture('natureBackgroundColor'),
            'collide_bg': bs.getcollisionmesh('natureBackgroundCollide'),
            'railing_collision_mesh': (
                bs.getcollisionmesh('bridgitLevelRailingCollide')
            ),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh_top'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bg'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bg_vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['bg_material'],
                    shared.death_material,
                ],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1, 1.2, 1.3)
        gnode.ambient_color = (1.1, 1.2, 1.3)
        gnode.vignette_outer = (0.65, 0.6, 0.55)
        gnode.vignette_inner = (0.9, 0.9, 0.93)


class BigG(bs.Map):
    """Large G shaped map for racing"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import big_g as defs

    name = 'Big G'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return [
            'race',
            'melee',
            'keep_away',
            'team_flag',
            'king_of_the_hill',
            'conquest',
        ]

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'bigGPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh_top': bs.getmesh('bigG'),
            'mesh_bottom': bs.getmesh('bigGBottom'),
            'mesh_bg': bs.getmesh('natureBackground'),
            'bg_vr_fill_mesh': bs.getmesh('natureBackgroundVRFill'),
            'collision_mesh': bs.getcollisionmesh('bigGCollide'),
            'tex': bs.gettexture('bigG'),
            'mesh_bg_tex': bs.gettexture('natureBackgroundColor'),
            'collide_bg': bs.getcollisionmesh('natureBackgroundCollide'),
            'bumper_collision_mesh': bs.getcollisionmesh('bigGBumper'),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'color': (0.7, 0.7, 0.7),
                'mesh': self.preloaddata['mesh_top'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'color': (0.7, 0.7, 0.7),
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bg'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bg_vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['bumper_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['bg_material'],
                    shared.death_material,
                ],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1, 1.2, 1.3)
        gnode.ambient_color = (1.1, 1.2, 1.3)
        gnode.vignette_outer = (0.65, 0.6, 0.55)
        gnode.vignette_inner = (0.9, 0.9, 0.93)


class Roundabout(bs.Map):
    """CTF map featuring two platforms and a long way around between them"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import roundabout as defs

    name = 'Roundabout'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'roundaboutPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('roundaboutLevel'),
            'mesh_bottom': bs.getmesh('roundaboutLevelBottom'),
            'mesh_bg': bs.getmesh('natureBackground'),
            'bg_vr_fill_mesh': bs.getmesh('natureBackgroundVRFill'),
            'collision_mesh': bs.getcollisionmesh('roundaboutLevelCollideMod'),
            'tex': bs.gettexture('roundaboutLevelColor'),
            'mesh_bg_tex': bs.gettexture('natureBackgroundColor'),
            'collide_bg': bs.getcollisionmesh('natureBackgroundCollide'),
            'railing_collision_mesh': (
                bs.getcollisionmesh('roundaboutLevelBumper')
            ),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -1, 1))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bg'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bg_vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['bg_material'],
                    shared.death_material,
                ],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.0, 1.05, 1.1)
        gnode.ambient_color = (1.0, 1.05, 1.1)
        gnode.shadow_ortho = True
        gnode.vignette_outer = (0.63, 0.65, 0.7)
        gnode.vignette_inner = (0.97, 0.95, 0.93)


class MonkeyFace(bs.Map):
    """Map sorta shaped like a monkey face; teehee!"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import monkey_face as defs

    name = 'Monkey Face'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'monkeyFacePreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('monkeyFaceLevel'),
            'bottom_mesh': bs.getmesh('monkeyFaceLevelBottom'),
            'mesh_bg': bs.getmesh('natureBackground'),
            'bg_vr_fill_mesh': bs.getmesh('natureBackgroundVRFill'),
            'collision_mesh': bs.getcollisionmesh('monkeyFaceLevelCollide'),
            'tex': bs.gettexture('monkeyFaceLevelColor'),
            'mesh_bg_tex': bs.gettexture('natureBackgroundColor'),
            'collide_bg': bs.getcollisionmesh('natureBackgroundCollide'),
            'railing_collision_mesh': (
                bs.getcollisionmesh('monkeyFaceLevelBumper')
            ),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bg'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bg_vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['bg_material'],
                    shared.death_material,
                ],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1, 1.2, 1.2)
        gnode.ambient_color = (1.2, 1.3, 1.3)
        gnode.vignette_outer = (0.60, 0.62, 0.66)
        gnode.vignette_inner = (0.97, 0.95, 0.93)
        gnode.vr_camera_offset = (-1.4, 0, 0)


class ZigZag(bs.Map):
    """A very long zig-zaggy map"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import zig_zag as defs

    name = 'Zigzag'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return [
            'melee',
            'keep_away',
            'team_flag',
            'conquest',
            'king_of_the_hill',
        ]

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'zigzagPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('zigZagLevel'),
            'mesh_bottom': bs.getmesh('zigZagLevelBottom'),
            'mesh_bg': bs.getmesh('natureBackground'),
            'bg_vr_fill_mesh': bs.getmesh('natureBackgroundVRFill'),
            'collision_mesh': bs.getcollisionmesh('zigZagLevelCollide'),
            'tex': bs.gettexture('zigZagLevelColor'),
            'mesh_bg_tex': bs.gettexture('natureBackgroundColor'),
            'collide_bg': bs.getcollisionmesh('natureBackgroundCollide'),
            'railing_collision_mesh': bs.getcollisionmesh('zigZagLevelBumper'),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bg'],
                'lighting': False,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bg_vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['mesh_bg_tex'],
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['bg_material'],
                    shared.death_material,
                ],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.0, 1.15, 1.15)
        gnode.ambient_color = (1.0, 1.15, 1.15)
        gnode.vignette_outer = (0.57, 0.59, 0.63)
        gnode.vignette_inner = (0.97, 0.95, 0.93)
        gnode.vr_camera_offset = (-1.5, 0, 0)


class ThePad(bs.Map):
    """A simple square shaped map with a raised edge."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import the_pad as defs

    name = 'The Pad'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'king_of_the_hill', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'thePadPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('thePadLevel'),
            'bottom_mesh': bs.getmesh('thePadLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('thePadLevelCollide'),
            'tex': bs.gettexture('thePadLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'railing_collision_mesh': bs.getcollisionmesh('thePadLevelBumper'),
            'vr_fill_mound_mesh': bs.getmesh('thePadVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.56, 0.55, 0.47),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1, 1.1, 1.0)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)


class DoomShroom(bs.Map):
    """A giant mushroom. Of doom!"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import doom_shroom as defs

    name = 'Doom Shroom'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'doomShroomPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('doomShroomLevel'),
            'collision_mesh': bs.getcollisionmesh('doomShroomLevelCollide'),
            'tex': bs.gettexture('doomShroomLevelColor'),
            'bgtex': bs.gettexture('doomShroomBGColor'),
            'bgmesh': bs.getmesh('doomShroomBG'),
            'vr_fill_mesh': bs.getmesh('doomShroomVRFill'),
            'stem_mesh': bs.getmesh('doomShroomStem'),
            'collide_bg': bs.getcollisionmesh('doomShroomStemCollide'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.stem = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['stem_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.bg_collide = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['collide_bg'],
                'materials': [shared.footing_material, shared.death_material],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.82, 1.10, 1.15)
        gnode.ambient_color = (0.9, 1.3, 1.1)
        gnode.shadow_ortho = False
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        xpos = point.x
        zpos = point.z
        x_adj = xpos * 0.125
        z_adj = (zpos + 3.7) * 0.2
        if running:
            x_adj *= 1.4
            z_adj *= 1.4
        return x_adj * x_adj + z_adj * z_adj > 1.0


class LakeFrigid(bs.Map):
    """An icy lake fit for racing."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import lake_frigid as defs

    name = 'Lake Frigid'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'race']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'lakeFrigidPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('lakeFrigid'),
            'mesh_top': bs.getmesh('lakeFrigidTop'),
            'mesh_reflections': bs.getmesh('lakeFrigidReflections'),
            'collision_mesh': bs.getcollisionmesh('lakeFrigidCollide'),
            'tex': bs.gettexture('lakeFrigid'),
            'tex_reflections': bs.gettexture('lakeFrigidReflections'),
            'vr_fill_mesh': bs.getmesh('lakeFrigidVRFill'),
        }
        mat = bs.Material()
        mat.add_actions(actions=('modify_part_collision', 'friction', 0.01))
        data['ice_material'] = mat
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [
                    shared.footing_material,
                    self.preloaddata['ice_material'],
                ],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_top'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_reflections'],
                'lighting': False,
                'overlay': True,
                'opacity': 0.15,
                'color_texture': self.preloaddata['tex_reflections'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1, 1, 1)
        gnode.ambient_color = (1, 1, 1)
        gnode.shadow_ortho = True
        gnode.vignette_outer = (0.86, 0.86, 0.86)
        gnode.vignette_inner = (0.95, 0.95, 0.99)
        gnode.vr_near_clip = 0.5
        self.is_hockey = True


class TipTop(bs.Map):
    """A pointy map good for king-of-the-hill-ish games."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import tip_top as defs

    name = 'Tip Top'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'king_of_the_hill', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'tipTopPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('tipTopLevel'),
            'bottom_mesh': bs.getmesh('tipTopLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('tipTopLevelCollide'),
            'tex': bs.gettexture('tipTopLevelColor'),
            'bgtex': bs.gettexture('tipTopBGColor'),
            'bgmesh': bs.getmesh('tipTopBG'),
            'railing_collision_mesh': bs.getcollisionmesh('tipTopLevelBumper'),
        }
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -0.2, 2.5))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'color': (0.7, 0.7, 0.7),
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color': (0.7, 0.7, 0.7),
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'color': (0.4, 0.4, 0.4),
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.8, 0.9, 1.3)
        gnode.ambient_color = (0.8, 0.9, 1.3)
        gnode.vignette_outer = (0.79, 0.79, 0.69)
        gnode.vignette_inner = (0.97, 0.97, 0.99)


class CragCastle(bs.Map):
    """A lovely castle map."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import crag_castle as defs

    name = 'Crag Castle'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'conquest']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'cragCastlePreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('cragCastleLevel'),
            'bottom_mesh': bs.getmesh('cragCastleLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('cragCastleLevelCollide'),
            'tex': bs.gettexture('cragCastleLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'railing_collision_mesh': (
                bs.getcollisionmesh('cragCastleLevelBumper')
            ),
            'vr_fill_mound_mesh': bs.getmesh('cragCastleVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        # fixme should chop this into vr/non-vr sections
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.2, 0.25, 0.2),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.shadow_ortho = True
        gnode.shadow_offset = (0, 0, -5.0)
        gnode.tint = (1.15, 1.05, 0.75)
        gnode.ambient_color = (1.15, 1.05, 0.75)
        gnode.vignette_outer = (0.6, 0.65, 0.6)
        gnode.vignette_inner = (0.95, 0.95, 0.95)
        gnode.vr_near_clip = 1.0


class TowerD(bs.Map):
    """Map used for runaround mini-game."""

    from bascenev1lib.mapdata import tower_d as defs

    name = 'Tower D'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'towerDPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('towerDLevel'),
            'mesh_bottom': bs.getmesh('towerDLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('towerDLevelCollide'),
            'tex': bs.gettexture('towerDLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'player_wall_collision_mesh': bs.getcollisionmesh(
                'towerDPlayerWall'
            ),
            'player_wall_material': bs.Material(),
        }
        # fixme should chop this into vr/non-vr sections
        data['player_wall_material'].add_actions(
            actions=('modify_part_collision', 'friction', 0.0)
        )
        # anything that needs to hit the wall can apply this material
        data['collide_with_wall_material'] = bs.Material()
        data['player_wall_material'].add_actions(
            conditions=(
                'they_dont_have_material',
                data['collide_with_wall_material'],
            ),
            actions=('modify_part_collision', 'collide', False),
        )
        data['vr_fill_mound_mesh'] = bs.getmesh('stepRightUpVRFillMound')
        data['vr_fill_mound_tex'] = bs.gettexture('vrFillMound')
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, 1, 1))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.node_bottom = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.53, 0.57, 0.5),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.player_wall = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata[
                    'player_wall_collision_mesh'
                ],
                'affect_bg_dynamics': False,
                'materials': [self.preloaddata['player_wall_material']],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.15, 1.11, 1.03)
        gnode.ambient_color = (1.2, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.73, 0.7)
        gnode.vignette_inner = (0.95, 0.95, 0.95)

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        # see if we're within edge_box
        boxes = self.defs.boxes
        box_position = boxes['edge_box'][0:3]
        box_scale = boxes['edge_box'][6:9]
        box_position2 = boxes['edge_box2'][0:3]
        box_scale2 = boxes['edge_box2'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        xpos2 = (point.x - box_position2[0]) / box_scale2[0]
        zpos2 = (point.z - box_position2[2]) / box_scale2[2]
        # if we're outside of *both* boxes we're near the edge
        return (xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5) and (
            xpos2 < -0.5 or xpos2 > 0.5 or zpos2 < -0.5 or zpos2 > 0.5
        )


class HappyThoughts(bs.Map):
    """Flying map."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import happy_thoughts as defs

    name = 'Happy Thoughts'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return [
            'melee',
            'keep_away',
            'team_flag',
            'conquest',
            'king_of_the_hill',
        ]

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'alwaysLandPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('alwaysLandLevel'),
            'bottom_mesh': bs.getmesh('alwaysLandLevelBottom'),
            'bgmesh': bs.getmesh('alwaysLandBG'),
            'collision_mesh': bs.getcollisionmesh('alwaysLandLevelCollideMod'),
            'tex': bs.gettexture('alwaysLandLevelColor'),
            'bgtex': bs.gettexture('alwaysLandBGColor'),
            'vr_fill_mound_mesh': bs.getmesh('alwaysLandVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        return data

    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        return bs.MusicType.FLYING

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -3.7, 2.5))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.2, 0.25, 0.2),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.happy_thoughts_mode = True
        gnode.shadow_offset = (0.0, 8.0, 5.0)
        gnode.tint = (1.3, 1.23, 1.0)
        gnode.ambient_color = (1.3, 1.23, 1.0)
        gnode.vignette_outer = (0.64, 0.59, 0.69)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        gnode.vr_near_clip = 1.0
        self.is_flying = True

        # throw out some tips on flying
        txt = bs.newnode(
            'text',
            attrs={
                'text': bs.Lstr(resource='pressJumpToFlyText'),
                'scale': 1.2,
                'maxwidth': 800,
                'position': (0, 200),
                'shadow': 0.5,
                'flatness': 0.5,
                'h_align': 'center',
                'v_attach': 'bottom',
            },
        )
        cmb = bs.newnode(
            'combine',
            owner=txt,
            attrs={'size': 4, 'input0': 0.3, 'input1': 0.9, 'input2': 0.0},
        )
        bs.animate(cmb, 'input3', {3.0: 0, 4.0: 1, 9.0: 1, 10.0: 0})
        cmb.connectattr('output', txt, 'color')
        bs.timer(10.0, txt.delete)


class StepRightUp(bs.Map):
    """Wide stepped map good for CTF or Assault."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import step_right_up as defs

    name = 'Step Right Up'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'conquest']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'stepRightUpPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('stepRightUpLevel'),
            'mesh_bottom': bs.getmesh('stepRightUpLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('stepRightUpLevelCollide'),
            'tex': bs.gettexture('stepRightUpLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mound_mesh': bs.getmesh('stepRightUpVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        # fixme should chop this into vr/non-vr chunks
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -1, 2))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.node_bottom = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.53, 0.57, 0.5),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.2, 1.1, 1.0)
        gnode.ambient_color = (1.2, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)


class Courtyard(bs.Map):
    """A courtyard-ish looking map for co-op levels."""

    from bascenev1lib.mapdata import courtyard as defs

    name = 'Courtyard'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'courtyardPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('courtyardLevel'),
            'mesh_bottom': bs.getmesh('courtyardLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('courtyardLevelCollide'),
            'tex': bs.gettexture('courtyardLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'player_wall_collision_mesh': (
                bs.getcollisionmesh('courtyardPlayerWall')
            ),
            'player_wall_material': bs.Material(),
        }
        # FIXME: Chop this into vr and non-vr chunks.
        data['player_wall_material'].add_actions(
            actions=('modify_part_collision', 'friction', 0.0)
        )
        # anything that needs to hit the wall should apply this.
        data['collide_with_wall_material'] = bs.Material()
        data['player_wall_material'].add_actions(
            conditions=(
                'they_dont_have_material',
                data['collide_with_wall_material'],
            ),
            actions=('modify_part_collision', 'collide', False),
        )
        data['vr_fill_mound_mesh'] = bs.getmesh('stepRightUpVRFillMound')
        data['vr_fill_mound_tex'] = bs.gettexture('vrFillMound')
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.53, 0.57, 0.5),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        # in co-op mode games, put up a wall to prevent players
        # from getting in the turrets (that would foil our brilliant AI)
        if isinstance(bs.getsession(), bs.CoopSession):
            cmesh = self.preloaddata['player_wall_collision_mesh']
            self.player_wall = bs.newnode(
                'terrain',
                attrs={
                    'collision_mesh': cmesh,
                    'affect_bg_dynamics': False,
                    'materials': [self.preloaddata['player_wall_material']],
                },
            )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.2, 1.17, 1.1)
        gnode.ambient_color = (1.2, 1.17, 1.1)
        gnode.vignette_outer = (0.6, 0.6, 0.64)
        gnode.vignette_inner = (0.95, 0.95, 0.93)

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        # count anything off our ground level as safe (for our platforms)
        # see if we're within edge_box
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5


class Rampage(bs.Map):
    """Wee little map with ramps on the sides."""

    from bascenev1lib.mapdata import rampage as defs

    name = 'Rampage'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'war']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'rampagePreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('rampageLevel'),
            'bottom_mesh': bs.getmesh('rampageLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('rampageLevelCollide'),
            'tex': bs.gettexture('rampageLevelColor'),
            'bgtex': bs.gettexture('rampageBGColor'),
            'bgtex2': bs.gettexture('rampageBGColor2'),
            'bgmesh': bs.getmesh('rampageBG'),
            'bgmesh2': bs.getmesh('rampageBG2'),
            'vr_fill_mesh': bs.getmesh('rampageVRFill'),
            'railing_collision_mesh': bs.getcollisionmesh('rampageBumper'),
        }
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, 0, 2))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.bottom = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bottom_mesh'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        self.bg2 = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh2'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex2'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['bgtex2'],
            },
        )
        self.railing = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata['railing_collision_mesh'],
                'materials': [shared.railing_material],
                'bumper': True,
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.2, 1.1, 0.97)
        gnode.ambient_color = (1.3, 1.2, 1.03)
        gnode.vignette_outer = (0.62, 0.64, 0.69)
        gnode.vignette_inner = (0.97, 0.95, 0.93)

    @override
    def is_point_near_edge(self, point: bs.Vec3, running: bool = False) -> bool:
        box_position = self.defs.boxes['edge_box'][0:3]
        box_scale = self.defs.boxes['edge_box'][6:9]
        xpos = (point.x - box_position[0]) / box_scale[0]
        zpos = (point.z - box_position[2]) / box_scale[2]
        return xpos < -0.5 or xpos > 0.5 or zpos < -0.5 or zpos > 0.5


class GummyStage(bs.Map):
    """The stage for Gummy's OverhaulInfinite Onslaught."""
    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import gummystage as defs

    name = 'Gummy Stage'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'doomShroomPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('gummystage'),
            'collision_mesh': bs.getcollisionmesh('gummystage'),
            'tex': bs.gettexture('gummystage'),
            'bgtex': bs.gettexture('gray'),
            'bgmesh': bs.getmesh('doomShroomBG'),
            'vr_fill_mesh': bs.getmesh('doomShroomVRFill'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.82, 1.10, 1.15)
        gnode.ambient_color = (0.9, 1.3, 1.1)
        gnode.shadow_ortho = False
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)

class Table(bs.Map):
    """a big flat map (its my table!)"""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import table as defs

    name = 'Table'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return [
            'melee',
            'keep_away',
            'team_flag',
            'king_of_the_hill',
            'war',
        ]

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'tablepreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('livingroom'),
            'mesh_bottom': bs.getmesh('zigZagLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('livingroom'),
            'tex': bs.gettexture('livingroom'),
            'bg_material': bs.Material(),
        }
        data['bg_material'].add_actions(
            actions=('modify_part_collision', 'friction', 10.0)
        )
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.0, 1.15, 1.15)
        gnode.ambient_color = (1.0, 1.15, 1.15)
        gnode.vignette_outer = (0.57, 0.59, 0.63)
        gnode.vignette_inner = (0.97, 0.95, 0.93)
        gnode.vr_camera_offset = (-1.5, 0, 0)

    
class TowerG(bs.Map):
    """Map used for gummy's runaround mini-game."""

    from bascenev1lib.mapdata import runaroundgummy as defs

    name = 'Tower G'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'gumrunaroundPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('gumrunaround'),
            'collision_mesh': bs.getcollisionmesh('gumrunaround'),
            'tex': bs.gettexture('untitled33'),
            'bgtex': bs.gettexture('gray'),
            'bgmesh': bs.getmesh('thePadBG'),
            'player_wall_collision_mesh': bs.getcollisionmesh(
                'gummyPlayerWall'
            ),
            'player_wall_material': bs.Material(),
        }
        # fixme should chop this into vr/non-vr sections
        data['player_wall_material'].add_actions(
            actions=('modify_part_collision', 'friction', 0.0)
        )
        # anything that needs to hit the wall can apply this material
        data['collide_with_wall_material'] = bs.Material()
        data['player_wall_material'].add_actions(
            conditions=(
                'they_dont_have_material',
                data['collide_with_wall_material'],
            ),
            actions=('modify_part_collision', 'collide', False),
        )
        return data
    
    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, 1, 1))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        self.player_wall = bs.newnode(
            'terrain',
            attrs={
                'collision_mesh': self.preloaddata[
                    'player_wall_collision_mesh'
                ],
                'affect_bg_dynamics': False,
                'materials': [self.preloaddata['player_wall_material']],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.6, 0.81, 0.83)
        gnode.ambient_color = (0.9, 1.3, 1.1)
        gnode.shadow_ortho = False
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)
        



class TheTower(bs.Map):
    """The hardcord infinite onslaught map."""
    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import TheTower as defs

    name = 'The Tower'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'thetowerPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('TheTower'),
            'collision_mesh': bs.getcollisionmesh('TheTower'),
            'tex': bs.gettexture('courtyardLevelColor'),
            'bgtex': bs.gettexture('gray'),
            'bgmesh': bs.getmesh('doomShroomBG'),
            'vr_fill_mesh': bs.getmesh('doomShroomVRFill'),
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mesh'],
                'lighting': False,
                'vr_only': True,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.82, 1.10, 1.15)
        gnode.ambient_color = (0.9, 1.3, 1.1)
        gnode.shadow_ortho = True
        gnode.vignette_outer = (0.76, 0.76, 0.76)
        gnode.vignette_inner = (0.95, 0.95, 0.99)
    
class StepRightUpMINIGAME(bs.Map):
    """Wide stepped map good for CTF or Assault."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import package as defs

    name = 'Package Minigame'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['package']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'stepRightUpPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('stepRightUpLevel'),
            'mesh_bottom': bs.getmesh('stepRightUpLevelBottom'),
            'collision_mesh': bs.getcollisionmesh('stepRight'),
            'tex': bs.gettexture('stepRightUpLevelColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mound_mesh': bs.getmesh('stepRightUpVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        # fixme should chop this into vr/non-vr chunks
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -1, 2))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.node_bottom = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['mesh_bottom'],
                'lighting': False,
                'color_texture': self.preloaddata['tex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.53, 0.57, 0.5),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.2, 1.1, 1.0)
        gnode.ambient_color = (1.2, 1.1, 1.0)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)

class NintendoDS(bs.Map):
    """A handheld, as a course. I still don't know how to edit UVs. - Mell""" 

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import nintendods as defs

    name = 'Nintendo DS'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee','team_flag','keep_away','king_of_the_hill']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'nintendoDSPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('nintendoDS'),
            'collision_mesh': bs.getcollisionmesh('nintendoDS'),
            'tex': bs.gettexture('nintendoDS'),
            'bgtex': bs.gettexture('DSspace'),
            'bgmesh': bs.getmesh('DSspace')
        }
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.7, 0.7, 0.6)
        gnode.ambient_color = (1, 1, 1)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)

    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        import random
        music_choices = [
            bs.MusicType.DS1,
            bs.MusicType.DS2,
            bs.MusicType.DS3
        ]
        chosen_music = random.choice(music_choices)
        return chosen_music

class SpaceStation(bs.Map):
    """ i hate blender

    but i like the idea
    
    low gravity
    """ 

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import SpaceStationDef as defs

    name = 'Space Station'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee','team_flag','keep_away','king_of_the_hill']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'MoonPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('MoonLevel'),
            'collision_mesh': bs.getcollisionmesh('MoonLevelCollide'),
            'tex': bs.gettexture('SpaceStation'),
            'bgtex': bs.gettexture('DSspace'),
            'bgmesh': bs.getmesh('thePadBG')
        }
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.8, 0.8, 0.93)
        gnode.ambient_color = (0.51, 0.5, 1)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)

        bs.timer(0.05, self.apply_low_gravity, repeat=True)

    
                    
                


    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        
        return bs.MusicType.MOON



class PitPass(bs.Map):
    """ Metal Map with a pit and a bridge in the middle
    """ 

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import PitPassing as defs

    name = 'Pit Pass'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        # the 2nd flag in ffa ctp kept falling idk why
        return ['melee','keep_away']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'PitPassingPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('pitpassLevel'),
            'collision_mesh': bs.getcollisionmesh('pitpassLevelCollide'),
            'tex': bs.gettexture('pitpassingColor'),
            'bgtex': bs.gettexture('gray'),
            'bgmesh': bs.getmesh('thePadBG'),
            'mesh_lava': bs.getmesh('pitpassLava'),
            'texture_lava': bs.gettexture('poisionColor'),
            'rail_mesh': bs.getmesh('pitpassingRail'),
            'rail_collision_mesh': bs.getcollisionmesh('pitpassingRailCollide'),
            'rail_tex': bs.gettexture('pitpassingRailColor'),
        }
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.terrain_trigger_material = bs.Material()
        self.terrain_trigger_material.add_actions(
            actions=(('modify_part_collision', 'collide', True),
                    ('call', 'at_connect', self._on_any_touch))
        )
        
                        
                    
        


        self.lava = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['mesh_lava'],
                'collision_mesh': bs.getcollisionmesh('pitpassLavaCollide'),
                'color_texture': self.preloaddata['texture_lava'],
                'materials': [shared.footing_material, self.terrain_trigger_material],
            },
        )
        bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['mesh'],
                'collision_mesh': self.preloaddata['collision_mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material, shared.object_material],
            },
        )
        bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'mesh': self.preloaddata['rail_mesh'],
                'collision_mesh': self.preloaddata['rail_collision_mesh'],
                'color_texture': self.preloaddata['rail_tex'],
                'materials': [shared.footing_material, shared.object_material],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
       
        
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1, 1.1, 1.0)
        gnode.ambient_color = (0.51, 0.5, 1)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
    
    def _on_any_touch(self):
        from bascenev1lib.actor.bomb import Bomb, ExplodeMessage
        from bascenev1lib.actor.spaz import Spaz
        from bascenev1lib.actor.flag import Flag
        from bascenev1lib.actor.spazfactory import SpazFactory
        c = bs.getcollision()
        node = c.opposingnode
        if not node or not node.exists():
            return
        
        if node.getnodetype() not in ['prop', 'spaz', 'bomb', 'flag']:
            return
        

        if node.getdelegate(Spaz):

            # We died.
            if not node.getdelegate(Spaz).is_alive():
                node.materials = []
                return

            # Fire
            node.getdelegate(Spaz).touched_fire(id('POISION'))
            node.getdelegate(Spaz).leave_fire(id('POISION'))
            node.getdelegate(Spaz).handlemessage(bs.HitMessage(flat_damage=15))
            node.getdelegate(Spaz)._safe_play_sound(bs.getsound('Firehurt'), 1.5)
            def up():
                if node.getdelegate(Spaz).shield:
                    node.getdelegate(Spaz).shield.delete()
                    node.getdelegate(Spaz).shield = None
                    SpazFactory.get().shield_down_sound.play(
                        1.0,
                        position=node.position,
                        )
                    
                for _ in range(18):
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                                    0, 25, 0,
                                                    45, 0.05, 0, 0,
                                                    0, 250, 0)
               
                for _ in range(50):
                    v = (node.position[0], 0, 0)
           
                    
                    node.handlemessage('impulse', node.position[0], node.position[1], node.position[2],
                                            0, 25, 0,
                                            21, 0.05, 0, 0,
                                            v[0]*15*2, 0, v[2]*15*2)
                
            bs.timer(0.02, up)
            if not node.getdelegate(Spaz).is_alive():
                try:
                    bs.timer(0.25, lambda: node.getdelegate(Spaz).shatter(True))
                except:
                    pass
        elif node.getdelegate(Bomb):
            # boom

            # im lazy
            node.velocity = (node.velocity[0], node.velocity[1]+10.4, node.velocity[2])
            try:
                bs.timer(0.23, lambda: node.getdelegate(Bomb).handlemessage(ExplodeMessage()))
            except:
                pass
        elif node.getdelegate(Flag):
            
            try:
                node.getdelegate(Flag).handlemessage(bs.DieMessage())
            except:
                pass
        else:
            # uh.. i dunno who you are
            # but you shouldnt be here
            node.delete()

            
class Melee(bs.Map):
    """MELEEEEEEEEEEEEEEEEE""" 
    class defs:
        points = {}
        boxes = {}
        boxes['area_of_interest_bounds'] = (0.0, 0.7956858119, 0.0) + (
            0.0, 0.0, 0.0) + (30.80223883, 0.5961646365, 13.88431707)
        boxes['map_bounds'] = (0.0, 0.7956858119, -0.4689020853) + (0.0, 0.0, 0.0) + (
            35.16182389, 12.18696164, 21.52869693)
        points['ffa_spawn1'] = (0.0, 1.4, 0.0)

        

        

    name = 'Melee'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.locs = []
        self.regions = []
        
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        set = [
              dict(
                  position=(0.0, 0.0, 0.0), 
                  color=(1.0, 1, 1), 
                  size=(50.0, 1.0, 1.0)),
              
              ]

        for i, map in enumerate(set):
            self.locs.append(
                bs.newnode('locator',
                    attrs={'shape': 'box',
                           'position': set[i]['position'],
                           'color': set[i]['color'],
                           'opacity': 1.0,
                           'draw_beauty': True,
                           'size': set[i]['size'],
                           'additive': False}))
                           
            self.regions.append(
                bs.newnode('region',
                    attrs={'scale': tuple(set[i]['size']),
                           'type': 'box',
                           'materials': [self.collision,
                                         shared.footing_material]}))
            self.locs[-1].connectattr('position', self.regions[-1], 'position')

        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': bs.getmesh('tipTopBG'),
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture('tipTopBGColor')})

        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.3, 0.3, 0.6)
        gnode.ambient_color = (1, 1, 1)
        gnode.vignette_outer = (1, 1, 1)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
    
    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        
        return bs.MusicType.BATTLEBRICKS
       
class GreatBritian(bs.Map):
    """Wide stepped map good for CTF or Assault."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import GreatBritianDefs as defs

    name = 'Great Fucking Britian'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'britainPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('mapofgreatbritian'),
            'collision_mesh': bs.getcollisionmesh('greatbritian_collision'),
            'tex': bs.gettexture('TheMapOfBBC'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mound_mesh': bs.getmesh('stepRightUpVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        # fixme should chop this into vr/non-vr chunks
        return data

    def __init__(self) -> None:
        super().__init__(vr_overlay_offset=(0, -1, 2))
        shared = SharedObjects.get()
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.53, 0.57, 0.5),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = tuple([0.75 for _ in range(3)])
        gnode.ambient_color = (0.3, 0.32, 0.33)
        gnode.vignette_outer = (0.7, 0.65, 0.75)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
        bs.timer(0.1, self.change, repeat=True)

    def change(self):
        if self.node:
            import random
            normal = bs.gettexture('TheMapOfGreatBritian')
            bbc = bs.gettexture('TheMapOfBBC')

            if random.randint(0, 13) == 0:
                self.node.color_texture = bbc
            else:
                self.node.color_texture = normal

class BJPark(bs.Map):
    """A simple square shaped map with a raised edge."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import bombjumppark as defs

    name = 'Bomb Jump Park'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'king_of_the_hill']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'BJparkPreview'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'mesh': bs.getmesh('bombjumpparkLevel'),
            'collision_mesh': bs.getcollisionmesh('bombjumpparkLevelCollide'),
            'tex': bs.gettexture('bombjumpparkColor'),
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mound_mesh': bs.getmesh('thePadVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        mat = bs.Material()
        mat.add_actions(actions=('modify_part_collision', 'friction', 0.345))
        data['ice_material'] = mat
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        bs.newnode('sound', attrs=dict(sound=bs.getsound('rain'), volume=8))
        
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material, self.preloaddata['ice_material']],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.56, 0.55, 0.47),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1*0.6, 1.1*0.6, 1.0*0.6)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.2, 0.55, 0.25)
        #self.is_hockey = True

        gnode.vignette_inner = (0.95, 0.95, 0.93)

   

        self._start_lightning_loop()
        bs.timer(0.1, self.rain, repeat=True)

    def rain(self):
        """Spawn falling raindrop particles over the map."""

        for _ in range(5):
                pos = (
                    random.uniform(-2, 2), 
                    10.7,                       
                    random.uniform(-2, 2)
                )
                bs.emitfx(
                    position=pos,
                    velocity=(0, -20, 0),
                    count=random.randint(5, 24),
                    scale=1.5,
                    spread=2,
                    chunk_type='sweat',     
                )
         

    def lightning_strike(self):
        gnode = self.getactivity().globalsnode
        original_tint = gnode.tint

        bs.animate_array(gnode, 'tint', 3, 
                           {
                                 0.0: original_tint,
                                 0.3: (1.1, 1.5, 1.8),
                                 0.4: (0.6, 0.9, 0.9),
                                 0.7: original_tint
                             })
    

    def _start_lightning_loop(self) -> None:
        """Continuously triggers random lightning strikes."""
        from bascenev1lib.actor.bomb import Blast


        def strike(doit: bool=True):
            if doit:
                if random.randint(0, 2) == 0 and len(self.getactivity().players) != 0:
                    try:
                        playerpos = random.choice(bs.getactivity().players).actor.node.position
                    except:
                       playerpos = (random.uniform(5, -5),  random.uniform(6, 4), random.uniform(2, -8))
                    pos = (
                        playerpos[0] + random.uniform(-1.7, 1.7),
                        playerpos[1],
                        playerpos[2] + random.uniform(-1.7, 1.7)
                    )
                else:
                    pos = (random.uniform(5, -5), random.uniform(6, 4), random.uniform(2, -8))
                Blast(pos, blast_radius=1.5, blast_type='lightning')
            next_time = random.uniform(10.0, 25.0)
            bs.timer(next_time, strike)    
        strike(False)
    
    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
       
        return bs.MusicType.BJPARKCALM
    
class MinesweeperMap(bs.Map):
    """MELEEEEEEEEEEEEEEEEE""" 
    class defs:
        points = {}
        boxes = {}
        boxes['area_of_interest_bounds'] = (0.0, 0.7956858119, 0.0) + (
            0.0, 0.0, 0.0) + (30.80223883, 0.5961646365, 13.88431707)
        boxes['map_bounds'] = (0.0, 0.2, -0.2) + (0.0, 0.0, 0.0) + (
            35.16182389, 12.18696164, 21.52869693)
        points['ffa_spawn1'] = (0.0, 1.4, 0.0)

        

        

    name = 'MineSweeper'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.locs = []
        self.regions = []
        
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        set = [
              dict(
                  position=(0.0, 0.0, 0.0), 
                  color=(1.0, 1, 1), 
                  size=(500.0, 1.0, 500.0)),
              
              ]

        for i, map in enumerate(set):
            self.locs.append(
                bs.newnode('locator',
                    attrs={'shape': 'box',
                           'position': set[i]['position'],
                           'color': set[i]['color'],
                           'opacity': 1.0,
                           'draw_beauty': True,
                           'size': (0, 0, 0),
                           'additive': False}))
                           
            self.regions.append(
                bs.newnode('region',
                    attrs={'scale': tuple(set[i]['size']),
                           'type': 'box',
                           'materials': [self.collision,
                                         shared.footing_material]}))
            self.locs[-1].connectattr('position', self.regions[-1], 'position')

        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': bs.getmesh('tipTopBG'),
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture('tipTopBGColor')})

        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.3, 0.3, 0.6)
        gnode.ambient_color = (1, 1, 1)
        gnode.vignette_outer = (1, 1, 1)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
    
    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        
        return bs.MusicType.MINESWEEPER
    

class PacManMap(bs.Map):
    """MELEEEEEEEEEEEEEEEEE""" 
    class defs:
        points = {}
        boxes = {}
        boxes['area_of_interest_bounds'] = (
            0.0, 0.8, 0.0
        ) + (0.0, 0.0, 0.0) + (
            150.0, 3.0, 60.0
        )
        boxes['map_bounds'] = (
            0.0, 0.8, 0.0
        ) + (0.0, 0.0, 0.0) + (
            180.0, 15.0, 80.0
        )
        points['ffa_spawn1'] = (0.0, 1.4, 0.0)

        

        

    name = 'pacuy'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()

        # had to get chatgpt to help me with all of this cuz HOLY shit

        # Material to tag ghost actors
        self.ghost_material = bs.Material()

        # Material that ignores collisions with anything tagged as ghost_material
        self.ghost_collide = bs.Material()
        self.ghost_collide.add_actions(
            conditions=('they_dont_have_material', self.ghost_material),
            actions=('modify_part_collision', 'collide', True)
        )
        

        # Map layout
        # # = wall, . = pellet, O = power pellet, S = start
        # ( iahte optimization)
        self.map_layout = [
"############################",
"#............##............#",
"#.####.#####.##.#####.####.#",
"#O####.#####.##.#####.####O#",
"#.####.#####.##.#####.####.#",
"#..........................#",
"#.####.##.########.##.####.#",
"#.####.##.########.##.####.#",
"#......##....##....##......#",
"######.##### ## #####.######",
"######.##### ## #####.######",
"######.##          ##.######",
"######.## ###==### ##.######",
"######.## #HHHHHH# ##.######",
"      .   #HHGHHH#   .      ",
"######.## ##HHHH## ##.######",
"######.## ###==### ##.######",
"######.##          ##.######",
"######.## ######## ##.######",
"######.## ######## ##.######",
"#............##............#",
"#.####.#####.##.#####.####.#",
"#O..##........S.......##..O#",
"###.##.##.########.##.##.###",
"#......##....##....##......#",
"#.##########.##.##########.#",
"#.##########.##.##########.#",
"#..........................#",
"############################"
]

        self.tile_size = 0.53
        self.grid_offset = (-3, -2)
        self.wall_locs = []
        self.ghost_gates = []
        self.wall_regions = []
        self.pellets = {}
        self.power_pellets = set()
        self.start_position = (0, 1.0, 0)
        self.ghost_house_tiles = []
        self.ghost_house_world_positions = {}

        rows = len(self.map_layout)
        cols = len(self.map_layout[0])
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))
        self.walk_tiles = []        
        self.walk_world_positions = {}
        self.wall_tiles = []
        self.wall_world_positions = {}
        

        
        bs.newnode(
            'region',
            attrs=dict(
                type='box',
                scale=(99, 1, 99),
                materials=[self.collision, shared.footing_material]
            )
        )

        # Build tiles
        for gy, row in enumerate(self.map_layout):
            for gx, tile in enumerate(row):
                pos = (
                    self.grid_offset[0] + gx * self.tile_size,
                    1.0,
                    self.grid_offset[1] + gy * self.tile_size
                )
                if tile != '#':
                    wx = self.grid_offset[0] + gx * self.tile_size
                    wz = self.grid_offset[1] + gy * self.tile_size
                    self.walk_tiles.append((gx, gy))
                    self.walk_world_positions[(gx, gy)] = (wx, 1.0, wz)
                
                    
                    

                if tile == "#":
                    # Visual wall
                    wall_size = (self.tile_size, 0.1, self.tile_size)
                    loc = bs.newnode(
                        "locator",
                        attrs=dict(
                            shape="box",
                            position=pos,
                            size=wall_size,
                            color=(0.2, 0.6, 1.0),
                            additive=True,
                            draw_beauty=True,
                        )
                    )
                    self.wall_tiles.append((gx, gy))
                    self.wall_world_positions[(gx, gy)] = pos
                    # Collision region
                    region = bs.newnode(
                        "region",
                        attrs=dict(
                            type="box",
                            scale=(wall_size[0], 10, wall_size[2]),
                            materials=[self.collision]
                        )
                    )
                    loc.connectattr("position", region, "position")
                    self.wall_locs.append(loc)
                    self.wall_regions.append(region)

                elif tile == "=":
                    # Ghost gate
                    gate_size = (self.tile_size, 0.5, self.tile_size / 2)
                    loc = bs.newnode(
                        "locator",
                        attrs=dict(
                            shape="box",
                            position=pos,
                            size=gate_size,
                            color=(1.0, 0.0, 0.0), 
                            draw_beauty=True,
                            opacity=1.0,
                        ),
                    )
                    region = bs.newnode(
                        "region",
                        attrs=dict(
                            type="box",
                            scale=gate_size,
                            materials=[self.ghost_collide],
                        ),
                    )
                    loc.connectattr("position", region, "position")
                    self.ghost_gates.append(loc)
                    # also treat this as a ghost house
                    self.ghost_house_tiles.append((gx, gy))
                    self.ghost_house_world_positions[(gx, gy)] = pos

                elif tile == ".":
                    pellet = bs.newnode(
                        "shield",
                        attrs=dict(color=(3, 3, 3), radius=0.25)
                    )
                    pellet.position = pos
                    self.pellets[(gx, gy)] = pellet

                elif tile == "O":
                    pellet = bs.newnode(
                        "shield",
                        attrs=dict(color=(3, 3, 0), radius=0.35)
                    )
                    pellet.position = pos
                    self.pellets[(gx, gy)] = pellet
                    self.power_pellets.add((gx, gy))

                elif tile == "S":
                    self.start_position = pos
                elif tile == "G":
                    self.ghost_house_position = pos
                    self.ghost_house_tiles.append((gx, gy))
                    self.ghost_house_world_positions[(gx, gy)] = pos
                elif tile == "H":
                    self.ghost_house_tiles.append((gx, gy))
                    self.ghost_house_world_positions[(gx, gy)] = pos
                
        # Background
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': bs.getmesh('tipTopBG'),
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture('black')
            }
        )

        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.76, 0.76, 1)
        gnode.ambient_color = (1, 1, 1)
        gnode.vignette_outer = (0.63, 0.6, 1)
        gnode.vignette_inner = (1.15, 1, 1.3)
   
    def world_to_tile(self, pos):
        # converts world position to grid index
        gx = round((pos[0] - self.grid_offset[0]) / self.tile_size)
        gy = round((pos[2] - self.grid_offset[1]) / self.tile_size)
        return (gx, gy)
    

    

class EmptyMap(bs.Map):
    """MELEEEEEEEEEEEEEEEEE""" 
    class defs:
        points = {}
        boxes = {}
        boxes['area_of_interest_bounds'] = (0.0, 0.7956858119, 0.0) + (
            0.0, 0.0, 0.0) + (30.80223883, 0.5961646365, 13.88431707)
        boxes['map_bounds'] = (0.0, 0.7956858119, -0.4689020853) + (0.0, 0.0, 0.0) + (
            35.16182389, 12.18696164, 21.52869693)
        points['ffa_spawn1'] = (0.0, 1.4, 0.0)

        

        

    name = 'Empty'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
        }
        return data

    def __init__(self) -> None:
        super().__init__()
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': bs.getmesh('tipTopBG'),
                'lighting': False,
                'background': True,
                'color_texture': bs.gettexture('tipTopBGColor')})

      
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.3, 0.3, 0.6)
        gnode.ambient_color = (1, 1, 1)
        gnode.vignette_outer = (1, 1, 1)
        gnode.vignette_inner = (0.95, 0.95, 0.93)
    
class MainMenuStage(bs.Map):
    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import gummystage as defs

    name = ''

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []

    # eh, just leave the map making to the main menu


class Infi8(bs.Map):
    """A simple square shaped map with a raised edge."""

    # noinspection PyUnresolvedReferences

    name = 'Infi8'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return []#['melee', 'keep_away', 'team_flag', 'king_of_the_hill']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {
            'bgtex': bs.gettexture('menuBG'),
            'bgmesh': bs.getmesh('thePadBG'),
            'vr_fill_mound_mesh': bs.getmesh('thePadVRFillMound'),
            'vr_fill_mound_tex': bs.gettexture('vrFillMound'),
        }
        mat = bs.Material()
        mat.add_actions(actions=('modify_part_collision', 'friction', 0.345))
        data['ice_material'] = mat
        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        
        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': self.preloaddata['collision_mesh'],
                'mesh': self.preloaddata['mesh'],
                'color_texture': self.preloaddata['tex'],
                'materials': [shared.footing_material, self.preloaddata['ice_material']],
            },
        )
        self.background = bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['bgmesh'],
                'lighting': False,
                'background': True,
                'color_texture': self.preloaddata['bgtex'],
            },
        )
        bs.newnode(
            'terrain',
            attrs={
                'mesh': self.preloaddata['vr_fill_mound_mesh'],
                'lighting': False,
                'vr_only': True,
                'color': (0.56, 0.55, 0.47),
                'background': True,
                'color_texture': self.preloaddata['vr_fill_mound_tex'],
            },
        )
        gnode = bs.getactivity().globalsnode
        gnode.tint = (1.1*0.6, 1.1*0.6, 1.0*0.6)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.2, 0.55, 0.25)
        #self.is_hockey = True

        gnode.vignette_inner = (0.95, 0.95, 0.93)

   

class Theater(bs.Map):
    """A simple square shaped map with a raised edge."""

    # noinspection PyUnresolvedReferences
    from bascenev1lib.mapdata import theaterdefs as defs

    name = 'Theater'

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ['melee', 'keep_away', 'team_flag', 'king_of_the_hill']

    @override
    @classmethod
    def get_preview_texture_name(cls) -> str:
        return 'null'

    @override
    @classmethod
    def on_preload(cls) -> Any:
        data: dict[str, Any] = {}

        # fixme should chop this into vr/non-vr sections for efficiency
        return data

    def __init__(self) -> None:
        super().__init__()
        shared = SharedObjects.get()
        self.allow_swapping = True
        self.max_hurts = random.randint(10, 23)
        self.dead = False
        self.hurts = 0
        self.terrain_trigger_material = bs.Material()
        self.terrain_trigger_material.add_actions(
            actions=(('modify_part_collision', 'collide', True),
                    ('call', 'at_connect', self._on_any_touch))
        )
        
        self.swap_sfx = bs.getsound('jumboSwapSfx')
        self.screens = {
            'airball': bs.gettexture('jumboAirball'),
            'ankha':   bs.gettexture('jumboAnkha'),
            'bomb':    bs.gettexture('jumboBomb'),
            'cat_la':  bs.gettexture('jumboCatLalala'),
            'cat_pl':  bs.gettexture('jumboCatPlead'),
            'dap':     bs.gettexture('jumboDap'),
            'monkey':  bs.gettexture('jumboMonkey'),
            'r34':     bs.gettexture('jumboR34'),
            's':       bs.gettexture('jumboS'),
            'sponge':  bs.gettexture('jumboSponge'),
            'thragg':  bs.gettexture('jumboThragg'),
            'kill':    bs.gettexture('jumboKill')
            
        }

        self.special_screens = {
            'swap_animation': [bs.gettexture('jumboSwap1'), bs.gettexture('jumboSwap2'), bs.gettexture('jumboSwap3')],
            'hurt':    bs.gettexture('jumboHurt'),
            'dead': bs.gettexture('jumboCracked')


        }

        self.node = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': bs.getcollisionmesh('theaterFloor'),
                'mesh': bs.getmesh('theaterFloor'),
                'color_texture': bs.gettexture('stageFloorColor'),
                'materials': [shared.footing_material],
            },
        )
        self.death_floor = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': bs.getcollisionmesh('theaterDeaethFloor'),
                'mesh': bs.getmesh('theaterDeathFloor'),
                'color_texture': bs.gettexture('brown'),
                'materials': [shared.footing_material, shared.death_material],
            },
        )
        self.curtain = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': bs.getcollisionmesh('curtainCollide'),
                'mesh': bs.getmesh('theaterCurtain'),
                'color_texture': bs.gettexture('CurtainColor'),
                'materials': [shared.footing_material]
            },
        )
        self.background = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                                'collision_mesh': bs.getcollisionmesh('theaterBG'),
                'mesh': bs.getmesh('theaterBG'),

                'color_texture': bs.gettexture('black'),
                'materials': [shared.footing_material]
            },
        )
        self.screen = bs.newnode(
            'terrain',
            delegate=self,
            attrs={
                'collision_mesh': bs.getcollisionmesh('theaterScreen'),
                'mesh': bs.getmesh('theaterScreen'),
                'materials': [shared.footing_material, self.terrain_trigger_material]
            },
        )
     
        gnode = bs.getactivity().globalsnode
        gnode.tint = tuple([0.85]*3)
        gnode.ambient_color = (1.1, 1.1, 1.0)
        gnode.vignette_outer = (0.45, .45, 0.45)
        #self.is_hockey = True


        gnode.vignette_inner = (0.95, 0.95, 0.93)
        self.next_timer: bs.Timer = None

        self.swap_and_start_next()
        bs.timer(0.1, self.dead_tick, repeat=True)

    # i hate you spaz
    def dead_tick(self):
        if self.dead: self._set_screen_tex(self.special_screens['dead'])
  

    def swap_and_start_next(self):
        self.swap_screen()
        self.start_random_swapping()
    
    def start_random_swapping(self):
        self.next_timer = bs.Timer(random.uniform(3, 7), self.swap_and_start_next)

    
    def hurt(self):
        if self.dead:
            return
        self.next_timer = None

        # Make sure we stop if we reached da max
        if self.hurts >= self.max_hurts and not self.dead:
            self.dead = True
            self._set_screen_tex(self.special_screens['dead'])
            bs.getsound('shatter').play()
            self.allow_swapping = False
            self.next_timer = None

            return

        self.swap_screen('hurt')
        
        self.next_timer = bs.Timer(3, self.swap_and_start_next)


        
    
    def swap_screen(self, texture: str = 'random') -> None:
        if not self.allow_swapping:
            return
  
        
        frames = self.special_screens['swap_animation']
        
        for i, frame_tex in enumerate(frames):
            bs.timer(0.1 * i, bs.Call(self._set_screen_tex, frame_tex))
            
        reveal_time = 0.1 * len(frames)
        
        if texture == 'random':
            random_key = random.choice(list(self.screens.keys()))

            final_tex = self.screens[random_key]
        else:
            final_tex = self.screens.get(texture, False) or self.special_screens[texture]
        self.swap_sfx.play()
        
        bs.timer(reveal_time, bs.Call(self._set_screen_tex, final_tex))

    def _set_screen_tex(self, tex: bs.Texture) -> None:
        if self.screen:
            self.screen.color_texture = tex

    def _on_any_touch(self):
        from bascenev1lib.actor.bomb import Bomb, Blast
        from bascenev1lib.actor.spaz import Spaz

        c = bs.getcollision()
        node = c.opposingnode
        if not node or not node.exists():
            return
        
        if node.getnodetype() not in ['prop', 'spaz', 'bomb', 'region']:
            return
        
        # Make sure they're like flinged towards us 
        


        
        if node.getdelegate(Spaz):
            if node.velocity[2] > -3:
                return
            self.hurts += 0.5
            bs.emitfx(
                    position=(node.position),
                    velocity=(0, 0, -2),
                    count=4,
                    scale=0.6,
                    spread=3,
                    chunk_type='spark',
                    #color=color
            )

    
        elif node.getdelegate(Bomb):
            if node.velocity[2] > -3:
                return
            self.hurts += 4
            bs.emitfx(
                    position=(node.position),
                    velocity=(0, 0, -2),
                    count=12,
                    scale=2.2,
                    spread=1,
                    chunk_type='spark',
                    #color=color
            )
        elif node.getdelegate(Blast):
            # Auto count it akot
            self.hurts += 6
            bs.emitfx(
                    position=(node.position),
                    velocity=(0, 0, -2),
                    count=23,
                    scale=2.6,
                    spread=2,
                    chunk_type='spark',
                    #color=color
            )
        self.hurt()

    @override
    @classmethod
    def get_music_type(cls) -> bs.MusicType:
        
        return bs.MusicType.THEATER
    

        