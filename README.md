# Apple Health Deep Analysis

**Clinical-grade<sup>*</sup> health data analysis for Apple Health exports.**

Transforms raw Apple Health XML into comprehensive health assessment reports — 21 statistical methods, 30 disease risk screenings, 35+ SVG visualizations, citing 59 peer-reviewed papers. Works with Claude Code, Cursor, Copilot, Codex, Gemini CLI, and 8+ other AI agents.

> <sup>*</sup> **"Clinical-grade" refers to the use of peer-reviewed statistical methods and published clinical reference ranges — NOT to regulatory approval or diagnostic validity. This tool is for informational and educational purposes only. It is not a medical device, does not provide medical advice, and has not been validated in clinical trials or cleared by any regulatory body (FDA, CE, etc.). All disease risk screenings are preliminary estimates that require confirmation by a licensed healthcare provider. Do not make medical decisions based solely on this tool's output.**

<img src="https://img.shields.io/badge/skills.sh-compatible-D97757?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Papers-59_cited-3B7DD8?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Disease_Screenings-30-C44536?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Python_3.6+-Zero_Deps-9B59B6?style=for-the-badge"/>

## Install

```bash
npx skills add labrinyang/apple-health-analysis -y -g
```

Non-interactive, global install to all supported AI agents. Then say **"Analyze my Apple Health data"**.

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

---

## Features

### 21 Statistical Methods

| Category | Methods | Papers |
|----------|---------|--------|
| **Causal Inference** | Granger Causality, Transfer Entropy, Convergent Cross Mapping | Granger 1969, Schreiber 2000, Sugihara 2012 |
| **Nonlinear Dynamics** | Sample Entropy, DFA, Poincare Plot, Multiscale Entropy | Richman 2000, Peng 1994, Brennan 2001, Costa 2002 |
| **Advanced CGM** | LBGI/HBGI, ADRR, CONGA-1/2/4h, GVP, Rate of Change | Kovatchev 2002/2006, McDonnell 2005, Peyser 2018 |
| **Circadian** | Cosinor Analysis, Interdaily Stability, Intradaily Variability | Cornelissen 2014, Witting 1990 |
| **Trend & Change** | Mann-Kendall, Bayesian Change Points, CUSUM | Mann 1945, Adams & MacKay 2007 |
| **Statistical Rigor** | Bootstrap CI, Cohen's d / Hedge's g, Permutation Tests | Efron 1979, Cohen 1988 |
| **Composite Models** | Biological Age, Fitness Age, Allostatic Load Index | Levine 2013, Nes 2013, McEwen 1998 |

### 30 Disease Risk Screenings

Each screening uses paper-cited biomarker thresholds and returns a risk score with contributing factors and clinical recommendations.

| Category | Conditions | Key References |
|----------|-----------|----------------|
| **Endocrine** | Type 2 Diabetes, Hypothyroidism, Hyperthyroidism, Insulin Resistance | Lindstrom 2003 (FINDRISC), Lee 2021, Hall 2018, Battelino 2019 |
| **Cardiovascular** | CVD, Hypertension, Coronary Artery Disease, Atrial Fibrillation, Heart Failure, POTS | D'Agostino 2008 (Framingham), Krivoshei 2022, Cole 1999 (NEJM), Alonso 2013 (CHARGE-AF) |
| **Respiratory** | Obstructive Sleep Apnea, COPD | Chung 2008 (STOP-BANG), Zhang 2025 |
| **Neurological** | Parkinson's (early), Cognitive Decline, Seizure Risk | Adams 2024 (WATCH-PD), Doi 2022 (JAMA), Regalia 2024 |
| **Musculoskeletal** | Sarcopenia, Fall Risk | Cruz-Jentoft 2019 (EWGSOP2), Apple Walking Steadiness |
| **Sleep Disorders** | Insomnia, REM Behavior Disorder, Circadian Rhythm Disorder | Stefani 2023, Diago 2024, Morin 2017 |
| **Psychiatric** | Depression/Circadian Disruption, Anxiety, Chronic Fatigue | Lyall 2018 (Lancet Psych), Chalmers 2014, Escorihuela 2020 |
| **Other** | Anemia, Hearing Loss, Infection/Fever, Metabolic Syndrome, Vitamin D proxy, Dehydration | Li 2021 (Nature Med), Mishra 2020 (Nature), WHO 2022, Alberti 2006 |

### HTML Report (35+ SVG Charts)

Self-contained ~160KB HTML using Claude's design system. Charts and data are pre-rendered; 14 narrative slots are left empty for the AI to fill with personalized clinical interpretation.

