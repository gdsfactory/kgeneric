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


# %% [markdown]
## bend_circular

# %%

c = kg.cells.bend_circular(theta="90", theta_step="1")
c.plot()


# %% [markdown]
## bend_euler

# %%

c = kg.cells.bend_euler(theta="90", resolution="150")
c.plot()


# %% [markdown]
## bend_s

# %%

c = kg.cells.bend_s(nb_points="99", t_start="0", t_stop="1")
c.plot()


# %% [markdown]
## bend_s_euler

# %%

c = kg.cells.bend_s_euler(resolution="150")
c.plot()


# %% [markdown]
## coupler

# %%

c = kg.cells.coupler(gap="0p2", length="10", dy="5", dx="5", width="0p5", layer="WG")
c.plot()


# %% [markdown]
## mzi

# %%

c = kg.cells.mzi(
    delta_length="10",
    length_y="2",
    length_x="0p1",
    with_splitter="True",
    port_e1_splitter="o3",
    port_e0_splitter="o4",
    port_e0_combiner="o1",
    width="1",
    layer="0",
    radius="5",
)
c.plot()


# %% [markdown]
## straight_coupler

# %%

c = kg.cells.straight_coupler(gap="0p2", length="10", width="0p5", layer="WG")
c.plot()


# %% [markdown]
## taper

# %%

c = kg.cells.taper()
c.plot()


# %% [markdown]
## waveguide

# %%

c = kg.cells.waveguide()
c.plot()
