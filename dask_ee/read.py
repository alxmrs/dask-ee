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


# TODO(#4): Support 'auto' chunks, where we calculate the maximum allowed page size given the number of
#  bytes in each row.
def read_ee(
    fc: ee.FeatureCollection, io_chunks: t.Union[int, t.Literal['auto']] = 5_000
) -> dd.DataFrame:

  if io_chunks == 'auto':
    raise NotImplementedError('Auto `io_chunks` are not implemented yet!')

  # Make all the getInfo() calls at once, up front.
  fc_size, all_info = ee.List([fc.size(), fc]).getInfo()

  columns = {'geo': 'Json'}
  columns.update(all_info['columns'])
  del columns['system:index']

  divisions = tuple(range(0, fc_size, io_chunks))

  # TODO(#5): Compare `toList()` to other range operations, like getting all index IDs via `getInfo()`.
  pages = [ee.FeatureCollection(fc.toList(io_chunks, i)) for i in divisions]
  # Get the remainder, if it exists. `io_chunks` are not likely to evenly partition the data.
  d, r = divmod(fc_size, io_chunks)
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