**Visualizations include:**
- Circular gauge dashboard (8 dimensions + overall score)
- 24-hour circadian curves (heart rate + glucose)
- 7×7 cross-metric correlation heatmap
- Weight trajectory with linear regression + projection
- Heart rate zone donut chart
- Blood glucose TIR stacked bar
- Disease risk screening cards (color-coded by severity)
- Biological vs Fitness vs Chronological age comparison
- Sleep architecture donut
- Monthly trend bar charts with sparklines
- Workout type comparison
- Data quality stream table

### Clinical Rigor

- **Data Quality Assessment**: 11 data streams evaluated (reliability grade: high / moderate / low / insufficient)
- **Evidence Grading**: A (strong) / B (moderate) / C (suggestive) / D (insufficient) per finding
- **Missing Data Protocol**: Never crashes, never fabricates. Sections with insufficient data are skipped with explanation
- **Multi-language**: `--lang en` / `--lang zh` for report UI; AI narratives written in user's language

### Supported Apple Health Data Types (27)

| Data Type | Metrics Derived |
|-----------|----------------|
| Heart Rate (continuous) | Circadian profile, zones, nocturnal trend, day-night ratio, workout HR |
| Resting Heart Rate | Monthly trend, autonomic proxy, disease screening input |
| HRV (SDNN) | Poincare SD1/SD2, DFA alpha, Sample Entropy, MSE, trend |
| Blood Glucose (CGM) | TIR, MAGE, MODD, LBGI/HBGI, ADRR, CONGA, GVP, GMI, eA1c, rate of change |
| Steps | Daily/weekly/monthly, Mann-Kendall, change points, Granger causality |
| Workouts | HR during exercise, recovery analysis, type comparison, caloric efficiency |
| Sleep Stages | Architecture (deep/REM/core), efficiency, duration, RBD screening |
| Body Weight | Regression projection, BMI, fat/lean decomposition |
| Body Fat % | Trend, gain decomposition |
| VO2 Max | Age/sex percentile, fitness age |
| SpO2 | Nocturnal desaturation (OSA screening) |
| Respiratory Rate | COPD/infection screening |
| Walking Speed | Sarcopenia, cognitive decline proxy |
| Stair Ascent Speed | Sarcopenia screening |
| Walking Steadiness | Fall risk assessment |
| Wrist Temperature | Infection/fever detection, circadian |
| Headphone Audio | WHO safe listening, hearing loss risk |
| Environmental Audio | Noise exposure assessment |
| Flights Climbed | Activity indicator |
| Time in Daylight | Vitamin D proxy |
| Stand Time | Sedentary behavior |
| Active/Basal Energy | Total energy expenditure |
| Physical Effort | Activity intensity |
| ECG recordings | Rhythm classification summary |
| Walking Step Length | Gait analysis |
| Walking Asymmetry | Gait analysis |
| Cycling Distance | Workout analysis |

---

## How to Export Apple Health Data

1. Open **Health** app on iPhone → tap profile picture (top right)
2. Scroll down → **Export All Health Data**
3. Save the `apple_health_export` folder to your computer

---

## Architecture

```
apple-health-analysis/                       10,198 lines total
├── SKILL.md                                 (176 lines — workflow + principles)
├── scripts/
│   ├── analyze_health.py                    (1,622 — base analysis, 19 JSON sections)
│   ├── advanced_analytics.py                (3,609 — 21 methods + 30 screenings)
│   └── generate_report_html.py              (2,857 — HTML report, 35+ SVG charts)
├── references/
│   ├── clinical_interpretation.md           (480 — 13 categories of reference ranges)
│   ├── report_template.md                   (221 — report structure + formatting rules)
│   └── wearable_screening_literature.md     (1,233 — 28 disease screening evidence base)
├── .claude-plugin/                          (Claude Code plugin manifests)
├── .claude/skills/apple-health-analysis/    (skills.sh compatible skill path)
└── evals/
    └── evals.json                           (3 test cases)
```

---

## Complete Reference List (59 papers)

### Statistical Methods

