#!/usr/bin/env python3
"""
Advanced Health Analytics Engine

Implements state-of-the-art statistical methods for wearable health data:

  TIME SERIES & TREND
    - Mann-Kendall Trend Test (Mann 1945, Kendall 1975)
    - Seasonal-Trend Decomposition (moving-average based)
    - Autocorrelation Function (ACF) with Bartlett CI

  CAUSAL INFERENCE
    - Granger Causality Test (Granger 1969, Econometrica)
    - Transfer Entropy (Schreiber 2000, Physical Review Letters)
    - Convergent Cross Mapping (Sugihara et al. 2012, Science 338:496)

  NONLINEAR DYNAMICS
    - Sample Entropy (Richman & Moorman 2000, Am J Physiol)
    - Detrended Fluctuation Analysis (Peng et al. 1994, Phys Rev E)
    - Poincaré Plot SD1/SD2 (Brennan et al. 2001, IEEE Trans Biomed Eng)
    - Multiscale Entropy (Costa et al. 2002, Physical Review Letters)

  ADVANCED CGM METRICS
    - LBGI/HBGI (Kovatchev et al. 2002, Diabetes Care)
    - ADRR (Kovatchev et al. 2006, Diabetes Technology & Therapeutics)
    - CONGA-n (McDonnell et al. 2005, Diabetes Technology & Therapeutics)
    - GVP: Glycemic Variability Percentage (Peyser et al. 2018)
    - Glucose Rate of Change distribution

  CIRCADIAN ANALYSIS
    - Single Cosinor (Cornelissen 2014, Theoretical Biology & Medical Modelling)
    - Rhythm Quotient & Interdaily Stability (Witting et al. 1990)

  STATISTICAL RIGOR
    - Bootstrap Confidence Intervals (Efron 1979)
    - Cohen's d Effect Sizes with Hedge's correction
    - Bayesian Online Change Point Detection (Adams & MacKay 2007)
    - Permutation Test for correlations

  COMPOSITE MODELS
    - Biological / Phenotypic Age estimation (Levine 2013 concept, adapted)
    - Fitness Age from VO2 Max (Nes et al. 2013, Medicine & Sci in Sports)
    - Allostatic Load Index (McEwen 1998 concept, adapted for wearables)

Usage:
    python3 advanced_analytics.py <path-to-export.xml> [--output json]

    Outputs JSON with advanced analysis sections. Designed to complement
    the base analyze_health.py output.

Requires: Python 3.6+, no external dependencies.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta
import statistics
import json
import sys
import os
import math
import random
import argparse

# ============================================================================
# Core Math Utilities (no numpy required)
# ============================================================================

def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z")
    except:
        return None

def dot(a, b):
    """Dot product of two vectors."""
    return sum(x * y for x, y in zip(a, b))

def mat_mul(A, B):
    """Multiply matrices A (m×n) and B (n×p)."""
    m, n, p = len(A), len(A[0]), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(p)] for i in range(m)]

def mat_T(A):
    """Transpose matrix."""
    return [list(row) for row in zip(*A)]

def solve_linear(A, b):
    """Solve Ax = b using Gaussian elimination with partial pivoting. Returns x."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[max_row] = M[max_row], M[col]
        if abs(M[col][col]) < 1e-12:
            return None
        for row in range(col + 1, n):
            f = M[row][col] / M[col][col]
            for j in range(col, n + 1):
                M[row][j] -= f * M[col][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x

def ols(X, y):
    """
    Ordinary Least Squares: y = Xβ + ε
    X: list of lists (n×p), y: list (n,)
    Returns: coefficients β, residuals, SSR, R²
    """
    Xt = mat_T(X)
    XtX = mat_mul(Xt, [[yi] for yi in y])  # X'y
    XtX_mat = mat_mul(Xt, X)               # X'X
    Xty = [row[0] for row in XtX]
    beta = solve_linear(XtX_mat, Xty)
    if beta is None:
        return None, None, None, None
    # Residuals
    y_pred = [dot(X[i], beta) for i in range(len(y))]
    resid = [y[i] - y_pred[i] for i in range(len(y))]
    ssr = sum(r * r for r in resid)
    y_mean = sum(y) / len(y)
    sst = sum((yi - y_mean) ** 2 for yi in y)
    r2 = 1 - ssr / sst if sst > 0 else 0
    return beta, resid, ssr, r2

def norm_cdf(z):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    if z < -8:
        return 0.0
    if z > 8:
        return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    z = abs(z)
    t = 1.0 / (1.0 + p * z)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1) * t * math.exp(-z*z/2)
    return 0.5 * (1.0 + sign * y)

def f_cdf(f_val, d1, d2):
    """
    Approximate F-distribution CDF using the transformation to Beta distribution.
    For large d2, F ≈ chi²(d1)/d1. Uses regularized incomplete beta function approximation.
    """
    if f_val <= 0:
        return 0.0
    x = d1 * f_val / (d1 * f_val + d2)
    return regularized_beta(x, d1 / 2, d2 / 2)

def regularized_beta(x, a, b, max_iter=200):
    """Regularized incomplete beta function I_x(a,b) via continued fraction (Lentz)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    if x > (a + 1) / (a + b + 2):
        return 1.0 - regularized_beta(1 - x, b, a, max_iter)
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) / a
    # Lentz's continued fraction
    f, C, D = 1.0, 1.0, 0.0
    for m in range(max_iter):
        if m == 0:
            num = 1.0
        elif m % 2 == 0:
            k = m // 2
            num = k * (b - k) * x / ((a + 2*k - 1) * (a + 2*k))
        else:
            k = (m + 1) // 2
            num = -(a + k) * (a + b + k) * x / ((a + 2*k) * (a + 2*k + 1))
        D = 1.0 + num * D
        if abs(D) < 1e-30:
            D = 1e-30
        D = 1.0 / D
        C = 1.0 + num / C
        if abs(C) < 1e-30:
            C = 1e-30
        delta = C * D
        f *= delta
        if abs(delta - 1.0) < 1e-10:
            break
    return front * (f - 1.0)

# ============================================================================
# 1. MANN-KENDALL TREND TEST (Mann 1945, Kendall 1975)
# ============================================================================

def mann_kendall(data):
    """
    Mann-Kendall trend test. Nonparametric test for monotonic trend.
    Returns: S, z_score, p_value (two-sided), trend direction
    Reference: Mann (1945), Kendall (1975)
    """
    n = len(data)
    if n < 8:
        return None
    S = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = data[j] - data[i]
            if diff > 0:
                S += 1
            elif diff < 0:
                S -= 1
    # Tie correction
    from collections import Counter
    ties = Counter(data)
    tie_correction = sum(t * (t - 1) * (2 * t + 5) for t in ties.values() if t > 1)
    var_S = (n * (n - 1) * (2 * n + 5) - tie_correction) / 18
    if var_S <= 0:
        return None
    if S > 0:
        z = (S - 1) / math.sqrt(var_S)
    elif S < 0:
        z = (S + 1) / math.sqrt(var_S)
    else:
        z = 0
    p = 2 * (1 - norm_cdf(abs(z)))
    tau = S / (n * (n - 1) / 2)  # Kendall's tau
    trend = "increasing" if z > 0 and p < 0.05 else "decreasing" if z < 0 and p < 0.05 else "no_trend"
    return {"S": S, "tau": round(tau, 4), "z": round(z, 4), "p_value": round(p, 6), "trend": trend, "n": n}

# ============================================================================
# 2. GRANGER CAUSALITY (Granger 1969, Econometrica)
# ============================================================================

def granger_causality(x, y, max_lag=4):
    """
    Granger causality: does x Granger-cause y?
    Test: restricted model y_t = Σ a_i y_{t-i} + ε
          unrestricted model y_t = Σ a_i y_{t-i} + Σ b_i x_{t-i} + ε
    F-test on the improvement from adding x lags.
    Reference: Granger (1969), Econometrica 37(3):424-438
    """
    results = {}
    for lag in range(1, max_lag + 1):
        n = len(y) - lag
        if n < 2 * lag + 10:
            continue
        # Build design matrices
        # Restricted: y_t ~ const + y_{t-1} + ... + y_{t-lag}
        Y = [y[t] for t in range(lag, lag + n)]
        X_r = [[1.0] + [y[t - i] for i in range(1, lag + 1)] for t in range(lag, lag + n)]
        # Unrestricted: y_t ~ const + y_lags + x_lags
        X_u = [[1.0] + [y[t - i] for i in range(1, lag + 1)] + [x[t - i] for i in range(1, lag + 1)]
                for t in range(lag, lag + n)]

        _, _, ssr_r, _ = ols(X_r, Y)
        _, _, ssr_u, r2_u = ols(X_u, Y)

        if ssr_r is None or ssr_u is None or ssr_u <= 0:
            continue

        p_extra = lag  # Number of extra parameters
        df_u = n - 2 * lag - 1
        if df_u <= 0:
            continue

        f_stat = ((ssr_r - ssr_u) / p_extra) / (ssr_u / df_u)
        p_value = 1 - f_cdf(f_stat, p_extra, df_u)

        results[f"lag_{lag}"] = {
            "f_statistic": round(f_stat, 4),
            "p_value": round(p_value, 6),
            "significant": p_value < 0.05,
            "ssr_restricted": round(ssr_r, 4),
            "ssr_unrestricted": round(ssr_u, 4),
            "r2_unrestricted": round(r2_u, 4),
        }
    return results if results else None

# ============================================================================
# 3. TRANSFER ENTROPY (Schreiber 2000, Physical Review Letters)
# ============================================================================

def transfer_entropy(x, y, lag=1, bins=8):
    """
    Transfer Entropy: TE(X→Y) = H(Y_{t+1} | Y_t) - H(Y_{t+1} | Y_t, X_t)
    Measures directed information flow from X to Y.
    Uses histogram-based probability estimation.
    Reference: Schreiber (2000), PRL 85(2):461-464
    """
    n = len(x) - lag
    if n < 50:
        return None

    # Discretize
    def discretize(vals, nb):
        mn, mx = min(vals), max(vals)
        if mx == mn:
            return [0] * len(vals)
        return [min(int((v - mn) / (mx - mn + 1e-10) * nb), nb - 1) for v in vals]

    xd = discretize(x, bins)
    yd = discretize(y, bins)

    # Count joint probabilities
    # p(y_{t+1}, y_t, x_t), p(y_t, x_t), p(y_{t+1}, y_t), p(y_t)
    from collections import Counter
    joint_yyx = Counter()
    joint_yx = Counter()
    joint_yy = Counter()
    count_y = Counter()

    for t in range(n):
        y_next = yd[t + lag]
        y_now = yd[t]
        x_now = xd[t]
        joint_yyx[(y_next, y_now, x_now)] += 1
        joint_yx[(y_now, x_now)] += 1
        joint_yy[(y_next, y_now)] += 1
        count_y[y_now] += 1

    # TE = Σ p(y_{t+1}, y_t, x_t) * log( p(y_{t+1}|y_t,x_t) / p(y_{t+1}|y_t) )
    te = 0.0
    for (yn, yt, xt), c_yyx in joint_yyx.items():
        p_yyx = c_yyx / n
        p_yx = joint_yx[(yt, xt)] / n
        p_yy = joint_yy[(yn, yt)] / n
        p_y = count_y[yt] / n

        if p_yx > 0 and p_yy > 0 and p_y > 0:
            # p(y_{t+1}|y_t,x_t) = p(y_{t+1},y_t,x_t) / p(y_t,x_t)
            # p(y_{t+1}|y_t) = p(y_{t+1},y_t) / p(y_t)
            cond_full = c_yyx / joint_yx[(yt, xt)]
            cond_reduced = joint_yy[(yn, yt)] / count_y[yt]
            if cond_full > 0 and cond_reduced > 0:
                te += p_yyx * math.log2(cond_full / cond_reduced)

    # Significance via shuffle test
    te_shuffled = []
    random.seed(42)
    for _ in range(100):
        xs = xd[:]
        random.shuffle(xs)
        te_s = 0.0
        joint_s = Counter()
        joint_yx_s = Counter()
        for t in range(n):
            joint_s[(yd[t+lag], yd[t], xs[t])] += 1
            joint_yx_s[(yd[t], xs[t])] += 1
        for (yn, yt, xt), c in joint_s.items():
            p_s = c / n
            p_yx_s = joint_yx_s[(yt, xt)] / n
            p_yy_s = joint_yy[(yn, yt)] / n
            p_y_s = count_y[yt] / n
            if p_yx_s > 0 and p_yy_s > 0 and p_y_s > 0:
                cf = c / joint_yx_s[(yt, xt)]
                cr = joint_yy[(yn, yt)] / count_y[yt]
                if cf > 0 and cr > 0:
                    te_s += p_s * math.log2(cf / cr)
        te_shuffled.append(te_s)

    te_mean_null = statistics.mean(te_shuffled) if te_shuffled else 0
    te_sd_null = statistics.stdev(te_shuffled) if len(te_shuffled) >= 2 else 1
    z_score = (te - te_mean_null) / te_sd_null if te_sd_null > 0 else 0
    p_value = 1 - norm_cdf(z_score)

    return {
        "te_bits": round(te, 6),
        "te_null_mean": round(te_mean_null, 6),
        "z_score": round(z_score, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
        "direction": "X→Y"
    }

# ============================================================================
# 4. CONVERGENT CROSS MAPPING (Sugihara et al. 2012, Science)
# ============================================================================

def ccm(x, y, E=3, tau=1, lib_sizes=None):
    """
    Convergent Cross Mapping: test if X causally influences Y.
    Key insight: if X drives Y, then Y's shadow manifold can predict X,
    and prediction skill increases with library size (convergence).
    Reference: Sugihara et al. (2012), Science 338(6106):496-500
    """
    n = len(x)
    if n < E * tau + 20:
        return None

    if lib_sizes is None:
        lib_sizes = [max(E+2, n//5), n//3, n//2, 2*n//3, n - E*tau]
        lib_sizes = sorted(set(min(ls, n - E*tau) for ls in lib_sizes if ls > E+1))

    def embed(ts, E, tau):
        """Create time-delay embedding."""
        emb = []
        for i in range((E-1)*tau, len(ts)):
            emb.append([ts[i - j*tau] for j in range(E)])
        return emb

    def euclidean(a, b):
        return math.sqrt(sum((ai-bi)**2 for ai, bi in zip(a, b)))

    def predict_from_manifold(manifold_y, target_x, lib_idx, pred_idx, E):
        """Use Y's shadow manifold to predict X."""
        predictions = []
        actuals = []
        for pi in pred_idx:
            if pi >= len(manifold_y) or pi >= len(target_x):
                continue
            # Find E+1 nearest neighbors in library
            dists = []
            for li in lib_idx:
                if li == pi or li >= len(manifold_y):
                    continue
                d = euclidean(manifold_y[pi], manifold_y[li])
                dists.append((d, li))
            if len(dists) < E + 1:
                continue
            dists.sort(key=lambda x: x[0])
            nn = dists[:E+1]
            min_d = nn[0][0]
            if min_d == 0:
                min_d = 1e-10
            # Exponential weights
            weights = [math.exp(-d/min_d) if min_d > 0 else 1.0 for d, _ in nn]
            w_sum = sum(weights)
            if w_sum == 0:
                continue
            pred = sum(w * target_x[idx] for w, (_, idx) in zip(weights, nn)) / w_sum
            predictions.append(pred)
            actuals.append(target_x[pi])

        if len(predictions) < 5:
            return None
        # Correlation
        n_p = len(predictions)
        mp = sum(predictions) / n_p
        ma = sum(actuals) / n_p
        num = sum((p-mp)*(a-ma) for p, a in zip(predictions, actuals))
        den = (sum((p-mp)**2 for p in predictions) * sum((a-ma)**2 for a in actuals)) ** 0.5
        return round(num / den, 4) if den > 0 else 0

    y_emb = embed(y, E, tau)
    offset = (E-1) * tau

    rho_by_L = {}
    for L in lib_sizes:
        if L > len(y_emb):
            continue
        # Random subsample for library
        random.seed(42)
        all_idx = list(range(len(y_emb)))
        lib_idx = sorted(random.sample(all_idx, min(L, len(all_idx))))
        pred_idx = [i for i in all_idx if i not in set(lib_idx)][:L]
        if not pred_idx:
            pred_idx = lib_idx

        x_offset = x[offset:]
        rho = predict_from_manifold(y_emb, x_offset, lib_idx, pred_idx, E)
        if rho is not None:
            rho_by_L[L] = rho

    if len(rho_by_L) < 2:
        return None

    # Check convergence: does rho increase with L?
    Ls = sorted(rho_by_L.keys())
    rhos = [rho_by_L[L] for L in Ls]
    converges = rhos[-1] > rhos[0] + 0.05  # Meaningful increase

    return {
        "rho_by_library_size": {str(L): rho for L, rho in rho_by_L.items()},
        "min_rho": round(min(rhos), 4),
        "max_rho": round(max(rhos), 4),
        "converges": converges,
        "causal_evidence": "strong" if converges and rhos[-1] > 0.3 else "weak" if converges else "none",
    }

# ============================================================================
# 5. SAMPLE ENTROPY (Richman & Moorman 2000, Am J Physiology)
# ============================================================================

def sample_entropy(data, m=2, r_factor=0.2):
    """
    Sample Entropy: measures complexity/regularity of time series.
    Lower = more regular/predictable, Higher = more complex.
    m: embedding dimension, r: tolerance = r_factor * std(data)
    Reference: Richman & Moorman (2000), Am J Physiol Heart Circ Physiol 278:H2039
    """
    N = len(data)
    if N < 50:
        return None
    # Subsample if too large
    if N > 2000:
        step = N // 2000
        data = data[::step]
        N = len(data)

    r = r_factor * statistics.stdev(data)
    if r == 0:
        return None

    def count_matches(dim):
        count = 0
        templates = []
        for i in range(N - dim):
            templates.append(data[i:i+dim])
        for i in range(len(templates)):
            for j in range(i + 1, len(templates)):
                if max(abs(templates[i][k] - templates[j][k]) for k in range(dim)) <= r:
                    count += 1
        return count

    B = count_matches(m)
    A = count_matches(m + 1)

    if B == 0:
        return None
    if A == 0:
        return {"value": float('inf'), "interpretation": "maximum_complexity"}

    se = -math.log(A / B)
    # Interpretation (for heart rate)
    interp = "high_complexity" if se > 1.5 else "moderate_complexity" if se > 0.8 else "low_complexity_regular"
    return {"value": round(se, 4), "m": m, "r": round(r, 4), "N": N, "interpretation": interp}

# ============================================================================
# 6. DFA - Detrended Fluctuation Analysis (Peng et al. 1994)
# ============================================================================

def dfa(data, min_box=4, max_box=None):
    """
    DFA alpha exponent: characterizes long-range correlations.
    α ≈ 0.5: uncorrelated (white noise)
    α ≈ 1.0: 1/f noise (healthy heart rate)
    α ≈ 1.5: Brownian motion (random walk)
    Reference: Peng et al. (1994), Phys Rev E 49:1685
    """
    N = len(data)
    if N < 50:
        return None
    if N > 5000:
        step = N // 5000
        data = data[::step]
        N = len(data)

    mean_val = sum(data) / N
    # Integrate (cumulative sum of mean-subtracted)
    y = []
    cumsum = 0
    for d in data:
        cumsum += (d - mean_val)
        y.append(cumsum)

    if max_box is None:
        max_box = N // 4

    # Box sizes (logarithmically spaced)
    box_sizes = []
    s = min_box
    while s <= max_box:
        box_sizes.append(int(s))
        s *= 1.5
    box_sizes = sorted(set(box_sizes))

    fluctuations = []
    for box_size in box_sizes:
        n_boxes = N // box_size
        if n_boxes < 2:
            continue
        rms_values = []
        for i in range(n_boxes):
            segment = y[i * box_size:(i + 1) * box_size]
            # Linear detrend
            x_vals = list(range(box_size))
            x_mean = (box_size - 1) / 2
            y_mean = sum(segment) / box_size
            ssxy = sum((x - x_mean) * (s - y_mean) for x, s in zip(x_vals, segment))
            ssxx = sum((x - x_mean) ** 2 for x in x_vals)
            slope = ssxy / ssxx if ssxx > 0 else 0
            intercept = y_mean - slope * x_mean
            detrended = [s - (slope * x + intercept) for x, s in zip(x_vals, segment)]
            rms = math.sqrt(sum(d * d for d in detrended) / box_size)
            rms_values.append(rms)
        if rms_values:
            fluctuations.append((box_size, statistics.mean(rms_values)))

    if len(fluctuations) < 3:
        return None

    # Log-log regression
    log_n = [math.log(f[0]) for f in fluctuations]
    log_f = [math.log(f[1]) if f[1] > 0 else -10 for f in fluctuations]

    n_pts = len(log_n)
    mx = sum(log_n) / n_pts
    my = sum(log_f) / n_pts
    ssxy = sum((x - mx) * (y - my) for x, y in zip(log_n, log_f))
    ssxx = sum((x - mx) ** 2 for x in log_n)
    ssyy = sum((y - my) ** 2 for y in log_f)

    alpha = ssxy / ssxx if ssxx > 0 else 0
    r2 = (ssxy ** 2) / (ssxx * ssyy) if ssxx > 0 and ssyy > 0 else 0

    if alpha < 0.65:
        interp = "anti_correlated"
    elif alpha < 0.85:
        interp = "uncorrelated_white_noise"
    elif alpha < 1.15:
        interp = "healthy_1f_noise"
    elif alpha < 1.35:
        interp = "correlated"
    else:
        interp = "brownian_motion"

    return {
        "alpha": round(alpha, 4),
        "r_squared": round(r2, 4),
        "interpretation": interp,
        "n_points": N,
        "box_sizes_used": len(fluctuations),
    }

