from typing import Any
from typing_extensions import TypeVar

from matplotlib.backend_bases import (
    _Backend,
    Event,
    FigureManagerBase,
    NavigationToolbar2,
    ShowBase,
    TimerBase,
)
from matplotlib.figure import Figure
from matplotlib.transforms import BboxBase
from matplotlib.backends._macosx import (
    FigureCanvas as _FigureCanvasMacOSX,
    FigureManager as _FigureManagerMacOSX,
    NavigationToolbar2 as _NavigationToolbar2MacOSX,
    Timer as _TimerMacOSX,
)
from matplotlib.backends.backend_agg import FigureCanvasAgg

class TimerMac(_TimerMacOSX, TimerBase): ...

# Type parameters of the Mac canvas, toolbar and manager.  See the comment in
# ``backend_qt.pyi`` for why these classes are generic and how the bounds,
# defaults and per-class variables are chosen.
MacToolbarT = TypeVar(
    "MacToolbarT",
    bound="NavigationToolbar2Mac[Any]",
    default="NavigationToolbar2Mac[FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac]]",
)
MacManagerT = TypeVar(
    "MacManagerT",
    bound="FigureManagerMac[Any, Any]",
    default="FigureManagerMac[FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac], NavigationToolbar2Mac[FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac]]]",
)
MacTimerT = TypeVar("MacTimerT", bound=TimerMac, default=TimerMac)
# The toolbar's canvas, the manager's canvas and the manager's toolbar.
_MacToolbarCanvasT = TypeVar(
    "_MacToolbarCanvasT",
    bound="FigureCanvasMac[Any, Any, Any]",
    default="FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac]",
)
_MacManagerCanvasT = TypeVar(
    "_MacManagerCanvasT",
    bound="FigureCanvasMac[Any, Any, Any]",
    default="FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac]",
)
_MacManagerToolbarT = TypeVar(
    "_MacManagerToolbarT",
    bound="NavigationToolbar2Mac[Any]",
    default="NavigationToolbar2Mac[FigureCanvasMac[NavigationToolbar2Mac[Any], FigureManagerMac[Any, Any], TimerMac]]",
)

class FigureCanvasMac(
    FigureCanvasAgg[MacToolbarT, MacManagerT, MacTimerT],
    _FigureCanvasMacOSX,
):
    required_interactive_framework: str
    def blit(self, bbox: BboxBase | None = ...) -> None: ...
    def resize(self, width: float, height: float) -> None: ...

class NavigationToolbar2Mac(
    _NavigationToolbar2MacOSX, NavigationToolbar2[_MacToolbarCanvasT]
):
    def draw_rubberband(
        self, event: Event, x0: float, y0: float, x1: float, y1: float
    ) -> None: ...
    def remove_rubberband(self) -> None: ...
    def save_figure(self, *args: object) -> str | None: ...

class FigureManagerMac(
    _FigureManagerMacOSX, FigureManagerBase[_MacManagerCanvasT, _MacManagerToolbarT]
):
    def destroy(self) -> None: ...
    @classmethod
    def start_main_loop(cls) -> None: ...
    def show(self) -> None: ...

class _BackendMac(_Backend[type[FigureCanvasMac]]): ...

# Names injected into the module namespace by ``@_Backend.export``.
backend_version: str
FigureCanvas = FigureCanvasMac
FigureManager = FigureManagerMac

def new_figure_manager(
    num: int | str, *args: Any, **kwargs: Any
) -> FigureManagerMac: ...
def new_figure_manager_given_figure(
    num: int | str, figure: Figure
) -> FigureManagerMac: ...
def draw_if_interactive() -> None: ...
def show(*, block: bool | None = ...) -> None: ...

class Show(ShowBase): ...
