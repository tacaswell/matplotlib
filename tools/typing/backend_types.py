"""
Static checks for the backend typing model.

The ``_check_*`` helpers in this module are analyzed by mypy and Pyright
but never executed.  Runtime tests and shared backend fixtures live in
``lib/matplotlib/tests/test_backend_types.py``.
They exercise the generic cross-references between ``FigureCanvasBase``,
``NavigationToolbar2``, ``FigureManagerBase``, and ``RendererBase`` from the
point of view of

* ordinary downstream code that passes concrete backend objects through the
  general-purpose Matplotlib API, and
* a third-party backend author who subclasses the base classes (including the
  "mixin + toolkit" diamond pattern).

The simulated third-party backend is modelled on a real thin-client backend:
its classes have method bodies that use each other through ``self.canvas`` /
``self.toolbar`` / ``self.manager``, because that is where a backend author
meets the typing model.  Empty class bodies only check the class statements.

The simulated backend carries no ``# type: ignore`` and no
``# pyright: ignore``, and redeclares no attribute: everything a backend
author needs is expressed by specializing the generic classes.  The only
suppressions in this module mark the *negative* checks.

Negative checks use ``# type: ignore[<code>]`` together with the
``warn_unused_ignores`` override for this module in ``pyproject.toml``: if a
declaration ever stops rejecting an invalid call, the now-unused ignore is
reported as an error.
"""

from __future__ import annotations

import io
import tkinter as tk
from typing import TYPE_CHECKING, Any, assert_type

from matplotlib.artist import Artist
from matplotlib.backend_bases import (
    CloseEvent,
    DrawEvent,
    Event,
    FigureCanvasBase,
    FigureManagerBase,
    GraphicsContextBase,
    KeyEvent,
    LocationEvent,
    MouseEvent,
    NavigationToolbar2,
    PickEvent,
    ResizeEvent,
    RendererBase,
    TimerBase,
    ToolContainerBase,
    button_press_handler,
    get_registered_canvas_class,
    key_press_handler,
    register_backend,
    scroll_handler,
)
from matplotlib.backend_managers import ToolManager
from matplotlib.backend_tools import (
    ToolBase,
    _find_tool_class,
    _register_tool_class,
    _tool_registry,
)
from matplotlib.backends._backend_agg import BufferRegion
from matplotlib.backends.backend_agg import FigureCanvasAgg, RendererAgg
from matplotlib.backends.backend_mixed import MixedModeRenderer
from matplotlib.backends.backend_pdf import (
    FigureCanvasPdf,
    RendererPdf,
)
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.backends.backend_template import (
    FigureCanvasTemplate,
    FigureManagerTemplate,
)
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure, SubFigure
from matplotlib.gridspec import GridSpec
from matplotlib.image import AxesImage, composite_images
from matplotlib.inset import InsetIndicator
from matplotlib.lines import VertexSelector
from matplotlib.offsetbox import DraggableBase, OffsetBox
from matplotlib.patches import bbox_artist, draw_bbox
from matplotlib.patheffects import PathEffectRenderer
from matplotlib.table import Cell
from matplotlib.texmanager import TexManager
from matplotlib.text import Annotation, OffsetFrom
from matplotlib.tests.test_backend_types import (
    FigureCanvasRemote,
    FigureManagerRemote,
    NavigationToolbar2Remote,
    RemoteCanvasMixin,
    RemoteRenderer,
    RemoteTimer,
    RemoteToolbarMixin,
    SpecializedFigureCanvasAgg,
    SpecializedFigureManager,
    SpecializedTimer,
    SpecializedTool,
)
from matplotlib.transforms import Bbox
from matplotlib.widgets import AxesWidget

if TYPE_CHECKING:
    # GUI backends need optional native dependencies; only their stubs are
    # exercised here, so import them for the type checker alone.
    from matplotlib.backends._backend_tk import (
        FigureCanvasTk,
        FigureManagerTk,
        NavigationToolbar2Tk,
        TimerTk,
    )
    from matplotlib.backends._backend_gtk import TimerGTK
    from matplotlib.backends.backend_cairo import FigureCanvasCairo, RendererCairo
    from matplotlib.backends.backend_gtk3 import (
        FigureCanvasGTK3,
        FigureManagerGTK3,
        NavigationToolbar2GTK3,
    )
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
    from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo
    from matplotlib.backends.backend_gtk4 import (
        FigureCanvasGTK4,
        FigureManagerGTK4,
        NavigationToolbar2GTK4,
    )
    from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg
    from matplotlib.backends.backend_gtk4cairo import FigureCanvasGTK4Cairo
    from matplotlib.backends.backend_macosx import (
        FigureCanvasMac,
        FigureManagerMac,
        NavigationToolbar2Mac,
        TimerMac,
    )
    from matplotlib.backends.backend_nbagg import (
        FigureCanvasNbAgg,
        FigureManagerNbAgg,
        NavigationIPy,
    )
    from matplotlib.backends.backend_qt import (
        FigureCanvasQT,
        FigureManagerQT,
        MainWindow,
        NavigationToolbar2QT,
        TimerQT,
    )
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qtcairo import FigureCanvasQTCairo
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.backends.backend_tkcairo import FigureCanvasTkCairo
    from matplotlib.backends.backend_webagg import (
        FigureCanvasWebAgg,
        FigureManagerWebAgg as FigureManagerWebAggApplication,
    )
    from matplotlib.backends.backend_webagg_core import (
        FigureCanvasWebAggCore,
        FigureManagerWebAgg as FigureManagerWebAggCore,
        NavigationToolbar2WebAgg,
        TimerAsyncio,
    )
    from matplotlib.backends.backend_wx import (
        FigureCanvasWx,
        FigureManagerWx,
        NavigationToolbar2Wx,
        TimerWx,
        _FigureCanvasWxBase,
    )
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
    from matplotlib.backends.backend_wxcairo import FigureCanvasWxCairo


