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

The analysis makes use of 3 input data sets:

* A road network data set split into an edge and a node table
* A polygon data set with the Danish municipal boundaries
* A polygon data set with socio-economic data on population density, income etc.

### Road network data

The road network data set is prepared using [dk_bicycle_network](https://github.com/anerv/dk_bicycle_network).

The edge and node tables are imported in script `01_load_data.py`. For successfull data import, provide/update the table names of the input tables and the input database as needed (`config.yml`).

### Municipal boundaries

A data set with the name and spatial extent of all municipalities is provided as `../data/input/adm_boundaries/muni_boundaries.gpkg`. Update with more recent input data as needed, but do not change the filepath or attributes in the input data set.

### Socio-economic data

A data set with socio-economic variables for all voting areas is provided as `../data/processed/voting_areas.gpkg`. Update with more recent input data as needed, but do not change the filepath or attributes in the input data set.

## 4. Run analysis

* Run all Python scripts in the `scripts` folder in consecutive order. The full analysis will take several hours to complete, depending on your machine.

* All results are stored in the `results` folder.