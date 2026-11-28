from typing import Any

from matplotlib.backend_bases import ShowBase
from matplotlib.figure import Figure
from matplotlib.backends.backend_cairo import FigureCanvasCairo
from matplotlib.backends.backend_qt import (
    FigureCanvasQT,
    FigureManagerQT,
    NavigationToolbar2QT,
    TimerQT,
    _BackendQT,
)

class FigureCanvasQTCairo(
    # A leaf class: the type arguments are fixed to the stock Qt classes
    # (see ``FigureCanvasQTAgg``).
    FigureCanvasCairo[NavigationToolbar2QT, FigureManagerQT, TimerQT],
    FigureCanvasQT[NavigationToolbar2QT, FigureManagerQT, TimerQT],
):
    def paintEvent(self, event: Any) -> None: ...

class _BackendQTCairo(_BackendQT): ...

# Names injected into the module namespace by ``@_Backend.export``.
backend_version: str
FigureCanvas = FigureCanvasQTCairo
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
