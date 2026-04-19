from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import analysis, feed, messages, reports, users
from .settings import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    init_db()
    yield


app = FastAPI(
    title="Finsta — FlowLens Social Network Simulator",
    description=(
        "Red social simulada para detección de captación ilícita, "
        "trata de personas y fraudes digitales."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(feed.router)
app.include_router(messages.router)
app.include_router(reports.router)
app.include_router(analysis.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "finsta"}


@app.get("/health", tags=["health"])
def health():
    return root()
