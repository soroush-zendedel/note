import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from note.models import Note

logger = logging.getLogger(__name__)



class NoteManager:
    """CRUD operations"""

    def __init__(self) -> None:
        """Initializes with a dictionary."""
        self._notes: Dict[uuid.UUID, Note] = {}
        logger.info("NoteManager initialized successfully.")

    def create_note(self, title: str, content: str) -> Note:
        """Creates a new note"""
        new_note = Note(title=title, content=content)
        self._notes[new_note.id] = new_note
        # Use INFO for successful, routine operations.
        logger.info(f"Note created with ID: {new_note.id}")
        return new_note

    def get_note_by_id(self, note_id: uuid.UUID) -> Optional[Note]:
        """Retrieves a single note by its ID."""
        return self._notes.get(note_id)

    def list_all_notes(self) -> List[Note]:
        """Returns a list of all notes."""
        return list(self._notes.values())

    def update_note(self, note_id: uuid.UUID, title: str, content: str) -> Optional[Note]:
        """Updates an existing note."""
        note_to_update = self.get_note_by_id(note_id)

        if not note_to_update:
            # Use WARNING for expected issues that don't crash the app.
            logger.warning(f"Update failed: Note with ID {note_id} not found.")
            return None

        note_to_update.title = title
        note_to_update.content = content
        note_to_update.updated_at = datetime.now(timezone.utc)

        logger.info(f"Note with ID {note_id} successfully updated.")
        return note_to_update

    def delete_note(self, note_id: uuid.UUID) -> bool:
        """Deletes a note by its ID."""
        if note_id in self._notes:
            del self._notes[note_id]
            logger.info(f"Note with ID {note_id} deleted.")
            return True

        logger.warning(f"Delete failed: Note with ID {note_id} not found.")
        return False


if __name__ == "__main__":
    manager = NoteManager()

    note1 = manager.create_note("Shopping", "1. Milk\n2. Bread")
    note2 = manager.create_note("Meeting", "Meeting with team at 04:00PM")

    manager.update_note(
        note_id=note1.id,
        title="Shopping",
        content="1. Milk\n2. Bread\n3. Egg"
    )

    non_existent_id = uuid.uuid4()
    manager.update_note(
        note_id=non_existent_id,
        title="Delete me!",
        content="Id is not a valid note."
    )

    manager.delete_note(note2.id)
