from unittest import TestCase, main

from a5client import Crud

from random import random

class TestCreateSeries(TestCase):
    def test_success(self):
        valor = int(random() * 10000) * 0.01
        client = Crud("http://localhost:3005","my_token")
        series = client.createSeries(
            [
                {
                    "id": 3,
                    "estacion": {
                        "id": 1018,
                        "nombre": "test",
                        "geom": {
                            "type": "Point",
                            "coordinates": [-1, 1]
                        },
                        "tabla": "estaciones_virtuales",
                        "id_externo": "1"
                    },
                    "var_id": 2,
                    "proc_id": 1,
                    "unit_id": 11,
                    "observaciones": [
                        {
                            "timestart": "2024-01-01T03:00:00.000Z",
                            "timeend": "2024-01-01T03:00:00.000Z",
                            "valor": valor
                        }
                    ]
                }
            ],
            tipo = "puntual",
            series_metadata = True)
        self.assertTrue(isinstance(series, list), "list return type expected")
        self.assertEqual(len(series),1," 1 returned series element expected")
        self.assertEqual(type(series[0]["observaciones"]), list, " expected type of observaciones attribute is list. Instead, %s was found" % type(series[0]["observaciones"]))
        self.assertEqual(len(series[0]["observaciones"]),1," 1 returned observacion element expected")
        self.assertEqual(series[0]["observaciones"][0]["valor"], valor, "Expected return value of observation is %f. Instead, %f was found" % (valor, series[0]["observaciones"][0]["valor"]))




if __name__ == '__main__':
    main()