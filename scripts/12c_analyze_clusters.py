# %%
socio_cluster_gdf["share_low_income"] = (
    socio_cluster_gdf["Income under 100k"]
    + socio_cluster_gdf["Income 100-150k"]
    + socio_cluster_gdf["Income 150-200k"]
    + socio_cluster_gdf["Income 200-300k"]
)


# %%
import plotly_express as px

fig = px.scatter(
    socio_cluster_gdf,
    x="share_low_income",
    y="Households w car",
    hover_data=["socio_label", "id"],
    color="socio_label",
)
fig.show()

# %%

# %%
# Plot socio clusters and pop/urban density
plt.figure(figsize=(15, 10))
plt.scatter(
    socio_cluster_gdf["socio_label"], socio_cluster_gdf["population_density"], alpha=0.5
)
plt.xlabel("Socio Label")
plt.ylabel("Population Density")
plt.title("Population Density by Socio Label")
plt.xticks(rotation=45)
plt.show()


plt.figure(figsize=(15, 10))
plt.scatter(socio_cluster_gdf["socio_label"], socio_cluster_gdf["urban_pct"], alpha=0.5)
plt.xlabel("Socio Label")
plt.ylabel("Urban pct")
plt.title("Urban pct by Socio Label")
plt.xticks(rotation=45)
plt.show()


# %%
# Plot distribution of network rank in each socio cluster
grouped = (
    socio_cluster_gdf.groupby("socio_label")["network_rank"]
    .value_counts()
    .unstack(fill_value=0)
)
fig, axes = plt.subplots(len(grouped), 1, figsize=(15, 20))
axes = axes.flatten()
for i, (label, data) in enumerate(grouped.iterrows()):
    axes[i].bar(data.index, data.values)
    axes[i].set_title(f"Socio Label: {label}")
    axes[i].set_xlabel("Network Rank")
    axes[i].set_ylabel("Count")
    axes[i].tick_params(labelsize=10)
plt.tight_layout()
plt.show()

# %%

# Plot proporiton of network rank in each socio cluster
correlation = (
    socio_cluster_gdf.groupby(["socio_label", "network_rank"])
    .size()
    .unstack(fill_value=0)
)
correlation = correlation.div(correlation.sum(axis=1), axis=0)
plt.figure(figsize=(15, 15))
correlation.plot(
    kind="bar", stacked=True, color=input_colors
)  # lts_color_dict.values()
plt.ylabel("Proportion", fontsize=12)
plt.title("Correlation between Socio Label and Network Rank", fontsize=14)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12, title="Network Rank", title_fontsize=10)
plt.tick_params(
    labelsize=10,
)
plt.xlabel("", fontsize=12)
plt.show()

# %%

# %%