if TYPE_CHECKING:
    # Diamond: remote mixin first, stock toolkit class second.  A thin client
    # has no local renderer, so it pairs with the bare toolkit canvas
    # (``FigureCanvasQT``, not ``FigureCanvasQTAgg``).
    #
    # Both bases of each class derive from the same ``backend_bases`` class,
    # so they are given the *same* type arguments.  That is all it takes: the
    # shared base is specialized consistently, and ``self.toolbar`` /
    # ``self.canvas`` have the concrete downstream type on the mixin side and
    # on the toolkit side alike.  Nothing is redeclared and nothing is
    # suppressed.

    # --- Qt ----------------------------------------------------------------
    # The window manager of this thin client is a plain class (below), not a
    # ``FigureManagerBase``, so the canvas' manager parameter is specialized
    # with the stock Qt manager: ``canvas.manager`` is simply never set.

    class FigureCanvasQTRemote(
        RemoteCanvasMixin[
            "NavigationToolbar2QTRemote", FigureManagerQT[Any, Any], TimerQT
        ],
        FigureCanvasQT[
            "NavigationToolbar2QTRemote", FigureManagerQT[Any, Any], TimerQT
        ],
    ):
        def resizeEvent(self, event: Any) -> None:
            # Toolkit members and remote-mixin members on the same object.
            width = event.size().width() * self.devicePixelRatioF()
            self.send({"type": "resize", "width": width})
            if self.toolbar is not None:
                self.toolbar.locLabel.setText("resizing")
                self.toolbar._on_navigate_mode("")

    class NavigationToolbar2QTRemote(
        RemoteToolbarMixin[FigureCanvasQTRemote],
        NavigationToolbar2QT[FigureCanvasQTRemote],
    ):
        def draw_rubberband(
            self, event: Event, x0: float, y0: float, x1: float, y1: float
        ) -> None:
            # Qt-only canvas members reached through ``self.canvas``.
            height = self.canvas.height() * self.canvas.devicePixelRatioF()
            self.canvas.drawRectangle([x0, height - y0, x1 - x0, y0 - y1])

        def remove_rubberband(self) -> None:
            self.canvas.drawRectangle(None)
            self.canvas.send({"type": "rubberband", "visible": False})

        def _on_navigate_mode(self, mode: str) -> None:
            super()._on_navigate_mode(mode)
            self._actions["pan"].setChecked(mode == "PAN")

    # The window managers of a thin client are *not* ``FigureManagerBase``
    # subclasses.  ``FigureManagerBase.__init__`` connects the default key,
    # button and scroll handlers to the canvas, and a thin client forwards
    # those events to a server that applies the bindings itself; a local copy
    # would act on each navigation key a second time.  The managers below
    # only have the *methods* of a figure manager.
    class FigureManagerQTRemote:
        def __init__(self, canvas: FigureCanvasQTRemote, num: int | str) -> None:
            self.canvas = canvas
            self.window = MainWindow()
            self.toolbar = NavigationToolbar2QTRemote(canvas, self.window)

        def show(self) -> None:
            self.window.show()

        def resize(self, width: int, height: int) -> None:
            ratio = self.canvas.devicePixelRatioF()
            self.canvas.send({"type": "resize", "width": width / ratio})
            self.window.resize(int(width / ratio), int(height / ratio))

        def destroy(self) -> None:
            self.toolbar.destroy()
            self.toolbar.home()
            self.window.close()

    # --- Tk (whose toolbar ``message`` is a ``tk.StringVar`` at runtime) ----

    class FigureCanvasTkRemote(
        RemoteCanvasMixin[
            "NavigationToolbar2TkRemote", FigureManagerTk[Any, Any], TimerTk
        ],
        FigureCanvasTk[
            "NavigationToolbar2TkRemote", FigureManagerTk[Any, Any], TimerTk
        ],
    ):
        def __init__(self, figure: Figure, master: tk.Misc) -> None:
            super().__init__(figure, master=master)
            self._tkcanvas.bind("<Configure>", lambda event: None)

    class NavigationToolbar2TkRemote(
        RemoteToolbarMixin[FigureCanvasTkRemote],
        NavigationToolbar2Tk[FigureCanvasTkRemote],
    ):
        def draw_rubberband(
            self, event: Event, x0: float, y0: float, x1: float, y1: float
        ) -> None:
            # Tk-only canvas members reached through ``self.canvas``.
            height = self.canvas._tkcanvas.winfo_height()
            self.canvas._tkcanvas.create_rectangle(x0, height - y0, x1, height - y1)

        def set_message(self, s: str) -> None:
            # ``NavigationToolbar2Tk.message`` is a ``tk.StringVar``.
            self.message.set(s)

    class FigureManagerTkRemote:
        def __init__(
            self, canvas: FigureCanvasTkRemote, num: int | str, window: tk.Tk
        ) -> None:
            self.canvas = canvas
            self.window = window
            self.toolbar = NavigationToolbar2TkRemote(canvas, window)

        def show(self) -> None:
            self.window.deiconify()

        def resize(self, width: int, height: int) -> None:
            extra = self.window.winfo_width() - self.canvas._tkcanvas.winfo_width()
            self.canvas.send({"type": "resize", "width": width})
            self.window.geometry(f"{width + extra}x{height}")

        def destroy(self) -> None:
            self.window.destroy()

    # --- GTK3, GTK4, wx, macOS ---------------------------------------------
    # The same diamond on every other GUI toolkit, here with a manager that
    # *does* derive from the toolkit's manager: a specialization of the
    # generic toolkit manager, again with nothing redeclared.  (GTK has no
    # timer parameter: every GTK version uses ``TimerGTK``.)

    class FigureCanvasGTK3Remote(
        RemoteCanvasMixin[
            "NavigationToolbar2GTK3Remote", "FigureManagerGTK3Remote", TimerGTK
        ],
        FigureCanvasGTK3["NavigationToolbar2GTK3Remote", "FigureManagerGTK3Remote"],
    ):
        pass

    class NavigationToolbar2GTK3Remote(
        RemoteToolbarMixin[FigureCanvasGTK3Remote],
        NavigationToolbar2GTK3[FigureCanvasGTK3Remote],
    ):
        pass

    class FigureManagerGTK3Remote(
        FigureManagerGTK3[FigureCanvasGTK3Remote, NavigationToolbar2GTK3Remote]
    ):
        def announce(self) -> None:
            self.canvas.send({"type": "title"})
            self.canvas.queue_draw()
            if isinstance(self.toolbar, NavigationToolbar2GTK3Remote):
                self.toolbar.home()

    class FigureCanvasGTK4Remote(
        RemoteCanvasMixin[
            "NavigationToolbar2GTK4Remote", "FigureManagerGTK4Remote", TimerGTK
        ],
        FigureCanvasGTK4["NavigationToolbar2GTK4Remote", "FigureManagerGTK4Remote"],
    ):
        pass

    class NavigationToolbar2GTK4Remote(
        RemoteToolbarMixin[FigureCanvasGTK4Remote],
        NavigationToolbar2GTK4[FigureCanvasGTK4Remote],
    ):
        pass

    class FigureManagerGTK4Remote(
        FigureManagerGTK4[FigureCanvasGTK4Remote, NavigationToolbar2GTK4Remote]
    ):
        pass

    class FigureCanvasWxRemote(
        RemoteCanvasMixin[
            "NavigationToolbar2WxRemote", "FigureManagerWxRemote", TimerWx
        ],
        FigureCanvasWx["NavigationToolbar2WxRemote", "FigureManagerWxRemote", TimerWx],
    ):
        pass

    class NavigationToolbar2WxRemote(
        RemoteToolbarMixin[FigureCanvasWxRemote],
        NavigationToolbar2Wx[FigureCanvasWxRemote],
    ):
        pass

    class FigureManagerWxRemote(
        FigureManagerWx[FigureCanvasWxRemote, NavigationToolbar2WxRemote]
    ):
        pass

    class FigureCanvasMacRemote(
        RemoteCanvasMixin[
            "NavigationToolbar2MacRemote", "FigureManagerMacRemote", TimerMac
        ],
        FigureCanvasMac[
            "NavigationToolbar2MacRemote", "FigureManagerMacRemote", TimerMac
        ],
    ):
        pass

    class NavigationToolbar2MacRemote(
        RemoteToolbarMixin[FigureCanvasMacRemote],
        NavigationToolbar2Mac[FigureCanvasMacRemote],
    ):
        pass

    class FigureManagerMacRemote(
        FigureManagerMac[FigureCanvasMacRemote, NavigationToolbar2MacRemote]
    ):
        pass

    # Narrowing a stock toolkit backend further.
    class MyQtCanvas(FigureCanvasQTAgg):
        def _check(self) -> None:  # pragma: no cover
            assert_type(self.manager, FigureManagerQT | None)
            assert_type(self.toolbar, NavigationToolbar2QT | None)
            assert_type(self.new_timer(), TimerQT)
            assert_type(type(self).manager_class, type[FigureManagerQT])
            region = self.copy_from_bbox(self.figure.bbox)
            assert_type(region, BufferRegion)
            self.restore_region(region)
            self.renderer.clear()
            assert_type(self._lastKey, tuple[float, float, float] | None)


