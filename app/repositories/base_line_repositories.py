from typing import Type, List

from pydantic.tools import parse_obj_as
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.models import BasePlan
from app.schema.baselines import BaseLinesOut


class BaseLinesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    @property
    def _table(self) -> Type[BasePlan]:
        return BasePlan

    async def get_base_plans_by_project_id(self, project_id: int) -> List[BaseLinesOut]:

        """ Возвращает таблицу справочника услуг """

        query = (
            select(self._table)
            .where(self._table.project_id == project_id)
            .options(selectinload(self._table.tasks))
            .options(selectinload(self._table.versions)))

        entry = await self.db.execute(query)
        return parse_obj_as(List[BaseLinesOut], entry.scalars().all())
