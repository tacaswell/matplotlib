"""
Runtime backend typing tests and fixtures shared with tools/typing/backend_types.py.
"""

from __future__ import annotations

import datetime
import io
from pathlib import Path
from typing import Any, assert_type, get_origin

import matplotlib.backend_bases as backend_bases
from matplotlib import _api
from matplotlib.artist import Artist
from matplotlib.backend_bases import (
    Event,
    FigureCanvasBase,
    FigureManagerBase,
    GraphicsContextBase,
    MouseEvent,
    NavigationToolbar2,
    RendererBase,
    TimerBase,
    _Backend,
    get_registered_canvas_class,
    register_backend,
)
from matplotlib.backend_tools import ToolBase
from matplotlib.backends._backend_agg import BufferRegion
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import (
    FigureManagerPdf,
    Name,
    PdfFile,
    PdfPages,
    RendererPdf,
)
from matplotlib.figure import Figure
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Transform


class SpecializedTimer(TimerBase):
    pass


class SpecializedFigureCanvasAgg(
    FigureCanvasAgg[
        NavigationToolbar2[Any], FigureManagerBase[Any, Any], SpecializedTimer
    ]
):
    pass


class SpecializedTool(ToolBase):
    pass


class SpecializedFigureManager(FigureManagerBase[Any, Any]):
    pass


# A simulated third-party backend.  Both type checkers analyze the method
# bodies here as well as the static checks that import these fixtures.
# The toolkit-agnostic classes are generic mixins: each toolkit specialization
# in tools/typing/backend_types.py supplies its own toolbar, manager and timer.
class RemoteTimer(TimerBase):
    pass


class RemoteGraphicsContext(GraphicsContextBase):
    pass


class RemoteRenderer(RendererBase[RemoteGraphicsContext]):
    def new_gc(self) -> RemoteGraphicsContext:
        return RemoteGraphicsContext()

    def draw_path(
        self,
        gc: RemoteGraphicsContext,
        path: MplPath,
        transform: Transform,
        rgbFace: Any = None,
    ) -> None:
        pass


class RemoteCanvasMixin[
    ToolbarT: RemoteToolbarMixin[Any],
    ManagerT: FigureManagerBase[Any, Any],
    TimerT: TimerBase,
](FigureCanvasBase[ToolbarT, ManagerT, TimerT]):
    """Toolkit-agnostic canvas of a thin client: forwards to a server."""

    def __init__(self, figure: Figure | None = None, **kwargs: Any) -> None:
        # Toolkit keyword arguments (``master=`` for Tk) pass through the MRO
        # to the toolkit canvas this class is mixed with.
        super().__init__(figure, **kwargs)
        self.sent: list[dict[str, Any]] = []

    def send(self, message: dict[str, Any]) -> None:
        """Stand-in for the wire transport of a real thin client."""
        self.sent.append(message)

    def on_server_message(self, message: dict[str, Any]) -> None:
        """Update the toolbar from a message pushed by the server."""
        # The bound of ``ToolbarT`` makes the remote toolbar's hooks available.
        if self.toolbar is None:
            return
        if message["type"] == "navigate_mode":
            self.toolbar._on_navigate_mode(message["mode"])
        elif message["type"] == "message":
            self.toolbar.set_message(message["text"])

    def _use_backend_authoring_api(self) -> None:  # pragma: no cover
        assert_type(self._set_device_pixel_ratio(2.0), bool)
        Event("remote_event", self)._process()
        MouseEvent("button_press_event", self, 1, 2)._process()


class RemoteToolbarMixin[
    CanvasT: RemoteCanvasMixin[Any, Any, Any],
](NavigationToolbar2[CanvasT]):
    """Toolkit-agnostic toolbar of a thin client."""

    def __init__(self, canvas: CanvasT, *args: Any, **kwargs: Any) -> None:
        self.server_mode = ""
        super().__init__(canvas, *args, **kwargs)

    # The bound of ``CanvasT`` makes the remote canvas's ``send`` available.
    def home(self, *args: Any) -> None:
        self.canvas.send({"type": "toolbar_button", "name": "home"})

    def pan(self, *args: Any) -> None:
        self.canvas.send({"type": "toolbar_button", "name": "pan"})

    def set_history_buttons(self) -> None:
        pass

    def _on_navigate_mode(self, mode: str) -> None:
        self.server_mode = mode


# The mixins used without a GUI toolkit: each specialization names the others.
class FigureCanvasRemote(
    RemoteCanvasMixin["NavigationToolbar2Remote", "FigureManagerRemote", RemoteTimer]
):
    _timer_cls = RemoteTimer

    # A ``classproperty`` allows class access and a forward reference to the
    # manager.  Its owner is generic, so ``cls`` cannot be narrowed here.
    @_api.classproperty
    def manager_class(cls: Any) -> type[FigureManagerRemote]:
        return FigureManagerRemote


