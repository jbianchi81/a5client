from typing import TypedDict, List
from .tvp_prono import TVPProno


class TVPGroupedByQualifier(TypedDict):
    qualifier : str
    pronosticos : List[TVPProno]