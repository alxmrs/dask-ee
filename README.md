# dask-ee

_Google Earth Engine Feature Collections via Dask DataFrames._

[![ci](https://github.com/alxmrs/dask-ee/actions/workflows/ci-build.yml/badge.svg)](https://github.com/alxmrs/dask-ee/actions/workflows/ci-build.yml)
[![PyPi Version](https://img.shields.io/pypi/v/dask-ee.svg)](https://pypi.python.org/pypi/dask-ee)
[![Downloads](https://static.pepy.tech/badge/dask-ee)](https://pepy.tech/project/dask-ee)
[![Conda Recipe](https://img.shields.io/badge/recipe-dask--ee-green.svg)](https://anaconda.org/conda-forge/dask-ee)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/dask-ee.svg)](https://anaconda.org/conda-forge/dask-ee)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/dask-ee.svg)](https://anaconda.org/conda-forge/dask-ee)

## How to use

Install with pip:

```shell
pip install dask-ee
```

Install with conda:

```shell
conda install -c conda-forge dask-ee
```

Then, authenticate Earth Engine:

```shell
earthengine authenticate
```

In your Python environment, you may now import the library:

```python
import ee
import dask_ee
```

You'll need to initialize Earth Engine before working with data:

```python
ee.Initialize()
```

From here, you can read Earth Engine FeatureCollections like they are DataFrames:

```python
df = dask_ee.read_ee("WRI/GPPD/power_plants")
df.head()
```

These work like Pandas DataFrames, but they are lazily evaluated via [Dask](https://dask.org/).

Feel free to do any analysis you wish. For example:

```python
# Thanks @aazuspan, https://www.aazuspan.dev/blog/dask_featurecollection
(
    df[df.comm_year.gt(1940) & df.country.eq("USA") & df.fuel1.isin(["Coal", "Wind"])]
    .astype({"comm_year": int})
    .drop(columns=["geo"])
    .groupby(["comm_year", "fuel1"])
    .agg({"capacitymw": "sum"})
    .reset_index()
    .sort_values(by=["comm_year"])
    .compute(scheduler="threads")
    .pivot_table(index="comm_year", columns="fuel1", values="capacitymw", fill_value=0)
    .plot()
)
```

![Coal vs Wind in the US since 1940](https://raw.githubusercontent.com/alxmrs/dask-ee/main/demo.png)

There are a few other useful things you can do.

For one, you may pass in a pre-processed `ee.FeatureCollection`. This allows full utilization
of the Earth Engine API.

```python
fc = (
  ee.FeatureCollection("WRI/GPPD/power_plants")
  .filter(ee.Filter.gt("comm_year", 1940))
  .filter(ee.Filter.eq("country", "USA"))
)
df = dask_ee.read_ee(fc)
```

In addition, you may change the `chunksize`, which controls how many rows are included in each
Dask partition.

```python
df = dask_ee.read_ee("WRI/GPPD/power_plants", chunksize=7_000)
df.head()
```

## Contributing

Contributions are welcome. A good way to start is to check out open [issues](https://github.com/alxmrs/dask-ee/issues)
or file a new one. We're happy to review pull requests, too.

Before writing code, please install the development dependencies (after cloning the repo):

```shell
pip install -e ".[dev]"
```

## License

```
Copyright 2024 Alexander S Merose

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

Some sources are re-distributed from Google LLC via https://github.com/google/Xee (also Apache-2.0 License) with and
without modification. These files are subject to the original copyright; they include the original license header
comment as well as a note to indicate modifications (when appropriate).
