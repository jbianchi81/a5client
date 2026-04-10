from typing import Any

GEOJSON_TYPES = {
    "Point",
    "MultiPoint",
    "LineString",
    "MultiLineString",
    "Polygon",
    "MultiPolygon",
    "Feature",
    "FeatureCollection",
}

def is_position(p: Any) -> bool:
    return (
        isinstance(p, (list, tuple)) and
        len(p) >= 2 and
        all(isinstance(x, (int, float)) for x in p)
    )

def is_coordinates(coords: Any, geom_type: str) -> bool:
    if geom_type == "Point":
        return is_position(coords)

    if geom_type == "MultiPoint" or geom_type == "LineString":
        return isinstance(coords, list) and all(is_position(p) for p in coords)

    if geom_type == "MultiLineString" or geom_type == "Polygon":
        return (
            isinstance(coords, list) and
            all(isinstance(line, list) and all(is_position(p) for p in line) for line in coords)
        )

    if geom_type == "MultiPolygon":
        return (
            isinstance(coords, list) and
            all(
                isinstance(poly, list) and
                all(
                    isinstance(ring, list) and all(is_position(p) for p in ring)
                    for ring in poly
                )
                for poly in coords
            )
        )

    return False


def is_geometry(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False

    t = obj.get("type")
    if t not in GEOJSON_TYPES - {"Feature", "FeatureCollection"}:
        return False

    if "coordinates" not in obj:
        return False

    return is_coordinates(obj["coordinates"], t)


def is_feature(obj: Any) -> bool:
    return (
        isinstance(obj, dict) and
        obj.get("type") == "Feature" and
        "geometry" in obj and
        (obj["geometry"] is None or is_geometry(obj["geometry"])) and
        "properties" in obj and
        isinstance(obj["properties"], (dict, type(None)))
    )


def is_feature_collection(obj: Any) -> bool:
    return (
        isinstance(obj, dict) and
        obj.get("type") == "FeatureCollection" and
        isinstance(obj.get("features"), list) and
        all(is_feature(f) for f in obj["features"])
    )


def is_geojson(data: Any) -> bool:
    if not isinstance(data, dict):
        return False

    t = data.get("type")

    if t in GEOJSON_TYPES - {"Feature", "FeatureCollection"}:
        return is_geometry(data)

    if t == "Feature":
        return is_feature(data)

    if t == "FeatureCollection":
        return is_feature_collection(data)

    return False