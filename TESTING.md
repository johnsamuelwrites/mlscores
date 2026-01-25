# Testing and Code Coverage

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Running Tests](#running-tests)
   - [Using `pytest`](#using-pytest)
   - [Running Specific Tests](#running-specific-tests)
   - [Test Modules](#test-modules)
4. [Code Coverage](#code-coverage)
   - [Using `pytest-cov`](#using-pytest-cov)
5. [Test Fixtures](#test-fixtures)
6. [Troubleshooting](#troubleshooting)
7. [Conclusion](#conclusion)

---

## 1. Introduction
This documentation provides developers with guidelines on how to run tests for the `mlscores` Python package and measure code coverage using `pytest` and `pytest-cov`.

## 2. Prerequisites
Before you can run the tests and check code coverage, ensure that you have the following installed:

- Python 3.x
- `pytest`
- `pytest-cov`

You can install the required packages using one of the following methods:

```bash
# Using pip with extras
pip install ".[dev]"

# Using requirements file
pip install -r requirements-dev.txt

# Or install directly
pip install pytest pytest-cov
```

## 3. Running Tests

### Using `pytest`
To run all tests in the project, navigate to the root directory (where `setup.py` is located) and run:

```bash
pytest
```

This command will automatically discover and execute all test files that match the naming pattern `test_*.py` or `*_test.py` located in the `tests/` folder.

### Running Specific Tests
You can also run specific tests by specifying the test file or function.

- To run a specific test file:
  ```bash
  pytest tests/test_scores.py
  ```

- To run a specific test function within a test file:
  ```bash
  pytest tests/test_scores.py::test_all_properties_in_language
  ```

- To run a specific test class:
  ```bash
  pytest tests/test_display.py::TestPrintLanguagePercentages
  ```

Use the `-v` option for verbose output, which provides more detailed information about the tests being executed:

```bash
pytest -v
```

### Test Modules

The test suite includes the following test modules:

| Module | Description |
|--------|-------------|
| `test_scores.py` | Tests for multilinguality score calculations |
| `test_query.py` | Tests for SPARQL query functions |
| `test_display.py` | Tests for display and output formatting |
| `test_main.py` | Tests for CLI and main module functions |

Run all tests with verbose output:
```bash
pytest -v tests/
```

## 4. Code Coverage

### Using `pytest-cov`
To check code coverage while running your tests, you need to use the `pytest-cov` plugin. This tool will give you insights into which parts of your code are covered by tests.

1. **Run Tests with Coverage**
   Execute the following command to run tests and measure code coverage:

   ```bash
   pytest --cov=mlscores
   ```

2. **View Coverage Report**
   After running the tests, `pytest-cov` will display a summary of the coverage in the terminal. You will see output similar to this:

   ```
   ---------- coverage: platform linux, python 3.10.12-final-0 ----------
   Name                       Stmts   Miss  Cover
   ----------------------------------------------
   mlscores/__init__.py           1      0   100%
   mlscores/__main__.py          85     20    76%
   mlscores/cache.py             45     10    78%
   mlscores/constants.py         12      0   100%
   mlscores/display.py           35      5    86%
   mlscores/endpoint.py          25      8    68%
   mlscores/formatters.py        60     15    75%
   mlscores/query.py             67     10    85%
   mlscores/scores.py            39      2    95%
   ----------------------------------------------
   TOTAL                        369     70    81%
   ```

3. **Generate a Coverage Report in HTML Format**
   For a more detailed view, you can generate an HTML report:

   ```bash
   pytest --cov=mlscores --cov-report=html
   ```

   This command will create an `htmlcov/` directory in your project root containing the HTML coverage report. Open `htmlcov/index.html` in your browser to view the coverage details interactively.

4. **Coverage with Missing Lines**
   To see which specific lines are missing coverage:

   ```bash
   pytest --cov=mlscores --cov-report=term-missing
   ```

## 5. Test Fixtures

The test suite uses pytest fixtures defined in `tests/conftest.py` to provide common test data and mock objects. Key fixtures include:

| Fixture | Description |
|---------|-------------|
| `sample_properties` | Sample property data for testing score calculations |
| `sample_property_labels` | Sample property label data with language information |
| `sample_value_labels` | Sample value label data with language information |
| `mock_sparql_wrapper` | Mock for SPARQLWrapper to avoid network calls |

Example usage of fixtures in tests:

```python
def test_calculate_scores(sample_properties, sample_property_labels):
    # Use fixtures in your test
    result = calculate_language_percentages(sample_properties)
    assert result is not None
```

## 6. Troubleshooting

### Common Issues

1. **Import Errors**
   If you encounter import errors, ensure the package is installed in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Missing Dependencies**
   Install all required dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
   Or separately:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov
   ```

3. **Test Discovery Issues**
   Ensure test files follow the naming convention `test_*.py` and are located in the `tests/` directory.

4. **Mock-related Failures**
   Tests use `unittest.mock` to avoid making actual network requests. If tests fail with network-related errors, check that mocks are properly configured.

## 7. Conclusion

Regular testing ensures code quality and prevents regressions. Run the test suite before submitting pull requests:

```bash
# Run all tests with coverage
pytest --cov=mlscores --cov-report=term-missing -v

# Generate HTML coverage report
pytest --cov=mlscores --cov-report=html
```

For questions or issues with testing, please open an issue on the [GitHub repository](https://github.com/johnsamuelwrites/mlscores).
