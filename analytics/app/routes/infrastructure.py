from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.dependencies import require_analytics_api_key
from ..database import get_db
from ..schemas.infrastructure import (
    BlacklistLinkCreate,
    BlacklistLinkResponse,
    HeatmapClusterResponse,
    SuspiciousAdCreate,
    SuspiciousAdResponse,
)
from ..services.infrastructure_service import (
    build_heatmap,
    list_blacklist_links,
    list_suspicious_ads,
    upsert_blacklist_link,
    upsert_suspicious_ad,
)

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["infrastructure"],
    dependencies=[Depends(require_analytics_api_key)],
)


@router.post("/blacklist-links", response_model=BlacklistLinkResponse, status_code=201)
def create_blacklist_link(
    payload: BlacklistLinkCreate,
    db: Session = Depends(get_db),
):
    record = upsert_blacklist_link(
        db,
        url=payload.url,
        ip_origen=payload.ip_origen,
        plataforma=payload.plataforma,
        descripcion=payload.descripcion,
    )
    return BlacklistLinkResponse.model_validate(record, from_attributes=True)


@router.get("/blacklist-links", response_model=list[BlacklistLinkResponse])
def get_blacklist_links(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    records = list_blacklist_links(db, limit=limit)
    return [
        BlacklistLinkResponse.model_validate(record, from_attributes=True)
        for record in records
    ]


@router.post("/anuncios-sospechosos", response_model=SuspiciousAdResponse, status_code=201)
def create_suspicious_ad(
    payload: SuspiciousAdCreate,
    db: Session = Depends(get_db),
):
    record = upsert_suspicious_ad(
        db,
        url=payload.url,
        ip_origen=payload.ip_origen,
        plataforma=payload.plataforma,
        titulo=payload.titulo,
        descripcion=payload.descripcion,
    )
    return SuspiciousAdResponse.model_validate(record, from_attributes=True)


@router.get("/anuncios-sospechosos", response_model=list[SuspiciousAdResponse])
def get_suspicious_ads(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    records = list_suspicious_ads(db, limit=limit)
    return [
        SuspiciousAdResponse.model_validate(record, from_attributes=True)
        for record in records
    ]


@router.get("/heatmap", response_model=list[HeatmapClusterResponse])
def get_heatmap(
    lookback_hours: int = Query(default=24, ge=1, le=168),
    eps_meters: float = Query(default=5000.0, ge=100.0, le=100000.0),
    min_points: int = Query(default=2, ge=2, le=50),
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    clusters = build_heatmap(
        db,
        lookback_hours=lookback_hours,
        eps_meters=eps_meters,
        min_points=min_points,
        limit=limit,
    )
    return [HeatmapClusterResponse.model_validate(item) for item in clusters]
