from functools import partial
from typing import Optional

import kfactory as kf
from kfactory import cell
from kfactory.routing.optical import route
from kfactory.typings import CellFactory
from kfactory.utils.enclosure import LayerEnclosure

from kgeneric.cells.dbu.straight import straight as straight_dbu_function
from kgeneric.cells.DCs import coupler
from kgeneric.cells.euler import bend_euler
from kgeneric.cells.straight import straight as straight_function


@cell
def mzi(
    delta_length: float = 10.0,
    length_y: float = 2.0,
    length_x: Optional[float] = 0.1,
    bend: CellFactory = bend_euler,
    straight: CellFactory = straight_function,
    straight_dbu: CellFactory = straight_dbu_function,
    straight_y: Optional[CellFactory] = None,
    straight_x_top: Optional[CellFactory] = None,
    straight_x_bot: Optional[CellFactory] = None,
    splitter: CellFactory = coupler,
    combiner: CellFactory | None = None,
    with_splitter: bool = True,
    port_e1_splitter: str = "o3",
    port_e0_splitter: str = "o4",
    port_e0_combiner: str = "o1",
    enclosure: Optional[LayerEnclosure] = None,
    min_length: float = 10.0,
) -> kf.KCell:
    """Mzi.
    Args:
        delta_length: bottom arm vertical extra length.
        length_y: vertical length for both and top arms.
        length_x: horizontal length. None uses to the straight_x_bot/top defaults.
        bend: 90 degrees bend library.
        straight: straight function.
        straight_y: straight for length_y and delta_length.
        straight_x_top: top straight for length_x.
        straight_x_bot: bottom straight for length_x.
        splitter: splitter function.
        combiner: combiner function.
        with_splitter: if False removes splitter.
        port_e1_splitter: east top splitter port.
        port_e0_splitter: east bot splitter port.
        port_e0_combiner: east bot combiner port.
        enclosure: waveguide enclosure.
        kwargs: combiner/splitter kwargs.

    .. code::
                       b2______b3
                      |  sxtop  |
              straight_y        |
                      |         |
                      b1        b4
            splitter==|         |==combiner
                      b5        b8
                      |         |
              straight_y        |
                      |         |
        delta_length/2          |
                      |         |
                     b6__sxbot__b7
                          Lx

    """
    combiner = combiner or splitter
    straight_x_top = straight_x_top or straight
    straight_x_bot = straight_x_bot or straight
    straight_y = straight_y or straight

    bend = bend()
    c = kf.KCell()
    combiner = combiner or splitter

    _cp1 = splitter()

    cp1 = c << _cp1 if with_splitter else _cp1
    cp2 = c << _cp1
    b5 = c << bend
    b5.connect("o2", cp2.ports[port_e0_splitter])

    syl = c << straight_y(
        length=delta_length / 2 + length_y,
        enclosure=enclosure,
    )
    syl.connect("o1", b5.ports["o1"])
    b6 = c << bend
    b6.connect("o2", syl.ports["o2"], mirror=True)
    # b6.transform(kf.kdb.Trans.M90.R270)

    straight_x_bot = straight_x_top(
        length=length_x,
        enclosure=enclosure,
    )

    sxb = c << straight_x_bot
    sxb.connect("o1", b6.ports["o2"], mirror=True)

    b1 = c << bend
    b1.connect("o1", cp1.ports[port_e1_splitter])

    sytl = c << straight_y(length=length_y, enclosure=enclosure)
    sytl.connect("o1", b1.ports["o2"])

    b2 = c << bend
    b2.connect("o2", sytl.ports["o2"])
    straight_x_top = straight_x_top(
        length=length_x,
        enclosure=enclosure,
    )
    sxt = c << straight_x_top
    sxt.connect("o1", b2.ports["o1"])

    cp2.d.xmin = sxt.ports["o2"].d.x + bend.info["radius"] * 2 + 2 * min_length

    route(
        c,
        cp2.ports["o2"],
        sxt.ports["o2"],
        straight_dbu,
        bend,
    )
    route(
        c,
        cp2.ports["o1"],
        sxb.ports["o1"],
        straight_dbu,
        bend,
    )

    if with_splitter:
        c.add_ports([port for port in cp1.ports if port.orientation == 180])
    else:
        c.add_port(name="o1", port=b1.ports["o1"])
        c.add_port(name="o2", port=b5.ports["o1"])
    c.add_ports([port for port in cp2.ports if port.orientation == 0])
    c.autorename_ports()
    return c


if __name__ == "__main__":
    from kgeneric.pdk import LAYER
    from kgeneric import pdk

    width = 0.5
    s_sc = partial(pdk.cell_factories.straight, width=width, layer=LAYER.WG)
    sdbu_sc = partial(pdk.cell_factories.straight_dbu, width=width, layer=LAYER.WG)
    b_sc = partial(
        pdk.cell_factories.bend_euler, width=width, radius=10, layer=LAYER.WG
    )

    um = 1 / pdk.kcl.dbu
    enclosure = LayerEnclosure(
        [
            (LAYER.DEEPTRENCH, 2 * um, 3 * um),
            (LAYER.SLAB90, 2 * um),
        ],
        name="WGSLAB",
        main_layer=LAYER.WG,
    )
    c = mzi(
        length_x=1,
        with_splitter=True,
        enclosure=enclosure,
        straight=s_sc,
        bend=b_sc,
        straight_dbu=sdbu_sc,
    )
    c.draw_ports()
    c.show()
