import uuid
from unittest.mock import patch

import pytest

from note.exceptions import NoteNotFoundError, NotUniqueIDError
from note.interfaces import INoteManager
from note.models import Note


def test_create_note(manager: INoteManager): # It will run the test on each manager(in-memory, json, sql, etc.)
    """Tests the creation of a single note."""
    assert len(manager.list_all_notes()) == 0, "Should start with no notes"
    note = manager.create_note("Test Title", "Test Content")
    assert note.title == "Test Title"
    assert note.content == "Test Content"
    assert len(manager.list_all_notes()) == 1, "Should have exactly one note after creation"

def test_list_all_notes(manager: INoteManager):
    """Tests listing multiple notes."""
    manager.create_note("Title 1", "Content 1")
    manager.create_note("Title 2", "Content 2")
    notes = manager.list_all_notes()
    assert len(notes) == 2
    assert {note.title for note in notes} == {"Title 1", "Title 2"}

def test_get_note_by_id(manager: INoteManager):
    """Tests retrieving a note by its full ID."""
    note = manager.create_note("Specific Title", "Content")
    retrieved_note = manager.get_note_by_id(note.id)
    assert retrieved_note is not None
    assert retrieved_note.id == note.id
    assert retrieved_note.title == "Specific Title"
    # Test getting a non-existent note
    non_existent_id = uuid.uuid4()
    assert manager.get_note_by_id(non_existent_id) is None

def test_update_note(manager: INoteManager):
    """Tests updating an existing note."""
    note = manager.create_note("Old Title", "Old Content")
    original_created_at = note.created_at
    original_updated_at = note.updated_at
    updated_note = manager.update_note(note.id, "New Title", "New Content")
    assert updated_note is not None
    assert updated_note.title == "New Title"
    assert updated_note.content == "New Content"
    assert updated_note.created_at == original_created_at, "Creation time should not change"
    assert updated_note.updated_at > original_updated_at, "Update time should be newer"

def test_delete_note(manager: INoteManager):
    """Tests deleting a note."""
    note1 = manager.create_note("To Delete", "...")
    note2 = manager.create_note("To Keep", "...")
    assert len(manager.list_all_notes()) == 2
    was_deleted = manager.delete_note(note1.id)
    assert was_deleted is True, "Delete operation should return True for success"
    assert len(manager.list_all_notes()) == 1
    assert manager.get_note_by_id(note1.id) is None
    assert manager.get_note_by_id(note2.id) is not None
    # Test deleting a non-existent note
    was_deleted_again = manager.delete_note(uuid.uuid4())
    assert was_deleted_again is False, "Delete should return False for non-existent note"

def test_search_notes(manager: INoteManager):
    """Tests the search functionality."""
    manager.create_note("Python is great", "I love programming in Python.")
    manager.create_note("Groceries", "Need to buy apples and bananas.")
    manager.create_note("Another Topic", "Completely different content, great!.")
    # Test search by title (case-insensitive)
    results_python = manager.search_notes("python")
    assert len(results_python) == 1
    assert results_python[0].title == "Python is great"
    # Test search that matches multiple notes
    results_great = manager.search_notes("great")
    assert len(results_great) == 2
    # Test search with no results
    results_js = manager.search_notes("javascript")
    assert len(results_js) == 0

def test_find_note_by_prefix_unique_and_not_found(manager: INoteManager):
    """Tests finding a note by unique prefix and handling not found cases."""
    note1 = manager.create_note("Note 1", "...")
    # Test unique match
    short_id = str(note1.id)[:8]
    found_note = manager.find_note_by_prefix(short_id)
    assert found_note.id == note1.id

    # Test no match
    with pytest.raises(NoteNotFoundError):
        manager.find_note_by_prefix("xxxxxxxx")

# This test!
# def test_find_note_by_prefix_NotUnique(manager: INoteManager)
# We can not create two Note instance with same prefix it to test! This is why we use uuid :)
