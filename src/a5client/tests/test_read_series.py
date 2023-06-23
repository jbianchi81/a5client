from unittest import TestCase

import a5client

class TestReadSeries(TestCase):
    def test_is_dict(self):
        client = a5client.a5.Crud()
        series = client.readSeries(var_id=2)
        self.assertTrue(isinstance(series, dict))