from unittest import TestCase, main
from datetime import datetime, timedelta
from a5client import Crud

class TestReadForecasts(TestCase):
    def test_runs_not_found(self):
        client = Crud("https://alerta.ina.gob.ar/a5","my_token")
        self.assertRaises(
            FileNotFoundError,
            client.readSeriePronoConcat,
            cal_id = 445,
            series_id = 29586,
            tipo = "puntual",
            forecast_timestart = datetime(1900,1,1),
            forecast_timeend = datetime(1901,1,1) 
        )

    def test_series_not_found(self):
        client = Crud("https://alerta.ina.gob.ar/a5","my_token")
        serie = client.readSeriePronoConcat(
            cal_id = 489,
            series_id = 3456729586,
            tipo = "puntual",
            forecast_timestart = datetime.now() - timedelta(days=10),
            forecast_timeend = datetime.now() 
        )
        self.assertEqual(len(serie["pronosticos"]), 0)

if __name__ == '__main__':
    main()