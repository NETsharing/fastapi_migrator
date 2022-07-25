from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.services.migration_services import migrate_data

migration_router = APIRouter()


@migration_router.get('/')
async def start_migration(session: AsyncSession = Depends(get_async_session)) -> True:
    """ Миграция данных из MS SQL"""

    return await migrate_data(session)
