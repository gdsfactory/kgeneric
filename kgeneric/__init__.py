"""kgeneric - KLayout extras for KCells, PDK and generic_tech"""

__version__ = "0.0.2"
from kfactory.pdk import Pdk, get_cells

from kgeneric.pdk import LAYER
from kgeneric import cells


cells_dict = get_cells([cells])
pdk = Pdk(name="generic", cell_factories=cells_dict, layers=LAYER)
pdk.activate()


__all__ = ("pdk", "cells")
