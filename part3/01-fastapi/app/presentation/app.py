from fastapi import FastAPI

from app.presentation.router import router

app = FastAPI()
app.include_router(router=router)
