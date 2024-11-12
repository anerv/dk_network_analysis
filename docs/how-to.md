# HOW TO

## 1. Installation

For instructions for setting up PostgreSQL and Python, see [*docs/installation.md*](docs/installation.md).

## 2. Setup

### Fill out the configuration file

In order to run the code, the configuration file [`config.yml`](config.yml) must be filled out.

Plot settings can be changed in [`scripts/settings/plotting.py`](scripts/settings/plotting.py).

### Set up the folder structure

Next, to create the required folder structure, navigate to the main folder in a terminal window and run the Python file `setup_folders.py`

```python
python setup_folders.py
```

This should return:

```python
Successfully created folder data
Successfully created folder results
...
```

## 3. Provide input data

The analysis makes use of 5 input data sets:

* A road network data set split into an edge and a node table
* A polygon data set with the Danish municipal boundaries
* A polygon data set with socio-economic data on population density, income etc.
* A polygon data set with areas classified as urban.

### Road network data

The road network data set is prepared using [dk_bicycle_network](https://github.com/anerv/dk_bicycle_network).

The edge and node tables are imported in script `01_load_data.py`. For successfull data import, provide/update the table names of the input tables and the input database as needed (`config.yml`).

### Municipal boundaries

A data set with the name and spatial extent of all municipalities is provided as `../data/input/municipalities/muni_boundaries.gpkg`. Update with more recent input data as needed, but do not change the filepath or attributes in the input data set.

### Socio-economic data

A data set with socio-economic variables for all voting areas is provided as `../data/processed/voting_areas.gpkg`. Update with more recent input data as needed, but do not change the filepath or attributes in the input data set. To recreate the data with newer input data, replace the files in `../data/input/socioeconomic` and run script `00_prepare_socioeconomic_data.py`.

### Urban areas

A data set with polygons representing areas classified as urban, provided as `../data/input/urban/urban_areas.parquet`. Update with more recent input data as needed, but do not change the filepath or attributes in the input data set.

### Population data

Get the latest population data from GHSL: [https://human-settlement.emergency.copernicus.eu/download.php?ds=pop](https://human-settlement.emergency.copernicus.eu/download.php?ds=pop).

1. Download the two raster data sets covering the entire extent of Denmark.
2. Place the downloaded zip-files in the folder `data/population/`.
3. Unzip the zip files.
4. Update the filepaths `pop_fp_1` and `pop_fp_2` in `config.yml` if needed.

## 4. Run analysis

* Run all Python scripts in the `scripts` folder in consecutive order. The full analysis will take several hours to complete, depending on your machine.

* All results are stored in the `results` folder.
