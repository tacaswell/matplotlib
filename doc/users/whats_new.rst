.. _whats-new:

==========================
 What's new in matplotlib
==========================

For a list of all of the issues and pull requests since the last
revision, see the :ref:`github-stats`.

.. contents:: Table of Contents
   :depth: 3


..
   For a release, add a new section after this, then comment out the include
   and toctree below by indenting them. Uncomment them after the release.
   .. include:: next_whats_new/README.rst
   .. toctree::
      :glob:
      :maxdepth: 1

      next_whats_new/*

New in Matplotlib 2.1
=====================

New Features
++++++++++++


Interactive JSAnimation widget
------------------------------

Jake Vanderplas' JSAnimation package has been merged into matplotlib. This
adds to matplotlib the `~matplotlib.animation.HTMLWriter` class for
generating a javascript HTML animation, suitable for the IPython notebook.
This can be activated by default by setting the ``animation.html`` rc
parameter to ``jshtml``. One can also call the ``anim_to_jshtml`` function
to manually convert an animation. This can be displayed using IPython's
``HTML`` display class::

    from IPython.display import HTML
    HTML(animation.anim_to_jshtml(anim))

The `~matplotlib.animation.HTMLWriter` class can also be used to generate
an HTML file by asking for the ``html`` writer.

Added `matplotlib.ticker.PercentFormatter`
------------------------------------------

The new formatter has some nice features like being able to convert from
arbitrary data scales to percents, a customizable percent symbol and
either automatic or manual control over the decimal points.


String Categorical support
--------------------------


Reproducible PS, PDF and SVG output
-----------------------------------

The ``SOURCE_DATE_EPOCH`` environment variable can now be used to set
the timestamp value in the PS and PDF outputs. See
https://reproducible-builds.org/specs/source-date-epoch/

Alternatively, calling ``savefig`` with ``metadata={'creationDate': None}``
will omit the timestamp altogether.

The reproducibility of the output from the PS and PDF backends has so
far been tested using various plot elements but only default values of
options such as ``{ps,pdf}.fonttype`` that can affect the output at a
low level, and not with the mathtext or usetex features. When
matplotlib calls external tools (such as PS distillers or LaTeX) their
versions need to be kept constant for reproducibility, and they may
add sources of nondeterminism outside the control of matplotlib.

For SVG output, the ``svg.hashsalt`` rc parameter has been added in an
earlier release. This parameter changes some random identifiers in the
SVG file to be deterministic. The downside of this setting is that if
more than one file is generated using deterministic identifiers
and they end up as parts of one larger document, the identifiers can
collide and cause the different parts to affect each other.

These features are now enabled in the tests for the PDF and SVG
backends, so most test output files (but not all of them) are now
deterministic.



Extensions
++++++++++
Enhancements to polar plot
--------------------------

The polar axes transforms have been greatly re-factored to allow for more
customization of view limits and tick labelling. Additional options for view
limits allow for creating an annulus, a sector, or some combination of the two.

The :meth:`~matplotlib.axes.projections.polar.PolarAxes.set_rorigin` method may
be used to provide an offset to the minimum plotting radius, producing an
annulus.

The :meth:`~matplotlib.projections.polar.PolarAxes.set_theta_zero_location` now
has an optional :code:`offset` argument. This argument may be used to further
specify the zero location based on the given anchor point.

.. figure:: ../gallery/pie_and_polar_charts/images/sphx_glr_polar_scatter_001.png
   :target: ../gallery/pie_and_polar_charts/polar_scatter.html
   :align: center
   :scale: 50

   Polar Offset Demo

The :meth:`~matplotlib.axes.projections.polar.PolarAxes.set_thetamin` and
:meth:`~matplotlib.axes.projections.polar.PolarAxes.set_thetamax` methods may
be used to limit the range of angles plotted, producing sectors of a circle.

.. figure:: ../gallery/pie_and_polar_charts/images/sphx_glr_polar_scatter_002.png
   :target: ../gallery/pie_and_polar_charts/polar_scatter.html
   :align: center
   :scale: 50

   Polar Sector Demo

Previous releases allowed plots containing negative radii for which the
negative values are simply used as labels, and the real radius is shifted by
the configured minimum. This release also allows negative radii to be used for
grids and ticks, which were previously silently ignored.

Radial ticks have been modified to be parallel to the circular grid line, and
angular ticks have been modified to be parallel to the grid line. It may also
be useful to rotate tick *labels* to match the boundary. Calling
``ax.tick_params(rotation='auto')`` will enable new behavior: radial tick
labels will be parallel to the circular grid line, and angular tick labels will
be perpendicular to the grid line (i.e., parallel to the outer boundary.)


Control stream length and dirction in `~matplotlib.axes.Axes.streamplot`
------------------------------------------------------------------------

This allows to follow the vector field for a longer time and can
enhance the visibility of the flow pattern in some use cases.


`Axis.set_tick_params` now responds to 'rotation'
-------------------------------------------------

Bulk setting of tick label rotation is now possible via :func:`set_tick_params` using the `rotation` keyword.

Example
~~~~~~~
::

    ax.xaxis.set_tick_params(which='both', rotation=90)

Users can now toggle shading in 3D bar plots
--------------------------------------------

A new ``shade`` parameter has been added the 3D bar plotting method.
The default behavior remains to shade the bars, but now users
have the option of setting ``shade`` to ``False``.


Example
~~~~~~~
::

    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(7,3))
    ax1 = fig.add_subplot(121, projection='3d')
    x = np.arange(2)
    y = np.arange(3)
    x2d, y2d = np.meshgrid(x, y)
    x2d, y2d = x2d.ravel(), y2d.ravel()
    z = x2d + y2d
    ax1.bar3d(x2d, y2d, x2d * 0, 1, 1, z, shade=True)

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.bar3d(x2d, y2d, x2d * 0, 1, 1, z, shade=False)
    fig.canvas.draw()


New which Parameter for autofmt_xdate
-------------------------------------

A ``which`` parameter now exists for the method :func:`autofmt_xdate`. This
allows a user to format ``major``, ``minor`` or ``both`` tick labels
selectively. If ``which`` is ``None`` (default) then the method will rotate
``major`` tick labels.

Example
~~~~~~~
::

    autofmt_xdate(self, bottom=0.2, rotation=30, ha='right', which='minor')


New Figure Parameter for subplot2grid
-------------------------------------

A ``fig`` parameter now exists for the method :func:`subplot2grid`.  This allows
a user to specify the figure where the subplots will be created.  If ``fig``
is ``None`` (default) then the method will use the current figure retrieved by
:func:`gcf`.

Example
~~~~~~~
::

    subplot2grid(shape, loc, rowspan=1, colspan=1, fig=myfig)


Interpolation in fill_betweenx
------------------------------

The ``interpolate`` parameter now exists for the method :func:`fill_betweenx`.
This allows a user to interpolate the data and fill the areas in the crossover
points, similarly to :func:`fill_between`.


New quiverkey angle kwarg
-------------------------

Plotting a :func:`quiverkey`  now admits the ``angle`` kwarg,
which sets the angle at which to draw the key arrow.

Colormap reversed method
------------------------

The methods :meth:`~matplotlib.colors.LinearSegmentedColormap.reversed` and
:meth:`~matplotlib.colors.ListedColormap.reversed` return a reversed
instance of the Colormap. This implements a way for any Colormap to be
reversed.


`Artist.setp` (and `pyplot.setp`) accept a `file` key-word argument
-------------------------------------------------------------------

The argument is keyword-only. It allows an output file other than
`sys.stdout` to be specified. It works exactly like the `file` argument
to `print`.


New keyword argument 'sep' for EngFormatter
-------------------------------------------

A new "sep" keyword argument has been added to
:class:`~matplotlib.ticker.EngFormatter` and provides a means to define
the string that will be used between the value and its unit. The default
string is " ", which preserves the former behavior. Besides, the separator is
now present between the value and its unit even in the absence of SI prefix.
There was formerly a bug that was causing strings like "3.14V" to be returned
instead of the expected "3.14 V" (with the default behavior).



CheckButtons widget get_status function
---------------------------------------

A :func:`get_status` function has been added the
:class:`matplotlib.widgets.CheckButtons` class. This
:func:`get_status` function allows user to query the status
(True/False) of all of the buttons in the CheckButtons object.

Add fill_bar argument to ``AnchoredSizeBar``
--------------------------------------------

The mpl_toolkits class
:class:`~mpl_toolkits.axes_grid1.anchored_artists.AnchoredSizeBar` now has an
additional ``fill_bar`` argument, which makes the size bar a solid rectangle
instead of just drawing the border of the rectangle. The default is ``None``,
and whether or not the bar will be filled by default depends on the value of
``size_vertical``. If ``size_vertical`` is nonzero, ``fill_bar`` will be set to
``True``. If ``size_vertical`` is zero then ``fill_bar`` will be set to
``False``. If you wish to override this default behavior, set ``fill_bar`` to
``True`` or ``False`` to unconditionally always or never use a filled patch
rectangle for the size bar.


Annotation can use a default arrow style
----------------------------------------

Annotations now use the default arrow style when setting `arrowprops={}`,
rather than no arrow (the new behavior actually matches the documentation).

Barbs and Quiver Support Dates
------------------------------

When using the :func:`quiver` and :func:`barbs` plotting methods,
it is now possible to pass dates, just like for other methods like
:func:`plot`. This also allows these functions to handle values
that need unit-conversion applied.


Hexbin default line color
-------------------------

The default ``linecolor`` kwarg for :func:`hexbin` is now ``'face'``, and
supplying ``'none'`` now prevents lines from being drawn around the hexagons.


New parameter `clear` for :func:`~matplotlib.pyplot.figure`
-----------------------------------------------------------

When the pyplot's function :func:`~matplotlib.pyplot.figure` is called
with a ``num`` parameter, a new window is only created if no existing
window with the same value exists. A new bool parameter `clear` was
added for explicitly clearing its existing contents. This is particularly
useful when utilized in interactive sessions. Since
:func:`~matplotlib.pyplot.subplots` also accepts keyword arguments
from :func:`~matplotlib.pyplot.figure`, it can also be used there::

   import matplotlib.pyplot as plt

   fig0 = plt.figure(num=1)
   fig0.suptitle("A fancy plot")
   print("fig0.texts: ", [t.get_text() for t in fig0.texts])

   fig1 = plt.figure(num=1, clear=False)  # do not clear contents of window
   fig1.text(0.5, 0.5, "Really fancy!")
   print("fig0 is fig1: ",  fig0 is fig1)
   print("fig1.texts: ", [t.get_text() for t in fig1.texts])

   fig2, ax2 = plt.subplots(2, 1, num=1, clear=True)  # clear contents
   print("fig0 is fig2: ",  fig0 is fig2)
   print("fig2.texts: ", [t.get_text() for t in fig2.texts])

   # The output:
   # fig0.texts:  ['A fancy plot']
   # fig0 is fig1:  True
   # fig1.texts:  ['A fancy plot', 'Really fancy!']
   # fig0 is fig2:  True
   # fig2.texts:  []


Metadata savefig kwarg
----------------------

:func:`~matplotlib.pyplot.savefig` now accepts `metadata` as a keyword argument.
It can be used to store key/value pairs in the image metadata.

Supported formats and backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* 'png' with Agg backend
* 'pdf' with PDF backend (see
  :func:`~matplotlib.backends.backend_pdf.PdfFile.writeInfoDict` for a list of
  supported keywords)
* 'eps' and 'ps' with PS backend (only 'Creator' key is accepted)

Example
~~~~~~~
::

    plt.savefig('test.png', metadata={'Software': 'My awesome software'})

Specify minimum value to format as scalar for ``LogFormatterMathtext``
----------------------------------------------------------------------

``LogFormatterMathtext`` now includes the option to specify a minimum value
exponent to format as a scalar (ie. 0.001 instead of 10^-3).




plot3D
++++++

Orthographic projection for mplot3d
-----------------------------------
:class:`~mpl_toolkits.mplot3d.axes3d.Axes3D` now accepts ``proj_type``
kwarg and has a method
:meth:`~mpl_toolkits.mplot3d.axes3d.Axes3D.set_proj_type`. The default
option is ``'persp'`` as before, and supplying ``'ortho'`` enables
orthographic view.


``voxels`` function for mplot3d
-------------------------------
:class:`~mpl_toolkits.mplot3d.axes3d.Axes3D` now has a ``voxels`` method, for
visualizing boolean 3d data. Uses could include plotting a sparse 3D heat map,
or visualizing a volumetric model.




Performance
+++++++++++
Path simplification updates
---------------------------

Line simplification controlled by the ``path.simplify`` and
``path.simplify_threshold`` parameters has been improved. You should
notice better rendering performance when plotting large amounts of
data (as long as the above parameters are set accordingly). Only the
line segment portion of paths will be simplified -- if you are also
drawing markers and experiencing problems with rendering speed, you
should consider using the ``markevery`` option to ``plot``.
See the :ref:`performance` section in the usage tutorial for more
information.

The simplification works by iteratively merging line segments
into a single vector until the next line segment's perpendicular
distance to the vector (measured in display-coordinate space)
is greater than the ``path.simplify_threshold`` parameter. Thus, higher
values of ``path.simplify_threshold`` result in quicker rendering times.
If you are plotting just to explore data and not for publication quality,
pixel perfect plots, then a value of ``1.0`` can be safely used. If you
want to make sure your plot reflects your data *exactly*, then you should
set ``path.simplify`` to false and/or ``path.simplify_threshold`` to ``0``.
Matplotlib currently defaults to a conservative value of ``1/9``, smaller
values are unlikely to cause any visible differences in your plots.



Internals
+++++++++

New TransformedPatchPath caching object
---------------------------------------

A newly added :class:`~matplotlib.transforms.TransformedPatchPath` provides a
means to transform a :class:`~matplotlib.patches.Patch` into a
:class:`~matplotlib.path.Path` via a :class:`~matplotlib.transforms.Transform`
while caching the resulting path. If neither the patch nor the transform have
changed, a cached copy of the path is returned.

This class differs from the older
:class:`~matplotlib.transforms.TransformedPath` in that it is able to refresh
itself based on the underlying patch while the older class uses an immutable
path.


Abstract base class for movie writers
-------------------------------------

The new :class:`~matplotlib.animation.AbstractMovieWriter` class defines
the API required by a class that is to be used as the `writer` in the
`save` method of the :class:`~matplotlib.animation.Animation` class.
The existing :class:`~matplotlib.animation.MovieWriter` class now derives
from the new abstract base class.

Validation of line style rcParams
---------------------------------

Stricter validation
~~~~~~~~~~~~~~~~~~~
The validation of rcParams that are related to line styles
(``lines.linestyle``, ``boxplot.*.linestyle``, ``grid.linestyle`` and
``contour.negative_linestyle``) now effectively checks that the values
are valid line styles. Strings like ``dashed`` or ``--`` are accepted,
as well as even-length sequences of on-off ink like ``[1, 1.65]``. In
this latter case, the offset value is handled internally and should *not*
be provided by the user.

The validation is case-insensitive.

Deprecation of the former validators for ``contour.negative_linestyle``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The new validation scheme replaces the former one used for the
``contour.negative_linestyle`` rcParams, that was limited to ``solid``
and ``dashed`` line styles.

The former public validation functions ``validate_negative_linestyle``
and ``validate_negative_linestyle_legacy`` will be deprecated in 2.1 and
may be removed in 2.3. There are no public functions to replace them.

Examples of use
~~~~~~~~~~~~~~~
::

    grid.linestyle             : (1, 3)   # loosely dotted grid lines
    contour.negative_linestyle : dashdot  # previously only solid or dashed




Legend
++++++

figure.legend() can be called without arguments
-----------------------------------------------

Calling :func:`figure.legend` can now be done with no arguments. In this case a
legend will be created that contains all the artists on all the axes contained
within the figure.



Multiple legend keys for legend entries
---------------------------------------

A legend entry can now contain more than one legend key. The extended
``HandlerTuple`` class now accepts two parameters: ``ndivide`` divides the
legend area in the specified number of sections; ``pad`` changes the padding
between the legend keys.

.. figure:: /gallery/text_labels_and_annotations/images/sphx_glr_legend_demo_004.png
   :target: ../../gallery/text_labels_and_annotations/legend_demo.html
   :align: center
   :scale: 50

   Multiple Legend Keys



Previous Whats New
==================

.. toctree::
   :glob:
   :maxdepth: 1
   :reversed:

   prev_whats_new/changelog
   prev_whats_new/whats_new_*
