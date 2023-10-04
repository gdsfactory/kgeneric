"""kgeneric - KLayout extras for KCells, PDK and generic_tech"""

__version__ = "0.0.2"

import kfactory as kf
from kfactory.kcell import get_cells

from kgeneric import cells, gpdk, layers
from kgeneric.layers import LAYER
from kgeneric.tech import TECH

cells_dict = get_cells([cells])

kf.kcl.factories.update(cells_dict)


__all__ = ("gpdk", "cells", "layers", "TECH", "LAYER")
