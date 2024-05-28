# Interpretation of results

LTS 1 and LTS 2 make up a big part of the bikeable/driveable network!
LTS 4 is not a lot - but very important for reach!
Also significant portion not available to cars (but these are mostly just tracks??)

Large differences between munis in how much of the network is 1, 2, 3, etc.

Value ranges are larger at a fine scale.

Density and connectivity are correlated - at some scales

Much higher fragmentation for more bikefriendly network

Tendency to have a lot of high ranked roads in cities - but not only cities - does not have to be an urban thing

The question is - is high share a goal? Is minimum share enough?

## Density - MAPS

### MUNI

#### ABSOLUTE

- For absolute densities - highest in cities for LTS 1 and 2
- Much less consistent pattern for LTS 3
- LTS 4 low around CPH - otherwise also inconsistent pattern - but distinct from pattern for lts 3

#### SHARE

- Large variation in municipal SHARE of LTS 1%
    - Cluster of high density around CPH, but otherwise no discernible pattern?
- Higher shares of LTS 2 % at Sjælland and around CPH, Odense, Aarhus
- Higher shares of LTS 3 % outside of the cities (CPH, Aarhus, Odense)
- Same for LTS 4% - low share in cities - but different munis with highest share than for LTS 3
- Total car also highest outside of cities

### Socio

#### ABSOLUTE

- LTS 1 - clusters around cities - especially but not only CPH
- Also some small high density areas outside of cities
- Similar pattern for LTS 2 (also mostly same clusters)
- LTS 3 almost reversed from LTS 1 and 2 - mostly outside cities - but also large variations
- LTS 4 also mostly outside of cities - very low around CPH - but not same pattern as LTS 3!

#### SHARE 

- somewhat random pattern for LTS 1
- LTS 2 share highest around cities and coastal?
- LTS 3 share low around cities, otherwise kind of random pattern?
- same for LTS 4 but even stronger tendency
- Total car share lowest around cities

### H3

#### ABSOLUTE

- LTS 1: High density around cities, especially CPH/Fingerplanen
- LTS 2: same - but even more clustered around cities/towns
- LTS 3: very dispersed - but lower in cities
- LTS 4: dispersed, low/none in cites, clear clusters around major roads - might change as I update data!

#### Share

- LTS 1 share is mixed - highest around non-urban/recreational areas?
- LTS 2 share highest around coastal areas and towns
- LTS 3 share lowest around cities! otherwise dispersed/everywhere
- Same for LTS 4 - but less infra than 3
- Lowest total car share around cities/towns

- No biking - mostly highways and roads with parallel separate bike tracks
    - very clear pattern


## Density - VIOLIN

(all h3)

### Density

- LTS 1: Many with very low or zero - a long tail/top of some with high
- LTS 2: similar (but higher densities)
- LTS 3: Less skewed, lower density range, more middle values
- LTS 4: Even less skewed - some with very little, many with some, few with a high density - also low density range
- Total car - looks similar-ish to LTS 1/2 - very skewed - although fewer with zero ofc, and higher values
- Total network

## Density - KDE

### Length

- Comparing KDE plots at different levels of aggregation - socio and muni smoothens variation
- Regardless of aggregation scale, LTS 1 and 2 follow approximately same distribution, LTS 3 and 4 follow *approx* the same, and car and full network follow very similar distribution (also same for lenght vs. density - similar follows, but very different pattern!)

At the muni level, 1+2 and full + car are most clustered/not skewed, 3 and 4 have a long wide tail with areas with low/medium length
At the local level, same

At the grid level, different picture - total network still similar, but now both lts 3-4 and lts 1+2 have wider tails - even widest for lts 1+2

### Density

## Fragmentation - zip

For total data set - similar shaped distributions, but:

- 4, total, car, almost same (also overlapping data)
- no very small car components
- 1,2,3 somewhat similar, but more components (and larger) for LTS 2
- For smaller comp sizes, lts 1 and 3 follow similar shape - for larger sizes 1 and 2 are more similar
- smallest largest component among lts 1

At municipal level - look somewhat similar, but there are differences!

## Fragmentation - correlation w density/length

### MUNI

- LTS 1: munis with high length, low density --> high fragmentation
- LTS 1-2: same (but some exceptions) - density controls fragmentation generally
- LTS 1-3: same
- LTS 1-4: much less consistent pattern - still some tendency, but many outliers
- car, all: even less pattern

Always tendency for lower comp count in high density low length munis.

### SOCIO

- LTS 1: still correlation between comp ocunt and density, but more outliers/exceptions
- LTS 1-2: low density = high component count - also some positive correlation with length and comp count
- LTS 1-3: same, but more dispersed
- 1-4: very little pattern
- same for car and all

### H3

At grid level, high density equals high comp count - patterns are hard to discern at this level? Too local

### Scatter plots

For lts 1, 2, 3 - some indication that low density results in higher component count at municipal level
At socio/local - same-ish, but also many exceptions. Higher comp count for lts 1-2 than 1 - but also higher density. Lower comp count for lts 1-3 - but higher density than 1-2.
Very hard to identify pattern at the grid level 

### Rug plots

Somewhat similar across aggregation

- Total, car, 4: no with very high count
- 1 and 1-3 in between
- 1-2 many with high count, much higher range

## Fragmentation - local component count

### MUNI

- LTS 1 - lowest component count around CPH, Roskilde, and Aarhus (large variation in this class as well though!)
- similar ish for LTS 1-2 - but lowest for greater CPH
- similar-ish for LTS 1-3
- different pattern for LTS 1-4 - and much lower component count (at this level, general fragmentation of network seems to be the issue)

### SOCIO

- lowest lts 1 component count around greater cph - but also in other areas
- 1-2 even more clusters of low count arounad cph, central aarhus, central odense
- 1-3 mostly similar
- 1-4 - most places very low count, a few with high - often geography driven for very high areas (islands)

### H3

- LTS 1 comp count becomes proxy for density?
- LTS 1-2 is lower or same in areas with high density! (but higher range)
- LTS 1-3 same - but even stronger tendency to low comp count in high dens? (and lower range than 1-2)
- LTS 1-4 - very low count in most places, but a few with very high - investigate

## Spatial weights sensitivity

All positive significant spatial auto!
Only very few examples of the different weights changing the direction - and only in cases with already very low Moran's I. Better results for smaller K.

### Reach

Comparing K = 6, 18, 36 for hex grids

Highest Moran's I with w2, but w1 and w2 almost similar
More grid cells are in significant clusters with w3?
Same pattern across all LTS levels.

### Density

Comparing:
hex_ks = [6, 18, 36]
muni_ks = [3, 5, 7]
socio_ks = [4, 8, 12]

#### Administrative

##### Individual LTS

Moran's I is sometimes slightly smaller or similar for w3, w1 and w2 identical, clusters bigger.

##### Relative length

w3 tends to be smaller than w1 and w2, clusters bigger.

#### Socio

#### Ind LTS

w3 smaller, w1 and w2 mostly similar - but sometimes slightly different pattern than at adm level.

Clusters again bigger for w3.

Similar for relative length.

#### Hex grid

w3 significantly lower, w3 clusters bigger.
Both for ind. and rel. density.

### Fragmentation

#### Adm

##### Comp count

Similar Moran's I, larger clusters for w3.
w3 larger, positive for car and total - but very small - w1 and w2 negative but very small.

##### Comp count per km

w3 usually lower.

Same for socio and hexgrid.

Comp per length usually very low.