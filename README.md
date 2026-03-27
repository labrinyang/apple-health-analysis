# Apple Health Deep Analysis

**Mayo Clinic-grade health data analysis for Apple Health exports.**

A Claude Code skill that transforms raw Apple Health XML exports into comprehensive clinical-quality health assessment reports, applying 20+ peer-reviewed statistical methods with beautiful HTML visualization.

<img src="https://img.shields.io/badge/Claude_Code-Skill-D97757?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9IiNENzc1N0EiLz48L3N2Zz4="/>
<img src="https://img.shields.io/badge/Methods-20_papers-3B7DD8?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Python-3.6%2B-2D8B4E?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Dependencies-Zero-9B59B6?style=for-the-badge"/>

## Install

```bash
claude install-skill https://github.com/labrinyang/apple-health-analysis
```

Then say: **"Analyze my Apple Health data"** and point Claude to your `apple_health_export/` directory.

## What It Does

### 20 Peer-Reviewed Statistical Methods

| Category | Methods |
|----------|---------|
| **Causal Inference** | Granger Causality, Transfer Entropy, Convergent Cross Mapping |
| **Nonlinear Dynamics** | Sample Entropy, DFA, Poincare Plot, Multiscale Entropy |
| **Advanced CGM** | LBGI/HBGI, ADRR, CONGA, GVP, Glucose Rate of Change |
| **Circadian** | Cosinor Analysis, Interdaily Stability / Intradaily Variability |
| **Statistical** | Mann-Kendall, Bootstrap CI, Cohen's d, Bayesian Change Points |
| **Composite** | Biological Age, Fitness Age, Allostatic Load Index |

### Beautiful HTML Reports

Self-contained HTML report with 35+ SVG visualizations using Claude's design system:

- Circular gauge dashboards (8 health dimensions)
- 24-hour circadian rhythm curves
- Correlation heatmaps
- Weight trajectory with regression projection
- Heart rate zone donut charts
- Blood glucose TIR visualization
- Biological age comparison cards
- Trend momentum sparklines
- Causal inference verdict tables
- And much more...

### Clinical-Grade Analysis

- **Data Quality Assessment**: Every data stream evaluated for reliability before interpretation
- **Evidence Grading**: Each finding carries A/B/C/D confidence based on statistical significance + sample size
- **Risk Stratification**: HIGH / MODERATE / LOW risk flags with clinical significance
- **Missing Data Handling**: Graceful degradation — never crashes, never fabricates data
- **Multi-language**: Reports generated in English or Chinese (matches user language)

## How to Export Apple Health Data

1. Open the **Health** app on your iPhone
2. Tap your profile picture (top right)
3. Scroll down and tap **Export All Health Data**
4. Wait for the export to complete (may take a few minutes)
5. Save/share the `apple_health_export` folder to your computer

## Architecture

```
apple-health-analysis/
├── SKILL.md                              # Skill instructions
├── scripts/
│   ├── analyze_health.py                 # Base analysis engine (19 JSON sections)
│   ├── advanced_analytics.py             # 20 peer-reviewed methods
│   └── generate_report_html.py           # HTML report generator (35+ charts)
├── references/
│   ├── clinical_interpretation.md        # Evidence-based reference ranges
│   └── report_template.md               # Report structure template
└── evals/
    └── evals.json                        # Test cases
```

## Supported Data Types

| Data Type | Analysis |
|-----------|----------|
| Heart Rate | Circadian profile, zones, recovery, nocturnal trend |
| Resting HR | Monthly trend, autonomic function proxy |
| HRV (SDNN) | Poincare SD1/SD2, DFA alpha, trend |
| Blood Glucose (CGM) | TIR, MAGE, MODD, LBGI/HBGI, ADRR, CONGA, GVP |
| Steps | Daily/weekly/monthly patterns, Mann-Kendall trend |
| Workouts | HR during exercise, recovery analysis, type comparison |
| Sleep | Architecture (deep/REM/core), efficiency, duration |
| Body Weight | Regression projection, fat/lean decomposition |
| VO2 Max | Percentile for age/sex, fitness age |
| SpO2 | Blood oxygen assessment |
| Respiratory Rate | Trend analysis |
| Audio Exposure | WHO safe listening assessment |

## References

The advanced analysis engine cites 20 peer-reviewed publications including:

- Granger (1969) *Econometrica* — Causality testing
- Sugihara et al. (2012) *Science* — Convergent Cross Mapping
- Schreiber (2000) *Physical Review Letters* — Transfer Entropy
- Peng et al. (1994) *Physical Review E* — DFA
- Richman & Moorman (2000) *Am J Physiol* — Sample Entropy
- Kovatchev et al. (2002) *Diabetes Care* — Glucose risk indices
- Battelino et al. (2019) *Diabetes Care* — Time-in-Range consensus
- Cornelissen (2014) *Theor Biol Med Model* — Cosinor analysis
- Adams & MacKay (2007) — Bayesian change point detection
- Nes et al. (2013) *MSSE* — Fitness age
- And 10 more...

## License

MIT
