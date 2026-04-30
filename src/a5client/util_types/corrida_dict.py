from .corrida_dict_no_id import CorridaDictNoId

class CorridaDict(CorridaDictNoId):
    """
    Parameters:
    -----------
    cal_id : int
    
    id : int

    forecast_date : datetime
    
    series: List[SeriesPronoDict]
    """
    id : int