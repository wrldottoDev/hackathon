from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import lookup, reports, users
from .settings import ALLOWED_ORIGINS

app = FastAPI(
    title="SafeCall — FlowLens",
    description="Microservicio de deteccion de fraude telefonico",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(lookup.router)
app.include_router(reports.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "safecall"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("safecall.app.main:app", host="127.0.0.1", port=8006, reload=True)
