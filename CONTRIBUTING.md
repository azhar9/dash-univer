# Contributing to dash-univer

## Development workflow

1. **Branch** — create a feature branch off `main` (`git checkout -b fix/sheet-sync`). Never commit directly to `main` unless you have admin rights.
2. **Change + test** — see [Local setup](#local-setup) below.
3. **PR** — open a pull request into `main`. Fill in the PR template.
4. **Gate** — the PR must have:
   - CI green (tests on Python 3.9/3.11/3.13)
   - 1 approving review
5. **Merge** — squash-merge after approval.

## Releasing

1. Bump `version` in `pyproject.toml` on `main`.
2. Tag: `git tag v0.2.0 && git push origin v0.2.0` (tags matching `v*` are restricted to maintainers).
3. The release workflow builds and publishes to PyPI (trusted publishing, no tokens) and creates a GitHub Release with the artifacts.

## Local setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"   # includes dash[testing], pytest, etc.
uv pip install -U "selenium==4.11.2"   # dash[testing] pins selenium<=4.2, which
                                       # breaks with modern ChromeDriver
npm ci
npm run build                # webpack bundle + dash-generate-components
```

## Running tests

```bash
pytest --headless -v
```

The end-to-end tests use `dash.testing` (Selenium) — a Chrome/chromedriver
pair is required. Selenium Manager fetches the driver automatically.
