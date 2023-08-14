"""Provides straight waveguides in dbu and um versions.

A straight is a rectangle of material with excludes and/or slab around it::

    ┌─────────────────────────────┐
    │        Slab/Exclude         │
    ├─────────────────────────────┤
    │                             │
    │            Core             │
    │                             │
    ├─────────────────────────────┤
    │        Slab/Exclude         │
    └─────────────────────────────┘

The slabs and excludes can be given in the form of an :py:class:~`Enclosure`.
"""


from kfactory import KCell, LayerEnum, kcl
from kfactory.utils import LayerEnclosure

from kgeneric.cells.dbu.straight import straight as straight_dbu

__all__ = ["straight", "straight_dbu"]


def straight(
    width: float,
    length: float,
    layer: int | LayerEnum,
    enclosure: LayerEnclosure | None = None,
) -> KCell:
    """Straight straight in um.

    Visualization::

        ┌─────────────────────────────┐
        │        Slab/Exclude         │
        ├─────────────────────────────┤
        │                             │
        │            Core             │
        │                             │
        ├─────────────────────────────┤
        │        Slab/Exclude         │
        └─────────────────────────────┘

    Args:
        width: Width of the straight. [um]
        length: Length of the straight. [um]
        layer: Layer index / :py:class:~`LayerEnum`
        enclosure: Definition of slabs/excludes. [um]
    """
    return straight_dbu(
        int(width / kcl.dbu), int(length / kcl.dbu), layer, enclosure=enclosure
    )


if __name__ == "__main__":
    from kgeneric.layers import LAYER

    c = straight(width=1, length=10, layer=LAYER.WG)
    c.show()
