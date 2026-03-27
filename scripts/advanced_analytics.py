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
               weight_ts, bf_ts, vo2_ts, height_ts]:
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

        # Poincare on HRV (use raw HRV measurements as RR-interval proxies)
        if n_hrv >= 20:
            poincare = poincare_plot(hrv_vals)
            if poincare:
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

    # Deduplicate methods
    result["methods_applied"] = list(dict.fromkeys(result["methods_applied"]))

    # Add data_requirements to output
    result["data_requirements"] = data_requirements

    print(f"  Advanced analysis complete. {len(result['methods_applied'])} methods applied.", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
