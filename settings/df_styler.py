import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

exec(open("../settings/plotting.py").read())
exec(open("../settings/yaml_variables.py").read())

# summarize_results_df.style.pipe(format_osm_style)


# General settings
cell_hover = {"selector": "td:hover", "props": [("background-color", "#ffffb3")]}

row_hover = {"selector": "tr:hover", "props": [("background-color", "#eff7fa")]}

caption = {
    "selector": "caption",
    "props": "caption-side: top; text-align:center; font-weight: bold; font-size:20px; color: white;",
}

cell_style = {"selector": "td", "props": "text-align: center; font-weight: bold; "}

index_styler = {
    "selector": ".index_name",
    "props": f"color:{"black"}; font-size:14px;", 
}

columns_styler = {
    "selector": "th",
    "props": f"color: {"black"}; font-size:14px;",
}

pct_formatter={
            "min_share": lambda x: f"{x:,.1f}%",
            "mean_share": lambda x: f"{x:,.1f}%",
            "median_share": lambda x: f"{x:,.1f}%",
            "max_share": lambda x: f"{x:,.1f}%",
            "std_dev (share)": lambda x: f"{x:,.1f}%",
            "more_bike_share": lambda x: f"{x:,.1f}%",

        }

# Make individual ones based on columns with %, and titles
def format_style_index(styler):
    #styler.set_caption(f"MY TITLE")
    caption_here = caption.copy()
    caption_here["props"] += "background-color: " + "black" + ";"
    styler.format(precision=2, na_rep=" - ", thousands=",", formatter=pct_formatter)
    styler.set_table_styles(
        [cell_hover, row_hover, columns_styler, caption_here, index_styler, cell_style],
        overwrite=False,
    )
    styler.map_index(
        lambda v: f"color:{"black"}; font-size:14px;",
        axis=0,
    )

    return styler

def format_style_no_index(styler):
    #styler.set_caption(f"MY TITLE")
    caption_here = caption.copy()
    caption_here["props"] += "background-color: " + "black" + ";"
    styler.format(precision=2, na_rep=" - ", thousands=",", formatter=pct_formatter)
    styler.set_table_styles(
        [cell_hover, row_hover, columns_styler, caption_here, index_styler, cell_style],
        overwrite=False,
    )
    styler.hide(axis="index")
    return styler

