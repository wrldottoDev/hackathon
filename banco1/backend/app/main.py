from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import accounts, auth, network, risk, transactions, users
from .settings import ALLOWED_ORIGINS, BANK_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    init_db()
    yield


app = FastAPI(
    title=f"{BANK_NAME} API",
    description=f"Simulador bancario para demo de cuentas, transferencias y analítica para {BANK_NAME}.",
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

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(risk.router)
app.include_router(network.router)


@app.get("/")
def root():
    return {
        "name": f"{BANK_NAME} API",
        "status": "ok",
        "docs": "/docs",
    }
