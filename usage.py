"""Run a live demo: python usage.py, then open http://127.0.0.1:8050."""

from dash import Dash, Input, Output, html

from dash_univer import UniverSheet

SEED = {
    "id": "demo",
    "name": "Demo Workbook",
    "sheetOrder": ["s1"],
    "sheets": {
        "s1": {
            "id": "s1",
            "name": "Sheet1",
            "cellData": {
                "0": {"0": {"v": "Product"}, "1": {"v": "Revenue"}},
                "1": {"0": {"v": "Widget"}, "1": {"v": 1000}},
                "2": {"0": {"v": "Gadget"}, "1": {"v": 2500}},
            },
        },
    },
}

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H3("dash-univer demo"),
        UniverSheet(id="sheet", data=SEED, style={"height": "70vh"}),
        html.H4("Live workbook snapshot (updates as you edit):"),
        html.Pre(id="out", style={"maxHeight": "200px", "overflow": "auto"}),
    ]
)


@app.callback(Output("out", "children"), Input("sheet", "data"))
def show(data):
    import json

    return json.dumps(data, indent=2)[:2000]


if __name__ == "__main__":
    app.run(debug=True)
