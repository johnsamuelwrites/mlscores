## Usage Examples

### Basic Usage

* Generate multilinguality scores for a single Wikidata item (Q5) in English:
```bash
python3 -m mlscores Q5 -l en
```

* Generate multilinguality scores for a single Wikidata item (Q5) in multiple languages (English, French, and Spanish):
```bash
python3 -m mlscores Q5 -l en fr es
```

### Multiple Identifiers

* Generate multilinguality scores for multiple Wikidata items (Q5, Q10, and Q15) in a single language (English):
```bash
python3 -m mlscores Q5 Q15 -l en
```

* Generate multilinguality scores for multiple Wikidata items (Q5, Q10, and Q15) in multiple languages (English, French, and Spanish):
```bash
python3 -m mlscores Q5 Q10 Q15 -l en fr es
```

### Missing Translations

* Generate a list of properties and property values missing translations in multiple languages (English, French, and Spanish) for Wikidata item Q5:

```bash
python3 -m mlscores Q5 -l en fr es -m
```

* Generate a list of properties and property values missing translations in multiple languages (English, French, and Spanish) for multiple Wikidata items (Q5, Q10, and Q15):

```bash
python3 -m mlscores Q5 Q10 Q15 -l en fr es -m
```

### Output Formats

`mlscores` supports three output formats: `table` (default), `json`, and `csv`.

#### Table Output (Default)

```bash
python3 -m mlscores Q5 -l en fr es
```

#### JSON Output

* Output JSON to console:
```bash
python3 -m mlscores Q5 -l en fr es -f json
```

* Output JSON to file:
```bash
python3 -m mlscores Q5 -l en fr es -f json -o results.json
```

Example JSON output:
```json
[
  {
    "item_id": "Q5",
    "property_label_percentages": {
      "en": 99.5,
      "fr": 96.2,
      "es": 92.1
    },
    "value_label_percentages": {
      "en": 98.8,
      "fr": 95.5,
      "es": 91.0
    },
    "combined_percentages": {
      "en": 99.1,
      "fr": 95.8,
      "es": 91.5
    }
  }
]
```

#### CSV Output

* Output CSV to console:
```bash
python3 -m mlscores Q5 -l en fr es -f csv
```

* Output CSV to file:
```bash
python3 -m mlscores Q5 -l en fr es -f csv -o results.csv
```

Example CSV output:
```csv
item_id,type,en,fr,es
Q5,property_labels,99.5,96.2,92.1
Q5,value_labels,98.8,95.5,91.0
Q5,combined,99.1,95.8,91.5
```

### Including Missing Translation Details in JSON

When using JSON format with the `-m` flag, missing translations are included:

```bash
python3 -m mlscores Q5 -l en fr es -f json -m
```

Example output:
```json
[
  {
    "item_id": "Q5",
    "property_label_percentages": {"en": 99.5, "fr": 96.2, "es": 92.1},
    "value_label_percentages": {"en": 98.8, "fr": 95.5, "es": 91.0},
    "combined_percentages": {"en": 99.1, "fr": 95.8, "es": 91.5},
    "missing_property_translations": {
      "fr": ["P11955", "P12596"],
      "es": ["P5806", "P9495", "P11955"]
    },
    "missing_value_translations": {
      "fr": ["Q12345"],
      "es": ["Q12345", "Q67890"]
    }
  }
]
```

### Special Cases

* Generate multilinguality scores for a Wikidata property (e.g., P31):
```bash
python3 -m mlscores P31 -l en fr es
```

* Generate multilinguality scores for a Wikidata item with a special identifier (e.g., Q2012):
```bash
python3 -m mlscores Q2012
```

### Web Interface

`mlscores` includes a web interface for interactive use and REST API access.

#### Prerequisites

Install web dependencies before using the web interface:

```bash
# Using pip with extras
pip install ".[web]"

# Or using requirements file
pip install -r requirements-web.txt
```

#### Starting the Web Server

* Start with default settings (localhost:8000):
```bash
python3 -m mlscores --web
```

* Start with custom host and port:
```bash
python3 -m mlscores --web --host 0.0.0.0 --port 5000
```

#### Browser-Only WASM UI (Pyodide)

A browser-only interface is available in addition to the FastAPI-backed UI:

- Local URL (served by FastAPI static files): `http://127.0.0.1:8000/static/wasm/index.html`
- Static file path: `mlscores/web/static/wasm/index.html`
- This mode executes scoring in-browser via Pyodide and directly queries a SPARQL endpoint.

This is suitable for static hosting scenarios such as GitHub Pages, subject to endpoint CORS policies.

#### Accessing the Web Interface

Once the server is running:

* **Interactive UI**: Open `http://127.0.0.1:8000/` in your browser
* **API Documentation (Swagger)**: `http://127.0.0.1:8000/api/docs`
* **API Documentation (ReDoc)**: `http://127.0.0.1:8000/api/redoc`

#### REST API Endpoints

**Health Check**
```bash
curl http://127.0.0.1:8000/api/health
```

**Get Scores for a Single Item**
```bash
curl "http://127.0.0.1:8000/api/scores/Q5?languages=en,fr,es"
```

**Get Scores for Multiple Items**
```bash
curl -X POST http://127.0.0.1:8000/api/scores \
  -H "Content-Type: application/json" \
  -d '{"item_ids": ["Q5", "Q10"], "languages": ["en", "fr", "es"], "include_missing": true}'
```

### Batch Processing

For processing many items, you can combine shell scripting with `mlscores`:

```bash
# Process a list of items and save to JSON
for item in Q5 Q10 Q15 Q20; do
  python3 -m mlscores $item -l en fr es -f json -o "${item}_scores.json"
done
```

Or process all items in a single command:
```bash
python3 -m mlscores Q5 Q10 Q15 Q20 -l en fr es -f json -o all_scores.json
```

### Tips

1. **Performance**: Processing items with many properties may take longer due to SPARQL query complexity. Results are cached to improve performance on repeated queries.

2. **Language Codes**: Use standard ISO 639-1 language codes (e.g., `en`, `fr`, `es`, `de`, `zh`, `ja`).

3. **Rate Limiting**: The Wikidata Query Service has rate limits. If you encounter errors, try reducing the number of concurrent requests.

4. **Output Files**: When using `-o` with an existing file, the file will be overwritten.
