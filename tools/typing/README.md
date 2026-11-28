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
