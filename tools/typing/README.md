# Static typing checks

`backend_types.py` contains static checks for the backend typing model. Its
runtime fixtures and tests live in `lib/matplotlib/tests/test_backend_types.py`.
Run the checks with `pixi run -e typing pyright` or mypy using `pyproject.toml`.

## Deferred investigations

### Relative font sizes

`FontManager.score_size` in `lib/matplotlib/font_manager.py` multiplies
`self.default_size` by a relative-size scaling factor. The constructor permits
`default_size` to be `None`, so relative-size scoring against a non-scalable font
can fail. Investigate resolving the effective default size without overriding an
explicit constructor value. The normal scalable-font path returns early.

### Constrained-layout colorbar offsets

`reposition_colorbar` in `lib/matplotlib/_constrained_layout.py` defaults
`offset` to `None`, then unconditionally indexes and updates its four direction
keys. Its current caller passes a dictionary. Investigate making the argument
required or initializing a fresh direction dictionary when omitted; preserve
the shared offsets used to position multiple colorbars.

### Bounding-box point storage

Some `BboxBase` methods in `lib/matplotlib/transforms.py` access `_points`
directly, but subclasses need only implement `get_points()`. `TransformedBbox`
starts its point cache at `None` and materializes it through `get_points()`.
Investigate using the accessor where appropriate instead of assuming every
base instance has an initialized ndarray backing field. Review invalidation
and lazy-cache semantics before changing these accesses or silencing them.

### AFM header fields

`FontMetricsHeader` in `lib/matplotlib/_afm.py` is a `total=False` TypedDict.
The parser skips invalid or absent fields, while accessors index those fields
directly. Investigate whether missing-field `KeyError` is the intended contract
or whether required fields should be validated after parsing. Do not add
`Required[...]` blindly: the parser also uses the annotations as its runtime
conversion schema, so typing wrappers would need to be unwrapped there.
