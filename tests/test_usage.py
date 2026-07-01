"""End-to-end tests: a real Dash app + headless Chrome, driving the actual
Univer spreadsheet through its Facade API and asserting the Dash <-> Univer
data round-trip works.

Univer renders to a <canvas>, so cell contents can't be read from the DOM. We
drive/read the workbook via the Facade API exposed on the container node as
`node.univerAPI` (see UniverSheet.react.js).
"""

import json

import pytest
from dash import Dash, Input, Output, State, html

from dash_univer import UniverSheet

SEED = {
    "id": "wb",
    "name": "Test",
    "sheetOrder": ["s1"],
    "sheets": {
        "s1": {
            "id": "s1",
            "name": "Sheet1",
            "cellData": {"0": {"0": {"v": "Widget"}, "1": {"v": 1000}}},
        }
    },
}


def _wait_for_univer(dash_duo):
    """Wait until Univer has mounted (canvas drawn + facade handle attached)."""
    dash_duo.wait_for_element("#sheet canvas", timeout=20)
    dash_duo.wait_for_element("#sheet", timeout=20)
    dash_duo._wait_for(
        lambda driver: driver.execute_script(
            "return !!document.getElementById('sheet').univerAPI"
        ),
        timeout=20,
        msg="univerAPI never attached to #sheet",
    )


def _cell(dash_duo, a1):
    """Read a cell value from the live workbook via the Facade API."""
    return dash_duo.driver.execute_script(
        "return document.getElementById('sheet').univerAPI"
        ".getActiveWorkbook().getActiveSheet()"
        f".getRange('{a1}').getValue();"
    )


def _set_cell(dash_duo, a1, value):
    """Set a cell value via the Facade API (mimics a user edit)."""
    dash_duo.driver.execute_script(
        "document.getElementById('sheet').univerAPI"
        ".getActiveWorkbook().getActiveSheet()"
        f".getRange('{a1}').setValue(arguments[0]);",
        value,
    )


def test_dush001_renders_without_console_errors(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([UniverSheet(id="sheet", data=SEED)])
    dash_duo.start_server(app)

    _wait_for_univer(dash_duo)

    severe = [e for e in dash_duo.get_logs() if e["level"] == "SEVERE"]
    assert severe == [], f"Unexpected browser console errors: {severe}"


def test_dush002_initial_data_reaches_univer(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([UniverSheet(id="sheet", data=SEED)])
    dash_duo.start_server(app)

    _wait_for_univer(dash_duo)

    # The seeded value made it into the actual Univer workbook, not just the prop.
    assert _cell(dash_duo, "A1") == "Widget"
    assert _cell(dash_duo, "B1") == 1000


def test_dush003_edit_propagates_to_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [UniverSheet(id="sheet", data=SEED, debounce=50), html.Pre(id="out")]
    )

    @app.callback(Output("out", "children"), Input("sheet", "data"))
    def show(data):
        return json.dumps(data or {})

    dash_duo.start_server(app)
    _wait_for_univer(dash_duo)

    _set_cell(dash_duo, "A1", "EDITED")

    # The edit must flow: Univer -> setProps(data) -> Dash callback -> #out.
    dash_duo.wait_for_contains_text("#out", "EDITED", timeout=10)


def test_dush004_python_update_rerenders_without_loop(dash_duo):
    """Setting data from a callback must re-render the sheet AND not trigger an
    edit->emit->callback feedback loop."""
    fire_count = {"n": 0}

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("load", id="btn"),
            UniverSheet(id="sheet", data=SEED, debounce=50),
            html.Div(id="count"),
        ]
    )

    new_wb = {
        "id": "wb2",
        "name": "Test2",
        "sheetOrder": ["s1"],
        "sheets": {
            "s1": {
                "id": "s1",
                "name": "Sheet1",
                "cellData": {"0": {"0": {"v": "FROMPYTHON"}}},
            }
        },
    }

    @app.callback(
        Output("sheet", "data"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def load(_):
        return new_wb

    @app.callback(Output("count", "children"), Input("sheet", "data"))
    def counter(_):
        fire_count["n"] += 1
        return str(fire_count["n"])

    dash_duo.start_server(app)
    _wait_for_univer(dash_duo)

    baseline = fire_count["n"]
    dash_duo.find_element("#btn").click()

    # Sheet actually re-rendered with the Python-provided workbook.
    dash_duo._wait_for(
        lambda driver: _cell(dash_duo, "A1") == "FROMPYTHON",
        timeout=10,
        msg="sheet did not update from Python callback",
    )

    # Give any runaway loop time to manifest, then assert bounded firing.
    import time

    time.sleep(2)
    delta = fire_count["n"] - baseline
    assert delta <= 3, f"data callback fired {delta} times — likely a feedback loop"


def test_dush005_debounce_coalesces_rapid_edits(dash_duo):
    fire_count = {"n": 0}

    app = Dash(__name__)
    app.layout = html.Div(
        [UniverSheet(id="sheet", data=SEED, debounce=300), html.Div(id="count")]
    )

    @app.callback(Output("count", "children"), Input("sheet", "data"))
    def counter(_):
        fire_count["n"] += 1
        return str(fire_count["n"])

    dash_duo.start_server(app)
    _wait_for_univer(dash_duo)

    baseline = fire_count["n"]
    for i in range(5):
        _set_cell(dash_duo, "A1", f"v{i}")

    import time

    time.sleep(1.5)
    # 5 rapid edits within the debounce window should collapse to ~1 emission.
    delta = fire_count["n"] - baseline
    assert delta <= 2, f"debounce failed: {delta} emissions for 5 rapid edits"
