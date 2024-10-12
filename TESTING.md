# Testing and Code Coverage

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Running Tests](#running-tests)
   - [Using `pytest`](#using-pytest)
   - [Running Specific Tests](#running-specific-tests)
4. [Code Coverage](#code-coverage)
   - [Using `pytest-cov`](#using-pytest-cov)
5. [Troubleshooting](#troubleshooting)
6. [Conclusion](#conclusion)

---

## 1. Introduction
This documentation provides developers with guidelines on how to run tests for the `mlscores` Python package and measure code coverage using `pytest` and `pytest-cov`. 

## 2. Prerequisites
Before you can run the tests and check code coverage, ensure that you have the following installed:

- Python 3.x
- `pytest`
- `pytest-cov`

You can install the required packages using the following command:

```bash
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

Use the `-v` option for verbose output, which provides more detailed information about the tests being executed:

```bash
pytest -v
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
     Name                   Stmts   Miss  Cover
     ------------------------------------------
     mlscores/__init__.py       0      0   100%
     mlscores/__main__.py      47     47     0%
     mlscores/display.py       10     10     0%
     mlscores/query.py         67     38    43%
     mlscores/scores.py        39      2    95%
     ------------------------------------------
     TOTAL                    163     97    40%
     
   ```

3. **Generate a Coverage Report in HTML Format**
   For a more detailed view, you can generate an HTML report:

   ```bash
   pytest --cov=mlscores --cov-report=html
   ```

   This command will create an `htmlcov/` directory in your project root containing the HTML coverage report. Open `htmlcov/index.html` in your browser to view the coverage details interactively.

