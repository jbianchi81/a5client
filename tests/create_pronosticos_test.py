from unittest import TestCase, main
from datetime import datetime
import json

from a5client import Crud, client

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