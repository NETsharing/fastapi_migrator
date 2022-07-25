from fastapi import APIRouter

from app.services.healthcheck_services import check_service

healthcheck_router = APIRouter()


@healthcheck_router.get('/')
async def get_healthcheck():
    """ healthcheck """
    return await check_service()