# ---------------------------------------------------------------------------
# Static checks (analyzed by mypy and Pyright, never called).
# ---------------------------------------------------------------------------


def _check_remote_backend_types(  # pragma: no cover
    canvas: FigureCanvasRemote,
    toolbar: NavigationToolbar2Remote,
    manager: FigureManagerRemote,
    figure: Figure,
) -> None:
    # Every cross-reference of the specialized classes is the concrete type.
    assert_type(canvas.toolbar, NavigationToolbar2Remote | None)
    assert_type(canvas.manager, FigureManagerRemote | None)
    assert_type(canvas.new_timer(), RemoteTimer)
    assert_type(FigureCanvasRemote.manager_class, type[FigureManagerRemote])
    assert_type(FigureCanvasRemote.new_manager(figure, 1), FigureManagerRemote)

    assert_type(toolbar.canvas, FigureCanvasRemote)
    assert_type(toolbar.canvas.toolbar, NavigationToolbar2Remote | None)
    assert_type(toolbar.canvas.manager, FigureManagerRemote | None)

    assert_type(manager.canvas, FigureCanvasRemote)
    assert_type(
        manager.toolbar, NavigationToolbar2Remote | ToolContainerBase | None
    )
    # Assigned (not annotated) in the class body; mypy infers the narrowed
    # declared type from the assignment, pyright keeps the inherited one.
    assert manager._toolbar2_class is NavigationToolbar2Remote
    assert_type(
        FigureManagerRemote.create_with_canvas(FigureCanvasRemote, figure, 1),
        FigureManagerRemote,
    )

    # Concrete backend objects are accepted wherever the general API takes a
    # bare base type.
    figure.set_canvas(canvas)
    Artist().draw(RemoteRenderer())
    Event("x", canvas)
    key_press_handler(KeyEvent("key_press_event", canvas, "x"), canvas, toolbar)


