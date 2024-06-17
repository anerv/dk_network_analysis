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
* Sig. clustering in reach differences - high differences in 5-10/5-15 in urban areas - and some others! - low in non urban for LTS 1, 1-2. Opposite for LTS 4 and car.

## Correlation

### Socio socio

**Under 100k:**

* Very low income positively correlated with other low income - with decreasing strength - up untill 500+ K, which is negatively correlated
* Very low income is negatively correlated with share of households with cars
* Positive with urban pct and pop density

**100-150k:**

* Similar for income 100-150 - but even stronger association with urban, pop, no car

**Income 150-200 + 200-300:**

* Similar, but positive corr with share of households with 1 car - but negative with 2!
* Positive but weak corr with pop and urban

**Income 400 - 500k:**

* positive corr with almot all income groups - but weak, except 200-300,400-400, and negative for 750+!
* Positive for share of households with 1 car, but negative for households with 2 cars --> results in negative in households w car and pos for no car
* Weak positive corr with urban, pop

**Income 500-750k:**

* Negativ corr with all income segments except 400-500 and 750+
* Strong positive with cars and 2 cars (!) - weaker positive corr with 1 car
* Negative corr with pop density and urban

**Income 750+:**

* Negative corr with all groups except 500-750
* Positive corr with car and 2 cars - but negative with 1 car!
* Negative corr with pop dens and urban (but only weak corr for urban)
* Fairly weak positive corr with total number of households with cars

**1 car:**

* Negatively correlated with two lowest income groups
* Positively corr with 3-6
* Negatively with two higest
* Quite weak corr between 1 car and 2 car
* Negative with urban and pop

**2 cars:**

* Negative corr with all income groups except two highest
* Strong positive corr with households with car
* Strong negative corr with pop and urban pct

**POP & Urban pct:**

* Pop and urban have similar corrs
* Positive with lower income groups - up to 200-300 k for pop and 300-400k for urban
* Negative with higer incomes
* Negative with car ownership

## Socio density

* Lower income groups live in areas with higher network density and higher density of low LTS network
* Medium income weak positive corr with high density/high lts 1 and 2 density
* High income live in low density areas, low dens of lts 1 and 2
* Negative corr with 1 and 2 dens and total network dens vs. cars
* Positve corr with 3 and 4 dens and cars (might change with updated data!)

## Socio fragmentation

* Low income associated with lower fragmentation of LTS 1 and 2 networks
* weak both pos and negative corr with middle income and lts 1 and 2 fragmentation
* 500-700 live in areas iwth high fragmentation of 1-3 lts but low fragmenation of lts 4
* weaker pattern for 750+ (they live in slightly more urban areas?)

* Car ownership positively correlated with fragmentation of low lts network - negatively correlated with fragmentation of car and lts 4 network

## Socio reach

* High network reach possitive cor with income groups up to 300-400k - this group has slightly negative corr with network reach
* Slightly positive for 400-500
* Negative for high income - especially 500-700 (matches results for fragmentation and dens?)

## Socio network
 
* Positive corr between LTS 1 and 2 density
* Positive corr between 3 and 4
* Negative corr between 1-2 and 3-4 (weaker for 3!)
* Also holds for relative length!

* Negative corr between lts 1 dens and lts comp count and comp per length - but positive with 4 and car comp count and comp per length
* Similar with lts 2

* On the other hand, high lts 3 and 4 positively correlated with many components of LTS 1 and 2 (lts 4 density also positively correlated with many lts 3 comps!)

* BUT - high lts 3 and 4 density is negatively correlated with all levels of network reach! Only positively correlated with differences in 5-10 and 10-15 reach for own LTS level

* High fragmentation results in low network reach

## Hex network

* Much weaker pattern between components/fragmentation and density

* Similar pattern as socio with areas with high 1-2 and low 3-4 and vice versa.

* Different pattern for relative length - high relative LTS X is usually negatively associated with high relative lenght of other levels - because of the scale.

* Reach corrs a bit different - still a stronger pos corr between LTS 1 reach and lts 4 dens, but also a weak positive corr between lts 4 dens and lts 4 reach (same for 3)

* Reach comparison interesting - a high jump from lts 1 and lts 2 5 to 10 reach or 10 to 15 is associoated with low 3 and 4 dens. For LTS 3, associated with low lts 4 dens. For 4, associated with low lts 1-2 dens to, weaker assoc wiht low lts 3 --> seems like good network reach for low lts do not happen in areas with high lts 4, and vice versa.

## Spatial weights sensitivity tests

### Socio densi

Moran's I decrease for most LTS levels as K increase, clusters increase - but smaller differences and still positive

Same for relative length - mostly the same, but smaller variations

### Hex grid densi

Usually higest Moran's I for smallest k - but only smaller differences.

### Socio fragmentation

Similar - does change number of areas in clusters, but does not change the general trend/global value a lot

### Hex fragmentation