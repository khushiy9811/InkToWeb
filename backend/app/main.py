from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine, Base, run_migrations
from .config import CORS_ORIGINS, UPLOAD_DIR
from .routers import auth as auth_router
from .routers import customers as customers_router
from .routers import forms as forms_router

run_migrations()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InkToWeb API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth_router.router)
app.include_router(customers_router.router)
app.include_router(forms_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
