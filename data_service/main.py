from fastapi import FastAPI
from api import tasks, providers, storage, users

app = FastAPI(title="Data Service")

app.include_router(tasks.router, prefix="/tasks")
app.include_router(providers.router, prefix="/providers")
app.include_router(storage.router, prefix="/storage")
app.include_router(users.router, prefix="/users")
