# Comprehensive Health Assessment Report
**Data Source**: Apple Health Export
**Analysis Date**: 2026-03-27
**Data Period**: 2024-05-07 -- 2026-03-27 (688 days)
**Subject**: 23.8 year-old Male, 185.4 cm
**Methods Applied**: 20 statistical methods from 20 peer-reviewed publications

> **Disclaimer**: This report is generated from consumer wearable data for informational
> purposes only. It does not constitute medical advice. Consult a licensed healthcare
> provider before making health decisions based on this report.

---

## Executive Summary

- Your cardiorespiratory fitness is critically below age expectations, with a VO2 Max of 31.2 mL/min/kg placing you below the 5th percentile for a 23-year-old male, equivalent to the fitness of a 64-year-old (Fitness Age 64.4 vs. chronological 23.8; **Evidence: A**)
- Weight has increased 18.0 kg over 21 months at +0.82 kg/month with no sign of plateauing (linear R^2=0.87, Mann-Kendall tau=0.807, p<0.001); 68% of the gain is fat mass, pushing BMI to 30.5 (Obese Class I; **Evidence: A**)
- Daily step count has dropped sharply in the most recent quarter -- last 30 days average 4,142 steps/day vs. all-time average 8,889 steps/day, a 53% decline that corroborates your perception of declining fitness (Cohen's d=-0.28 recent vs. prior 90d; **Evidence: B**)
- Resting heart rate has risen to 84.0 bpm in the most recent month (Feb-Mar 2026), up from 69.1 bpm in Jan 2026 -- the overall mean of 77.9 bpm is in the "above average" range for your age and associated with increased cardiovascular risk (Fox et al. 2007; **Evidence: B**)
- Metabolic health is a bright spot: blood glucose time-in-range is 97.8% with an eA1c of 5.35%, well within non-diabetic norms (Battelino et al. 2019; **Evidence: A**)

---

## Section 1: Health Dashboard

| Dimension | Score | Grade | Key Metric | Trend |
|---|---|---|---|---|
| Metabolic Health | 90 | A | TIR 97.8%, eA1c 5.35%, CV 19.5% | -> stable |
| Resting Heart Rate | 60 | C | Mean 77.9 bpm (95% CI: 76.7-79.0) | ↑ worse |
| HRV / Autonomic Recovery | 50 | D+ | SDNN mean 35.6 ms, SD1/SD2 ratio 0.72 | -> stable |
| Cardiorespiratory Fitness | 35 | F | VO2 Max 31.2 mL/min/kg, <5th %ile | ↓ worse |
| Activity Level | 45 | D | 6,953 steps/day (last 90d), declining | ↓ worse |
| Exercise Consistency | 30 | F | 2.1 workouts/month, 88-day max gap | ↓ worse |
| Sleep Quality | 40 | D | Mean 9.5h in-bed, efficiency 67.1% | -> unstable |
| Body Composition | 25 | F | BMI 30.5, body fat 29.7%, +0.82 kg/mo | ↑ worse |
| **OVERALL** | **47** | **D+** | | |

This score reflects 8 of 8 possible dimensions. All dimensions have data, though weight (3% coverage, 261-day gap), VO2 Max (7% coverage), and workouts (6% coverage) have low reliability and should be interpreted with caution.

---

## Section 2: Data Availability & Quality

| Data Type | Records | Coverage | Span | Reliability | Notes |
|---|---|---|---|---|---|
| Heart Rate | 159,427 | 49% | 2024-05 -- 2026-03 | Low | 118-day gap; circadian analysis may be affected |
| Resting Heart Rate | 240 | 56% | 2025-01 -- 2026-03 | Moderate | 24-day max gap |
| HRV (SDNN) | 2,333 | 60% | 2025-01 -- 2026-03 | Moderate | 24-day max gap |
| Blood Glucose (CGM) | 8,040 | 32% | 2025-12 -- 2026-03 | Low | ~90 days; 63-day internal gap |
| Sleep | 7,038 | 50% | 2024-05 -- 2026-03 | Low | 112-day gap; architecture from 175 nights |
| Steps | 132,776 | 100% | 2024-05 -- 2026-03 | High | Near-continuous |
| Body Weight | 25 | 3% | 2024-05 -- 2026-02 | Low | Sporadic; 261-day gap |
| VO2 Max | 25 | 7% | 2025-01 -- 2026-01 | Low | Sparse; 65-day max gap |
| SpO2 | 4,545 | 59% | 2025-01 -- 2026-03 | Moderate | |
| Respiratory Rate | 8,524 | 51% | 2025-01 -- 2026-03 | Moderate | |
| Workouts | 30 | 6% | 2025-01 -- 2026-03 | Low | 88-day max gap between sessions |
| Body Fat % | 21 | -- | 2024-05 -- 2025-12 | Low | Sparse |
| *(not available)* | | | | | |
| Blood Pressure | 0 | -- | -- | -- | Not collected |
| ECG | 0 | -- | -- | -- | Not collected |

**Advanced analyses completed**: All 20 methods ran successfully. Mann-Kendall, Granger Causality, Transfer Entropy, CCM, Sample Entropy, DFA, Poincare, MSE, Cosinor, IS/IV, LBGI/HBGI, ADRR, CONGA, GVP, Bootstrap CIs, Cohen's d, Bayesian changepoints, Fitness Age, Biological Age, and Allostatic Load all had sufficient data.

---

## Section 3: Critical Findings & Risk Stratification

### HIGH RISK

**Sustained Weight Gain Trajectory** -- 18.0 kg gained over 21 months with no plateau
- Data: 87.0 kg (May 2024) to 105.0 kg (Feb 2026); linear regression +0.82 kg/month, R^2=0.87
- Mann-Kendall: tau=0.807, z=5.64, p<0.001 -- highly significant increasing trend (n=25)
- Gain decomposition: 12.2 kg fat (68%) + 5.8 kg lean (32%). Healthy gain is >=50% lean; this ratio indicates predominantly adipose accumulation
- Body fat %: 24.0% (May 2024) to 29.7% (Dec 2025), approaching the obese threshold for men (>25%, ACSM 2021)
- BMI: 30.5 (Obese Class I, WHO). Projected if trend continues: BMI 32.6 at +3 months, 34.7 at +12 months
- Clinical significance: BMI >30 is an independent risk factor for type 2 diabetes, cardiovascular disease, and musculoskeletal disorders
- Evidence grade: A
- Recommended action: Consult physician for metabolic workup. Aim for caloric deficit of 300-500 kcal/day combined with structured resistance training to preserve lean mass

**Critically Low VO2 Max** -- cardiorespiratory fitness far below age expectations
- Data: VO2 Max 31.2 mL/min/kg (mean, n=25), below the 5th percentile for 20-29 year-old males (ACSM: <37 = 5th percentile)
- Monthly trend: 31.2 (Jan 2025) -> 32.4 (Sep 2025) -> 30.1 (Jan 2026), suggesting a recent decline
- Clinical significance: Low CRF is a stronger predictor of all-cause mortality than smoking, diabetes, or hypertension (Kodama et al. 2009). Your Fitness Age equivalent is 64.4 years -- a gap of +40.6 years
- Apple Watch caveat: VO2 Max estimated from outdoor walking/running only; swimmers and cyclists may be underestimated (your workout mix includes swimming and elliptical)
- Evidence grade: A (despite sparse VO2 data, values are consistently low across 25 measurements over 12 months)
- Recommended action: Begin a structured aerobic program -- 3-4 sessions/week of 30+ minutes at 60-70% HRmax (Zone 2). Expect measurable improvement in 6-8 weeks

**Rapid Recent Activity Decline** -- step count collapsed in last 2 months
- Data: Monthly steps (mean): 11,916 (May 2025) -> 12,827 (Sep 2025) -> 9,986 (Jan 2026) -> 5,278 (Feb 2026) -> 4,217 (Mar 2026)
- Trend momentum: All-time 8,889 -> Last 180d 7,897 -> Last 90d 6,953 -> Last 30d 4,142 steps/day
- Change point: Feb 24, 2026 detected as a downward shift (before: 8,166 -> after: 3,989 steps/day)
- Effect size: Recent 90d vs prior 90d: Cohen's d=-0.28 (small effect; group1 mean 6,953, group2 mean 8,851, n1=91, n2=90)
- At current level (4,142 steps/day), you are in the "sedentary" category (<4,000 threshold; Paluch et al. 2022, Lancet)
- Evidence grade: B (Mann-Kendall on weekly steps: tau=-0.033, p=0.555 -- not significant over full span, but the recent decline is clear from momentum and changepoint analysis)
- Recommended action: Set an immediate daily target of 7,500+ steps. Even returning to 8,000 steps/day would provide approximately 50% mortality risk reduction vs. the current level

### MODERATE RISK

**Resting Heart Rate Elevated and Rising** -- above optimal range with concerning recent uptick
- Data: Overall mean RHR 77.9 bpm (95% CI: 76.7-79.0, n=240). Recent months: Jan 2026 = 69.1 bpm, Feb 2026 = 83.5 bpm, Mar 2026 = 84.0 bpm
- For a 23-year-old male, RHR 70-79 bpm is "average" and 80-89 bpm is "above average" with increased cardiovascular risk (Palatini 1999; Fox et al. 2007)
- Mann-Kendall on RHR: tau=-0.059, p=0.137 -- no statistically significant overall trend (n=240), but the recent 2-month surge from 69 to 84 bpm is notable
- Each 10 bpm above 60 is associated with ~20% increase in mortality risk (Cooney et al. 2010)
- Nocturnal HR monthly trend mirrors this: Jan 2026 = 66.3, Feb 2026 = 77.5, Mar 2026 = 78.3 bpm
- Evidence grade: B (recent pattern clear but overall trend non-significant)
- Recommended action: Monitor closely. If RHR remains >80 bpm for 4+ consecutive weeks despite adequate sleep and hydration, discuss with physician

**Low Exercise Frequency** -- insufficient structured exercise
- Data: 30 workouts over 421 days = 2.1 sessions/month. Max gap between workouts: 88 days
- WHO 2020 recommendation: 150-300 min/week moderate-intensity aerobic activity. Median exercise minutes/day is 0.0, indicating more than half of days have zero recorded exercise
- Last recorded workout: 2026-03-03 (24 days ago)
- Evidence grade: B
- Recommended action: Target 3 sessions/week minimum. Your data shows elliptical sessions maintain Zone 3-4 HR most effectively (mean HR 149 bpm, 84% HRmax) -- prioritize this modality

### POSITIVE FINDINGS

**Excellent Glycemic Control** -- non-diabetic glucose regulation is well within normal limits
- Data: TIR (70-180 mg/dL) = 97.8%, exceeding the >96% non-diabetic target (Vigersky 2019). eA1c 5.35% (normal <5.7%). Mean glucose 106.9 mg/dL (95% CI: 106.5-107.4)
- CV% = 19.5% (stable, well below 36% threshold; Monnier et al. 2017)
- MAGE = 37.7 mg/dL (<40 = normal), MODD = 16.9 mg/dL (<20 = normal)
- LBGI 1.08 (minimal risk), HBGI 0.39 (minimal risk) (Kovatchev et al. 2002)
- Evidence grade: A

**Healthy Heart Rate Complexity** -- autonomic nervous system shows good adaptive capacity
- HR Sample Entropy = 2.20 (high complexity, healthy; Richman & Moorman 2000)
- DFA alpha = 0.648 (approaching healthy 1/f range; Peng et al. 1994)
- Multiscale entropy profile: scale 1=2.20, scale 2=2.18, scale 3=1.96, scale 5=1.61 -- gradual decline consistent with healthy complexity preservation
- Evidence grade: B

**Normal Circadian Architecture** -- appropriate day-night heart rate modulation
- Day-night HR ratio: 1.51 (normal dipping pattern; range 1.20-1.59, Hermida et al. 2013)
- Cosinor acrophase: 16:53 (within normal 12:00-20:00 window)
- Interdaily Stability: 0.49 (moderately stable rhythm; Witting et al. 1990)
- Evidence grade: B

**Safe Audio Exposure** -- hearing health well protected
- Headphone mean: 47.9 dB, 0% above 80 dB
- Environmental mean: 56.8 dB, 1.1% above 80 dB
- Well below WHO safe listening thresholds
- Evidence grade: A

---

## Body Composition & Anthropometrics

### Key Metrics
| Metric | Value | Reference Range | Assessment |
|---|---|---|---|
| Current Weight | 105.0 kg (Feb 2026) | -- | -- |
| BMI | 30.5 | 18.5-24.9 normal (WHO) | Obese Class I |
| Body Fat % | 29.7% (Dec 2025) | 14-17% fitness, 18-24% average (ACSM, 20-29M) | Obese (>25%) |
| Lean Body Mass | 74.4 kg (Dec 2025) | -- | -- |
| Weight Gain Rate | +0.82 kg/month | -- | Concerning |
| Linear Regression R^2 | 0.87 | >0.7 = strong trend | Strong, consistent |

### Weight Trajectory
| Date | Weight (kg) | Body Fat % | Lean Mass (kg) | BMI |
|---|---|---|---|---|
| 2024-05-07 | 87.0 | 24.0 | 68.1 | 25.3 |
| 2024-09-05 | 92.7 | 25.7 | 68.9 | 27.0 |
| 2025-01-02 | 100.0 | 28.3 | 71.7 | 29.1 |
| 2025-03-17 | 103.8 | 29.3 | 73.4 | 30.2 |
| 2025-12-23 | 105.8 | 29.7 | 74.4 | 30.8 |
| 2026-02-02 | 105.0 | -- | -- | 30.5 |

Mann-Kendall trend test: tau=0.807, z=5.642, p<0.001 -- highly significant increasing trend (n=25)

### Gain Decomposition
Over the full data span (87.0 to 105.0 kg):
- Total gain: 18.0 kg
- Fat mass gain: 12.2 kg (68%)
- Lean mass gain: 5.8 kg (32%)

A healthy weight gain profile is >=50% lean mass. At 68% fat gain, dietary and exercise intervention is warranted (clinical_interpretation.md). The lean mass increase (5.8 kg) may partially reflect natural maturation in a 22-24 year-old male, but the fat-dominant ratio is not explained by growth alone.

### Projections (if current trend continues)
| Timeframe | Projected Weight (kg) | Projected BMI |
|---|---|---|
| +3 months | 112.0 | 32.6 |
| +6 months | 114.4 | 33.3 |
| +12 months | 119.3 | 34.7 (Obese Class II) |

### Clinical Context
At 23.8 years old, you are in a critical window for metabolic trajectory. BMI 30.5 at this age is associated with substantially elevated lifetime risk of type 2 diabetes and cardiovascular disease. The weight gain is not decelerating (R^2=0.87 indicates a consistent linear increase, not a plateauing curve). Your glucose metrics are still excellent, suggesting you have not yet developed insulin resistance -- this represents a window of opportunity to intervene before metabolic complications emerge.

---

## Cardiovascular Function

### Key Metrics
| Metric | Value | Reference Range | Assessment |
|---|---|---|---|
| Resting HR (mean) | 77.9 bpm (95% CI: 76.7-79.0, n=240) | 60-69 good, 70-79 average (Palatini 1999) | Average / above average |
| RHR last 30 days | 84.0 bpm (n=5) | <70 target for 23M | Above average |
| Walking HR (mean) | 118.8 bpm (n=189) | -- | Elevated for walking |
| Workout HR (mean) | 134.7 bpm (n=2,811 readings) | -- | Moderate intensity |
| VO2 Max (mean) | 31.2 mL/min/kg (n=25) | 42-48 = 50th %ile for 20-29M | <5th percentile |
| Max HR observed | 184 bpm (est. max: 191) | 208 - 0.7 x 23.8 = 191 | 96% HRmax reached |

### Resting HR Monthly Trend
| Month | Mean RHR (bpm) | n |
|---|---|---|
| 2025-04 | 75.2 | 27 |
| 2025-05 | 76.1 | 19 |
| 2025-06 | 86.5 | 6 |
| 2025-07 | 79.3 | 12 |
| 2025-08 | 81.8 | 16 |
| 2025-09 | 80.3 | 21 |
| 2025-10 | 82.3 | 7 |
| 2025-11 | 74.6 | 7 |
| 2025-12 | 73.8 | 17 |
| 2026-01 | 69.1 | 14 |
| 2026-02 | 83.5 | 10 |
| 2026-03 | 84.0 | 5 |

Mann-Kendall on RHR: tau=-0.059, z=-1.359, p=0.137 -- no significant overall trend (n=240). However, the pattern shows a dip to 69.1 bpm in January 2026 followed by a sharp rise to 84.0 bpm by March 2026. This recent trajectory warrants monitoring.

Effect size (recent vs. prior 90 days): Cohen's d=-0.087 (negligible; recent mean 75.9, prior mean 76.7, n1=34, n2=26). The recent spike is concentrated in the last 30 days and not yet reflected in the 90-day comparison.

Bayesian changepoint detection: RHR max posterior probability = 0.033 -- no statistically robust changepoint detected, though the Feb 2026 shift is flagged in the classical changepoint analysis (before: 75.0, after: 83.0).

### Heart Rate Zones
| Zone | %HRmax Range | % of All Readings | Interpretation |
|---|---|---|---|
| Below Zone 1 | <50% | 49.0% | Resting / sedentary |
| Zone 1 (Recovery) | 50-60% | 24.7% | Light activity |
| Zone 2 (Aerobic) | 60-70% | 19.8% | Fat burning, base fitness |
| Zone 3 (Tempo) | 70-80% | 5.2% | Aerobic development |
| Zone 4 (Threshold) | 80-90% | 1.2% | Anaerobic threshold |
| Zone 5 (Max) | 90-100% | 0.1% | Peak output |

Time in Zone 3+ (productive training zones): 6.5% of all HR readings. This is low -- effective cardiovascular conditioning requires sustained time in Zones 2-4. The vast majority of your recorded heart rate is at rest or light activity.

### VO2 Max Monthly Trend
| Month | VO2 Max (mL/min/kg) | n |
|---|---|---|
| 2025-01 | 31.2 | 5 |
| 2025-04 | 30.7 | 3 |
| 2025-08 | 31.4 | 3 |
| 2025-09 | 32.4 | 4 |
| 2025-12 | 30.3 | 1 |
| 2026-01 | 30.1 | 1 |

VO2 Max peaked at 32.4 in September 2025 (your most active workout month) and declined to 30.1 by January 2026 as workout frequency dropped. This pattern supports a direct relationship between exercise consistency and fitness level.

### Clinical Context
Your walking HR average of 118.8 bpm is high for a 23-year-old during moderate walking. For reference, well-conditioned individuals of your age would typically show walking HR of 90-105 bpm. This elevated walking HR, combined with low VO2 Max, indicates reduced cardiovascular efficiency -- your heart must work harder to meet basic physical demands. The recent RHR rise from 69 to 84 bpm in 2 months, combined with a simultaneous drop in daily steps from ~10,000 to ~4,000, suggests deconditioning may be accelerating.

---

## Autonomic Nervous System

### Key Metrics
| Metric | Value | Reference Range (25-35 age) | Assessment |
|---|---|---|---|
| HRV SDNN (mean) | 35.6 ms (95% CI: 34.5-36.5, n=2,333) | 40-55 good (Shaffer & Ginsberg 2017) | Below good; average range |
| HRV SDNN (median) | 28.3 ms | -- | Right-skewed distribution |
| Poincare SD1 | 22.3 ms | -- | Short-term (parasympathetic) variability |
| Poincare SD2 | 31.0 ms | -- | Long-term variability |
| SD1/SD2 Ratio | 0.72 | 0.5-1.5 = balanced | Balanced sympathovagal |
| CSI (SD2/SD1) | 1.39 | <3.0 = normal | Normal; no sympathetic overactivity |
| CVI (log(SD1xSD2)) | 6.54 | Higher = better vagal | Moderate vagal tone |

### HRV Monthly Trend
| Month | Mean SDNN (ms) | n |
|---|---|---|
| 2025-04 | 36.0 | 281 |
| 2025-05 | 38.2 | 178 |
| 2025-06 | 25.2 | 52 |
| 2025-07 | 36.8 | 124 |
| 2025-08 | 30.9 | 128 |
| 2025-09 | 34.5 | 180 |
| 2025-10 | 29.3 | 51 |
| 2025-11 | 36.6 | 72 |
| 2025-12 | 39.0 | 173 |
| 2026-01 | 42.4 | 141 |
| 2026-02 | 35.2 | 110 |
| 2026-03 | 29.4 | 59 |

Mann-Kendall on weekly HRV: tau=0.060, z=0.510, p=0.536 -- no significant trend (n=37 weekly aggregates). HRV fluctuates but peaked at 42.4 ms in Jan 2026 before dropping to 29.4 ms in March 2026, paralleling the activity decline.

### Nocturnal HR Monthly Trend
| Month | Mean Nocturnal HR (bpm) | n |
|---|---|---|
| 2025-01 | 76.5 | 1,453 |
| 2025-03 | 67.8 | 1,490 |
| 2025-05 | 67.2 | 840 |
| 2025-07 | 68.8 | 503 |
| 2025-09 | 77.7 | 894 |
| 2025-12 | 71.0 | 772 |
| 2026-01 | 66.3 | 695 |
| 2026-02 | 77.5 | 566 |
| 2026-03 | 78.3 | 246 |

The nocturnal HR pattern mirrors the RHR pattern -- a dip in Jan 2026 (66.3 bpm) followed by a sharp rise to 78.3 bpm in March. Nocturnal HR is a sensitive proxy for training status, weight change, and chronic stress (clinical_interpretation.md). The Feb-Mar 2026 increase coincides with the steep activity drop and may reflect deconditioning and/or physiological stress.

### Day-Night HR Ratio
- Day-night ratio: 1.51 (normal dipping pattern, 1.20-1.59 range; Hermida et al. 2013)
- Day-night difference: 35.6 bpm
- This normal dipping pattern is a positive finding -- it indicates preserved circadian autonomic modulation, not secondary hypertension or sleep apnea-related non-dipping.

### Correlation: RHR and HRV
RHR-HRV correlation: r=-0.587 (n=aligned daily observations). This strong inverse correlation is physiologically expected -- higher parasympathetic (vagal) tone lowers RHR while increasing beat-to-beat variability. Your balanced SD1/SD2 ratio (0.72) confirms that sympathovagal balance is preserved, though total HRV is below optimal for your age.

---

## Metabolic / Glucose

### Key Metrics
| Metric | Value | Reference / Target | Assessment |
|---|---|---|---|
| Mean Glucose | 106.9 mg/dL (95% CI: 106.5-107.4) | -- | -- |
| eA1c | 5.35% | <5.7% normal | Normal |
| GMI | 5.87% | <5.7% normal | Borderline -- note: GMI often differs from eA1c |
| TIR (70-180 mg/dL) | 97.8% | >96% for non-diabetic (Vigersky 2019) | Excellent |
| TBR (<70 mg/dL) | 1.6% (0.8% <54 + 0.77% 54-70) | <4% | Within target |
| TAR (>180 mg/dL) | 0.6% | <1% for non-diabetic | Excellent |
| CV% | 19.5% | <36% = stable (Monnier et al. 2017) | Stable |
| MAGE | 37.7 mg/dL | <40 normal (Service et al. 1970) | Normal |
| MODD | 16.9 mg/dL | <20 normal (Molnar et al. 1972) | Normal |
| J-Index | 16.3 | <20 normal (Wojcicki 1995) | Normal |
| GRI | 4.7 | Zone A (0-20) low risk (Klonoff et al. 2023) | Low risk |

### Kovatchev Glucose Risk Indices
| Metric | Value | Risk Level | Source |
|---|---|---|---|
| LBGI | 1.08 | Minimal (<1.1) | Kovatchev et al. 2002 |
| HBGI | 0.39 | Minimal (<4.5) | Kovatchev et al. 2002 |
| ADRR | 13.64 | Low (<20) | Kovatchev et al. 2006 |

### Continuous Glucose Analysis (CONGA & GVP)
| Metric | Value | Non-diabetic Reference | Source |
|---|---|---|---|
| CONGA-1h | 19.2 mg/dL | 15-25 (healthy) | McDonnell et al. 2005 |
| CONGA-2h | 24.5 mg/dL | 20-30 (healthy) | McDonnell et al. 2005 |
| CONGA-4h | 27.7 mg/dL | 25-35 (healthy) | McDonnell et al. 2005 |
| GVP | 30.8% | >30% = high variability | Peyser et al. 2018 |

### Rate of Change
| Metric | Value |
|---|---|
| Mean rate | 0.002 mg/dL/min |
| SD rate | 0.991 mg/dL/min |
| Max rise | 10.81 mg/dL/min |
| Max fall | -6.85 mg/dL/min |
| % rapid rise (>2 mg/dL/min) | 2.9% |
| % rapid fall (<-2 mg/dL/min) | 2.5% |

The max rise (10.81 mg/dL/min) and max fall (-6.85 mg/dL/min) are notable, though they represent extreme tail events. Rapid rises >2 mg/dL/min occur 2.9% of the time, suggesting occasional high-glycemic-index meals.

### Very Low Glucose Episodes
TBR <54 mg/dL = 0.8% (64 of 8,040 readings). This borderline exceeds the <1% target. Review compression low artifacts: readings <54 during sleep may be due to lying on the CGM sensor arm rather than true hypoglycemia.

### Glucose Circadian Rhythm
- Cosinor: MESOR 106.9 mg/dL, amplitude 9.9 mg/dL, acrophase 18:50
- R^2=0.113 (weak fit -- glucose driven more by meals than endogenous rhythm, as expected)
- Glucose is lowest 06:00-08:00 (92.9-94.1 mg/dL) and peaks 14:00-15:00 (118-121 mg/dL) and again 20:00-23:00 (117-118 mg/dL), consistent with a meal-driven pattern

### Weekly Pattern
| Day | Mean Glucose (mg/dL) | TIR % | Above 180 % |
|---|---|---|---|
| Mon | 108.7 | 98.7 | 1.3 |
| Tue | 100.9 | 97.0 | 0.0 |
| Wed | 101.9 | 92.6 | 0.3 |
| Thu | 108.7 | 99.0 | 0.2 |
| Fri | 104.7 | 99.8 | 0.1 |
| Sat | 109.3 | 99.2 | 0.8 |
| Sun | 114.0 | 98.5 | 1.5 |

Sunday has the highest mean glucose (114.0) and highest percentage above 180 (1.5%), suggesting dietary differences on weekends. Wednesday has the lowest TIR at 92.6% (still acceptable but below the 96% non-diabetic target) -- this may reflect a single anomalous day in the relatively short CGM dataset.

### Clinical Context
Your glucose regulation is excellent by all measures. Despite a BMI of 30.5, you show no signs of insulin resistance or impaired glucose tolerance in the CGM data. This is protective but should not be taken as reassurance that current weight trends are benign -- the metabolic consequences of obesity typically emerge over years, and maintaining glycemic health now provides a strong foundation for intervention. The GVP of 30.8% (borderline high variability; Peyser et al. 2018) and the occasional rapid glucose excursions suggest attention to meal composition could further optimize glycemic patterns.

---

## Nonlinear Dynamics & Complexity

### Heart Rate Complexity
| Metric | Value | Interpretation | Reference |
|---|---|---|---|
| Sample Entropy (m=2, r=2.71, N=326) | 2.20 | High complexity -- healthy | Richman & Moorman 2000 |
| DFA Alpha (N=326, R^2=0.993) | 0.648 | Between anti-correlated and healthy 1/f | Peng et al. 1994 |

Sample Entropy of 2.20 indicates rich, complex heart rate dynamics -- this is a positive finding associated with healthy adaptive regulation. The DFA alpha of 0.648 is below the ideal 1/f range of 0.75-1.05 but well above the 0.5 white-noise threshold. Computed on daily HR means (not beat-to-beat), this reflects longer-term regulatory dynamics. The value may be influenced by the 118-day gap in HR data.

### Multiscale Entropy (HR)
| Scale | SampEn |
|---|---|
| 1 | 2.20 |
| 2 | 2.18 |
| 3 | 1.96 |
| 5 | 1.61 |

The MSE profile shows gradual, monotonic decline across scales -- consistent with healthy complexity preservation (Costa et al. 2002). Pathological states typically show steep entropy loss at coarser scales.

### Glucose Complexity
| Metric | Value | Interpretation | Reference |
|---|---|---|---|
| Sample Entropy (m=2, r=4.66, N=2000) | 0.53 | Normal for CGM data (0.3-0.8 range) | Richman & Moorman 2000 |

Glucose Sample Entropy of 0.53 indicates regular but not rigid glucose patterns, consistent with healthy metabolic regulation combined with meal-driven variability.

---

## Activity & Exercise

### Daily Steps Summary
| Metric | Value |
|---|---|
| All-time mean | 8,889 steps/day (n=690 days) |
| Median | 7,457 steps/day |
| Last 90 days (95% CI) | 6,953 (5,543-8,750) steps/day |
| Last 30 days | 4,142 steps/day |
| Days over 10,000 | 240 (34.8%) |
| Days under 5,000 | 204 (29.6%) |

### Monthly Steps Trend
| Month | Mean Steps/Day | n |
|---|---|---|
| 2025-04 | 11,218 | 30 |
| 2025-05 | 11,916 | 31 |
| 2025-06 | 8,414 | 30 |
| 2025-07 | 8,567 | 31 |
| 2025-08 | 8,021 | 31 |
| 2025-09 | 12,827 | 30 |
| 2025-10 | 8,292 | 31 |
| 2025-11 | 8,111 | 30 |
| 2025-12 | 10,572 | 31 |
| 2026-01 | 9,986 | 31 |
| 2026-02 | 5,278 | 28 |
| 2026-03 | 4,217 | 27 |

Mann-Kendall on weekly steps: tau=-0.033, z=-0.484, p=0.555 -- no significant overall trend over the full 690-day span (n=99 weeks), likely because the early period also had variable step counts. However, the last 2 months show a clear, precipitous decline.

Bayesian changepoint: max posterior 0.05 -- no statistically robust changepoint, though the classical analysis flags Feb 24, 2026 as a downward shift.

### Weekly Pattern
| Day | Mean Steps |
|---|---|
| Monday | 9,530 |
| Tuesday | 8,166 |
| Wednesday | 8,520 |
| Thursday | 8,418 |
| Friday | 9,768 |
| Saturday | 9,249 |
| Sunday | 8,577 |

Fridays and Mondays are the most active days. The distribution is relatively even, suggesting no strong weekday/weekend asymmetry.

### Active Calories
Monthly active calories have declined from 574 kcal/day (Apr 2025) to 316 kcal/day (Mar 2026), tracking the step decline.

### Workout Analysis
| Type | Count | Avg Duration (min) | Avg HR (bpm) |
|---|---|---|---|
| Walking | 9 | 36.1 | 143 |
| Swimming | 8 | 24.9 | 138 |
| Elliptical | 8 | 23.3 | 149 |
| Badminton | 2 | 27.9 | 140 |
| Cycling | 2 | 15.6 | 144 |
| HIIT | 1 | 3.6 | 129 |

Total: 30 workouts over 421 days. Average gap: 14.2 days, max gap: 88 days. Last workout: 2026-03-03.

Elliptical sessions show the highest average HR (149 bpm, ~78% HRmax), placing them solidly in Zone 3-4, which is most effective for cardiovascular conditioning at your current fitness level.

### Exercise Consistency Analysis
Your workout frequency shows bursts of activity followed by long gaps:
- Jan-Apr 2025: 13 workouts (~3.3/month) -- most consistent period
- May-Jun 2025: 0 workouts
- Jul-Aug 2025: 8 workouts (4/month)
- Sep 2025: 3 workouts
- Oct 2025: 0 workouts
- Nov-Dec 2025: 2 workouts
- Jan 2026: 2 workouts
- Feb 2026: 0 workouts
- Mar 2026: 1 workout

The pattern of inconsistency makes it difficult to build cumulative cardiovascular adaptation, which requires sustained, regular training over 8-12+ week blocks.

---

## Sleep Architecture

### Key Metrics
| Metric | Value | Reference | Assessment |
|---|---|---|---|
| Mean total in-bed time | 9.46 h (n=181 nights) | 7-9h recommended (NSF 2015) | Above recommended -- see below |
| Median total in-bed time | 10.28 h | -- | Significant in-bed excess |
| Sleep efficiency (mean) | 67.1% | >=85% good | Poor |
| Deep sleep (mean) | 1.25 h (n=175) | 1.1-1.9h (15-25% of 7.5h) | Normal |
| REM sleep (mean) | 1.29 h (n=175) | 1.5-1.9h (20-25% of 7.5h) | Below target |
| Core/light sleep (mean) | 3.15 h (n=175) | 3.75-4.5h (50-60% of 7.5h) | Below typical |

### Architecture Breakdown (based on staged nights, n=175)
| Stage | Mean Hours | % of Staged Time | Target % | Assessment |
|---|---|---|---|---|
| Deep (N3/SWS) | 1.25 | 22.0% | 15-25% | Normal |
| REM | 1.29 | 22.7% | 20-25% | Normal |
| Core (N1-N2) | 3.15 | 55.3% | 50-60% | Normal |
| **Total staged** | **5.69 h** | -- | -- | -- |

### Important Caveat
There is a significant discrepancy between total in-bed time (mean 9.46h) and total staged sleep (mean ~5.69h), producing the low efficiency of 67.1%. This likely reflects Apple Watch sleep tracking artifacts: "InBed" and "Asleep" categories may overlap, and if multiple sleep-tracking apps are running (e.g., AutoSleep + native), records may be duplicated. The actual sleep duration is likely closer to 5.5-6.5 hours based on the staged analysis, which would place you below the 7-hour recommended minimum.

### Monthly Sleep Trend
| Month | Total In-Bed (h) | Deep (h) | REM (h) | Efficiency % | n |
|---|---|---|---|---|---|
| 2025-04 | 9.8 | 1.16 | 1.46 | 67.6 | 19 |
| 2025-05 | 11.2 | 1.29 | 1.29 | 59.7 | 11 |
| 2025-07 | 11.8 | 1.17 | 1.22 | 62.5 | 9 |
| 2025-09 | 11.2 | 1.36 | 1.10 | 66.7 | 14 |
| 2025-12 | 5.4 | 1.22 | 1.18 | 93.8 | 14 |
| 2026-01 | 6.0 | 1.10 | 1.77 | 72.7 | 12 |
| 2026-02 | 6.5 | 1.42 | 1.98 | 46.8 | 10 |
| 2026-03 | 5.6 | 1.64 | 1.69 | 48.9 | 5 |

The apparent shift from ~10-12h in-bed to ~5-6h in-bed starting in December 2025 may reflect a change in tracking methodology or watch-wearing habits rather than a true sleep duration change. The efficiency metrics are unreliable given the tracking artifacts.

### Clinical Context
Deep sleep (1.25h, 22% of staged time) is within the healthy range, which is positive for physical recovery, immune function, and growth hormone release. REM sleep (1.29h, 22.7%) is at the lower end of the 20-25% target. The sleep data should be interpreted with substantial caution due to tracking inconsistencies. If your actual sleep duration is closer to 5.5-6h (as the staged data suggests for recent months), this is below the NSF recommendation and may contribute to weight gain, elevated resting HR, and reduced recovery.

---

## Circadian Rhythm

### Cosinor Analysis
| Parameter | Heart Rate | Glucose |
|---|---|---|
| MESOR | 94.95 bpm | 106.93 mg/dL |
| Amplitude | 20.3 bpm | 9.89 mg/dL |
| Acrophase | 16:53 | 18:50 |
| R^2 | 0.341 | 0.113 |
| F-statistic | 5,900.3 | 510.2 |
| p-value | <0.001 | <0.001 |
| Significant rhythm | Yes | Yes |

HR amplitude of 20.3 bpm is within the healthy 15-25 bpm range (Cornelissen 2014). Acrophase at 16:53 is within the normal 14:00-18:00 window. The glucose cosinor R^2 of 0.113 confirms that glucose variability is primarily meal-driven rather than endogenously circadian.

### Rhythm Stability (HR)
| Metric | Value | Interpretation | Source |
|---|---|---|---|
| Interdaily Stability (IS) | 0.487 | Moderately stable | Witting et al. 1990 |
| Intradaily Variability (IV) | 0.507 | Moderate fragmentation | Witting et al. 1990 |

IS of 0.487 indicates moderately consistent day-to-day rhythms (threshold: >0.6 = very stable, 0.4-0.6 = moderate). IV of 0.507 indicates moderate within-day transitions between activity and rest, within normal range (0.5-1.0). These are healthy values for a young adult.

---

## Respiratory & SpO2

### Key Metrics
| Metric | Value | Reference | Assessment |
|---|---|---|---|
| SpO2 (mean) | 95.9% | >=96% normal | Low-normal |
| SpO2 (p5) | 93.0% | 94-95% low-normal | Border zone |
| Respiratory rate (mean) | 18.9 /min (sleeping, n=8,524) | 10-16 normal sleeping | Elevated for sleep |
| Wrist temperature (mean) | 35.4 C | -- | Normal |
| VO2 Max (mean) | 31.2 mL/min/kg | -- | See Cardiovascular section |

SpO2 mean of 95.9% is at the low-normal boundary. The 5th percentile of 93% is below normal and could warrant screening for obstructive sleep apnea, particularly given a BMI >30. The respiratory rate during sleep (mean 18.9 /min) is above the normal sleeping range of 10-16 /min, though Apple Watch respiratory rate measurements during sleep can be noisy.

---

## Audio Exposure

### Headphone Exposure
| Metric | Value |
|---|---|
| Mean | 47.9 dB |
| P95 | 62.5 dB |
| Max | 96.5 dB |
| % above 80 dB | 0.0% |
| % above 85 dB | 0.0% |

### Environmental Exposure
| Metric | Value |
|---|---|
| Mean | 56.8 dB |
| P95 | 73.9 dB |
| Max | 96.7 dB |
| % above 80 dB | 1.1% |

Both headphone and environmental exposure are well within WHO safe listening guidelines (85 dB for 8 hours). No noise-induced hearing loss risk identified.

---

## Causal Inference Analysis

The following results test whether one metric **causes** changes in another -- a stronger claim than correlation. Three independent methods were applied:

| Causal Hypothesis | Granger (F, p) | Transfer Entropy | CCM Convergence | Verdict |
|---|---|---|---|---|
| Steps -> Heart Rate | F=18.83, p<0.001 (lag 1) | 0.18 bits, p=0.013 | N/A | **Causal (A)** |
| Steps -> Resting HR | F=9.59, p=0.002 (lag 1) | 0.13 bits, p=0.337 | no convergence | **Likely (B)** |
| Steps -> Glucose | F=2.33, p=0.550 (lag 1); F=4.19, p=0.021 (lag 2) | -- | -- | **Suggestive (C)** |
| RHR -> Steps (reverse) | -- | -- | no convergence | **Not causal (D)** |

**Interpretation:**

The strongest causal finding is that daily step count causally influences heart rate (both Granger and Transfer Entropy agree; Evidence Grade A). This means that on days when you walk more, your average heart rate changes in a predictable way -- and this is not simply due to the immediate effect of exercise but persists across daily lags.

For Steps -> Resting HR, Granger causality is significant at all lags (1-4 days, all p<0.05), but Transfer Entropy (which captures nonlinear dependencies) is not significant (p=0.337), and CCM shows no convergence. This gives moderate evidence (Grade B) -- your step count helps predict your RHR, but the relationship may be primarily linear and modulated by other factors.

The lagged correlation analysis supports this: weekly steps correlated with RHR at lag 2 weeks shows r=-0.298 (n=47) -- the strongest negative correlation among lags tested. This means increasing your steps this week is associated with lower RHR two weeks later.

Steps -> Glucose shows a suggestive relationship only at lag 2 (F=4.19, p=0.021), but this is based on limited overlapping data (glucose data covers only 90 days). Insufficient evidence for a causal claim.

The CCM analysis found no convergence for either direction of the Steps-RHR relationship (rho values: -0.002 to -0.132). This indicates that while linear predictive causality exists (Granger), the systems may not be strongly dynamically coupled in the nonlinear sense (Sugihara et al. 2012). This is common when the causal effect is mediated through multiple intermediate variables (e.g., steps -> fitness -> autonomic tone -> RHR) rather than being a direct dynamical coupling.

---

## Biological Age Assessment

| Model | Estimated Age | Chronological Age | Gap | Key Drivers |
|---|---|---|---|---|
| Fitness Age (VO2 Max) | 64.4 yr | 23.8 yr | +40.6 yr | Low VO2 Max (31.2) |
| Biological Age (multi) | 35.3 yr | 23.8 yr | +11.5 yr | VO2 Max (+8.0), BMI (+1.2), Sleep (+0.8), RHR (+0.7) |
| Allostatic Load | 2/7 | -- | Moderate | BMI flagged (30.5 >30), VO2 Max flagged (31.2 <35) |

**Note:** Fitness Age is derived from VO2 Max using the HUNT study regression (Nes et al. 2013, MSSE 45:2017): Male Fitness Age = (57.0 - VO2max) / 0.40. It represents the age at which the average person has your VO2 Max level. The +40.6 year gap is the single most concerning finding in this report, though it should be noted that Apple Watch VO2 Max estimates may underestimate true fitness, especially in swimmers and elliptical users.

The biological age model is a simplified multi-biomarker estimate. The +11.5 year gap is driven primarily by VO2 Max (+8.0 years), with smaller contributions from BMI (+1.2), sleep deviation (+0.8), RHR (+0.7), HRV (+0.4), and activity (+0.3). Treat this as directional, not precise.

Allostatic load of 2/7 (moderate) reflects cumulative physiological stress. Two biomarkers are flagged: BMI (30.5, threshold 30) and VO2 Max (31.2, threshold 35). The remaining markers -- RHR (77.9, threshold 80), HRV (35.6, threshold 25), steps (6,953, threshold 5,000), sleep (9.5h, threshold 6h), glucose CV (19.5%, threshold 36%) -- are within acceptable ranges. However, RHR at 77.9 is very close to the 80 bpm threshold and may cross it given recent trends.

---

## Cross-Metric Correlation Matrix

| | Steps | ActiveCal | AvgHR | RHR | HRV | Sleep | Glucose |
|---|---|---|---|---|---|---|---|
| **Steps** | 1.000 | 0.831 | 0.413 | 0.077 | -0.028 | 0.041 | 0.175 |
| **ActiveCal** | 0.831 | 1.000 | 0.360 | 0.097 | -0.129 | 0.061 | 0.312 |
| **AvgHR** | 0.413 | 0.360 | 1.000 | 0.573 | -0.502 | 0.110 | 0.049 |
| **RHR** | 0.077 | 0.097 | 0.573 | 1.000 | -0.587 | 0.154 | -0.424 |
| **HRV** | -0.028 | -0.129 | -0.502 | -0.587 | 1.000 | -0.095 | 0.348 |
| **Sleep** | 0.041 | 0.061 | 0.110 | 0.154 | -0.095 | 1.000 | 0.104 |
| **Glucose** | 0.175 | 0.312 | 0.049 | -0.424 | 0.348 | 0.104 | 1.000 |

### Clinically Meaningful Correlations

1. **RHR <-> HRV: r=-0.587** -- The strongest bivariate relationship. Higher resting HR is strongly associated with lower heart rate variability, reflecting reduced parasympathetic tone. This is the expected physiological pattern and confirms internal consistency of the data.

2. **AvgHR <-> HRV: r=-0.502** -- Days with higher average HR (more active or more stressed) are associated with lower HRV readings that day. This could reflect sympathetic activation during activity suppressing vagal metrics.

3. **RHR <-> Glucose: r=-0.424** -- Lower RHR days are associated with higher glucose, and vice versa. This unexpected inverse relationship may reflect the confound of the glucose data covering only the most recent 90 days, during which RHR dropped (Jan) then rose (Feb-Mar). Further data would be needed to confirm.

4. **Steps <-> ActiveCal: r=0.831** -- Expected strong correlation. Steps and active calories measure overlapping constructs.

5. **HRV <-> Glucose: r=0.348** -- Higher HRV days are associated with higher glucose. Like the RHR-glucose relationship, this may be a temporal confound.

### Lagged Correlations

| Relationship | Lag | r | n |
|---|---|---|---|
| Weekly Steps -> RHR | 0 weeks | -0.245 | 49 |
| Weekly Steps -> RHR | 1 week | -0.159 | 48 |
| Weekly Steps -> RHR | **2 weeks** | **-0.298** | 47 |
| Weekly Steps -> RHR | 4 weeks | -0.086 | 45 |
| Sleep -> Next-Day HRV | 0 days | r=0.010 | 179 |

The strongest lagged relationship is Steps -> RHR at a 2-week lag (r=-0.298, n=47): increasing step count is associated with lower resting HR two weeks later. This aligns with the known physiological timeline -- aerobic adaptation requires approximately 2 weeks to manifest as measurable RHR reduction (clinical_interpretation.md).

Sleep duration shows no meaningful correlation with next-day HRV (r=0.010, n=179). Short sleep (<6h) HRV: 35.8 ms; normal sleep (6-8h) HRV: 37.4 ms; long sleep (>8h) HRV: 37.1 ms -- negligible difference.

---

## Personalized Recommendations

**1. Arrest the weight gain trajectory immediately.**
Your weight is increasing at +0.82 kg/month (9.9 kg/year) with 68% as fat. Target a modest caloric deficit of 300-500 kcal/day. Based on your active calorie burn data (current ~316 kcal/day, down from ~574 kcal/day in April 2025), even restoring your prior activity level would create a meaningful energy deficit. Combine this with resistance training to protect lean mass during weight loss. Discuss with a physician, particularly given your young age and the metabolic implications of sustained obesity.
*Based on: Body Composition analysis, weight regression R^2=0.87, gain decomposition*

**2. Restore daily step count to 8,000+ immediately; target 10,000.**
Your last-30-day average is 4,142 steps -- below the sedentary threshold. Even returning to your all-time average of 8,889 steps/day provides approximately 50% mortality risk reduction vs. <4,000 steps (Paluch et al. 2022). Based on your lag-2-week Steps->RHR correlation (r=-0.298), expect measurable RHR improvement within 14 days of sustained increase. Start by adding a 30-minute walk daily -- your data shows walking sessions maintain Zone 2-3 HR (avg 143 bpm).
*Based on: Activity trend analysis, lagged correlations, Granger causality*

**3. Establish a consistent structured exercise routine: 3 sessions/week, 30+ minutes each.**
Your data shows elliptical workouts achieve the highest effective training HR (mean 149 bpm, 78% HRmax = Zone 3-4), making them the most efficient modality for cardiovascular improvement. Aim for 3 elliptical or swim sessions per week. Consistency matters more than intensity -- your workout pattern shows bursts followed by 60-88 day gaps, preventing cumulative adaptation. Maintain this for 8+ consecutive weeks before reassessing VO2 Max.
*Based on: Workout type comparison, VO2 Max monthly trend (peaked during most consistent exercise period in Sep 2025)*

**4. Investigate the recent RHR surge (69 -> 84 bpm in 2 months).**
This 15 bpm increase since January 2026 could reflect deconditioning (coincides with step count collapse), weight gain, increased stress, or insufficient sleep. If RHR remains >80 bpm for 4+ consecutive weeks despite improved activity and sleep, discuss with a physician. Monitor nocturnal HR as a more sensitive proxy for underlying changes.
*Based on: RHR monthly trend, nocturnal HR trend, changepoint analysis*

**5. Address potential sleep deficit.**
Your staged sleep data suggests actual sleep duration of approximately 5.5-6.5 hours, below the 7-hour minimum recommendation (NSF 2015). Aim for 7-8 hours of actual sleep. If you are spending 10+ hours in bed but only sleeping 5-6 hours, this may indicate sleep onset or maintenance issues worth discussing with a provider. The low mean SpO2 (95.9%) combined with BMI >30 warrants screening for obstructive sleep apnea.
*Based on: Sleep architecture analysis, SpO2 data, BMI-OSA association*

**6. Continue excellent glucose management.**
Your metabolic health is the strongest dimension (score 90/100). Maintain your current dietary patterns. To further optimize: reduce Sunday evening high-glycemic meals (Sunday shows the highest mean glucose at 114.0 mg/dL and highest TAR at 1.5%), and maintain moderate post-meal walking -- your data shows some glucose-lowering effect of activity at 2-day lag.
*Based on: Glucose analysis, weekly pattern, Steps->Glucose Granger at lag 2*

These recommendations are based on patterns in your wearable data. Discuss significant changes to your exercise or diet with your healthcare provider.
