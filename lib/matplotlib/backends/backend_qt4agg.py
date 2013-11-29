"""
Render to qt from agg
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

# import Gcf/pyplot stuff
from matplotlib._pylab_helpers import Gcf
from matplotlib.backend_bases import key_press_handler

# import Gcf stuff from QT4 backend
from .backend_qt4 import show
from .backend_qt4 import draw_if_interactive
from .backend_qt4 import backend_version
# import clean stuff from qt4 backend
from ._backend_qt4 import (TimerQT,
                            SubplotToolQt,
                            backend_version)

# import qtAgg stuff
from ._backend_qt4agg import (new_figure_manager,
                              new_figure_manager_given_figure,
                              FigureManagerQT,
                              NavigationToolbar2QT,
                              FigureCanvasQTAgg)


FigureCanvas = FigureCanvasQTAgg
FigureManager = FigureManagerQT

# register default key_handlers
FigureManager._key_press_handler = staticmethod(key_press_handler)
FigureManager._destroy_callback = staticmethod(Gcf.destroy)
