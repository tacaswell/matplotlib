from typing import Any
from typing_extensions import TypeVar

from matplotlib import backend_tools
from matplotlib._pylab_helpers import Gcf as Gcf
from matplotlib.backend_bases import (
    _Backend,
    FigureCanvasBase as FigureCanvasBase,
    FigureManagerBase as FigureManagerBase,
    MouseButton as MouseButton,
    NavigationToolbar2 as NavigationToolbar2,
    ShowBase as ShowBase,
    TimerBase as TimerBase,
    ToolContainerBase as ToolContainerBase,
    _UntypedToolkitWidget,
)
from matplotlib.backends.qt_editor import figureoptions as figureoptions
from matplotlib.figure import Figure

# Qt is resolved dynamically and has no stubs, so Qt objects are typed as Any.
SPECIAL_KEYS: dict[Any, str]
cursord: dict[Any, Any]

def _create_qApp() -> Any: ...

# The Qt classes below also inherit their native Qt widget class at runtime
# (``QtWidgets.QWidget``, ``QToolBar``, ...).  The Qt binding is chosen at
# runtime and has no type stubs, so ``_UntypedToolkitWidget`` stands in for
# the native base: downstream subclasses see the widget API (as ``Any``)
# exactly as they would from the runtime module, while the Matplotlib-owned
# members stay precisely typed.

class TimerQT(TimerBase): ...

# The Qt canvas, toolbar and manager are generic over each other in the same
# way as their ``backend_bases`` parents.  This is what lets a downstream
# backend that layers a mixin on top of the Qt classes, e.g. ::
#
#     class MyCanvas(MyCanvasMixin[MyToolbar, MyManager, TimerQT],
#                    FigureCanvasQT[MyToolbar, MyManager, TimerQT]): ...
#
# give both paths to the shared ``FigureCanvasBase`` the *same* type
# arguments.  With the arguments fixed here instead, the two paths disagree:
# pyright rejects the class ("base classes are mutually incompatible") and
# the subclass has to redeclare ``toolbar`` / ``canvas``, which pyright also
# rejects because the attributes are mutable.
#
# * Bounds keep the parameters inside the Qt family: these classes call Qt
#   widget methods on each other.
# * Defaults are the stock Qt classes, so a bare ``FigureCanvasQT``,
#   ``NavigationToolbar2QT`` or ``FigureManagerQT`` is the stock backend.
#   They spell out one level of the stock classes because a default cannot
#   name its own, still unparameterized, class.
# * Each class has its own type variables.  Sharing one between two of these
#   mutually-referencing classes makes pyright mis-resolve them: depending on
#   which class a module touches first, it reports the others as taking
#   fewer type arguments than declared.
#
# The other GUI toolkits (Tk, GTK3, GTK4, wx, macOS) follow the same scheme.
QtToolbarT = TypeVar(
    "QtToolbarT",
    bound="NavigationToolbar2QT[Any]",
    default="NavigationToolbar2QT[FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT]]",
)
QtManagerT = TypeVar(
    "QtManagerT",
    bound="FigureManagerQT[Any, Any]",
    default="FigureManagerQT[FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT], NavigationToolbar2QT[FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT]]]",
)
QtTimerT = TypeVar("QtTimerT", bound=TimerQT, default=TimerQT)
# The toolbar's canvas, the manager's canvas and the manager's toolbar.
_QtToolbarCanvasT = TypeVar(
    "_QtToolbarCanvasT",
    bound="FigureCanvasQT[Any, Any, Any]",
    default="FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT]",
)
_QtManagerCanvasT = TypeVar(
    "_QtManagerCanvasT",
    bound="FigureCanvasQT[Any, Any, Any]",
    default="FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT]",
)
_QtManagerToolbarT = TypeVar(
    "_QtManagerToolbarT",
    bound="NavigationToolbar2QT[Any]",
    default="NavigationToolbar2QT[FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT]]",
)

