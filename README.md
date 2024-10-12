# mlscores
Multilinguality score of Wikidata (or Wikibase) items


## Overview

This package generates multilinguality scores for Wikidata (Wikibase) items, specifically for property and property value labels. The scores represent the percentage of labels available in a given language.

## Installation

For installation, please follow these steps:

1. Make sure you have Python 3.x and pip installed on your system.
2. Clone the repository or download the source code.
3. Navigate to the directory containing the source code.
4. Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

This will install all the necessary dependencies listed in the `requirements.txt` file.

## Usage

To generate multilinguality scores, use the following command:

```bash
python3 -m mlscores <identifier> [-l <language_code>...]
```

* `<identifier>`: One or more Wikidata (Wikibase) item identifiers (e.g., Q5)
* `<language_code>`: One or more language codes (e.g., en, fr, es, pt, ml)

Example:
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

For more usage examples, see [USAGE.md](USAGE.md).

## Output

The package generates three types of output:

* **Language Percentages for property labels**: A table showing the percentage of property labels available in each specified language.
* **Language Percentages for property value labels**: A table showing the percentage of property value labels available in each specified language.
* **Combined Language Percentages for property label and property value labels**: A table showing the combined percentage of property labels and property value labels available in each specified language.

## Features

* Supports multiple language codes
* Generates multilinguality scores for property and property value labels
* Provides combined scores for both label types

## Requirements

* Python 3.x
* `argparse` library (included in Python 3.x)
* `rich`
* `SPARQLWrapper`

## Contributing

Contributions are welcome! If you'd like to report an issue or submit a pull request, please visit our [GitHub repository](https://github.com/johnsamuelwrites/mlscores).

## Author
* John Samuel

## Licence
All code are released under GPLv3+ licence. The associated documentation and other content are released under [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).
