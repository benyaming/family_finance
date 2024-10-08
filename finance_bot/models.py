from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    id: Optional[int] = None
    name: str
    group_id: int


class CategoryGroup(BaseModel):
    id: Optional[int] = None
    name: str
    limit: Optional[int] = None


class Transaction(BaseModel):
    amount: int
    category_id: int
    created_at: datetime = Field(default_factory=datetime.now)


class Subscription(BaseModel):
    id: Optional[int] = None
    name: str
    amount: int
    day_of_month: int = Field(..., ge=1, le=31)
    category_id: int
    category_name: Optional[str] = None
    group_name: Optional[str] = None
    user_id: int


class Limit(BaseModel):
    group_name: str
    limit: int
    spent: int
    rest: int
    usage_percentage: int
