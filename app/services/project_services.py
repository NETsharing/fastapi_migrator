from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from fastapi import Depends

from app.repositories.project_repositories import ProjectRepository
from app.schema.project import ProjectBase


class ProjectService:

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        self.repo = ProjectRepository(db)

    async def get_projects(self) -> List[ProjectBase]:

        """ Отдает проекты """

        return await self.repo.get_all_projects()
