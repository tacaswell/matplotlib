from typing import Any
from typing_extensions import TypeVar

from matplotlib import backend_tools
from matplotlib.backend_bases import ShowBase, ToolContainerBase, _UntypedToolkitWidget
from matplotlib.figure import Figure

from ._backend_gtk import (
    _BackendGTK,
    _FigureCanvasGTK,
    _FigureManagerGTK,
    _NavigationToolbar2GTK,
    TimerGTK,
)

# GTK/GObject objects (Gtk.*, Gdk.*, etc.) have no type stubs → Any.
# GLib and Gtk are imported from gi.repository and re-exported by this module.
GLib: Any
Gtk: Any

# GTK3 uses the same TimerGTK implementation.
TimerGTK3 = TimerGTK

# The GTK widget classes below also inherit their native ``Gtk`` base at
# runtime.  ``gi`` has no type stubs, so ``_UntypedToolkitWidget`` stands in
# for the native base: downstream subclasses see the widget API (as ``Any``)
# exactly as they would from the runtime module.

# Type parameters of the GTK3 canvas, toolbar and manager.  See the comment in
# ``backend_qt.pyi`` for why these classes are generic and how the bounds,
# defaults and per-class variables are chosen.  There is no timer parameter:
# ``_FigureCanvasGTK`` fixes ``TimerGTK`` for every GTK version.
GTK3ToolbarT = TypeVar(
    "GTK3ToolbarT",
    bound="NavigationToolbar2GTK3[Any]",
    default="NavigationToolbar2GTK3[FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]]]",
)
GTK3ManagerT = TypeVar(
    "GTK3ManagerT",
    bound="FigureManagerGTK3[Any, Any]",
    default="FigureManagerGTK3[FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]], NavigationToolbar2GTK3[FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]]]]",
)
# The toolbar's canvas, the manager's canvas and the manager's toolbar.
_GTK3ToolbarCanvasT = TypeVar(
    "_GTK3ToolbarCanvasT",
    bound="FigureCanvasGTK3[Any, Any]",
    default="FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]]",
)
_GTK3ManagerCanvasT = TypeVar(
    "_GTK3ManagerCanvasT",
    bound="FigureCanvasGTK3[Any, Any]",
    default="FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]]",
)
_GTK3ManagerToolbarT = TypeVar(
    "_GTK3ManagerToolbarT",
    bound="NavigationToolbar2GTK3[Any]",
    default="NavigationToolbar2GTK3[FigureCanvasGTK3[NavigationToolbar2GTK3[Any], FigureManagerGTK3[Any, Any]]]",
)

class FigureCanvasGTK3(  # Gtk.DrawingArea
    _FigureCanvasGTK[GTK3ToolbarT, GTK3ManagerT], _UntypedToolkitWidget
):
    # GTK signal-handler methods (new; not base overrides):
    def scroll_event(self, widget: Any, event: Any) -> bool: ...
    def button_press_event(self, widget: Any, event: Any) -> bool: ...
    def button_release_event(self, widget: Any, event: Any) -> bool: ...
    def key_press_event(self, widget: Any, event: Any) -> bool: ...
    def key_release_event(self, widget: Any, event: Any) -> bool: ...
    def motion_notify_event(self, widget: Any, event: Any) -> bool: ...
    def enter_notify_event(self, widget: Any, event: Any) -> bool: ...
    def leave_notify_event(self, widget: Any, event: Any) -> bool: ...
    def size_allocate(self, widget: Any, allocation: Any) -> None: ...
    def configure_event(self, widget: Any, event: Any) -> bool: ...
    def on_draw_event(self, widget: Any, ctx: Any) -> bool: ...

class NavigationToolbar2GTK3(  # Gtk.Toolbar
    _NavigationToolbar2GTK[_GTK3ToolbarCanvasT], _UntypedToolkitWidget
): ...

class ToolbarGTK3(ToolContainerBase, _UntypedToolkitWidget):  # Gtk.Box
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

class SaveFigureGTK3(backend_tools.SaveFigureBase):
    def trigger(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, *args: Any, **kwargs: Any
    ) -> None: ...

class HelpGTK3(backend_tools.ToolHelpBase):
    def trigger(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, *args: Any
    ) -> None: ...

class ToolCopyToClipboardGTK3(backend_tools.ToolCopyToClipboardBase):
    def trigger(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, *args: Any, **kwargs: Any
    ) -> None: ...

class FigureManagerGTK3(_FigureManagerGTK[_GTK3ManagerCanvasT, _GTK3ManagerToolbarT]):
    ...

class _BackendGTK3(_BackendGTK): ...

Toolbar = ToolbarGTK3

# Names injected into the module namespace by ``@_Backend.export``.
backend_version: str
FigureCanvas = FigureCanvasGTK3
FigureManager = FigureManagerGTK3

def new_figure_manager(
    num: int | str, *args: Any, **kwargs: Any
) -> FigureManagerGTK3: ...
def new_figure_manager_given_figure(
    num: int | str, figure: Figure
) -> FigureManagerGTK3: ...
def draw_if_interactive() -> None: ...
def show(*, block: bool | None = ...) -> None: ...

class Show(ShowBase): ...
