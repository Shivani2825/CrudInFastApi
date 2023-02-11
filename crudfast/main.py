from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from user import api as ApiRoute
from user import route as UserRoute
from configs.connection import DATABASE_URL 
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware



db_url = DATABASE_URL()

middleware=[
    Middleware(SessionMiddleware,secret_key="super-secret")
]


app = FastAPI()
app.add_middleware(SessionMiddleware,secret_key='some-random-string')
# app.include_router(ApiRoute. prefix="/api", tags=["apis"]),
app.include_router(UserRoute.router, tags=["users"]),
# app.mount("/static",StaticFiles(directory="static"),name="static")


register_tortoise(
    app,
    db_url=db_url,
    modules={'models': ['user.models']},
    generate_schemas=True,
    add_exception_handlers=True
)