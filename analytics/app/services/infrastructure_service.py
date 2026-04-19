from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import mean
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import engine
from ..models.blacklist_link import BlacklistLink
from ..models.external_alert import ExternalAlert
from ..models.observed_account import ObservedAccount
from ..models.secure_alert import SecureAlert
from ..models.suspicious_ad import SuspiciousAd
from .geo_utils import (
    haversine_meters,
    normalize_alert_region,
    normalize_transaction_region,
    parse_coordinates_from_text,
)

URL_PATTERN = re.compile(
    r"(?:(?:https?://)|(?:www\.))?[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(?:/[^\s<>()]*)?",
    re.IGNORECASE,
)
TRAILING_PUNCTUATION = ".,;:!?)\"]}'"
PLATFORM_BY_HOST = {
    "facebook.com": "FB",
    "fb.com": "FB",
    "instagram.com": "IG",
}
RESCUE_PIN_LOOKBACK_HOURS = 12


def upsert_blacklist_link(
    db: Session,
    *,
    url: str,
    ip_origen: str | None,
    plataforma: str,
    descripcion: str | None,
) -> BlacklistLink:
    normalized_url = normalize_url(url)
    domain = extract_domain(normalized_url)
    record = (
        db.query(BlacklistLink)
        .filter(BlacklistLink.url == normalized_url)
        .one_or_none()
    )
    if record is None:
        record = BlacklistLink(
            url=normalized_url,
            dominio=domain,
            ip_origen=ip_origen,
            plataforma=plataforma,
            descripcion=descripcion,
        )
        db.add(record)
    else:
        record.ip_origen = ip_origen or record.ip_origen
        record.plataforma = plataforma or record.plataforma
        record.descripcion = descripcion or record.descripcion
        record.dominio = domain

    db.commit()
    db.refresh(record)
    return record


def upsert_suspicious_ad(
    db: Session,
    *,
    url: str,
    ip_origen: str | None,
    plataforma: str,
    titulo: str | None,
    descripcion: str | None,
) -> SuspiciousAd:
    normalized_url = normalize_url(url)
    domain = extract_domain(normalized_url)
    record = (
        db.query(SuspiciousAd)
        .filter(SuspiciousAd.url == normalized_url)
        .one_or_none()
    )
    if record is None:
        record = SuspiciousAd(
            url=normalized_url,
            dominio=domain,
            ip_origen=ip_origen,
            plataforma=plataforma,
            titulo=titulo,
            descripcion=descripcion,
        )
        db.add(record)
    else:
        record.ip_origen = ip_origen or record.ip_origen
        record.plataforma = plataforma or record.plataforma
        record.titulo = titulo or record.titulo
        record.descripcion = descripcion or record.descripcion
        record.dominio = domain

    db.commit()
    db.refresh(record)
    return record


def list_blacklist_links(db: Session, *, limit: int = 100) -> list[BlacklistLink]:
    return (
        db.query(BlacklistLink)
        .order_by(BlacklistLink.created_at.desc())
        .limit(limit)
        .all()
    )


def list_suspicious_ads(db: Session, *, limit: int = 100) -> list[SuspiciousAd]:
    return (
        db.query(SuspiciousAd)
        .order_by(SuspiciousAd.created_at.desc())
        .limit(limit)
        .all()
    )


def extract_links_from_text(text: str | None) -> list[str]:
    if not text:
        return []

    results: list[str] = []
    for match in URL_PATTERN.finditer(text):
        candidate = match.group(0).strip().rstrip(TRAILING_PUNCTUATION)
        if "." not in candidate:
            continue
        results.append(candidate)
    return sorted(set(results))


def normalize_url(url: str) -> str:
    cleaned = url.strip().rstrip(TRAILING_PUNCTUATION)
    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"
    parsed = urlparse(cleaned)
    netloc = parsed.netloc.lower()
    path = parsed.path or ""
    normalized = parsed._replace(
        scheme="https",
        netloc=netloc,
        params="",
        query="",
        fragment="",
    )
    normalized_url = normalized.geturl()
    if path == "/" and normalized_url.endswith("/"):
        return normalized_url[:-1]
    return normalized_url


