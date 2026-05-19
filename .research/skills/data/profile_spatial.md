---
skill_id: "profile_spatial"
version: "3.0.0"
category: "data"
domain_compatibility: ["all"]
required_tools: ["python", "geopandas", "shapely"]
estimated_tokens: 2500
depends_on: []
produces: ["data/01_ingested/profile_spatial.json"]
---

# Skill: Spatial Data Profiling

## Purpose
Profile spatial and geographic vector datasets to determine geometric validity, coordinate bounds, and spatial projection properties.

## Input Specification
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spatial_path` | Path | Yes | Path to vector dataset (Shapefile, GeoJSON, GeoPackage) |

## Execution Protocol

### Step 1: Geometric Load & Projection Validation
- Ingest dataset using GeoPandas.
- Extract Coordinate Reference System (CRS) details (EPSG code or WKT string). Verify if the projection is geographic (lat/lon) or projected (meters/feet).

### Step 2: Geometric Integrity Check
- Loop through geometries using `shapely` to check:
  - `is_valid` status.
  - Presence of self-intersections or ring-orientations.
  - Count of null or empty geometries.
- Group counts by geometry type (e.g., Point, LineString, Polygon, MultiPolygon).

### Step 3: Spatial Bound Calculations
- Calculate the total bounding box coordinates (MinX, MinY, MaxX, MaxY).
- Calculate the geometric centroid of the combined features.

## Output Specification
Produces:
- `data/01_ingested/profile_spatial.json` mapping CRS, bounding limits, and invalid geometric records.

## Validation Criteria
- [ ] CRS is identified or flagged if undefined.
- [ ] Bounding boxes contain only numeric coordinates.