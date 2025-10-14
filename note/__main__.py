import logging

from note.cli import app


def setup_logging():
    """Logging setup."""

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

def main():
    """Main function of Note program."""
    setup_logging()
    app()

if __name__ == "__main__":
    main()
