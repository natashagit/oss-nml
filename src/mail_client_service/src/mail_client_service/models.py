"""Pydantic models for request/response serialization."""

from pydantic import BaseModel, Field


class MessageSummary(BaseModel):
    """Summary representation of an email message."""

    id: str
    from_: str = Field(alias="from")
    to: str
    date: str
    subject: str

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class MessageDetail(BaseModel):
    """Full detail representation of an email message."""

    id: str
    from_: str = Field(alias="from")
    to: str
    date: str
    subject: str
    body: str

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True


class OperationResponse(BaseModel):
    """Generic response for operations like mark-as-read or delete."""

    success: bool
    message: str
