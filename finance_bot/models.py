from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    id: Optional[int]
    name: str
    group_id: int


class CategoryGroup(BaseModel):
    id: Optional[int]
    name: str


class Transaction(BaseModel):
    amount: int
    category_id: int
    created_at: datetime = Field(default_factory=datetime.now)


class Subscription(BaseModel):
    id: Optional[int]
    name: str
    amount: int
    day_of_month: int = Field(..., ge=1, le=31)
    category_id: int