# ============================================================================
# 7. POINCARÉ PLOT (Brennan et al. 2001, IEEE Trans Biomed Eng)
# ============================================================================

def poincare_plot(rr_intervals):
    """
    Poincaré plot analysis for HRV.
    SD1: short-term variability (beat-to-beat)
    SD2: long-term variability
    SD1/SD2: vagal-sympathetic balance indicator
    Reference: Brennan et al. (2001), IEEE Trans Biomed Eng 48(11):1342-1347
    """
    if not rr_intervals:
        return None
    n = len(rr_intervals)
    if n < 20:
        return None

    diffs = [rr_intervals[i+1] - rr_intervals[i] for i in range(n - 1)]
    try:
        var_rr = statistics.variance(rr_intervals)
        var_diff = statistics.variance(diffs) if len(diffs) >= 2 else 0
    except statistics.StatisticsError:
        return None

    sd1 = math.sqrt(0.5 * var_diff)
    sd2 = math.sqrt(2 * var_rr - 0.5 * var_diff) if (2 * var_rr - 0.5 * var_diff) > 0 else 0

    ratio = sd1 / sd2 if sd2 > 0 else 0

    # CSI (Cardiac Sympathetic Index) and CVI (Cardiac Vagal Index)
    # Toichi et al. (1997)
    csi = sd2 / sd1 if sd1 > 0 else 0
    cvi = math.log(sd1 * sd2) if sd1 > 0 and sd2 > 0 else 0

    return {
        "sd1_ms": round(sd1, 2),
        "sd2_ms": round(sd2, 2),
        "sd1_sd2_ratio": round(ratio, 4),
        "csi": round(csi, 4),
        "cvi": round(cvi, 4),
        "interpretation": {
            "sd1": "short_term_variability_parasympathetic",
            "sd2": "long_term_variability_overall",
            "ratio": "low_ratio_sympathetic_dominant" if ratio < 0.5 else
                     "balanced" if ratio < 1.5 else "high_ratio_parasympathetic_dominant"
        }
    }

# ============================================================================
# 8. COSINOR ANALYSIS (Cornelissen 2014, Theor Biol Med Model)
# ============================================================================

def cosinor(times_hours, values, period=24.0):
    """
    Single-component cosinor: Y(t) = M + A·cos(2πt/T + φ)
    Linearized: Y = M + β·cos(ωt) + γ·sin(ωt)
    MESOR: M, Amplitude: sqrt(β²+γ²), Acrophase: atan2(-γ, β)
    F-test for rhythm significance.
    Reference: Cornelissen (2014), Theor Biol Med Model 11:16
    """
    n = len(values)
    if n < 10:
        return None
    omega = 2 * math.pi / period

    # Design matrix: [1, cos(ωt), sin(ωt)]
    X = [[1.0, math.cos(omega * t), math.sin(omega * t)] for t in times_hours]
    beta, resid, ssr, r2 = ols(X, values)
    if beta is None:
        return None

    M, b_cos, b_sin = beta[0], beta[1], beta[2]
    amplitude = math.sqrt(b_cos ** 2 + b_sin ** 2)
    # Model: Y = M + A*cos(wt - phi). Expanding: beta = A*cos(phi), gamma = A*sin(phi).
    # Peak at t = phi/omega, where phi = atan2(gamma, beta) = atan2(b_sin, b_cos).
    acrophase_rad = math.atan2(b_sin, b_cos)
    acrophase_hours = (acrophase_rad / omega) % period

    # F-test for rhythm
    y_mean = sum(values) / n
    sst = sum((v - y_mean) ** 2 for v in values)
    ssr_rhythm = sst - ssr
    df1 = 2  # cos and sin terms
    df2 = n - 3
    if ssr > 0 and df2 > 0:
        f_stat = (ssr_rhythm / df1) / (ssr / df2)
        p_value = 1 - f_cdf(f_stat, df1, df2)
    else:
        f_stat = 0
        p_value = 1.0

    return {
        "mesor": round(M, 2),
        "amplitude": round(amplitude, 2),
        "acrophase_hours": round(acrophase_hours, 2),
        "acrophase_time": f"{int(acrophase_hours):02d}:{int((acrophase_hours % 1) * 60):02d}",
        "r_squared": round(r2, 4),
        "f_statistic": round(f_stat, 4),
        "p_value": round(p_value, 6),
        "significant_rhythm": p_value < 0.05,
        "period_hours": period,
    }

# ============================================================================
# 9. ADVANCED GLUCOSE METRICS
# ============================================================================

def kovatchev_glucose_risk(glucose_values):
    """
    LBGI/HBGI: Low/High Blood Glucose Index
    ADRR: Average Daily Risk Range
    Reference: Kovatchev et al. (2002), Diabetes Care 25:2058-2064
               Kovatchev et al. (2006), Diabetes Technol Ther 8(6):644-653
    """
    if not glucose_values or len(glucose_values) < 3:
        return None
    # BG risk function: f(BG) = 1.509 * (ln(BG)^1.084 - 5.381)
    def f_bg(bg):
        if bg <= 0:
            return 0
        return 1.509 * ((math.log(bg)) ** 1.084 - 5.381)

    rl_vals = []
    rh_vals = []
    for bg in glucose_values:
        fbg = f_bg(bg)
        rl = 10 * fbg ** 2 if fbg < 0 else 0
        rh = 10 * fbg ** 2 if fbg > 0 else 0
        rl_vals.append(rl)
        rh_vals.append(rh)

    lbgi = statistics.mean(rl_vals)
    hbgi = statistics.mean(rh_vals)

    return {
        "lbgi": round(lbgi, 2),
        "hbgi": round(hbgi, 2),
        "lbgi_risk": "minimal" if lbgi < 1.1 else "low" if lbgi < 2.5 else "moderate" if lbgi < 5 else "high",
        "hbgi_risk": "minimal" if hbgi < 4.5 else "low" if hbgi < 9 else "moderate" if hbgi < 18 else "high",
    }

def adrr(glucose_ts_by_day):
    """
    Average Daily Risk Range.
    ADRR = mean over days of (max_rl + max_rh) for each day.
    Reference: Kovatchev et al. (2006)
    """
    if not glucose_ts_by_day:
        return None
    def f_bg(bg):
        if bg <= 0:
            return 0
        return 1.509 * ((math.log(bg)) ** 1.084 - 5.381)

    daily_risk_ranges = []
    for day, readings in glucose_ts_by_day.items():
        if len(readings) < 5:
            continue
        max_rl = 0
        max_rh = 0
        for bg in readings:
            fbg = f_bg(bg)
            rl = 10 * fbg ** 2 if fbg < 0 else 0
            rh = 10 * fbg ** 2 if fbg > 0 else 0
            max_rl = max(max_rl, rl)
            max_rh = max(max_rh, rh)
        daily_risk_ranges.append(max_rl + max_rh)

    if not daily_risk_ranges:
        return None
    val = statistics.mean(daily_risk_ranges)
    risk = "low" if val < 20 else "moderate" if val < 40 else "high"
    return {"adrr": round(val, 2), "risk": risk, "n_days": len(daily_risk_ranges)}

def conga(glucose_ts, hours=1):
    """
    CONGA-n: Continuous Overall Net Glycemic Action.
    SD of differences between current reading and reading n hours earlier.
    Reference: McDonnell et al. (2005), Diabetes Technol Ther 7(2):253-263
    """
    if not glucose_ts or len(glucose_ts) < 20:
        return None
    # Find pairs separated by approximately 'hours' hours
    target_delta = timedelta(hours=hours)
    tolerance = timedelta(minutes=10)
    diffs = []
    for i in range(len(glucose_ts)):
        dt_i, v_i = glucose_ts[i]
        for j in range(i + 1, len(glucose_ts)):
            dt_j, v_j = glucose_ts[j]
            delta = dt_j - dt_i
            if delta > target_delta + tolerance:
                break
            if abs(delta - target_delta) <= tolerance:
                diffs.append(v_j - v_i)
                break

    if len(diffs) < 10:
        return None
    return {"conga": round(statistics.stdev(diffs), 2), "hours": hours, "n_pairs": len(diffs)}

def glucose_rate_of_change(glucose_ts):
    """
    Rate of glucose change (mg/dL/min) distribution.
    Clinically relevant: rapid drops predict hypoglycemia.
    """
    if not glucose_ts or len(glucose_ts) < 20:
        return None
    rates = []
    for i in range(1, len(glucose_ts)):
        dt_diff = (glucose_ts[i][0] - glucose_ts[i-1][0]).total_seconds() / 60
        if 0 < dt_diff <= 15:  # Only consecutive readings ≤ 15 min apart
            rate = (glucose_ts[i][1] - glucose_ts[i-1][1]) / dt_diff
            rates.append(rate)
    if not rates:
        return None
    return {
        "mean_rate": round(statistics.mean(rates), 3),
        "sd_rate": round(statistics.stdev(rates), 3) if len(rates) >= 2 else None,
        "max_rise": round(max(rates), 3),
        "max_fall": round(min(rates), 3),
        "pct_rapid_rise_gt2": round(sum(1 for r in rates if r > 2) / len(rates) * 100, 1),
        "pct_rapid_fall_lt_neg2": round(sum(1 for r in rates if r < -2) / len(rates) * 100, 1),
        "n": len(rates),
    }

def gvp(glucose_ts):
    """
    Glycemic Variability Percentage (GVP).
    Ratio of total path length to ideal straight line.
    GVP = (L/L0 - 1) * 100%  where L = sum of |ΔBG| segments, L0 = straight line.
    Reference: Peyser et al. (2018), J Diabetes Sci Technol 12(4):718-726
    """
    if not glucose_ts or len(glucose_ts) < 20:
        return None
    # Total path length in (time, glucose) space
    L = 0
    dt_total = 0
    for i in range(1, len(glucose_ts)):
        dt_min = (glucose_ts[i][0] - glucose_ts[i-1][0]).total_seconds() / 60
        dg = glucose_ts[i][1] - glucose_ts[i-1][1]
        if 0 < dt_min <= 30:  # Only count valid intervals
            L += math.sqrt(dt_min**2 + dg**2)
            dt_total += dt_min
    L0 = dt_total  # Straight line length (no glucose change)
    if L0 <= 0:
        return None
    gvp_val = (L / L0 - 1) * 100
    return {"gvp_pct": round(gvp_val, 2), "interpretation": "low_variability" if gvp_val < 15 else "moderate" if gvp_val < 30 else "high_variability"}

# ============================================================================
# 10. BOOTSTRAP CI (Efron 1979)
# ============================================================================

def bootstrap_ci(data, stat_func=statistics.mean, n_boot=1000, ci=0.95, seed=42):
    """Bootstrap confidence interval."""
    if len(data) < 5:
        return None
    random.seed(seed)
    n = len(data)
    boot_stats = []
    for _ in range(n_boot):
        sample = [data[random.randint(0, n-1)] for _ in range(n)]
        try:
            boot_stats.append(stat_func(sample))
        except:
            continue
    if not boot_stats:
        return None
    alpha = (1 - ci) / 2
    lo = sorted(boot_stats)[int(alpha * len(boot_stats))]
    hi = sorted(boot_stats)[int((1 - alpha) * len(boot_stats))]
    return {"point_estimate": round(stat_func(data), 4),
            "ci_lower": round(lo, 4), "ci_upper": round(hi, 4),
            "ci_level": ci, "n_bootstrap": n_boot}

# ============================================================================
# 11. EFFECT SIZE (Cohen 1988, with Hedge's correction)
# ============================================================================

def cohens_d(group1, group2):
    """
    Cohen's d with Hedge's correction for small samples.
    Reference: Cohen (1988), Hedges & Olkin (1985)
    """
    n1, n2 = len(group1), len(group2)
    if n1 < 3 or n2 < 3:
        return None
    m1, m2 = statistics.mean(group1), statistics.mean(group2)
    s1, s2 = statistics.stdev(group1), statistics.stdev(group2)
    pooled_sd = math.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    if pooled_sd == 0:
        return None
    d = (m1 - m2) / pooled_sd
    # Hedge's correction
    correction = 1 - 3 / (4*(n1+n2) - 9)
    g = d * correction
    size = "negligible" if abs(g) < 0.2 else "small" if abs(g) < 0.5 else "medium" if abs(g) < 0.8 else "large"
    return {"cohens_d": round(d, 4), "hedges_g": round(g, 4), "effect_size": size,
            "group1_mean": round(m1, 2), "group2_mean": round(m2, 2), "n1": n1, "n2": n2}

# ============================================================================
# 12. BAYESIAN ONLINE CHANGE POINT DETECTION (Adams & MacKay 2007)
# ============================================================================

def bayesian_changepoint(data, hazard_rate=1/50):
    """
    Bayesian Online Change Point Detection.
    Finds points where the generative process changes.
    Uses conjugate Normal-Inverse-Gamma prior.
    Reference: Adams & MacKay (2007), arXiv:0710.3742
    """
    n = len(data)
    if n < 20:
        return None

    # Hyperparameters for Normal-Inverse-Gamma prior
    mu0 = statistics.mean(data)
    kappa0 = 1.0
    alpha0 = 1.0
    beta0 = statistics.variance(data) if len(data) >= 2 else 1.0

    # Run lengths and sufficient statistics
    max_run = min(n, 300)
    R = [[0.0] * (max_run + 1) for _ in range(n + 1)]
    R[0][0] = 1.0

    # Sufficient stats for each run length
    muT = [[0.0] * (max_run + 1) for _ in range(n + 1)]
    kappaT = [[0.0] * (max_run + 1) for _ in range(n + 1)]
    alphaT = [[0.0] * (max_run + 1) for _ in range(n + 1)]
    betaT = [[0.0] * (max_run + 1) for _ in range(n + 1)]

    for r in range(max_run + 1):
        muT[0][r] = mu0
        kappaT[0][r] = kappa0
        alphaT[0][r] = alpha0
        betaT[0][r] = beta0

    changepoint_probs = []

    for t in range(1, n + 1):
        x = data[t - 1]
        pred_probs = []
        for r in range(min(t, max_run)):
            # Predictive probability: Student-t
            mu_p = muT[t-1][r]
            kappa_p = kappaT[t-1][r]
            alpha_p = alphaT[t-1][r]
            beta_p = betaT[t-1][r]
            nu = 2 * alpha_p
            sigma2 = beta_p * (kappa_p + 1) / (alpha_p * kappa_p)
            if sigma2 <= 0:
                sigma2 = 1e-10
            # Student-t pdf
            z = (x - mu_p) ** 2 / (nu * sigma2)
            try:
                log_pred = math.lgamma((nu+1)/2) - math.lgamma(nu/2) - 0.5*math.log(nu*math.pi*sigma2) - (nu+1)/2 * math.log(1+z)
                pred = math.exp(log_pred)
            except:
                pred = 1e-10
            pred_probs.append(pred)

        # Growth probabilities
        for r in range(min(t, max_run) - 1, -1, -1):
            R[t][r+1] = R[t-1][r] * pred_probs[r] * (1 - hazard_rate) if r < len(pred_probs) else 0

        # Changepoint probability
        cp_mass = sum(R[t-1][r] * pred_probs[r] * hazard_rate for r in range(min(t, max_run)) if r < len(pred_probs))
        R[t][0] = cp_mass

        # Normalize
        total = sum(R[t][r] for r in range(min(t+1, max_run+1)))
        if total > 0:
            for r in range(min(t+1, max_run+1)):
                R[t][r] /= total

        changepoint_probs.append(R[t][0])

        # Update sufficient statistics
        for r in range(min(t+1, max_run+1)):
            if r == 0:
                muT[t][0] = mu0
                kappaT[t][0] = kappa0
                alphaT[t][0] = alpha0
                betaT[t][0] = beta0
            else:
                kp = kappaT[t-1][r-1]
                mp = muT[t-1][r-1]
                ap = alphaT[t-1][r-1]
                bp = betaT[t-1][r-1]
                kappaT[t][r] = kp + 1
                muT[t][r] = (kp * mp + x) / (kp + 1)
                alphaT[t][r] = ap + 0.5
                betaT[t][r] = bp + kp * (x - mp)**2 / (2 * (kp + 1))

    # Find significant changepoints (peaks in changepoint probability)
    threshold = 0.15
    peaks = []
    for i in range(1, len(changepoint_probs) - 1):
        if changepoint_probs[i] > threshold and \
           changepoint_probs[i] > changepoint_probs[i-1] and \
           changepoint_probs[i] > changepoint_probs[i+1]:
            before = data[max(0, i-10):i]
            after = data[i:min(len(data), i+10)]
            peaks.append({
                "index": i,
                "posterior_prob": round(changepoint_probs[i], 4),
                "before_mean": round(statistics.mean(before), 2) if before else None,
                "after_mean": round(statistics.mean(after), 2) if after else None,
            })

    return {
        "changepoints": peaks[:10],  # Top 10
        "max_posterior": round(max(changepoint_probs), 4) if changepoint_probs else 0,
    }

# ============================================================================
# 13. BIOLOGICAL AGE / FITNESS AGE
# ============================================================================

def fitness_age(vo2max, age, sex="Male"):
    """
    Fitness Age from VO2 Max.
    Based on the HUNT study regression (Nes et al. 2013, Med Sci Sports Exerc).
    The age at which the population average VO2 Max matches yours.
    Reference: Nes et al. (2013), MSSE 45(11):2017-2025
    """
    if vo2max is None or age is None:
        return None
    # Approximate population VO2 Max decline curves
    # Male: VO2max ≈ 57.0 - 0.40 * age  (simplified from HUNT data)
    # Female: VO2max ≈ 48.0 - 0.35 * age
    if sex == "Male":
        fit_age = (57.0 - vo2max) / 0.40
    else:
        fit_age = (48.0 - vo2max) / 0.35
    fit_age = max(15, min(90, fit_age))
    return {
        "fitness_age": round(fit_age, 1),
        "chronological_age": age,
        "age_gap": round(fit_age - age, 1),
        "interpretation": "younger_than_chronological" if fit_age < age - 2 else
                          "age_appropriate" if abs(fit_age - age) <= 2 else
                          "older_than_chronological",
    }

