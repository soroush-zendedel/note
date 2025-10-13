class NoteNotFoundError(Exception):
    """Raised when a note is not found."""
    pass

class NotUniqueIDError(Exception):
    """Raised when multiple notes found."""
    def __init__(self, matches: list[str]):
        self.matches = matches
        super().__init__(f"ID is not unique. Found matches: {matches}")
