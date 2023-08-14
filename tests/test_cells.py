import pathlib

import kfactory as kf
import pytest
from kfactory import kdb
from kfactory.conf import logger

from kgeneric import cells_dict


class GeometryDifference(ValueError):
    """Exception for Geometric differences."""

    pass


cell_names = set(cells_dict.keys())


@pytest.fixture(params=cell_names, scope="function")
def cell_name(request):
    """Returns cell name."""
    return request.param


def test_cells(cell_name: str) -> None:
    """Ensure cells have the same geometry as their golden references."""
    gds_ref = pathlib.Path(__file__).parent / "gds" / "gds_ref"
    cell = cells_dict[cell_name]()
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
