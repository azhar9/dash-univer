# dash-univer

[![PyPI](https://img.shields.io/pypi/v/dash-univer.svg?v=1)](https://pypi.org/project/dash-univer/)
[![Python](https://img.shields.io/pypi/pyversions/dash-univer.svg?v=1)](https://pypi.org/project/dash-univer/)
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

## Common patterns

Helpers used below: the workbook is Univer's
[`IWorkbookData`](https://docs.univer.ai/guides/sheets/getting-started/workbook-data) —
a plain dict, so everything is ordinary Python.

```python
import copy

def read_cell(data, sheet_id, row, col):
    """Read one cell value from the workbook dict."""
    return (
        data["sheets"][sheet_id]
        .get("cellData", {})
        .get(str(row), {})
        .get(str(col), {})
        .get("v")
    )

def set_cell(data, sheet_id, row, col, value):
    """Write one cell into the workbook dict (returns the dict)."""
    data = copy.deepcopy(data)
    sheet = data["sheets"][sheet_id]
    sheet.setdefault("cellData", {}).setdefault(str(row), {})[str(col)] = {"v": value}
    return data
```

### Listen — react to edits (read)

Every user edit pushes a debounced full snapshot to `data` (300 ms default;
tune with the `debounce` prop). Any callback with `Input("sheet", "data")`
sees the current state:

```python
@app.callback(Output("total", "children"), Input("sheet", "data"))
def on_edit(data):
    revenue = sum(
        cell.get("v", 0)
        for row in data["sheets"]["s1"].get("cellData", {}).values()
        for cell in row.values()
        if isinstance(cell.get("v"), (int, float))
    )
    return f"Total: {revenue}"
```

### Update — write data from Python (edit / delete)

Return a workbook from a callback to re-render the sheet:

```python
# Edit: write a value into a cell
@app.callback(Output("sheet", "data"), Input("set-btn", "n_clicks"),
              State("sheet", "data"), prevent_initial_call=True)
def update(n, data):
    return set_cell(data, "s1", 2, 0, "Updated")

# Delete: remove a sheet (and clear cells the same way — set "v": None)
@app.callback(Output("sheet", "data"), Input("delete-sheet-btn", "n_clicks"),
              State("sheet", "data"), prevent_initial_call=True)
def delete_sheet(n, data):
    data = copy.deepcopy(data)
    if "s2" in data["sheets"]:
        del data["sheets"]["s2"]
        data["sheetOrder"].remove("s2")
    return data
```

### Save & restore

`data` is the complete workbook — persist it anywhere (DB, file, Redis) as
JSON and feed it back to restore:

```python
app.layout = html.Div([
    UniverSheet(id="sheet", data=seed),
    html.Button("Save", id="save-btn"),
    html.Button("Restore", id="restore-btn"),
    dcc.Store(id="saved"),  # or json.dump(data, open("wb.json", "w")) instead
])

@app.callback(Output("saved", "data"), Input("save-btn", "n_clicks"),
              State("sheet", "data"), prevent_initial_call=True)
def save(n, data):
    return data

@app.callback(Output("sheet", "data"), Input("restore-btn", "n_clicks"),
              State("saved", "data"), prevent_initial_call=True)
def restore(n, saved):
    return saved or {}
```

Note: restoring rebuilds the sheet, so transient UI state (cursor, undo
history, scroll position) resets — document content is fully preserved.

### Export to Excel / CSV

The workbook dict converts to a DataFrame per sheet, then to any format
(`openpyxl`/`xlsxwriter`/`pandas` in your app's own dependencies):

```python
import io
import pandas as pd
from dash import dcc

def sheet_to_df(data, sheet_id):
    values = {
        int(r): {int(c): cell.get("v") for c, cell in cols.items()}
        for r, cols in data["sheets"][sheet_id].get("cellData", {}).items()
    }
    df = pd.DataFrame.from_dict(values, orient="index").sort_index()
    return df.reindex(sorted(df.columns), axis=1)

@app.callback(Output("download-excel", "data"), Input("export-btn", "n_clicks"),
              State("sheet", "data"), prevent_initial_call=True)
def export_excel(n, data):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_id in data["sheetOrder"]:
            sheet_to_df(data, sheet_id).to_excel(
                writer, sheet_name=data["sheets"][sheet_id]["name"], index=False
            )
    return dcc.send_bytes(buf.getvalue(), "workbook.xlsx")

# CSV is one line: sheet_to_df(data, "s1").to_csv(index=False)
# Don't forget dcc.Download(id="download-excel") in the layout.
```

## Development

Requires Python ≥3.9, Node ≥18, and Chrome (for the tests).

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uv pip install -U "selenium==4.11.2"   # dash[testing] pins selenium<=4.2, which
                                       # breaks with modern ChromeDriver
npm install
npm run build          # webpack bundle + generates the Python classes
python usage.py        # live demo at http://127.0.0.1:8050

pytest --headless      # end-to-end tests (real browser)
```

`npm run build` runs webpack (bundling Univer, with React/ReactDOM externalized
to the ones Dash provides) and then `dash-generate-components`, which regenerates
`dash_univer/UniverSheet.py` from the component's PropTypes.

The tests use `dash.testing` with Selenium; Selenium Manager downloads a
matching `chromedriver` automatically, so just have Chrome installed.
CI tests on Python 3.9, 3.13, and 3.14.

## Scope

v1 wraps Univer **Sheets** (`@univerjs/preset-sheets-core`) in English. Docs,
Slides, other locales, and granular per-cell events are intentionally out of
scope for now — the full-snapshot `data` contract already exposes everything,
including export (see [Export to Excel / CSV](#export-to-excel--csv)). Univer's
native export toolbar plugins are not bundled; export server-side from `data`
as shown above, or reach the
[Facade API](https://docs.univer.ai/guides/sheets/getting-started/facade) for
client-side workflows.

## License

This wrapper is [MIT](LICENSE) licensed. [Univer](https://github.com/dream-num/univer)
itself is Apache-2.0. The wheel ships the full Apache-2.0 and MIT texts of all
bundled third-party code under `LICENSES/` — see `THIRD_PARTY_LICENSES.md`.
