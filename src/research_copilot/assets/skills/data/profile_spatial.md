---
skill_id: "profile_spatial"
version: "7.0.0"
category: "data"
domain_compatibility: ["ecology", "epidemiology", "geography"]
required_tools: ["python", "geopandas", "shapely", "pyproj"]
depends_on: ["profile_tabular"]
produces: ["data/01_ingested/spatial_profile.json"]
complexity: "advanced"
---

# Skill: Spatial Data Profiling

## Purpose
Profile geospatial data to understand coordinate systems, spatial extent, topology, and spatial autocorrelation structure.

## When to Use
- Dataset contains coordinates (lat/lon), geometries, or spatial identifiers
- Before spatial analysis, mapping, or geostatistical modeling
- When merging datasets by location

## When NOT to Use
- No spatial information in data
- Spatial resolution is too coarse for analysis (e.g., country-level only)

## Execution Protocol

### Step 1: Spatial Reference Identification
- Detect coordinate reference system (CRS): EPSG code or WKT string
- If lat/lon columns: assume EPSG:4326 (WGS84)
- If projected coordinates: identify projection type
- Flag unknown or missing CRS

### Step 2: Spatial Extent
- Bounding box: min/max latitude, min/max longitude
- Centroid: geographic center of all observations
- Spatial span: maximum pairwise distance (km)
- Area coverage: convex hull area

### Step 3: Point Pattern Analysis
- Point density: points per unit area
- Nearest neighbor distances: mean, median, SD
- Clark-Evans index: R < 1 = clustered, R = 1 = random, R > 1 = dispersed
- Ripley's K function (if N > 100): assess clustering at multiple scales

### Step 4: Spatial Autocorrelation
- Construct spatial weights matrix (k-nearest neighbors or distance band)
- Global Moran's I: overall spatial autocorrelation
- Local Moran's I (LISA): identify hot spots, cold spots, spatial outliers
- Geary's C: alternative measure (more sensitive to local differences)

### Step 5: Topology Checks
- Duplicate coordinates: count and flag
- Points outside expected bounds: e.g., lat outside [-90, 90], lon outside [-180, 180]
- Points on land vs water (if applicable)
- Coordinate precision: sufficient for analysis scale

### Step 6: Aggregation Unit Assessment (if polygon data)
- Polygon count, area distribution
- Modifiable Areal Unit Problem (MAUP) risk: results may change with different aggregation
- Neighbor relationships: queen vs rook contiguity

## Diagnostics & Interpretation

| Diagnostic | Pass | Fail → Interpret | Fail → Action |
|------------|------|-------------------|---------------|
| CRS defined | Known projection | Coordinates ambiguous | Assign CRS based on context |
| Moran's I p > 0.05 | No spatial autocorrelation | Spatial dependence present | Use spatial regression models |
| Coordinate bounds | All valid | Impossible coordinates | Correct or remove invalid points |
| Point density | Adequate for scale | Too sparse or too dense | Adjust analysis resolution |

### Red Flags
- **Swapped lat/lon**: points in ocean or wrong continent; verify coordinate order
- **Mixed CRS**: some points in different projection; unify before analysis
- **Spatial clustering (R < 0.5)**: non-independence violates standard regression assumptions
- **MAUP risk**: results at one aggregation level may not hold at another

## Output Specification
- `data/01_ingested/spatial_profile.json`: CRS, bounding box, extent, point pattern analysis, spatial autocorrelation results, topology flags

## Validation Checks
- [ ] CRS is identified or assigned
- [ ] All coordinates within valid bounds
- [ ] Spatial autocorrelation tested
- [ ] Point pattern classified (clustered/random/dispersed)
