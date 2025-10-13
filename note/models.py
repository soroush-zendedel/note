import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Note(BaseModel):
    """Note Model"""
    id : uuid.UUID = Field(default_factory=uuid.uuid4)
    title : str
    content : str
    creation_at : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
