from __future__ import annotations

import math
import re


def parse_coordinates_from_text(location_value: str | None) -> tuple[float, float] | None:
    if not location_value:
        return None

    match = re.search(r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", location_value)
    if not match:
        return None
    return float(match.group(1)), float(match.group(2))


def normalize_alert_region(location_value: str | None) -> str:
    if not location_value:
        return "sin_datos"

    coordinates = parse_coordinates_from_text(location_value)
    if coordinates is not None:
        latitude, longitude = coordinates
        if 10.2 <= latitude <= 11.4 and -85.7 <= longitude <= -83.8:
            return "zona_norte"
        if 9.7 <= latitude <= 10.2 and -84.5 <= longitude <= -83.7:
            return "valle_central"

    return normalize_transaction_region(location_value)


def normalize_transaction_region(location_value: str | None) -> str:
    if not location_value:
        return "sin_datos"

    normalized = location_value.upper()
    if "CROSS-BANK API" in normalized or "API" in normalized:
        return "virtual"
    if any(
        keyword in normalized
        for keyword in [
            "SAN CARLOS",
            "CIUDAD QUESADA",
            "LOS CHILES",
            "UPALA",
            "GUATUSO",
            "PITAL",
            "FORTUNA",
            "SARAPIQUI",
        ]
    ):
        return "zona_norte"
    if any(
        keyword in normalized
        for keyword in ["SAN JOSE", "ALAJUELA", "HEREDIA", "CARTAGO"]
    ):
        return "valle_central"
    if any(
        keyword in normalized
        for keyword in ["LIMON", "POCOCI", "SIQUIRRES", "TALAMANCA"]
    ):
        return "caribe"
    if any(
        keyword in normalized
        for keyword in ["PUNTARENAS", "QUEPOS", "OSA", "GOLFITO", "PARRITA"]
    ):
        return "pacifico"
    if any(
        keyword in normalized
        for keyword in ["GUANACASTE", "LIBERIA", "NICOYA", "SANTA CRUZ", "CAÑAS"]
    ):
        return "guanacaste"
    if any(
        keyword in normalized
        for keyword in ["PANAMA", "COLOMBIA", "NICARAGUA"]
    ):
        return "transfronterizo"
    return "otra_region"


def haversine_meters(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    radius = 6371000.0
    lat1 = math.radians(latitude_a)
    lat2 = math.radians(latitude_b)
    delta_lat = math.radians(latitude_b - latitude_a)
    delta_lng = math.radians(longitude_b - longitude_a)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c
