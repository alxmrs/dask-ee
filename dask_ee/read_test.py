import unittest


class ReadFeatureCollections(unittest.TestCase):

  def test_can_import_read_op(self):
    try:
      from dask_ee import read_ee
    except ModuleNotFoundError:
      self.fail('Cannot import `read_ee` function.')


if __name__ == '__main__':
  unittest.main()
