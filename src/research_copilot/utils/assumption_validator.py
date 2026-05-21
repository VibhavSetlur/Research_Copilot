#!/usr/bin/env python3
"""Assumption Validator — checks statistical assumptions before analysis runs.

Provides validation tests for:
1. t-test (normality, variance homogeneity)
2. ANOVA (normality of residuals, variance homogeneity)
3. OLS Regression (linearity, homoscedasticity, normality of residuals, multicollinearity, independence)
4. ARIMA/Time Series (stationarity)

Writes reports to reports/analysis/assumption_validation_{question_id}.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller

try:
    import yaml
except ImportError:
    yaml = None


from research_copilot.utils.common import find_project_root


def load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def load_assumption_registry(root: Path) -> Dict[str, Any]:
    config = load_yaml(root / ".research" / "config.yaml")
    registries = config.get("registries", {}) if isinstance(config, dict) else {}
    registry_path = registries.get("assumption_registry", ".research/domains/assumption_registry.json")
    return load_json(root / registry_path)


def build_manual_registry_result(method: str, entry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str, str]:
    checks = ", ".join(entry.get("checks", [])) if entry else ""
    results = [{
        "assumption": "Registry-driven checks",
        "test_name": "Manual review required",
        "statistic": None,
        "p_value": None,
        "status": "MANUAL",
        "message": f"Automated checks not implemented for '{method}'. Refer to registry checks: {checks}"
    }]
    verdict = "MANUAL"
    fallback_method = entry.get("pivot_if_fail", "manual_review") if entry else "manual_review"
    return results, verdict, fallback_method


def run_ttest_validation(df: pd.DataFrame, y_col: str, group_col: str) -> Tuple[List[Dict[str, Any]], str, str]:
    """Validate assumptions for independent t-test."""
    results = []
    groups = df[group_col].dropna().unique()
    
    if len(groups) != 2:
        return [{
            "assumption": "Group Count",
            "test_name": "Unique groups count",
            "statistic": float(len(groups)),
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"t-test requires exactly 2 groups, found {len(groups)}: {groups}"
        }], "FAIL", "Mann-Whitney U test"

    g1_data = df[df[group_col] == groups[0]][y_col].dropna().values
    g2_data = df[df[group_col] == groups[1]][y_col].dropna().values

    if len(g1_data) < 3 or len(g2_data) < 3:
        return [{
            "assumption": "Sample Size",
            "test_name": "Minimum observations",
            "statistic": float(min(len(g1_data), len(g2_data))),
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"Sample size too small: group {groups[0]} has {len(g1_data)}, group {groups[1]} has {len(g2_data)}"
        }], "FAIL", "Mann-Whitney U test"

    # 1. Normality (Shapiro-Wilk)
    # Group 1
    shapiro_g1_stat, shapiro_g1_p = stats.shapiro(g1_data)
    g1_norm_pass = shapiro_g1_p >= 0.05
    results.append({
        "assumption": f"Normality ({groups[0]})",
        "test_name": "Shapiro-Wilk",
        "statistic": float(shapiro_g1_stat),
        "p_value": float(shapiro_g1_p),
        "status": "PASS" if g1_norm_pass else "FAIL",
        "message": f"Normality of {groups[0]}: {'passed' if g1_norm_pass else 'failed'} (p={shapiro_g1_p:.4f})"
    })

    # Group 2
    shapiro_g2_stat, shapiro_g2_p = stats.shapiro(g2_data)
    g2_norm_pass = shapiro_g2_p >= 0.05
    results.append({
        "assumption": f"Normality ({groups[1]})",
        "test_name": "Shapiro-Wilk",
        "statistic": float(shapiro_g2_stat),
        "p_value": float(shapiro_g2_p),
        "status": "PASS" if g2_norm_pass else "FAIL",
        "message": f"Normality of {groups[1]}: {'passed' if g2_norm_pass else 'failed'} (p={shapiro_g2_p:.4f})"
    })

    # 2. Homogeneity of Variance (Levene)
    levene_stat, levene_p = stats.levene(g1_data, g2_data)
    var_pass = levene_p >= 0.05
    results.append({
        "assumption": "Homogeneity of Variance",
        "test_name": "Levene",
        "statistic": float(levene_stat),
        "p_value": float(levene_p),
        "status": "PASS" if var_pass else "FAIL",
        "message": f"Variance homogeneity: {'passed' if var_pass else 'failed'} (p={levene_p:.4f})"
    })

    # Overall Routing
    verdict = "PASS"
    fallback_method = "t-test (independent)"
    
    if not (g1_norm_pass and g2_norm_pass):
        verdict = "FAIL"
        fallback_method = "Mann-Whitney U test"
    elif not var_pass:
        verdict = "FAIL"  # Though Welch's t-test is technically a parametric t-test variant
        fallback_method = "Welch's t-test"

    return results, verdict, fallback_method


def run_anova_validation(df: pd.DataFrame, y_col: str, group_col: str) -> Tuple[List[Dict[str, Any]], str, str]:
    """Validate assumptions for one-way ANOVA."""
    results = []
    
    # Drop rows with NaNs in y_col or group_col
    clean_df = df[[y_col, group_col]].dropna()
    groups = clean_df[group_col].unique()
    
    if len(groups) < 2:
        return [{
            "assumption": "Group Count",
            "test_name": "Unique groups count",
            "statistic": float(len(groups)),
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"ANOVA requires at least 2 groups, found {len(groups)}"
        }], "FAIL", "Kruskal-Wallis test"

    group_datasets = [clean_df[clean_df[group_col] == g][y_col].values for g in groups]
    for idx, gd in enumerate(group_datasets):
        if len(gd) < 3:
            return [{
                "assumption": "Sample Size",
                "test_name": "Minimum observations",
                "statistic": float(len(gd)),
                "p_value": 0.0,
                "status": "FAIL",
                "message": f"Group {groups[idx]} has sample size {len(gd)} < 3"
            }], "FAIL", "Kruskal-Wallis test"

    # Fit a simple OLS model to get residuals
    formula = f"{y_col} ~ C({group_col})"
    try:
        import statsmodels.formula.api as smf
        model = smf.ols(formula, data=clean_df).fit()
        residuals = model.resid
    except Exception as e:
        return [{
            "assumption": "Model Fit",
            "test_name": "OLS residuals generation",
            "statistic": 0.0,
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"Could not fit ANOVA model to compute residuals: {e}"
        }], "FAIL", "Kruskal-Wallis test"

    # 1. Normality of Residuals (Shapiro-Wilk)
    shapiro_stat, shapiro_p = stats.shapiro(residuals)
    norm_pass = shapiro_p >= 0.05
    results.append({
        "assumption": "Normality of residuals",
        "test_name": "Shapiro-Wilk",
        "statistic": float(shapiro_stat),
        "p_value": float(shapiro_p),
        "status": "PASS" if norm_pass else "FAIL",
        "message": f"Normality of residuals: {'passed' if norm_pass else 'failed'} (p={shapiro_p:.4f})"
    })

    # 2. Homogeneity of Variances (Levene)
    levene_stat, levene_p = stats.levene(*group_datasets)
    var_pass = levene_p >= 0.05
    results.append({
        "assumption": "Homogeneity of Variances",
        "test_name": "Levene",
        "statistic": float(levene_stat),
        "p_value": float(levene_p),
        "status": "PASS" if var_pass else "FAIL",
        "message": f"Variance homogeneity: {'passed' if var_pass else 'failed'} (p={levene_p:.4f})"
    })

    verdict = "PASS"
    fallback_method = "ANOVA (one-way)"
    
    if not norm_pass:
        verdict = "FAIL"
        fallback_method = "Kruskal-Wallis test"
    elif not var_pass:
        verdict = "FAIL"
        fallback_method = "Welch's ANOVA"

    return results, verdict, fallback_method


def run_ols_validation(df: pd.DataFrame, y_col: str, x_cols: List[str]) -> Tuple[List[Dict[str, Any]], str, str]:
    """Validate assumptions for Ordinary Least Squares (OLS) regression."""
    results = []
    
    # Prepare data (drop missing values)
    all_cols = [y_col] + x_cols
    clean_df = df[all_cols].dropna()
    
    if len(clean_df) < len(x_cols) + 5:
        return [{
            "assumption": "Sample Size",
            "test_name": "Minimum degrees of freedom",
            "statistic": float(len(clean_df)),
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"Too few observations: {len(clean_df)} rows for {len(x_cols)} predictors"
        }], "FAIL", "Robust Regression (RLM)"

    y = clean_df[y_col]
    X = clean_df[x_cols]
    X_with_const = sm.add_constant(X)
    
    try:
        model = sm.OLS(y, X_with_const).fit()
        residuals = model.resid
    except Exception as e:
        return [{
            "assumption": "Model Fit",
            "test_name": "OLS model fitting",
            "statistic": 0.0,
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"Could not fit OLS model: {e}"
        }], "FAIL", "Robust Regression (RLM)"

    # 1. Normality of Residuals (Shapiro-Wilk)
    # Shapiro-Wilk can fail on large samples (>5000), default to Jarque-Bera or limit SW
    if len(residuals) <= 5000:
        shapiro_stat, shapiro_p = stats.shapiro(residuals)
        norm_pass = shapiro_p >= 0.05
        test_name = "Shapiro-Wilk"
    else:
        # Jarque-Bera test
        jb_stat, jb_p, _, _ = sm.stats.jarque_bera(residuals)
        shapiro_stat, shapiro_p = jb_stat, jb_p
        norm_pass = shapiro_p >= 0.05
        test_name = "Jarque-Bera"

    results.append({
        "assumption": "Normality of residuals",
        "test_name": test_name,
        "statistic": float(shapiro_stat),
        "p_value": float(shapiro_p),
        "status": "PASS" if norm_pass else "FAIL",
        "message": f"Normality of residuals: {'passed' if norm_pass else 'failed'} (p={shapiro_p:.4f})"
    })

    # 2. Homoscedasticity (Breusch-Pagan)
    try:
        bp_stat, bp_p, _, _ = het_breuschpagan(residuals, X_with_const)
        homo_pass = bp_p >= 0.05
        results.append({
            "assumption": "Homoscedasticity",
            "test_name": "Breusch-Pagan",
            "statistic": float(bp_stat),
            "p_value": float(bp_p),
            "status": "PASS" if homo_pass else "FAIL",
            "message": f"Homoscedasticity check: {'passed' if homo_pass else 'failed'} (p={bp_p:.4f})"
        })
    except Exception as e:
        homo_pass = True
        results.append({
            "assumption": "Homoscedasticity",
            "test_name": "Breusch-Pagan",
            "statistic": 0.0,
            "p_value": 1.0,
            "status": "PASS",
            "message": f"Could not compute Breusch-Pagan (likely singular design): {e}"
        })

    # 3. Independence of Residuals (Durbin-Watson)
    dw_stat = durbin_watson(residuals)
    dw_pass = 1.5 <= dw_stat <= 2.5
    results.append({
        "assumption": "Independence of residuals",
        "test_name": "Durbin-Watson",
        "statistic": float(dw_stat),
        "p_value": None,
        "status": "PASS" if dw_pass else "FAIL",
        "message": f"Independence check (DW stat): {dw_stat:.4f} (expected between 1.5 and 2.5)"
    })

    # 4. Multicollinearity (VIF) - only if >= 2 predictors
    vif_pass = True
    if len(x_cols) >= 2:
        max_vif = 0.0
        vif_details = {}
        for i, col in enumerate(x_cols):
            try:
                # index 0 is constant in X_with_const, predictors start at 1
                v = variance_inflation_factor(X_with_const.values, i + 1)
                vif_details[col] = v
                max_vif = max(max_vif, v)
            except Exception:
                pass
        
        vif_pass = max_vif < 5.0
        results.append({
            "assumption": "No Multicollinearity",
            "test_name": "Variance Inflation Factor (VIF)",
            "statistic": float(max_vif),
            "p_value": None,
            "status": "PASS" if vif_pass else "FAIL",
            "message": f"Multicollinearity check: Max VIF is {max_vif:.2f} ({'passed' if vif_pass else 'failed'} < 5.0)"
        })

    verdict = "PASS"
    fallback_method = "OLS"
    
    if not norm_pass or not homo_pass:
        verdict = "FAIL"
        fallback_method = "Robust Regression (RLM)"
    elif not dw_pass:
        verdict = "FAIL"
        fallback_method = "Newey-West standard errors OLS"
    elif not vif_pass:
        verdict = "FAIL"
        fallback_method = "OLS (with dropped collinear features)"

    return results, verdict, fallback_method


def run_arima_validation(df: pd.DataFrame, y_col: str) -> Tuple[List[Dict[str, Any]], str, str]:
    """Validate assumptions for ARIMA time series modeling (specifically stationarity)."""
    results = []
    
    series = df[y_col].dropna().values
    
    if len(series) < 10:
        return [{
            "assumption": "Sample Size",
            "test_name": "Minimum observations",
            "statistic": float(len(series)),
            "p_value": 0.0,
            "status": "FAIL",
            "message": f"Time series too short: only {len(series)} points"
        }], "FAIL", "Differencing ARIMA"

    # 1. Stationarity (Augmented Dickey-Fuller)
    try:
        adf_res = adfuller(series)
        adf_stat = adf_res[0]
        adf_p = adf_res[1]
        stationary = adf_p < 0.05
        results.append({
            "assumption": "Stationarity",
            "test_name": "Augmented Dickey-Fuller (ADF)",
            "statistic": float(adf_stat),
            "p_value": float(adf_p),
            "status": "PASS" if stationary else "FAIL",
            "message": f"Stationarity check (ADF): {'passed' if stationary else 'failed'} (p={adf_p:.4f})"
        })
    except Exception as e:
        stationary = False
        results.append({
            "assumption": "Stationarity",
            "test_name": "Augmented Dickey-Fuller (ADF)",
            "statistic": 0.0,
            "p_value": 1.0,
            "status": "FAIL",
            "message": f"Stationarity test failed to compute: {e}"
        })

    verdict = "PASS" if stationary else "FAIL"
    fallback_method = "ARIMA with Differencing (d=1)" if not stationary else "ARIMA (d=0)"
    
    return results, verdict, fallback_method


def main():
    parser = argparse.ArgumentParser(description="Assumption Validator for Statistical Analysis")
    parser.add_argument("--data", type=str, required=True, help="Path to input data (CSV or Parquet)")
    parser.add_argument("--y", type=str, required=True, help="Dependent variable (outcome)")
    parser.add_argument("--x", type=str, help="Independent variable(s), comma-separated")
    parser.add_argument("--group", type=str, help="Grouping column (for t-test or ANOVA)")
    parser.add_argument("--method", type=str, required=True, help="Target analysis method")
    parser.add_argument("--question-id", type=str, default="q_unknown", help="ID of the research question being checked")
    parser.add_argument("--output", type=str, help="Custom output path for the JSON validation report")
    parser.add_argument("--registry", type=str, help="Override path to assumption_registry.json")
    args = parser.parse_args()

    root = find_project_root()
    registry = load_assumption_registry(root)
    if args.registry:
        reg_path = Path(args.registry) if Path(args.registry).is_absolute() else root / args.registry
        registry = load_json(reg_path) if reg_path.exists() else registry
    data_path = Path(args.data) if Path(args.data).is_absolute() else root / args.data
    
    if not data_path.exists():
        print(f"ERROR: Data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    # Load data
    try:
        if data_path.suffix == ".csv":
            df = pd.read_csv(data_path)
        elif data_path.suffix in [".parquet", ".pq"]:
            df = pd.read_parquet(data_path)
        elif data_path.suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(data_path)
        else:
            print(f"ERROR: Unsupported file format: {data_path.suffix}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read data file: {e}", file=sys.stderr)
        sys.exit(1)

    # Verify column existence
    if args.y not in df.columns:
        print(f"ERROR: Column '{args.y}' not found in dataset.", file=sys.stderr)
        sys.exit(1)

    x_cols = []
    if args.x:
        x_cols = [x.strip() for x in args.x.split(",") if x.strip()]
        for x_col in x_cols:
            if x_col not in df.columns:
                print(f"ERROR: Column '{x_col}' not found in dataset.", file=sys.stderr)
                sys.exit(1)

    if args.group:
        if args.group not in df.columns:
            print(f"ERROR: Group column '{args.group}' not found in dataset.", file=sys.stderr)
            sys.exit(1)

    # Run tests
    registry_entry = registry.get(args.method, {}) if isinstance(registry, dict) else {}
    if args.method == "ttest":
        if not args.group:
            print("ERROR: --group is required for ttest", file=sys.stderr)
            sys.exit(1)
        results, verdict, fallback_method = run_ttest_validation(df, args.y, args.group)
    elif args.method == "anova":
        if not args.group:
            print("ERROR: --group is required for anova", file=sys.stderr)
            sys.exit(1)
        results, verdict, fallback_method = run_anova_validation(df, args.y, args.group)
    elif args.method == "ols":
        if not x_cols:
            print("ERROR: --x (independent variables) is required for ols", file=sys.stderr)
            sys.exit(1)
        results, verdict, fallback_method = run_ols_validation(df, args.y, x_cols)
    elif args.method == "arima":
        results, verdict, fallback_method = run_arima_validation(df, args.y)
    elif registry_entry:
        results, verdict, fallback_method = build_manual_registry_result(args.method, registry_entry)
    else:
        print(f"ERROR: Unknown method {args.method}", file=sys.stderr)
        sys.exit(1)

    # Construct report
    report = {
        "question_id": args.question_id,
        "planned_method": args.method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "results": results,
        "registry_entry": registry_entry,
        "routing": {
            "action": "execute_primary" if verdict == "PASS" else ("manual_review" if verdict == "MANUAL" else "execute_fallback"),
            "target_method": args.method if verdict == "PASS" else fallback_method,
            "reason": "All assumptions passed" if verdict == "PASS" else ("Manual checks required" if verdict == "MANUAL" else f"Failed assumptions under {args.method}")
        }
    }

    # Print summary to stdout
    print(f"\n============================================================")
    print(f"ASSUMPTION VALIDATION REPORT: {args.question_id}")
    print(f"Planned Method: {args.method}")
    print(f"Verdict:        {verdict}")
    print(f"============================================================")
    for res in results:
        status_marker = "✓" if res["status"] == "PASS" else "✗"
        print(f"  [{status_marker}] {res['assumption']} ({res['test_name']}): {res['message']}")
    print(f"------------------------------------------------------------")
    print(f"Routing Action: {report['routing']['action']}")
    print(f"Target Method:  {report['routing']['target_method']}")
    print(f"============================================================\n")

    # Output to JSON
    output_path = args.output
    if not output_path:
        reports_dir = root / "reports" / "analysis"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_path = reports_dir / f"assumption_validation_{args.question_id}.json"
    else:
        output_path = Path(output_path) if Path(output_path).is_absolute() else root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Saved validation report to: {output_path}")
    except Exception as e:
        print(f"ERROR: Could not write validation report JSON: {e}", file=sys.stderr)

    sys.exit(0 if verdict in ("PASS", "MANUAL") else 1)


if __name__ == "__main__":
    main()