def extract_domain(url: str) -> str | None:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = parsed.netloc.lower().split("@")[-1]
    if not domain:
        return None
    if ":" in domain:
        domain = domain.split(":", 1)[0]
    return domain or None


def infer_platform(url: str) -> str:
    domain = extract_domain(url) or ""
    for suffix, platform in PLATFORM_BY_HOST.items():
        if domain.endswith(suffix):
            return platform
    return "Web"


def dga_score(domain: str | None) -> float:
    if not domain:
        return 0.0

    host = domain.split(".", 1)[0]
    if len(host) < 8:
        return 0.0

    vowels = sum(1 for character in host if character in "aeiou")
    digits = sum(1 for character in host if character.isdigit())
    hyphens = host.count("-")
    unique_ratio = len(set(host)) / max(len(host), 1)
    vowel_ratio = vowels / len(host)
    digit_ratio = digits / len(host)
    hyphen_ratio = hyphens / len(host)

    score = 0.0
    score += min(len(host) / 20, 1.0) * 0.2
    score += unique_ratio * 0.25
    score += digit_ratio * 0.25
    score += hyphen_ratio * 0.1
    score += max(0.0, 0.22 - vowel_ratio) * 1.2
    return round(min(score, 1.0), 3)


def is_probable_dga(domain: str | None) -> bool:
    return dga_score(domain) >= 0.62


def detect_alert_link_indicators(
    db: Session,
    alert: SecureAlert,
    *,
    increment_hits: bool = False,
) -> list[dict]:
    combined_text = "\n".join(
        _buffer_item_to_text(item)
        for item in (alert.buffer_texto or [])
    ).strip()
    candidate_links = extract_links_from_text(combined_text)
    if not candidate_links:
        return []

    normalized_links = [normalize_url(link) for link in candidate_links]
    domains = {extract_domain(link) for link in normalized_links}
    domains.discard(None)

    blacklist_by_url = {
        record.url: record
        for record in db.query(BlacklistLink)
        .filter(BlacklistLink.url.in_(normalized_links))
        .all()
    }
    blacklist_by_domain = {
        record.dominio: record
        for record in db.query(BlacklistLink)
        .filter(BlacklistLink.dominio.in_(domains))
        .all()
    }
    ads_by_url = {
        record.url: record
        for record in db.query(SuspiciousAd)
        .filter(SuspiciousAd.url.in_(normalized_links))
        .all()
    }
    ads_by_domain = {
        record.dominio: record
        for record in db.query(SuspiciousAd)
        .filter(SuspiciousAd.dominio.in_(domains))
        .all()
    }

    indicators: list[dict] = []
    modified_records = False
    for normalized_link in normalized_links:
        domain = extract_domain(normalized_link)
        blacklist_record = blacklist_by_url.get(normalized_link) or blacklist_by_domain.get(domain)
        ad_record = ads_by_url.get(normalized_link) or ads_by_domain.get(domain)
        if increment_hits:
            if blacklist_record is not None:
                blacklist_record.hits_reportados += 1
                modified_records = True
            if ad_record is not None:
                ad_record.hits_reportados += 1
                modified_records = True

        indicators.append(
            {
                "url": normalized_link,
                "domain": domain,
                "platform": infer_platform(normalized_link),
                "dga_score": dga_score(domain),
                "probable_dga": is_probable_dga(domain),
                "blacklist_match": blacklist_record is not None,
                "blacklist_id": blacklist_record.id if blacklist_record else None,
                "suspicious_ad_match": ad_record is not None,
                "suspicious_ad_id": ad_record.id if ad_record else None,
                "ad_title": ad_record.titulo if ad_record else None,
            }
        )

    if modified_records:
        db.commit()

    return indicators


def _buffer_item_to_text(item: object) -> str:
    if isinstance(item, dict):
        payload = item.get("payload")
        return str(payload) if payload is not None else ""
    if isinstance(item, str):
        return item
    return ""


