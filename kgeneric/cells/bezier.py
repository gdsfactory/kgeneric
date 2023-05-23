"""Bezier curve based bends and functions."""

from collections.abc import Sequence

import numpy as np
import numpy.typing as nty
from scipy.special import binom  # type: ignore[import]

from kfactory import KCell, LayerEnum, cell, kdb
from kfactory.utils.enclosure import LayerEnclosure
from kfactory.utils.enclosure import extrude_path

__all__ = ["bend_s"]


def bezier_curve(
    t: nty.NDArray[np.float64],
    control_points: Sequence[tuple[np.float64 | float, np.float64 | float]],
) -> list[kdb.DPoint]:
    """Calculates the backbone of a bezier bend."""
    xs = np.zeros(t.shape, dtype=np.float64)
    ys = np.zeros(t.shape, dtype=np.float64)
    n = len(control_points) - 1
    for k in range(n + 1):
        ank = binom(n, k) * (1 - t) ** (n - k) * t**k
        xs += ank * control_points[k][0]
        ys += ank * control_points[k][1]

    return [kdb.DPoint(float(x), float(y)) for x, y in zip(xs, ys)]


@cell
def bend_s(
    width: float,
    height: float,
    length: float,
    layer: int | LayerEnum,
    nb_points: int = 99,
    t_start: float = 0,
    t_stop: float = 1,
    enclosure: LayerEnclosure | None = None,
) -> KCell:
    """Creat a bezier bend.

    Args:
        width: Width of the core. [um]
        height: height difference of left/right. [um]
        length: Length of the bend. [um]
        layer: Layer index of the core.
        nb_points: Number of points of the backbone.
        t_start: start
        t_stop: end
        enclosure: Slab/Exclude definition. [dbu]
    """
    c = KCell()
    _length, _height = length, height
    pts = bezier_curve(
        control_points=[
            (0.0, 0.0),
            (_length / 2, 0.0),
            (_length / 2, _height),
            (_length, _height),
        ],
        t=np.linspace(t_start, t_stop, nb_points),
    )

    extrude_path(c, path=pts, layer=layer, width=width, start_angle=0, end_angle=0)
    if enclosure:
        enclosure.extrude_path(c, pts, layer, width, start_angle=0, end_angle=0)
        # enclosure.apply_minkowski_tiled(c)
        # enclosure.apply_bbox(c)

    bbox_layer = c.bbox_per_layer(layer)
    c.create_port(
        name="o1",
        width=int(width / c.kcl.dbu),
        trans=kdb.Trans(2, True, 0, 0),
        layer=layer,
        port_type="optical",
    )
    c.create_port(
        name="o2",
        width=int(width / c.kcl.dbu),
        trans=kdb.Trans(
            0, False, bbox_layer.right, bbox_layer.top - int(width / c.kcl.dbu) // 2
        ),
        layer=layer,
        port_type="optical",
    )

    c.info["sim"] = "FDTD"
    return c


if __name__ == "__main__":
    from kgeneric.pdk import LAYER
    from kgeneric import pdk

    um = 1 / pdk.kcl.dbu
    enclosure = LayerEnclosure(
        [
            (LAYER.DEEPTRENCH, 2 * um, 3 * um),
            (LAYER.SLAB90, 2 * um),
        ],
        name="WGSLAB",
        main_layer=LAYER.WG,
    )

    c = bend_s(width=0.25, height=2, length=1, layer=LAYER.WG, enclosure=enclosure)
    c.draw_ports()
    c.show()
