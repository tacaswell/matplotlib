from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import warnings

from matplotlib._pylab_helpers import Gcf
from ._backend_gtk3agg import (FigureCanvasGTK3Agg,
                            new_figure_manager,
                            new_figure_manager_given_figure
                            )

from ._backend_gtk3 import FigureManagerGTK3
from .backend_gtk3 import (show,
                           draw_if_interactive,
                           _gtk_cleanup,
                           key_press_handler)


if six.PY3:
    warnings.warn("The Gtk3Agg backend is not known to work on Python 3.x.")


FigureCanvas = FigureCanvasGTK3Agg
FigureManager = FigureManagerGTK3
