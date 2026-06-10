from unittest import TestCase, main
import json
from a5client import Crud, client

class TestReadAreas(TestCase):
    def test_json(self):
        client_ = Crud("https://alerta.ina.gob.ar/a5","my_token")
        areas = client_.readAreas()
        # self.assertTrue(isinstance(areas, dict))
        assert isinstance(areas, dict)
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
        # self.assertTrue(isinstance(areas, dict))
        assert isinstance(areas, dict)
        self.assertTrue("features" in areas)
        self.assertTrue(isinstance(areas["features"],list))
        for feature in areas["features"]:
            self.assertTrue(isinstance(feature,dict))
            self.assertTrue("geometry" in feature)
            self.assertTrue("coordinates" in feature["geometry"])
            self.assertTrue("type" in feature["geometry"])
            self.assertEqual(feature["geometry"]["type"],"Polygon")
    
    def test_additional_params(self):
        client_ = Crud("https://alerta.ina.gob.ar/a5","my_token")
        result = client_.readAreas(format="geojson", additional_params={"mostrar": True, "activar": True})
        assert isinstance(result, dict)
        self.assertTrue("areas" in result)
        assert isinstance(result["areas"],list)
        self.assertTrue(len(result["areas"]) > 0)
        self.assertEqual(len([f for f in result["features"] if f["properties"]["activar"] == True]), len(result["areas"]))
        self.assertEqual(len([f for f in result["features"] if f["properties"]["mostrar"] == True]), len(result["areas"]))
        # json.dump(result, open("data/areas_activas_y_visibles.json","w",encoding="utf-8"), indent=2)


if __name__ == '__main__':
    main()