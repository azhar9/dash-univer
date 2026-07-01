import json
import os as _os
import sys as _sys

from ._imports_ import *  # noqa: F401, F403
from ._imports_ import __all__

_basepath = _os.path.dirname(__file__)
with open(_os.path.join(_basepath, "package.json")) as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")
__version__ = package["version"]

# Univer's CSS is injected at runtime by style-loader from within this bundle,
# so a single JS file is all Dash needs to serve. React/ReactDOM/PropTypes are
# provided by Dash itself and are externalized out of this bundle.
_js_dist = [
    {
        "relative_package_path": "dash_univer.js",
        "namespace": package_name,
    }
]

_css_dist = []

_this_module = _sys.modules[__name__]
for _component in __all__:
    setattr(getattr(_this_module, _component), "_js_dist", _js_dist)
    setattr(getattr(_this_module, _component), "_css_dist", _css_dist)
