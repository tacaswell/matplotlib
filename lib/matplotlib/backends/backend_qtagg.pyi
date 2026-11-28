from typing import Any

from matplotlib.backend_bases import ShowBase
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_qt import (
    FigureCanvasQT,
    FigureManagerQT as FigureManagerQT,
    NavigationToolbar2QT as NavigationToolbar2QT,
    TimerQT,
    _BackendQT,
)

class FigureCanvasQTAgg(
    # Both bases derive from ``FigureCanvasBase``, so they must get the same
    # type arguments or the checkers see two inconsistent specializations of
    # it.
    #
    # This class is a leaf: it joins a renderer to the Qt canvas and is not
    # generic.  Its type arguments are fixed to the stock Qt classes, which
    # are also what a bare ``FigureCanvasQT`` defaults to.  A backend with
    # its own toolbar, manager or timer is built on the generic
    # ``FigureCanvasQT``, not on this class.
    FigureCanvasAgg[NavigationToolbar2QT, FigureManagerQT, TimerQT],
    FigureCanvasQT[NavigationToolbar2QT, FigureManagerQT, TimerQT],
):
    def paintEvent(self, event: Any) -> None: ...

class _BackendQTAgg(_BackendQT): ...

# Names injected into the module namespace by ``@_Backend.export``.
backend_version: str
FigureCanvas = FigureCanvasQTAgg
FigureManager = FigureManagerQT

def new_figure_manager(
    num: int | str, *args: Any, **kwargs: Any
) -> FigureManagerQT: ...
def new_figure_manager_given_figure(
    num: int | str, figure: Figure
) -> FigureManagerQT: ...
def draw_if_interactive() -> None: ...
def show(*, block: bool | None = ...) -> None: ...

class Show(ShowBase): ...
