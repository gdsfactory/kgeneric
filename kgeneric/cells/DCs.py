from typing import Union

from kfactory import KCell, cell, kdb

from kfactory.kcell import LayerEnum

from kfactory.utils.enclosure import LayerEnclosure

from kgeneric.pdk import LAYER
from kgeneric.cells.bezier import bend_s
from kgeneric.cells.waveguide import waveguide


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
        enclosure: waveguide enclosure.
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
    sbend = c << bend_s(
        width=width,
        height=((dy) / 2 - gap / 2 - width / 2),
        length=dx,
        layer=layer,
        enclosure=enclosure,
    )
    sbend_2 = c << bend_s(
        width=width,
        height=((dy) / 2 - gap / 2 - width / 2),
        length=dx,
        layer=layer,
        enclosure=enclosure,
    )

    wg = c << straight_coupler(gap, length, width, layer, enclosure)

    sbend.align("o2", wg.ports["o1"])
    sbend_2.align("o2", wg.ports["o4"])
    sbend_r_top = c << bend_s(
        width=width,
        height=(dy / 2 - width / 2 - gap / 2),
        length=dx,
        layer=layer,
        enclosure=enclosure,
    )
    sbend_r_bottom = c << bend_s(
        width=width,
        height=(dy / 2 - width / 2 - gap / 2),
        length=dx,
        layer=layer,
        enclosure=enclosure,
    )

    sbend_r_top.align("o1", wg.ports["o3"])
    sbend_r_bottom.align("o1", wg.ports["o2"])

    # sbend_r_top.transform(kdb.DTrans(0, False, 0, 0))
    # sbend_r_bottom.transform(kdb.DTrans(0, False, 0, 0))

    c.add_port(name="o1", port=sbend_2.ports["o1"])
    c.add_port(name="o2", port=sbend.ports["o1"])
    c.add_port(name="o3", port=sbend_r_bottom.ports["o2"])
    c.add_port(name="o4", port=sbend_r_top.ports["o2"])
    c.begin_instances_rec()
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
        enclosure: waveguide enclosure.
    """
    c = KCell()

    wg_top = c << waveguide(width, length, layer, enclosure)
    wg_top.trans = kdb.Trans(0, True, 0, int((gap + width) / 2 / c.kcl.dbu))

    wg_bottom = c << waveguide(width, length, layer, enclosure)
    wg_bottom.trans = kdb.Trans(0, False, 0, -int((gap + width) / 2 / c.kcl.dbu))

    c.add_port(name="o1", port=wg_top.ports["o1"])
    c.add_port(name="o2", port=wg_top.ports["o2"])
    c.add_port(name="o3", port=wg_bottom.ports["o2"])
    c.add_port(name="o4", port=wg_bottom.ports["o1"])

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
    c.show()
