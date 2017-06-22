Path simplification updates
---------------------------

Lines will now be simplified according to the ``path.simplify`` and
``path.simplify_threshold`` RC parameters, as long as other conditions
such as not using dashed lines are met. Simplification will only happen
when drawing the line segment portion of a path, if you are also drawing
markers you should consider using the ``markevery`` option to ``plot``.
