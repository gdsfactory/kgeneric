
Here are some generic Parametric cells.

You can customize them your fab or use them as an inspiration to build your own.


Parametric cells
=============================



bend_circular
----------------------------------------------------

.. autofunction:: kgeneric.cells.bend_circular

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.bend_circular(width=1, radius=10, layer=<LAYER.WG: 0>, angle=90, angle_step=1)
  fig = c.plot()
  glue("boot_fig", fig, display=True)



bend_euler
----------------------------------------------------

.. autofunction:: kgeneric.cells.bend_euler

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.bend_euler(width=1, radius=10, layer=<LAYER.WG: 0>, angle=90, resolution=150)
  c.plot()



bend_s_euler
----------------------------------------------------

.. autofunction:: kgeneric.cells.bend_s_euler

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.bend_s_euler(offset=0, width=0.5, radius=5, layer=<LAYER.WG: 0>, resolution=150)
  c.plot()



coupler
----------------------------------------------------

.. autofunction:: kgeneric.cells.coupler

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.coupler(gap=0.2, length=10.0, dy=5.0, dx=5.0, width=0.5, layer=<LAYER.WG: 0>)
  fig = c.plot()
  glue("boot_fig", fig, display=True)



grating_coupler_elliptical
----------------------------------------------------

.. autofunction:: kgeneric.cells.grating_coupler_elliptical

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.grating_coupler_elliptical(polarization='te', taper_length=16600, taper_angle=40.0, trenches_extra_angle=10.0, lambda_c=1.554, fiber_angle=15.0, grating_line_width=343, wg_width=500, neff=2.638, layer_taper=<LAYER.WG: 0>, layer_trench=<LAYER.UNDERCUT: 7>, p_start=26, n_periods=30, taper_offset=0, taper_extent_n_periods='last', clad_index=1.443)
  c.plot()



mzi
----------------------------------------------------

.. autofunction:: kgeneric.cells.mzi

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.mzi(delta_length=10.0, length_y=2.0, length_x=0.1, with_splitter=True, port_e1_splitter='o3', port_e0_splitter='o4', port_e0_combiner='o1', width=1.0, layer=0, radius=5.0)
  c.plot()



straight
----------------------------------------------------

.. autofunction:: kgeneric.cells.straight

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.straight(width=0.5, length=1, layer=<LAYER.WG: 0>)
  c.plot()



straight_coupler
----------------------------------------------------

.. autofunction:: kgeneric.cells.straight_coupler

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.straight_coupler(gap=0.2, length=10.0, width=0.5, layer=<LAYER.WG: 0>)
  c.plot()



taper
----------------------------------------------------

.. autofunction:: kgeneric.cells.taper

.. plot::
  :include-source:

  import kgeneric.cells as kc

  c = kc.taper(width1=0.5, width2=1, length=10, layer=<LAYER.WG: 0>)
  c.plot()
