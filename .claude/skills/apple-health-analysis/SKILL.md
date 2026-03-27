---
name: apple-health-analysis
description: >
  Mayo Clinic-grade deep analysis of Apple Health export data. Parses the XML from iPhone's
  Health app export and produces a comprehensive clinical-quality health assessment report
  using 20+ peer-reviewed statistical methods including Granger Causality, Transfer Entropy,
  Convergent Cross Mapping, Sample Entropy, DFA, Cosinor analysis, Kovatchev glucose risk
  indices, Bayesian change-point detection, and biological age estimation.
  Use this skill whenever the user mentions Apple Health data, health export, health XML,
  CGM data, wants to analyze their fitness/sleep/heart rate/glucose/weight trends,
  or has an `apple_health_export` directory in their project. Also trigger when the user
  asks about health data analysis, wearable data analysis, or wants insights from their
  Apple Watch or iPhone health data. Even if they just say "analyze my health" or
  "look at my health data" and there's an Apple Health export nearby, use this skill.
  Trigger on Chinese equivalents too: "分析健康数据", "健康报告", "Apple Watch 数据".
---

# Apple Health Deep Analysis — Clinical-Grade Report Engine

This skill produces a **comprehensive health assessment report** at the standard of a top-tier academic medical center. It applies 20+ peer-reviewed statistical methods to Apple Health export data, contextualizes every finding against evidence-based clinical reference ranges, grades the confidence of each conclusion, and handles missing or insufficient data transparently.

**Medical Disclaimer**: This analysis is for informational and educational purposes only. It does not constitute medical advice, diagnosis, or treatment. Consult a qualified healthcare provider for medical decisions.

## Workflow

### Step 1: Locate the Export

Find the Apple Health XML file inside `apple_health_export/`. Common names: `导出.xml`, `export.xml`, `Export.xml`.

```bash
find . -path "*/apple_health_export/*.xml" -size +1M | head -5
```

### Step 2: Run Both Analysis Engines

```bash
# Base analysis — comprehensive health metrics
python3 <skill-path>/scripts/analyze_health.py <xml-path> --output json 2>/dev/null > /tmp/health_base.json

# Advanced analysis — 20 peer-reviewed statistical methods
python3 <skill-path>/scripts/advanced_analytics.py <xml-path> 2>/dev/null > /tmp/health_advanced.json
```

Both scripts: streaming XML parsing (handles 1GB+), Python 3.6+ only, no external deps. If >500MB, warn about 2-3 min runtime.

### Step 3: Generate HTML Report

Generate a visual HTML report with Claude's design system — interactive gauges, circadian charts, risk flags, and more:

```bash
python3 <skill-path>/scripts/generate_report_html.py /tmp/health_base.json /tmp/health_advanced.json -o /tmp/health_report.html
open /tmp/health_report.html  # macOS
# xdg-open /tmp/health_report.html  # Linux
```

This produces a self-contained HTML file (~40KB) with:
- Circular gauge charts for composite health scores
- SVG circadian rhythm curves (24h HR and glucose)
- Stacked TIR bar (time-in-range visualization)
- Weight trajectory sparkline with gain decomposition
- HR zone distribution bars
- Causal inference verdict table
- Biological/Fitness age comparison
- Trend momentum dashboard
- Data quality transparency table
- All in Claude's warm terracotta color scheme

After opening the HTML in the browser, also present a text-based analysis in the conversation following the report template (Step 5) — the HTML is a visual companion, not a replacement for the interpretive narrative.

### Step 4: Assess Data Quality

Before interpreting ANY results, read the `data_quality` section from the base analysis output. This tells you which analyses are reliable and which should be presented with caveats or skipped entirely.

**Data sufficiency rules:**
- If a metric has `reliability: "insufficient"` → **do not present** that section. Mention it in the Data Availability section as "not enough data."
- If `reliability: "low"` → present with a prominent caveat: "Limited data (X days of Y); interpret with caution."
- If `reliability: "moderate"` → present normally with a brief note on coverage.
- If `reliability: "high"` → present with full confidence.

