"""Integration tests with Google Earth Engine.

Before running, please authenticate:
```
earthengine authenticate
```

"""

import unittest

import dask.dataframe as dd
import ee

import dask_ee


class ReadIntegrationTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    ee.Initialize()

  def test_reads_dask_dataframe(self):
    fc = ee.FeatureCollection("WRI/GPPD/power_plants")
    ddf = dask_ee.read_ee(fc)

    head = ddf.head()
    columns = ddf.columns

    self.assertIsNotNone(ddf)
    self.assertIsNotNone(head)
    self.assertIsInstance(ddf, dd.DataFrame)
    self.assertEqual(ddf.compute().shape, (28_664, 23))

    print(columns)
    print(head)


if __name__ == "__main__":
  unittest.main()
