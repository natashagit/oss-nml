"""Pydantic models for request/response serialization."""

from pydantic import BaseModel, ConfigDict, Field


class MessageSummary(BaseModel):
    """Summary representation of an email message."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    from_: str = Field(alias="from")
    to: str
    date: str
    subject: str


class MessageDetail(BaseModel):
    """Full detail representation of an email message."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    from_: str = Field(alias="from")
    to: str
    date: str
    subject: str
    body: str


class OperationResponse(BaseModel):
    """Generic response for operations like mark-as-read or delete."""

    success: bool
    message: str
