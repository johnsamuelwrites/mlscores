# mlscores
Multilinguality score of Wikidata (or Wikibase) items


## Overview

This package generates multilinguality scores for Wikidata (Wikibase) items, specifically for property and property value labels. The scores represent the percentage of labels available in a given language.

## Context

### Multilinguality Calculator for Wikidata Items

`mlscores` analyzes the multilinguality of Wikidata items and properties, providing a measure of how much content is available in different languages. By evaluating the completeness of descriptions, labels, and statements (**properties, property values, qualifier properties, qualifier values, reference properties, reference property values**) in multiple languages (e.g., English, French, Spanish,... any supported language), it gives insights into the global accessibility of Wikidata entries.

Designed to support researchers, data scientists, and Wikidata contributors, this tool helps identify language gaps and prioritize translations to enhance the multilingual coverage of Wikidata's knowledge base. Whether you're working on expanding local language content or analyzing cross-language data availability, `mlscores` provides the metrics to guide your efforts.

## Installation

For installation, please follow these steps:

1. Make sure you have Python 3.x and pip installed on your system.
2. Clone the repository or download the source code.
3. Navigate to the directory containing the source code.
4. Install the package:

```bash
# Basic installation
pip install .

# With development dependencies (pytest, pytest-cov)
pip install ".[dev]"

# With web interface dependencies (FastAPI, uvicorn)
pip install ".[web]"

# With all dependencies
pip install ".[dev,web]"
```

Alternatively, install dependencies using requirements files:

```bash
# Core dependencies only
pip install -r requirements.txt

# With development dependencies
pip install -r requirements-dev.txt

# With web interface dependencies
pip install -r requirements-web.txt
```

## Quick Start

### CLI (core)

```bash
pip install .
python3 -m mlscores Q42 -l en fr es
```

### FastAPI Web UI

```bash
pip install ".[web]"
python3 -m mlscores --web
```

Open:
- UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/api/docs`

### Browser-Only WASM UI (Pyodide)

When FastAPI is running locally:
- `http://127.0.0.1:8000/static/wasm/index.html`

On GitHub Pages:
- Deploy via `.github/workflows/deploy-pages.yml`
- Open your Pages URL after workflow completion

## Usage

To generate multilinguality scores, use the following command:

```bash
python3 -m mlscores <identifier> [-l <language_code>...] [-f <format>] [-o <output_file>]
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `<identifier>` | One or more Wikidata (Wikibase) item identifiers (e.g., Q5) |
| `-l, --languages` | One or more language codes (e.g., en, fr, es, pt, ml) |
| `-m, --missing` | Show properties missing translation |
| `-f, --format` | Output format: `table` (default), `json`, or `csv` |
| `-o, --output` | Output file path (prints to console if not specified) |
| `--web` | Start the web interface server |
| `--host` | Web server host (default: 127.0.0.1) |
| `--port` | Web server port (default: 8000) |

### Examples

Basic usage:
```bash
python3 -m mlscores Q5 -l en fr es pt
```

Output (on October 12, 2024):
```bash
    Combined Language
Percentages for property
label and property value
         labels

┏━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Language ┃ Percentage ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━┩
│ en       │     99.40% │
│ fr       │     96.39% │
│ es       │     92.17% │
│ pt       │     71.08% │
└──────────┴────────────┘
```

With the `-m` (--missing) option to show properties and property values missing translations:

```bash
python3 -m mlscores Q5 -l en fr es pt -m
```

Output (on October 20, 2024):
```bash
                                                 Properties missing translation
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Languages ┃ Items                                                                                                               ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ fr        │ P11955, P12596                                                                                                      │
│ es        │ P5806, P9495, P11955, P10376, P7314, P12596, P8785                                                                  │
│ pt        │ P4527, P8419, P5247, P12596, P8785, P4212, P7807, P8814, P7329, P3222, P8168, P1256, P7497, P6839, P8895, P7775,    │
│           │ P6385, P6573, P9084, P7703, P5337, P5806, P8885, P5198, P4613, P7007, P6900, P2892, P11955, P9495, P12800, P3911,   │
│           │ P6058, P7314, P10757                                                                                                │
└───────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Output Formats

