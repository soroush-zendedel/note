import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from note.exceptions import NoteNotFoundError, NotUniqueIDError
from note.interfaces import INoteManager
from note.models import Note

logger = logging.getLogger(__name__)



class InMemoryNoteManager(INoteManager):
    """CRUD operations for Note Model(in-memory)."""

    def __init__(self) -> None:
        """Initializes with a dictionary."""
        self._notes: Dict[uuid.UUID, Note] = {}
        self._load_notes() # loads notes if exists any
        logger.info(f"{self.__class__.__name__} initialized.")

    def _load_notes(self) -> None:
        """Placeholder for loading notes."""
        pass # In-memory version doesn't need this

    def _save_notes(self) -> None:
        """Placeholder for saving notes."""
        pass # In-memory version doesn't need this

    def create_note(self, title: str, content: str) -> Note:
        """Creates a new note"""
        new_note = Note(title=title, content=content)
        self._notes[new_note.id] = new_note
        self._save_notes()
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
            logger.warning(f"Update failed: Note with ID {note_id} not found.")
            return None

        note_to_update.title = title
        note_to_update.content = content
        note_to_update.updated_at = datetime.now(timezone.utc)
        self._save_notes()
        logger.info(f"Note with ID {note_id} updated.")
        return note_to_update

    def delete_note(self, note_id: uuid.UUID) -> bool:
        """Deletes a note by its ID."""
        if note_id in self._notes:
            del self._notes[note_id]
            logger.info(f"Note with ID {note_id} deleted.")
            self._save_notes()
            return True

        logger.warning(f"Delete failed: Note with ID {note_id} not found.")
        return False

    def find_note_by_prefix(self, short_id: str) -> Note:
        """Finds a single note whose ID starts with the given prefix."""
        if not short_id:
            msg = "ID prefix cannot be empty."
            raise ValueError(msg)

        matches = [
            note for note in self._notes.values()
            if str(note.id).startswith(short_id)
        ]

        if len(matches) == 0:
            msg = f"No note found with ID prefix '{short_id}'."
            raise NoteNotFoundError(msg)

        if len(matches) > 1:
            full_ids = [str(note.id) for note in matches]
            raise NotUniqueIDError(matches=full_ids)

        return matches[0]

    def search_notes(self, query: str) -> List[Note]:
        """Searches for notes by their title or content(case-insensitive)."""

        if not query:
            return []

        lower_query = query.lower()

        # List comprehension to find all matching notes
        matches = [
            note for note in self._notes.values()
            if lower_query in note.title.lower() or lower_query in note.content.lower()
        ]

        return matches


class JsonNoteManager(InMemoryNoteManager):
    """JSON file storage for NoteManager."""
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.touch(exist_ok=True) # Check if a Json file already exists
        super().__init__() # We SHOULD call the parent for initializing in-memory version first

    def _load_notes(self) -> None:
        """Loads notes from the JSON file."""
        try:
            with self._db_path.open("r") as f:
                content = f.read()
                if not content:
                    return
                notes_data = json.loads(content)
                for note_data in notes_data:
                    note = Note(**note_data)
                    self._notes[note.id] = note
            logger.info(f"Loaded {len(self._notes)} notes from: \npath={self._db_path}.")
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning(f"Could not load notes from: \npath={self._db_path}.")
            self._notes = {}

    def _save_notes(self) -> None:
        """Saves notes to the JSON file"""
        notes_to_save = [note.model_dump(mode="json") for note in self._notes.values()]
        with self._db_path.open("w") as f:
            json.dump(notes_to_save, f, indent=4)
        logger.info(f"Saved {len(notes_to_save)} notes to {self._db_path}.")


if __name__ == "__main__":
    # Setting up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("notes.log"), # file
            logging.StreamHandler() # console
        ]
    )
    logging.info("Logging has been configured.")
    logger = logging.getLogger(__name__)

    #manager = NoteManager()
    manager = JsonNoteManager(Path("notes.json"))

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
