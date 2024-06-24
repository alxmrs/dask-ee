"""Integration tests with Google Earth Engine.

Before running, please authenticate:
```
earthengine authenticate
```
"""

import cProfile
import pstats
import unittest

import dask.dataframe as dd
import ee

import dask_ee


class ReadIntegrationTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    ee.Initialize()

  def test_reads_dask_dataframe(self):
    fc = ee.FeatureCollection('WRI/GPPD/power_plants')
    df = dask_ee.read_ee(fc)

    head = df.head()
    columns = df.columns

    self.assertIsNotNone(df)
    self.assertIsNotNone(head)
    self.assertIsInstance(df, dd.DataFrame)
    self.assertEqual(df.compute().shape, (28_664, 23))

    print(columns)
    print(head)

  def test_works_with_defined_features(self):
    # Make a list of Features.
    features = [
        ee.Feature(
            ee.Geometry.Rectangle(30.01, 59.80, 30.59, 60.15),
            {'name': 'Voronoi'},
        ),
        ee.Feature(ee.Geometry.Point(-73.96, 40.781), {'name': 'Thiessen'}),
        ee.Feature(ee.Geometry.Point(6.4806, 50.8012), {'name': 'Dirichlet'}),
    ]

    fc = ee.FeatureCollection(features)

    df = dask_ee.read_ee(fc)

    self.assertEqual(list(df.columns), ['geo', 'name'])

  def test_works_with_a_single_feature_in_fc(self):
    from_geom = ee.FeatureCollection(ee.Geometry.Point(16.37, 48.225))

    df = dask_ee.read_ee(from_geom)

    self.assertEqual(list(df.columns), ['geo'])
    self.assertEqual(df.compute().shape, (1, 1))

  def test_can_create_random_points(self):
    # Define an arbitrary region in which to compute random points.
    region = ee.Geometry.Rectangle(-119.224, 34.669, -99.536, 50.064)

    # Create 1000 random points in the region.
    random_points = ee.FeatureCollection.randomPoints(region)

    # Note: these random points have no system:index!
    df = dask_ee.read_ee(random_points)

    self.assertEqual(list(df.columns), ['geo'])
    self.assertEqual(df.compute().shape, (1000, 1))

  def test_prof__read_ee(self):
    fc = ee.FeatureCollection('WRI/GPPD/power_plants')
    with cProfile.Profile() as pr:
      _ = dask_ee.read_ee(fc)

      # Modified version of `pr.print_stats()`.
      pstats.Stats(pr).sort_stats('cumtime').print_stats()


if __name__ == '__main__':
  unittest.main()