Export results in different formats:

```bash
# JSON output to console
python3 -m mlscores Q5 -l en fr -f json

# CSV output to file
python3 -m mlscores Q5 -l en fr -f csv -o results.csv

# JSON output to file
python3 -m mlscores Q5 Q10 -l en fr es -f json -o results.json
```

For more usage examples, see [USAGE.md](USAGE.md).

## Web Interface

`mlscores` includes a web interface powered by FastAPI. To use it, first install the web dependencies:

```bash
# Using pip extras
pip install ".[web]"

# Or using requirements file
pip install -r requirements-web.txt
```

Then start the web server:

```bash
python3 -m mlscores --web
```

The server starts at `http://127.0.0.1:8000` by default. You can customize the host and port:

```bash
python3 -m mlscores --web --host 0.0.0.0 --port 5000
```

### Browser-Only WASM Interface (Pyodide)

In addition to the FastAPI interface, mlscores now includes a browser-only UI powered by Pyodide/WebAssembly:

- URL when running FastAPI locally: `http://127.0.0.1:8000/static/wasm/index.html`
- Main file: `mlscores/web/static/wasm/index.html`
- It runs SPARQL queries directly from the browser and does not require FastAPI API routes.

This mode is useful for static hosting (for example GitHub Pages), with the caveat that browser CORS restrictions apply based on the selected SPARQL endpoint.

GitHub Actions workflow: `.github/workflows/deploy-pages.yml` deploys `mlscores/web/static/wasm/` to GitHub Pages.

### Web Interface Features

- **Interactive UI**: Access at `http://127.0.0.1:8000/`
- **REST API**:
  - `GET /api/health` - Health check endpoint
  - `POST /api/scores` - Calculate scores for multiple items
  - `GET /api/scores/{item_id}` - Calculate scores for a single item
- **API Documentation**:
  - Swagger UI: `http://127.0.0.1:8000/api/docs`
  - ReDoc: `http://127.0.0.1:8000/api/redoc`

## Output

The package generates three types of output:

* **Language Percentages for property labels**: A table showing the percentage of property labels available in each specified language.
* **Language Percentages for property value labels**: A table showing the percentage of property value labels available in each specified language.
* **Combined Language Percentages for property label and property value labels**: A table showing the combined percentage of property labels and property value labels available in each specified language.
* **Missing translations** (optional): A table showing list of properties and property values missing translation.

### Language Support

`mlscores` supports any language code returned by the target Wikibase labels (typically ISO 639-1/639-3 codes).

- For users: pass languages via `-l` in CLI or the `languages` field in the web UI/API.
- For maintainers: adding a *new language* generally does **not** require backend code changes; the score logic is language-agnostic.
- Optional UX enhancement: if you want a curated language picker, that would be a UI-only change.

## Features

* Supports multiple language codes
* Generates multilinguality scores for property and property value labels
* Provides combined scores for both label types
* Provides the list of properties and property labels missing translations
* Multiple output formats (table, JSON, CSV)
* Query caching for improved performance
* Web interface with REST API
* Custom Wikibase endpoint support

## Requirements

* Python 3.x
* `SPARQLWrapper` >= 2.0.0
* `rich` >= 4.1
* `tqdm` >= 4.65.0
* `urllib3` >= 1.26.15

Optional dependencies:
* For web interface: `fastapi`, `uvicorn`, `pydantic`
* For development: `pytest`, `pytest-cov`

## Onboarding and Extension

For new contributors and maintainers, see:
- `ONBOARDING.md`

It includes:
- local setup and test workflow
- project structure overview
- how to add or expose new languages
- how to add endpoint presets
- how to update shared SPARQL query builders used by FastAPI and WASM

## Contributing

Contributions are welcome! If you'd like to report an issue or submit a pull request, please visit our [GitHub repository](https://github.com/johnsamuelwrites/mlscores).

### Testing

For information on testing the `mlscores` package, including running the test suite, please see [TESTING.md](TESTING.md).

## Author
* John Samuel

## Licence
All code are released under GPLv3+ licence. The associated documentation and other content are released under [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).
