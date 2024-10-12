import pytest
from mlscores.query import get_properties_and_values


def test_get_properties_and_values_success():
    item_id = "Q5"
    result = get_properties_and_values(item_id)
    assert result is not None


def test_get_properties_and_values_invalid_item_id():
    item_id = " invalid"
    result = get_properties_and_values(item_id)
    assert result is None
