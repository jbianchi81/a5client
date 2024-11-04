from unittest import TestCase, main

from a5client import Crud

class TestReadSeries(TestCase):
    def test_is_dict(self):
        client = Crud("https://alerta.ina.gob.ar/a5","my_token")
        series = client.readSeries(var_id=2)
        self.assertTrue(isinstance(series, dict))


if __name__ == '__main__':
    main()