class FigureCanvasQT(  # QtWidgets.QWidget
    FigureCanvasBase[QtToolbarT, QtManagerT, QtTimerT],
    _UntypedToolkitWidget,
):
    buttond: dict[Any, MouseButton]
    def set_cursor(self, cursor: Any) -> None: ...
    def mouseEventCoords(self, pos: Any = ...) -> tuple[float, float]: ...
    def enterEvent(self, event: Any) -> None: ...
    def leaveEvent(self, event: Any) -> None: ...
    def mousePressEvent(self, event: Any) -> None: ...
    def mouseDoubleClickEvent(self, event: Any) -> None: ...
    def mouseMoveEvent(self, event: Any) -> None: ...
    def mouseReleaseEvent(self, event: Any) -> None: ...
    def wheelEvent(self, event: Any) -> None: ...
    def keyPressEvent(self, event: Any) -> None: ...
    def keyReleaseEvent(self, event: Any) -> None: ...
    def resizeEvent(self, event: Any) -> None: ...
    def sizeHint(self) -> Any: ...
    def minimumSizeHint(self) -> Any: ...
    def stop_event_loop(self, event: Any = ...) -> None: ...
    def drawRectangle(self, rect: Any) -> None: ...

class MainWindow(_UntypedToolkitWidget): ...  # QtWidgets.QMainWindow

class FigureManagerQT(FigureManagerBase[_QtManagerCanvasT, _QtManagerToolbarT]):
    window: Any
    def __init__(self, canvas: _QtManagerCanvasT, num: int | str) -> None: ...
    # Runtime names the parameters ``width, height`` while the base uses
    # ``w, h``; the base only ever calls this positionally.
    def resize(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, width: int, height: int
    ) -> None: ...
    def destroy(self, *args: Any) -> None: ...

class NavigationToolbar2QT(
    NavigationToolbar2[_QtToolbarCanvasT], _UntypedToolkitWidget
):  # QtWidgets.QToolBar
    coordinates: bool
    locLabel: Any
    # Backend-authoring API: toolitem method name -> QAction, used by
    # subclasses to enable/disable or restyle the standard buttons.
    _actions: dict[str, Any]
    def __init__(
        self,
        canvas: _QtToolbarCanvasT,
        parent: Any = ...,
        coordinates: bool = ...,
    ) -> None: ...
    def edit_parameters(self) -> None: ...
    # Returns the Qt dialog rather than a ``SubplotTool``.
    def configure_subplots(self) -> Any: ...  # pyright: ignore[reportIncompatibleMethodOverride]

class SubplotToolQt(_UntypedToolkitWidget):  # QtWidgets.QDialog
    def __init__(self, targetfig: Figure, parent: Any) -> None: ...
    def update_from_current_subplotpars(self) -> None: ...

class ToolbarQt(ToolContainerBase, _UntypedToolkitWidget):  # QtWidgets.QToolBar
    def __init__(self, toolmanager: Any, parent: Any = ...) -> None: ...
    # Runtime names the fourth parameter ``image_file`` while the base uses
    # ``image``; the base only ever calls this positionally.
    def add_toolitem(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        name: str,
        group: str,
        position: int,
        image_file: str,
        description: str,
        toggle: bool,
    ) -> None: ...

class ConfigureSubplotsQt(backend_tools.ConfigureSubplotsBase): ...
class SaveFigureQt(backend_tools.SaveFigureBase): ...
class RubberbandQt(backend_tools.RubberbandBase): ...
class HelpQt(backend_tools.ToolHelpBase): ...
class ToolCopyToClipboardQT(backend_tools.ToolCopyToClipboardBase): ...
class _BackendQT(_Backend[type[FigureCanvasQT]]): ...

# Names injected into the module namespace by ``@_Backend.export``.
backend_version: str
FigureCanvas = FigureCanvasQT
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
