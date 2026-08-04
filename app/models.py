from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

# Tag constraints (Feature: tags/labels). Kept small and explicit so both the
# create and update validators enforce the same rules.
MAX_TAGS = 10
MAX_TAG_LENGTH = 30


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _normalize_tags(value: object) -> list[str]:
    """Trim, reject blanks, de-duplicate, and cap tag count/length.

    Raises ValueError/TypeError so Pydantic surfaces a 422 to the client.
    """
    if not isinstance(value, list):
        raise TypeError("Tags must be a list of strings")

    cleaned: list[str] = []
    for tag in value:
        if not isinstance(tag, str):
            raise TypeError("Each tag must be a string")
        stripped = tag.strip()
        if not stripped:
            raise ValueError("Tags must not be blank")
        if len(stripped) > MAX_TAG_LENGTH:
            raise ValueError(f"Each tag must be {MAX_TAG_LENGTH} characters or less")
        if stripped not in cleaned:
            cleaned.append(stripped)

    if len(cleaned) > MAX_TAGS:
        raise ValueError(f"A task can have at most {MAX_TAGS} tags")
    return cleaned


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        if value is None:
            raise ValueError("Title is required")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Title must not be blank")
        if len(stripped_value) > 200:
            raise ValueError("Title must be 200 characters or less")
        return stripped_value

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: object) -> list[str]:
        if value is None:
            return []
        return _normalize_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_null_title(cls, data: object) -> object:
        # A partial update may OMIT title (leave it unchanged), but it must never
        # set it to null — a task always has a title. Because title is Optional,
        # an omitted field and an explicit `null` both arrive as None at the field
        # validator; only the raw payload can tell them apart (the key is present
        # exactly when the client sent it), so we check it here.
        if isinstance(data, dict) and "title" in data and data["title"] is None:
            raise ValueError("Title must not be null")
        return data

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("Title must be a string")

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Title must not be blank")
        if len(stripped_value) > 200:
            raise ValueError("Title must be 200 characters or less")
        return stripped_value

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: object) -> Optional[list[str]]:
        # None means "field not provided" for a partial update; leave it alone.
        if value is None:
            return None
        return _normalize_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def overdue(self) -> bool:
        """A task is overdue when it has a past due date and isn't Done.

        Computed on serialization so it stays correct as the calendar advances
        without needing a stored value to be recalculated.
        """
        if self.due_date is None or self.status == TaskStatus.DONE:
            return False
        return self.due_date < date.today()
