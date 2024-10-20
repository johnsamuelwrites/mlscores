#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import pytest
from mlscores.scores import (
    calculate_language_percentage,
    calculate_language_percentages,
    calculate_language_percentage_for_languages,
    get_missing_translations,
    get_properties_without_translations,
    get_properties_without_translations_in_languages,
    get_missing_translations_for_all_languages,
)


def test_empty_properties():
    properties = []
    language = "en"
    assert calculate_language_percentage(properties, language) == 0


def test_no_properties_in_language():
    properties = [("prop1", "value1", "fr"), ("prop2", "value2", "fr")]
    language = "en"
    assert calculate_language_percentage(properties, language) == 0


def test_all_properties_in_language():
    properties = [("prop1", "value1", "en"), ("prop2", "value2", "en")]
    language = "en"
    assert calculate_language_percentage(properties, language) == 100


def test_some_properties_in_language():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
    ]
    language = "en"
    assert round(calculate_language_percentage(properties, language), 2) == 66.67


def test_properties_with_duplicates():
    properties = [
        ("prop1", "value1", "en"),
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
    ]
    language = "en"
    assert calculate_language_percentage(properties, language) == 50


def test_properties_with_multiple_languages():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "es"),
    ]
    language = "en"
    assert round(calculate_language_percentage(properties, language), 2) == 33.33


def test_properties_with_none_language():
    properties = [("prop1", "value1", None), ("prop2", "value2", "fr")]
    language = "en"
    assert calculate_language_percentage(properties, language) == 0


def test_empty_properties():
    properties = []
    assert calculate_language_percentages(properties) == {}


def test_single_property():
    properties = [("prop1", "value1", "en")]
    expected_result = {"en": 100.0}
    assert calculate_language_percentages(properties) == expected_result


def test_multiple_properties_single_language():
    properties = [("prop1", "value1", "en"), ("prop2", "value2", "en")]
    expected_result = {"en": 100.0}
    assert calculate_language_percentages(properties) == expected_result


def test_multiple_properties_multiple_languages():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
    ]
    expected_result = {"en": 66.67, "fr": 33.33}
    assert calculate_language_percentages(properties) == pytest.approx(
        expected_result, rel=1e-2
    )


def test_properties_with_duplicates():
    properties = [
        ("prop1", "value1", "en"),
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
    ]
    expected_result = {"en": 50.0, "fr": 50.0}
    assert calculate_language_percentages(properties) == pytest.approx(
        expected_result, rel=1e-2
    )


def test_properties_with_multiple_languages_and_duplicates():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
        ("prop1", "value1", "en"),
    ]
    expected_result = {"en": 66.67, "fr": 33.33}
    assert calculate_language_percentages(properties) == pytest.approx(
        expected_result, rel=1e-2
    )


def test_properties_with_empty_language():
    properties = [("prop1", "value1", "")]
    expected_result = {"": 100.0}
    assert calculate_language_percentages(properties) == expected_result


def test_empty_properties():
    properties = []
    languages = ["en", "fr"]
    expected_result = {"en": 0, "fr": 0}
    assert (
        calculate_language_percentage_for_languages(properties, languages)
        == expected_result
    )


def test_single_property():
    properties = [("prop1", "value1", "en")]
    languages = ["en", "fr"]
    expected_result = {"en": 100.0, "fr": 0}
    assert (
        calculate_language_percentage_for_languages(properties, languages)
        == expected_result
    )


def test_multiple_properties_single_language():
    properties = [("prop1", "value1", "en"), ("prop2", "value2", "en")]
    languages = ["en", "fr"]
    expected_result = {"en": 100.0, "fr": 0}
    assert (
        calculate_language_percentage_for_languages(properties, languages)
        == expected_result
    )


def test_multiple_properties_multiple_languages():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
    ]
    languages = ["en", "fr"]
    expected_result = {"en": 66.67, "fr": 33.33}
    assert calculate_language_percentage_for_languages(
        properties, languages
    ) == pytest.approx(expected_result, rel=1e-2)


def test_languages_not_in_properties():
    properties = [("prop1", "value1", "en")]
    languages = ["fr", "es"]
    expected_result = {"fr": 0, "es": 0}
    assert (
        calculate_language_percentage_for_languages(properties, languages)
        == expected_result
    )