def _check_remote_diamond_types(  # pragma: no cover
    qt_canvas: FigureCanvasQTRemote,
    qt_toolbar: NavigationToolbar2QTRemote,
    qt_manager: FigureManagerQTRemote,
    tk_canvas: FigureCanvasTkRemote,
    tk_toolbar: NavigationToolbar2TkRemote,
    tk_manager: FigureManagerTkRemote,
) -> None:
    # Both bases of each diamond were given the same type arguments, so every
    # cross-reference has the concrete downstream type ...
    assert_type(qt_canvas.toolbar, NavigationToolbar2QTRemote | None)
    assert_type(qt_canvas.new_timer(), TimerQT)
    assert_type(qt_toolbar.canvas, FigureCanvasQTRemote)
    assert_type(qt_manager.canvas, FigureCanvasQTRemote)
    assert_type(qt_manager.toolbar, NavigationToolbar2QTRemote)
    assert_type(tk_canvas.toolbar, NavigationToolbar2TkRemote | None)
    assert_type(tk_canvas.new_timer(), TimerTk)
    assert_type(tk_toolbar.canvas, FigureCanvasTkRemote)
    assert_type(tk_manager.canvas, FigureCanvasTkRemote)
    assert_type(tk_manager.toolbar, NavigationToolbar2TkRemote)
    # ... so both the toolkit API and the remote API are usable through them.
    qt_toolbar.canvas.drawRectangle(None)
    qt_toolbar.canvas.send({"type": "refresh"})
    qt_manager.toolbar.home()
    tk_toolbar.canvas._tkcanvas.delete("all")
    tk_manager.canvas.send({"type": "refresh"})
    # The manager parameter was specialized with the stock toolkit manager.
    assert_type(qt_canvas.manager, FigureManagerQT[Any, Any] | None)
    assert_type(tk_canvas.manager, FigureManagerTk[Any, Any] | None)
    assert_type(FigureCanvasQTRemote.manager_class, type[FigureManagerQT[Any, Any]])
    # The duck-typed window managers are not figure managers to the type
    # system, so they cannot be stored as ``canvas.manager`` ...
    qt_canvas.manager = qt_manager  # type: ignore[assignment]
    tk_canvas.manager = tk_manager  # type: ignore[assignment]
    # ... and need no ``toolbar`` narrowing: a plain attribute has exactly
    # the declared type, with no toolmanager container or ``None`` in it.
    qt_manager.toolbar.locLabel.setText("ready")
    tk_manager.toolbar.message.set("ready")
    # Toolkit-specific members remain available through the second base.
    qt_canvas.mouseEventCoords()
    tk_canvas.get_tk_widget()
    # ``NavigationToolbar2Tk.message`` is a ``tk.StringVar`` at runtime.
    tk_toolbar.message.set("x")


def _check_remote_diamond_all_toolkits(  # pragma: no cover
    gtk3_canvas: FigureCanvasGTK3Remote,
    gtk3_toolbar: NavigationToolbar2GTK3Remote,
    gtk3_manager: FigureManagerGTK3Remote,
    gtk4_canvas: FigureCanvasGTK4Remote,
    gtk4_toolbar: NavigationToolbar2GTK4Remote,
    gtk4_manager: FigureManagerGTK4Remote,
    wx_canvas: FigureCanvasWxRemote,
    wx_toolbar: NavigationToolbar2WxRemote,
    wx_manager: FigureManagerWxRemote,
    mac_canvas: FigureCanvasMacRemote,
    mac_toolbar: NavigationToolbar2MacRemote,
    mac_manager: FigureManagerMacRemote,
) -> None:
    # The same diamond on every GUI toolkit, with a manager derived from the
    # toolkit's manager: all three classes see each other's concrete type.
    assert_type(gtk3_canvas.toolbar, NavigationToolbar2GTK3Remote | None)
    assert_type(gtk3_canvas.manager, FigureManagerGTK3Remote | None)
    assert_type(gtk3_canvas.new_timer(), TimerGTK)
    assert_type(gtk3_toolbar.canvas, FigureCanvasGTK3Remote)
    assert_type(gtk3_manager.canvas, FigureCanvasGTK3Remote)
    assert_type(
        gtk3_manager.toolbar,
        NavigationToolbar2GTK3Remote | ToolContainerBase | None,
    )

    assert_type(gtk4_canvas.toolbar, NavigationToolbar2GTK4Remote | None)
    assert_type(gtk4_canvas.manager, FigureManagerGTK4Remote | None)
    assert_type(gtk4_canvas.new_timer(), TimerGTK)
    assert_type(gtk4_toolbar.canvas, FigureCanvasGTK4Remote)
    assert_type(gtk4_manager.canvas, FigureCanvasGTK4Remote)

    assert_type(wx_canvas.toolbar, NavigationToolbar2WxRemote | None)
    assert_type(wx_canvas.manager, FigureManagerWxRemote | None)
    assert_type(wx_canvas.new_timer(), TimerWx)
    assert_type(wx_toolbar.canvas, FigureCanvasWxRemote)
    assert_type(wx_manager.canvas, FigureCanvasWxRemote)

    assert_type(mac_canvas.toolbar, NavigationToolbar2MacRemote | None)
    assert_type(mac_canvas.manager, FigureManagerMacRemote | None)
    assert_type(mac_canvas.new_timer(), TimerMac)
    assert_type(mac_toolbar.canvas, FigureCanvasMacRemote)
    assert_type(mac_manager.canvas, FigureCanvasMacRemote)

    # Remote-mixin API and toolkit API through the cross-references.
    for remote_canvas in (gtk3_toolbar.canvas, gtk4_toolbar.canvas,
                          wx_manager.canvas, mac_manager.canvas):
        remote_canvas.send({"type": "refresh"})
    gtk3_toolbar.canvas.queue_draw()
    wx_toolbar.canvas.Refresh()
    if gtk4_canvas.toolbar is not None:
        gtk4_canvas.toolbar._on_navigate_mode("PAN")


