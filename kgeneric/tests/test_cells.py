from functools import partial
import pathlib
import pytest

from kfactory import kdb
import kfactory as kf
from kfactory.conf import logger

from kgeneric import cells
from kgeneric.pdk import LAYER


class GeometryDifference(ValueError):
    """Exception for Geometric differences."""

    pass


wg_enc = kf.utils.LayerEnclosure(name="WGSTD", sections=[(LAYER.WGCLAD, 0, 2000)])

straight = partial(
    cells.straight, width=0.5, length=1, layer=LAYER.WG, enclosure=wg_enc
)

bend90 = partial(
    cells.circular.bend_circular,
    width=1,
    radius=10,
    layer=LAYER.WG,
    enclosure=wg_enc,
    angle=90,
)


bend180 = partial(
    cells.circular.bend_circular,
    width=1,
    radius=10,
    layer=LAYER.WG,
    enclosure=wg_enc,
    angle=180,
)


bend90_euler = partial(
    cells.euler.bend_euler,
    width=1,
    radius=10,
    layer=LAYER.WG,
    enclosure=wg_enc,
    angle=90,
)


bend180_euler = partial(
    cells.euler.bend_euler,
    width=1,
    radius=10,
    layer=LAYER.WG,
    enclosure=wg_enc,
    angle=180,
)

coupler = cells.coupler
straight_coupler = cells.straight_coupler

GC_TE = cells.GC_TE
GC_TM = cells.GC_TM

taper = partial(
    cells.taper,
    width1=0.5,
    width2=1,
    length=10,
    layer=LAYER.WG,
    enclosure=wg_enc,
)

bend_s_euler = partial(
    cells.bend_s_euler,
    offset=0,
    width=0.5,
    radius=5,
    layer=LAYER.WG,
    enclosure=wg_enc,
)

mzi = cells.mzi
straight_coupler = cells.straight_coupler


cell_factories = dict(
    bend_circular=bend90,
    bend_euler=bend90_euler,
    bend_s_euler=bend_s_euler,
    coupler=coupler,
    GC_TE=GC_TE,
    GC_TM=GC_TM,
    straight_coupler=straight_coupler,
    mzi=mzi,
    taper=taper,
    straight=straight,
)

cell_names = set(cell_factories.keys())


@pytest.fixture(params=cell_names, scope="function")
def cell_name(request):
    """Returns cell name."""
    return request.param


def test_cells(cell_name: str) -> None:
    """Ensure cells have the same geometry as their golden references."""
    gds_ref = pathlib.Path(__file__).parent / "gds" / "gds_ref"
    cell = cell_factories[cell_name]()
    ref_file = gds_ref / f"{cell.name}.gds"
    run_cell = cell
    if not ref_file.exists():
        gds_ref.mkdir(parents=True, exist_ok=True)
        run_cell.write(str(ref_file))
        raise FileNotFoundError(f"GDS file not found. Saving it to {ref_file}")
    kcl_ref = kf.KCLayout()
    kcl_ref.read(gds_ref / f"{cell.name}.gds")
    ref_cell = kcl_ref[kcl_ref.top_cell().name]

    for layer in kcl_ref.layer_infos():
        layer = kcl_ref.layer(layer)
        region_run = kdb.Region(run_cell.begin_shapes_rec(layer))
        region_ref = kdb.Region(ref_cell.begin_shapes_rec(layer))

        region_diff = region_run - region_ref

        if not region_diff.is_empty():
            layer_tuple = kcl_ref.layer_infos()[layer]
            region_xor = region_ref ^ region_run
            c = kf.KCell(f"{cell.name}_diffs")
            c_run = kf.KCell(f"{cell.name}_new")
            c_ref = kf.KCell(f"{cell.name}_old")
            c_xor = kf.KCell(f"{cell.name}_xor")
            c_run.shapes(layer).insert(region_run)
            c_ref.shapes(layer).insert(region_ref)
            c_xor.shapes(layer).insert(region_xor)
            c << c_run
            c << c_ref
            c << c_xor
            c.show()

            print(f"Differences found in {cell!r} on layer {layer_tuple}")
            val = input("Save current GDS as new reference (Y)? [Y/n]")
            if not val.upper().startswith("N"):
                logger.info(f"replacing file {str(ref_file)!r}")
                run_cell.write(ref_file.name)

            raise GeometryDifference(
                f"Differences found in {cell!r} on layer {layer_tuple}"
            )
