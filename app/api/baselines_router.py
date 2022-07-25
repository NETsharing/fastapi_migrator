from typing import List

from fastapi import APIRouter, Depends

from app.schema.baselines import BaseLinesOut
from app.services.beselines_services import BaseLinesService

baselines_router = APIRouter()


@baselines_router.get('/', response_model=List[BaseLinesOut])
async def get_project_base_plans(project_id: int, service: BaseLinesService = Depends()):

    """ Отдает все базовые планы по проекту
        project_id - id проекта """

    return await service.get_base_plans(project_id)