class NavigationToolbar2Remote(RemoteToolbarMixin[FigureCanvasRemote]):
    pass


class FigureManagerRemote(
    FigureManagerBase[FigureCanvasRemote, NavigationToolbar2Remote]
):
    _toolbar2_class = NavigationToolbar2Remote

    def announce(self) -> None:
        """Use the canvas and the toolbar through the manager's references."""
        self.canvas.send({"type": "title", "title": self.get_window_title()})
        # ``toolbar`` may also be a toolmanager container or ``None``.
        if isinstance(self.toolbar, NavigationToolbar2Remote):
            self.toolbar.home()


class _BackendRemote(_Backend[type[FigureCanvasRemote]]):
    FigureCanvas = FigureCanvasRemote
    FigureManager = FigureManagerRemote


def test_backend_subclass_types() -> None:
    fig = Figure()
    canvas = SpecializedFigureCanvasAgg(fig)

    fig.set_canvas(canvas)
    assert_type(fig.canvas, FigureCanvasBase[Any, Any, Any])

    event = MouseEvent("button_press_event", canvas, 1, 2)
    assert event.canvas is canvas

    file_format = "backend_types"
    try:
        register_backend(file_format, SpecializedFigureCanvasAgg)
        assert get_registered_canvas_class(file_format) is SpecializedFigureCanvasAgg
    finally:
        vars(backend_bases)["_default_backends"].pop(file_format)
        vars(backend_bases)["_default_filetypes"].pop(file_format)

    pdf_file = PdfFile(io.BytesIO())
    try:
        renderer = RendererPdf(pdf_file, 72, 1, 1)
        Artist().draw(renderer)
    finally:
        pdf_file.close()


def test_remote_backend_runtime() -> None:
    # The generic bases are subscriptable at runtime (``__class_getitem__``),
    # so the class statements above import and instantiate.
    fig = Figure()
    canvas = FigureCanvasRemote(fig)
    manager = FigureManagerRemote(canvas, 1)
    assert canvas.manager is manager
    assert isinstance(manager.toolbar, NavigationToolbar2Remote)
    assert manager.toolbar.canvas is canvas
    assert isinstance(canvas.new_timer(), RemoteTimer)
    assert canvas._set_device_pixel_ratio(2.0)
    assert canvas.device_pixel_ratio == 2.0

    # The static and the runtime answer for ``manager_class`` agree, and
    # ``new_manager`` builds the manager it names.
    assert_type(FigureCanvasRemote.manager_class, type[FigureManagerRemote])
    assert FigureCanvasRemote.manager_class is FigureManagerRemote
    made = FigureCanvasRemote.new_manager(Figure(), 2)
    assert_type(made, FigureManagerRemote)
    assert type(made) is FigureManagerRemote
    assert made.canvas.manager is made

    # The mixins are generic classes at runtime too: subscripting one gives
    # an alias of the class, which is what a class statement inherits from.
    assert get_origin(RemoteCanvasMixin[Any, Any, Any]) is RemoteCanvasMixin
    assert issubclass(FigureCanvasRemote, RemoteCanvasMixin)
    assert issubclass(NavigationToolbar2Remote, RemoteToolbarMixin)

    # The classes use each other through the cross-references.
    manager.toolbar.pan()
    manager.announce()
    assert canvas.sent == [
        {"type": "toolbar_button", "name": "pan"},
        {"type": "title", "title": manager.get_window_title()},
        {"type": "toolbar_button", "name": "home"},
    ]
    canvas.on_server_message({"type": "navigate_mode", "mode": "PAN"})
    assert manager.toolbar.server_mode == "PAN"


def test_agg_buffer_region_runtime() -> None:
    fig = Figure()
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    region = canvas.copy_from_bbox(fig.bbox)
    assert isinstance(region, BufferRegion)
    x0, y0, x1, y1 = region.get_extents()
    assert (x1 - x0, y1 - y0) == tuple(int(v) for v in fig.bbox.size)
    assert memoryview(region).ndim == 3
    canvas.restore_region(region)
    canvas.restore_region(region, bbox=(x0, y0, x1, y1), xy=(x0, y0))


def test_pdfpages_types(tmp_path: Path) -> None:
    fig = Figure()
    metadata: dict[str, str] = {"Title": "A title"}
    removed_metadata: dict[str, str | None] = {"Creator": None}

    with PdfPages(tmp_path / "output.pdf", metadata=metadata) as pdf:
        pdf.savefig(fig, dpi=100)
        info = pdf.infodict()
        info["ModDate"] = datetime.datetime.now()
        assert_type(info, dict[str, str | datetime.datetime | Name])
        assert info["Title"] == "A title"

    with PdfPages(tmp_path / "without-creator.pdf", metadata=removed_metadata) as pdf:
        pdf.savefig(fig)
        assert "Creator" not in pdf.infodict()

    assert FigureManagerPdf is FigureManagerBase
