from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import accounts, alerts, banks, network, transactions
from .settings import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    init_db()
    yield


app = FastAPI(
    title="FlowLens Analytics API",
    description="Servicio externo de analítica, alertas y seguimiento de redes transaccionales.",
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

app.include_router(banks.router)
app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(network.router)
app.include_router(accounts.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "analytics"}


@app.get("/health", tags=["health"])
def health():
    return root()

