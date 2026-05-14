import asyncio
import math
from typing import Any

import httpx
from diskcache import Cache

from app.core.config import settings


cache = Cache(settings.ROUTE_CACHE_DIR)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    radius_km = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius_km * c


async def geocode_with_nominatim(
    title: str,
    address: str,
    city: str,
) -> dict[str, Any] | None:
    query = ", ".join(part for part in [title, address, city, "Vietnam"] if part)
    cache_key = f"geocode:{query.lower()}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    if not query.strip():
        return None

    url = f"{settings.NOMINATIM_BASE_URL}/search"

    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT,
        "Accept": "application/json",
    }

    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "vn",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as http:
            response = await http.get(url, params=params, headers=headers)

            if response.status_code == 403:
                print(f"Nominatim 403 Forbidden for query: {query}")
                return None

            response.raise_for_status()
            data = response.json()

    except Exception as exc:
        print(f"Nominatim geocoding failed for query '{query}': {exc}")
        return None

    await asyncio.sleep(1)

    if not data:
        return None

    first = data[0]

    try:
        result = {
            "latitude": float(first["lat"]),
            "longitude": float(first["lon"]),
            "display_name": first.get("display_name", ""),
            "provider": "nominatim",
        }
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Nominatim returned invalid coordinate data for query '{query}': {exc}")
        return None

    cache.set(cache_key, result, expire=60 * 60 * 24 * 30)

    return result


async def ensure_coordinates(place: dict[str, Any]) -> dict[str, Any]:
    latitude = _to_float(place.get("latitude"))
    longitude = _to_float(place.get("longitude"))

    if latitude is not None and longitude is not None:
        return {
            **place,
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_source": "json",
        }

    geocoded = await geocode_with_nominatim(
        title=place.get("title", ""),
        address=place.get("address", ""),
        city=place.get("city", ""),
    )

    if geocoded:
        return {
            **place,
            "latitude": geocoded["latitude"],
            "longitude": geocoded["longitude"],
            "coordinate_source": "nominatim",
        }

    return {
        **place,
        "latitude": None,
        "longitude": None,
        "coordinate_source": "missing",
    }


def sort_places_by_nearest_neighbor(
    places: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    valid_places = [
        place
        for place in places
        if place.get("latitude") is not None and place.get("longitude") is not None
    ]

    if len(valid_places) <= 2:
        return valid_places

    unvisited = valid_places[:]
    route = [unvisited.pop(0)]

    while unvisited:
        current = route[-1]

        next_place = min(
            unvisited,
            key=lambda place: haversine_distance_km(
                current["latitude"],
                current["longitude"],
                place["latitude"],
                place["longitude"],
            ),
        )

        route.append(next_place)
        unvisited.remove(next_place)

    return route


def estimate_route_by_haversine(
    ordered_places: list[dict[str, Any]],
) -> dict[str, Any]:
    segments = []
    total_distance_km = 0.0

    for index in range(len(ordered_places) - 1):
        origin = ordered_places[index]
        destination = ordered_places[index + 1]

        distance_km = haversine_distance_km(
            origin["latitude"],
            origin["longitude"],
            destination["latitude"],
            destination["longitude"],
        )

        total_distance_km += distance_km

        segments.append(
            {
                "from": origin.get("title"),
                "to": destination.get("title"),
                "distance_km": round(distance_km, 2),
                "duration_minutes_estimate": round(distance_km / 4.5 * 60),
                "method": "haversine_estimate",
            }
        )

    return {
        "provider": "haversine_fallback",
        "profile": "walking_estimate",
        "total_distance_km": round(total_distance_km, 2),
        "total_duration_minutes": sum(
            segment["duration_minutes_estimate"] for segment in segments
        ),
        "segments": segments,
        "note": "Khoảng cách được ước lượng theo đường thẳng, không phải tuyến đường thực tế.",
    }


async def get_route_from_ors(
    ordered_places: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not settings.ORS_API_KEY:
        return None

    if len(ordered_places) < 2:
        return None

    coordinates = [
        [place["longitude"], place["latitude"]]
        for place in ordered_places
        if place.get("latitude") is not None and place.get("longitude") is not None
    ]

    if len(coordinates) < 2:
        return None

    cache_key = f"ors:{settings.ROUTE_PROFILE}:{coordinates}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    url = f"{settings.ORS_BASE_URL}/v2/directions/{settings.ROUTE_PROFILE}/geojson"

    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "coordinates": coordinates,
        "instructions": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as http:
            response = await http.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        summary = data["features"][0]["properties"]["summary"]

        result = {
            "provider": "openrouteservice_heigit",
            "profile": settings.ROUTE_PROFILE,
            "total_distance_km": round(summary["distance"] / 1000, 2),
            "total_duration_minutes": round(summary["duration"] / 60),
            "segments": [],
            "note": "Tuyến đường được tính bằng OpenRouteService/HeiGIT API.",
        }

        cache.set(cache_key, result, expire=60 * 60 * 24 * 7)

        return result

    except Exception as exc:
        print(f"ORS route request failed: {exc}")
        return None


async def build_route_plan(
    places: list[dict[str, Any]],
) -> dict[str, Any]:
    limited_places = places[: settings.ROUTE_MAX_PLACES]

    places_with_coordinates = []

    for place in limited_places:
        enriched = await ensure_coordinates(place)
        places_with_coordinates.append(enriched)

    valid_places = [
        place
        for place in places_with_coordinates
        if place.get("latitude") is not None and place.get("longitude") is not None
    ]

    missing_places = [
        place.get("title")
        for place in places_with_coordinates
        if place.get("latitude") is None or place.get("longitude") is None
    ]

    ordered_places = sort_places_by_nearest_neighbor(valid_places)

    ors_route = await get_route_from_ors(ordered_places)

    route_summary = ors_route or estimate_route_by_haversine(ordered_places)

    return {
        "strategy": "Ưu tiên tọa độ có sẵn trong JSON, sau đó geocoding bằng Nominatim nếu cần, rồi tính tuyến bằng ORS hoặc Haversine fallback.",
        "ordered_places": [
            {
                "title": place.get("title"),
                "category": place.get("category"),
                "address": place.get("address"),
                "best_time": place.get("best_time"),
            }
            for place in ordered_places
        ],
        "missing_coordinate_places": missing_places,
        "route_summary": route_summary,
    }