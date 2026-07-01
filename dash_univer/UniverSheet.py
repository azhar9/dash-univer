# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.types import NumberType  # noqa: F401
except ImportError:
    # Backwards compatibility for dash<=4.1.0
    if typing.TYPE_CHECKING:
        raise
    NumberType = typing.Union[  # noqa: F401
        typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
    ]

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]


class UniverSheet(Component):
    """An UniverSheet component.
UniverSheet renders a Univer spreadsheet (https://univer.ai) inside a Dash app.

The `data` prop is the workbook (Univer's IWorkbookData as a plain dict) and
round-trips in both directions: user edits emit a debounced full snapshot back
to Dash callbacks, and setting `data` from a callback re-renders the sheet.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    CSS class for the container div.

- data (dict; optional):
    The workbook contents as Univer's IWorkbookData (a plain object).
    Updated (debounced) as the user edits, and re-rendered when set
    from a callback.

- debounce (number; default 300):
    Milliseconds to debounce edit -> `data` updates sent to Dash.
    Default 300."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_univer'
    _type = 'UniverSheet'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        data: typing.Optional[dict] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        debounce: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'className', 'data', 'debounce', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'data', 'debounce', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(UniverSheet, self).__init__(**args)

setattr(UniverSheet, "__init__", _explicitize_args(UniverSheet.__init__))
