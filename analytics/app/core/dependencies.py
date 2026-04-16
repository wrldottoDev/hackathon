from fastapi import Header, HTTPException, status

from ..settings import ANALYTICS_API_KEY


def require_analytics_api_key(
    x_analytics_key: str | None = Header(default=None, alias="X-Analytics-Key"),
) -> None:
    if x_analytics_key != ANALYTICS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key de analytics inválida",
        )

