import pytest

from note.exceptions import NotUniqueIDError


def test_not_unique_id_error_stores_matches():
    """
    Tests that the NotUniqueIDError correctly stores the list of matching IDs.
    """
    sample_ids = [
        "a1b2c3d4-0001-0000-0000-000000000000",
        "a1b2c3d4-0002-0000-0000-000000000000",
    ]

    with pytest.raises(NotUniqueIDError) as excinfo:
        raise NotUniqueIDError(matches=sample_ids)

    assert excinfo.value.matches == sample_ids
    assert "a1b2c3d4-0001" in str(excinfo.value)
    assert "a1b2c3d4-0002" in str(excinfo.value)
