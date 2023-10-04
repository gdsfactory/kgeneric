"""kgeneric - KLayout extras for KCells, PDK and generic_tech"""

__version__ = "0.0.2"

import kfactory as kf

from kgeneric import cells, gpdk, layers
from kgeneric.tech import TECH

kf.kcl.cells = cells


__all__ = ("pdk", "gpdk", "cells", "layers", "TECH")
