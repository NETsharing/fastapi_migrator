from typing import List

from fastapi import APIRouter, Depends

from app.schema.project import ProjectBase
from app.services.project_services import ProjectService

project_router = APIRouter()


@project_router.get('/', response_model=List[ProjectBase])
async def get_projects(service: ProjectService = Depends()):

    """ Отдает все проекты   """

    return await service.get_projects()

