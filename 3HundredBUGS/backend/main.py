from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routers.chat_router import chat_router
from routers.health_router import health_router
from routers.notification_router import notification_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(notification_router)
