from typing import Union

from kfactory import KCell, cell

from kfactory.kcell import LayerEnum

from kfactory.utils.enclosure import LayerEnclosure

from kgeneric.pdk import LAYER
from kgeneric.cells.bezier import bend_s
from kgeneric.cells.straight import straight


@cell
def coupler(
    gap: float = 0.2,
    length: float = 10.0,
    dy: float = 5.0,
    dx: float = 5.0,
    width: float = 0.5,
    layer: Union[int, LayerEnum] = LAYER.WG,
    enclosure: LayerEnclosure = LayerEnclosure(),
) -> KCell:
    r"""Symmetric coupler.
    Args:
        gap: between straights in um.
        length: of coupling region in um.
        dy: port to port vertical spacing in um.
        dx: length of bend in x direction in um.
        layer: layer number or name.
        enclosure: straight enclosure.

    .. code::
               dx                                 dx
            |------|                           |------|
         o2 ________                           ______o3
                    \                         /           |
                     \        length         /            |
                      ======================= gap         | dy
                     /                       \            |
            ________/                         \_______    |
         o1                                          o4
    """
    c = KCell()
    enclosure = enclosure if enclosure is not None else LayerEnclosure()
    _bend_s = bend_s(
        width=width,
        height=((dy) / 2 - gap / 2 - width / 2),
        length=dx,
        layer=layer,
        enclosure=enclosure,
    )
    sbend_l_top = c << _bend_s
    sbend_l_bot = c << _bend_s
    wg = c << straight_coupler(gap, length, width, layer, enclosure)

    sbend_l_top.connect("o1", wg.ports["o1"])
    sbend_l_bot.connect("o2", wg.ports["o4"])

    sbend_r_top = c << _bend_s
    sbend_r_bot = c << _bend_s

    sbend_r_top.connect("o2", wg.ports["o2"])
    sbend_r_bot.connect("o1", wg.ports["o3"])

    c.add_port(name="o1", port=sbend_l_bot.ports["o1"])
    c.add_port(name="o2", port=sbend_l_top.ports["o2"])
    c.add_port(name="o3", port=sbend_r_top.ports["o1"])
    c.add_port(name="o4", port=sbend_r_bot.ports["o2"])
    return c


@cell
def straight_coupler(
    gap: float = 0.2,
    length: float = 10.0,
    width: float = 0.5,
    layer: Union[int, LayerEnum] = LAYER.WG,
    enclosure: LayerEnclosure = LayerEnclosure(),
) -> KCell:
    """Straight coupler.

    Args:
        gap: between straights in um.
        length: of coupling region in um.
        layer: layer number or name.
        enclosure: straight enclosure.
    """
    c = KCell()

    wg_top = c << straight(width, length, layer, enclosure)
    wg_bot = c << straight(width, length, layer, enclosure)
    wg_top.d.movey(width + gap)

    c.add_port(name="o1", port=wg_top.ports["o1"])
    c.add_port(name="o2", port=wg_top.ports["o2"])
    c.add_port(name="o3", port=wg_bot.ports["o2"])
    c.add_port(name="o4", port=wg_bot.ports["o1"])

    c.info["sim"] = "MODE"
    return c


if __name__ == "__main__":
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

    c = coupler(enclosure=enclosure)
    c.draw_ports()
    c.show()
