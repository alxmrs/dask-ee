import unittest


class ImportTest(unittest.TestCase):

  def test_can_import_module(self):
    try:
      import dask_ee
    except ModuleNotFoundError:
      self.fail('Cannot import `dask_ee`.')


if __name__ == '__main__':
  unittest.main()
