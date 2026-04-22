from typing import TypedDict
from dateutil.relativedelta import relativedelta

class VariableDict(TypedDict):
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
    timeSupport: relativedelta