1. Granger CWJ (1969). "Investigating causal relations by econometric models and cross-spectral methods." *Econometrica* 37(3):424-438.
2. Sugihara G et al. (2012). "Detecting causality in complex ecosystems." *Science* 338(6106):496-500.
3. Schreiber T (2000). "Measuring information transfer." *Physical Review Letters* 85(2):461-464.
4. Richman JS & Moorman JR (2000). "Physiological time-series analysis using approximate entropy and sample entropy." *Am J Physiol Heart Circ Physiol* 278:H2039.
5. Peng CK et al. (1994). "Mosaic organization of DNA nucleotides." *Physical Review E* 49:1685.
6. Brennan M et al. (2001). "Do existing measures of Poincare plot geometry reflect nonlinear features of heart rate variability?" *IEEE Trans Biomed Eng* 48(11):1342-1347.
7. Cornelissen G (2014). "Cosinor-based rhythmometry." *Theoretical Biology & Medical Modelling* 11:16.
8. Costa M et al. (2002). "Multiscale entropy analysis of complex physiologic time series." *Physical Review Letters* 89(6):068102.
9. Witting W et al. (1990). "Alterations in the circadian rest-activity rhythm in aging and Alzheimer's disease." *Biological Psychiatry* 27:563-572.
10. Adams RP & MacKay DJC (2007). "Bayesian online changepoint detection." *arXiv:0710.3742*.
11. Mann HB (1945). "Nonparametric tests against trend." *Econometrica* 13:245-259.
12. Efron B (1979). "Bootstrap methods: Another look at the jackknife." *The Annals of Statistics* 7(1):1-26.
13. Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*. 2nd ed.

### Clinical Standards & Glucose

14. Kovatchev BP et al. (2002). "Symmetrization of the blood glucose measurement scale and its applications." *Diabetes Care* 25:2058-2064.
15. Kovatchev BP et al. (2006). "Evaluation of a new measure of blood glucose variability in diabetes." *Diabetes Technology & Therapeutics* 8(6):644-653.
16. McDonnell CM et al. (2005). "A novel approach to continuous glucose analysis utilizing glycemic variation." *Diabetes Technology & Therapeutics* 7(2):253-263.
17. Peyser TA et al. (2018). "Glycemic variability percentage: A novel method for assessing glycemic variability from CGM data." *J Diabetes Sci Technol* 12(4):718-726.
18. Battelino T et al. (2019). "Clinical targets for continuous glucose monitoring data interpretation." *Diabetes Care* 42(8):1593-1603.
19. Hall H et al. (2018). "Glucotypes reveal new patterns of glucose dysregulation." *PLOS Biology* 16(7):e2005143.
20. Shah VN et al. (2019). "Continuous glucose monitoring profiles in healthy nondiabetic participants." *J Clin Endocrinol Metab* 104(10):4356-4364.
21. Monnier L et al. (2017). "Toward defining the threshold between low and high glucose variability." *Diabetes Care* 40(7):832-838.

### Cardiovascular & Fitness

22. D'Agostino RB et al. (2008). "General cardiovascular risk profile for use in primary care." *Circulation* 117(6):743-753.
23. Fox K et al. (2007). "Resting heart rate in cardiovascular disease." *CMAJ* 177(5):461-466.
24. Cole CR et al. (1999). "Heart-rate recovery immediately after exercise as a predictor of mortality." *NEJM* 341(18):1351-1357.
25. Kodama S et al. (2009). "Cardiorespiratory fitness as a quantitative predictor of all-cause mortality and cardiovascular events." *JAMA* 301(19):2024-2035.
26. Nes BM et al. (2013). "Estimating V·O2peak from a nonexercise prediction model." *Medicine & Science in Sports & Exercise* 45(11):2017.
27. Palatini P et al. (1999). "Heart rate as a predictor of cardiovascular risk." *J Hypertens* 17(7):903-910.
28. Tsuji H et al. (1996). "Reduced heart rate variability and mortality risk in an elderly cohort." *Circulation* 94(11):2850-2855.
29. Krivoshei L et al. (2022). "Smartwatch-based detection of hypertension." *medRxiv*.
30. Alonso A et al. (2013). "Simple risk model predicts incidence of atrial fibrillation." *Circulation* 127:962-972.
31. Perez MV et al. (2019). "Large-scale assessment of a smartwatch to identify atrial fibrillation." *NEJM* 381:1909-1917.

### Composite Models

32. Levine ME (2013). "Modeling the rate of senescence." *Journals of Gerontology Series A* 68(6):667-674.
33. McEwen BS (1998). "Protective and damaging effects of stress mediators." *New England Journal of Medicine* 338:171-179.

### Disease Screening

