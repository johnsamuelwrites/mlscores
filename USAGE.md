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


### Special Cases

* Generate multilinguality scores for a Wikidata property (e.g., P31):
```bash
python3 -m mlscores P31 -l en fr es
```

* Generate multilinguality scores for a Wikidata item with a special identifier (e.g., Q2012):
```bash
python3 -m mlscores Q2012
```
