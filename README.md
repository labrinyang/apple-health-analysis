# Apple Health Deep Analysis

**Clinical-grade health data analysis for Apple Health exports.**

Transforms raw Apple Health XML into comprehensive health assessment reports — 21 peer-reviewed statistical methods, 30 disease risk screenings, 35+ SVG visualizations, all in a beautiful HTML report with Claude's design system.

<img src="https://img.shields.io/badge/skills.sh-compatible-D97757?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Methods-21_papers-3B7DD8?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Disease_Screenings-30-C44536?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Dependencies-Zero-9B59B6?style=for-the-badge"/>

## Install

```bash
npx skills add labrinyang/apple-health-analysis -y -g
```

That's it. Installs globally to all supported agents: Claude Code, Cursor, GitHub Copilot, Codex, Gemini CLI, Cline, OpenCode, and more.

<details>
<summary>Alternative: Claude Code Plugin CLI</summary>

```bash
claude plugins marketplace add labrinyang/apple-health-analysis
claude plugins install apple-health-analysis
```
</details>

<details>
<summary>Update</summary>

```bash
npx skills update
```
</details>

Then say: **"Analyze my Apple Health data"** — the skill triggers automatically.

## What It Does

### 21 Peer-Reviewed Statistical Methods

| Category | Methods |
|----------|---------|
| **Causal Inference** | Granger Causality, Transfer Entropy, Convergent Cross Mapping |
| **Nonlinear Dynamics** | Sample Entropy, DFA, Poincare Plot, Multiscale Entropy |
| **Advanced CGM** | LBGI/HBGI, ADRR, CONGA, GVP, Glucose Rate of Change |
| **Circadian** | Cosinor Analysis, Interdaily Stability / Intradaily Variability |
| **Statistical** | Mann-Kendall, Bootstrap CI, Cohen's d, Bayesian Change Points |
| **Composite** | Biological Age, Fitness Age, Allostatic Load Index |

### 30 Disease Risk Screenings

| Category | Conditions | Key Papers |
|----------|-----------|------------|
| **Endocrine** | T2D, Hypothyroidism, Hyperthyroidism, Insulin Resistance | FINDRISC, Lee 2021 |
| **Cardiovascular** | CVD, Hypertension, CAD, AFib, Heart Failure, POTS | Framingham, Cole 1999 NEJM, CHARGE-AF |
| **Respiratory** | OSA, COPD | STOP-BANG, Zhang 2025 |
| **Neurological** | Parkinson's, Cognitive Decline, Seizure Risk | WATCH-PD, Doi 2022 JAMA |
| **Musculoskeletal** | Sarcopenia, Fall Risk | EWGSOP2, Apple Walking Steadiness |
| **Sleep** | Insomnia, REM Behavior Disorder, Circadian Disorder | Stefani 2023, Diago 2024 |
| **Psychiatric** | Depression, Anxiety, Chronic Fatigue | Lyall 2018 Lancet Psych, Chalmers 2014 |
| **Other** | Anemia, Hearing Loss, Infection/Fever, Metabolic Syndrome | Li 2021 Nature Med, Mishra 2020 Nature, WHO 2022 |

### HTML Report with 35+ Charts

Self-contained HTML report (~160KB) using Claude's design system:

- Circular gauge dashboards (8 health dimensions + overall score)
- 24-hour circadian rhythm curves (HR + glucose)
- Correlation heatmap (7×7 matrix)
- Weight trajectory with regression projection
- Heart rate zone donut charts
- Blood glucose TIR stacked bar
- Disease risk screening cards with color-coded severity
- Biological/Fitness age comparison
- Trend momentum sparklines
- 14 empty narrative slots for AI to fill with personalized analysis

### Clinical Rigor

- **Data Quality Assessment**: 11 data streams evaluated for reliability before interpretation
- **Evidence Grading**: Each finding carries A/B/C/D confidence
- **30 Disease Screenings**: Paper-cited thresholds from 40+ publications
- **Missing Data Handling**: Graceful degradation — never crashes, never fabricates
- **Multi-language**: EN/ZH with `--lang` flag

## How to Export Apple Health Data

1. Open **Health** app on iPhone → tap profile picture (top right)
2. Scroll down → **Export All Health Data**
3. Save the `apple_health_export` folder to your computer

## Architecture

```
apple-health-analysis/
├── SKILL.md                              # Skill instructions (180 lines)
├── scripts/
│   ├── analyze_health.py                 # Base analysis (19 JSON sections)
│   ├── advanced_analytics.py             # 21 methods + 30 disease screenings
│   └── generate_report_html.py           # HTML report (35+ SVG charts)
├── references/
│   ├── clinical_interpretation.md        # Evidence-based reference ranges
│   ├── report_template.md               # Report structure guide
│   └── wearable_screening_literature.md  # 1233-line disease screening evidence base
└── evals/
    └── evals.json
```

## Supported Data Types

| Data Type | Analysis |
|-----------|----------|
| Heart Rate | Circadian profile, zones, recovery, nocturnal trend |
| Resting HR | Monthly trend, autonomic function proxy |
| HRV (SDNN) | Poincare SD1/SD2, DFA alpha, trend |
| Blood Glucose (CGM) | TIR, MAGE, MODD, LBGI/HBGI, ADRR, CONGA, GVP |
| Steps | Daily/weekly/monthly patterns, Mann-Kendall trend |
| Workouts | HR during exercise, recovery, type comparison |
| Sleep | Architecture (deep/REM/core), efficiency, duration |
| Body Weight | Regression projection, fat/lean decomposition |
| VO2 Max | Percentile for age/sex, fitness age |
| SpO2 | Blood oxygen, nocturnal desaturation screening |
| Walking Speed | Sarcopenia screening, cognitive decline proxy |
| Walking Steadiness | Fall risk assessment |
| Audio Exposure | WHO safe listening assessment |
| Wrist Temperature | Infection/fever detection |

## References

40+ peer-reviewed publications including:

- Granger (1969) *Econometrica* — Causality testing
- Sugihara et al. (2012) *Science* — Convergent Cross Mapping
- Kovatchev et al. (2002) *Diabetes Care* — Glucose risk indices
- Cole (1999) *NEJM* — Heart rate recovery
- Mishra et al. (2020) *Nature Biomedical Engineering* — Infection detection
- Li et al. (2021) *Nature Medicine* — Wearable blood test prediction
- Doi et al. (2022) *JAMA Network Open* — Dual decline and dementia
- Nes et al. (2013) *MSSE* — Fitness age
- Battelino et al. (2019) *Diabetes Care* — CGM consensus
- And 30+ more...

## License

MIT
