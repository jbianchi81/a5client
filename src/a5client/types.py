from typing import Literal, Union, List, TypedDict, Tuple, Dict, Any

Position = Union[Tuple[float, float],Tuple[float, float, float]]

LineString = List[Position]

Polygon = List[LineString]

MultiPolygon = List[Polygon]

class Geometry(TypedDict):
    type : Literal[ "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon", "GeometryCollection" ]
    """tipo de geometría"""

    coordinates : Union[Position, LineString, Polygon, MultiPolygon]


class Sitio(TypedDict):
    nombre : str
    """nombre"""

    id : int
    """identificador único"""

    geom : Geometry
    """geometría"""

class Estacion(Sitio):
    tabla : str

class Escena(Sitio):
    pass

class Area(Sitio):
    exutorio : Geometry
    """geometría de la sección de salida (punto)"""

class Feature(TypedDict):
    type: Literal['Feature']
    geometry: Geometry
    properties: Dict[str, Any]

class FeatureCollection(TypedDict):
    type: Literal['FeatureCollection']
    features: List[Feature]

GeoJSON = Union[FeatureCollection, Feature]


