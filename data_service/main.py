from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import tasks, providers, storage, users

app = FastAPI(title="Data Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://34.173.111.175",
        "http://34.173.111.175:3000",
        "http://34.173.111.175:8000",
        "http://34.173.111.175:8003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks")
app.include_router(providers.router, prefix="/providers")
app.include_router(storage.router, prefix="/storage")
app.include_router(users.router, prefix="/users")
