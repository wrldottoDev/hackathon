from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.network import GraphResponse
from ..services.network_service import get_network_graph

router = APIRouter(
    prefix="/network",
    tags=["network"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.get("/graph", response_model=GraphResponse)
def graph(db: Session = Depends(get_db)):
    return get_network_graph(db)

