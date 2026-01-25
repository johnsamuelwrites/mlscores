#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import os

import pytest

# Add the parent directory (project root) to sys.path so that pytest can find my_package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_properties():
    """Sample properties for testing."""
    return [
        ("prop1", "value1", "en"),
        ("prop1", "value1", "fr"),
        ("prop2", "value2", "en"),
        ("prop3", "value3", "es"),
    ]


@pytest.fixture
def sample_sparql_response():
    """Sample SPARQL query response."""
    return {
        "results": {
            "bindings": [
                {
                    "property": {"value": "http://www.wikidata.org/prop/direct/P31"},
                    "value": {"value": "http://www.wikidata.org/entity/Q5"},
                },
                {
                    "property": {"value": "http://www.wikidata.org/prop/direct/P21"},
                    "value": {"value": "http://www.wikidata.org/entity/Q6581097"},
                },
            ]
        }
    }


@pytest.fixture
def sample_property_labels_response():
    """Sample property labels SPARQL response."""
    return {
        "results": {
            "bindings": [
                {
                    "p": {"value": "http://www.wikidata.org/prop/direct/P31"},
                    "propertyLabel": {"value": "instance of"},
                    "propertyLabelLang": {"value": "en"},
                },
                {
                    "p": {"value": "http://www.wikidata.org/prop/direct/P31"},
                    "propertyLabel": {"value": "nature de l'élément"},
                    "propertyLabelLang": {"value": "fr"},
                },
            ]
        }
    }


@pytest.fixture
def sample_value_labels_response():
    """Sample value labels SPARQL response."""
    return {
        "results": {
            "bindings": [
                {
                    "v": {"value": "http://www.wikidata.org/entity/Q5"},
                    "valueLabel": {"value": "human"},
                    "valueLabelLang": {"value": "en"},
                },
                {
                    "v": {"value": "http://www.wikidata.org/entity/Q5"},
                    "valueLabel": {"value": "être humain"},
                    "valueLabelLang": {"value": "fr"},
                },
            ]
        }
    }