def test_properties_with_duplicates():
    properties = [
        ("prop1", "value1", "en"),
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
    ]
    languages = ["en", "fr"]
    expected_result = {"en": 50.0, "fr": 50.0}
    assert calculate_language_percentage_for_languages(
        properties, languages
    ) == pytest.approx(expected_result, rel=1e-2)


def test_empty_languages():
    properties = [("prop1", "value1", "en")]
    languages = []
    expected_result = {}
    assert (
        calculate_language_percentage_for_languages(properties, languages)
        == expected_result
    )


import pytest


def test_get_properties_without_translations():
    properties = [
        ("prop1", "value1", "en"),
        ("prop1", "value2", "fr"),
        ("prop2", "value3", "en"),
        ("prop3", "value4", "fr"),
    ]
    expected_result = {"en": {"prop3"}, "fr": {"prop2"}}
    assert get_properties_without_translations(properties) == expected_result


def test_get_properties_without_translations_empty_properties():
    properties = []
    expected_result = {}
    assert get_properties_without_translations(properties) == expected_result


def test_get_properties_without_translations_single_language():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "en"),
        ("prop3", "value3", "en"),
    ]
    expected_result = {}
    assert get_properties_without_translations(properties) == expected_result


def test_get_properties_without_translations_in_languages():
    properties = [
        ("prop1", "value1", "en"),
        ("prop1", "value2", "fr"),
        ("prop2", "value3", "en"),
        ("prop3", "value4", "fr"),
    ]
    languages = ["de", "es"]
    expected_result = {
        "de": {"prop1", "prop2", "prop3"},
        "es": {"prop1", "prop2", "prop3"},
    }
    assert (
        get_properties_without_translations_in_languages(properties, languages)
        == expected_result
    )


def test_get_properties_without_translations_in_languages_empty_properties():
    properties = []
    languages = ["de", "es"]
    expected_result = {}
    print(get_properties_without_translations_in_languages(properties, languages))
    assert (
        get_properties_without_translations_in_languages(properties, languages)
        == expected_result
    )


def test_get_properties_without_translations_in_languages_empty_languages():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
    ]
    languages = []
    expected_result = {}
    assert (
        get_properties_without_translations_in_languages(properties, languages)
        == expected_result
    )


def test_get_properties_without_translations_in_languages_single_language():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value2", "fr"),
        ("prop3", "value3", "en"),
    ]
    languages = ["en"]
    expected_result = {"en": set(["prop2"])}
    assert (
        get_properties_without_translations_in_languages(properties, languages)
        == expected_result
    )


import pytest


def test_get_missing_translations_empty_properties():
    properties = []
    languages = ["en", "fr"]
    assert get_missing_translations(properties, languages) == {}


def test_get_missing_translations_no_missing_translations():
    properties = [("prop1", "value1", "en"), ("prop1", "value1", "fr")]
    languages = ["en", "fr"]
    assert get_missing_translations(properties, languages) == {}


def test_get_missing_translations_missing_translations():
    properties = [("prop1", "value1", "en")]
    languages = ["en", "fr"]
    assert get_missing_translations(properties, languages) == {"prop1": {"fr"}}


def test_get_missing_translations_multiple_properties():
    properties = [("prop1", "value1", "en"), ("prop2", "value2", "fr")]
    languages = ["en", "fr"]
    assert get_missing_translations(properties, languages) == {
        "prop1": {"fr"},
        "prop2": {"en"},
    }


def test_get_missing_translations_for_all_languages_empty_properties():
    properties = []
    assert get_missing_translations_for_all_languages(properties) == {}


def test_get_missing_translations_for_all_languages_no_missing_translations():
    properties = [("prop1", "value1", "en"), ("prop1", "value1", "fr")]
    assert get_missing_translations_for_all_languages(properties) == {}


def test_get_missing_translations_for_all_languages_missing_translations():
    properties = [
        ("prop1", "value1", "en"),
        ("prop2", "value1", "en"),
        ("prop1", "value1", "fr"),
    ]
    assert get_missing_translations_for_all_languages(properties) == {"prop2": {"fr"}}


def test_get_missing_translations_for_all_languages_multiple_properties():
    properties = [("prop1", "value1", "en"), ("prop2", "value2", "fr")]
    assert get_missing_translations_for_all_languages(properties) == {
        "prop1": {"fr"},
        "prop2": {"en"},
    }
