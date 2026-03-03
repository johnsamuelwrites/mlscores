# Onboarding Guide

## 1. Local Setup

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Optional web dependencies:

```bash
pip install -r requirements-web.txt
```

## 2. Run Tests

```bash
pytest -q
```

## 3. Run the App

### CLI

```bash
python3 -m mlscores Q42 -l en fr es
```

### FastAPI

```bash
python3 -m mlscores --web
```

Main UI: `http://127.0.0.1:8000/`

### WASM (Pyodide)

Served by FastAPI static files:
- `http://127.0.0.1:8000/static/wasm/index.html`

Static hosting path (GitHub Pages workflow source):
- `mlscores/web/static/wasm/`

## 4. Project Structure

- `mlscores/` core package
- `mlscores/query.py` backend query execution (SPARQLWrapper transport)
- `mlscores/scores.py` language percentage and missing translation logic
- `mlscores/web/` FastAPI app and routes
- `mlscores/web/static/` frontend assets
- `mlscores/web/static/wasm/` browser-only Pyodide implementation
- `mlscores/web/static/wasm/query_builders.py` shared SPARQL query builders

## 5. Adding New Languages

Most of the time, no code change is needed.

- CLI: users pass `-l <codes...>`
- API: pass `languages: ["en", "fr", ...]`
- UI: users enter comma-separated language codes

If you want predefined language shortcuts/presets, implement them in UI code only.

## 6. Adding Endpoint Presets

FastAPI web UI presets live in:
- `mlscores/web/static/app.js` (`ENDPOINT_CONFIGS`)

To add a preset:
1. Add config entry with endpoint metadata.
2. Add corresponding `<option>` in `mlscores/web/static/index.html`.
3. Validate link rendering and score calls.

WASM UI currently accepts a direct endpoint URL input.

## 7. Changing Query Logic Safely

Use shared builders in:
- `mlscores/web/static/wasm/query_builders.py`

When modifying query text:
1. Update builder function(s) once.
2. Verify backend path (`mlscores/query.py`) still imports and executes builders.
3. Verify WASM path (`mlscores/web/static/wasm/mlscores_wasm.py`) still imports `query_builders`.
4. Re-run tests and a manual web check.

## 8. Release/Deployment Notes

- FastAPI deployment: deploy Python app normally.
- GitHub Pages deployment: workflow `.github/workflows/deploy-pages.yml` publishes WASM static app.

