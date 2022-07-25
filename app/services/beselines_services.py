from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.repositories.base_line_repositories import BaseLinesRepository
from app.schema.baselines import BaseLinesOut


class BaseLinesService:

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        self.repo = BaseLinesRepository(db)

    async def get_base_plans(self, project_id: int) -> List[BaseLinesOut]:
        """
        Отдает базовые планы по проекту
        project_id: ID проекта
        """
        result = await self.repo.get_base_plans_by_project_id(project_id)

        return result
