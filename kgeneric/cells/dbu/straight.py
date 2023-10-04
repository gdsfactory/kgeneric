"""Straight waveguide in dbu.

A straight is a rectangle of material with excludes and/or slab around it::

    ┌──────────────────────────────┐
    │         Slab/Exclude         │
    ├──────────────────────────────┤
    │                              │
    │             Core             │
    │                              │
    ├──────────────────────────────┤
    │         Slab/Exclude         │
    └──────────────────────────────┘

The slabs and excludes can be given in the form of an :py:class:~`Enclosure`.
"""

from kfactory import KCell, LayerEnum, cell, kdb
from kfactory.enclosure import LayerEnclosure
from kfactory.kcell import Info

__all__ = ["straight"]


@cell
def straight(
    width: int,
    length: int,
    layer: int | LayerEnum,
    enclosure: LayerEnclosure | None = None,
) -> KCell:
    """Waveguide defined in dbu.

    Visualization::

        ┌──────────────────────────────┐
        │         Slab/Exclude         │
        ├──────────────────────────────┤
        │                              │
        │             Core             │
        │                              │
        ├──────────────────────────────┤
        │         Slab/Exclude         │
        └──────────────────────────────┘
    Args:
        width: Waveguide width. [dbu]
        length: Waveguide length. [dbu]
        layer: Layer index / :py:class:~`LayerEnum`.
        enclosure: Definition of slab/excludes. [dbu]
    """
    c = KCell()

    if width // 2 * 2 != width:
        raise ValueError("The width (w) must be a multiple of 2 database units")

    c.shapes(layer).insert(kdb.Box(0, -width // 2, length, width // 2))
    c.create_port(name="o1", trans=kdb.Trans(2, False, 0, 0), layer=layer, width=width)
    c.create_port(
        name="o2", trans=kdb.Trans(0, False, length, 0), layer=layer, width=width
    )

    if enclosure is not None:
        enclosure.apply_minkowski_y(c, layer)
    c.info = Info(
        **{
            "width_um": width * c.kcl.dbu,
            "length_um": length * c.kcl.dbu,
            "width_dbu": width,
            "length_dbu": length,
        }
    )
    c.autorename_ports()

    return c
