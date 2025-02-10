from fastapi import FastAPI

from containers import AppContainer
from .api import chat


def create_app() -> FastAPI:
    container = AppContainer()

    app = FastAPI()
    app.container = container
    app.include_router(chat.router)
    return app


app = create_app()