def biological_age_estimate(age, rhr, hrv_mean, vo2max, bmi, steps_per_day, sleep_hours, sex="Male"):
    """
    Composite biological age from wearable biomarkers.
    Conceptually based on Levine (2013) phenotypic age, adapted for wearable data.
    Each biomarker contributes a delta-age based on deviation from population norms.
    """
    if age is None:
        return None
    delta = 0
    components = {}

    if rhr is not None:
        norm_rhr = 72 if sex == "Male" else 75
        d = max(-3, min(3, (rhr - norm_rhr) * 0.12))
        delta += d
        components["rhr_delta"] = round(d, 1)

    if hrv_mean is not None:
        norm_hrv = max(20, 55 - 0.5 * age)  # Declines with age
        d = max(-3, min(3, -(hrv_mean - norm_hrv) * 0.06))
        delta += d
        components["hrv_delta"] = round(d, 1)

    if vo2max is not None:
        fa = fitness_age(vo2max, age, sex)
        if fa:
            d = max(-5, min(8, (fa["fitness_age"] - age) * 0.25))
            delta += d
            components["vo2max_delta"] = round(d, 1)

    if bmi is not None:
        norm_bmi = 24.5
        d = max(-2, min(4, (bmi - norm_bmi) * 0.2))
        delta += d
        components["bmi_delta"] = round(d, 1)

    if steps_per_day is not None:
        d = max(-3, min(3, -(steps_per_day - 8000) / 3000))
        delta += d
        components["activity_delta"] = round(d, 1)

    if sleep_hours is not None:
        optimal = 7.5
        d = max(0, min(2, abs(sleep_hours - optimal) * 0.4))
        delta += d
        components["sleep_delta"] = round(d, 1)

    bio_age = age + delta
    return {
        "biological_age": round(bio_age, 1),
        "chronological_age": age,
        "age_acceleration": round(delta, 1),
        "components": components,
        "interpretation": "accelerated_aging" if delta > 3 else
                          "normal" if abs(delta) <= 3 else "decelerated_aging",
    }

# ============================================================================
# 14. INTERDAILY STABILITY & INTRADAILY VARIABILITY (Witting 1990)
# ============================================================================

def rhythm_stability(hourly_means_by_day):
    """
    IS: Interdaily Stability — consistency of rhythm across days (0-1, higher = more stable)
    IV: Intradaily Variability — fragmentation within days (close to 0 = smooth, >1 = fragmented)
    Reference: Witting et al. (1990), Biol Psychiatry 27:563-572
    """
    if not hourly_means_by_day or len(hourly_means_by_day) < 3:
        return None

    # Flatten all values
    all_vals = []
    for day_vals in hourly_means_by_day.values():
        all_vals.extend(day_vals.values())
    if len(all_vals) < 24:
        return None
    grand_mean = statistics.mean(all_vals)

    # Hourly means across all days
    hourly_grand = defaultdict(list)
    for day, h_vals in hourly_means_by_day.items():
        for h, v in h_vals.items():
            hourly_grand[h].append(v)

    n_hours = 24
    n_total = len(all_vals)

    # IS = n * Σ(x_h_bar - x_bar)² / (p * Σ(x_i - x_bar)²)
    # where n = total observations, p = number of hourly bins
    p = len(hourly_grand)
    numerator_IS = n_total * sum(
        (statistics.mean(hourly_grand[h]) - grand_mean) ** 2
        for h in hourly_grand
    )
    denominator_IS = p * sum((v - grand_mean) ** 2 for v in all_vals)
    IS = numerator_IS / denominator_IS if denominator_IS > 0 else 0

    # IV = n * Σ(x_i - x_{i-1})² / ((n-1) * Σ(x_i - x_bar)²)
    # Use sequential hourly values
    sequential = []
    for day in sorted(hourly_means_by_day.keys()):
        for h in range(24):
            if h in hourly_means_by_day[day]:
                sequential.append(hourly_means_by_day[day][h])

    if len(sequential) < 2:
        return None
    n_seq = len(sequential)
    sq_diffs = sum((sequential[i] - sequential[i-1]) ** 2 for i in range(1, n_seq))
    sq_mean = sum((v - grand_mean) ** 2 for v in sequential)
    IV = n_seq * sq_diffs / ((n_seq - 1) * sq_mean) if sq_mean > 0 else 0

    return {
        "interdaily_stability": round(IS, 4),
        "intradaily_variability": round(IV, 4),
        "IS_interpretation": "very_stable" if IS > 0.6 else "stable" if IS > 0.4 else "unstable",
        "IV_interpretation": "smooth_rhythm" if IV < 0.5 else "moderate" if IV < 1.0 else "fragmented",
    }

# ============================================================================
# 15. ALLOSTATIC LOAD (McEwen 1998, adapted for wearables)
# ============================================================================

def allostatic_load(rhr, hrv, bmi, steps, sleep_h, vo2max, glucose_cv=None, age=None, sex="Male"):
    """
    Allostatic Load Index: cumulative wear-and-tear from chronic stress.
    Count of biomarkers in the "high risk" quartile.
    Reference: McEwen (1998), New England J Med 338:171-179 (concept)
    Adapted for wearable biomarkers.
    """
    score = 0
    max_score = 0
    details = {}

    thresholds = {
        "rhr": (80, "above"),    # High RHR = stress
        "hrv": (25, "below"),    # Low HRV = poor recovery
        "bmi": (30, "above"),    # High BMI = metabolic stress
        "steps": (5000, "below"),# Low activity
        "sleep": (6, "below"),   # Short sleep
        "vo2max": (35, "below"), # Poor fitness
    }

    for name, (thresh, direction) in thresholds.items():
        val = {"rhr": rhr, "hrv": hrv, "bmi": bmi, "steps": steps,
               "sleep": sleep_h, "vo2max": vo2max}.get(name)
        if val is not None:
            max_score += 1
            flagged = (val > thresh if direction == "above" else val < thresh)
            if flagged:
                score += 1
                details[name] = {"value": round(val, 1), "threshold": thresh, "flagged": True}
            else:
                details[name] = {"value": round(val, 1), "threshold": thresh, "flagged": False}

    if glucose_cv is not None:
        max_score += 1
        if glucose_cv > 36:
            score += 1
            details["glucose_cv"] = {"value": round(glucose_cv, 1), "threshold": 36, "flagged": True}
        else:
            details["glucose_cv"] = {"value": round(glucose_cv, 1), "threshold": 36, "flagged": False}

    if max_score == 0:
        return None
    risk = "low" if score <= 1 else "moderate" if score <= 3 else "high"
    return {
        "score": score,
        "max_score": max_score,
        "risk_level": risk,
        "details": details,
    }

# ============================================================================
# 16. DISEASE RISK SCREENING (Evidence-based, multi-condition)
# ============================================================================

