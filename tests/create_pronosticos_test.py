from unittest import TestCase, main
from datetime import datetime
import json
from pandas import DataFrame

from a5client import Crud, client, observacionesListToDataFrame

class TestCreatePronosticos(TestCase):
    def test_create(self):
        client = Crud("http://localhost:3005","my_token")
        pronosticos = json.load(open("data/pronos_areales.json","r", encoding="utf-8"))
        cor_id = 954778
        result = client.createPronosticos(
            cor_id,
            pronosticos,
            "areal"
        )
        self.assertEqual(len(result), 7680)

    def test_create_from_df(self):
        client = Crud("http://localhost:3005","my_token")
        cor_id = 954778
        series_id = 6759
        serie_prono = client.readSerieProno(series_id,676,cor_id=cor_id,tipo="areal")
        self.assertEqual(len(serie_prono["pronosticos"]), 64)
        pronos_df = DataFrame(serie_prono["pronosticos"])
        result = client.createPronosticos(
            cor_id,
            pronos_df,
            "areal",
            series_id=series_id
        )
        self.assertEqual(len(result), 64)