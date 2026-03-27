#!/usr/bin/env python3
"""
Apple Health Export — Comprehensive Analysis Engine

Parses an Apple Health XML export and produces structured JSON covering:
  - Personal info & data overview
  - Circadian rhythm profiling (HR, glucose)
  - Heart rate zones & autonomic indicators
  - Advanced CGM glucose metrics (MAGE, MODD, GRI, GMI, TIR)
  - Sleep architecture & efficiency
  - Activity & step analysis
  - Body composition trajectory & projection
  - Workout effectiveness & HR recovery
  - Cross-metric correlation matrix
  - Lagged cross-correlations
  - CUSUM change-point detection
  - Composite health scoring
  - Trend momentum analysis
  - Audio exposure risk
  - Risk stratification

Usage:
    python3 analyze_health.py <path-to-export.xml> [--output json|text]

Requires: Python 3.6+, no external dependencies.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import statistics
import json
import sys
import os
import math
import argparse
import glob as glob_mod

# ============================================================================
# Utilities
# ============================================================================

def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S %z")
    except Exception:
        return None

def pct(data, p):
    if not data:
        return 0
    s = sorted(data)
    k = (len(s) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (k - f) * (s[c] - s[f])

def safe_mean(vals):
    return statistics.mean(vals) if vals else None

def safe_median(vals):
    return statistics.median(vals) if vals else None

def safe_stdev(vals):
    return statistics.stdev(vals) if len(vals) >= 2 else None

def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x)/n, sum(y)/n
    num = sum((a-mx)*(b-my) for a,b in zip(x,y))
    den = (sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y)) ** 0.5
    return round(num/den, 4) if den else None

def linear_reg(x, y):
    n = len(x)
    if n < 3:
        return {"slope": 0, "intercept": 0, "r_squared": 0}
    mx, my = sum(x)/n, sum(y)/n
    ssxy = sum((a-mx)*(b-my) for a,b in zip(x,y))
    ssxx = sum((a-mx)**2 for a in x)
    ssyy = sum((b-my)**2 for b in y)
    if ssxx == 0 or ssyy == 0:
        return {"slope": 0, "intercept": 0, "r_squared": 0}
    slope = ssxy / ssxx
    return {
        "slope": round(slope, 6),
        "intercept": round(my - slope * mx, 4),
        "r_squared": round((ssxy**2) / (ssxx * ssyy), 4)
    }

def cusum_changes(values, threshold_factor=2.0):
    if len(values) < 10:
        return []
    mean_val = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) >= 2 else 1
    threshold = sd * threshold_factor
    s_pos, s_neg = [0], [0]
    for v in values:
        s_pos.append(max(0, s_pos[-1] + (v - mean_val) - threshold/4))
        s_neg.append(min(0, s_neg[-1] + (v - mean_val) + threshold/4))
    changes = []
    for i in range(1, len(s_pos)):
        if s_pos[i] > threshold and s_pos[i-1] <= threshold:
            changes.append(("up", i))
        if s_neg[i] < -threshold and s_neg[i-1] >= -threshold:
            changes.append(("down", i))
    return changes

def daily_sum(segments):
    d = defaultdict(float)
    for dt, val in segments:
        d[dt.strftime("%Y-%m-%d")] += val
    return dict(d)

def daily_mean(ts):
    d = defaultdict(list)
    for dt, val in ts:
        d[dt.strftime("%Y-%m-%d")].append(val)
    return {k: round(statistics.mean(v), 2) for k, v in d.items()}

def monthly_agg(daily_dict, last_n=12):
    m = defaultdict(list)
    for day, val in daily_dict.items():
        m[day[:7]].append(val)
    result = {}
    for month in sorted(m.keys())[-last_n:]:
        vals = m[month]
        result[month] = {
            "mean": round(statistics.mean(vals), 2),
            "n": len(vals)
        }
    return result

def stat_block(vals, label=""):
    if not vals:
        return None
    result = {
        "count": len(vals),
        "mean": round(statistics.mean(vals), 2),
        "median": round(statistics.median(vals), 2),
        "min": round(min(vals), 2),
        "max": round(max(vals), 2),
    }
    if len(vals) >= 2:
        result["stdev"] = round(statistics.stdev(vals), 2)
        result["p5"] = round(pct(vals, 5), 2)
        result["p10"] = round(pct(vals, 10), 2)
        result["p25"] = round(pct(vals, 25), 2)
        result["p75"] = round(pct(vals, 75), 2)
        result["p90"] = round(pct(vals, 90), 2)
        result["p95"] = round(pct(vals, 95), 2)
    return result

def period_avg(daily_dict, start, end):
    vals = [v for d, v in daily_dict.items() if start <= d <= end]
    return round(statistics.mean(vals), 2) if vals else None

# ============================================================================
# Auto-detect XML path
# ============================================================================

def find_xml(hint=None):
    if hint and os.path.isfile(hint):
        return hint
    # Search common patterns
    patterns = [
        "apple_health_export/导出.xml",
        "apple_health_export/export.xml",
        "apple_health_export/Export.xml",
        "*/apple_health_export/导出.xml",
        "*/apple_health_export/export.xml",
    ]
    for p in patterns:
        matches = glob_mod.glob(p)
        if matches:
            return matches[0]
    # Fallback: largest XML in any apple_health_export dir
    xmls = glob_mod.glob("**/apple_health_export/*.xml", recursive=True)
    if xmls:
        return max(xmls, key=os.path.getsize)
    return None

# ============================================================================
# Main Analysis
# ============================================================================

def analyze(xml_path):
    result = {}

    # ------------------------------------------------------------------
    # Phase 1: Parse
    # ------------------------------------------------------------------
    hr_ts = []
    rhr_daily = {}
    glucose_ts = []
    steps_seg = []
    active_cal_seg = []
    basal_cal_seg = []
    hrv_ts = []
    spo2_ts = []
    resp_ts = []
    wrist_temp_ts = []
    weight_ts = []
    bf_ts = []
    lbm_ts = []
    vo2_ts = []
    walking_hr_ts = []
    headphone_ts = []
    env_audio_ts = []
    physical_effort_ts = []
    flights_seg = []
    stand_time_seg = []
    walking_speed_ts = []
    sleep_records = []

    record_types = Counter()
    workouts = []
    activity_summaries = []
    me_info = {}

    height_ts = []  # (datetime, meters)

    TYPE_MAP = {
        "HKQuantityTypeIdentifierHeartRate": hr_ts,
        "HKQuantityTypeIdentifierBloodGlucose": glucose_ts,
        "HKQuantityTypeIdentifierStepCount": steps_seg,
        "HKQuantityTypeIdentifierActiveEnergyBurned": active_cal_seg,
        "HKQuantityTypeIdentifierBasalEnergyBurned": basal_cal_seg,
        "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": hrv_ts,
        "HKQuantityTypeIdentifierOxygenSaturation": spo2_ts,
        "HKQuantityTypeIdentifierRespiratoryRate": resp_ts,
        "HKQuantityTypeIdentifierAppleSleepingWristTemperature": wrist_temp_ts,
        "HKQuantityTypeIdentifierBodyMass": weight_ts,
        "HKQuantityTypeIdentifierBodyFatPercentage": bf_ts,
        "HKQuantityTypeIdentifierLeanBodyMass": lbm_ts,
        "HKQuantityTypeIdentifierVO2Max": vo2_ts,
        "HKQuantityTypeIdentifierWalkingHeartRateAverage": walking_hr_ts,
        "HKQuantityTypeIdentifierHeadphoneAudioExposure": headphone_ts,
        "HKQuantityTypeIdentifierEnvironmentalAudioExposure": env_audio_ts,
        "HKQuantityTypeIdentifierPhysicalEffort": physical_effort_ts,
        "HKQuantityTypeIdentifierFlightsClimbed": flights_seg,
        "HKQuantityTypeIdentifierAppleStandTime": stand_time_seg,
        "HKQuantityTypeIdentifierWalkingSpeed": walking_speed_ts,
        "HKQuantityTypeIdentifierHeight": height_ts,
    }
    RHR_KEY = "HKQuantityTypeIdentifierRestingHeartRate"
    SLEEP_KEY = "HKCategoryTypeIdentifierSleepAnalysis"

    print(f"Parsing {xml_path} ...", file=sys.stderr)
    ctx = ET.iterparse(xml_path, events=("end",))
    count = 0
    for _, elem in ctx:
        tag = elem.tag
        if tag == "Me":
            me_info = dict(elem.attrib)
        elif tag == "Record":
            rtype = elem.attrib.get("type", "")
            record_types[rtype] += 1
            value = elem.attrib.get("value")
            start = elem.attrib.get("startDate", "")
            dt = parse_date(start)

            if dt and value is not None:
                # Numeric records
                target = TYPE_MAP.get(rtype)
                if target is not None:
                    try:
                        val = float(value)
                        if rtype == "HKQuantityTypeIdentifierOxygenSaturation":
                            val *= 100  # fraction -> %
                        elif rtype == "HKQuantityTypeIdentifierBodyFatPercentage":
                            val *= 100
                        target.append((dt, val))
                    except ValueError:
                        pass
                elif rtype == RHR_KEY:
                    try:
                        rhr_daily[dt.strftime("%Y-%m-%d")] = float(value)
                    except ValueError:
                        pass

            # Sleep (categorical)
            if rtype == SLEEP_KEY and dt:
                end_dt = parse_date(elem.attrib.get("endDate", ""))
                cat = elem.attrib.get("value", "")
                if end_dt:
                    sleep_records.append((dt, end_dt, cat))

        elif tag == "Workout":
            workouts.append(dict(elem.attrib))
        elif tag == "ActivitySummary":
            activity_summaries.append(dict(elem.attrib))

        elem.clear()
        count += 1
        if count % 500000 == 0:
            print(f"  {count:,} elements...", file=sys.stderr)

    print(f"  Done: {count:,} elements.", file=sys.stderr)

    # Sort
    for ts in [hr_ts, glucose_ts, steps_seg, active_cal_seg, basal_cal_seg,
               hrv_ts, spo2_ts, resp_ts, wrist_temp_ts, weight_ts, bf_ts,
               lbm_ts, vo2_ts, walking_hr_ts, headphone_ts, env_audio_ts,
               physical_effort_ts, flights_seg, stand_time_seg, walking_speed_ts]:
        ts.sort(key=lambda x: x[0])
    sleep_records.sort(key=lambda x: x[0])

    # Daily aggregations
    d_steps = daily_sum(steps_seg)
    d_active_cal = daily_sum(active_cal_seg)
    d_hr = daily_mean(hr_ts)
    d_hrv = daily_mean(hrv_ts)

    # ------------------------------------------------------------------
    # Personal Info
    # ------------------------------------------------------------------
    dob_str = me_info.get("HKCharacteristicTypeIdentifierDateOfBirth", "")
    sex_raw = me_info.get("HKCharacteristicTypeIdentifierBiologicalSex", "")
    sex_map = {"HKBiologicalSexMale": "Male", "HKBiologicalSexFemale": "Female"}
    age = None
    if dob_str:
        try:
            age = round((datetime.now() - datetime.strptime(dob_str, "%Y-%m-%d")).days / 365.25, 1)
        except Exception:
            pass

    # Height: use most recent measurement, convert cm to m
    height_m = None
    if height_ts:
        # Apple Health stores height in cm (or m depending on locale)
        last_h = height_ts[-1][1]
        height_m = last_h / 100 if last_h > 3 else last_h  # >3 means cm, else already m

    result["personal_info"] = {
        "date_of_birth": dob_str or None,
        "sex": sex_map.get(sex_raw, sex_raw or None),
        "age": age,
        "height_m": round(height_m, 4) if height_m else None,
    }

    # ------------------------------------------------------------------
    # Data Overview
    # ------------------------------------------------------------------
    type_summary = {}
    for rtype, cnt in record_types.most_common():
        short = rtype.replace("HKQuantityTypeIdentifier", "").replace("HKCategoryTypeIdentifier", "Cat:")
        type_summary[short] = cnt

    result["data_overview"] = {
        "total_records": sum(record_types.values()),
        "total_record_types": len(record_types),
        "total_workouts": len(workouts),
        "total_activity_days": len(activity_summaries),
        "record_types": type_summary,
        "data_sources": dict(Counter(
            elem_src for ts in [hr_ts, glucose_ts, steps_seg] for elem_src in []
        )),  # Sources would need separate collection; omit for now
    }

    # ------------------------------------------------------------------
    # Data Quality
    # ------------------------------------------------------------------
    def _compute_data_quality():
        """Assess completeness and reliability of each data stream."""

        # Determine overall date range from all timestamped data
        all_dates = []
        for ts in [hr_ts, glucose_ts, steps_seg, active_cal_seg, basal_cal_seg,
                    hrv_ts, spo2_ts, resp_ts, wrist_temp_ts, weight_ts, bf_ts,
                    lbm_ts, vo2_ts, walking_hr_ts, headphone_ts, env_audio_ts,
                    physical_effort_ts, flights_seg, stand_time_seg, walking_speed_ts]:
            if ts:
                all_dates.append(ts[0][0])
                all_dates.append(ts[-1][0])
        if sleep_records:
            all_dates.append(sleep_records[0][0])
            all_dates.append(sleep_records[-1][0])
        # rhr_daily uses date strings — skip; we have enough date anchors from time-series data
        for w in workouts:
            wd = parse_date(w.get("startDate", ""))
            if wd:
                all_dates.append(wd)

        if not all_dates:
            return {
                "streams": {},
                "data_sufficiency": {},
                "warnings": ["No timestamped data found in the export."],
            }

        global_first = min(all_dates).replace(tzinfo=None)
        global_last = max(all_dates).replace(tzinfo=None)
        total_days_range = max((global_last - global_first).days, 1)

        def _stream_quality(name, ts_data, daily_dict=None):
            """Compute quality metrics for a single data stream.

            ts_data: list of (datetime, value) tuples, OR None
            daily_dict: optional pre-computed {date_str: value} dict (e.g. rhr_daily)
            """
            # Handle the case where we use a daily dict instead of raw ts
            if daily_dict is not None:
                n_total = len(daily_dict)
                if n_total == 0:
                    return {
                        "total_readings": 0,
                        "completeness_pct": 0.0,
                        "data_span": None,
                        "avg_readings_per_day": 0.0,
                        "longest_gap_days": None,
                        "reliability_grade": "insufficient",
                    }
                sorted_days = sorted(daily_dict.keys())
                first_date = sorted_days[0]
                last_date = sorted_days[-1]
                try:
                    fd = datetime.strptime(first_date, "%Y-%m-%d")
                    ld = datetime.strptime(last_date, "%Y-%m-%d")
                    span_days = max((ld - fd).days, 1)
                except Exception:
                    span_days = 1
                days_with_data = len(sorted_days)
                completeness = round(days_with_data / max(span_days, 1) * 100, 1)
                # Longest gap
                longest_gap = 0
                for i in range(1, len(sorted_days)):
                    try:
                        d1 = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
                        d2 = datetime.strptime(sorted_days[i], "%Y-%m-%d")
                        gap = (d2 - d1).days
                        if gap > longest_gap:
                            longest_gap = gap
                    except Exception:
                        pass
                avg_per_day = round(n_total / max(span_days, 1), 1)
                # Grade
                if n_total < 10:
                    grade = "insufficient"
                elif completeness > 80 and avg_per_day > 0.5:
                    grade = "high"
                elif completeness > 50:
                    grade = "moderate"
                else:
                    grade = "low"
                return {
                    "total_readings": n_total,
                    "completeness_pct": completeness,
                    "data_span": {"first": first_date, "last": last_date, "days": span_days},
                    "avg_readings_per_day": avg_per_day,
                    "longest_gap_days": longest_gap if longest_gap > 0 else None,
                    "reliability_grade": grade,
                }

            # ts_data path
            if not ts_data:
                return {
                    "total_readings": 0,
                    "completeness_pct": 0.0,
                    "data_span": None,
                    "avg_readings_per_day": 0.0,
                    "longest_gap_days": None,
                    "reliability_grade": "insufficient",
                }

            n_total = len(ts_data)
            first_dt = ts_data[0][0].replace(tzinfo=None)
            last_dt = ts_data[-1][0].replace(tzinfo=None)
            span_days = max((last_dt - first_dt).days, 1)

            # Days with at least one reading
            days_set = set()
            for dt, _ in ts_data:
                days_set.add(dt.strftime("%Y-%m-%d"))
            days_with_data = len(days_set)
            completeness = round(days_with_data / max(span_days, 1) * 100, 1)
            avg_per_day = round(n_total / max(span_days, 1), 1)

            # Longest gap
            sorted_days = sorted(days_set)
            longest_gap = 0
            for i in range(1, len(sorted_days)):
                try:
                    d1 = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
                    d2 = datetime.strptime(sorted_days[i], "%Y-%m-%d")
                    gap = (d2 - d1).days
                    if gap > longest_gap:
                        longest_gap = gap
                except Exception:
                    pass

            # Grade
            if n_total < 10:
                grade = "insufficient"
            elif completeness > 80 and avg_per_day > 5:
                grade = "high"
            elif completeness > 50:
                grade = "moderate"
            else:
                grade = "low"

            return {
                "total_readings": n_total,
                "completeness_pct": completeness,
                "data_span": {
                    "first": first_dt.strftime("%Y-%m-%d"),
                    "last": last_dt.strftime("%Y-%m-%d"),
                    "days": span_days,
                },
                "avg_readings_per_day": avg_per_day,
                "longest_gap_days": longest_gap if longest_gap > 0 else None,
                "reliability_grade": grade,
            }

        def _sleep_quality():
            """Compute quality for sleep records (different structure)."""
            if not sleep_records:
                return {
                    "total_readings": 0,
                    "completeness_pct": 0.0,
                    "data_span": None,
                    "avg_readings_per_day": 0.0,
                    "longest_gap_days": None,
                    "reliability_grade": "insufficient",
                }
            n_total = len(sleep_records)
            first_dt = sleep_records[0][0].replace(tzinfo=None)
            last_dt = sleep_records[-1][0].replace(tzinfo=None)
            span_days = max((last_dt - first_dt).days, 1)
            days_set = set()
            for start_dt, end_dt, _ in sleep_records:
                days_set.add(start_dt.strftime("%Y-%m-%d"))
            days_with_data = len(days_set)
            completeness = round(days_with_data / max(span_days, 1) * 100, 1)
            avg_per_day = round(n_total / max(span_days, 1), 1)

            sorted_days = sorted(days_set)
            longest_gap = 0
            for i in range(1, len(sorted_days)):
                try:
                    d1 = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
                    d2 = datetime.strptime(sorted_days[i], "%Y-%m-%d")
                    gap = (d2 - d1).days
                    if gap > longest_gap:
                        longest_gap = gap
                except Exception:
                    pass

            if n_total < 10:
                grade = "insufficient"
            elif completeness > 80 and avg_per_day > 5:
                grade = "high"
            elif completeness > 50:
                grade = "moderate"
            else:
                grade = "low"

            return {
                "total_readings": n_total,
                "completeness_pct": completeness,
                "data_span": {
                    "first": first_dt.strftime("%Y-%m-%d"),
                    "last": last_dt.strftime("%Y-%m-%d"),
                    "days": span_days,
                },
                "avg_readings_per_day": avg_per_day,
                "longest_gap_days": longest_gap if longest_gap > 0 else None,
                "reliability_grade": grade,
            }

        def _workout_quality():
            """Compute quality for workouts (list of dicts)."""
            if not workouts:
                return {
                    "total_readings": 0,
                    "completeness_pct": 0.0,
                    "data_span": None,
                    "avg_readings_per_day": 0.0,
                    "longest_gap_days": None,
                    "reliability_grade": "insufficient",
                }
            w_dates = sorted([parse_date(w.get("startDate", "")) for w in workouts
                              if parse_date(w.get("startDate", ""))])
            if not w_dates:
                return {
                    "total_readings": len(workouts),
                    "completeness_pct": 0.0,
                    "data_span": None,
                    "avg_readings_per_day": 0.0,
                    "longest_gap_days": None,
                    "reliability_grade": "insufficient",
                }
            first_dt = w_dates[0].replace(tzinfo=None)
            last_dt = w_dates[-1].replace(tzinfo=None)
            span_days = max((last_dt - first_dt).days, 1)
            days_set = set(d.strftime("%Y-%m-%d") for d in w_dates)
            completeness = round(len(days_set) / max(span_days, 1) * 100, 1)
            avg_per_day = round(len(workouts) / max(span_days, 1), 1)

            sorted_days = sorted(days_set)
            longest_gap = 0
            for i in range(1, len(sorted_days)):
                try:
                    d1 = datetime.strptime(sorted_days[i - 1], "%Y-%m-%d")
                    d2 = datetime.strptime(sorted_days[i], "%Y-%m-%d")
                    gap = (d2 - d1).days
                    if gap > longest_gap:
                        longest_gap = gap
                except Exception:
                    pass

            n = len(workouts)
            if n < 10:
                grade = "insufficient"
            elif completeness > 80 and avg_per_day > 0.3:
                grade = "high"
            elif completeness > 50:
                grade = "moderate"
            else:
                grade = "low"

            return {
                "total_readings": n,
                "completeness_pct": completeness,
                "data_span": {
                    "first": first_dt.strftime("%Y-%m-%d"),
                    "last": last_dt.strftime("%Y-%m-%d"),
                    "days": span_days,
                },
                "avg_readings_per_day": avg_per_day,
                "longest_gap_days": longest_gap if longest_gap > 0 else None,
                "reliability_grade": grade,
            }

        # Build per-stream quality
        streams = {
            "heart_rate": _stream_quality("heart_rate", hr_ts),
            "resting_hr": _stream_quality("resting_hr", None, daily_dict=rhr_daily),
            "hrv": _stream_quality("hrv", hrv_ts),
            "glucose": _stream_quality("glucose", glucose_ts),
            "sleep": _sleep_quality(),
            "steps": _stream_quality("steps", steps_seg),
            "weight": _stream_quality("weight", weight_ts),
            "vo2max": _stream_quality("vo2max", vo2_ts),
            "spo2": _stream_quality("spo2", spo2_ts),
            "respiratory_rate": _stream_quality("respiratory_rate", resp_ts),
            "workouts": _workout_quality(),
        }

        # Data sufficiency for each analysis type
        def _is_sufficient(stream_name, min_readings=10, min_completeness=20):
            s = streams.get(stream_name, {})
            return (s.get("total_readings", 0) >= min_readings
                    and s.get("completeness_pct", 0) >= min_completeness)

        data_sufficiency = {
            "circadian_analysis": _is_sufficient("heart_rate", 100, 20),
            "heart_rate_zones": _is_sufficient("heart_rate", 50, 10),
            "hrv_analysis": _is_sufficient("hrv", 20, 10),
            "glucose_advanced": _is_sufficient("glucose", 100, 20),
            "sleep_architecture": _is_sufficient("sleep", 14, 10),
            "activity_analysis": _is_sufficient("steps", 30, 10),
            "body_composition_trend": (streams["weight"]["total_readings"] >= 5),
            "vo2max_trend": (streams["vo2max"]["total_readings"] >= 5),
            "workout_effectiveness": (streams["workouts"]["total_readings"] >= 5
                                      and streams["heart_rate"]["total_readings"] >= 50),
            "correlation_analysis": (
                _is_sufficient("heart_rate", 30, 10)
                and _is_sufficient("steps", 30, 10)
            ),
            "causal_inference": (
                _is_sufficient("heart_rate", 60, 20)
                and _is_sufficient("steps", 60, 20)
                and _is_sufficient("hrv", 30, 10)
            ),
            "change_point_detection": _is_sufficient("steps", 30, 20),
            "risk_stratification": any(
                streams[s]["total_readings"] >= 10
                for s in ["heart_rate", "steps", "weight", "glucose"]
            ),
        }

        # Warnings
        warnings = []
        for stream_name, sq in streams.items():
            total = sq.get("total_readings", 0)
            comp = sq.get("completeness_pct", 0)
            grade = sq.get("reliability_grade", "insufficient")
            gap = sq.get("longest_gap_days")

            if total == 0:
                continue  # No data at all -- not worth warning about

            if grade == "insufficient":
                warnings.append(
                    f"Only {total} {stream_name.replace('_', ' ')} readings "
                    f"-- trend analysis not meaningful."
                )
            elif grade == "low":
                analysis_map = {
                    "heart_rate": "circadian and heart rate zone analysis",
                    "resting_hr": "resting HR trend analysis",
                    "hrv": "HRV recovery analysis",
                    "glucose": "advanced glucose metrics (MAGE, MODD, GRI)",
                    "sleep": "sleep architecture analysis",
                    "steps": "activity trend analysis",
                    "weight": "body composition trajectory",
                    "vo2max": "VO2 Max trend analysis",
                    "spo2": "oxygen saturation analysis",
                    "respiratory_rate": "respiratory analysis",
                    "workouts": "workout effectiveness analysis",
                }
                detail = analysis_map.get(stream_name, f"{stream_name} analysis")
                warnings.append(
                    f"{stream_name.replace('_', ' ').title()} data has "
                    f"{comp:.0f}% coverage -- {detail} may be unreliable."
                )

            if gap is not None and gap > 30:
                warnings.append(
                    f"{stream_name.replace('_', ' ').title()} has a gap of "
                    f"{gap} days -- this may affect trend and change-point analysis."
                )

        return {
            "streams": streams,
            "total_date_range": {
                "first": global_first.strftime("%Y-%m-%d"),
                "last": global_last.strftime("%Y-%m-%d"),
                "total_days": total_days_range,
            },
            "data_sufficiency": data_sufficiency,
            "warnings": warnings,
        }

    result["data_quality"] = _compute_data_quality()

    # ------------------------------------------------------------------
    # Circadian Rhythm
    # ------------------------------------------------------------------
    hr_by_hour = defaultdict(list)
    for dt, v in hr_ts:
        hr_by_hour[dt.hour].append(v)

    hr_24h = {}
    for h in range(24):
        vals = hr_by_hour.get(h, [])
        if vals:
            hr_24h[f"{h:02d}"] = {
                "mean": round(statistics.mean(vals), 1),
                "median": round(statistics.median(vals), 1),
                "p10": round(pct(vals, 10), 1),
                "p90": round(pct(vals, 90), 1),
                "stdev": round(statistics.stdev(vals), 1) if len(vals) >= 2 else None,
                "n": len(vals),
            }

    nocturnal = [v for dt, v in hr_ts if 2 <= dt.hour <= 5]
    daytime = [v for dt, v in hr_ts if 10 <= dt.hour <= 16]

    nocturnal_monthly = defaultdict(list)
    for dt, v in hr_ts:
        if 2 <= dt.hour <= 5:
            nocturnal_monthly[dt.strftime("%Y-%m")].append(v)
    noct_trend = {}
    for m in sorted(nocturnal_monthly.keys())[-15:]:
        vals = nocturnal_monthly[m]
        noct_trend[m] = {"mean": round(statistics.mean(vals), 1),
                         "stdev": round(statistics.stdev(vals), 1) if len(vals) >= 2 else None,
                         "n": len(vals)}

    glucose_24h = {}
    if glucose_ts:
        g_by_hour = defaultdict(list)
        for dt, v in glucose_ts:
            g_by_hour[dt.hour].append(v)
        for h in range(24):
            vals = g_by_hour.get(h, [])
            if vals:
                glucose_24h[f"{h:02d}"] = {
                    "mean": round(statistics.mean(vals), 1),
                    "p25": round(pct(vals, 25), 1),
                    "p75": round(pct(vals, 75), 1),
                    "p95": round(pct(vals, 95), 1),
                    "cv_pct": round(statistics.stdev(vals) / statistics.mean(vals) * 100, 1) if len(vals) >= 2 else None,
                    "n": len(vals),
                }

    result["circadian_rhythm"] = {
        "heart_rate_24h": hr_24h,
        "nocturnal_hr": stat_block(nocturnal) if nocturnal else None,
        "daytime_hr": stat_block(daytime) if daytime else None,
        "day_night_difference": round(safe_mean(daytime) - safe_mean(nocturnal), 1) if nocturnal and daytime else None,
        "day_night_ratio": round(safe_mean(daytime) / safe_mean(nocturnal), 3) if nocturnal and daytime and safe_mean(nocturnal) else None,
        "dipping_pattern": ("normal" if (safe_mean(daytime) - safe_mean(nocturnal)) > 15 else "reduced") if nocturnal and daytime else None,
        "nocturnal_hr_monthly_trend": noct_trend,
        "glucose_24h": glucose_24h,
    }

    # ------------------------------------------------------------------
    # Heart Rate
    # ------------------------------------------------------------------
    all_hr = [v for _, v in hr_ts]
    max_hr_est = round(208 - 0.7 * age) if age else 191

    zones_def = [
        ("below_zone1", 0, max_hr_est * 0.50),
        ("zone1_recovery_50_60", max_hr_est * 0.50, max_hr_est * 0.60),
        ("zone2_fatburn_60_70", max_hr_est * 0.60, max_hr_est * 0.70),
        ("zone3_aerobic_70_80", max_hr_est * 0.70, max_hr_est * 0.80),
        ("zone4_threshold_80_90", max_hr_est * 0.80, max_hr_est * 0.90),
        ("zone5_max_90_100", max_hr_est * 0.90, max_hr_est * 1.00),
        ("above_max", max_hr_est * 1.00, 999),
    ]

    zone_dist = {}
    total_hr = len(all_hr)
    for name, lo, hi in zones_def:
        cnt = sum(1 for v in all_hr if lo <= v < hi)
        zone_dist[name] = {"count": cnt, "pct": round(cnt / total_hr * 100, 1) if total_hr else 0}

    # Workout vs non-workout HR
    workout_periods = []
    for w in workouts:
        ws = parse_date(w.get("startDate", ""))
        we = parse_date(w.get("endDate", ""))
        if ws and we:
            workout_periods.append((ws, we))

    def in_workout(dt):
        for ws, we in workout_periods:
            if ws <= dt <= we:
                return True
        return False

    w_hr = [v for dt, v in hr_ts if in_workout(dt)]
    nw_hr = [v for dt, v in hr_ts if not in_workout(dt)]

    result["heart_rate"] = {
        "overall": stat_block(all_hr),
        "estimated_max_hr": max_hr_est,
        "zone_distribution": zone_dist,
        "during_workouts": stat_block(w_hr) if w_hr else None,
        "non_workout": stat_block(nw_hr) if nw_hr else None,
        "resting_hr": stat_block(list(rhr_daily.values())) if rhr_daily else None,
        "resting_hr_monthly": monthly_agg(rhr_daily),
        "walking_hr_avg": stat_block([v for _, v in walking_hr_ts]) if walking_hr_ts else None,
    }

    # ------------------------------------------------------------------
    # HRV
    # ------------------------------------------------------------------
    hrv_vals = [v for _, v in hrv_ts]
    hrv_monthly = defaultdict(list)
    for dt, v in hrv_ts:
        hrv_monthly[dt.strftime("%Y-%m")].append(v)

    result["heart_rate_variability"] = {
        "overall": stat_block(hrv_vals),
        "monthly": {m: {"mean": round(statistics.mean(v), 1), "n": len(v)}
                    for m, v in sorted(hrv_monthly.items())[-12:]},
    }

    # ------------------------------------------------------------------
    # Glucose (Advanced CGM Metrics)
    # ------------------------------------------------------------------
    glucose_result = None
    if glucose_ts:
        gvals = [v for _, v in glucose_ts]
        g_mean = statistics.mean(gvals)
        g_sd = statistics.stdev(gvals) if len(gvals) >= 2 else 0
        n_g = len(gvals)

        # TIR ranges
        tir = {
            "very_low_lt54": {"count": sum(1 for v in gvals if v < 54),
                              "pct": round(sum(1 for v in gvals if v < 54) / n_g * 100, 2)},
            "low_54_70": {"count": sum(1 for v in gvals if 54 <= v < 70),
                          "pct": round(sum(1 for v in gvals if 54 <= v < 70) / n_g * 100, 2)},
            "target_70_180": {"count": sum(1 for v in gvals if 70 <= v <= 180),
                              "pct": round(sum(1 for v in gvals if 70 <= v <= 180) / n_g * 100, 2)},
            "high_181_250": {"count": sum(1 for v in gvals if 180 < v <= 250),
                             "pct": round(sum(1 for v in gvals if 180 < v <= 250) / n_g * 100, 2)},
            "very_high_gt250": {"count": sum(1 for v in gvals if v > 250),
                                "pct": round(sum(1 for v in gvals if v > 250) / n_g * 100, 2)},
        }

        # MAGE
        excursions = []
        direction = None
        turning = [gvals[0]]
        for i in range(1, len(gvals)):
            if gvals[i] > gvals[i-1]:
                if direction == "down":
                    turning.append(gvals[i-1])
                direction = "up"
            elif gvals[i] < gvals[i-1]:
                if direction == "up":
                    turning.append(gvals[i-1])
                direction = "down"
        turning.append(gvals[-1])
        for i in range(1, len(turning)):
            exc = abs(turning[i] - turning[i-1])
            if exc > g_sd:
                excursions.append(exc)
        mage = round(statistics.mean(excursions), 1) if excursions else 0

        # MODD
        g_day_hour = defaultdict(lambda: defaultdict(list))
        for dt, v in glucose_ts:
            g_day_hour[dt.strftime("%Y-%m-%d")][dt.hour].append(v)
        days_sorted = sorted(g_day_hour.keys())
        modd_diffs = []
        for i in range(1, len(days_sorted)):
            d1, d2 = days_sorted[i-1], days_sorted[i]
            dt1 = datetime.strptime(d1, "%Y-%m-%d")
            dt2 = datetime.strptime(d2, "%Y-%m-%d")
            if (dt2 - dt1).days != 1:
                continue
            for h in range(24):
                if h in g_day_hour[d1] and h in g_day_hour[d2]:
                    modd_diffs.append(abs(statistics.mean(g_day_hour[d2][h]) - statistics.mean(g_day_hour[d1][h])))
        modd = round(statistics.mean(modd_diffs), 1) if modd_diffs else None

        # Other indices
        gmi = round(3.31 + 0.02392 * g_mean, 2)
        eA1c = round((g_mean + 46.7) / 28.7, 2)
        cv = round(g_sd / g_mean * 100, 1) if g_mean else 0
        g_iqr = round(pct(gvals, 75) - pct(gvals, 25), 1)
        j_index = round(0.001 * (g_mean + g_sd) ** 2, 1)
        vlow_pct = sum(1 for v in gvals if v < 54) / n_g * 100
        low_pct = sum(1 for v in gvals if 54 <= v < 70) / n_g * 100
        vhigh_pct = sum(1 for v in gvals if v > 250) / n_g * 100
        high_pct = sum(1 for v in gvals if 180 < v <= 250) / n_g * 100
        gri = round((3.0 * vlow_pct + 2.4 * low_pct) + (1.6 * vhigh_pct + 0.8 * high_pct), 1)

        # Weekly pattern
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        g_weekly = {}
        g_wd = defaultdict(list)
        for dt, v in glucose_ts:
            g_wd[dt.weekday()].append(v)
        for wd in range(7):
            if wd in g_wd:
                vals = g_wd[wd]
                g_weekly[weekday_names[wd]] = {
                    "mean": round(statistics.mean(vals), 1),
                    "sd": round(statistics.stdev(vals), 1) if len(vals) >= 2 else None,
                    "tir_pct": round(sum(1 for v in vals if 70 <= v <= 180) / len(vals) * 100, 1),
                    "above_180_pct": round(sum(1 for v in vals if v > 180) / len(vals) * 100, 1),
                }

        # Daily summaries
        g_daily = defaultdict(list)
        for dt, v in glucose_ts:
            g_daily[dt.strftime("%Y-%m-%d")].append(v)
        daily_summaries = []
        for day in sorted(g_daily.keys()):
            vals = g_daily[day]
            if len(vals) >= 10:
                daily_summaries.append({
                    "date": day,
                    "mean": round(statistics.mean(vals), 1),
                    "sd": round(statistics.stdev(vals), 1),
                    "min": round(min(vals), 1),
                    "max": round(max(vals), 1),
                    "range": round(max(vals) - min(vals), 1),
                    "tir_pct": round(sum(1 for v in vals if 70 <= v <= 180) / len(vals) * 100, 1),
                    "cv_pct": round(statistics.stdev(vals) / statistics.mean(vals) * 100, 1),
                    "n": len(vals),
                })

        # Glucose response to workouts
        glucose_workout_response = []
        for w in workouts:
            ws = parse_date(w.get("startDate", ""))
            we = parse_date(w.get("endDate", ""))
            wtype = w.get("workoutActivityType", "").replace("HKWorkoutActivityType", "")
            if ws and we:
                pre = [v for dt, v in glucose_ts if ws - timedelta(hours=1) <= dt < ws]
                during = [v for dt, v in glucose_ts if ws <= dt <= we]
                post = [v for dt, v in glucose_ts if we < dt <= we + timedelta(hours=1)]
                if pre or during or post:
                    glucose_workout_response.append({
                        "date": ws.strftime("%Y-%m-%d %H:%M"),
                        "type": wtype,
                        "pre_mean": round(statistics.mean(pre), 1) if pre else None,
                        "during_mean": round(statistics.mean(during), 1) if during else None,
                        "post_mean": round(statistics.mean(post), 1) if post else None,
                    })

        glucose_result = {
            "overall": stat_block(gvals),
            "gmi": gmi,
            "eA1c": eA1c,
            "cv_pct": cv,
            "cv_stability": "stable" if cv < 36 else "unstable",
            "mage": mage,
            "modd": modd,
            "iqr": g_iqr,
            "j_index": j_index,
            "gri": gri,
            "time_in_range": tir,
            "weekly_pattern": g_weekly,
            "daily_summaries": daily_summaries[-30:],  # Last 30 days
            "workout_response": glucose_workout_response,
        }

    result["glucose"] = glucose_result

    # ------------------------------------------------------------------
    # Sleep
    # ------------------------------------------------------------------
    night_sleep = defaultdict(lambda: defaultdict(float))
    for start_dt, end_dt, cat in sleep_records:
        dur_h = (end_dt - start_dt).total_seconds() / 3600
        if dur_h <= 0 or dur_h > 14:
            continue
        night_key = start_dt.strftime("%Y-%m-%d") if start_dt.hour >= 18 else \
                    (start_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        short_cat = cat.replace("HKCategoryValueSleepAnalysis", "")
        night_sleep[night_key][short_cat] += dur_h

    nights = []
    for night, cats in sorted(night_sleep.items()):
        total = sum(v for k, v in cats.items() if k not in ("Awake", "InBed"))
        if total < 1 or total > 14:
            continue
        deep = cats.get("AsleepDeep", 0)
        rem = cats.get("AsleepREM", 0)
        core = cats.get("AsleepCore", 0)
        awake = cats.get("Awake", 0)
        bed = sum(cats.values())
        eff = round(total / bed * 100, 1) if bed else 0
        nights.append({
            "night": night,
            "total_h": round(total, 2),
            "deep_h": round(deep, 2),
            "rem_h": round(rem, 2),
            "core_h": round(core, 2),
            "awake_h": round(awake, 2),
            "efficiency_pct": eff,
            "deep_pct": round(deep / total * 100, 1) if total else 0,
            "rem_pct": round(rem / total * 100, 1) if total else 0,
        })

    sleep_monthly = defaultdict(lambda: {"total": [], "deep": [], "rem": [], "eff": []})
    for n in nights:
        m = n["night"][:7]
        sleep_monthly[m]["total"].append(n["total_h"])
        if n["deep_h"] > 0:
            sleep_monthly[m]["deep"].append(n["deep_h"])
        if n["rem_h"] > 0:
            sleep_monthly[m]["rem"].append(n["rem_h"])
        if n["efficiency_pct"] > 0:
            sleep_monthly[m]["eff"].append(n["efficiency_pct"])

    sleep_trend = {}
    for m in sorted(sleep_monthly.keys())[-12:]:
        s = sleep_monthly[m]
        sleep_trend[m] = {
            "total_h": round(safe_mean(s["total"]), 2) if s["total"] else None,
            "deep_h": round(safe_mean(s["deep"]), 2) if s["deep"] else None,
            "rem_h": round(safe_mean(s["rem"]), 2) if s["rem"] else None,
            "efficiency_pct": round(safe_mean(s["eff"]), 1) if s["eff"] else None,
            "n": len(s["total"]),
        }

    result["sleep"] = {
        "total_nights": len(nights),
        "duration_stats": stat_block([n["total_h"] for n in nights]) if nights else None,
        "deep_stats": stat_block([n["deep_h"] for n in nights if n["deep_h"] > 0]) or None,
        "rem_stats": stat_block([n["rem_h"] for n in nights if n["rem_h"] > 0]) or None,
        "core_stats": stat_block([n["core_h"] for n in nights if n["core_h"] > 0]) or None,
        "efficiency_stats": stat_block([n["efficiency_pct"] for n in nights if n["efficiency_pct"] > 0]) or None,
        "recent_nights": nights[-30:],
        "monthly_trend": sleep_trend,
    }

    # ------------------------------------------------------------------
    # Activity
    # ------------------------------------------------------------------
    step_vals = list(d_steps.values())
    weekly_steps = defaultdict(list)
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d, s in d_steps.items():
        dt = datetime.strptime(d, "%Y-%m-%d")
        weekly_steps[dt.weekday()].append(s)

    steps_weekly = {}
    for wd in range(7):
        if wd in weekly_steps:
            steps_weekly[weekday_names[wd]] = {
                "mean": round(statistics.mean(weekly_steps[wd]), 0),
                "n": len(weekly_steps[wd])
            }

    result["activity"] = {
        "daily_steps": {
            "stats": stat_block(step_vals) if step_vals else None,
            "days_over_10k": sum(1 for v in step_vals if v >= 10000),
            "days_over_10k_pct": round(sum(1 for v in step_vals if v >= 10000) / len(step_vals) * 100, 1) if step_vals else 0,
            "days_under_3k": sum(1 for v in step_vals if v < 3000),
            "days_under_5k": sum(1 for v in step_vals if v < 5000),
            "monthly": monthly_agg(d_steps),
            "weekly_pattern": steps_weekly,
        },
        "active_calories": {
            "daily_stats": stat_block(list(d_active_cal.values())) if d_active_cal else None,
            "monthly": monthly_agg(d_active_cal),
        },
        "activity_summaries": {
            "days_tracked": len(activity_summaries),
            "move_cal": stat_block([float(a["activeEnergyBurned"]) for a in activity_summaries if "activeEnergyBurned" in a]) if activity_summaries else None,
            "exercise_min": stat_block([float(a["appleExerciseTime"]) for a in activity_summaries if "appleExerciseTime" in a]) if activity_summaries else None,
            "stand_hours": stat_block([float(a["appleStandHours"]) for a in activity_summaries if "appleStandHours" in a]) if activity_summaries else None,
        },
    }

    # ------------------------------------------------------------------
    # Body Composition
    # ------------------------------------------------------------------
    bc = {}
    if weight_ts:
        first_dt = weight_ts[0][0]
        x_days = [(dt - first_dt).days for dt, _ in weight_ts]
        y_weight = [w for _, w in weight_ts]
        reg = linear_reg(x_days, y_weight)

        weight_history = [{"date": dt.strftime("%Y-%m-%d"), "kg": round(w, 1)} for dt, w in weight_ts]

        # Projection
        today_days = (datetime.now() - first_dt.replace(tzinfo=None)).days
        projections = {}
        for months in [3, 6, 12]:
            proj_d = today_days + months * 30
            proj_w = reg["intercept"] + reg["slope"] * proj_d
            projections[f"+{months}mo"] = {
                "weight_kg": round(proj_w, 1),
                "bmi": round(proj_w / (height_m ** 2), 1) if height_m else None
            }

        bc["weight"] = {
            "history": weight_history,
            "stats": stat_block(y_weight),
            "regression": {
                "kg_per_month": round(reg["slope"] * 30, 2),
                "kg_per_year": round(reg["slope"] * 365, 1),
                "r_squared": reg["r_squared"],
            },
            "projections": projections,
        }

    if bf_ts:
        bc["body_fat_pct"] = {
            "history": [{"date": dt.strftime("%Y-%m-%d"), "pct": round(v, 1)} for dt, v in bf_ts],
            "stats": stat_block([v for _, v in bf_ts]),
        }
    if lbm_ts:
        bc["lean_body_mass"] = {
            "history": [{"date": dt.strftime("%Y-%m-%d"), "kg": round(v, 1)} for dt, v in lbm_ts],
            "stats": stat_block([v for _, v in lbm_ts]),
        }
    if weight_ts and lbm_ts and len(weight_ts) >= 2 and len(lbm_ts) >= 2:
        first_w, last_w = weight_ts[0][1], weight_ts[-1][1]
        first_lbm, last_lbm = lbm_ts[0][1], lbm_ts[-1][1]
        fat_gain = (last_w - last_lbm) - (first_w - first_lbm)
        lean_gain = last_lbm - first_lbm
        total_gain = last_w - first_w
        bc["gain_decomposition"] = {
            "total_kg": round(total_gain, 1),
            "lean_kg": round(lean_gain, 1),
            "fat_kg": round(fat_gain, 1),
            "lean_pct": round(lean_gain / total_gain * 100, 0) if total_gain else 0,
            "fat_pct": round(fat_gain / total_gain * 100, 0) if total_gain else 0,
        }

    result["body_composition"] = bc if bc else None

    # ------------------------------------------------------------------
    # Workouts
    # ------------------------------------------------------------------
    workout_data = []
    for w in workouts:
        ws = parse_date(w.get("startDate", ""))
        we = parse_date(w.get("endDate", ""))
        wtype = w.get("workoutActivityType", "").replace("HKWorkoutActivityType", "")
        dur = float(w.get("duration", 0))
        cal = float(w.get("totalEnergyBurned", 0))
        dist = float(w.get("totalDistance", 0))

        wd = {
            "date": ws.strftime("%Y-%m-%d %H:%M") if ws else None,
            "type": wtype,
            "duration_min": round(dur, 1),
            "calories": round(cal, 0),
            "distance_km": round(dist, 2),
        }

        if ws and we:
            whr = [v for dt, v in hr_ts if ws <= dt <= we]
            pre_hr = [v for dt, v in hr_ts if ws - timedelta(minutes=30) <= dt < ws]
            post_hr = [v for dt, v in hr_ts if we < dt <= we + timedelta(minutes=15)]
            if whr:
                wd["hr_mean"] = round(statistics.mean(whr), 0)
                wd["hr_max"] = round(max(whr), 0)
                wd["hr_min"] = round(min(whr), 0)
                wd["peak_hr_pct_max"] = round(max(whr) / max_hr_est * 100, 0) if max_hr_est else None
            if pre_hr:
                wd["pre_workout_hr"] = round(statistics.mean(pre_hr), 0)
            if post_hr:
                wd["post_15min_hr"] = round(statistics.mean(post_hr), 0)
            if pre_hr and post_hr:
                wd["recovery_delta"] = round(statistics.mean(post_hr) - statistics.mean(pre_hr), 0)

        workout_data.append(wd)

    # Type comparison
    type_stats = defaultdict(lambda: {"dur": [], "cal": [], "hr": []})
    for wd in workout_data:
        type_stats[wd["type"]]["dur"].append(wd["duration_min"])
        type_stats[wd["type"]]["cal"].append(wd["calories"])
        if "hr_mean" in wd:
            type_stats[wd["type"]]["hr"].append(wd["hr_mean"])

    type_comparison = {}
    for t, s in type_stats.items():
        type_comparison[t] = {
            "count": len(s["dur"]),
            "avg_duration": round(safe_mean(s["dur"]), 1) if s["dur"] else None,
            "avg_calories": round(safe_mean(s["cal"]), 0) if s["cal"] else None,
            "avg_hr": round(safe_mean(s["hr"]), 0) if s["hr"] else None,
        }

    # Workout frequency gaps
    workout_dates = sorted([parse_date(w.get("startDate", "")) for w in workouts if parse_date(w.get("startDate", ""))])
    gaps = [(workout_dates[i] - workout_dates[i-1]).days for i in range(1, len(workout_dates))] if len(workout_dates) >= 2 else []

    result["workouts"] = {
        "total": len(workouts),
        "individual": workout_data,
        "type_comparison": type_comparison,
        "frequency": {
            "first": workout_dates[0].strftime("%Y-%m-%d") if workout_dates else None,
            "last": workout_dates[-1].strftime("%Y-%m-%d") if workout_dates else None,
            "avg_gap_days": round(safe_mean(gaps), 1) if gaps else None,
            "max_gap_days": max(gaps) if gaps else None,
            "median_gap_days": round(safe_median(gaps), 0) if gaps else None,
        },
    }

    # ------------------------------------------------------------------
    # Respiratory
    # ------------------------------------------------------------------
    result["respiratory"] = {
        "spo2": stat_block([v for _, v in spo2_ts]) if spo2_ts else None,
        "respiratory_rate": stat_block([v for _, v in resp_ts]) if resp_ts else None,
        "wrist_temperature": stat_block([v for _, v in wrist_temp_ts]) if wrist_temp_ts else None,
        "vo2max": stat_block([v for _, v in vo2_ts]) if vo2_ts else None,
        "vo2max_monthly": monthly_agg(daily_mean(vo2_ts)) if vo2_ts else None,
    }

    # ------------------------------------------------------------------
    # Correlations
    # ------------------------------------------------------------------
    all_days = sorted(set(d_steps.keys()) & set(d_hr.keys()))
    sleep_dict = {n["night"]: n["total_h"] for n in nights}
    g_daily_avg = {}
    if glucose_ts:
        gd = defaultdict(list)
        for dt, v in glucose_ts:
            gd[dt.strftime("%Y-%m-%d")].append(v)
        g_daily_avg = {k: round(statistics.mean(v), 2) for k, v in gd.items()}

    metric_names = ["Steps", "ActiveCal", "AvgHR", "RHR", "HRV", "Sleep", "Glucose"]
    metric_sources = {
        "Steps": d_steps,
        "ActiveCal": d_active_cal,
        "AvgHR": d_hr,
        "RHR": rhr_daily,
        "HRV": d_hrv,
        "Sleep": sleep_dict,
        "Glucose": g_daily_avg,
    }

    corr_matrix = {}
    for m1 in metric_names:
        corr_matrix[m1] = {}
        for m2 in metric_names:
            paired = [(metric_sources[m1][d], metric_sources[m2][d])
                      for d in all_days
                      if d in metric_sources[m1] and d in metric_sources[m2]]
            if len(paired) >= 10:
                corr_matrix[m1][m2] = pearson([p[0] for p in paired], [p[1] for p in paired])
            else:
                corr_matrix[m1][m2] = None

    result["correlations"] = corr_matrix

    # ------------------------------------------------------------------
    # Lagged Correlations
    # ------------------------------------------------------------------
    lagged = {}
    # Steps → RHR lag
    w_steps = defaultdict(list)
    w_rhr = defaultdict(list)
    for d, s in d_steps.items():
        dt = datetime.strptime(d, "%Y-%m-%d")
        w_steps[dt.strftime("%Y-W%W")].append(s)
    for d, v in rhr_daily.items():
        dt = datetime.strptime(d, "%Y-%m-%d")
        w_rhr[dt.strftime("%Y-W%W")].append(v)
    wa_steps = {w: statistics.mean(v) for w, v in w_steps.items()}
    wa_rhr = {w: statistics.mean(v) for w, v in w_rhr.items()}
    weeks = sorted(set(wa_steps.keys()) & set(wa_rhr.keys()))

    steps_rhr_lag = {}
    for lag in [0, 1, 2, 4]:
        pairs = [(wa_steps[weeks[i-lag]], wa_rhr[weeks[i]])
                 for i in range(lag, len(weeks))
                 if weeks[i-lag] in wa_steps and weeks[i] in wa_rhr]
        if len(pairs) >= 5:
            steps_rhr_lag[f"lag_{lag}_weeks"] = {
                "r": pearson([p[0] for p in pairs], [p[1] for p in pairs]),
                "n": len(pairs)
            }
    lagged["weekly_steps_to_rhr"] = steps_rhr_lag

    # Sleep → next-day HRV
    sleep_hrv_pairs = []
    for n in nights:
        next_day = (datetime.strptime(n["night"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        if next_day in d_hrv and n["total_h"] > 1:
            sleep_hrv_pairs.append((n["total_h"], d_hrv[next_day]))

    if len(sleep_hrv_pairs) >= 10:
        short = [h for s, h in sleep_hrv_pairs if s < 6]
        normal = [h for s, h in sleep_hrv_pairs if 6 <= s <= 8]
        long_ = [h for s, h in sleep_hrv_pairs if s > 8]
        lagged["sleep_to_next_day_hrv"] = {
            "r": pearson([s for s, h in sleep_hrv_pairs], [h for s, h in sleep_hrv_pairs]),
            "n": len(sleep_hrv_pairs),
            "short_sleep_lt6h_hrv": round(safe_mean(short), 1) if short else None,
            "normal_sleep_6_8h_hrv": round(safe_mean(normal), 1) if normal else None,
            "long_sleep_gt8h_hrv": round(safe_mean(long_), 1) if long_ else None,
        }

    result["lagged_correlations"] = lagged

    # ------------------------------------------------------------------
    # Change Points
    # ------------------------------------------------------------------
    cp = {}

    # Steps
    sorted_step_days = sorted(d_steps.keys())
    if len(sorted_step_days) > 30:
        weekly_s = []
        for i in range(0, len(sorted_step_days), 7):
            chunk = sorted_step_days[i:i+7]
            weekly_s.append((chunk[0], statistics.mean([d_steps[d] for d in chunk])))
        step_w_vals = [v for _, v in weekly_s]
        changes = cusum_changes(step_w_vals)
        step_cps = []
        for direction, idx in changes:
            if idx < len(weekly_s):
                before = safe_mean(step_w_vals[max(0, idx-8):idx])
                after = safe_mean(step_w_vals[idx:min(len(step_w_vals), idx+8)])
                step_cps.append({
                    "direction": direction,
                    "date": weekly_s[idx][0],
                    "before": round(before, 0) if before else None,
                    "after": round(after, 0) if after else None,
                })
        cp["steps"] = step_cps

    # RHR
    rhr_sorted = sorted(rhr_daily.items())
    if len(rhr_sorted) > 20:
        rhr_vals = [v for _, v in rhr_sorted]
        changes = cusum_changes(rhr_vals, 1.5)
        rhr_cps = []
        for direction, idx in changes:
            if idx < len(rhr_sorted):
                before = safe_mean(rhr_vals[max(0, idx-15):idx])
                after = safe_mean(rhr_vals[idx:min(len(rhr_vals), idx+15)])
                rhr_cps.append({
                    "direction": direction,
                    "date": rhr_sorted[idx][0],
                    "before": round(before, 0) if before else None,
                    "after": round(after, 0) if after else None,
                })
        cp["resting_hr"] = rhr_cps

    result["change_points"] = cp

    # ------------------------------------------------------------------
    # Composite Scores
    # ------------------------------------------------------------------
    scores = {}

    # Cardio Fitness
    vo2_avg = safe_mean([v for _, v in vo2_ts]) if vo2_ts else None
    if vo2_avg is not None:
        if age and age < 30:
            if vo2_avg >= 51: scores["cardio_fitness"] = 95
            elif vo2_avg >= 42: scores["cardio_fitness"] = 75
            elif vo2_avg >= 35: scores["cardio_fitness"] = 55
            elif vo2_avg >= 31: scores["cardio_fitness"] = 35
            else: scores["cardio_fitness"] = 15
        else:
            if vo2_avg >= 45: scores["cardio_fitness"] = 95
            elif vo2_avg >= 37: scores["cardio_fitness"] = 75
            elif vo2_avg >= 30: scores["cardio_fitness"] = 55
            elif vo2_avg >= 25: scores["cardio_fitness"] = 35
            else: scores["cardio_fitness"] = 15

    # RHR
    rhr_avg = safe_mean(list(rhr_daily.values())) if rhr_daily else None
    if rhr_avg is not None:
        if rhr_avg < 60: scores["resting_hr"] = 95
        elif rhr_avg < 70: scores["resting_hr"] = 80
        elif rhr_avg < 80: scores["resting_hr"] = 60
        elif rhr_avg < 90: scores["resting_hr"] = 40
        else: scores["resting_hr"] = 20

    # Activity
    recent_step_vals = [v for d, v in d_steps.items() if d >= (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")]
    avg_recent_steps = safe_mean(recent_step_vals) if recent_step_vals else None
    if avg_recent_steps is not None:
        if avg_recent_steps >= 12000: scores["activity_level"] = 95
        elif avg_recent_steps >= 10000: scores["activity_level"] = 80
        elif avg_recent_steps >= 7500: scores["activity_level"] = 65
        elif avg_recent_steps >= 5000: scores["activity_level"] = 45
        else: scores["activity_level"] = 25

    # Exercise consistency
    if workout_dates and len(workout_dates) >= 2:
        span_months = max(1, (workout_dates[-1] - workout_dates[0]).days / 30)
        wpm = len(workouts) / span_months
        if wpm >= 12: scores["exercise_consistency"] = 90
        elif wpm >= 8: scores["exercise_consistency"] = 70
        elif wpm >= 4: scores["exercise_consistency"] = 50
        elif wpm >= 2: scores["exercise_consistency"] = 30
        else: scores["exercise_consistency"] = 15

    # Body composition
    if weight_ts:
        last_bmi = weight_ts[-1][1] / (height_m ** 2) if height_m else 0
        if last_bmi < 22: scores["body_composition"] = 95
        elif last_bmi < 25: scores["body_composition"] = 80
        elif last_bmi < 27: scores["body_composition"] = 65
        elif last_bmi < 30: scores["body_composition"] = 45
        else: scores["body_composition"] = 25

    # Metabolic health
    if glucose_ts:
        tir_val = sum(1 for v in gvals if 70 <= v <= 180) / len(gvals) * 100
        if tir_val >= 95 and cv < 25: scores["metabolic_health"] = 90
        elif tir_val >= 90: scores["metabolic_health"] = 75
        elif tir_val >= 80: scores["metabolic_health"] = 60
        elif tir_val >= 70: scores["metabolic_health"] = 45
        else: scores["metabolic_health"] = 30

    # Sleep
    if nights:
        avg_sleep = safe_mean([n["total_h"] for n in nights])
        deep_pcts = [n["deep_pct"] for n in nights if n["deep_pct"] > 0]
        avg_deep_pct = safe_mean(deep_pcts) if deep_pcts else 0
        s_score = 0
        if avg_sleep and 7 <= avg_sleep <= 9: s_score += 50
        elif avg_sleep and (6 <= avg_sleep < 7 or 9 < avg_sleep <= 10): s_score += 30
        else: s_score += 15
        if avg_deep_pct >= 20: s_score += 40
        elif avg_deep_pct >= 15: s_score += 25
        else: s_score += 10
        scores["sleep_quality"] = min(s_score, 95)

    # HRV
    hrv_avg = safe_mean(hrv_vals) if hrv_vals else None
    if hrv_avg is not None:
        if hrv_avg >= 60: scores["hrv_recovery"] = 90
        elif hrv_avg >= 40: scores["hrv_recovery"] = 70
        elif hrv_avg >= 25: scores["hrv_recovery"] = 50
        else: scores["hrv_recovery"] = 30

    overall = round(safe_mean(list(scores.values())), 0) if scores else None

    result["composite_scores"] = {
        "dimensions": scores,
        "overall": overall,
    }

    # ------------------------------------------------------------------
    # Trend Momentum
    # ------------------------------------------------------------------
    today_str = datetime.now().strftime("%Y-%m-%d")
    d30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    d90 = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    d180 = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

    momentum = {}
    for name, data in [("steps", d_steps), ("active_cal", d_active_cal), ("avg_hr", d_hr)]:
        momentum[name] = {
            "last_30d": period_avg(data, d30, today_str),
            "last_90d": period_avg(data, d90, today_str),
            "last_180d": period_avg(data, d180, today_str),
            "all_time": period_avg(data, "2000-01-01", today_str),
        }
    momentum["rhr"] = {
        "last_30d": period_avg(rhr_daily, d30, today_str),
        "last_90d": period_avg(rhr_daily, d90, today_str),
        "last_180d": period_avg(rhr_daily, d180, today_str),
        "all_time": period_avg(rhr_daily, "2000-01-01", today_str),
    }
    result["trend_momentum"] = momentum

    # ------------------------------------------------------------------
    # Audio Exposure
    # ------------------------------------------------------------------
    audio = {}
    if headphone_ts:
        hp_vals = [v for _, v in headphone_ts]
        audio["headphone"] = {
            "stats": stat_block(hp_vals),
            "above_80db_pct": round(sum(1 for v in hp_vals if v > 80) / len(hp_vals) * 100, 2),
            "above_85db_pct": round(sum(1 for v in hp_vals if v > 85) / len(hp_vals) * 100, 2),
            "above_90db_pct": round(sum(1 for v in hp_vals if v > 90) / len(hp_vals) * 100, 2),
        }
    if env_audio_ts:
        env_vals = [v for _, v in env_audio_ts]
        audio["environmental"] = {
            "stats": stat_block(env_vals),
            "above_80db_pct": round(sum(1 for v in env_vals if v > 80) / len(env_vals) * 100, 2),
        }
    result["audio_exposure"] = audio if audio else None

    # ------------------------------------------------------------------
    # Risk Stratification
    # ------------------------------------------------------------------
    risks = []

    if weight_ts:
        last_bmi = weight_ts[-1][1] / (height_m ** 2) if height_m else 0
        if last_bmi >= 30:
            risks.append({"level": "HIGH", "title": "BMI >= 30 (Obese Class I)",
                          "detail": f"BMI={round(last_bmi, 1)}"})
        elif last_bmi >= 27:
            risks.append({"level": "MODERATE", "title": "BMI 27-30 (Overweight)",
                          "detail": f"BMI={round(last_bmi, 1)}"})

    if vo2_avg is not None and age:
        threshold = 35 if age < 30 else 30
        if vo2_avg < threshold:
            risks.append({"level": "HIGH", "title": "Low VO2 Max for age",
                          "detail": f"VO2={round(vo2_avg, 1)}"})

    if avg_recent_steps is not None:
        if avg_recent_steps < 5000:
            risks.append({"level": "HIGH", "title": "Sedentary (recent avg <5000 steps/day)",
                          "detail": f"{round(avg_recent_steps, 0)} steps/day"})
        elif avg_recent_steps < 7500:
            risks.append({"level": "MODERATE", "title": "Insufficient activity (<7500 steps/day)",
                          "detail": f"{round(avg_recent_steps, 0)} steps/day"})

    if workout_dates and len(workout_dates) >= 2:
        span_months = max(1, (workout_dates[-1] - workout_dates[0]).days / 30)
        if len(workouts) / span_months < 4:
            risks.append({"level": "MODERATE", "title": "Low exercise frequency",
                          "detail": f"{round(len(workouts)/span_months, 1)}/month"})

    if rhr_avg and rhr_avg > 80:
        risks.append({"level": "MODERATE", "title": "Elevated resting heart rate",
                      "detail": f"RHR={round(rhr_avg, 0)} bpm"})

    if glucose_ts:
        vlow = sum(1 for v in gvals if v < 54) / n_g * 100
        if vlow > 1:
            risks.append({"level": "MODERATE", "title": "Elevated severe hypoglycemia rate",
                          "detail": f"{round(vlow, 1)}% readings <54 mg/dL"})

    if weight_ts and len(weight_ts) >= 3:
        w_reg = result.get("body_composition", {}).get("weight", {}).get("regression", {})
        if w_reg.get("kg_per_year", 0) > 5 and w_reg.get("r_squared", 0) > 0.7:
            risks.append({"level": "HIGH", "title": "Sustained weight gain trend",
                          "detail": f"+{w_reg['kg_per_year']}kg/year, R²={w_reg['r_squared']}"})

    if hrv_avg and hrv_avg < 30:
        risks.append({"level": "MODERATE", "title": "Low HRV (autonomic function)",
                      "detail": f"HRV={round(hrv_avg, 1)} ms"})

    result["risk_stratification"] = sorted(risks, key=lambda x: {"HIGH": 0, "MODERATE": 1, "LOW": 2}.get(x["level"], 3))

    return result

# ============================================================================
# Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Apple Health Export Analyzer")
    parser.add_argument("xml_path", nargs="?", help="Path to Apple Health export XML file")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    xml_path = args.xml_path or find_xml()
    if not xml_path or not os.path.isfile(xml_path):
        print(json.dumps({"error": f"XML file not found. Searched for common Apple Health export paths. Please provide the path as an argument."}))
        sys.exit(1)

    result = analyze(xml_path)

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        # Simple text output for debugging
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

if __name__ == "__main__":
    main()
