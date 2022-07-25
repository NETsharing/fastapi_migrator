from datetime import date
from typing import List

from app.schema.key_dates import KeyDatesBase
from app.schema.response import BaseSchema
from app.schema.versions import VersionsBase, VersionsBaseOut


class BaseLinesBase(BaseSchema):
    id: int
    created_at: date
    base_number: int
    base_plan_start_date: date
    base_plan_finish_date: date
    updated_at: date = None

    class Config:
        orm_mode = True


class BaseLinesOut(BaseLinesBase):

    tasks: List[KeyDatesBase]
    versions: List[VersionsBaseOut]

    class Config:
        orm_mode = True


class BaseLinesChildVersions(BaseLinesBase):

    versions: List[VersionsBase]

    class Config:
        orm_mode = True
