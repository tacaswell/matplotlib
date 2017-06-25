Path simplification updates
---------------------------

Lines will now be simplified according to the ``path.simplify`` and
``path.simplify_threshold`` RC parameters, as long as other conditions
such as not using dashed lines are met. Simplification will only happen
when drawing the line segment portion of a path, if you are also drawing
markers you should consider using the ``markevery`` option to ``plot``.

The ``path.simplify_threshold`` parameter controls the tolerance used
when deciding if two consecutive line segments can be merged.
If you are plotting just to explore data and not for publication quality,
pixel perfect plots, then a value of `1.0` can be safely used. If you
want to make sure your plot reflects your data *exactly*, then you should
set ``path.simplify`` to false and/or ``path.simplify_threshold`` to 0.
