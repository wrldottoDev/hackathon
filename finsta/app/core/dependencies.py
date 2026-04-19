from fastapi import Header, HTTPException

from ..settings import FINSTA_API_KEY


def require_finsta_api_key(
    x_api_key: str = Header(alias="X-API-Key", default=""),
) -> str:
    if x_api_key != FINSTA_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
