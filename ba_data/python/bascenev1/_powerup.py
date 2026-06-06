# Released under the MIT License. See LICENSE for details.
#
"""Powerup related functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass
import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Sequence

import bascenev1


@dataclass
class PowerupMessage:
    """A message telling an object to accept a powerup.

    Category: **Message Classes**

    This message is normally received by touching a bascenev1.PowerupBox.
    """

    poweruptype: str
    """The type of powerup to be granted (a string).
       See bascenev1.Powerup.poweruptype for available type values."""

    sourcenode: bascenev1.Node | None = None
    """The node the powerup game from, or None otherwise.
       If a powerup is accepted, a bascenev1.PowerupAcceptMessage should be
       sent back to the sourcenode to inform it of the fact. This will
       generally cause the powerup box to make a sound and disappear or
       whatnot."""


@dataclass
class PowerupAcceptMessage:
    """A message informing a bascenev1.Powerup that it was accepted.

    Category: **Message Classes**

    This is generally sent in response to a bascenev1.PowerupMessage
    to inform the box (or whoever granted it) that it can go away.
    """


def get_default_powerup_distribution() -> Sequence[tuple[str, int]]:
    """Standard set of powerups."""

   
    from bascenev1lib.game.SuperSmash import SuperSmash, SuperSmashDM
    if isinstance(bascenev1.getactivity(), SuperSmash) or isinstance(bascenev1.getactivity(), SuperSmashDM):
        return (
        ('triple_bombs', 3),
        ('ice_bombs', 3),
        ('punch', 3),
        ('impact_bombs', 3),
        ('land_mines', 2),
        ('sticky_bombs', 3),
        ('shield', 3),
        ('health', 1),
        ('curse', 1),
        ('random', 3),
        ('rock', 2),
        ('negative', 2),
        ('faker', 1),
        ('stack', 2),
        ('promine', 2),
        ('egg', 2),
        ('lightning', 3),
        ('impulse', 3),
        ('mini', 2),
        ('what', 1),
        ('star', 2),
        ('boom', 2),
        ('kys', 0 if isinstance(bascenev1.getsession(), bascenev1.CoopSession) else 2),
        ('gold', 3),
        ('bed', 3),
    )


   
    
    
    # This is the order i made the powerups btw
    return (
        ('triple_bombs', 3),
        ('ice_bombs', 3),
        ('punch', 3),
        ('impact_bombs', 3),
        ('land_mines', 2),
        ('sticky_bombs', 3),
        ('shield', 3),
        ('health', 1),
        ('curse', 1),
        ('random', 3),
        ('rock', 2),
        ('negative', 2),
        ('faker', 1),
        ('stack', 2),
        ('promine', 2),
        ('egg', 2),
        ('lightning', 3),
        ('impulse', 3),
        ('mini', 2),
        ('what', 1),
        ('boogie', 2),
        ('waffle', 3),
        ('breaker', 2),
        ('star', 2),
        ('heart', 2),
        ('boom', 2),
        ('kys', 0 if isinstance(bascenev1.getsession(), bascenev1.CoopSession) else 2),
        ('totem', 1),
        ('gold', 3),
        ('bed', 3),
        ('cloak', 2),
    )

