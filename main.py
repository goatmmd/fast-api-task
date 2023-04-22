from fastapi import FastAPI

from routers import api_view

app = FastAPI()

app.include_router(api_view.router)
