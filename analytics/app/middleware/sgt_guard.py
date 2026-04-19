from ipaddress import ip_address

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ..settings import SECURE_ALERTS_ALLOWED_IPS, SECURE_ALERTS_SGT_TAG


class SGTGuardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix: str = "/api/v1/alertas") -> None:
        super().__init__(app)
        self._protected_prefix = protected_prefix
        self._allowed_ips = set(SECURE_ALERTS_ALLOWED_IPS)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith(self._protected_prefix):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        client_ip = _extract_client_ip(request)
        sgt_tag = request.headers.get("X-SGT-Tag")
        if sgt_tag != SECURE_ALERTS_SGT_TAG or client_ip not in self._allowed_ips:
            return JSONResponse(
                status_code=403,
                content={"detail": "Solicitud bloqueada por politica de seguridad."},
            )

        request.state.secure_alert_client_ip = client_ip
        return await call_next(request)


def _extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    candidate = forwarded.split(",")[0].strip()
    if not candidate and request.client is not None:
        candidate = request.client.host

    try:
        return str(ip_address(candidate))
    except ValueError:
        return ""
