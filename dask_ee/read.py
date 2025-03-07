# Special thanks to @aazuspan for help with the implementation
import typing as t

import dask.dataframe as dd
import ee
import numpy as np
import pandas as pd

# Order is in appearance of types in the EE documentation. This looks alphabetical.
_BUILTIN_DTYPES = {
    'Byte': np.uint8,
    'Double': np.float64,
    'Float': np.float32,
    'Int': np.int32,
    'Integer': np.int32,
    'Int16': np.int16,
    'Int32': np.int32,
    'Int64': np.int64,
    'Int8': np.int8,
    'Json': np.object_,  # added to handle GeoJSON columns.
    'Long': np.int64,
    'Short': np.int16,
    'Uint16': np.uint16,
    'Uint32': np.uint32,
    'Uint8': np.uint8,
    'String': np.str_,
}


def read_ee(
    fc: t.Union[ee.FeatureCollection, str],
    chunksize: t.Union[int, t.Literal['auto']] = 5_000,
) -> dd.DataFrame:
  """Read Google Earth Engine FeatureCollections into a Dask Dataframe.

  Args:
    fc: A Google Earth Engine FeatureCollection or valid string path to a FeatureCollection.
    chunksize: The number of rows per partition to use.

  Returns:
    A dask DataFrame with paged Google Earth Engine data.
  """
  # TODO(#4): Support 'auto' chunks, where we calculate the maximum allowed page size given the number of
  #  bytes in each row.
  if chunksize == 'auto':
    raise NotImplementedError('Auto chunksize is not implemented yet!')

  if isinstance(fc, str):
    fc = ee.FeatureCollection(fc)

  # Make all the getInfo() calls at once, up front.
  fc_size, all_info = ee.List([fc.size(), fc.limit(0)]).getInfo()

  columns = {'geo': 'Json'}
  columns.update(all_info['columns'])
  if 'system:index' in columns:
    del columns['system:index']

  divisions = tuple(range(0, fc_size, chunksize))

  # TODO(#5): Compare `toList()` to other range operations, like getting all index IDs via `getInfo()`.
  pages = [ee.FeatureCollection(fc.toList(chunksize, i)) for i in divisions]
  # Get the remainder, if it exists. `chunksize` is not likely to evenly partition the data.
  d, r = divmod(fc_size, chunksize)
  if r != 0:
    pages.append(ee.FeatureCollection(fc.toList(r, d)))
    divisions += (fc_size,)

  def to_df(page: ee.FeatureCollection) -> pd.DataFrame:
    return ee.data.computeFeatures(
        {
            'expression': page,
            'fileFormat': 'PANDAS_DATAFRAME',
        }
    )

  meta = {k: _BUILTIN_DTYPES[v] for k, v in columns.items()}

  return dd.from_map(
      to_df,
      pages,
      meta=meta,
      divisions=divisions,
  )
