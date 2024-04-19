
goodresearchdev

reuse from data repo

```bash
conda config --prepend channels conda-forge
conda create -n dk_network_analysis --strict-channel-priority geopandas seaborn psycopg2 contextily sqlalchemy geoalchemy2 pyarrow h3-py pyyaml plotly plotly_express==0.4.0 ipykernel
```
