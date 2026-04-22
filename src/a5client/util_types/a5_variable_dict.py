from typing import TypedDict
from .a5_interval_dict import A5IntervalDict

class A5VariableDict(TypedDict):
    id : int
    var : str
    nombre: str
    abrev: str
    type: str
    datatype: str
    valuetype: str
    GeneralCategory: str
    VariableName: str
    SampleMedium: str
    def_unit_id: int
    timeSupport: A5IntervalDict
