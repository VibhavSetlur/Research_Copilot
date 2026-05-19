# data_raw

**Drop zone for raw data files.**

This directory is immutable. No agent, script, or manual process may modify files placed here. Only `scripts/01_validation.py` reads from this directory.

Supported formats: CSV, XLSX, JSON, TXT, SHP, GeoJSON, Parquet, and any other format your data arrives in.
