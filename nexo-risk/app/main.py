from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.models.database import init_db, get_db
from app.routers import analysis, accounts
from app.services.seed import seed_database

app = FastAPI(
    title="NEXO Risk API",
    description="Plataforma de inteligencia financiera explicable — Hackathon Rastrea la Red",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(accounts.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "project": "NEXO Risk",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.post("/api/seed", tags=["dev"])
def seed(db: Session = Depends(get_db)):
    """Puebla la BD con datos sintéticos de prueba."""
    result = seed_database(db)
    return {"status": "ok", **result}