34. Lindstrom J & Tuomilehto J (2003). "The diabetes risk score." *Diabetes Care* 26(3):725-731.
35. Chung F et al. (2008). "STOP questionnaire: A tool to screen patients for obstructive sleep apnea." *Anesthesiology* 108:812-821.
36. Alberti KGMM et al. (2006). "Metabolic syndrome — a new world-wide definition." *Lancet* 366:1059-1062.
37. Lee DY et al. (2021). "Association between thyroid function and heart rate monitored by wearable devices." *Endocrinology and Metabolism* 36(6):1121-1130.
38. Biondi B & Cooper DS (2008). "The clinical significance of subclinical thyroid dysfunction." *Endocrine Reviews* 29(1):76-131.
39. Vinik AI et al. (2003). "Diabetic autonomic neuropathy." *Diabetes Care* 26:1553-1579.
40. Goldberger AL et al. (2002). "What is physiologic complexity and how does it change with aging and disease?" *PNAS* 99:2466-2472.
41. Lyall LM et al. (2018). "Association of disrupted circadian rhythmicity with mood disorders." *Lancet Psychiatry* 5:507-514.
42. Smagula SF et al. (2016). "Rest-activity rhythms characteristics and seasonal changes in seasonal affective disorder." *J Clin Psychiatry* 77:e1085-e1091.
43. Chalmers JA et al. (2014). "Anxiety disorders are associated with reduced heart rate variability: A meta-analysis." *Frontiers in Psychiatry* 5:80.
44. Alvares GA et al. (2013). "Reduced heart rate variability in social anxiety disorder." *Depress Anxiety* 30(12):1128-1134.
45. Tomasi J et al. (2024). "Heart rate variability and anxiety: A systematic review." *Psychophysiology* 61(2):e14481.
46. Li X et al. (2021). "Digital health: Tracking physiomes and activity using wearable biosensors reveals useful health-related information." *Nature Medicine*.
47. Mishra T et al. (2020). "Pre-symptomatic detection of COVID-19 from smartwatch data." *Nature Biomedical Engineering*.
48. Doi T et al. (2022). "Association of dual decline in cognition and gait speed with risk of dementia." *JAMA Network Open*.
49. Stefani A et al. (2023). "Ambulatory detection of REM sleep behavior disorder." *Movement Disorders* 38(5):847-855.
50. Diago EB et al. (2024). "Multicenter validation of actigraphy for RBD detection." *npj Digital Medicine* 8:158.
51. Cruz-Jentoft AJ et al. (2019). "Sarcopenia: Revised European consensus (EWGSOP2)." *Age and Ageing* 48(1):16-31.
52. Regalia G et al. (2024). "Apple Watch seizure detection." *Epilepsy & Behavior* 158:109911.
53. Mendonca F et al. (2018). "Oximetry for OSA screening." *Sleep Medicine Reviews* 41:94-106.
54. Stove MP et al. (2023). "Wearable respiratory monitoring in COPD." *Respiratory Care* 68(7).
55. Zhang C et al. (2025). "Digital health monitoring for COPD." *Digital Health* 11.
56. Wu CT et al. (2024). "Wearable sensors for COPD exacerbation." *JMIR mHealth* 12:e63047.
57. Escorihuela RM et al. (2020). "Reduced heart rate variability predicts fatigue severity in CFS/ME." *J Translational Medicine*.
58. WHO (2022). *Global Standard for Safe Listening*. Geneva.
59. Holick MF (2007). "Vitamin D deficiency." *New England Journal of Medicine* 357:266-281.

---

## Changelog

### v2.0.0 (2026-03-27)
- **30 Disease Risk Screenings** across 8 categories (endocrine, cardiovascular, respiratory, neurological, musculoskeletal, sleep, psychiatric, other)
- **1,233-line evidence base** (`wearable_screening_literature.md`) covering 28 screening algorithms
- **HTML report refactored**: 14 AI narrative slots for personalized clinical interpretation
- **skills.sh compatible**: `npx skills add` installs to all AI agents
- **Claude Code plugin**: `.claude-plugin/` manifests for `claude plugins install`
- **Algorithm review**: Cosinor sign convention verified, weight_trend_kg_yr fixed, Poincaré caveat added
- **Data quality system**: 11 streams × reliability grading, 13 sufficiency checks, auto-warnings
- **i18n**: Chinese/English support with `--lang` flag

### v1.0.0 (2026-03-27)
- **21 statistical methods** from 20 peer-reviewed papers
- **Base analysis engine**: 19 JSON sections covering HR, HRV, glucose, sleep, activity, body composition, workouts, respiratory, correlations, change points
- **Advanced analytics**: Granger Causality, Transfer Entropy, CCM, Sample Entropy, DFA, Poincaré, Multiscale Entropy, Cosinor, IS/IV, Mann-Kendall, Bootstrap CI, Cohen's d, Bayesian Change Points, Fitness Age, Biological Age, Allostatic Load
- **HTML report generator**: 35+ SVG charts, Claude design system, responsive layout
- **Clinical reference**: 480-line evidence-based interpretation guide
- **8 initial disease screenings**: T2D, CVD, OSA, Metabolic Syndrome, Autonomic Neuropathy, Depression, Heart Failure, AFib
- **Zero dependencies**: Pure Python 3.6+ standard library

## License

MIT
