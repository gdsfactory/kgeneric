import inspect
import pathlib

import numpy as np
from kfactory.kcell import Any, Callable, KCell, LayerEnum, clean_name

from kgeneric.tests.test_cells import cell_factories as cells


def dict2name(prefix: str = "", **kwargs) -> str:
    """Returns name from a dict."""
    ignore_from_name = kwargs.pop("ignore_from_name", [])
    kv = []
    kwargs = kwargs.copy()
    kwargs.pop("layer_to_inclusion", "")

    for key in sorted(kwargs):
        if key not in ignore_from_name and isinstance(key, str):
            value = kwargs[key]
            # key = join_first_letters(key).upper()
            if value is not None:
                kv += [f"{key}{clean_name(value)}"]
    label = prefix + "_".join(kv)
    return clean_name(label)


def clean_value_json(
    value: float | np.float64 | dict[Any, Any] | KCell | Callable[..., Any]
) -> float | np.float64:
    """Makes sure a value is representable in a limited character_space."""
    try:
        if isinstance(value, int):  # integer
            return value
        elif isinstance(value, LayerEnum):
            return value.name
        elif type(value) in [float, np.float64]:  # float
            return np.round(value, 3)
        elif isinstance(value, tuple | list):
            return value
        elif isinstance(value, dict):
            return dict2name(**value)
        elif hasattr(value, "name"):
            return clean_name(value.name)
        elif callable(value):
            return str(value.__name__)
        else:
            return clean_name(value)
    except TypeError:  # use the __str__ method
        return clean_name(value)


filepath = pathlib.Path(__file__).parent.absolute() / "cells.rst"

skip = {}
skip_plot = []
skip_settings = {}


with open(filepath, "w+") as f:
    f.write(
        """
Here are some generic Parametric cells.

You can customize them your fab or use them as an inspiration to build your own.


Parametric cells
=============================

"""
    )

    for name in sorted(cells.keys()):
        if name in skip or name.startswith("_"):
            continue
        print(name)
        sig = inspect.signature(cells[name])
        kwargs = ", ".join(
            [
                f"{p}={repr(clean_value_json(sig.parameters[p].default))}"
                for p in sig.parameters
                if isinstance(sig.parameters[p].default, int | float | str | tuple)
                and p not in skip_settings
            ]
        )
        if name in skip_plot:
            f.write(
                f"""

{name}
----------------------------------------------------

.. autofunction:: kgeneric.cells.{name}

"""
            )
        else:
            f.write(
                f"""

{name}
----------------------------------------------------

.. autofunction:: kgeneric.cells.{name}

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.{name}({kwargs})
  c.plot()

"""
            )
