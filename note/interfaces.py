import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from note.models import Note


class INoteManager(ABC):
    """A Contract for all note managers(JSON, SQL, etc.)."""

    @abstractmethod
    def create_note(self, title: str, content: str) -> Note:
        """Creates a new note."""
        raise NotImplementedError

    @abstractmethod
    def get_note_by_id(self, note_id: uuid.UUID) -> Optional[Note]:
        """Retrieves a single note by its ID."""
        raise NotImplementedError

    @abstractmethod
    def list_all_notes(self) -> List[Note]:
        """Returns a list of all notes."""
        raise NotImplementedError

    @abstractmethod
    def update_note(self, note_id: uuid.UUID, title: str, content: str) -> Optional[Note]:
        """Updates an existing note."""
        raise NotImplementedError

    @abstractmethod
    def delete_note(self, note_id: uuid.UUID) -> bool:
        """Deletes a note by its ID."""
        raise NotImplementedError
