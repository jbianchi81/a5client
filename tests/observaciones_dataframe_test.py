from unittest import TestCase, main
from a5client import observacionesDataFrameToList
import pandas
from datetime import datetime, timedelta

class TestObservacionesDataFrameToList(TestCase):
    def test_timestart_column(self):
        data = pandas.DataFrame([
            {
                "timestart": datetime(2000,1,1),
                "valor": 45.8
            },
            {
                "timestart": datetime(2000,1,2),
                "valor": 34.3
            },
            {
                "timestart": datetime(2000,1,3),
                "valor": 22.1
            }
        ])
        data["timestart"] = data["timestart"].dt.tz_localize("America/Argentina/Buenos_Aires", nonexistent="shift_forward")

        observaciones = observacionesDataFrameToList(data, series_id=333, timeSupport=timedelta(days=1))

        self.assertTrue(isinstance(observaciones, list), "list return type expected")
        self.assertEqual(len(observaciones),3," 3 returned observacion element expected")
        self.assertEqual(type(observaciones[0]), dict, " expected type of observacion is dict. Instead, %s was found" % type(observaciones[0]))
        self.assertEqual(type(observaciones[0]["timestart"]), str,"expected str type for timestart. Instead, %s was found" % type(observaciones[0]["timestart"]))
        expected_dt = "2000-01-01T00:00:00-03:00"
        self.assertEqual(observaciones[0]["timestart"], expected_dt)

    def test_timestart_str_column(self):
        data = pandas.DataFrame([
            {
                "timestart": "2000-01-01T00:00:00-03:00",
                "valor": 45.8
            },
            {
                "timestart": "2000-01-02T00:00:00-03:00",
                "valor": 34.3
            },
            {
                "timestart": "2000-01-03T00:00:00-03:00",
                "valor": 22.1
            }
        ])

        observaciones = observacionesDataFrameToList(data, series_id=333, timeSupport=timedelta(days=1))

        self.assertTrue(isinstance(observaciones, list), "list return type expected")
        self.assertEqual(len(observaciones),3," 3 returned observacion element expected")
        self.assertEqual(type(observaciones[0]), dict, " expected type of observacion is dict. Instead, %s was found" % type(observaciones[0]))
        self.assertEqual(type(observaciones[0]["timestart"]), str,"expected str type for timestart. Instead, %s was found" % type(observaciones[0]["timestart"]))
        expected_dt = "2000-01-01T00:00:00-03:00"
        self.assertEqual(observaciones[0]["timestart"], expected_dt)

    def test_multiseries(self):
        data = pandas.DataFrame([
            {
                "timestart": "2000-01-01T00:00:00-03:00",
                "timeend": "2000-01-01T01:00:00-03:00",
                "series_id": 1,
                "valor": 45.8
            },
            {
                "timestart": "2000-01-01T00:00:00-03:00",
                "timeend": "2000-01-01T01:00:00-03:00",
                "series_id": 2,
                "valor": 34.3
            },
            {
                "timestart": "2000-01-01T00:00:00-03:00",
                "timeend": "2000-01-01T01:00:00-03:00",
                "series_id": 3,
                "valor": 22.1
            }
        ])
        observaciones = observacionesDataFrameToList(data)

        self.assertTrue(isinstance(observaciones, list), "list return type expected")
        self.assertEqual(len(observaciones),3," 3 returned observacion element expected")
        for i, observacion in enumerate(observaciones):
            self.assertEqual(type(observacion), dict, " expected type of observacion is dict. Instead, %s was found" % type(observacion))
            self.assertEqual(type(observacion["timestart"]), str,"expected str type for timestart. Instead, %s was found" % type(observacion["timestart"]))
            expected_ts = "2000-01-01T00:00:00-03:00"
            self.assertEqual(observacion["timestart"], expected_ts)
            expected_te = "2000-01-01T01:00:00-03:00"
            self.assertEqual(observacion["timeend"], expected_te)
            self.assertEqual(observacion["series_id"], i + 1)


if __name__ == '__main__':
    main()