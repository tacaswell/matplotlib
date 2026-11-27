from typing import Any

from matplotlib.backend_bases import ShowBase
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_qt import (
    FigureCanvasQT,
    FigureManagerQT as FigureManagerQT,
    NavigationToolbar2QT as NavigationToolbar2QT,
    QtManagerT,
    QtTimerT,
    QtToolbarT,
    _BackendQT,
)

class FigureCanvasQTAgg(
    # Both bases derive from ``FigureCanvasBase``, so they must get the same
    # type arguments or the checkers see two inconsistent specializations of
    # it.  The Qt parameters are passed through, not fixed, so that this class
    # can itself be re-parameterized by a subclass.
    FigureCanvasAgg[QtToolbarT, QtManagerT, QtTimerT],
    FigureCanvasQT[QtToolbarT, QtManagerT, QtTimerT],
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
