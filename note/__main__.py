import logging
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from note.exceptions import NoteNotFoundError, NotUniqueIDError
from note.services import JsonNoteManager
from note.web_app import create_app


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

app = typer.Typer(help="Personal Note Manager - A Simple Notebook!")

console = Console()

DB_PATH = Path("notes.json")
manager = JsonNoteManager(DB_PATH)


@app.command()
def create(
    title: str = typer.Option(..., "--title", "-t", prompt="Enter note title"),
    content: str = typer.Option(..., "--content", "-c", prompt="Enter note content")
) -> None:
    """Create a new note interactively."""
    try:
        note = manager.create_note(title=title, content=content)
        console.print(f"Note created with ID: [bold green]{note.id}[/bold green]")
    except Exception as e:
        console.print(f"Error creating note: [bold red]{e}[/bold red]")

@app.command()
def delete(
    short_id: str = typer.Argument(..., help="Just enter first characters of Id.")
) -> None:
    """Delete a note."""
    try:
        note_to_delete = manager.find_note_by_prefix(short_id)

        console.print(f"Found note: '[bold]{note_to_delete.title}[/bold]' (ID: {note_to_delete.id})")
        if not typer.confirm("Are you sure you want to delete this note?"):
            raise typer.Abort()

        if manager.delete_note(note_to_delete.id):
            console.print("Note deleted.")
        else:
            console.print("Sorry, There is a problem to delete this note.")

    except NoteNotFoundError as e:
        console.print(f"Error: {e}")
    except NotUniqueIDError as e:
        console.print(f"Error: Not Unique ID prefix '{short_id}'.")
        console.print("More than one note found.")
        for full_id in e.matches:
            console.print(f"  - {full_id}")
    except ValueError as e:
        console.print(f"Error: {e}")

@app.command(name="list")
def list_notes() -> None:
    """List all notes."""
    notes = manager.list_all_notes()
    if not notes:
        console.print("No notes found.")
        return

    table = Table("ID", "Title", "Created", "Updated")
    for note in notes:
        table.add_row(
            f"[bold blue]{note.id!s}[/bold blue]",
            f"[bold purple]{note.title!s}[/bold purple]",
            f"[bold green]{note.created_at.strftime('%Y-%m-%d %H:%M')!s}[/bold green]",
            f"[bold yellow]{note.updated_at.strftime('%Y-%m-%d %H:%M')!s}[/bold yellow]"
        )
    console.print(table)

@app.command()
def search(
    query: str = typer.Argument(..., help="The text to search for it (titles and contents).")
) -> None:
    """Searche notes by title or content."""
    console.print(f"Searching for notes containing: '[bold yellow]{query}[/bold yellow]'")

    results = manager.search_notes(query)

    if not results:
        console.print("No matching notes found.")
        return

    # Display the results in a table.
    table = Table("ID", "Title", "Content Snippet")
    for note in results:
        content_length = 75 # How many character must display?
        snippet = (note.content[:content_length] + "...") if len(note.content) > content_length else note.content
        table.add_row(
            str(note.id)[:8], # only the first 8 characters of the ID
            note.title,
            snippet.replace("\n", " ") # Newlines breaks the table, so we remove them
        )

    console.print(table)

@app.command(name="show")
def show_note(
    short_id: str = typer.Argument(..., help="Just enter first characters of Id.")
) -> None:
    """Show details of a specific note."""
    try:
        note = manager.find_note_by_prefix(short_id) # Find by short Id


        content_display = Text()
        content_display.append(f"ID: {note.id}\n", style="cyan")
        content_display.append(f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
        content_display.append(f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n", style="dim")
        content_display.append("─" * 40 + "\n", style="dim") # A separator line
        content_display.append(note.content)

        panel = Panel(
            content_display,
            title=f"[bold yellow]{note.title}[/bold yellow]",
            border_style="green",
            expand=True,
            padding=(1, 2)
        )

        console.print(panel)

    except NoteNotFoundError as e:
        console.print(f"Error: {e}", style="bold red")
    except NotUniqueIDError as e:
        console.print(f"Error: Not Unique ID prefix '{short_id}'.", style="bold red")
        console.print("More than one note found.")
        for full_id in e.matches:
            console.print(f"  - {full_id}")
    except ValueError as e:
        console.print(f"Error: {e}", style="bold red")

@app.command(name="update")
def update_note(
    short_id: str = typer.Argument(..., help="Just enter first characters of Id.")
) -> None:
    """Update an existing note."""
    try:
        note = manager.find_note_by_prefix(short_id)

        console.print(f"Updating note: '[bold]{note.title}[/bold]'")

        new_title = typer.prompt("New title", default=note.title) # Get the new title

        new_content = typer.edit(text=note.content) # multi-line text


        if new_content is None: # if No Changes made
            console.print("No changes.")
            new_content = note.content
            return

        updated_note = manager.update_note(
            note_id=note.id,
            title=new_title,
            content=new_content
        )

        if updated_note:
            console.print("Note updated!", style="bold green")
        else:
            console.print("Sorry, There is a problem.", style="bold red")

    except NoteNotFoundError as e:
        console.print(f"Error: {e}", style="bold red")
    except NotUniqueIDError as e:
        console.print(f"Error: Not Unique ID prefix '{short_id}'.", style="bold red")
        console.print("More than one note found.")
        for full_id in e.matches:
            console.print(f"  - {full_id}")
    except ValueError as e:
        console.print(f"Error: {e}", style="bold red")

@app.command(name="web")
def run_web_app(
    host: str = typer.Option("127.0.0.1", help="Server Address."),
    port: int = typer.Option(8000, help="Server Port.")
) -> None:
    """Launches the web application."""
    console.print(f"Starting web server at [bold green]http://{host}:{port}[/bold green]")
    console.print("Press CTRL+C to stop.")

    web_app = create_app()

    # Run the server with uvicorn
    uvicorn.run(web_app, host=host, port=port)

if __name__ == "__main__":
    setup_logging()
    app()
