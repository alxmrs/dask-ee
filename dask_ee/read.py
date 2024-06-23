# Implementation heavily inspired by @aazuspan via
#  https://medium.com/@aa.zuspan/parallelizing-earth-engine-feature-collections-with-dask-bc6cdf9e2f48
# Taken with permission.
# Independent equivalent design was drawn up here:
#  https://docs.google.com/document/d/1Ltl6XrZ_uGD2J7OW1roUsxhpFxx5QvNeInjuONIkmL8/edit
import typing as t

import dask.dataframe as dd
import ee
import numpy as np
import pandas as pd

# Order is in appearance of types in the EE documentation. This looks alphabetical.
_BUILTIN_DTYPES = {
    'byte': np.uint8,
    'double': np.float64,
    'float': np.float32,
    'int': np.int32,
    'int16': np.int16,
    'int32': np.int32,
    'int64': np.int64,
    'int8': np.int8,
    'long': np.int64,
    'short': np.int16,
    'uint16': np.uint16,
    'uint32': np.uint32,
    'uint8': np.uint8,
    'string': np.str_,
}


# TODO(#4): Support 'auto' chunks, where we calculate the maximum allowed page size given the number of
#  bytes in each row.
def read_ee(
    fc: ee.FeatureCollection, io_chunks: t.Union[int, t.Literal['auto']] = 5_000
) -> dd.DataFrame:

  if io_chunks == 'auto':
    raise NotImplementedError('Auto io_chunks are not implemented yet!')

  fc_size, all_info = ee.List([fc.size(), fc]).getInfo()
  columns = all_info['columns']

  # TODO(#5): Compare `toList()` to other range operations, like getting all index IDs via `getInfo()`.
  pages = [
      ee.FeatureCollection(fc.toList(io_chunks, i))
      for i in range(0, fc_size, io_chunks)
  ]

  def to_df(page: ee.FeatureCollection) -> pd.DataFrame:
    return ee.data.computeFeatures(
        {
            'expression': page,
            'fileFormat': 'PANDAS_DATAFRAME',
        }
    )

  meta = {k: _BUILTIN_DTYPES[v.lower()] for k, v in columns.items()}
  divisions = tuple(range(0, fc_size, io_chunks))

  return dd.from_map(
      to_df,
      pages,
      meta=meta,
      divisions=divisions,
  )