From the advanced analysis, check `data_requirements` — it explicitly states which methods had enough data to run and which were skipped.

### Step 4: Read Clinical Reference

Read `references/clinical_interpretation.md` for evidence-based reference ranges and interpretation guidelines. This file contains paper-cited norms for every metric including advanced nonlinear dynamics and glucose risk indices. Every number in the report should be contextualized against these ranges.

### Step 5: Generate the Report

Read `references/report_template.md` for the exact output format. Follow it precisely. The template defines the structure, tone, evidence grading system, and formatting rules for a clinical-quality report.

## Key Principles

### Never Simplify the Analysis

Present the full statistical results. Do not round away precision, omit p-values, or skip advanced metrics to "keep it simple." If a method was computed, present it. Users who export their Apple Health data and ask for analysis want depth, not dumbed-down summaries. Let the report structure (executive summary first, deep dives later) handle the complexity gradient — not omission.

### Handle Missing Data Explicitly

Every health data export is different. Some users have CGM data; most don't. Some have years of Apple Watch data; others have weeks. The report must adapt gracefully:

- **Present only what exists.** Never fabricate or guess at missing data.
- **State what's missing.** In the Data Availability section, list which data types are present and which are absent, so the user knows what they're NOT seeing.
- **Explain impact.** If CGM data is absent, note that glucose analysis, MAGE/MODD/LBGI/HBGI, and glucose-exercise correlations cannot be performed. If VO2 Max is missing, note that fitness age cannot be estimated.
- **Adjust composite scores.** Only score dimensions that have data. If only 4 of 8 dimensions have data, the overall score is the mean of those 4 — don't penalize for missing data.

### Evidence Grading

Every major finding should carry a confidence indicator:

| Grade | Meaning | When to use |
|-------|---------|-------------|
| **A — Strong** | Multiple converging metrics, high data quality, statistically significant | p<0.01, >100 data points, confirmed by multiple methods |
| **B — Moderate** | Single strong metric or multiple weak ones, adequate data | p<0.05, 30-100 data points |
| **C — Suggestive** | Trend visible but not statistically significant, limited data | p<0.10, 10-30 data points |
| **D — Insufficient** | Too little data to draw conclusions | <10 data points, >50% missing |

Example: "Your resting heart rate has been rising over the past 3 months (Mann-Kendall tau=0.24, p=0.03; **Evidence: B**)"

### Report Language — MUST Match User Language

The entire report — including the HTML visual report AND the conversational narrative — must be in the user's language. Detection priority:
1. The language of the user's message (highest priority)
2. The XML locale attribute (e.g., `zh-Hans_US` → Chinese)
3. Data source names (Chinese app names → Chinese)

When generating the HTML report, pass the `--lang` flag:
```bash
python3 <skill-path>/scripts/generate_report_html.py base.json adv.json -o report.html --lang zh  # Chinese
python3 <skill-path>/scripts/generate_report_html.py base.json adv.json -o report.html --lang en  # English
```

For Chinese: use standard medical terminology (静息心率, 心率变异性, 血糖时间达标率, 最大摄氧量, 自主神经功能, 生物年龄, etc.). For the conversational analysis, write entirely in the detected language — do not mix languages unless quoting metric names that have no standard translation.

## What the Scripts Output

### Base Analysis (`analyze_health.py`)
Outputs JSON with keys: `personal_info`, `data_quality`, `data_overview`, `circadian_rhythm`, `heart_rate`, `heart_rate_variability`, `glucose`, `sleep`, `activity`, `body_composition`, `workouts`, `respiratory`, `correlations`, `lagged_correlations`, `change_points`, `composite_scores`, `trend_momentum`, `audio_exposure`, `risk_stratification`.

### Advanced Analysis (`advanced_analytics.py`)
Outputs JSON with keys: `methods_applied`, `references` (20 papers), `data_requirements`, `trend_tests`, `causal_inference`, `nonlinear_dynamics`, `advanced_glucose`, `circadian_quantification`, `statistical_rigor`, `bayesian_changepoints`, `biological_age_models`.

Each section is `null` when data is insufficient — never crashes or produces garbage output.
