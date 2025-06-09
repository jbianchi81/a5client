from unittest import TestCase, main
from datetime import datetime, timedelta
from a5client import Crud
import pytz

class TestReadRuns(TestCase):

    client = Crud("https://alerta.ina.gob.ar/a5","my_token")

    ### readCorridas

    def test_archived(self):
        results = self.client.readCorridas(cal_id=445,archived=True)
        self.assertTrue(len(results) > 0)
