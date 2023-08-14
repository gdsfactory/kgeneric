"""kgeneric - KLayout extras for KCells, PDK and generic_tech"""

__version__ = "0.0.2"
from kfactory.pdk import Pdk, get_cells

from kgeneric import cells, gpdk, layers
from kgeneric.layers import LAYER
from kgeneric.tech import TECH

cells_dict = get_cells([gpdk])
pdk = Pdk(name="generic", cell_factories=cells_dict, layers=LAYER)


__all__ = ("pdk", "gpdk", "cells", "layers", "TECH")
