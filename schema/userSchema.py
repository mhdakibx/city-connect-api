from pydantic import BaseModel, Field
from typing import Annotated, Optional


class ComplaintCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    category: str
    location: str

class ComplaintUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=200)
    description: Optional[str] = Field(default=None, min_length=5)
    category: Optional[str] = None
    location: Optional[str] = None