def _check_explicit_any_specialization(  # pragma: no cover
    any_canvas: RemoteCanvasMixin[Any, Any, Any],
    any_toolbar: RemoteToolbarMixin[Any],
    standalone: FigureCanvasRemote,
    qt_canvas: FigureCanvasQTRemote,
    qt_toolbar: NavigationToolbar2QTRemote,
    tk_canvas: FigureCanvasTkRemote,
    gtk3_canvas: FigureCanvasGTK3Remote,
    wx_canvas: FigureCanvasWxRemote,
    mac_canvas: FigureCanvasMacRemote,
) -> None:
    # Code that works with *any* remote canvas says so by naming the type
    # arguments: ``[Any, Any, Any]`` accepts every specialization.
    def forward(canvas: RemoteCanvasMixin[Any, Any, Any]) -> None:
        canvas.send({"type": "refresh"})

    def hook(toolbar: RemoteToolbarMixin[Any]) -> None:
        toolbar._on_navigate_mode("")

    for canvas in (standalone, qt_canvas, tk_canvas, gtk3_canvas, wx_canvas,
                   mac_canvas):
        forward(canvas)
    hook(qt_toolbar)
    forward(any_canvas)
    hook(any_toolbar)
    # The mixin's own API stays available on an ``Any`` specialization.
    any_canvas.send({"type": "refresh"})
    any_toolbar.home()
    # The same holds for the Matplotlib classes: a concrete backend is
    # accepted where the parameters are spelled out as ``Any``.
    def stock_canvas(canvas: FigureCanvasQT[Any, Any, Any]) -> None: ...
    def base_canvas(canvas: FigureCanvasBase[Any, Any, Any]) -> None: ...

    stock_canvas(qt_canvas)
    base_canvas(qt_canvas)
    base_canvas(standalone)


def _check_manager_type_propagation(  # pragma: no cover
    canvas_type: type[
        FigureCanvasBase[
            NavigationToolbar2[Any], SpecializedFigureManager, SpecializedTimer
        ]
    ],
    figure: Figure,
) -> None:
    assert_type(canvas_type.manager_class, type[SpecializedFigureManager])
    assert_type(canvas_type.new_manager(figure, 1), SpecializedFigureManager)


def _check_bare_generic_defaults(  # pragma: no cover
    canvas: FigureCanvasBase,
    manager: FigureManagerBase,
    toolbar: NavigationToolbar2[Any],
    renderer: RendererBase,
    agg: FigureCanvasAgg,
    remote_manager: FigureManagerBase[FigureCanvasRemote, NavigationToolbar2Remote],
) -> None:
    assert_type(
        remote_manager._toolbar2_class, type[NavigationToolbar2Remote] | None
    )
    # Bare base types degrade to ``Any`` specializations, not to the base
    # class itself, so they accept every concrete backend.
    assert_type(canvas.manager, FigureManagerBase[Any, Any] | None)
    assert_type(canvas.toolbar, NavigationToolbar2[Any] | None)
    assert_type(canvas.new_timer(), TimerBase)
    assert_type(manager.toolbar, NavigationToolbar2[Any] | ToolContainerBase | None)
    assert_type(renderer.new_gc(), GraphicsContextBase)
    assert_type(agg.manager, FigureManagerBase[Any, Any] | None)


def _check_non_gui_canvas_types(  # pragma: no cover
    pdf: FigureCanvasPdf,
    svg: FigureCanvasSVG,
    template: FigureCanvasTemplate,
    figure: Figure,
) -> None:
    assert_type(pdf.manager, FigureManagerBase[Any, Any] | None)
    assert_type(svg.manager, FigureManagerBase[Any, Any] | None)
    assert_type(template.manager, FigureManagerTemplate | None)
    assert_type(FigureCanvasTemplate.manager_class, type[FigureManagerTemplate])
    assert_type(FigureCanvasTemplate.new_manager(figure, 1), FigureManagerTemplate)


