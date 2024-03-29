"""Taper definitions [dbu].

TODO: Non-linear tapers
"""

from kfactory import KCell, cell, kdb
from kfactory.enclosure import LayerEnclosure

__all__ = ["taper"]


@cell
def taper(
    width1: int,
    width2: int,
    length: int,
    layer: int,
    enclosure: LayerEnclosure | None = None,
) -> KCell:
    r"""Linear Taper [um].

    Visualization::

               __
             _/  │ Slab/Exclude
           _/  __│
         _/  _/  │
        │  _/    │
        │_/      │
        │_       │ Core
        │ \_     │
        │_  \_   │
          \_  \__│
            \_   │
              \__│ Slab/Exclude

    Args:
        width1: Width of the core on the left side. [dbu]
        width2: Width of the core on the right side. [dbu]
        length: Length of the taper. [dbu]
        layer: Layer index / :py:class:~`LayerEnum` of the core.
        enclosure: Definition of the slab/exclude.
    """
    c = KCell()

    c.shapes(layer).insert(
        kdb.Polygon(
            [
                kdb.Point(0, int(-width1 / 2)),
                kdb.Point(0, width1 // 2),
                kdb.Point(length, width2 // 2),
                kdb.Point(length, int(-width2 / 2)),
            ]
        )
    )

    c.create_port(name="o1", trans=kdb.Trans(2, False, 0, 0), width=width1, layer=layer)
    c.create_port(
        name="o2", trans=kdb.Trans(0, False, length, 0), width=width2, layer=layer
    )

    if enclosure is not None:
        enclosure.apply_minkowski_y(c, kdb.Region(c.bbox()))
    c.info["width1_um"] = width1 * c.kcl.dbu
    c.info["width2_um"] = width2 * c.kcl.dbu
    c.info["length_um"] = length * c.kcl.dbu

    return c
