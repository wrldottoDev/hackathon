from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routes import accounts, auth, interbank, transactions
from .settings import ALLOWED_ORIGINS, BANK_CODE, BANK_ID, BANK_NAME, PUBLIC_API_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=f"{BANK_NAME} API",
    description=f"API del {BANK_NAME} — plataforma FlowLens",
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
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(interbank.router)


@app.get("/", tags=["health"])
def health():
    return {
        "status": "ok",
        "bank": BANK_NAME,
        "bank_id": BANK_ID,
        "bank_code": BANK_CODE,
        "api_url": PUBLIC_API_URL,
    }


@app.get("/health", tags=["health"])
def detailed_health():
    return health()
