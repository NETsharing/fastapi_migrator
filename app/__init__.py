from fastapi import APIRouter

from app.api.healthcheck_router import healthcheck_router
from app.api.migration_router import migration_router
from app.api.baselines_router import baselines_router
from app.api.project_router import project_router


router = APIRouter(
    prefix="/api/grp_reporter",
    responses={404: {"description": "Not found"}}
)

router.include_router(healthcheck_router, prefix='/ping', tags=["healthcheck"])
router.include_router(migration_router, prefix='/migrate', tags=["migrate data"])
router.include_router(baselines_router, prefix='/baselines', tags=["baselines data"])
router.include_router(project_router, prefix='/project', tags=["project data"])
