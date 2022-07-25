from datetime import date
from typing import List

from app.schema.key_dates import KeyDatesBase
from app.schema.response import BaseSchema


class VersionsBase(BaseSchema):
    id: int
    migration_date: date
    base_plan_id: int
    project_id: int
    parent_version_id: int = None

    class Config:
        orm_mode = True


class VersionsBaseOut(VersionsBase):

    tasks: List[KeyDatesBase]

    class Config:
        orm_mode = True
