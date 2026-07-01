# Changelog

## 0.1.0 (unreleased)

Initial release.

- `UniverSheet` Dash component wrapping `@univerjs/preset-sheets-core` 0.25.1.
- Bidirectional `data` sync (Univer's `IWorkbookData`) with debounced edits and
  a guard against Python↔sheet feedback loops.
- Univer Facade API exposed on the container node for client-side callbacks.
- End-to-end test suite (`dash.testing` + headless Chrome).
