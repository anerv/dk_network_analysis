# Interpretation of results

## DENSITY

* Based on stack bar charts, most municipalities have comparable ratios of different levels of LTS? (of course with some variations - value ranges of LTS 1 13.6 - 43.6%, median and average around 30%, LTS 2 25-65%, mean and median around 40%.)

![alt text](results/density_distributions/administrative/lts_stacked_bar_len.jpg)

![alt text](results/density_distributions/administrative/lts_stacked_bar_dens.jpg)

At the local and grid level, obviously much larger variations.

At the global, adm and socio level, the median levels ordered after share:

* 2
* 1
* 3
* 4

(ofc total car highest)

At grid level:

* Same, but *much* closer values.
* Important to remember that LTS 3 and 4 etc. are for network used by cyclists! Not for roads with separate bike tracks.

Highly uneven distribution of both network length AND density.

Density distributions are different at various aggregation levels - but at socio and hex grid LTS 1+2 and LTS 3+4 follow roughly same distribution.

![alt text](results/density_distributions/socio/lts_kde_length.jpg)

![alt text](results/density_distributions/socio/lts_kde_density.jpg)

### Spatial distributions

* At socio level - *share* of LTS 1 is not an urban phenomenon - but absolute quantity is.
* Same for LTS 2
* Absolute values for LTS 3 a bit 'random' - but low in CPH. *Share* of LTS 3 low in larger cities.
* LTS 4 - not urban - neither based on share or absolute values.

Results for spatial autocorrelation:

#### HEX GRID

* Significant clustering of network density - obviously
* Significant clustering of LTS 1 density and LTS relative length - but not the same places!
* Sig clustering of LTS 2 dens and rel. length - overlapping but not identical clusters.
* Sig clustering of LTS 3 dens - but small scattered clusters. Slightly bigger clusters for LTS 3 share.
* LTS 4 dens - sig but sparse clustering - this might change with new results!! LTS 4 share - sig clustering, especially of low LTS 4 share.
* Car dens/car share - sig. clustering - but reversed (i.e. high dens in cities, but low share).

#### Socio

* Same for LTS 1 - mostly not the same places with a high dens and high share, but both sig.
* LTS 2 - same
* LTS 3 - sig., overlapping but not identical clusters
* LTS 4 - stronger clustering tendency than hex? Overlapping but not identical clusters for dens and share

## Fragmentation

The number of components per level (steps):

* 1-2
* 1-3
* 1
* 1-4
* Car
* Total

Mean component size ranked smallest to biggest:
(Median can be misleading - e.g. car have a few actual components and then tiny tracks and service)

* LTS 1-2
* LTS 1
* 1-3
* 1-4
* Car
* Total

Thus - LTS 1 is very fragmented - adding LTS 2 adds more network but does not result in less fragmentation! LTS 3 and 4 serve as connectors.

![alt text](results/component_size_distribution/administrative/component_distribution_muni.jpeg)

![alt text](results/component_size_distribution/socio/component_distribution_socio.jpeg)

![alt text](results/component_size_distribution/hexgrid/component_distribution_h3.jpeg)

Based on rug plots, the pattern in distribution of comp counts is similar across aggregation levels.

![alt text](results/component_size_distribution/combined_zipf.png)

Zipf plot confirms that LTS 4 works as connector (OBS - does this change after data update??)

![alt text](results/component_density_correlation/socio/component_count_infra_density_all_areas.jpeg)

Interpretation - for LTS 1, comp count increases with density/mixed picture - for LTS 1-2 and 1-3 it decreases? (see also ind. plots) (same at muni level - no pattern at hex level).

Some spatial clustering of comp per sqkm or km for lower LTS - less fragmentation around larger cities. (at socio level)

At hex grid:

* Longer largest components around CPH and across Sjælland
* Some clustering in component per length (lower in urban areas)
* But genereally very low Moran's I!

## Reach

![alt text](results/reach_distributions/kde_network_reach.png)

* As expected based on density and fragmentation results?
* Low reach for both LTS 1 and LTS 1-2
* A bit better for 1-3
* LTS 4 and car similar - and highest
* There are a few locations with more reach for bikes than cars

* Confirms picture from fragmentation:
* Average reach is from smallest to biggest: 1, 1-2, 1-3, car, 1-4, (OBS on car) (OBS - might change with update??)
* But for median reach is LTS 1-2 smaller than 1 because of smaller LTS 2 components

### Comparing reach

* Because of fragmentation, the majority of LTS 1 and LTS 1-2 cells have no improvement in reach when increasing distance.

* For LTS 1-3 it is around a third

* Almost no LTS 1-4 cells have no improvements.

![alt text](results/reach_distance_comparisons/distance_comparison_bar_mean.png)

![alt text](results/reach_distance_comparisons/distance_comparison_violin.png)

![alt text](results/reach_distance_comparisons/reach_diff_pct_kde_5_15.png)

* Clear spatial patterns in reach - both for distance 5 reach and for where there is no reach increase when increasing distance!

## Correlation

## Spatial weights sensitivity tests


