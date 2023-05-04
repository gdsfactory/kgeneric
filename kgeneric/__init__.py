"""KGeneric - KLayout extras for KCells, PDK and generic_tech"""

__version__ = "0.0.1"
from kfactory.pdk import Pdk, get_cells

from kgeneric.pdk import LAYER
from kgeneric import cells


pdk = Pdk(name="generic", cells=get_cells(cells), layers=LAYER)
pdk.activate()


__all__ = ("pdk",)