def disease_risk_screening(age, sex, bmi, rhr, hrv_sdnn, vo2max, steps_per_day,
                           sleep_hours, glucose_ts, spo2_ts, hr_ts,
                           dfa_alpha, is_val, iv_val, day_night_ratio, weight_trend_kg_yr,
                           walking_speed=None, stair_speed=None, walking_steadiness=None,
                           wrist_temp=None, daylight_minutes=None, headphone_audio_db=None,
                           resp_rate=None, sleep_efficiency=None, sleep_deep_pct=None,
                           sleep_rem_pct=None):
    """
    Evidence-based disease risk screening from wearable biomarkers.
    Each condition uses published clinical criteria adapted for consumer wearables.

    DISCLAIMER: These are SCREENING TOOLS, not diagnoses. A positive screen
    means further clinical evaluation is warranted, not that the condition is present.
    """
    if age is None:
        return None

    screenings = []

    # ------------------------------------------------------------------
    # 1. TYPE 2 DIABETES RISK
    # Adapted from FINDRISC (Lindström & Tuomilehto 2003, Diabetes Care 26:725)
    # ------------------------------------------------------------------
    t2d_score = 0
    t2d_max = 0
    t2d_factors = []

    if age is not None:
        t2d_max += 4
        if age >= 45: t2d_score += 2; t2d_factors.append(f"Age ≥45 (+2)")
        elif age >= 35: t2d_score += 1; t2d_factors.append(f"Age 35-44 (+1)")

    if bmi is not None:
        t2d_max += 3
        if bmi >= 30: t2d_score += 3; t2d_factors.append(f"BMI ≥30 (+3)")
        elif bmi >= 25: t2d_score += 1; t2d_factors.append(f"BMI 25-30 (+1)")

    if steps_per_day is not None:
        t2d_max += 2
        if steps_per_day < 5000: t2d_score += 2; t2d_factors.append(f"Sedentary <5000 steps (+2)")
        elif steps_per_day < 7500: t2d_score += 1; t2d_factors.append(f"Low activity (+1)")

    # Fasting glucose from CGM (4-6 AM readings)
    if glucose_ts and len(glucose_ts) > 50:
        fasting = [v for dt, v in glucose_ts if 4 <= dt.hour <= 6]
        if fasting:
            fasting_avg = statistics.mean(fasting)
            t2d_max += 3
            if fasting_avg >= 126: t2d_score += 3; t2d_factors.append(f"Fasting glucose ≥126 mg/dL (+3)")
            elif fasting_avg >= 100: t2d_score += 2; t2d_factors.append(f"Fasting glucose 100-125 mg/dL — impaired fasting (+2)")
            # Dawn phenomenon amplitude
            pre_dawn = [v for dt, v in glucose_ts if 3 <= dt.hour <= 4]
            post_dawn = [v for dt, v in glucose_ts if 7 <= dt.hour <= 9]
            if pre_dawn and post_dawn:
                dawn_rise = statistics.mean(post_dawn) - statistics.mean(pre_dawn)
                if dawn_rise > 20:
                    t2d_score += 1; t2d_factors.append(f"Exaggerated dawn phenomenon (+1, rise={dawn_rise:.0f} mg/dL)")
                    t2d_max += 1

    if t2d_max > 0:
        risk_pct = t2d_score / t2d_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Type 2 Diabetes",
            "risk_level": risk_level,
            "score": t2d_score,
            "max_score": t2d_max,
            "risk_pct": round(risk_pct, 1),
            "factors": t2d_factors,
            "recommendation": "Consider oral glucose tolerance test (OGTT) if elevated" if risk_pct >= 50 else "Maintain healthy lifestyle",
            "references": ["Lindström & Tuomilehto (2003) Diabetes Care 26:725-731 (FINDRISC)",
                           "ADA Standards of Care 2024"]
        })

    # ------------------------------------------------------------------
    # 2. CARDIOVASCULAR DISEASE RISK
    # Adapted from Framingham + wearable markers
    # (D'Agostino et al. 2008, Circulation 117:743-753)
    # ------------------------------------------------------------------
    cvd_score = 0
    cvd_max = 0
    cvd_factors = []

    if age is not None:
        cvd_max += 2
        if age >= 55: cvd_score += 2; cvd_factors.append("Age ≥55 (+2)")
        elif age >= 45: cvd_score += 1; cvd_factors.append("Age 45-54 (+1)")

    if bmi is not None:
        cvd_max += 2
        if bmi >= 30: cvd_score += 2; cvd_factors.append(f"BMI ≥30: obesity (+2)")
        elif bmi >= 27: cvd_score += 1; cvd_factors.append(f"BMI 27-30: overweight (+1)")

    if rhr is not None:
        cvd_max += 3
        if rhr >= 90: cvd_score += 3; cvd_factors.append(f"RHR ≥90 bpm (+3)")
        elif rhr >= 80: cvd_score += 2; cvd_factors.append(f"RHR 80-89 bpm (+2)")
        elif rhr >= 75: cvd_score += 1; cvd_factors.append(f"RHR 75-79 bpm (+1)")

    if vo2max is not None:
        cvd_max += 3
        if vo2max < 30: cvd_score += 3; cvd_factors.append(f"VO2 Max <30 — poor CRF (+3)")
        elif vo2max < 35: cvd_score += 2; cvd_factors.append(f"VO2 Max 30-35 — below average (+2)")
        elif vo2max < 40: cvd_score += 1; cvd_factors.append(f"VO2 Max 35-40 — average (+1)")

    if hrv_sdnn is not None:
        cvd_max += 2
        if hrv_sdnn < 20: cvd_score += 2; cvd_factors.append(f"HRV SDNN <20 ms — very low (+2)")
        elif hrv_sdnn < 30: cvd_score += 1; cvd_factors.append(f"HRV SDNN 20-30 ms — low (+1)")

    if steps_per_day is not None:
        cvd_max += 2
        if steps_per_day < 4000: cvd_score += 2; cvd_factors.append(f"<4000 steps/day — sedentary (+2)")
        elif steps_per_day < 6000: cvd_score += 1; cvd_factors.append(f"<6000 steps/day (+1)")

    if cvd_max > 0:
        risk_pct = cvd_score / cvd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Cardiovascular Disease",
            "risk_level": risk_level,
            "score": cvd_score,
            "max_score": cvd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": cvd_factors,
            "recommendation": "Prioritize aerobic exercise and VO2 Max improvement" if risk_pct >= 40 else "Continue current cardio maintenance",
            "references": ["D'Agostino et al. (2008) Circulation 117:743-753 (Framingham)",
                           "Fox et al. (2007) CMAJ 177:461-466 (RHR as predictor)",
                           "Kodama et al. (2009) JAMA 301:2024-2035 (CRF meta-analysis)"]
        })

    # ------------------------------------------------------------------
    # 3. OBSTRUCTIVE SLEEP APNEA (OSA) RISK
    # Adapted from STOP-BANG (Chung et al. 2008, Anesthesiology 108:812)
    # + wearable SpO2 data
    # ------------------------------------------------------------------
    osa_score = 0
    osa_max = 0
    osa_factors = []

    if bmi is not None:
        osa_max += 2
        if bmi >= 35: osa_score += 2; osa_factors.append(f"BMI ≥35 (+2)")
        elif bmi >= 30: osa_score += 1; osa_factors.append(f"BMI 30-35 (+1)")

    if sex == "Male":
        osa_max += 1; osa_score += 1; osa_factors.append("Male sex (+1)")

    if age is not None:
        osa_max += 1
        if age >= 50: osa_score += 1; osa_factors.append("Age ≥50 (+1)")

    # Nocturnal SpO2 desaturation from wearable
    if spo2_ts and len(spo2_ts) > 20:
        nocturnal_spo2 = [v for dt, v in spo2_ts if 0 <= dt.hour <= 6]
        if nocturnal_spo2:
            min_spo2 = min(nocturnal_spo2)
            pct_below_90 = sum(1 for v in nocturnal_spo2 if v < 90) / len(nocturnal_spo2) * 100
            osa_max += 3
            if min_spo2 < 85: osa_score += 3; osa_factors.append(f"Nocturnal SpO2 nadir <85% (+3)")
            elif min_spo2 < 90: osa_score += 2; osa_factors.append(f"Nocturnal SpO2 nadir <90% (+2)")
            elif pct_below_90 > 5: osa_score += 1; osa_factors.append(f"SpO2 <90% in {pct_below_90:.1f}% of nocturnal readings (+1)")

    # Elevated nocturnal HR (sign of respiratory effort)
    if hr_ts:
        noct_hr = [v for dt, v in hr_ts if 2 <= dt.hour <= 5]
        if noct_hr and rhr:
            noct_mean = statistics.mean(noct_hr)
            if noct_mean > rhr * 1.1:  # nocturnal HR should be BELOW resting
                osa_max += 1; osa_score += 1
                osa_factors.append(f"Nocturnal HR elevated above daytime RHR (+1)")

    if osa_max > 0:
        risk_pct = osa_score / osa_max * 100
        risk_level = "low" if risk_pct < 30 else "moderate" if risk_pct < 55 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Obstructive Sleep Apnea",
            "risk_level": risk_level,
            "score": osa_score,
            "max_score": osa_max,
            "risk_pct": round(risk_pct, 1),
            "factors": osa_factors,
            "recommendation": "Consider sleep study (polysomnography) if elevated" if risk_pct >= 50 else "Low OSA risk based on available markers",
            "references": ["Chung et al. (2008) Anesthesiology 108:812-821 (STOP-BANG)",
                           "Mendonça et al. (2018) Sleep Med Rev 41:94-106 (SpO2 screening)"]
        })

    # ------------------------------------------------------------------
    # 4. METABOLIC SYNDROME
    # IDF criteria (Alberti et al. 2006, Lancet 366:1059)
    # Adapted: using BMI as waist circumference proxy
    # ------------------------------------------------------------------
    met_criteria = 0
    met_max = 0
    met_factors = []

    if bmi is not None:
        met_max += 1
        if bmi >= 30:  # BMI≥30 as proxy for elevated waist circumference
            met_criteria += 1; met_factors.append("Central obesity (BMI ≥30 as waist proxy)")

    if glucose_ts and len(glucose_ts) > 50:
        fasting = [v for dt, v in glucose_ts if 4 <= dt.hour <= 6]
        if fasting:
            met_max += 1
            if statistics.mean(fasting) >= 100:
                met_criteria += 1; met_factors.append(f"Elevated fasting glucose ≥100 mg/dL ({statistics.mean(fasting):.0f})")

    # Activity as proxy for triglyceride/HDL risk
    if steps_per_day is not None and bmi is not None:
        met_max += 1
        if steps_per_day < 5000 and bmi > 27:
            met_criteria += 1; met_factors.append("Sedentary + overweight (proxy for dyslipidemia risk)")

    if met_max >= 2:
        risk_level = "low" if met_criteria <= 0 else "moderate" if met_criteria == 1 else "elevated" if met_criteria == 2 else "high"
        screenings.append({
            "condition": "Metabolic Syndrome",
            "risk_level": risk_level,
            "score": met_criteria,
            "max_score": met_max,
            "risk_pct": round(met_criteria / met_max * 100, 1),
            "factors": met_factors,
            "recommendation": "Request full lipid panel + fasting glucose from physician" if met_criteria >= 2 else "Maintain current metabolic markers",
            "references": ["Alberti et al. (2006) Lancet 366:1059-1062 (IDF MetS criteria)",
                           "Note: Full diagnosis requires BP + lipids not available from wearables"]
        })

    # ------------------------------------------------------------------
    # 5. AUTONOMIC NEUROPATHY RISK
    # (Vinik et al. 2003, Diabetes Care 26:1553; Shaffer 2017)
    # ------------------------------------------------------------------
    an_score = 0
    an_max = 0
    an_factors = []

    if hrv_sdnn is not None:
        an_max += 3
        if hrv_sdnn < 15: an_score += 3; an_factors.append(f"SDNN <15 ms — severely depressed (+3)")
        elif hrv_sdnn < 25: an_score += 2; an_factors.append(f"SDNN <25 ms — depressed (+2)")
        elif hrv_sdnn < 35: an_score += 1; an_factors.append(f"SDNN <35 ms — borderline (+1)")

    if dfa_alpha is not None:
        an_max += 2
        if dfa_alpha < 0.5 or dfa_alpha > 1.5: an_score += 2; an_factors.append(f"DFA α={dfa_alpha:.2f} — loss of fractal dynamics (+2)")
        elif dfa_alpha < 0.65 or dfa_alpha > 1.3: an_score += 1; an_factors.append(f"DFA α={dfa_alpha:.2f} — borderline (+1)")

    if rhr is not None:
        an_max += 1
        if rhr > 100: an_score += 1; an_factors.append(f"Resting tachycardia >100 bpm (+1)")

    if an_max >= 3:
        risk_pct = an_score / an_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Cardiac Autonomic Neuropathy",
            "risk_level": risk_level,
            "score": an_score,
            "max_score": an_max,
            "risk_pct": round(risk_pct, 1),
            "factors": an_factors,
            "recommendation": "Consider Ewing battery or tilt-table test if elevated" if risk_pct >= 50 else "Autonomic function appears preserved",
            "references": ["Vinik et al. (2003) Diabetes Care 26:1553-1579",
                           "Goldberger et al. (2002) PNAS 99:2466-2472 (fractal dynamics)"]
        })

    # ------------------------------------------------------------------
    # 6. DEPRESSION / CIRCADIAN DISRUPTION RISK
    # (Smagula et al. 2016, J Clin Psychiatry; Lyall et al. 2018, Lancet Psych)
    # ------------------------------------------------------------------
    dep_score = 0
    dep_max = 0
    dep_factors = []

    if is_val is not None:
        dep_max += 2
        if is_val < 0.3: dep_score += 2; dep_factors.append(f"Very unstable circadian rhythm IS={is_val:.2f} (+2)")
        elif is_val < 0.4: dep_score += 1; dep_factors.append(f"Unstable circadian rhythm IS={is_val:.2f} (+1)")

    if iv_val is not None:
        dep_max += 2
        if iv_val > 1.2: dep_score += 2; dep_factors.append(f"Highly fragmented rest-activity IV={iv_val:.2f} (+2)")
        elif iv_val > 0.8: dep_score += 1; dep_factors.append(f"Moderately fragmented IV={iv_val:.2f} (+1)")

    if sleep_hours is not None:
        dep_max += 2
        if sleep_hours < 5: dep_score += 2; dep_factors.append(f"Very short sleep {sleep_hours:.1f}h (+2)")
        elif sleep_hours < 6: dep_score += 1; dep_factors.append(f"Short sleep {sleep_hours:.1f}h (+1)")
        elif sleep_hours > 10: dep_score += 1; dep_factors.append(f"Excessive sleep {sleep_hours:.1f}h (+1)")

    if steps_per_day is not None:
        dep_max += 1
        if steps_per_day < 3000: dep_score += 1; dep_factors.append(f"Very low activity <3000 steps (+1)")

    if dep_max >= 3:
        risk_pct = dep_score / dep_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 45 else "elevated" if risk_pct < 70 else "high"
        screenings.append({
            "condition": "Depression / Circadian Disruption",
            "risk_level": risk_level,
            "score": dep_score,
            "max_score": dep_max,
            "risk_pct": round(risk_pct, 1),
            "factors": dep_factors,
            "recommendation": "Consider PHQ-9 screening; prioritize circadian hygiene (regular sleep/wake times, morning light)" if risk_pct >= 40 else "Circadian rhythm and behavioral markers appear normal",
            "references": ["Lyall et al. (2018) Lancet Psychiatry 5:507-514 (circadian disruption & mood)",
                           "Smagula et al. (2016) J Clin Psychiatry 77:e1085-e1091 (rest-activity & depression)"]
        })

    # ------------------------------------------------------------------
    # 7. HEART FAILURE (EARLY MARKERS)
    # (Arena et al. 2007, Am Heart J; Keteyian et al. 2008, Circulation)
    # ------------------------------------------------------------------
    hf_score = 0
    hf_max = 0
    hf_factors = []

    if vo2max is not None:
        hf_max += 3
        if vo2max < 18: hf_score += 3; hf_factors.append(f"VO2 Max <18 — heart failure range (+3)")
        elif vo2max < 22: hf_score += 2; hf_factors.append(f"VO2 Max <22 — severely impaired (+2)")

    if rhr is not None:
        hf_max += 2
        if rhr > 100: hf_score += 2; hf_factors.append(f"Resting tachycardia >100 (+2)")
        elif rhr > 90: hf_score += 1; hf_factors.append(f"Elevated RHR >90 (+1)")

    if hrv_sdnn is not None:
        hf_max += 2
        if hrv_sdnn < 15: hf_score += 2; hf_factors.append(f"Very low HRV SDNN <15 ms (+2)")

    if hf_max >= 3 and hf_score > 0:
        risk_pct = hf_score / hf_max * 100
        risk_level = "low" if risk_pct < 30 else "moderate" if risk_pct < 55 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Heart Failure (early markers)",
            "risk_level": risk_level,
            "score": hf_score,
            "max_score": hf_max,
            "risk_pct": round(risk_pct, 1),
            "factors": hf_factors,
            "recommendation": "Urgent cardiology referral if elevated; consider BNP/NT-proBNP testing" if risk_pct >= 50 else "No concerning heart failure markers detected",
            "references": ["Arena et al. (2007) Am Heart J 153:918-924",
                           "Keteyian et al. (2008) Circulation 117:2431-2439"]
        })

    # ------------------------------------------------------------------
    # 8. ATRIAL FIBRILLATION RISK
    # Adapted from CHARGE-AF (Alonso et al. 2013, Circulation 127:962)
    # ------------------------------------------------------------------
    af_score = 0
    af_max = 0
    af_factors = []

    if age is not None:
        af_max += 2
        if age >= 65: af_score += 2; af_factors.append("Age ≥65 (+2)")
        elif age >= 50: af_score += 1; af_factors.append("Age 50-64 (+1)")

    if bmi is not None:
        af_max += 1
        if bmi >= 30: af_score += 1; af_factors.append("Obesity BMI ≥30 (+1)")

    # High heart rate events from wearable
    if hr_ts:
        high_hr_events = sum(1 for dt, v in hr_ts if v > 150 and 0 <= dt.hour <= 6)  # nocturnal high HR
        if high_hr_events > 0:
            af_max += 2
            if high_hr_events > 10: af_score += 2; af_factors.append(f"{high_hr_events} nocturnal HR >150 events (+2)")
            elif high_hr_events > 3: af_score += 1; af_factors.append(f"{high_hr_events} nocturnal HR >150 events (+1)")

    if hrv_sdnn is not None:
        af_max += 1
        # Very high HRV can paradoxically indicate irregular rhythm
        if hrv_sdnn > 150: af_score += 1; af_factors.append(f"Very high HRV SDNN={hrv_sdnn:.0f} ms — potential irregularity (+1)")

    if af_max >= 2 and af_score > 0:
        risk_pct = af_score / af_max * 100
        risk_level = "low" if risk_pct < 30 else "moderate" if risk_pct < 55 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Atrial Fibrillation",
            "risk_level": risk_level,
            "score": af_score,
            "max_score": af_max,
            "risk_pct": round(risk_pct, 1),
            "factors": af_factors,
            "recommendation": "Consider 24h Holter monitor or extended ECG monitoring" if risk_pct >= 40 else "Low AF risk based on available markers",
            "references": ["Alonso et al. (2013) Circulation 127:962-972 (CHARGE-AF)",
                           "Perez et al. (2019) NEJM 381:1909-1917 (Apple Watch AF detection)"]
        })

    # ------------------------------------------------------------------
    # 9. HYPOTHYROIDISM SCREENING
    # (Lee DY et al. 2021, Endocrinology and Metabolism 36(6):1121-1130)
    # ------------------------------------------------------------------
    hypo_score = 0
    hypo_max = 0
    hypo_factors = []

    if rhr is not None:
        hypo_max += 2
        if rhr < 55: hypo_score += 2; hypo_factors.append(f"Low RHR {rhr:.0f} bpm — bradycardia (+2)")
        elif rhr < 60: hypo_score += 1; hypo_factors.append(f"RHR {rhr:.0f} bpm — borderline low (+1)")

    if weight_trend_kg_yr is not None:
        hypo_max += 2
        if weight_trend_kg_yr > 3: hypo_score += 2; hypo_factors.append(f"Significant weight gain trend (+2)")
        elif weight_trend_kg_yr > 1.5: hypo_score += 1; hypo_factors.append(f"Moderate weight gain trend (+1)")

    if sleep_hours is not None:
        hypo_max += 2
        if sleep_hours > 10: hypo_score += 2; hypo_factors.append(f"Excessive sleep {sleep_hours:.1f}h — hypersomnia (+2)")
        elif sleep_hours > 9: hypo_score += 1; hypo_factors.append(f"Long sleep {sleep_hours:.1f}h (+1)")

    if wrist_temp is not None:
        hypo_max += 1
        if wrist_temp < 32.5: hypo_score += 1; hypo_factors.append(f"Low wrist temperature {wrist_temp:.1f}C (+1)")

    if steps_per_day is not None:
        hypo_max += 1
        if steps_per_day < 4000: hypo_score += 1; hypo_factors.append(f"Reduced activity <4000 steps (+1)")

    if hypo_max >= 4 and len(hypo_factors) >= 2:
        risk_pct = hypo_score / hypo_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Hypothyroidism",
            "risk_level": risk_level,
            "score": hypo_score,
            "max_score": hypo_max,
            "risk_pct": round(risk_pct, 1),
            "factors": hypo_factors,
            "recommendation": "Consider TSH and free T4 blood test if elevated" if risk_pct >= 50 else "Low hypothyroidism risk based on wearable markers",
            "references": ["Lee DY et al. (2021) Endocrinology and Metabolism 36(6):1121-1130",
                           "Biondi B & Cooper DS (2008) Endocrine Reviews 29(1):76-131"]
        })

    # ------------------------------------------------------------------
    # 10. HYPERTHYROIDISM SCREENING
    # (Lee DY et al. 2021)
    # ------------------------------------------------------------------
    hyper_score = 0
    hyper_max = 0
    hyper_factors = []

    if rhr is not None:
        hyper_max += 2
        if rhr > 100: hyper_score += 2; hyper_factors.append(f"Resting tachycardia RHR={rhr:.0f} bpm (+2)")
        elif rhr > 90: hyper_score += 1; hyper_factors.append(f"Elevated RHR={rhr:.0f} bpm (+1)")

    if weight_trend_kg_yr is not None:
        hyper_max += 2
        if weight_trend_kg_yr < -3: hyper_score += 2; hyper_factors.append(f"Significant weight loss trend (+2)")
        elif weight_trend_kg_yr < -1.5: hyper_score += 1; hyper_factors.append(f"Moderate weight loss trend (+1)")

    if sleep_hours is not None:
        hyper_max += 1
        if sleep_hours < 5: hyper_score += 1; hyper_factors.append(f"Short sleep {sleep_hours:.1f}h — insomnia pattern (+1)")

    if hrv_sdnn is not None:
        hyper_max += 2
        if hrv_sdnn < 15: hyper_score += 2; hyper_factors.append(f"Very low HRV SDNN={hrv_sdnn:.0f}ms — sympathetic overdrive (+2)")
        elif hrv_sdnn < 25: hyper_score += 1; hyper_factors.append(f"Low HRV SDNN={hrv_sdnn:.0f}ms (+1)")

    if sleep_efficiency is not None:
        hyper_max += 1
        if sleep_efficiency < 80: hyper_score += 1; hyper_factors.append(f"Low sleep efficiency {sleep_efficiency:.0f}% (+1)")

    if hyper_max >= 4 and len(hyper_factors) >= 2:
        risk_pct = hyper_score / hyper_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Hyperthyroidism",
            "risk_level": risk_level,
            "score": hyper_score,
            "max_score": hyper_max,
            "risk_pct": round(risk_pct, 1),
            "factors": hyper_factors,
            "recommendation": "Consider TSH and free T4 blood test if elevated" if risk_pct >= 50 else "Low hyperthyroidism risk based on wearable markers",
            "references": ["Lee DY et al. (2021) Endocrinology and Metabolism 36(6):1121-1130",
                           "Boelaert K et al. (2010) Am J Med 123(2):183.e1-9"]
        })

    # ------------------------------------------------------------------
    # 11. INSULIN RESISTANCE / PRE-DIABETES
    # (Hall 2018 PLOS Biology, Shah 2019, Battelino 2019, FINDRISC)
    # ------------------------------------------------------------------
    ir_score = 0
    ir_max = 0
    ir_factors = []

    if glucose_ts and len(glucose_ts) > 50:
        gvals = [v for _, v in glucose_ts]
        g_mean = statistics.mean(gvals)
        g_sd = statistics.stdev(gvals) if len(gvals) >= 2 else 0

        # Fasting glucose (4-6 AM)
        fasting = [v for dt, v in glucose_ts if 4 <= dt.hour <= 6]
        if fasting:
            fasting_avg = statistics.mean(fasting)
            ir_max += 3
            if fasting_avg >= 126: ir_score += 3; ir_factors.append(f"Fasting glucose {fasting_avg:.0f} mg/dL — diabetic range (+3)")
            elif fasting_avg >= 100: ir_score += 2; ir_factors.append(f"Fasting glucose {fasting_avg:.0f} mg/dL — impaired (+2)")

        # Time in range (70-180)
        tir = sum(1 for v in gvals if 70 <= v <= 180) / len(gvals) * 100
        ir_max += 2
        if tir < 90: ir_score += 2; ir_factors.append(f"TIR {tir:.0f}% — below 90% (+2)")
        elif tir < 96: ir_score += 1; ir_factors.append(f"TIR {tir:.0f}% — below healthy 96% (+1)")

        # Glucose CV%
        if g_mean > 0:
            cv_pct = g_sd / g_mean * 100
            ir_max += 2
            if cv_pct > 36: ir_score += 2; ir_factors.append(f"Glucose CV {cv_pct:.0f}% — high variability (+2)")
            elif cv_pct > 20: ir_score += 1; ir_factors.append(f"Glucose CV {cv_pct:.0f}% — moderate variability (+1)")

        # GMI (estimated A1c)
        gmi = 3.31 + 0.02392 * g_mean
        ir_max += 2
        if gmi >= 6.5: ir_score += 2; ir_factors.append(f"GMI {gmi:.1f}% — diabetic range (+2)")
        elif gmi >= 5.7: ir_score += 1; ir_factors.append(f"GMI {gmi:.1f}% — pre-diabetic range (+1)")

        # Dawn phenomenon
        pre_dawn = [v for dt, v in glucose_ts if 3 <= dt.hour <= 4]
        post_dawn = [v for dt, v in glucose_ts if 7 <= dt.hour <= 9]
        if pre_dawn and post_dawn:
            dawn_rise = statistics.mean(post_dawn) - statistics.mean(pre_dawn)
            ir_max += 1
            if dawn_rise > 20: ir_score += 1; ir_factors.append(f"Dawn phenomenon rise {dawn_rise:.0f} mg/dL (+1)")

    if bmi is not None:
        ir_max += 2
        if bmi >= 30: ir_score += 2; ir_factors.append(f"BMI {bmi:.1f} — obesity (+2)")
        elif bmi >= 25: ir_score += 1; ir_factors.append(f"BMI {bmi:.1f} — overweight (+1)")

    if age is not None:
        ir_max += 1
        if age >= 45: ir_score += 1; ir_factors.append(f"Age >=45 (+1)")

    if steps_per_day is not None:
        ir_max += 1
        if steps_per_day < 5000: ir_score += 1; ir_factors.append(f"Sedentary <5000 steps/day (+1)")

    if ir_max >= 4 and len(ir_factors) >= 2:
        risk_pct = ir_score / ir_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Insulin Resistance / Pre-diabetes",
            "risk_level": risk_level,
            "score": ir_score,
            "max_score": ir_max,
            "risk_pct": round(risk_pct, 1),
            "factors": ir_factors,
            "recommendation": "Consider HbA1c and OGTT; consult endocrinologist if elevated" if risk_pct >= 50 else "Glucose patterns within acceptable range",
            "references": ["Hall H et al. (2018) PLOS Biology 16(7):e2005143",
                           "Shah VN et al. (2019) J Clin Endocrinol Metab 104(10):4356-4364",
                           "Battelino T et al. (2019) Diabetes Care 42(8):1593-1603",
                           "Monnier L et al. (2017) Diabetes Care 40(7):832-838"]
        })

    # ------------------------------------------------------------------
    # 12. HYPERTENSION RISK
    # (Krivoshei 2022, Palatini 1999, Fox 2007, Tsuji 1996)
    # ------------------------------------------------------------------
    htn_score = 0
    htn_max = 0
    htn_factors = []

    if rhr is not None:
        htn_max += 2
        if rhr > 80: htn_score += 2; htn_factors.append(f"RHR >80 bpm ({rhr:.0f}) (+2)")
        elif rhr > 75: htn_score += 1; htn_factors.append(f"RHR 75-80 bpm ({rhr:.0f}) (+1)")

    if hrv_sdnn is not None:
        htn_max += 2
        if hrv_sdnn < 25: htn_score += 2; htn_factors.append(f"HRV SDNN <25 ms ({hrv_sdnn:.0f}) (+2)")
        elif hrv_sdnn < 35: htn_score += 1; htn_factors.append(f"HRV SDNN 25-35 ms ({hrv_sdnn:.0f}) (+1)")

    if day_night_ratio is not None:
        htn_max += 2
        if day_night_ratio < 1.10: htn_score += 2; htn_factors.append(f"Non-dipping HR pattern ratio={day_night_ratio:.2f} (+2)")
    elif hr_ts:
        day_hr = [v for dt, v in hr_ts if 8 <= dt.hour <= 20]
        night_hr = [v for dt, v in hr_ts if 0 <= dt.hour <= 5]
        if day_hr and night_hr:
            dn_ratio = statistics.mean(day_hr) / statistics.mean(night_hr)
            htn_max += 2
            if dn_ratio < 1.10: htn_score += 2; htn_factors.append(f"Non-dipping HR pattern ratio={dn_ratio:.2f} (+2)")

    if steps_per_day is not None:
        htn_max += 2
        if steps_per_day < 4000: htn_score += 2; htn_factors.append(f"Sedentary <4000 steps/day (+2)")
        elif steps_per_day < 6000: htn_score += 1; htn_factors.append(f"Low activity <6000 steps/day (+1)")

    if bmi is not None:
        htn_max += 2
        if bmi >= 30: htn_score += 2; htn_factors.append(f"BMI >=30 — obesity (+2)")
        elif bmi >= 27: htn_score += 1; htn_factors.append(f"BMI 27-30 (+1)")

    if age is not None:
        htn_max += 2
        if age >= 55: htn_score += 2; htn_factors.append(f"Age >=55 (+2)")
        elif age >= 45: htn_score += 1; htn_factors.append(f"Age >=45 (+1)")

    if htn_max >= 4 and len(htn_factors) >= 2:
        risk_pct = htn_score / htn_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Hypertension Risk",
            "risk_level": risk_level,
            "score": htn_score,
            "max_score": htn_max,
            "risk_pct": round(risk_pct, 1),
            "factors": htn_factors,
            "recommendation": "Consider home BP monitoring and physician evaluation" if risk_pct >= 50 else "Low hypertension risk based on available markers",
            "references": ["Krivoshei L et al. (2022) medRxiv (AI-PPG-ACC-HTN model)",
                           "Palatini P et al. (1999) J Hypertens 17(7):903-910",
                           "Fox K et al. (2007) CMAJ 177(5):461-466",
                           "Tsuji H et al. (1996) Circulation 94(11):2850-2855"]
        })

    # ------------------------------------------------------------------
    # 13. CORONARY ARTERY DISEASE (CAD)
    # (Cole 1999 NEJM — HR recovery <=12 bpm)
    # ------------------------------------------------------------------
    cad_score = 0
    cad_max = 0
    cad_factors = []

    if vo2max is not None:
        cad_max += 3
        if vo2max < 28: cad_score += 3; cad_factors.append(f"VO2 Max <28 — poor CRF (+3)")
        elif vo2max < 35: cad_score += 2; cad_factors.append(f"VO2 Max <35 — below average (+2)")
        elif vo2max < 40: cad_score += 1; cad_factors.append(f"VO2 Max <40 (+1)")

    if rhr is not None:
        cad_max += 2
        if rhr > 90: cad_score += 2; cad_factors.append(f"RHR >90 bpm (+2)")
        elif rhr > 80: cad_score += 1; cad_factors.append(f"RHR >80 bpm (+1)")

    if hrv_sdnn is not None:
        cad_max += 1
        if hrv_sdnn < 20: cad_score += 1; cad_factors.append(f"HRV SDNN <20 ms (+1)")

    if age is not None:
        cad_max += 2
        if age >= 55: cad_score += 2; cad_factors.append(f"Age >=55 (+2)")
        elif age >= 45: cad_score += 1; cad_factors.append(f"Age >=45 (+1)")

    if bmi is not None:
        cad_max += 1
        if bmi >= 30: cad_score += 1; cad_factors.append(f"BMI >=30 (+1)")

    if sex == "Male":
        cad_max += 1; cad_score += 1; cad_factors.append("Male sex (+1)")

    if steps_per_day is not None:
        cad_max += 1
        if steps_per_day < 4000: cad_score += 1; cad_factors.append(f"Sedentary <4000 steps/day (+1)")

    if cad_max >= 4 and len(cad_factors) >= 2:
        risk_pct = cad_score / cad_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Coronary Artery Disease Risk",
            "risk_level": risk_level,
            "score": cad_score,
            "max_score": cad_max,
            "risk_pct": round(risk_pct, 1),
            "factors": cad_factors,
            "recommendation": "Consider cardiac stress test; HRR1 <=12 bpm post-exercise is a strong mortality predictor" if risk_pct >= 50 else "Low CAD risk based on available markers",
            "references": ["Cole CR et al. (1999) NEJM 341(18):1351-1357 (HRR1 <=12 bpm: RR=4.0)",
                           "Kodama S et al. (2009) JAMA 301(19):2024-2035",
                           "D'Agostino RB et al. (2008) Circulation 117(6):743-753"]
        })

    # ------------------------------------------------------------------
    # 14. ORTHOSTATIC HYPOTENSION / POTS
    # (Jang 2020, Sheldon 2015)
    # ------------------------------------------------------------------
    pots_score = 0
    pots_max = 0
    pots_factors = []

    if hr_ts and len(hr_ts) > 100:
        # Detect HR spikes: sudden increases >25 bpm in short windows
        hr_sorted = sorted(hr_ts, key=lambda x: x[0])
        spike_count = 0
        total_hours = 0
        if len(hr_sorted) >= 2:
            total_hours = max(1, (hr_sorted[-1][0] - hr_sorted[0][0]).total_seconds() / 3600)
            for i in range(1, len(hr_sorted)):
                dt_diff = (hr_sorted[i][0] - hr_sorted[i-1][0]).total_seconds()
                if 0 < dt_diff < 300:  # within 5 min
                    hr_diff = hr_sorted[i][1] - hr_sorted[i-1][1]
                    if hr_diff > 25:
                        spike_count += 1
        spike_rate = spike_count / total_hours if total_hours > 0 else 0
        pots_max += 2
        if spike_rate >= 0.9: pots_score += 2; pots_factors.append(f"HR spike rate {spike_rate:.2f}/hour — elevated (+2)")
        elif spike_rate >= 0.5: pots_score += 1; pots_factors.append(f"HR spike rate {spike_rate:.2f}/hour — borderline (+1)")

    if hrv_sdnn is not None:
        pots_max += 2
        if hrv_sdnn < 25: pots_score += 2; pots_factors.append(f"Low HRV SDNN <25 ms (+2)")
        elif hrv_sdnn < 35: pots_score += 1; pots_factors.append(f"HRV SDNN 25-35 ms (+1)")

    if day_night_ratio is not None:
        pots_max += 1
        if day_night_ratio > 1.60: pots_score += 1; pots_factors.append(f"Extreme dipping ratio {day_night_ratio:.2f} — orthostatic tendency (+1)")
    elif hr_ts:
        day_hr = [v for dt, v in hr_ts if 8 <= dt.hour <= 20]
        night_hr = [v for dt, v in hr_ts if 0 <= dt.hour <= 5]
        if day_hr and night_hr:
            dn = statistics.mean(day_hr) / statistics.mean(night_hr)
            pots_max += 1
            if dn > 1.60: pots_score += 1; pots_factors.append(f"Extreme dipping ratio {dn:.2f} (+1)")

    if rhr is not None:
        pots_max += 1
        if rhr > 90: pots_score += 1; pots_factors.append(f"Elevated RHR {rhr:.0f} bpm (+1)")

    if pots_max >= 3 and len(pots_factors) >= 2:
        risk_pct = pots_score / pots_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Orthostatic Hypotension / POTS",
            "risk_level": risk_level,
            "score": pots_score,
            "max_score": pots_max,
            "risk_pct": round(risk_pct, 1),
            "factors": pots_factors,
            "recommendation": "Consider tilt-table test if elevated" if risk_pct >= 50 else "Low orthostatic risk based on HR patterns",
            "references": ["Jang K et al. (2020) Sensors 20(14):3819",
                           "Sheldon RS et al. (2015) Heart Rhythm 12(6):e41-63"]
        })

    # ------------------------------------------------------------------
    # 15. COPD INDICATORS
    # (Zhang 2025, Stove 2023, Wu 2024)
    # ------------------------------------------------------------------
    copd_score = 0
    copd_max = 0
    copd_factors = []

    if spo2_ts and len(spo2_ts) > 20:
        spo2_vals = [v for _, v in spo2_ts]
        resting_spo2 = statistics.mean(spo2_vals)
        nocturnal_spo2 = [v for dt, v in spo2_ts if 0 <= dt.hour <= 6]
        copd_max += 3
        if resting_spo2 < 92: copd_score += 3; copd_factors.append(f"Resting SpO2 <92% ({resting_spo2:.1f}%) (+3)")
        elif resting_spo2 < 94: copd_score += 2; copd_factors.append(f"Resting SpO2 <94% ({resting_spo2:.1f}%) (+2)")
        elif resting_spo2 < 96: copd_score += 1; copd_factors.append(f"Resting SpO2 <96% ({resting_spo2:.1f}%) (+1)")

        if nocturnal_spo2:
            noct_nadir = min(nocturnal_spo2)
            copd_max += 2
            if noct_nadir < 85: copd_score += 2; copd_factors.append(f"Nocturnal SpO2 nadir <85% (+2)")
            elif noct_nadir < 88: copd_score += 1; copd_factors.append(f"Nocturnal SpO2 nadir <88% (+1)")

    if resp_rate is not None:
        copd_max += 2
        if resp_rate > 22: copd_score += 2; copd_factors.append(f"Elevated respiratory rate {resp_rate:.0f}/min (+2)")
        elif resp_rate > 18: copd_score += 1; copd_factors.append(f"Borderline respiratory rate {resp_rate:.0f}/min (+1)")

    if vo2max is not None:
        copd_max += 1
        if vo2max < 22: copd_score += 1; copd_factors.append(f"Very low VO2 Max {vo2max:.0f} — activity limitation (+1)")

    if steps_per_day is not None:
        copd_max += 1
        if steps_per_day < 3000: copd_score += 1; copd_factors.append(f"Very low activity <3000 steps/day (+1)")

    if copd_max >= 3 and len(copd_factors) >= 2:
        risk_pct = copd_score / copd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "COPD Indicators",
            "risk_level": risk_level,
            "score": copd_score,
            "max_score": copd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": copd_factors,
            "recommendation": "Consider spirometry (pulmonary function test) if elevated" if risk_pct >= 50 else "Respiratory markers within acceptable range",
            "references": ["Zhang C et al. (2025) Digital Health 11, DOI:10.1177/20552076251320730",
                           "Stove MP et al. (2023) Resp Care 68(7)",
                           "Wu CT et al. (2024) JMIR mHealth 12:e63047"]
        })

    # ------------------------------------------------------------------
    # 16. PARKINSON'S EARLY DETECTION
    # (Adams 2024 WATCH-PD, Stefani 2023, Diago 2024)
    # ------------------------------------------------------------------
    pd_score = 0
    pd_max = 0
    pd_factors = []

    if walking_steadiness is not None:
        pd_max += 3
        if walking_steadiness == "Very Low": pd_score += 3; pd_factors.append("Walking Steadiness Very Low (+3)")
        elif walking_steadiness == "Low": pd_score += 2; pd_factors.append("Walking Steadiness Low (+2)")

    if walking_speed is not None:
        pd_max += 2
        if walking_speed < 0.8: pd_score += 2; pd_factors.append(f"Walking speed <0.8 m/s ({walking_speed:.2f}) (+2)")
        elif walking_speed < 1.0: pd_score += 1; pd_factors.append(f"Walking speed <1.0 m/s ({walking_speed:.2f}) (+1)")

    if sleep_rem_pct is not None:
        pd_max += 2
        # Elevated REM movement (RBD proxy) -- abnormal REM patterns
        if sleep_rem_pct < 10: pd_score += 2; pd_factors.append(f"Very low REM sleep {sleep_rem_pct:.0f}% — possible RBD (+2)")
        elif sleep_rem_pct < 15: pd_score += 1; pd_factors.append(f"Low REM sleep {sleep_rem_pct:.0f}% (+1)")

    if age is not None:
        pd_max += 1
        if age >= 60: pd_score += 1; pd_factors.append(f"Age >=60 (+1)")

    if steps_per_day is not None:
        pd_max += 1
        if steps_per_day < 4000: pd_score += 1; pd_factors.append(f"Reduced activity <4000 steps (+1)")

    if pd_max >= 3 and len(pd_factors) >= 2:
        risk_pct = pd_score / pd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Parkinson's Disease (early markers)",
            "risk_level": risk_level,
            "score": pd_score,
            "max_score": pd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": pd_factors,
            "recommendation": "Consider neurological evaluation if elevated; RBD is a strong Parkinson's prodrome" if risk_pct >= 50 else "Low risk based on gait and sleep markers",
            "references": ["Adams JL et al. (2024) npj Parkinson's Disease 10:64 (WATCH-PD)",
                           "Stefani A et al. (2023) Movement Disorders 38(5):847-855",
                           "Diago EB et al. (2024) npj Digital Medicine 8:158"]
        })

    # ------------------------------------------------------------------
    # 17. COGNITIVE DECLINE RISK
    # (Doi 2022 JAMA, Grande 2019, Witting 1990)
    # ------------------------------------------------------------------
    cog_score = 0
    cog_max = 0
    cog_factors = []

    if walking_speed is not None:
        cog_max += 3
        if walking_speed < 0.8: cog_score += 3; cog_factors.append(f"Walking speed <0.8 m/s — strong dementia risk marker (+3)")
        elif walking_speed < 1.0: cog_score += 1; cog_factors.append(f"Walking speed <1.0 m/s (+1)")

    if is_val is not None:
        cog_max += 2
        if is_val < 0.3: cog_score += 2; cog_factors.append(f"Very unstable circadian rhythm IS={is_val:.2f} (+2)")
        elif is_val < 0.4: cog_score += 1; cog_factors.append(f"Unstable circadian IS={is_val:.2f} (+1)")

    if iv_val is not None:
        cog_max += 2
        if iv_val > 1.0: cog_score += 2; cog_factors.append(f"Highly fragmented activity IV={iv_val:.2f} (+2)")
        elif iv_val > 0.7: cog_score += 1; cog_factors.append(f"Fragmented activity IV={iv_val:.2f} (+1)")

    if sleep_efficiency is not None:
        cog_max += 1
        if sleep_efficiency < 75: cog_score += 1; cog_factors.append(f"Low sleep efficiency {sleep_efficiency:.0f}% (+1)")

    if steps_per_day is not None:
        cog_max += 1
        if steps_per_day < 3000: cog_score += 1; cog_factors.append(f"Very low activity <3000 steps (+1)")

    if age is not None:
        cog_max += 1
        if age >= 65: cog_score += 1; cog_factors.append(f"Age >=65 (+1)")

    if cog_max >= 4 and len(cog_factors) >= 2:
        risk_pct = cog_score / cog_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Cognitive Decline Risk",
            "risk_level": risk_level,
            "score": cog_score,
            "max_score": cog_max,
            "risk_pct": round(risk_pct, 1),
            "factors": cog_factors,
            "recommendation": "Consider neuropsychological evaluation; dual gait+activity decline is a strong predictor" if risk_pct >= 50 else "Low cognitive decline risk",
            "references": ["Doi T et al. (2022) JAMA Network Open 5(5):e2214647",
                           "Grande G et al. (2019) JAMA Neurology 76(10):1197-1205",
                           "Witting W et al. (1990) Biol Psychiatry 27(6):563-572"]
        })

    # ------------------------------------------------------------------
    # 18. SEIZURE RISK MARKERS
    # (Regalia 2024, Pipatpratarnporn 2023)
    # ------------------------------------------------------------------
    sz_score = 0
    sz_max = 0
    sz_factors = []

    if hr_ts and len(hr_ts) > 100:
        # Nocturnal unexplained tachycardia episodes (HR >120 during sleep)
        noct_tachy = [v for dt, v in hr_ts if 0 <= dt.hour <= 6 and v > 120]
        noct_total = [v for dt, v in hr_ts if 0 <= dt.hour <= 6]
        sz_max += 3
        if len(noct_tachy) > 10: sz_score += 3; sz_factors.append(f"{len(noct_tachy)} nocturnal HR >120 episodes — recurrent (+3)")
        elif len(noct_tachy) > 3: sz_score += 2; sz_factors.append(f"{len(noct_tachy)} nocturnal HR >120 episodes (+2)")
        elif len(noct_tachy) > 0: sz_score += 1; sz_factors.append(f"{len(noct_tachy)} nocturnal HR >120 episode(s) (+1)")

        # HR spikes >30 bpm within 30 seconds (stereotyped tachycardia events)
        hr_sorted_sz = sorted(hr_ts, key=lambda x: x[0])
        sudden_spikes = 0
        for i in range(1, len(hr_sorted_sz)):
            dt_diff = (hr_sorted_sz[i][0] - hr_sorted_sz[i-1][0]).total_seconds()
            if 0 < dt_diff < 60:
                if hr_sorted_sz[i][1] - hr_sorted_sz[i-1][1] > 30:
                    sudden_spikes += 1
        sz_max += 2
        if sudden_spikes > 5: sz_score += 2; sz_factors.append(f"{sudden_spikes} sudden HR spike events >30 bpm (+2)")
        elif sudden_spikes > 1: sz_score += 1; sz_factors.append(f"{sudden_spikes} sudden HR spike event(s) >30 bpm (+1)")

    if hrv_sdnn is not None:
        sz_max += 1
        if hrv_sdnn < 20: sz_score += 1; sz_factors.append(f"Very low HRV SDNN <20 ms (+1)")

    if sz_max >= 3 and len(sz_factors) >= 2:
        risk_pct = sz_score / sz_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Seizure Risk Markers",
            "risk_level": risk_level,
            "score": sz_score,
            "max_score": sz_max,
            "risk_pct": round(risk_pct, 1),
            "factors": sz_factors,
            "recommendation": "Consider EEG and neurological evaluation if elevated" if risk_pct >= 50 else "No concerning seizure-related HR patterns detected",
            "references": ["Regalia G et al. (2024) Epilepsy & Behavior 158:109911",
                           "Pipatpratarnporn C et al. (2023) Epilepsia 64(11):3046-3057",
                           "Beniczky S et al. (2023) Epilepsy & Behavior 148:109455"]
        })

    # ------------------------------------------------------------------
    # 19. SARCOPENIA RISK
    # (EWGSOP2 Cruz-Jentoft 2019, Kim 2019, Galluzzo 2021)
    # ------------------------------------------------------------------
    sarc_score = 0
    sarc_max = 0
    sarc_factors = []

    if walking_speed is not None:
        sarc_max += 3
        if walking_speed < 0.8: sarc_score += 3; sarc_factors.append(f"Walking speed <0.8 m/s — EWGSOP2 cutoff (+3)")
        elif walking_speed < 1.0: sarc_score += 1; sarc_factors.append(f"Walking speed <1.0 m/s (+1)")

    if stair_speed is not None:
        sarc_max += 2
        # stair_speed in floors/min or similar; low values suggest weakness
        if stair_speed < 0.5: sarc_score += 2; sarc_factors.append(f"Very slow stair climb speed (+2)")
        elif stair_speed < 0.8: sarc_score += 1; sarc_factors.append(f"Slow stair climb speed (+1)")

    if steps_per_day is not None:
        sarc_max += 2
        if steps_per_day < 3000: sarc_score += 2; sarc_factors.append(f"Very low activity <3000 steps/day (+2)")
        elif steps_per_day < 5000: sarc_score += 1; sarc_factors.append(f"Low activity <5000 steps/day (+1)")

    if age is not None:
        sarc_max += 2
        if age >= 70: sarc_score += 2; sarc_factors.append(f"Age >=70 — major sarcopenia risk (+2)")
        elif age >= 60: sarc_score += 1; sarc_factors.append(f"Age >=60 (+1)")

    if weight_trend_kg_yr is not None:
        sarc_max += 1
        if weight_trend_kg_yr < -2: sarc_score += 1; sarc_factors.append(f"Weight loss trend — possible muscle mass loss (+1)")

    if sarc_max >= 4 and len(sarc_factors) >= 2:
        risk_pct = sarc_score / sarc_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Sarcopenia Risk",
            "risk_level": risk_level,
            "score": sarc_score,
            "max_score": sarc_max,
            "risk_pct": round(risk_pct, 1),
            "factors": sarc_factors,
            "recommendation": "Consider DEXA body composition scan and grip strength test" if risk_pct >= 50 else "Low sarcopenia risk",
            "references": ["Cruz-Jentoft AJ et al. (2019) Age and Ageing 48(1):16-31 (EWGSOP2)",
                           "Kim H et al. (2019) Innovation in Aging 3(S1):S885",
                           "Galluzzo V et al. (2021) Sensors 21(5):1786"]
        })

    # ------------------------------------------------------------------
    # 20. FALL RISK
    # (Apple Walking Steadiness, Howcroft 2021)
    # ------------------------------------------------------------------
    fall_score = 0
    fall_max = 0
    fall_factors = []

    if walking_steadiness is not None:
        fall_max += 3
        if walking_steadiness == "Very Low": fall_score += 3; fall_factors.append("Walking Steadiness Very Low — >3x fall risk (+3)")
        elif walking_steadiness == "Low": fall_score += 2; fall_factors.append("Walking Steadiness Low — elevated fall risk (+2)")

    if walking_speed is not None:
        fall_max += 3
        if walking_speed < 0.8: fall_score += 3; fall_factors.append(f"Walking speed <0.8 m/s (+3)")
        elif walking_speed < 1.0: fall_score += 1; fall_factors.append(f"Walking speed <1.0 m/s (+1)")

    if age is not None:
        fall_max += 2
        if age >= 75: fall_score += 2; fall_factors.append(f"Age >=75 (+2)")
        elif age >= 65: fall_score += 1; fall_factors.append(f"Age >=65 (+1)")

    if steps_per_day is not None:
        fall_max += 1
        if steps_per_day < 3000: fall_score += 1; fall_factors.append(f"Very low activity <3000 steps (+1)")

    if stair_speed is not None:
        fall_max += 1
        if stair_speed < 0.5: fall_score += 1; fall_factors.append(f"Slow stair speed — balance concern (+1)")

    if fall_max >= 3 and len(fall_factors) >= 2:
        risk_pct = fall_score / fall_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Fall Risk",
            "risk_level": risk_level,
            "score": fall_score,
            "max_score": fall_max,
            "risk_pct": round(risk_pct, 1),
            "factors": fall_factors,
            "recommendation": "Consider fall prevention program and home safety assessment" if risk_pct >= 50 else "Low fall risk based on gait metrics",
            "references": ["Apple Heart & Movement Study (2021+) Walking Steadiness",
                           "Howcroft J et al. (2021) Scientific Reports 11:20459",
                           "Ye B et al. (2020) JMIR mHealth uHealth 8(7):e19032"]
        })

    # ------------------------------------------------------------------
    # 21. INSOMNIA
    # (Morin 2017, Khosla 2018 AASM, Marino 2013)
    # ------------------------------------------------------------------
    ins_score = 0
    ins_max = 0
    ins_factors = []

    if sleep_efficiency is not None:
        ins_max += 3
        # Wearable overestimates by 5-15%; use stricter threshold
        if sleep_efficiency < 75: ins_score += 3; ins_factors.append(f"Very low sleep efficiency {sleep_efficiency:.0f}% (+3)")
        elif sleep_efficiency < 80: ins_score += 2; ins_factors.append(f"Low sleep efficiency {sleep_efficiency:.0f}% — below 85% clinical threshold (wearable-corrected) (+2)")
        elif sleep_efficiency < 85: ins_score += 1; ins_factors.append(f"Borderline sleep efficiency {sleep_efficiency:.0f}% (+1)")

    if sleep_hours is not None:
        ins_max += 2
        if sleep_hours < 5: ins_score += 2; ins_factors.append(f"Very short sleep {sleep_hours:.1f}h (+2)")
        elif sleep_hours < 6: ins_score += 1; ins_factors.append(f"Short sleep {sleep_hours:.1f}h (+1)")

    if rhr is not None:
        ins_max += 1
        # Hyperarousal marker
        if rhr > 80: ins_score += 1; ins_factors.append(f"Elevated RHR {rhr:.0f} bpm — possible hyperarousal (+1)")

    if hrv_sdnn is not None:
        ins_max += 1
        if hrv_sdnn < 25: ins_score += 1; ins_factors.append(f"Low HRV — autonomic hyperarousal (+1)")

    if ins_max >= 3 and len(ins_factors) >= 2:
        risk_pct = ins_score / ins_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Insomnia",
            "risk_level": risk_level,
            "score": ins_score,
            "max_score": ins_max,
            "risk_pct": round(risk_pct, 1),
            "factors": ins_factors,
            "recommendation": "Consider CBT-I (cognitive behavioral therapy for insomnia); avoid hypnotics as first-line" if risk_pct >= 50 else "Sleep markers within acceptable range",
            "references": ["Morin CM et al. (2017) Nature Reviews Disease Primers 3:17026",
                           "Khosla S et al. (2018) JCSM 14(7):1231-1237 (AASM actigraphy guideline)",
                           "Marino M et al. (2013) Sleep 36(11):1747-1755"]
        })

    # ------------------------------------------------------------------
    # 22. REM SLEEP BEHAVIOR DISORDER (Parkinson's prodrome)
    # (Stefani 2023, Diago 2024)
    # ------------------------------------------------------------------
    rbd_score = 0
    rbd_max = 0
    rbd_factors = []

    if sleep_rem_pct is not None:
        rbd_max += 3
        if sleep_rem_pct < 10: rbd_score += 3; rbd_factors.append(f"Very low REM {sleep_rem_pct:.0f}% — abnormal REM architecture (+3)")
        elif sleep_rem_pct < 15: rbd_score += 2; rbd_factors.append(f"Low REM {sleep_rem_pct:.0f}% (+2)")
        elif sleep_rem_pct < 20: rbd_score += 1; rbd_factors.append(f"Below-normal REM {sleep_rem_pct:.0f}% (+1)")

    if sleep_deep_pct is not None:
        rbd_max += 1
        if sleep_deep_pct < 10: rbd_score += 1; rbd_factors.append(f"Low deep sleep {sleep_deep_pct:.0f}% — disrupted sleep architecture (+1)")

    if age is not None:
        rbd_max += 1
        if age >= 60: rbd_score += 1; rbd_factors.append(f"Age >=60 — RBD risk increases with age (+1)")

    if sleep_efficiency is not None:
        rbd_max += 1
        if sleep_efficiency < 80: rbd_score += 1; rbd_factors.append(f"Low sleep efficiency {sleep_efficiency:.0f}% (+1)")

    if rbd_max >= 3 and len(rbd_factors) >= 2:
        risk_pct = rbd_score / rbd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "REM Sleep Behavior Disorder",
            "risk_level": risk_level,
            "score": rbd_score,
            "max_score": rbd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": rbd_factors,
            "recommendation": "Consider video polysomnography; RBD converts to PD/DLB at ~6.3%/year" if risk_pct >= 50 else "No concerning RBD markers detected",
            "references": ["Stefani A et al. (2023) Movement Disorders 38(5):847-855 (sens 88.1%, spec 100%)",
                           "Diago EB et al. (2024) npj Digital Medicine 8:158 (multicenter validation)",
                           "Iranzo A et al. (2006) Sleep Medicine 7:S34-S39"]
        })

    # ------------------------------------------------------------------
    # 23. CIRCADIAN RHYTHM SLEEP DISORDER
    # (Witting 1990, Cornelissen 2014, Lyall 2018)
    # ------------------------------------------------------------------
    crsd_score = 0
    crsd_max = 0
    crsd_factors = []

    if is_val is not None:
        crsd_max += 3
        if is_val < 0.2: crsd_score += 3; crsd_factors.append(f"Extremely unstable circadian IS={is_val:.2f} (+3)")
        elif is_val < 0.3: crsd_score += 2; crsd_factors.append(f"Very unstable circadian IS={is_val:.2f} (+2)")
        elif is_val < 0.4: crsd_score += 1; crsd_factors.append(f"Unstable circadian IS={is_val:.2f} (+1)")

    if iv_val is not None:
        crsd_max += 3
        if iv_val > 1.2: crsd_score += 3; crsd_factors.append(f"Extremely fragmented activity IV={iv_val:.2f} (+3)")
        elif iv_val > 1.0: crsd_score += 2; crsd_factors.append(f"Highly fragmented activity IV={iv_val:.2f} (+2)")
        elif iv_val > 0.7: crsd_score += 1; crsd_factors.append(f"Moderately fragmented activity IV={iv_val:.2f} (+1)")

    if sleep_hours is not None:
        crsd_max += 1
        # Extreme sleep durations suggest circadian misalignment
        if sleep_hours < 4 or sleep_hours > 11: crsd_score += 1; crsd_factors.append(f"Extreme sleep duration {sleep_hours:.1f}h (+1)")

    if sleep_efficiency is not None:
        crsd_max += 1
        if sleep_efficiency < 75: crsd_score += 1; crsd_factors.append(f"Very low sleep efficiency {sleep_efficiency:.0f}% (+1)")

    if crsd_max >= 4 and len(crsd_factors) >= 2:
        risk_pct = crsd_score / crsd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Circadian Rhythm Sleep Disorder",
            "risk_level": risk_level,
            "score": crsd_score,
            "max_score": crsd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": crsd_factors,
            "recommendation": "Consider actigraphy study and sleep specialist referral; prioritize regular sleep-wake schedule" if risk_pct >= 50 else "Circadian rhythm within acceptable range",
            "references": ["Witting W et al. (1990) Biol Psychiatry 27(6):563-572",
                           "Cornelissen G (2014) Theor Biol Med Model 11:16",
                           "Khosla S et al. (2018) JCSM 14(7):1231-1237 (AASM actigraphy guideline)"]
        })

    # ------------------------------------------------------------------
    # 24. ANEMIA INDICATORS
    # (Li 2021 Nature Medicine, Yokusoglu 2007)
    # ------------------------------------------------------------------
    anemia_score = 0
    anemia_max = 0
    anemia_factors = []

    if rhr is not None:
        anemia_max += 2
        if rhr > 90: anemia_score += 2; anemia_factors.append(f"Elevated RHR {rhr:.0f} bpm — compensatory tachycardia (+2)")
        elif rhr > 80: anemia_score += 1; anemia_factors.append(f"RHR {rhr:.0f} bpm — mildly elevated (+1)")

    if vo2max is not None:
        anemia_max += 2
        if vo2max < 25: anemia_score += 2; anemia_factors.append(f"Low VO2 Max {vo2max:.0f} — reduced O2 carrying capacity (+2)")
        elif vo2max < 30: anemia_score += 1; anemia_factors.append(f"Below-average VO2 Max {vo2max:.0f} (+1)")

    if hrv_sdnn is not None:
        anemia_max += 1
        if hrv_sdnn < 25: anemia_score += 1; anemia_factors.append(f"Low HRV SDNN — autonomic strain (+1)")

    if steps_per_day is not None:
        anemia_max += 1
        if steps_per_day < 4000: anemia_score += 1; anemia_factors.append(f"Low activity <4000 steps/day — possible exercise intolerance (+1)")

    if sex == "Female":
        anemia_max += 1; anemia_score += 1; anemia_factors.append("Female sex — higher anemia prevalence (+1)")

    if anemia_max >= 3 and len(anemia_factors) >= 2:
        risk_pct = anemia_score / anemia_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Anemia Indicators",
            "risk_level": risk_level,
            "score": anemia_score,
            "max_score": anemia_max,
            "risk_pct": round(risk_pct, 1),
            "factors": anemia_factors,
            "recommendation": "Consider complete blood count (CBC) with iron studies" if risk_pct >= 50 else "Low anemia risk based on wearable markers",
            "references": ["Li X et al. (2021) Nature Medicine 27:1012-1021 (Stanford smartwatch study)",
                           "Yokusoglu M et al. (2007) Arq Bras Cardiol 89(1):31-35"]
        })

    # ------------------------------------------------------------------
    # 25. ANXIETY DISORDER
    # (Chalmers 2014, Alvares 2013, Tomasi 2024)
    # ------------------------------------------------------------------
    anx_score = 0
    anx_max = 0
    anx_factors = []

    if hrv_sdnn is not None:
        anx_max += 3
        # Age-adjusted thresholds per Chalmers meta-analysis
        low_hrv_threshold = 20 if (age is not None and age < 35) else 15 if (age is not None and age < 50) else 12
        if hrv_sdnn < low_hrv_threshold: anx_score += 3; anx_factors.append(f"HRV SDNN={hrv_sdnn:.0f}ms below age-adjusted threshold {low_hrv_threshold}ms (+3)")
        elif hrv_sdnn < low_hrv_threshold + 10: anx_score += 1; anx_factors.append(f"HRV SDNN={hrv_sdnn:.0f}ms — borderline low (+1)")

    if rhr is not None:
        anx_max += 2
        if rhr > 85: anx_score += 2; anx_factors.append(f"Elevated RHR {rhr:.0f} bpm (+2)")
        elif rhr > 75: anx_score += 1; anx_factors.append(f"RHR {rhr:.0f} bpm — mildly elevated (+1)")

    if sleep_efficiency is not None:
        anx_max += 2
        if sleep_efficiency < 75: anx_score += 2; anx_factors.append(f"Low sleep efficiency {sleep_efficiency:.0f}% — hyperarousal (+2)")
        elif sleep_efficiency < 80: anx_score += 1; anx_factors.append(f"Sleep efficiency {sleep_efficiency:.0f}% — below normal (+1)")

    if sleep_hours is not None:
        anx_max += 1
        if sleep_hours < 5: anx_score += 1; anx_factors.append(f"Very short sleep {sleep_hours:.1f}h (+1)")

    if day_night_ratio is not None:
        anx_max += 1
        if day_night_ratio < 1.10: anx_score += 1; anx_factors.append(f"Non-dipping HR pattern — persistent sympathetic activation (+1)")
    elif hr_ts:
        day_hr = [v for dt, v in hr_ts if 8 <= dt.hour <= 20]
        night_hr = [v for dt, v in hr_ts if 0 <= dt.hour <= 5]
        if day_hr and night_hr:
            dn = statistics.mean(day_hr) / statistics.mean(night_hr)
            anx_max += 1
            if dn < 1.10: anx_score += 1; anx_factors.append(f"Non-dipping HR pattern ratio={dn:.2f} (+1)")

    if anx_max >= 4 and len(anx_factors) >= 2:
        risk_pct = anx_score / anx_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Anxiety Disorder",
            "risk_level": risk_level,
            "score": anx_score,
            "max_score": anx_max,
            "risk_pct": round(risk_pct, 1),
            "factors": anx_factors,
            "recommendation": "Consider GAD-7 screening questionnaire and clinical evaluation" if risk_pct >= 50 else "Low anxiety risk based on HRV and behavioral markers",
            "references": ["Chalmers JA et al. (2014) Frontiers in Psychiatry 5:80 (meta-analysis, d=0.45-0.55)",
                           "Alvares GA et al. (2013) Depress Anxiety 30(12):1128-1134",
                           "Tomasi J et al. (2024) Psychophysiology 61(2):e14481"]
        })

    # ------------------------------------------------------------------
    # 26. HEARING LOSS RISK
    # (WHO 2022, NIOSH 1998)
    # ------------------------------------------------------------------
    hear_score = 0
    hear_max = 0
    hear_factors = []

    if headphone_audio_db is not None:
        hear_max += 4
        if headphone_audio_db > 100: hear_score += 4; hear_factors.append(f"Headphone level {headphone_audio_db:.0f} dBA — immediate damage risk (+4)")
        elif headphone_audio_db > 90: hear_score += 3; hear_factors.append(f"Headphone level {headphone_audio_db:.0f} dBA — unsafe (max 2h/day at this level) (+3)")
        elif headphone_audio_db > 85: hear_score += 2; hear_factors.append(f"Headphone level {headphone_audio_db:.0f} dBA — exceeds NIOSH 8h REL (+2)")
        elif headphone_audio_db > 80: hear_score += 1; hear_factors.append(f"Headphone level {headphone_audio_db:.0f} dBA — approaching caution threshold (+1)")

    if age is not None:
        hear_max += 1
        if age >= 60: hear_score += 1; hear_factors.append(f"Age >=60 — presbycusis risk (+1)")

    if hear_max >= 2 and len(hear_factors) >= 2:
        risk_pct = hear_score / hear_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Hearing Loss Risk",
            "risk_level": risk_level,
            "score": hear_score,
            "max_score": hear_max,
            "risk_pct": round(risk_pct, 1),
            "factors": hear_factors,
            "recommendation": "Reduce headphone volume; consider audiometry if prolonged high exposure" if risk_pct >= 50 else "Audio exposure within safe limits",
            "references": ["WHO (2022) Global standard for safe listening venues and events",
                           "NIOSH (1998) Criteria for Occupational Noise Exposure (85 dBA, 8h TWA)"]
        })

    # ------------------------------------------------------------------
    # 27. CHRONIC FATIGUE INDICATORS (ME/CFS)
    # (Escorihuela 2020, Davenport 2020)
    # ------------------------------------------------------------------
    cfs_score = 0
    cfs_max = 0
    cfs_factors = []

    if hrv_sdnn is not None:
        cfs_max += 2
        if hrv_sdnn < 20: cfs_score += 2; cfs_factors.append(f"Very low HRV SDNN={hrv_sdnn:.0f}ms (+2)")
        elif hrv_sdnn < 30: cfs_score += 1; cfs_factors.append(f"Low HRV SDNN={hrv_sdnn:.0f}ms (+1)")

    if steps_per_day is not None:
        cfs_max += 2
        if steps_per_day < 3000: cfs_score += 2; cfs_factors.append(f"Very low activity <3000 steps/day (+2)")
        elif steps_per_day < 5000: cfs_score += 1; cfs_factors.append(f"Low activity <5000 steps/day (+1)")

    if sleep_hours is not None and sleep_efficiency is not None:
        cfs_max += 2
        # Non-restorative sleep: high duration with low efficiency
        if sleep_hours > 9 and sleep_efficiency < 80: cfs_score += 2; cfs_factors.append(f"Non-restorative sleep: {sleep_hours:.1f}h but {sleep_efficiency:.0f}% efficiency (+2)")
        elif sleep_hours > 8 and sleep_efficiency < 85: cfs_score += 1; cfs_factors.append(f"Possibly non-restorative sleep pattern (+1)")
    elif sleep_hours is not None:
        cfs_max += 1
        if sleep_hours > 10: cfs_score += 1; cfs_factors.append(f"Excessive sleep {sleep_hours:.1f}h (+1)")

    if rhr is not None and steps_per_day is not None:
        cfs_max += 1
        # Elevated HR despite low activity
        if rhr > 80 and steps_per_day < 5000: cfs_score += 1; cfs_factors.append(f"Disproportionate RHR for low activity level (+1)")

    if cfs_max >= 4 and len(cfs_factors) >= 2:
        risk_pct = cfs_score / cfs_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Chronic Fatigue Indicators",
            "risk_level": risk_level,
            "score": cfs_score,
            "max_score": cfs_max,
            "risk_pct": round(risk_pct, 1),
            "factors": cfs_factors,
            "recommendation": "Consider CFS/ME evaluation; rule out other causes (thyroid, anemia, depression)" if risk_pct >= 50 else "No significant chronic fatigue pattern detected",
            "references": ["Escorihuela RM et al. (2020) J Transl Med 18:173",
                           "Davenport TE et al. (2020) Front Physiol (activity patterns in CFS)",
                           "Siepmann M et al. (2021) Sensors 21(11):3746"]
        })

    # ------------------------------------------------------------------
    # 28. INFECTION / FEVER DETECTION
    # (Mishra 2020 Nature, Grant 2020, Natarajan 2020)
    # ------------------------------------------------------------------
    inf_score = 0
    inf_max = 0
    inf_factors = []

    if rhr is not None:
        inf_max += 2
        # Acute RHR elevation >7 bpm above baseline (use absolute thresholds as proxy)
        if rhr > 90: inf_score += 2; inf_factors.append(f"Elevated RHR {rhr:.0f} bpm — possible infection response (+2)")
        elif rhr > 80: inf_score += 1; inf_factors.append(f"RHR {rhr:.0f} bpm — mildly elevated (+1)")

    if wrist_temp is not None:
        inf_max += 3
        if wrist_temp >= 37.5: inf_score += 3; inf_factors.append(f"Wrist temp {wrist_temp:.1f}C >=37.5 — fever range (sens 80%, spec 98%) (+3)")
        elif wrist_temp >= 36.5: inf_score += 1; inf_factors.append(f"Wrist temp {wrist_temp:.1f}C — mildly elevated (+1)")

    if resp_rate is not None:
        inf_max += 2
        if resp_rate > 22: inf_score += 2; inf_factors.append(f"Elevated respiratory rate {resp_rate:.0f}/min (+2)")
        elif resp_rate > 18: inf_score += 1; inf_factors.append(f"Borderline respiratory rate {resp_rate:.0f}/min (+1)")

    if hrv_sdnn is not None:
        inf_max += 1
        if hrv_sdnn < 20: inf_score += 1; inf_factors.append(f"Acutely depressed HRV SDNN={hrv_sdnn:.0f}ms (+1)")

    if steps_per_day is not None:
        inf_max += 1
        if steps_per_day < 2000: inf_score += 1; inf_factors.append(f"Very low activity <2000 steps — acute activity decrease (+1)")

    if sleep_hours is not None:
        inf_max += 1
        if sleep_hours > 10: inf_score += 1; inf_factors.append(f"Excessive sleep {sleep_hours:.1f}h — possible illness response (+1)")

    if inf_max >= 3 and len(inf_factors) >= 2:
        risk_pct = inf_score / inf_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Infection / Fever Detection",
            "risk_level": risk_level,
            "score": inf_score,
            "max_score": inf_max,
            "risk_pct": round(risk_pct, 1),
            "factors": inf_factors,
            "recommendation": "Monitor symptoms; consult physician if febrile symptoms present" if risk_pct >= 50 else "No acute infection markers detected",
            "references": ["Mishra T et al. (2020) Nature Biomedical Engineering 4:1208-1220",
                           "Grant AD et al. (2020) Scientific Reports 10:21640",
                           "Natarajan A et al. (2020) npj Digital Medicine 3:156"]
        })

    # ------------------------------------------------------------------
    # 29. VITAMIN D DEFICIENCY PROXY
    # (Holick 2007 NEJM — theoretical only)
    # ------------------------------------------------------------------
    vitd_score = 0
    vitd_max = 0
    vitd_factors = []

    if daylight_minutes is not None:
        vitd_max += 3
        if daylight_minutes < 10: vitd_score += 3; vitd_factors.append(f"Very low daylight exposure {daylight_minutes:.0f} min/day (+3)")
        elif daylight_minutes < 20: vitd_score += 2; vitd_factors.append(f"Low daylight exposure {daylight_minutes:.0f} min/day (+2)")
        elif daylight_minutes < 30: vitd_score += 1; vitd_factors.append(f"Borderline daylight exposure {daylight_minutes:.0f} min/day (+1)")

    if steps_per_day is not None:
        vitd_max += 1
        if steps_per_day < 2000: vitd_score += 1; vitd_factors.append(f"Very sedentary <2000 steps — likely homebound/indoor (+1)")

    if age is not None:
        vitd_max += 1
        if age >= 65: vitd_score += 1; vitd_factors.append(f"Age >=65 — reduced skin synthesis capacity (+1)")

    if vitd_max >= 3 and len(vitd_factors) >= 2:
        risk_pct = vitd_score / vitd_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Vitamin D Deficiency Proxy",
            "risk_level": risk_level,
            "score": vitd_score,
            "max_score": vitd_max,
            "risk_pct": round(risk_pct, 1),
            "factors": vitd_factors,
            "recommendation": "Consider 25(OH)D blood test; increase outdoor sun exposure" if risk_pct >= 50 else "Daylight exposure appears adequate",
            "references": ["Holick MF (2007) NEJM 357:266-281",
                           "Note: This is a WEAK proxy — Vitamin D status requires blood test"]
        })

    # ------------------------------------------------------------------
    # 30. DEHYDRATION INDICATORS
    # (Li 2021, Seshadri 2021)
    # ------------------------------------------------------------------
    dehy_score = 0
    dehy_max = 0
    dehy_factors = []

    if rhr is not None:
        dehy_max += 2
        # Acute RHR elevation as dehydration marker
        if rhr > 90: dehy_score += 2; dehy_factors.append(f"Elevated RHR {rhr:.0f} bpm — compensatory tachycardia (+2)")
        elif rhr > 80: dehy_score += 1; dehy_factors.append(f"RHR {rhr:.0f} bpm — mildly elevated (+1)")

    if wrist_temp is not None:
        dehy_max += 2
        # Elevated wrist temp from reduced heat dissipation
        if wrist_temp > 36.5: dehy_score += 2; dehy_factors.append(f"Elevated wrist temp {wrist_temp:.1f}C — reduced heat dissipation (+2)")
        elif wrist_temp > 35.5: dehy_score += 1; dehy_factors.append(f"Wrist temp {wrist_temp:.1f}C — mildly elevated (+1)")

    if weight_trend_kg_yr is not None:
        dehy_max += 1
        # Acute weight loss proxy (weight_trend_kg_yr is annualized, but sudden drops suggest dehydration)
        if weight_trend_kg_yr < -5: dehy_score += 1; dehy_factors.append(f"Rapid weight loss trend (+1)")

    if hrv_sdnn is not None:
        dehy_max += 1
        if hrv_sdnn < 25: dehy_score += 1; dehy_factors.append(f"Low HRV — autonomic stress (+1)")

    if dehy_max >= 3 and len(dehy_factors) >= 2:
        risk_pct = dehy_score / dehy_max * 100
        risk_level = "low" if risk_pct < 25 else "moderate" if risk_pct < 50 else "elevated" if risk_pct < 75 else "high"
        screenings.append({
            "condition": "Dehydration Indicators",
            "risk_level": risk_level,
            "score": dehy_score,
            "max_score": dehy_max,
            "risk_pct": round(risk_pct, 1),
            "factors": dehy_factors,
            "recommendation": "Increase fluid intake; monitor during exercise and hot weather" if risk_pct >= 50 else "No acute dehydration markers detected",
            "references": ["Li X et al. (2021) Nature Medicine 27:1012-1021",
                           "Seshadri DR et al. (2021) Sensors 21(13):4469"]
        })

    # Sort by risk percentage descending
    screenings.sort(key=lambda x: -x["risk_pct"])

    return {
        "disclaimer": "These are SCREENING estimates based on consumer wearable data, NOT clinical diagnoses. "
                       "A positive screen means further clinical evaluation is recommended. "
                       "Many conditions require lab tests (blood lipids, HbA1c, BNP) and clinical examination "
                       "not available from wearables. Always consult a healthcare provider.",
        "screenings": screenings,
        "conditions_screened": len(screenings),
        "elevated_count": sum(1 for s in screenings if s["risk_level"] in ("elevated", "high")),
    }


