# %%

import pandas as pd
import numpy as np
import pandas as pd
from IPython.display import display
from src import db_functions as dbf

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
exec(open("../settings/df_styler.py").read())

# %%


engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

socio = pd.read_sql("SELECT * FROM socio", con=engine)

socio.rename(population_rename_dict, inplace=True, axis=1)

socio["Income under 150k (%)"] = (
    socio["Income under 100k (%)"] + socio["Income 100-150k (%)"]
)

# %%
display(socio[socio_corr_variables].describe().T)
# %%
