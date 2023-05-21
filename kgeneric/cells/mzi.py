from functools import partial
from typing import Any, Callable, Optional

import kfactory as kf
from kfactory import cell
from kfactory.kcell import LayerEnum
from kfactory.routing.optical import route
from kfactory.typings import CellSpec
from kfactory.utils.enclosure import LayerEnclosure

from kgeneric.cells.dbu.waveguide import waveguide as waveguide_dbu
from kgeneric.cells.DCs import coupler
from kgeneric.cells.euler import bend_euler
from kgeneric.cells.waveguide import waveguide as straight_function


@cell
def mzi(
    delta_length: float = 10.0,
    length_y: float = 2.0,
    length_x: Optional[float] = 0.1,
    bend_component: Callable[..., kf.KCell] = bend_euler,
    straight: CellSpec = straight_function,
    straight_y: Optional[CellSpec] = None,
    straight_x_top: Optional[CellSpec] = None,
    straight_x_bot: Optional[CellSpec] = None,
    splitter: CellSpec = coupler,
    combiner: Optional[CellSpec] = None,
    with_splitter: bool = True,
    port_e1_splitter: str = "o3",
    port_e0_splitter: str = "o4",
    port_e0_combiner: str = "o1",
    width: float = 1.0,
    layer: int | LayerEnum = 0,
    radius: float = 5.0,
    enclosure: Optional[LayerEnclosure] = None,
    **kwargs: Any,
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
        width: waveguide width.
        layer: waveguide layer.
        radius: bend radius.
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

    straight_x_top = (
        partial(straight_x_top, layer=layer)
        if straight_x_top and callable(straight_x_top)
        else None
    )
    straight_x_bot = (
        partial(straight_x_bot, layer=layer)
        if straight_x_bot and callable(straight_x_bot)
        else None
    )
    straight_x_top = straight_x_top or straight
    straight_x_bot = straight_x_bot or straight
    straight_y = straight_y or straight

    bend_settings = {
        "width": width,
        "layer": layer,
        "radius": radius,
        "enclosure": enclosure,
    }
    bend = kf.kcl.pdk.get_cell(bend_component, **bend_settings)
    c = kf.KCell()
    straight_connect = partial(waveguide_dbu, layer=layer, enclosure=enclosure)
    combiner_settings = {
        "width": width,
        "layer": layer,
        "enclosure": enclosure,
    }
    kwargs.pop("kwargs", "")
    kwargs |= combiner_settings
    _cp1 = kf.kcl.pdk.get_cell(splitter, **kwargs)
    kf.kcl.pdk.get_cell(combiner, **kwargs) if combiner else _cp1

    if with_splitter:
        cp1 = c << _cp1
    else:
        cp1 = _cp1

    cp2 = c << _cp1
    b5 = c << bend
    # b5.transform(kf.kdb.Trans.M90)
    b5.align("W0", cp2.ports[port_e0_splitter])
    # b5.instance.transform(kf.kdb.Trans(1, False, 0, 0))
    # b5.transform(kf.kdb.Trans.M90.R180)

    syl = c << kf.kcl.pdk.get_cell(
        straight_y,
        length=delta_length / 2 + length_y,
        width=width,
        layer=layer,
        enclosure=enclosure,
    )
    syl.align("o1", b5.ports["N0"])
    b6 = c << bend
    b6.align("W0", syl.ports["o2"], mirror=True)
    # b6.transform(kf.kdb.Trans.M90.R270)

    straight_x_bot = (
        kf.kcl.pdk.get_cell(
            straight_x_bot,
            width=width,
            length=length_x,
            layer=layer,
            enclosure=enclosure,
        )
        if length_x
        else kf.kcl.pdk.get_cell(
            straight_x_bot,
            length=length_x,
            width=width,
            layer=layer,
            enclosure=enclosure,
        )
    )

    sxb = c << straight_x_bot
    sxb.align("o1", b6.ports["N0"], mirror=True)

    b1 = c << bend
    b1.align("W0", cp1.ports[port_e1_splitter])

    sytl = c << kf.kcl.pdk.get_cell(
        straight_y, length=length_y, width=width, layer=layer, enclosure=enclosure
    )
    sytl.align("o1", b1.ports["N0"])

    b2 = c << bend
    b2.align("N0", sytl.ports["o2"])
    straight_x_top = (
        kf.kcl.pdk.get_cell(
            straight_x_top,
            length=length_x,
            width=width,
            layer=layer,
            enclosure=enclosure,
        )
        if length_x
        else kf.kcl.pdk.get_cell(
            straight_x_top,
            length=length_x,
            width=width,
            layer=layer,
            enclosure=enclosure,
        )
    )
    sxt = c << straight_x_top
    sxt.align("o1", b2.ports["W0"])

    # cp2.transform(port_e0_combiner, cp1.ports[port_e0_splitter])

    bend_width = abs(bend.ports[0].x - bend.ports[1].x)
    cp2.align(port_e0_combiner, cp1.ports[port_e0_splitter])
    cp2.transform(
        kf.kdb.Trans(sxt.ports["o2"].x - cp2.ports["o1"].x + 2 * bend_width, 0)
    )

    route(
        c,
        cp2.ports["o2"],
        sxt.ports["o2"],
        straight_connect,
        bend,
    )
    route(
        c,
        cp2.ports["o1"],
        sxb.ports["o2"],
        straight_connect,
        bend,
    )

    if with_splitter:
        c.add_ports([port for port in cp1.ports if port.orientation == 180])
    else:
        c.add_port(name="o1", port=b1.ports["W0"])
        c.add_port(name="o2", port=b5.ports["W0"])
    c.add_ports([port for port in cp2.ports if port.orientation == 0])
    c.autorename_ports()
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
    c = mzi(length_x=1, with_splitter=True, enclosure=enclosure)
    c.draw_ports()
    r0 = c.insts[0]
    r1 = c.insts[1]
    r2 = c.insts[2]
    print(r0)
    print(list(c.insts))
    c.show()
