""" Example on how to build a generic PDK."""
import kfactory as kf

from functools import partial
from kgeneric.tech import TECH
from kgeneric import cells
from kgeneric.layers import LAYER

enclosure_sc = kf.utils.LayerEnclosure(name="WGSTD", sections=[(LAYER.WGCLAD, 0, 2000)])

bend_s_sc = partial(
    cells.bend_s,
    width=TECH.width_sc,
    height=10,
    length=20,
    layer=LAYER.WG,
    enclosure=enclosure_sc,
)
straight_sc = partial(
    cells.straight,
    length=10,
    width=TECH.width_sc,
    layer=LAYER.WG,
    enclosure=enclosure_sc,
)
straight_dbu_sc = partial(
    cells.straight_dbu,
    length=int(10e3),
    width=int(TECH.width_sc * 1e3),
    layer=LAYER.WG,
    enclosure=enclosure_sc,
)

bend_euler_sc = partial(
    cells.bend_euler,
    width=TECH.width_sc,
    layer=LAYER.WG,
    radius=TECH.radius_sc,
    enclosure=enclosure_sc,
)
bend_circular_sc = partial(
    cells.bend_circular,
    width=TECH.width_sc,
    layer=LAYER.WG,
    radius=TECH.radius_sc,
    enclosure=enclosure_sc,
)

taper_sc = partial(
    cells.taper,
    width1=TECH.width_sc,
    width2=TECH.width_sc * 2,
    length=10,
    layer=LAYER.WG,
    enclosure=enclosure_sc,
)

grating_coupler_sc = partial(cells.grating_coupler_elliptical, wg_width=TECH.width_sc)

# mzi_sc = partial(cells.mzi, bend=bend_s_sc, straight=straight_sc) # TODO: fix


if __name__ == "__main__":
    c = straight_sc()
    c.show()
