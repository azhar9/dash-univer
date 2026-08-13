# dash-univer

[![PyPI](https://img.shields.io/pypi/v/dash-univer.svg)](https://pypi.org/project/dash-univer/)
[![Python](https://img.shields.io/pypi/pyversions/dash-univer.svg)](https://pypi.org/project/dash-univer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/azhar9/dash-univer/actions/workflows/ci.yml/badge.svg)](https://github.com/azhar9/dash-univer/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/azhar9/dash-univer/graph/badge.svg)](https://codecov.io/gh/azhar9/dash-univer)

A [Dash](https://dash.plotly.com/) component that embeds the
[Univer](https://univer.ai) spreadsheet — a full-featured, Excel-like sheet with
formulas — directly in your Dash app, wired to Dash callbacks.

```bash
pip install dash-univer
```

## Quick start

```python
from dash import Dash, html, Input, Output
from dash_univer import UniverSheet

app = Dash(__name__)

app.layout = html.Div([
    UniverSheet(id="sheet", data={
        "id": "wb",
        "name": "My Workbook",
        "sheetOrder": ["s1"],
        "sheets": {
            "s1": {
                "id": "s1",
                "name": "Sheet1",
                "cellData": {
                    "0": {"0": {"v": "Product"}, "1": {"v": "Revenue"}},
                    "1": {"0": {"v": "Widget"}, "1": {"v": 1000}},
                },
            },
        },
    }),
    html.Pre(id="out"),
])


@app.callback(Output("out", "children"), Input("sheet", "data"))
def show(data):
    return f"{len(data.get('sheets', {}))} sheet(s) in the workbook"


if __name__ == "__main__":
    app.run(debug=True)
```

Run `python usage.py` in this repo for a fuller live demo.

## How it works

`UniverSheet` mounts a Univer spreadsheet into a `<div>`. Univer runs in its own
isolated React root inside that div, so it never conflicts with Dash's React tree.

The `data` prop is the whole workbook (Univer's
[`IWorkbookData`](https://docs.univer.ai/guides/sheets/getting-started/workbook-data)
as a plain dict) and syncs **both ways**:

- **Sheet → Python:** as the user edits, a debounced full snapshot of the
  workbook is pushed to `data`, so any callback with `Input("sheet", "data")`
  sees the current state.
- **Python → Sheet:** returning a workbook from a callback's
  `Output("sheet", "data")` re-renders the sheet. The component guards against
  echoing its own snapshots, so this never causes a feedback loop.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | string | – | Component id for Dash callbacks. |
| `data` | dict | `{}` | The workbook (`IWorkbookData`). Round-trips both ways. |
| `debounce` | number | `300` | Milliseconds to debounce edit → `data` updates. |
| `style` | dict | `{height: "500px", width: "100%"}` | Container styles. **Give it a height** — Univer collapses to zero height otherwise. |
| `className` | string | – | Container CSS class. |

Advanced: the live Univer
[Facade API](https://docs.univer.ai/guides/sheets/getting-started/facade) is
exposed as `document.getElementById(id).univerAPI` for client-side callbacks or
custom JS.

## Development

Requires Python ≥3.9, Node ≥18, and Chrome (for the tests).

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
npm install
npm run build          # webpack bundle + generates the Python classes
python usage.py        # live demo at http://127.0.0.1:8050

pytest --headless      # end-to-end tests (real browser)
```

`npm run build` runs webpack (bundling Univer, with React/ReactDOM externalized
to the ones Dash provides) and then `dash-generate-components`, which regenerates
`dash_univer/UniverSheet.py` from the component's PropTypes.

The tests use `dash.testing` with Selenium; they need a `chromedriver` matching
your installed Chrome on `PATH` (see
[Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)).

## Scope

v1 wraps Univer **Sheets** (`@univerjs/preset-sheets-core`) in English. Docs,
Slides, other locales, and granular per-cell events are intentionally out of
scope for now — the full-snapshot `data` contract already exposes everything.

## License

This wrapper is [MIT](LICENSE) licensed. [Univer](https://github.com/dream-num/univer)
itself is Apache-2.0.
