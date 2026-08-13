# Changelog

## 0.1.1 (2026-08-12)

- Ship third-party license attribution with the wheel: bundled JS licenses
  (`dash_univer.js.LICENSE.txt`), a `THIRD_PARTY_LICENSES.md` listing
  Univer, rxjs, localForage, decimal.js, and react-jsx-runtime, and the full
  Apache-2.0 / MIT texts under `LICENSES/`.
- Pin `dash` to `>=3,<5` (upper bound until CI proves dash 5).
- Pin the hatchling build backend to `<2`.

## 0.1.0 (2026-08-12) — withdrawn

Initial release (withdrawn from PyPI and GitHub Releases; superseded by
0.1.1, which ships third-party license attribution).

- `UniverSheet` Dash component wrapping `@univerjs/preset-sheets-core` 0.25.1.
- Bidirectional `data` sync (Univer's `IWorkbookData`) with debounced edits and
  a guard against Python↔sheet feedback loops.
- Univer Facade API exposed on the container node for client-side callbacks.
- End-to-end test suite (`dash.testing` + headless Chrome).
