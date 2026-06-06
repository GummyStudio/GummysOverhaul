# Released under the MIT License. See LICENSE for details.
#
"""Music related bits."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

import _bascenev1

if TYPE_CHECKING:
    pass


class MusicType(Enum):
    """Types of music available to play in-game.

    These do not correspond to specific pieces of music, but rather to
    'situations'. The actual music played for each type can be overridden
    by the game or by the user.
    """

    MENU = 'Menu'
    VICTORY = 'Victory'
    CHAR_SELECT = 'CharSelect'
    RUN_AWAY = 'RunAway'
    ONSLAUGHT = 'Onslaught'
    KEEP_AWAY = 'Keep Away'
    RACE = 'Race'
    EPIC_RACE = 'Epic Race'
    SCORES = 'Scores'
    GRAND_ROMP = 'GrandRomp'
    TO_THE_DEATH = 'ToTheDeath'
    CHOSEN_ONE = 'Chosen One'
    FORWARD_MARCH = 'ForwardMarch'
    FLAG_CATCHER = 'FlagCatcher'
    SURVIVAL = 'Survival'
    EPIC = 'Epic'
    SPORTS = 'Sports'
    HOCKEY = 'Hockey'
    FOOTBALL = 'Football'
    FLYING = 'Flying'
    SCARY = 'Scary'
    MARCHING = 'Marching'

    FORTNITE = 'Fortnite'
    ROBLOX = 'Roblox'
    GD = 'Geometry Dash'
    GDPEAK = 'GD Beatbox'
    WII = 'Wii Party'
    HALFLIFE2 = 'Half-Life 2'
    GUMMYSTAGE = 'GummyStage'
    GUMMYONSLAUGHT = 'thisisfuckingfire'
    MARIOSMADDNESS = 'Marios Maddness'
    BALLIN = 'ballin x die in a fire'
    PORTAL = 'portal'
    PHIGHTING = 'phighting'
    PIZZA = 'pizzaDeluxe'
    GUMRUNAROUND = 'gummyrunaround'
    FLOOR1 = 'floor1'
    FLOOR2 = 'floor2'
    FLOOR3 = 'floor3'
    FLOOR4 = 'floor4'
    FLOOR5 = 'floor5'
    FLOOR6 = 'floor6'
    FLOOR7 = 'floor7'
    SPECTATE = 'spectate'
    OVERTIME = 'overtime'
    HYPERSPEED = 'hyperspeed'
    GOGOSUMMER = 'summer'
    EXPERT = 'floor1EXPERT'
    FALLGUYS = 'FGSS1'
    WAR = 'WAR'
    RFTI = 'Running From the Internet'
    MENUCOOLER = 'hoes with lyrics'
    BOWLING = 'bowling'
    CROWN = 'qwerty'
    PACKAGE = 'package'
    ZOMBIE = 'ZOMBESZ'
    DARKFUTURE = 'Dazzling Dark Future'
    JOINUSFORABITE = 'Join Us for a Bite'
    DS1 = 'Mario Kart DS Battle Mode Restored'
    DS2 = 'Mario Kart DS Battle Mode SMK Remix'
    DS3 = 'DS Twilight House - Mario Kart Wii'
    NSMB = 'Mario VS Luigi'

    SHOPMUSIC1 = 'Shop Music 1'
    SHOPMUSIC2 = 'Shop Music 2'
    SHOPMUSIC3 = 'Shop Music 3'
    SHOPMUSIC4 = 'Shop Music 4'
    SHOPMUSIC5 = 'Shop Music 5'
    SHOPMUSIC6 = 'Shop Music 6'
    BOSSFIGHT = 'the credits song for my death but im the final boss'

    MOON = 'shitty ass loop'
    PEAK = 'HOLY PEAK !'
    BATTLEBRICKS = 'Battle Bricks'
    RAIN = 'Nun.'

    BJPARKCALM = 'ULTRAKILL OST - Deep Blue [Calm Mix]'
    BJPARKCOMBAT = 'ULTRAKILL OST - Deep Blue [COMBAT MIX]'
    LIMBO = 'ITS BLUE'
    MINESWEEPER = 'mine'
    GHOST_BLUE = 'ghostlbue'
    MK8_WIFI = 'Mario Kart 8 - Online Wifi thingu'
    DISASTER = 'Disasters'
    DEFEND = '/Users/GummyBoiYT/Downloads/memes/and then he went this way.mp4'

    YOURECOOKEDBRO = 'BLEEDING HEARTS'
    BLEEDING = 'BLEEDING HEARTS 2'
    OVERDRIVE = 'BLEEDING HEARTS PEAK'
    FLOOR1_FESTIVE_EXPERT = 'floor1 festive expert'
    FLOOR4_BLEEDING = 'floor4 bleeding'
    SPECTATEFLOOR7 = 'spectate floor 7'
    DUDEHOLYSHIT = 'why is this so goodl mao'

    BLACKKNIFE = 'roryknite'

    THEATER = 'theater'
    SMASH = 'smashy'
    SMASH_PIANO = 'smashy but piano'


def setmusic(musictype: MusicType | None, continuous: bool = False) -> None:
    """Set the app to play (or stop playing) a certain type of music.

    This function will handle loading and playing sound assets as
    necessary, and also supports custom user soundtracks on specific
    platforms so the user can override particular game music with their
    own.

    Pass ``None`` to stop music.

    if ``continuous`` is True and musictype is the same as what is
    already playing, the playing track will not be restarted.
    """

    # All we do here now is set a few music attrs on the current globals
    # node. The foreground globals' current playing music then gets fed to
    # the do_play_music call in our music controller. This way we can
    # seamlessly support custom soundtracks in replays/etc since we're being
    # driven purely by node data.
    gnode = _bascenev1.getactivity().globalsnode
    gnode.music_continuous = continuous
    gnode.music = '' if musictype is None else musictype.value
    gnode.music_count += 1
