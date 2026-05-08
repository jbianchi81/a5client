from typing import Union, List, Tuple
from .tvp_dateable import TVPdateable
from .tvp import TVP
from .dateable import Dateable

TVPList = Union[List[TVPdateable],List[TVP],List[Tuple[Dateable,float]]]