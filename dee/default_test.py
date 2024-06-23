import unittest


class ImportTest(unittest.TestCase):

  def test_can_import_dee(self):
    try:
      import dee
    except ModuleNotFoundError:
      self.fail('Cannot import `dee`.')


if __name__ == '__main__':
  unittest.main()
