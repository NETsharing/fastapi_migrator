from http import HTTPStatus

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import router
from app.helpers.exception import BaseException, ErrorCode
from app.schema.response import ErrorResponse

tags_metadata = [
    {
        'name': 'healthcheck',
        'description': 'Доступность сервиса'
    },
    {
        'name': 'migrate data',
        'description': 'Миграция данных из MSSQL'
    },
    {
        'name': 'baselines data',
        'description': 'Базовые планы'
    },
    {
        'name': 'project data',
        'description': 'Проекты'
    },
]

# add OpenAPI
app = FastAPI(
    title="GRP reporter",
    version="0.0.1",
    description="Backend services for GRP reporter",
    docs_url='/api/grp_reporter/docs',
    openapi_url='/api/grp_reporter/openapi.json',
    redoc_url=None,
    openapi_tags=tags_metadata,
)

app.include_router(router)
origins = [
    "http://localhost",
    "http://localhost:8080",
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseException)
async def handle_base_exception(exception: BaseException) -> JSONResponse:
    """
    BaseException Handler
    """

    error_code = exception.get_error_code().value
    error_response = ErrorResponse(
        code=error_code.code,
        message=error_code.message
    )
    return JSONResponse(
        status_code=exception.get_status_code(),
        content=jsonable_encoder(error_response)
    )


@app.api_route("/{path_name:path}")
def api_not_found_handler():
    """
    API Not Found Handler
    """

    error_code = ErrorCode.NOT_FOUND_API.value
    error_response = ErrorResponse(
        code=error_code.code,
        message=error_code.message
    )
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content=jsonable_encoder(error_response)
    )