def _check_gui_canvas_types(  # pragma: no cover
    qt: FigureCanvasQT,
    qtagg: FigureCanvasQTAgg,
    qtcairo: FigureCanvasQTCairo,
    tk: FigureCanvasTk,
    tkagg: FigureCanvasTkAgg,
    tkcairo: FigureCanvasTkCairo,
    gtk3: FigureCanvasGTK3,
    gtk3agg: FigureCanvasGTK3Agg,
    gtk3cairo: FigureCanvasGTK3Cairo,
    gtk4: FigureCanvasGTK4,
    gtk4agg: FigureCanvasGTK4Agg,
    gtk4cairo: FigureCanvasGTK4Cairo,
    wx: _FigureCanvasWxBase,
    wxagg: FigureCanvasWxAgg,
    wxcairo: FigureCanvasWxCairo,
    figure: Figure,
    qtagg_type: type[FigureCanvasQTAgg],
    qtcairo_type: type[FigureCanvasQTCairo],
    tkagg_type: type[FigureCanvasTkAgg],
    gtk3agg_type: type[FigureCanvasGTK3Agg],
    gtk4cairo_type: type[FigureCanvasGTK4Cairo],
    wxagg_type: type[FigureCanvasWxAgg],
) -> None:
    # Every combined "rendering + toolkit" canvas must retain the toolkit's
    # concrete manager, toolbar, and timer types even though the rendering
    # canvas comes first in the MRO.
    for qt_canvas in (qt, qtagg, qtcairo):
        assert_type(qt_canvas.manager, FigureManagerQT | None)
        assert_type(qt_canvas.toolbar, NavigationToolbar2QT | None)
        assert_type(qt_canvas.new_timer(), TimerQT)
        # The stock classes are generic too, with the stock classes as their
        # defaults.  One hop along a cross-reference the default is written
        # out, so the type is the stock canvas specialized with ``Any``.
        if qt_canvas.manager is not None:
            assert_type(
                qt_canvas.manager.canvas,
                FigureCanvasQT[
                    NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT
                ],
            )
            assert_type(
                qt_canvas.manager.toolbar,
                NavigationToolbar2QT | ToolContainerBase | None,
            )
            stock_canvas: FigureCanvasQT = qt_canvas.manager.canvas
            stock_canvas.mouseEventCoords()
        if qt_canvas.toolbar is not None:
            assert_type(
                qt_canvas.toolbar.canvas,
                FigureCanvasQT[
                    NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT
                ],
            )
    # ``manager_class`` is read from a specialization, like every other use
    # of a generic class in this module.  (mypy does not apply type-parameter
    # defaults to a ``classproperty`` read from the *bare* class object.)
    assert_type(
        FigureCanvasQTAgg[
            NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT
        ].manager_class,
        type[FigureManagerQT[Any, Any]],
    )
    assert_type(qtagg_type.manager_class, type[FigureManagerQT])
    assert_type(qtcairo_type.manager_class, type[FigureManagerQT])
    assert_type(FigureCanvasQTAgg.new_manager(figure, 1), FigureManagerQT)
    assert_type(qtagg.copy_from_bbox(figure.bbox), BufferRegion)

    for tk_canvas in (tk, tkagg, tkcairo):
        assert_type(tk_canvas.manager, FigureManagerTk | None)
        assert_type(tk_canvas.toolbar, NavigationToolbar2Tk | None)
        assert_type(tk_canvas.new_timer(), TimerTk)
    assert_type(tkagg_type.manager_class, type[FigureManagerTk])
    assert_type(FigureCanvasTkCairo.new_manager(figure, 1), FigureManagerTk)

    for gtk3_canvas in (gtk3, gtk3agg, gtk3cairo):
        assert_type(gtk3_canvas.manager, FigureManagerGTK3 | None)
        assert_type(gtk3_canvas.toolbar, NavigationToolbar2GTK3 | None)
        assert_type(gtk3_canvas.new_timer(), TimerGTK)
    assert_type(gtk3agg_type.manager_class, type[FigureManagerGTK3])

    for gtk4_canvas in (gtk4, gtk4agg, gtk4cairo):
        assert_type(gtk4_canvas.manager, FigureManagerGTK4 | None)
        assert_type(gtk4_canvas.toolbar, NavigationToolbar2GTK4 | None)
        assert_type(gtk4_canvas.new_timer(), TimerGTK)
    assert_type(gtk4cairo_type.manager_class, type[FigureManagerGTK4])

    for wx_canvas in (wx, wxagg, wxcairo):
        assert_type(wx_canvas.manager, FigureManagerWx | None)
        assert_type(wx_canvas.toolbar, NavigationToolbar2Wx | None)
        assert_type(wx_canvas.new_timer(), TimerWx)
    assert_type(wxagg_type.manager_class, type[FigureManagerWx])


def _check_web_canvas_types(  # pragma: no cover
    core_canvas: FigureCanvasWebAggCore,
    web_canvas: FigureCanvasWebAgg,
    nbagg_canvas: FigureCanvasNbAgg,
    figure: Figure,
) -> None:
    assert_type(core_canvas.manager, FigureManagerWebAggCore[Any] | None)
    assert_type(core_canvas.toolbar, NavigationToolbar2WebAgg | None)
    assert_type(core_canvas.new_timer(), TimerAsyncio)
    assert_type(core_canvas.get_diff_image(), bytes | None)

    assert_type(web_canvas.manager, FigureManagerWebAggApplication | None)
    assert_type(web_canvas.toolbar, NavigationToolbar2WebAgg | None)
    assert_type(FigureCanvasWebAgg.manager_class, type[FigureManagerWebAggApplication])
    assert_type(
        FigureCanvasWebAgg.new_manager(figure, 1), FigureManagerWebAggApplication
    )
    if web_canvas.manager is not None:
        assert_type(web_canvas.manager.ToolbarCls, type[NavigationToolbar2WebAgg])
        assert_type(
            web_canvas.manager.toolbar,
            NavigationToolbar2WebAgg | ToolContainerBase | None,
        )

    assert_type(nbagg_canvas.manager, FigureManagerNbAgg | None)
    assert_type(nbagg_canvas.toolbar, NavigationIPy | None)
    assert_type(nbagg_canvas.new_timer(), TimerAsyncio)
    assert_type(FigureCanvasNbAgg.manager_class, type[FigureManagerNbAgg])
    assert_type(FigureCanvasNbAgg.new_manager(figure, 1), FigureManagerNbAgg)
    if nbagg_canvas.manager is not None:
        assert_type(nbagg_canvas.manager.ToolbarCls, type[NavigationIPy])

    assert_type(FigureManagerWebAggCore.get_javascript(), str)
    assert_type(FigureManagerWebAggCore.get_javascript(io.StringIO()), None)
    assert_type(FigureManagerNbAgg.get_javascript(), str)
    assert_type(FigureManagerNbAgg.get_javascript(io.StringIO()), None)


