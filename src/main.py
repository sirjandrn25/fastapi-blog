from fastapi import FastAPI,Depends
from .routers import user_router

from fastapi.security.api_key import APIKeyHeader
app = FastAPI()
app.include_router(user_router.router)
from fastapi.staticfiles import StaticFiles
import os


base_dir = os.getcwd()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}