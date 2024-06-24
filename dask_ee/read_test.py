import unittest


class ReadFeatureCollections(unittest.TestCase):

  def test_can_import_read_op(self):
    try:
      from dask_ee import read_ee
    except ModuleNotFoundError:
      self.fail('Cannot import `read_ee` function.')

  def test_rejects_auto_chunks(self):
    import dask_ee

    with self.assertRaises(NotImplementedError):
      dask_ee.read_ee('WRI/GPPD/power_plants', 'auto')


if __name__ == '__main__':
  unittest.main()
