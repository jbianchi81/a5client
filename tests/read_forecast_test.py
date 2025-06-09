from unittest import TestCase, main
from datetime import datetime, timedelta
from a5client import Crud
import pytz

class TestReadForecasts(TestCase):

    client = Crud("https://alerta.ina.gob.ar/a5","my_token")
    # client = Crud("http://localhost:3005","my_token")

    ### readSeriePronoConcat

    def test_runs_not_found(self):
        self.assertRaises(
            FileNotFoundError,
            self.client.readSeriePronoConcat,
            cal_id = 445,
            series_id = 29586,
            tipo = "puntual",
            forecast_timestart = datetime(1900,1,1),
            forecast_timeend = datetime(1901,1,1) 
        )

    def test_series_found(self):
        serie = self.client.readSeriePronoConcat(
            cal_id = 289,
            series_id = 3526,
            tipo = "puntual",
            forecast_timestart = datetime.now() - timedelta(days=10),
            forecast_timeend = datetime.now() 
        )
        self.assertTrue(len(serie["pronosticos"]))


    def test_series_not_found(self):
        serie = self.client.readSeriePronoConcat(
            cal_id = 289,
            series_id = 549846357,
            tipo = "puntual",
            forecast_timestart = datetime.now() - timedelta(days=10),
            forecast_timeend = datetime.now() 
        )
        self.assertEqual(len(serie["pronosticos"]), 0)

    def test_mixed_qualifiers(self):
        serie = self.client.readSeriePronoConcat(
            cal_id = 289,
            series_id = 3526,
            tipo = "puntual",
            forecast_timestart = datetime.now() - timedelta(days=10),
            forecast_timeend = datetime.now() 
        )
        self.assertTrue(len(serie["pronosticos"]))
        qualifiers = set([ p["qualifier"] for p in serie["pronosticos"] ])
        self.assertEqual(len(qualifiers),3)

    def test_one_qualifier(self):
        serie = self.client.readSeriePronoConcat(
            cal_id = 289,
            series_id = 3526,
            tipo = "puntual",
            forecast_timestart = datetime.now() - timedelta(days=10),
            forecast_timeend = datetime.now() ,
            qualifier = "superior"
        )
        self.assertTrue(len(serie["pronosticos"]))
        qualifiers = set([ p["qualifier"] for p in serie["pronosticos"] ])
        self.assertEqual(len(qualifiers),1)
        self.assertIn("superior", qualifiers)

    def test_forecast_timestart(self):
        forecast_timestart = datetime.now(pytz.timezone("UTC")) - timedelta(days=7)
        serie_forecast = self.client.readSeriePronoConcat(
            cal_id=289,
            series_id=3526,
            forecast_timestart = forecast_timestart
        )
        for p in serie_forecast["pronosticos"]:
            self.assertGreaterEqual(datetime.fromisoformat(p["timestart"]), forecast_timestart)

    ### readSerieProno

    def test_returned_ids(self):
        cal_id = 289
        series_id = 3526
        serie = self.client.readSerieProno(
            cal_id = cal_id,
            series_id = series_id 
        )
        self.assertEqual(serie["cal_id"], cal_id)
        self.assertEqual(serie["series_id"], series_id)
        self.assertTrue(len(serie["pronosticos"]))

    def test_returned_ids_archived(self):
        cal_id = 289
        series_id = 1540
        serie = self.client.readSerieProno(
            cal_id = cal_id,
            series_id = series_id,
            cor_id = 761182,
            archived=True,
            qualifier="medio"
        )
        self.assertEqual(serie["cal_id"], cal_id)
        self.assertEqual(serie["series_id"], series_id)
        self.assertEqual(serie["qualifier"], "medio")
        self.assertTrue(len(serie["pronosticos"]))

    def test_returned_qualifier(self):
        cal_id = 289
        series_id = 3526
        serie_superior = self.client.readSerieProno(
            cal_id = cal_id,
            series_id = series_id,
            qualifier = "superior"
        )
        self.assertEqual(serie_superior["qualifier"], "superior")
        self.assertEqual(serie_superior["cal_id"], cal_id)
        self.assertEqual(serie_superior["series_id"], series_id)
        self.assertTrue(len(serie_superior["pronosticos"]))
        serie_inferior = self.client.readSerieProno(
            cal_id = cal_id,
            series_id = series_id,
            qualifier = "inferior"
        )
        self.assertEqual(serie_inferior["qualifier"], "inferior")
        self.assertEqual(serie_inferior["cal_id"], cal_id)
        self.assertEqual(serie_inferior["series_id"], series_id)
        self.assertEqual(len(serie_inferior["pronosticos"]), len(serie_superior["pronosticos"]))
        self.assertGreaterEqual(serie_superior["pronosticos"][0]["valor"], serie_inferior["pronosticos"][0]["valor"])
        for i in range(1,3):
            self.assertGreater(serie_superior["pronosticos"][i]["valor"], serie_inferior["pronosticos"][i]["valor"])

    def test_estacion_var_ids(self):
        cal_id = 289
        series_id = 3526
        estacion_id = 24
        var_id = 2
        serie = self.client.readSerieProno(
            cal_id = cal_id,
            estacion_id = estacion_id,
            var_id = var_id
        )
        self.assertEqual(serie["cal_id"], cal_id)
        self.assertEqual(serie["series_id"], series_id)
        self.assertTrue(len(serie["pronosticos"]))    


if __name__ == '__main__':
    main()