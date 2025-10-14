import importlib.resources  # No Relative path should use for Pypi, This solves the problem.
import uuid
from functools import lru_cache

from fastapi import (
    Depends,  # We need depends so CLI and Web can work on the same json file at the same time for HotReload
    FastAPI,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from note.interfaces import INoteManager
from note.services import InMemoryNoteManager, JsonNoteManager
from settings import StorageType, settings

templates_path = str(importlib.resources.files("note").joinpath("templates")) # No Relative path should use for Pypi.
templates = Jinja2Templates(directory=templates_path)

# Instead of using Global variables, We should Singleton:
@lru_cache(maxsize=1) # Load and cache just one time in each programs start-up.
def get_singleton_manager() -> INoteManager:
    """
    What we are actually doing? :)
    We only need to load In-Memory or SQL manager once! So we cache them, by this function.
    """
    # After SQL implementation we should uncomment these:
    # if settings.STORAGE_TYPE == StorageType.SQL:
    #     return SQLNoteManager(...)
    # else:
    return InMemoryNoteManager() # We don't have sql, so we just cache and return In-Memory Manager.


def get_manager() -> INoteManager:
    """This function chooses which manager should be loaded, based on settings!"""
    # For Json, We should not cache! so in each CRUD function, CLI and Web can work on json file at the same time!
    if settings.STORAGE_TYPE == StorageType.JSON:
        return JsonNoteManager(db_path=settings.DB_PATH)

    # For other types, we use cached singleton instance(In-Memory for now).
    return get_singleton_manager()

def create_app() -> FastAPI:
    """Main function to create the FastAPI application."""

    app = FastAPI(title="Note Manager Web")

    # This line solves `python -m note` no template found problem, if user install Note App from Pypi
    templates = Jinja2Templates(directory=templates_path)

    @app.get("/")
    async def root():
        """Redirects the root URL to /notes."""
        return RedirectResponse(url="/notes")

    @app.get("/notes") # We should not use function as another functions input parameters, but it's ok in fastAPI!
    async def list_notes(request: Request, manager: INoteManager = Depends(get_manager)):  # noqa: B008
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
        content: str = Form(...),
        manager: INoteManager = Depends(get_manager)  # noqa: B008
    ):
        """submit button of the creation form"""
        manager.create_note(title=title, content=content)
        return RedirectResponse(url="/notes", status_code=303) # status_code 303 is important for POST redirects

    @app.get("/notes/{note_id}")
    async def read_note(
        request: Request,
        note_id: uuid.UUID,
        manager: INoteManager = Depends(get_manager)  # noqa: B008
    ):
        """Note details."""
        note = manager.get_note_by_id(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        return templates.TemplateResponse(
            "note_detail.html",
            {"request": request, "note": note}
        )

    @app.post("/notes/{note_id}/edit")
    async def update_note(
        note_id: uuid.UUID,
        title: str = Form(...),
        content: str = Form(...),
        manager: INoteManager = Depends(get_manager)  # noqa: B008
    ):
        """Edit button process"""
        updated_note = manager.update_note(note_id=note_id, title=title, content=content)
        if not updated_note:
            raise HTTPException(status_code=404, detail="Note not found for update")
        return RedirectResponse(url=f"/notes/{note_id}", status_code=303)

    @app.post("/notes/{note_id}/delete")
    async def delete_note(note_id: uuid.UUID, manager: INoteManager = Depends(get_manager)):  # noqa: B008
        """Delete button process."""
        success = manager.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found for deletion")
        return RedirectResponse(url="/notes", status_code=303)

    return app
