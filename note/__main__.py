import logging

from note.services import NoteManager


def setup_logging():
    """Logging setup."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("note_manager.log"), # file
            logging.StreamHandler() # console
        ]
    )
    logging.info("Logging has been configured.")

def main():
    """Application logic."""

    setup_logging()

    manager = NoteManager()
    note1 = manager.create_note("First Note", "This is a test.")
    manager.delete_note(note_id = note1.id)

if __name__ == "__main__":
    main()
