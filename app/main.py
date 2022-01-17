from fastapi import FastAPI, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise
from fastapi.exceptions import RequestValidationError
from config import get_settings, get_postges_uri
from print_logger import print_log, ERROR

# Router
from modules.module_name.router import router as module_router

from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tags import tags_metadata

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

environment = get_settings().ENV

# sentry_sdk.init(
#     get_settings().SENTRY_URI,
#     traces_sample_rate=0.1,
#     environment=environment
# )

options = {
    "openapi_url": "/api/v1/openapi.json" if environment == "development" or environment == "local" else None,
    "openapi_tags": tags_metadata
}
app = FastAPI(**options)

try:
    app.add_middleware(SentryAsgiMiddleware)
except Exception as e:
    print(e)
    pass

origins = get_settings().ALLOWED_HOST

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc):
    detail = dict()

    for error in exc.errors():
        loc = error.get("loc")
        message = error.get("msg")

        if not loc or type(loc) is not tuple:
            continue

        key = loc[-1]
        detail[key] = message

    print_log({
        "errors": detail
    }, ERROR)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(detail)
    )


app.include_router(
    module_router,
    dependencies=[Depends(get_settings)],
)


@app.get('/health_check')
def hello():
    return 'OK'


@app.get('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0
    return division_by_zero


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        content=jsonable_encoder(exc.detail),
        status_code=exc.status_code
    )

POSTGRES_URI = get_settings().POSTGRES_URI if environment == 'local' else get_postges_uri()

TORTOISE_ORM = {
    "connections": {"default": POSTGRES_URI},
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "modules.module_name.models",
            ],
            "default_connection": "default",
        },
    },
}

register_tortoise(
    app,
    db_url=POSTGRES_URI,
    modules={"models": [
        "aerich.models",
        "modules.module_name.models",
    ]},
    add_exception_handlers=True,
)
