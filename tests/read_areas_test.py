from unittest import TestCase, main

from a5client import Crud, client

class TestReadAreas(TestCase):
    def test_json(self):
        client_ = Crud("https://alerta.ina.gob.ar/a5","my_token")
        areas = client_.readAreas()
        self.assertTrue(isinstance(areas, dict))
        self.assertTrue("areas" in areas)
        self.assertTrue(isinstance(areas["areas"],list))
        for area in areas["areas"]:
            self.assertTrue(isinstance(area,dict))
            self.assertTrue("geom" in area)
            self.assertTrue("coordinates" in area["geom"])
            self.assertTrue("type" in area["geom"])
            self.assertEqual(area["geom"]["type"],"Polygon")

    def test_geojson(self):
        client_ = Crud("https://alerta.ina.gob.ar/a5","my_token")
        areas = client_.readAreas(format="geojson")
        self.assertTrue(isinstance(areas, dict))
        self.assertTrue("features" in areas)
        self.assertTrue(isinstance(areas["features"],list))
        for feature in areas["features"]:
            self.assertTrue(isinstance(feature,dict))
            self.assertTrue("geometry" in feature)
            self.assertTrue("coordinates" in feature["geometry"])
            self.assertTrue("type" in feature["geometry"])
            self.assertEqual(feature["geometry"]["type"],"Polygon")


if __name__ == '__main__':
    main()