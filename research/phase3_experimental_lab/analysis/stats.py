"""ASTRA-Sec Phase 3: Statistical Analysis and Distribution Metrics.

Computes parametric and non-parametric distribution statistics:
Mean, Standard Deviation, Median, Interquartile Range (IQR),
Percentiles (P50, P90, P95, P99), 99% Confidence Intervals, and Cohen's d effect sizes.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
from scipy import stats


def compute_distribution_metrics(values: List[float], confidence: float = 0.99) -> Dict[str, Any]:
    """Computes comprehensive distribution metrics for latency or throughput arrays."""
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "median": 0.0,
            "p90": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "max": 0.0,
            "iqr": 0.0,
            "ci_lower": 0.0,
            "ci_upper": 0.0,
        }

    arr = np.array(values, dtype=np.float64)
    n = len(arr)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    median_val = float(np.median(arr))
    p25 = float(np.percentile(arr, 25))
    p75 = float(np.percentile(arr, 75))
    iqr_val = p75 - p25

    # Confidence Interval (using t-distribution if n > 1)
    if n > 1 and std_val > 0:
        se = std_val / math.sqrt(n)
        t_crit = stats.t.ppf((1 + confidence) / 2.0, df=n - 1)
        ci_lower = mean_val - (t_crit * se)
        ci_upper = mean_val + (t_crit * se)
    else:
        ci_lower = mean_val
        ci_upper = mean_val

    return {
        "count": n,
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "min": round(float(np.min(arr)), 2),
        "p25": round(p25, 2),
        "median": round(median_val, 2),
        "p75": round(p75, 2),
        "iqr": round(iqr_val, 2),
        "p90": round(float(np.percentile(arr, 90)), 2),
        "p95": round(float(np.percentile(arr, 95)), 2),
        "p99": round(float(np.percentile(arr, 99)), 2),
        "max": round(float(np.max(arr)), 2),
        "ci_lower": round(ci_lower, 2),
        "ci_upper": round(ci_upper, 2),
    }


def compute_cohens_d(group1: List[float], group2: List[float]) -> float:
    """Computes Cohen's d effect size between two independent groups."""
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    s_pooled = math.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if s_pooled == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / s_pooled)
