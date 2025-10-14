from pathlib import Path

import pytest

from note.interfaces import INoteManager
from note.services import InMemoryNoteManager, JsonNoteManager

# We need to make an instance for managers, So we can test them! We do it HERE!
# for example, we write 7 test for testing, and if we are using 2 manager if will do job for both of them,
# So 14 tests will run!

@pytest.fixture
def in_memory_manager() -> InMemoryNoteManager:
    """in-memory manager instance for tests"""
    return InMemoryNoteManager()

@pytest.fixture
def json_manager(tmp_path: Path) -> JsonNoteManager:
    """
    JsonNoteManager instance for tests.
    tmp_path: built-in pytest fixture, It provides a temporary directory.
    """
    temp_db_file = tmp_path / "test_notes.json"
    return JsonNoteManager(db_path=temp_db_file)

@pytest.fixture(params=["in_memory", "json"])
def manager(request, in_memory_manager, json_manager) -> INoteManager:
    """We SHOULD choose a manager for each type(In-Memory or Json)"""
    if request.param == "json":
        return json_manager
    # elif request.param == "sql":
    #     return sql_manager
    return in_memory_manager

# @pytest.fixture
# def sql_manager(database_url: str) -> SqlNoteManager:
#     """
#     Provides a SqlNoteManager instance
#     """
#     DATABASE_URL = database_url
#     return SqlNoteManager(DATABASE_URL=DATABASE_URL)

