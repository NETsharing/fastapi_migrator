from datetime import date
from uuid import UUID

from pydantic import PrivateAttr

from app.schema.response import BaseSchema


class KeyDatesBase(BaseSchema):

    id: int
    name: str
    task_start_date: date
    _task_finish_date: date = PrivateAttr()
    task_uuid: UUID
    task_name: str

    class Config:
        underscore_attrs_are_private = True
        orm_mode = True