def _check_agg_extension_types(  # pragma: no cover
    canvas: FigureCanvasAgg,
    renderer: RendererAgg,
    figure: Figure,
) -> None:
    region = canvas.copy_from_bbox(figure.bbox)
    assert_type(region, BufferRegion)
    assert_type(region.get_extents(), tuple[int, int, int, int])
    region.set_x(1)
    region.set_y(2)
    memoryview(region)
    canvas.restore_region(region)
    canvas.restore_region(region, bbox=(0.0, 0.0, 1.0, 1.0), xy=(0.0, 0.0))
    canvas.restore_region(region, bbox=Bbox.from_bounds(0, 0, 1, 1))
    assert_type(renderer.copy_from_bbox(figure.bbox), BufferRegion)
    renderer.restore_region(region)
    renderer.clear()
    renderer.start_filter()
    renderer.stop_filter(lambda image, dpi: (image, 0.0, 0.0))
    memoryview(renderer._renderer)


def _check_cairo_types(  # pragma: no cover
    canvas: FigureCanvasCairo,
    renderer: RendererCairo,
    figure: Figure,
) -> None:
    assert_type(canvas.manager, FigureManagerBase[Any, Any] | None)
    canvas.restore_region(canvas.copy_from_bbox(figure.bbox))
    Artist().draw(renderer)


def _check_negative_cases(  # pragma: no cover
    qt_canvas: FigureCanvasQTAgg,
    web_canvas: FigureCanvasWebAggCore,
    remote_manager: FigureManagerRemote,
    web_manager: FigureManagerWebAggCore[Any],
) -> None:
    # Cross-backend assignments must be rejected: the relationships are
    # invariant on purpose.
    qt_canvas.manager = remote_manager  # type: ignore[assignment]
    remote_manager.canvas = web_canvas  # type: ignore[assignment]
    # The Qt manager's toolbar slot only accepts Qt toolbars.
    if qt_canvas.manager is not None:
        qt_canvas.manager._toolbar2_class = NavigationToolbar2Remote  # type: ignore[assignment]
    # Return types that were previously over-narrow.
    web_manager.get_javascript().upper()
    web_manager.get_javascript(io.StringIO()).upper()  # type: ignore[attr-defined]
    web_canvas.mouseEventCoords()  # type: ignore[attr-defined]
    # The timer class must match the declared timer type parameter.
    FigureCanvasRemote._timer_cls = TimerBase  # type: ignore[assignment]


def _check_diamond_negative_cases(  # pragma: no cover
    any_toolbar: RemoteToolbarMixin[Any],
    remote_toolbar: NavigationToolbar2Remote,
    remote_manager: FigureManagerRemote,
    qt_canvas: FigureCanvasQTRemote,
    tk_toolbar: NavigationToolbar2TkRemote,
    stock_qt_toolbar: NavigationToolbar2QT,
    stock_qt_manager: FigureManagerQT,
) -> None:
    # The standalone remote canvas has no toolkit members.
    remote_toolbar.canvas.drawRectangle(None)  # type: ignore[attr-defined]
    remote_manager.canvas.devicePixelRatioF()  # type: ignore[attr-defined]
    # Before narrowing, the manager's toolbar may be a toolmanager container.
    remote_manager.toolbar.home()  # type: ignore[union-attr]
    # A specialized cross-reference rejects another toolkit's classes, the
    # stock toolkit class, and the standalone remote class.
    qt_canvas.toolbar = tk_toolbar  # type: ignore[assignment]
    qt_canvas.toolbar = stock_qt_toolbar  # type: ignore[assignment]
    qt_canvas.toolbar = remote_toolbar  # type: ignore[assignment]
    # The stock Qt manager's canvas is the stock Qt canvas, not a remote one.
    # Qt classes stand in for an untyped widget, so an unknown member is
    # ``Any`` and not an error.
    assert_type(
        stock_qt_manager.canvas,
        FigureCanvasQT[NavigationToolbar2QT[Any], FigureManagerQT[Any, Any], TimerQT],
    )
    assert_type(stock_qt_manager.canvas.send, Any)
    # A generic class used bare takes its defaults; the mixins have none, so
    # the parameters of a bare mixin are unknown and nothing is checked
    # through it.  This module therefore always names them.
    assert_type(any_toolbar.canvas, Any)


if TYPE_CHECKING:
    # The bounds keep each toolkit family closed: a Tk toolbar is not a valid
    # type argument for a Qt canvas.
    class _WrongFamilyCanvas(
        FigureCanvasQT[
            "NavigationToolbar2TkRemote",  # type: ignore[type-var]
            FigureManagerQT[Any, Any],
            TimerQT,
        ]
    ):
        pass