# ============================================================================
# MAIN: Parse XML & Run All Advanced Analytics
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Advanced Apple Health Analytics")
    parser.add_argument("xml_path", nargs="?", help="Path to Apple Health export XML")
    parser.add_argument("--output", choices=["json"], default="json")
    args = parser.parse_args()

    xml_path = args.xml_path
    if not xml_path or not os.path.isfile(xml_path):
        print(json.dumps({"error": "XML file not found"}))
        sys.exit(1)

    # ---- Parse XML (same streaming approach) ----
    # Wrapped so that partial parse failures still yield whatever was collected.
    print("Parsing XML for advanced analysis...", file=sys.stderr)
    hr_ts = []
    glucose_ts = []
    steps_seg = []
    active_cal_seg = []
    hrv_ts = []
    spo2_ts = []
    weight_ts = []
    bf_ts = []
    vo2_ts = []
    rhr_daily = {}
    sleep_records = []
    height_ts = []
    walking_speed_ts = []
    stair_speed_ts = []
    walking_steadiness_ts = []
    wrist_temp_ts = []
    headphone_audio_ts = []
    resp_rate_ts = []
    daylight_ts = []
    me_info = {}
    workouts = []
    xml_parse_error = None

    try:
        ctx = ET.iterparse(xml_path, events=("end",))
        count = 0
        for _, elem in ctx:
            if elem.tag == "Me":
                me_info = dict(elem.attrib)
            elif elem.tag == "Record":
                rtype = elem.attrib.get("type", "")
                value = elem.attrib.get("value")
                start = elem.attrib.get("startDate", "")
                dt = parse_date(start)
                if dt and value:
                    try:
                        val = float(value)
                        if rtype == "HKQuantityTypeIdentifierHeartRate":
                            hr_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierBloodGlucose":
                            glucose_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierStepCount":
                            steps_seg.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierActiveEnergyBurned":
                            active_cal_seg.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN":
                            hrv_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierOxygenSaturation":
                            spo2_ts.append((dt, val * 100))
                        elif rtype == "HKQuantityTypeIdentifierBodyMass":
                            weight_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierBodyFatPercentage":
                            bf_ts.append((dt, val * 100))
                        elif rtype == "HKQuantityTypeIdentifierVO2Max":
                            vo2_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierRestingHeartRate":
                            rhr_daily[dt.strftime("%Y-%m-%d")] = val
                        elif rtype == "HKQuantityTypeIdentifierHeight":
                            height_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierWalkingSpeed":
                            walking_speed_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierStairAscentSpeed":
                            stair_speed_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierAppleWalkingSteadiness":
                            walking_steadiness_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierAppleSleepingWristTemperature":
                            wrist_temp_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierHeadphoneAudioExposure":
                            headphone_audio_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierRespiratoryRate":
                            resp_rate_ts.append((dt, val))
                        elif rtype == "HKQuantityTypeIdentifierTimeInDaylight":
                            daylight_ts.append((dt, val))
                    except ValueError:
                        pass
                if rtype == "HKCategoryTypeIdentifierSleepAnalysis" and dt:
                    end_dt = parse_date(elem.attrib.get("endDate", ""))
                    cat = elem.attrib.get("value", "")
                    if end_dt:
                        sleep_records.append((dt, end_dt, cat))
            elif elem.tag == "Workout":
                workouts.append(dict(elem.attrib))
            elem.clear()
            count += 1
            if count % 500000 == 0:
                print(f"  {count:,}...", file=sys.stderr)
        print(f"  Done: {count:,} elements.", file=sys.stderr)
    except ET.ParseError as e:
        xml_parse_error = f"XML parse error (partial data used): {e}"
        print(f"  WARNING: {xml_parse_error}", file=sys.stderr)
    except Exception as e:
        xml_parse_error = f"Unexpected XML error (partial data used): {e}"
        print(f"  WARNING: {xml_parse_error}", file=sys.stderr)

    for ts in [hr_ts, glucose_ts, steps_seg, active_cal_seg, hrv_ts, spo2_ts,
               weight_ts, bf_ts, vo2_ts, height_ts, walking_speed_ts,
               stair_speed_ts, walking_steadiness_ts, wrist_temp_ts,
               headphone_audio_ts, resp_rate_ts, daylight_ts]:
        ts.sort(key=lambda x: x[0])

    # ---- Derived daily aggregates ----
    d_steps = defaultdict(float)
    for dt, v in steps_seg:
        d_steps[dt.strftime("%Y-%m-%d")] += v
    d_steps = dict(d_steps)

    d_active = defaultdict(float)
    for dt, v in active_cal_seg:
        d_active[dt.strftime("%Y-%m-%d")] += v

    d_hr = defaultdict(list)
    for dt, v in hr_ts:
        d_hr[dt.strftime("%Y-%m-%d")].append(v)
    d_hr_mean = {k: statistics.mean(v) for k, v in d_hr.items()}

    d_hrv = defaultdict(list)
    for dt, v in hrv_ts:
        d_hrv[dt.strftime("%Y-%m-%d")].append(v)
    d_hrv_mean = {k: statistics.mean(v) for k, v in d_hrv.items()}

    # Sleep nightly totals
    night_sleep = defaultdict(float)
    for start_dt, end_dt, cat in sleep_records:
        if "Awake" in cat or "InBed" in cat:
            continue
        dur_h = (end_dt - start_dt).total_seconds() / 3600
        if 0 < dur_h < 14:
            nk = start_dt.strftime("%Y-%m-%d") if start_dt.hour >= 18 else (start_dt - timedelta(days=1)).strftime("%Y-%m-%d")
            night_sleep[nk] += dur_h
    night_sleep = {k: v for k, v in night_sleep.items() if 1 < v < 14}

    # Personal info
    dob = me_info.get("HKCharacteristicTypeIdentifierDateOfBirth", "")
    sex = "Male" if "Male" in me_info.get("HKCharacteristicTypeIdentifierBiologicalSex", "") else "Female"
    try:
        age = round((datetime.now() - datetime.strptime(dob, "%Y-%m-%d")).days / 365.25, 1) if dob else None
    except (ValueError, TypeError):
        age = None
    height_m = None
    if height_ts:
        h = height_ts[-1][1]
        height_m = h / 100 if h > 3 else h

    result = {
        "methods_applied": [],
        "references": [
            "Granger (1969) Econometrica 37(3):424-438",
            "Sugihara et al. (2012) Science 338(6106):496-500",
            "Schreiber (2000) Physical Review Letters 85(2):461-464",
            "Richman & Moorman (2000) Am J Physiol Heart Circ Physiol 278:H2039",
            "Peng et al. (1994) Physical Review E 49:1685",
            "Brennan et al. (2001) IEEE Trans Biomed Eng 48(11):1342-1347",
            "Cornelissen (2014) Theoretical Biology & Medical Modelling 11:16",
            "Kovatchev et al. (2002) Diabetes Care 25:2058-2064",
            "Kovatchev et al. (2006) Diabetes Technology & Therapeutics 8(6):644-653",
            "McDonnell et al. (2005) Diabetes Technology & Therapeutics 7(2):253-263",
            "Peyser et al. (2018) J Diabetes Sci Technol 12(4):718-726",
            "Adams & MacKay (2007) arXiv:0710.3742",
            "Mann (1945) Econometrica 13:245-259; Kendall (1975)",
            "Costa et al. (2002) Physical Review Letters 89(6):068102",
            "Witting et al. (1990) Biological Psychiatry 27:563-572",
            "Nes et al. (2013) Medicine & Science in Sports & Exercise 45(11):2017",
            "Levine (2013) Journals of Gerontology Series A 68(6):667-674",
            "McEwen (1998) New England Journal of Medicine 338:171-179",
            "Cohen (1988) Statistical Power Analysis for the Behavioral Sciences",
            "Efron (1979) The Annals of Statistics 7(1):1-26",
        ],
    }

    if xml_parse_error:
        result["xml_parse_warning"] = xml_parse_error

    # Pre-compute commonly needed aligned series and counts for data_requirements
    common_days = sorted(set(d_steps.keys()) & set(d_hr_mean.keys()))
    rhr_days = sorted(set(d_steps.keys()) & set(rhr_daily.keys()))
    hr_daily_vals = [d_hr_mean[d] for d in sorted(d_hr_mean.keys())]
    hrv_vals = [v for _, v in hrv_ts]
    rhr_sorted = sorted(rhr_daily.items())
    sorted_days = sorted(d_steps.keys())

    # Track data_requirements for each method
    data_requirements = {}

    # ---- Run all advanced analyses ----
    print("Running advanced analytics...", file=sys.stderr)

    # === TREND TESTS ===
    print("  Mann-Kendall trends...", file=sys.stderr)
    try:
        trends = {}
        n_step_days = len(sorted_days)
        mk_steps_met = n_step_days >= 12
        data_requirements["mann_kendall_steps"] = {
            "required": ">=12 days of step data (aggregated weekly)",
            "met": mk_steps_met,
            "actual": f"{n_step_days} days of step data",
        }
        if mk_steps_met:
            weekly_vals = []
            for i in range(0, n_step_days, 7):
                chunk = sorted_days[i:i+7]
                weekly_vals.append(statistics.mean([d_steps[d] for d in chunk]))
            mk_result = mann_kendall(weekly_vals)
            if mk_result is not None:
                trends["steps_weekly"] = mk_result
                result["methods_applied"].append("Mann-Kendall Trend Test")

        mk_rhr_met = len(rhr_sorted) >= 12
        data_requirements["mann_kendall_rhr"] = {
            "required": ">=12 resting HR observations",
            "met": mk_rhr_met,
            "actual": f"{len(rhr_sorted)} resting HR observations",
        }
        if mk_rhr_met:
            mk_result = mann_kendall([v for _, v in rhr_sorted])
            if mk_result is not None:
                trends["resting_hr"] = mk_result

        hrv_weekly = []
        hrv_days_sorted = sorted(d_hrv_mean.keys())
        n_hrv_days = len(hrv_days_sorted)
        if n_hrv_days >= 12:
            for i in range(0, n_hrv_days, 7):
                chunk = hrv_days_sorted[i:i+7]
                hrv_weekly.append(statistics.mean([d_hrv_mean[d] for d in chunk]))
        mk_hrv_met = len(hrv_weekly) >= 8
        data_requirements["mann_kendall_hrv"] = {
            "required": ">=8 weekly HRV aggregates (>=12 days HRV data)",
            "met": mk_hrv_met,
            "actual": f"{n_hrv_days} days HRV data, {len(hrv_weekly)} weekly aggregates",
        }
        if mk_hrv_met:
            mk_result = mann_kendall(hrv_weekly)
            if mk_result is not None:
                trends["hrv_weekly"] = mk_result

        mk_weight_met = len(weight_ts) >= 5
        data_requirements["mann_kendall_weight"] = {
            "required": ">=5 weight observations",
            "met": mk_weight_met,
            "actual": f"{len(weight_ts)} weight observations",
        }
        if mk_weight_met:
            mk_result = mann_kendall([w for _, w in weight_ts])
            if mk_result is not None:
                trends["weight"] = mk_result

        result["trend_tests"] = trends
    except Exception as e:
        print(f"  ERROR in trend tests: {e}", file=sys.stderr)
        result["trend_tests"] = {"error": f"Trend test computation failed: {e}"}

    # === CAUSAL INFERENCE ===
    print("  Causal inference (Granger, TE, CCM)...", file=sys.stderr)
    try:
        causal = {}
        n_common = len(common_days)
        n_rhr_days = len(rhr_days)

        data_requirements["granger_causality"] = {
            "required": ">=50 aligned daily observations (steps + HR)",
            "met": n_common >= 50,
            "actual": f"{n_common} aligned days (steps+HR)",
        }
        data_requirements["transfer_entropy"] = {
            "required": ">=50 aligned daily observations",
            "met": n_common >= 50,
            "actual": f"{n_common} aligned days (steps+HR)",
        }
        data_requirements["ccm"] = {
            "required": ">=80 aligned daily observations (steps + RHR)",
            "met": n_rhr_days >= 80,
            "actual": f"{n_rhr_days} aligned days (steps+RHR)",
        }

        if n_common >= 50:
            steps_aligned = [d_steps[d] for d in common_days]
            hr_aligned = [d_hr_mean[d] for d in common_days]

            # Granger: Steps -> HR
            gc_steps_hr = granger_causality(steps_aligned, hr_aligned, max_lag=4)
            if gc_steps_hr:
                causal["granger_steps_causes_hr"] = gc_steps_hr
                result["methods_applied"].append("Granger Causality Test")

            # Transfer Entropy: Steps -> HR
            te_steps_hr = transfer_entropy(steps_aligned, hr_aligned, lag=1, bins=6)
            if te_steps_hr:
                te_steps_hr["direction"] = "Steps->HR"
                causal["transfer_entropy_steps_to_hr"] = te_steps_hr
                result["methods_applied"].append("Transfer Entropy")

        # Granger/TE for RHR
        if n_rhr_days >= 50:
            steps_r = [d_steps[d] for d in rhr_days]
            rhr_r = [rhr_daily[d] for d in rhr_days]
            gc = granger_causality(steps_r, rhr_r, max_lag=4)
            if gc:
                causal["granger_steps_causes_rhr"] = gc
            te = transfer_entropy(steps_r, rhr_r, lag=1, bins=6)
            if te:
                te["direction"] = "Steps->RHR"
                causal["transfer_entropy_steps_to_rhr"] = te

        # Glucose causal analysis
        if glucose_ts:
            g_daily = defaultdict(list)
            for dt, v in glucose_ts:
                g_daily[dt.strftime("%Y-%m-%d")].append(v)
            g_daily_mean = {k: statistics.mean(v) for k, v in g_daily.items()}
            g_common = sorted(set(d_steps.keys()) & set(g_daily_mean.keys()))
            if len(g_common) >= 20:
                steps_g = [d_steps[d] for d in g_common]
                gluc_g = [g_daily_mean[d] for d in g_common]
                gc = granger_causality(steps_g, gluc_g, max_lag=3)
                if gc:
                    causal["granger_steps_causes_glucose"] = gc

        # CCM: Steps <-> RHR
        if n_rhr_days >= 80:
            print("  CCM convergent cross mapping...", file=sys.stderr)
            steps_ccm = [d_steps[d] for d in rhr_days]
            rhr_ccm = [rhr_daily[d] for d in rhr_days]
            ccm_result = ccm(steps_ccm, rhr_ccm, E=3, tau=1)
            if ccm_result:
                causal["ccm_steps_causes_rhr"] = ccm_result
                result["methods_applied"].append("Convergent Cross Mapping")
            # Reverse direction
            ccm_rev = ccm(rhr_ccm, steps_ccm, E=3, tau=1)
            if ccm_rev:
                causal["ccm_rhr_causes_steps"] = ccm_rev

        result["causal_inference"] = causal
    except Exception as e:
        print(f"  ERROR in causal inference: {e}", file=sys.stderr)
        result["causal_inference"] = {"error": f"Causal inference computation failed: {e}"}

    # === NONLINEAR DYNAMICS ===
    print("  Nonlinear dynamics (SampEn, DFA, Poincare)...", file=sys.stderr)
    try:
        nonlinear = {}
        n_hr_daily = len(hr_daily_vals)
        n_hrv = len(hrv_vals)

        data_requirements["sample_entropy"] = {
            "required": ">=50 daily HR means",
            "met": n_hr_daily >= 50,
            "actual": f"{n_hr_daily} daily HR means",
        }
        data_requirements["dfa"] = {
            "required": ">=50 daily HR means",
            "met": n_hr_daily >= 50,
            "actual": f"{n_hr_daily} daily HR means",
        }
        data_requirements["poincare"] = {
            "required": ">=20 HRV measurements",
            "met": n_hrv >= 20,
            "actual": f"{n_hrv} HRV measurements",
        }
        data_requirements["multiscale_entropy"] = {
            "required": ">=100 daily HR means",
            "met": n_hr_daily >= 100,
            "actual": f"{n_hr_daily} daily HR means",
        }

        # HR Sample Entropy (use daily means for efficiency)
        if n_hr_daily >= 50:
            se = sample_entropy(hr_daily_vals, m=2, r_factor=0.2)
            if se:
                nonlinear["hr_sample_entropy"] = se
                result["methods_applied"].append("Sample Entropy")

        if glucose_ts:
            gvals_nl = [v for _, v in glucose_ts]
            n_glucose_se = len(gvals_nl)
            data_requirements["glucose_sample_entropy"] = {
                "required": ">=100 glucose readings",
                "met": n_glucose_se >= 100,
                "actual": f"{n_glucose_se} glucose readings",
            }
            if n_glucose_se >= 100:
                se_g = sample_entropy(gvals_nl[:2000], m=2, r_factor=0.2)
                if se_g:
                    nonlinear["glucose_sample_entropy"] = se_g

        # DFA on HR
        if n_hr_daily >= 50:
            dfa_result = dfa(hr_daily_vals, min_box=4)
            if dfa_result:
                nonlinear["hr_dfa"] = dfa_result
                result["methods_applied"].append("Detrended Fluctuation Analysis")

        # Poincare on HRV SDNN values (NOTE: this applies Poincare to session-level
        # SDNN measurements, NOT beat-to-beat RR intervals. Results reflect variability
        # of HRV across sessions, not the classical RR-interval Poincare analysis.
        # Published SD1/SD2 norms (Brennan 2001) are for RR intervals — interpret with caution.)
        if n_hrv >= 20:
            poincare = poincare_plot(hrv_vals)
            if poincare:
                poincare["caveat"] = "Applied to session-level SDNN values, not beat-to-beat RR intervals. Published norms may not directly apply."
                nonlinear["hrv_poincare"] = poincare
                result["methods_applied"].append("Poincare Plot Analysis")

        # Multiscale Entropy (Costa et al. 2002) -- run SampEn at multiple scales
        if n_hr_daily >= 100:
            mse = {}
            for scale in [1, 2, 3, 5, 7, 10]:
                # Coarse-grain at scale
                coarse = []
                for i in range(0, n_hr_daily - scale + 1, scale):
                    coarse.append(statistics.mean(hr_daily_vals[i:i+scale]))
                if len(coarse) >= 30:
                    se = sample_entropy(coarse, m=2, r_factor=0.2)
                    if se:
                        mse[f"scale_{scale}"] = se["value"]
            if mse:
                nonlinear["multiscale_entropy"] = mse
                result["methods_applied"].append("Multiscale Entropy")

        result["nonlinear_dynamics"] = nonlinear
    except Exception as e:
        print(f"  ERROR in nonlinear dynamics: {e}", file=sys.stderr)
        result["nonlinear_dynamics"] = {"error": f"Nonlinear dynamics computation failed: {e}"}

    # === ADVANCED GLUCOSE ===
    print("  Advanced glucose metrics...", file=sys.stderr)
    try:
        adv_glucose = {}
        has_glucose = bool(glucose_ts)
        n_glucose = len(glucose_ts) if glucose_ts else 0

        data_requirements["glucose_kovatchev"] = {
            "required": "CGM / glucose data present (>=3 readings)",
            "met": n_glucose >= 3,
            "actual": f"{n_glucose} glucose readings" if n_glucose > 0 else "no glucose data",
        }
        data_requirements["glucose_adrr"] = {
            "required": "CGM data with multiple days of >=5 readings each",
            "met": False,  # Updated below if met
            "actual": f"{n_glucose} glucose readings" if n_glucose > 0 else "no glucose data",
        }
        data_requirements["glucose_conga"] = {
            "required": ">=20 glucose readings with timestamps",
            "met": n_glucose >= 20,
            "actual": f"{n_glucose} glucose readings" if n_glucose > 0 else "no glucose data",
        }
        data_requirements["glucose_gvp"] = {
            "required": ">=20 glucose readings with timestamps",
            "met": n_glucose >= 20,
            "actual": f"{n_glucose} glucose readings" if n_glucose > 0 else "no glucose data",
        }

        if has_glucose:
            gvals = [v for _, v in glucose_ts]

            # Kovatchev LBGI/HBGI
            kov = kovatchev_glucose_risk(gvals)
            if kov:
                adv_glucose["lbgi_hbgi"] = kov
                result["methods_applied"].append("LBGI/HBGI (Kovatchev)")

            # ADRR
            g_by_day = defaultdict(list)
            for dt, v in glucose_ts:
                g_by_day[dt.strftime("%Y-%m-%d")].append(v)
            adrr_result = adrr(g_by_day)
            if adrr_result:
                adv_glucose["adrr"] = adrr_result
                result["methods_applied"].append("ADRR")
                data_requirements["glucose_adrr"]["met"] = True
                data_requirements["glucose_adrr"]["actual"] = f"{adrr_result.get('n_days', 0)} days with >=5 readings"

            # CONGA
            for hours in [1, 2, 4]:
                c = conga(glucose_ts, hours=hours)
                if c:
                    adv_glucose[f"conga_{hours}h"] = c
            if any(f"conga_{h}h" in adv_glucose for h in [1,2,4]):
                result["methods_applied"].append("CONGA")

            # GVP
            gvp_result = gvp(glucose_ts)
            if gvp_result:
                adv_glucose["gvp"] = gvp_result
                result["methods_applied"].append("GVP")

            # Rate of change
            roc = glucose_rate_of_change(glucose_ts)
            if roc:
                adv_glucose["rate_of_change"] = roc

        result["advanced_glucose"] = adv_glucose
    except Exception as e:
        print(f"  ERROR in advanced glucose: {e}", file=sys.stderr)
        result["advanced_glucose"] = {"error": f"Advanced glucose computation failed: {e}"}

    # === CIRCADIAN ANALYSIS ===
    print("  Circadian cosinor analysis...", file=sys.stderr)
    try:
        circadian = {}

        n_hr_ts = len(hr_ts)
        data_requirements["cosinor_hr"] = {
            "required": ">=10 heart rate measurements",
            "met": n_hr_ts >= 10,
            "actual": f"{n_hr_ts} HR measurements",
        }
        data_requirements["rhythm_stability"] = {
            "required": ">=7 days with >=12 hours of HR data each",
            "met": False,  # Updated below if met
            "actual": "computing...",
        }

        # HR cosinor (uniform subsample to avoid time-of-day bias)
        if n_hr_ts >= 10:
            step = max(1, n_hr_ts // 20000)
            hr_sub = hr_ts[::step]
            hr_times = [dt.hour + dt.minute / 60 for dt, _ in hr_sub]
            hr_vals_cos = [v for _, v in hr_sub]
            cos_hr = cosinor(hr_times, hr_vals_cos, period=24.0)
            if cos_hr:
                circadian["hr_cosinor"] = cos_hr
                result["methods_applied"].append("Cosinor Analysis")

        if glucose_ts and len(glucose_ts) >= 10:
            g_times = [dt.hour + dt.minute / 60 for dt, _ in glucose_ts]
            g_vals = [v for _, v in glucose_ts]
            cos_g = cosinor(g_times, g_vals, period=24.0)
            if cos_g:
                circadian["glucose_cosinor"] = cos_g

        # Rhythm stability (IS/IV) for HR
        hr_by_day_hour = defaultdict(lambda: defaultdict(list))
        for dt, v in hr_ts:
            hr_by_day_hour[dt.strftime("%Y-%m-%d")][dt.hour].append(v)
        hr_day_hour_means = {d: {h: statistics.mean(v) for h, v in hrs.items()} for d, hrs in hr_by_day_hour.items()}
        # Only use days with >= 12 hours of data
        good_days = {d: v for d, v in hr_day_hour_means.items() if len(v) >= 12}
        n_good_days = len(good_days)
        rs_met = n_good_days >= 7
        data_requirements["rhythm_stability"]["met"] = rs_met
        data_requirements["rhythm_stability"]["actual"] = f"{n_good_days} days with >=12h HR coverage"
        if rs_met:
            rs = rhythm_stability(good_days)
            if rs:
                circadian["hr_rhythm_stability"] = rs
                result["methods_applied"].append("Interdaily Stability / Intradaily Variability")

        result["circadian_quantification"] = circadian
    except Exception as e:
        print(f"  ERROR in circadian analysis: {e}", file=sys.stderr)
        result["circadian_quantification"] = {"error": f"Circadian analysis computation failed: {e}"}

    # === STATISTICAL RIGOR ===
    print("  Bootstrap CI & effect sizes...", file=sys.stderr)
    try:
        stat_rigor = {}

        data_requirements["bootstrap_ci"] = {
            "required": ">=5 data points per metric",
            "met": bool(rhr_daily) or bool(hrv_vals) or bool(d_steps),
            "actual": f"RHR: {len(rhr_daily)}, HRV: {len(hrv_vals)}, steps days: {len(d_steps)}",
        }
        data_requirements["effect_sizes"] = {
            "required": ">=3 observations in both recent (90d) and prior (90-180d) periods",
            "met": False,  # Updated below if met
            "actual": "computing...",
        }

        # Bootstrap CIs
        boot_cis = {}
        if rhr_daily and len(rhr_daily) >= 5:
            boot_cis["resting_hr"] = bootstrap_ci(list(rhr_daily.values()), n_boot=500)
        if hrv_vals and len(hrv_vals) >= 5:
            boot_cis["hrv_sdnn"] = bootstrap_ci(hrv_vals, n_boot=500)
        if d_steps:
            recent_steps = [v for d, v in d_steps.items() if d >= (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")]
            if len(recent_steps) >= 5:
                boot_cis["recent_daily_steps"] = bootstrap_ci(recent_steps, n_boot=500)
        if glucose_ts:
            gvals_boot = [v for _, v in glucose_ts]
            if len(gvals_boot) >= 5:
                boot_cis["mean_glucose"] = bootstrap_ci(gvals_boot, n_boot=500)
        stat_rigor["bootstrap_ci_95"] = boot_cis
        if boot_cis:
            result["methods_applied"].append("Bootstrap Confidence Intervals")

        # Effect sizes: recent vs prior periods
        effect_sizes = {}
        cutoff = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        prior_start = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

        recent_s = [v for d, v in d_steps.items() if d >= cutoff]
        prior_s = [v for d, v in d_steps.items() if prior_start <= d < cutoff]
        if len(recent_s) >= 3 and len(prior_s) >= 3:
            effect_sizes["steps_recent_vs_prior_90d"] = cohens_d(recent_s, prior_s)

        recent_rhr = [v for d, v in rhr_daily.items() if d >= cutoff]
        prior_rhr = [v for d, v in rhr_daily.items() if prior_start <= d < cutoff]
        if len(recent_rhr) >= 3 and len(prior_rhr) >= 3:
            effect_sizes["rhr_recent_vs_prior_90d"] = cohens_d(recent_rhr, prior_rhr)

        stat_rigor["effect_sizes"] = effect_sizes
        if effect_sizes:
            result["methods_applied"].append("Cohen's d / Hedge's g Effect Sizes")
            data_requirements["effect_sizes"]["met"] = True
        data_requirements["effect_sizes"]["actual"] = (
            f"recent steps: {len(recent_s)}, prior steps: {len(prior_s)}, "
            f"recent RHR: {len(recent_rhr)}, prior RHR: {len(prior_rhr)}"
        )

        result["statistical_rigor"] = stat_rigor
    except Exception as e:
        print(f"  ERROR in statistical rigor: {e}", file=sys.stderr)
        result["statistical_rigor"] = {"error": f"Statistical rigor computation failed: {e}"}

    # === BAYESIAN CHANGE POINTS ===
    print("  Bayesian change point detection...", file=sys.stderr)
    try:
        bcp = {}
        n_sorted_days = len(sorted_days)

        data_requirements["bayesian_changepoint_steps"] = {
            "required": ">=30 days of step data",
            "met": n_sorted_days >= 30,
            "actual": f"{n_sorted_days} days of step data",
        }
        data_requirements["bayesian_changepoint_rhr"] = {
            "required": ">=20 resting HR observations",
            "met": len(rhr_sorted) >= 20,
            "actual": f"{len(rhr_sorted)} resting HR observations",
        }

        # Steps (weekly)
        if n_sorted_days >= 30:
            weekly_step_vals = []
            week_labels = []
            for i in range(0, n_sorted_days, 7):
                chunk = sorted_days[i:i+7]
                weekly_step_vals.append(statistics.mean([d_steps[d] for d in chunk]))
                week_labels.append(chunk[0])
            bc = bayesian_changepoint(weekly_step_vals, hazard_rate=1/20)
            if bc:
                for cp in bc.get("changepoints", []):
                    idx = cp["index"]
                    if idx < len(week_labels):
                        cp["date"] = week_labels[idx]
                bcp["steps_weekly"] = bc
                result["methods_applied"].append("Bayesian Online Change Point Detection")

        if len(rhr_sorted) >= 20:
            rhr_vals_sorted = [v for _, v in rhr_sorted]
            rhr_labels = [d for d, _ in rhr_sorted]
            bc = bayesian_changepoint(rhr_vals_sorted, hazard_rate=1/30)
            if bc:
                for cp in bc.get("changepoints", []):
                    idx = cp["index"]
                    if idx < len(rhr_labels):
                        cp["date"] = rhr_labels[idx]
                bcp["resting_hr"] = bc

        result["bayesian_changepoints"] = bcp
    except Exception as e:
        print(f"  ERROR in Bayesian change points: {e}", file=sys.stderr)
        result["bayesian_changepoints"] = {"error": f"Bayesian change point computation failed: {e}"}

    # === BIOLOGICAL AGE ===
    print("  Biological & fitness age...", file=sys.stderr)
    try:
        bio = {}
        vo2_avg = statistics.mean([v for _, v in vo2_ts]) if vo2_ts else None
        rhr_avg = statistics.mean(list(rhr_daily.values())) if rhr_daily else None
        hrv_avg = statistics.mean(hrv_vals) if hrv_vals else None
        bmi = None
        if weight_ts and height_m:
            bmi = weight_ts[-1][1] / (height_m ** 2)
        recent_steps_list = [v for d, v in d_steps.items() if d >= (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")]
        recent_steps_avg = statistics.mean(recent_steps_list) if recent_steps_list else None
        sleep_avg = statistics.mean(list(night_sleep.values())) if night_sleep else None

        data_requirements["fitness_age"] = {
            "required": "VO2 Max data and age (from DOB)",
            "met": vo2_avg is not None and age is not None,
            "actual": f"VO2 Max: {'present' if vo2_avg is not None else 'absent'}, age: {'present' if age is not None else 'absent'}",
        }
        data_requirements["biological_age"] = {
            "required": "Age (from DOB) and at least one biomarker (RHR, HRV, VO2, BMI, steps, sleep)",
            "met": age is not None and any(v is not None for v in [rhr_avg, hrv_avg, vo2_avg, bmi, recent_steps_avg, sleep_avg]),
            "actual": (
                f"age: {'present' if age is not None else 'absent'}, "
                f"RHR: {'yes' if rhr_avg is not None else 'no'}, "
                f"HRV: {'yes' if hrv_avg is not None else 'no'}, "
                f"VO2: {'yes' if vo2_avg is not None else 'no'}, "
                f"BMI: {'yes' if bmi is not None else 'no'}, "
                f"steps: {'yes' if recent_steps_avg is not None else 'no'}, "
                f"sleep: {'yes' if sleep_avg is not None else 'no'}"
            ),
        }
        data_requirements["allostatic_load"] = {
            "required": "At least one biomarker (RHR, HRV, BMI, steps, sleep, VO2, glucose CV)",
            "met": any(v is not None for v in [rhr_avg, hrv_avg, bmi, recent_steps_avg, sleep_avg, vo2_avg]),
            "actual": f"{sum(1 for v in [rhr_avg, hrv_avg, bmi, recent_steps_avg, sleep_avg, vo2_avg] if v is not None)} of 6 base biomarkers available",
        }

        fa = fitness_age(vo2_avg, age, sex)
        if fa:
            bio["fitness_age"] = fa
            result["methods_applied"].append("Fitness Age (Nes et al. 2013)")

        ba = biological_age_estimate(age, rhr_avg, hrv_avg, vo2_avg, bmi, recent_steps_avg, sleep_avg, sex)
        if ba:
            bio["biological_age"] = ba
            result["methods_applied"].append("Biological Age Estimation")

        # Allostatic Load
        glucose_cv = None
        if glucose_ts:
            gvals_al = [v for _, v in glucose_ts]
            if len(gvals_al) >= 2:
                g_mean = statistics.mean(gvals_al)
                g_sd = statistics.stdev(gvals_al)
                glucose_cv = g_sd / g_mean * 100 if g_mean > 0 else None

        al = allostatic_load(rhr_avg, hrv_avg, bmi, recent_steps_avg, sleep_avg, vo2_avg, glucose_cv, age, sex)
        if al:
            bio["allostatic_load"] = al
            result["methods_applied"].append("Allostatic Load Index")

        result["biological_age_models"] = bio
    except Exception as e:
        print(f"  ERROR in biological age models: {e}", file=sys.stderr)
        result["biological_age_models"] = {"error": f"Biological age computation failed: {e}"}

    # === DISEASE RISK SCREENING ===
    print("  Disease risk screening...", file=sys.stderr)
    try:
        # Compute aggregated values for new screening parameters
        avg_walking_speed = statistics.mean([v for _, v in walking_speed_ts]) if walking_speed_ts else None
        avg_stair_speed = statistics.mean([v for _, v in stair_speed_ts]) if stair_speed_ts else None
        avg_wrist_temp = statistics.mean([v for _, v in wrist_temp_ts]) if wrist_temp_ts else None
        avg_headphone_db = statistics.mean([v for _, v in headphone_audio_ts]) if headphone_audio_ts else None
        avg_resp_rate = statistics.mean([v for _, v in resp_rate_ts]) if resp_rate_ts else None

        # Walking steadiness: use most recent classification
        # Apple reports as 0-1 value; map to categories
        ws_classification = None
        if walking_steadiness_ts:
            ws_val = walking_steadiness_ts[-1][1]
            if ws_val < 0.25:
                ws_classification = "Very Low"
            elif ws_val < 0.50:
                ws_classification = "Low"
            else:
                ws_classification = "OK"

        def _compute_weight_trend(wts):
            """Compute actual weight trend in kg/year from weight time series."""
            if not wts or len(wts) < 3:
                return None
            first_dt = wts[0][0]
            x_days = [(dt - first_dt).days for dt, _ in wts]
            y_w = [w for _, w in wts]
            n_w = len(x_days)
            mx_w = sum(x_days) / n_w
            my_w = sum(y_w) / n_w
            ssxy = sum((a - mx_w) * (b - my_w) for a, b in zip(x_days, y_w))
            ssxx = sum((a - mx_w) ** 2 for a in x_days)
            if ssxx == 0:
                return None
            slope = ssxy / ssxx
            return round(slope * 365.25, 2)

        # Daylight: compute daily average in minutes
        avg_daylight_min = None
        if daylight_ts:
            d_daylight = defaultdict(float)
            for dt_dl, v in daylight_ts:
                d_daylight[dt_dl.strftime("%Y-%m-%d")] += v
            if d_daylight:
                avg_daylight_min = statistics.mean(list(d_daylight.values()))

        # Sleep efficiency and stage percentages from sleep records
        sleep_eff_val = None
        sleep_deep_pct_val = None
        sleep_rem_pct_val = None
        if sleep_records:
            total_in_bed = 0
            total_asleep = 0
            total_deep = 0
            total_rem = 0
            for s_start, s_end, s_cat in sleep_records:
                dur_s = (s_end - s_start).total_seconds()
                if dur_s <= 0 or dur_s > 50400:  # skip >14h
                    continue
                if "InBed" in s_cat:
                    total_in_bed += dur_s
                elif "Awake" in s_cat:
                    total_in_bed += dur_s  # awake in bed counts as in-bed time
                else:
                    total_asleep += dur_s
                    total_in_bed += dur_s
                    if "Deep" in s_cat:
                        total_deep += dur_s
                    elif "REM" in s_cat:
                        total_rem += dur_s
            if total_in_bed > 0:
                sleep_eff_val = total_asleep / total_in_bed * 100
            if total_asleep > 0:
                sleep_deep_pct_val = total_deep / total_asleep * 100
                sleep_rem_pct_val = total_rem / total_asleep * 100

        risk_screening = disease_risk_screening(
            age=age, sex=sex, bmi=bmi,
            rhr=rhr_avg, hrv_sdnn=hrv_avg, vo2max=vo2_avg,
            steps_per_day=recent_steps_avg, sleep_hours=sleep_avg,
            glucose_ts=glucose_ts if glucose_ts else [],
            spo2_ts=spo2_ts if spo2_ts else [],
            hr_ts=hr_ts if hr_ts else [],
            dfa_alpha=result.get("nonlinear_dynamics", {}).get("hr_dfa", {}).get("alpha") if isinstance(result.get("nonlinear_dynamics", {}).get("hr_dfa"), dict) else None,
            is_val=result.get("circadian_quantification", {}).get("hr_rhythm_stability", {}).get("interdaily_stability") if isinstance(result.get("circadian_quantification", {}).get("hr_rhythm_stability"), dict) else None,
            iv_val=result.get("circadian_quantification", {}).get("hr_rhythm_stability", {}).get("intradaily_variability") if isinstance(result.get("circadian_quantification", {}).get("hr_rhythm_stability"), dict) else None,
            day_night_ratio=None,  # computed inside
            weight_trend_kg_yr=_compute_weight_trend(weight_ts),
            walking_speed=avg_walking_speed,
            stair_speed=avg_stair_speed,
            walking_steadiness=ws_classification,
            wrist_temp=avg_wrist_temp,
            daylight_minutes=avg_daylight_min,
            headphone_audio_db=avg_headphone_db,
            resp_rate=avg_resp_rate,
            sleep_efficiency=sleep_eff_val,
            sleep_deep_pct=sleep_deep_pct_val,
            sleep_rem_pct=sleep_rem_pct_val,
        )
        if risk_screening:
            result["disease_risk_screening"] = risk_screening
            result["methods_applied"].append("Multi-condition Disease Risk Screening")
    except Exception as e:
        print(f"  ERROR in disease risk screening: {e}", file=sys.stderr)
        result["disease_risk_screening"] = {"error": str(e)}

    # Deduplicate methods
    result["methods_applied"] = list(dict.fromkeys(result["methods_applied"]))

    # Add data_requirements to output
    result["data_requirements"] = data_requirements

    print(f"  Advanced analysis complete. {len(result['methods_applied'])} methods applied.", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
