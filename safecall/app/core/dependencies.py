from fastapi import Header, HTTPException

from ..settings import SAFECALL_API_KEY


def require_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != SAFECALL_API_KEY:
        raise HTTPException(status_code=403, detail="API key invalida")
    return x_api_key