def _check_native_toolkit_members(  # pragma: no cover
    qt_canvas: FigureCanvasQTRemote,
    qt_toolbar: NavigationToolbar2QTRemote,
    tk_canvas: FigureCanvasTkRemote,
    tk_toolbar: NavigationToolbar2TkRemote,
) -> None:
    # GUI classes inherit their native toolkit widget at runtime.  For Qt, GTK
    # and wx the toolkit is untyped, so the stub spells that base ``Any`` and
    # the widget API is available (as ``Any``); Tk uses the real ``tkinter``
    # stubs.  A downstream thin client subclassing a GUI canvas relies on this.
    qt_canvas.show()
    qt_canvas.setFocus()
    assert_type(qt_canvas.width(), Any)
    assert_type(qt_canvas.devicePixelRatioF(), Any)
    assert_type(qt_toolbar._actions, dict[str, Any])
    qt_toolbar.sizeHint()
    # Matplotlib-owned members keep their precise types alongside ``Any``.
    assert_type(qt_canvas.figure, Figure)
    assert_type(qt_canvas.manager, FigureManagerQT[Any, Any] | None)
    assert_type(qt_toolbar.canvas, FigureCanvasQTRemote)

    assert_type(tk_canvas._tkcanvas, tk.Canvas)
    tk_canvas._tkcanvas.bind("<Configure>", lambda event: None)
    tk_canvas.get_tk_widget()
    tk_toolbar.pack(side=tk.BOTTOM, fill=tk.X)
    assert_type(tk_toolbar.winfo_width(), int)


def _check_renderer_base_boundaries(  # pragma: no cover
    renderer: RendererPdf,
    colorbar: Colorbar,
    figure: Figure,
    gridspec: GridSpec,
    image: AxesImage,
    indicator: InsetIndicator,
    offset_box: OffsetBox,
    cell: Cell,
    annotation: Annotation,
    offset_from: OffsetFrom,
) -> None:
    axes = colorbar.ax

    cell.get_window_extent(renderer)
    cell.get_tightbbox(renderer)
    cell.draw(renderer)
    axes.xaxis.get_tightbbox(renderer)
    axes.set_axes_locator(lambda ax, renderer: ax.bbox)
    axes.get_axes_locator()(axes, renderer)
    axes.get_tightbbox(renderer)
    colorbar.outline.get_window_extent(renderer)
    colorbar.outline.draw(renderer)
    figure.get_tightbbox(renderer)
    gridspec.tight_layout(figure, renderer)
    composite_images([image], renderer)
    image.make_image(renderer)
    image.draw(renderer)
    image.get_window_extent(renderer)
    indicator.draw(renderer)
    offset_box.get_bbox(renderer)
    offset_box.get_window_extent(renderer)
    bbox_artist(cell, renderer)
    draw_bbox(cell.get_window_extent(renderer), renderer)
    PathEffectRenderer([], renderer)
    cell.auto_set_font_size(renderer)
    cell.get_text_bounds(renderer)
    cell.get_required_width(renderer)
    TexManager.get_text_width_height_descent("", 10.0, renderer)
    text = cell.get_text()
    text.update_bbox_position_size(renderer)
    text.get_window_extent(renderer)
    offset_from(renderer)
    annotation.update_positions(renderer)
    annotation.get_window_extent(renderer)
    MixedModeRenderer(
        figure, 1.0, 1.0, 72.0, renderer, raster_renderer_class=RendererPdf
    )


def _check_canvas_base_boundaries(  # pragma: no cover
    canvas: SpecializedFigureCanvasAgg,
    renderer: RendererBase[Any],
    figure: Figure,
    subfigure: SubFigure,
    toolmanager: ToolManager,
    tool: ToolBase,
    selector: VertexSelector,
    draggable: DraggableBase,
    widget: AxesWidget,
    artist: Artist,
) -> None:
    assert_type(
        register_backend("backend_types_mypy", SpecializedFigureCanvasAgg), None
    )
    assert_type(
        get_registered_canvas_class("backend_types_mypy"),
        type[FigureCanvasBase[Any, Any, Any]],
    )

    event = Event("test_event", canvas)
    draw_event = DrawEvent("draw_event", canvas, renderer)
    resize_event = ResizeEvent("resize_event", canvas)
    close_event = CloseEvent("close_event", canvas)
    location_event = LocationEvent("motion_notify_event", canvas, 1, 2)
    mouse_event = MouseEvent("button_press_event", canvas, 1, 2)
    pick_event = PickEvent("pick_event", canvas, mouse_event, artist)
    key_event = KeyEvent("key_press_event", canvas, "x")

    events: list[Event] = [
        event,
        draw_event,
        resize_event,
        close_event,
        location_event,
        mouse_event,
        pick_event,
        key_event,
    ]
    for canvas_event in events:
        assert_type(canvas_event.canvas, FigureCanvasBase[Any, Any, Any])

    key_press_handler(key_event, canvas)
    button_press_handler(mouse_event, canvas)
    scroll_handler(mouse_event, canvas)

    assert_type(toolmanager.canvas, FigureCanvasBase[Any, Any, Any] | None)
    assert_type(tool.canvas, FigureCanvasBase[Any, Any, Any] | None)
    assert_type(
        _tool_registry,
        set[tuple[type[FigureCanvasBase[Any, Any, Any]], type[ToolBase]]],
    )
    assert_type(
        _register_tool_class(SpecializedFigureCanvasAgg, SpecializedTool),
        type[SpecializedTool],
    )
    assert_type(
        _register_tool_class(SpecializedFigureCanvasAgg)(SpecializedTool),
        type[SpecializedTool],
    )
    assert_type(
        _find_tool_class(SpecializedFigureCanvasAgg, SpecializedTool),
        type[SpecializedTool],
    )

    figure.set_canvas(canvas)
    assert_type(figure.canvas, FigureCanvasBase[Any, Any, Any])
    assert_type(subfigure.canvas, FigureCanvasBase[Any, Any, Any])
    assert_type(selector.canvas, FigureCanvasBase[Any, Any, Any])
    assert_type(draggable.canvas, FigureCanvasBase[Any, Any, Any])
    assert_type(widget.canvas, FigureCanvasBase[Any, Any, Any] | None)
