import importlib.resources  # No Relative path should use for Pypi, This solves the problem.
import uuid

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from note.services import JsonNoteManager

templates_path = str(importlib.resources.files("note").joinpath("templates")) # No Relative path should use for Pypi.

def create_app(manager: JsonNoteManager) -> FastAPI:
    """Main function to create the FastAPI application."""

    app = FastAPI(title="Note Manager Web")

    # This line solves `python -m note` no template found problem, if user install Note App from Pypi
    templates = Jinja2Templates(directory=templates_path)

    @app.get("/")
    async def root():
        """Redirects the root URL to /notes."""
        return RedirectResponse(url="/notes")

    @app.get("/notes")
    async def list_notes(request: Request):
        """Lists all notes."""
        all_notes = manager.list_all_notes()

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "notes": all_notes}
        )

    @app.get("/notes/create")
    async def create_note_form(request: Request):
        """Displays the form to create a new note."""
        return templates.TemplateResponse("create_note.html", {"request": request})

    @app.post("/notes/create")
    async def create_note(
        title: str = Form(...),
        content: str = Form(...)
    ):
        """submit button of the creation form"""
        manager.create_note(title=title, content=content)
        return RedirectResponse(url="/notes", status_code=303) # status_code 303 is important for POST redirects

    @app.get("/notes/{note_id}")
    async def read_note(request: Request, note_id: uuid.UUID):
        """Note details."""
        note = manager.get_note_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        return templates.TemplateResponse(
            "note_detail.html",
            {"request": request, "note": note}
        )

    @app.post("/notes/{note_id}/edit")
    async def update_note(note_id: uuid.UUID, title: str = Form(...), content: str = Form(...)):
        """Edit button process"""
        updated_note = manager.update_note(note_id=note_id, title=title, content=content)
        if not updated_note:
            raise HTTPException(status_code=404, detail="Note not found for update")
        return RedirectResponse(url=f"/notes/{note_id}", status_code=303)

    @app.post("/notes/{note_id}/delete")
    async def delete_note(note_id: uuid.UUID):
        """Delete button process."""
        success = manager.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found for deletion")
        return RedirectResponse(url="/notes", status_code=303)

    return app
