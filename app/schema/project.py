from datetime import date
from typing import List

from uuid import UUID

from app.schema.baselines import BaseLinesChildVersions
from app.schema.response import BaseSchema


class ProjectBase(BaseSchema):
    id: int
    name: str
    uuid: UUID
    is_active: bool
    start_date: date
    finish_date: date

    base_plans: List[BaseLinesChildVersions]

    class Config:
        orm_mode = True