def evaluate_rescue_mode_for_alert(
    db: Session,
    alert: SecureAlert,
    *,
    link_indicators: list[dict] | None = None,
) -> dict:
    indicators = link_indicators or detect_alert_link_indicators(db, alert)
    if not any(item.get("blacklist_match") for item in indicators):
        return {"triggered": False, "reason": "No se detectaron links en blacklist."}

    region = normalize_alert_region(alert.ubicacion_gps)
    if region == "sin_datos":
        return {"triggered": False, "reason": "La alerta no tiene geografia utilizable."}

    threshold = datetime.now(timezone.utc) - timedelta(hours=RESCUE_PIN_LOOKBACK_HOURS)
    accounts = (
        db.query(ObservedAccount)
        .filter(ObservedAccount.last_credentials_change_at.is_not(None))
        .filter(ObservedAccount.last_credentials_change_at >= threshold)
        .all()
    )
    matching_accounts = [
        account
        for account in accounts
        if normalize_transaction_region(account.current_location) == region
    ]
    if not matching_accounts:
        return {
            "triggered": False,
            "reason": "No hay activaciones recientes de PIN/credenciales en la misma zona.",
        }

    matched_links = [
        indicator["url"]
        for indicator in indicators
        if indicator.get("blacklist_match")
    ]
    alert_record = ExternalAlert(
        alert_type="modo_rescate_blacklist",
        severity="critical",
        description=(
            f"Modo Rescate activado. Link blacklist detectado en {region}. "
            f"Links: {', '.join(matched_links[:3])}. "
            f"Cuentas con cambio reciente de PIN/credenciales en la zona: "
            f"{', '.join(account.account_number for account in matching_accounts[:5])}."
        ),
        source_service="infrastructure",
    )
    db.add(alert_record)
    db.commit()
    db.refresh(alert_record)
    return {
        "triggered": True,
        "region": region,
        "external_alert_id": alert_record.id,
        "matched_links": matched_links,
        "accounts": [account.account_number for account in matching_accounts],
    }


def build_heatmap(
    db: Session,
    *,
    lookback_hours: int = 24,
    eps_meters: float = 5000.0,
    min_points: int = 2,
    limit: int = 500,
) -> list[dict]:
    period_end = datetime.now(timezone.utc)
    period_start = period_end - timedelta(hours=lookback_hours)

    if engine.url.get_backend_name().startswith("postgresql"):
        try:
            return _build_heatmap_postgis(
                db,
                period_start=period_start,
                period_end=period_end,
                eps_meters=eps_meters,
                min_points=min_points,
                limit=limit,
            )
        except Exception:  # noqa: BLE001
            return _build_heatmap_fallback(
                db,
                period_start=period_start,
                period_end=period_end,
                eps_meters=eps_meters,
                min_points=min_points,
                limit=limit,
            )

    return _build_heatmap_fallback(
        db,
        period_start=period_start,
        period_end=period_end,
        eps_meters=eps_meters,
        min_points=min_points,
        limit=limit,
    )


