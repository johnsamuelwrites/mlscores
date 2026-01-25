# Release Notes

## v0.1.0 - Initial Release

First public release of mlscores, a multilinguality score calculator for Wikidata and Wikibase items.

### Features

**Core Functionality**
- Calculate multilinguality scores for Wikidata items (Q-items) and properties (P-items)
- Analyze property labels, value labels, qualifiers, and references
- Support for multiple items and languages in a single query
- Identify missing translations with the `-m` flag

**Output Formats**
- Table output (default) - Rich formatted tables in terminal
- JSON output - Machine-readable format for integration
- CSV output - Spreadsheet-compatible format
- File export with `-o` option

**Web Interface**
- Modern, responsive UI with dark/light theme support
- Interactive score calculation with visual progress bars
- Clickable links to Wikidata entities
- REST API with OpenAPI documentation
- Endpoint selection (Wikidata, Commons, custom)

**Architecture**
- Query caching for improved performance
- Configurable SPARQL endpoints for custom Wikibase instances
- Type hints throughout codebase
- Comprehensive test suite (73 tests)

### Installation

```bash
pip install .                  # Core
pip install ".[web]"           # With web interface
pip install ".[dev]"           # With dev tools
```

### Quick Start

```bash
# CLI usage
python -m mlscores Q42 -l en fr es

# Start web server
python -m mlscores --web
```

### Documentation

- [README.md](README.md) - Overview and installation
- [USAGE.md](USAGE.md) - Detailed usage examples
- [TESTING.md](TESTING.md) - Testing guide

### Requirements

- Python 3.8+
- SPARQLWrapper >= 2.0.0
- rich >= 4.1
- tqdm >= 4.65.0

### License

GPL-3.0-or-later
