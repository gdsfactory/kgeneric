"""Deprecated."""

import inspect
import pathlib
from kfactory.kcell import clean_value
from kgeneric import cells_dict as cells

filepath = pathlib.Path(__file__).parent.absolute() / "cells.py"

skip = {}
skip_plot = []
skip_settings = {}


with open(filepath, "w+") as f:
    f.write(
        """

# ---
# jupyter:
#   jupytext:
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Cells

# %%

import kgeneric as kg

"""
    )

    for name in sorted(cells.keys()):
        if name in skip or name.startswith("_"):
            continue
        print(name)
        sig = inspect.signature(cells[name])
        kwargs = ", ".join(
            [
                f"{p}={repr(clean_value(sig.parameters[p].default))}"
                for p in sig.parameters
                if isinstance(sig.parameters[p].default, (int, float, str, tuple))
                and p not in skip_settings
            ]
        )
        f.write(
            f"""

# %% [markdown]
## {name}

# %%

c = kg.cells.{name}({kwargs})
c.plot()

"""
        )