def _build_heatmap_postgis(
    db: Session,
    *,
    period_start: datetime,
    period_end: datetime,
    eps_meters: float,
    min_points: int,
    limit: int,
) -> list[dict]:
    query = text(
        """
        WITH points AS (
            SELECT
                id,
                COALESCE(CAST(riesgo_probabilidad AS DOUBLE PRECISION), 0) AS risk,
                ST_Transform(
                    ST_SetSRID(ST_Point(longitude, latitude), 4326),
                    3857
                ) AS geom_3857,
                ST_SetSRID(ST_Point(longitude, latitude), 4326) AS geom_4326,
                ubicacion_gps
            FROM alertas
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
              AND timestamp BETWEEN :period_start AND :period_end
            ORDER BY id
            LIMIT :limit
        ),
        clustered AS (
            SELECT
                id,
                risk,
                geom_4326,
                ubicacion_gps,
                ST_ClusterDBSCAN(
                    geom_3857,
                    eps => :eps_meters,
                    minpoints => :min_points
                ) OVER (ORDER BY id) AS cid
            FROM points
        )
        SELECT
            cid,
            COUNT(*) AS hit_count,
            AVG(risk) AS avg_risk,
            ST_Y(ST_Centroid(ST_Collect(geom_4326))) AS centroid_latitude,
            ST_X(ST_Centroid(ST_Collect(geom_4326))) AS centroid_longitude,
            ARRAY_AGG(id ORDER BY id) AS alert_ids,
            MIN(ubicacion_gps) AS region_sample
        FROM clustered
        WHERE cid IS NOT NULL
        GROUP BY cid
        ORDER BY hit_count DESC, cid
        """
    )
    rows = db.execute(
        query,
        {
            "period_start": period_start,
            "period_end": period_end,
            "eps_meters": eps_meters,
            "min_points": min_points,
            "limit": limit,
        },
    ).mappings()

    results: list[dict] = []
    for row in rows:
        region_sample = row["region_sample"]
        results.append(
            {
                "cluster_id": f"cluster-{row['cid']}",
                "hit_count": int(row["hit_count"]),
                "avg_risk": float(row["avg_risk"] or 0.0),
                "centroid_latitude": float(row["centroid_latitude"]),
                "centroid_longitude": float(row["centroid_longitude"]),
                "alert_ids": [int(value) for value in row["alert_ids"]],
                "region_bucket": normalize_alert_region(region_sample),
            }
        )
    return results


def _build_heatmap_fallback(
    db: Session,
    *,
    period_start: datetime,
    period_end: datetime,
    eps_meters: float,
    min_points: int,
    limit: int,
) -> list[dict]:
    alerts = (
        db.query(SecureAlert)
        .filter(SecureAlert.timestamp >= period_start)
        .filter(SecureAlert.timestamp <= period_end)
        .filter(SecureAlert.latitude.is_not(None))
        .filter(SecureAlert.longitude.is_not(None))
        .order_by(SecureAlert.timestamp.desc())
        .limit(limit)
        .all()
    )

    points = [
        {
            "id": alert.id,
            "latitude": float(alert.latitude),
            "longitude": float(alert.longitude),
            "risk": float(alert.riesgo_probabilidad or 0),
            "region": normalize_alert_region(alert.ubicacion_gps),
        }
        for alert in alerts
    ]
    if not points:
        return []

    adjacency: dict[int, set[int]] = defaultdict(set)
    for index_a, point_a in enumerate(points):
        for index_b in range(index_a + 1, len(points)):
            point_b = points[index_b]
            distance = haversine_meters(
                point_a["latitude"],
                point_a["longitude"],
                point_b["latitude"],
                point_b["longitude"],
            )
            if distance <= eps_meters:
                adjacency[index_a].add(index_b)
                adjacency[index_b].add(index_a)

    visited: set[int] = set()
    clusters: list[list[dict]] = []
    for index in range(len(points)):
        if index in visited:
            continue
        stack = [index]
        component: list[int] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(adjacency.get(current, set()) - visited)
        if len(component) >= min_points:
            clusters.append([points[item] for item in component])

    results: list[dict] = []
    for index, cluster in enumerate(clusters):
        results.append(
            {
                "cluster_id": f"cluster-{index}",
                "hit_count": len(cluster),
                "avg_risk": round(mean(point["risk"] for point in cluster), 4),
                "centroid_latitude": sum(point["latitude"] for point in cluster)
                / len(cluster),
                "centroid_longitude": sum(point["longitude"] for point in cluster)
                / len(cluster),
                "alert_ids": [int(point["id"]) for point in sorted(cluster, key=lambda item: item["id"])],
                "region_bucket": _dominant_region(cluster),
            }
        )
    return results


def _dominant_region(cluster: list[dict]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for item in cluster:
        counts[item["region"]] += 1
    return max(counts.items(), key=lambda pair: pair[1])[0]
