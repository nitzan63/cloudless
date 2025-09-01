from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import tasks, providers, storage, users

app = FastAPI(title="Data Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks")
app.include_router(providers.router, prefix="/providers")
app.include_router(storage.router, prefix="/storage")
app.include_router(users.router, prefix="/users")
