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
* `<missing>` (optional): show properties missing translation.  

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

and with the -m (--missing) option, it shows the properties and property values missing translations.

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

For more usage examples, see [USAGE.md](USAGE.md).

## Output

The package generates three types of output:

* **Language Percentages for property labels**: A table showing the percentage of property labels available in each specified language.
* **Language Percentages for property value labels**: A table showing the percentage of property value labels available in each specified language.
* **Combined Language Percentages for property label and property value labels**: A table showing the combined percentage of property labels and property value labels available in each specified language.
* **Missing translations** (optional) : A table showing list of properties and property values missing translation. 

## Features

* Supports multiple language codes
* Generates multilinguality scores for property and property value labels
* Provides combined scores for both label types
* Provides the list of properties and property labels missing translations

## Requirements

* Python 3.x
* `argparse` library (included in Python 3.x)
* `rich`
* `SPARQLWrapper`

## Contributing

Contributions are welcome! If you'd like to report an issue or submit a pull request, please visit our [GitHub repository](https://github.com/johnsamuelwrites/mlscores).

### Testing

For information on testing the `mlscores` package, including running the test suite, please see [TESTING.md](TESTING.md).

## Author
* John Samuel

## Licence
All code are released under GPLv3+ licence. The associated documentation and other content are released under [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/).
