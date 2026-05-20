#!/usr/bin/env python3
"""
Context7 Documentation Lookup System
Resolves library IDs and retrieves API documentation, integrating with ResearchCache.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Import ResearchCache
sys.path.append(str(Path(__file__).parent.parent.parent))
from scripts.utils.cache_manager import ResearchCache

# Curated documentation database for scientific and visualization libraries
MOCK_DOCS = {
    "pandas": {
        "id": "lib_pandas_v2",
        "groupby": "DataFrame.groupby(by=None, axis=0, level=None, as_index=True, sort=True, group_keys=True, observed=False, dropna=True)\n\nGroups DataFrame using a mapper or by a Series of columns.",
        "merge": "DataFrame.merge(right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=None, indicator=False, validate=None)\n\nMerge DataFrame or named Series objects with a database-style join.",
    },
    "scipy": {
        "id": "lib_scipy_v1",
        "ttest_ind": "scipy.stats.ttest_ind(a, b, axis=0, equal_var=True, nan_policy='propagate', permutations=None, random_state=None, alternative='two-sided', trim=0)\n\nCalculate the T-test for the means of two independent samples of scores.",
        "wilcoxon": "scipy.stats.wilcoxon(x, y=None, zero_method='pratt', correction=False, alternative='two-sided', method='auto', axis=0, nan_policy='propagate', keepdims=False)\n\nCalculate the Wilcoxon signed-rank test.",
    },
    "sklearn": {
        "id": "lib_sklearn_v1",
        "LinearRegression": "sklearn.linear_model.LinearRegression(*, fit_intercept=True, copy_X=True, n_jobs=None, positive=False)\n\nOrdinary least squares Linear Regression.",
        "train_test_split": "sklearn.model_selection.train_test_split(*arrays, test_size=None, train_size=None, random_state=None, shuffle=True, stratify=None)\n\nSplit arrays or matrices into random train and test subsets.",
    },
    "statsmodels": {
        "id": "lib_statsmodels_v0",
        "OLS": "statsmodels.regression.linear_model.OLS(endog, exog=None, missing='none', hasconst=None, **kwargs)\n\nOrdinary Least Squares regression model.",
    },
    "altair": {
        "id": "lib_altair_v5",
        "Chart": "altair.Chart(data=None, encoding=None, width=None, height=None, **kwargs)\n\nCreate an Altair Chart object.",
    },
    "bokeh": {
        "id": "lib_bokeh_v3",
        "figure": "bokeh.plotting.figure(*args, **kwargs)\n\nCreate a new Figure for plotting.",
    },
    "panel": {
        "id": "lib_panel_v1",
        "Row": "panel.Row(*objects, **params)\n\nLayout component that lays out its children horizontally.",
    },
    "holoviews": {
        "id": "lib_holoviews_v1",
        "Dataset": "holoviews.Dataset(data, kdims=None, vdims=None, **kwargs)\n\nWrapper for tabular/multidimensional datasets.",
    },
    "plotly": {
        "id": "lib_plotly_v5",
        "scatter": "plotly.express.scatter(data_frame=None, x=None, y=None, color=None, symbol=None, size=None, hover_name=None, hover_data=None, custom_data=None, text=None, facet_row=None, facet_col=None, facet_col_wrap=0, facet_row_spacing=None, facet_col_spacing=None, marginal_x=None, marginal_y=None, trendline=None, trendline_options=None, trendline_color_override=None, log_x=False, log_y=False, range_x=None, range_y=None, render_mode='auto', title=None, template=None, width=None, height=None)\n\nCreate an interactive scatter plot.",
    }
}


def resolve_library_id(library_name: str, cache: ResearchCache) -> str:
    lib_clean = library_name.strip().lower()
    cache_query = f"context7:resolve:{lib_clean}"
    
    # Check cache
    cached_val = cache.get_web_search(cache_query)
    if cached_val:
        return cached_val[0]["library_id"]
        
    # Resolve
    if lib_clean in MOCK_DOCS:
        lib_id = MOCK_DOCS[lib_clean]["id"]
    else:
        lib_id = f"lib_{lib_clean}_generic"
        
    # Cache result for 30 days
    cache.set_web_search(cache_query, [{"library_id": lib_id}], ttl_days=30.0)
    return lib_id


def get_library_docs(library_id: str, topic: str, cache: ResearchCache) -> str:
    topic_clean = topic.strip().lower()
    cache_query = f"context7:docs:{library_id}:{topic_clean}"
    
    # Check cache
    cached_val = cache.get_web_search(cache_query)
    if cached_val:
        return cached_val[0]["docs"]
        
    # Retrieve
    # Try to match the library ID back to mock docs
    lib_name = None
    for name, data in MOCK_DOCS.items():
        if data["id"] == library_id:
            lib_name = name
            break
            
    docs = None
    if lib_name and topic_clean in MOCK_DOCS[lib_name]:
        docs = MOCK_DOCS[lib_name][topic_clean]
    else:
        docs = f"Documentation for {topic} in {library_id}:\nNo detailed offline doc available. Refer to online specifications."
        
    # Cache result for 30 days
    cache.set_web_search(cache_query, [{"docs": docs}], ttl_days=30.0)
    return docs


def main():
    parser = argparse.ArgumentParser(description="Context7 Documentation Lookup Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Resolve sub-command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve library name to Context7 ID")
    resolve_parser.add_argument("library", help="Standard name of the library (e.g. pandas)")
    
    # Docs sub-command
    docs_parser = subparsers.add_parser("docs", help="Retrieve API documentation for a resolved library ID")
    docs_parser.add_argument("library_id", help="The resolved Context7 library ID")
    docs_parser.add_argument("topic", help="The function, class, or topic to lookup")
    
    args = parser.parse_args()
    cache = ResearchCache()
    
    if args.command == "resolve":
        lib_id = resolve_library_id(args.library, cache)
        print(lib_id)
        sys.exit(0)
        
    elif args.command == "docs":
        docs = get_library_docs(args.library_id, args.topic, cache)
        print(docs)
        sys.exit(0)


if __name__ == "__main__":
    main()
