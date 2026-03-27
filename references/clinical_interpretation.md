# Clinical Interpretation Reference

Evidence-based reference ranges for interpreting Apple Health analytics output. All ranges cite source literature. Always contextualize by the user's age and sex.

## Table of Contents
1. Cardiovascular — Resting HR, HR Zones, HR Recovery, Day-Night Ratio
2. Heart Rate Variability — SDNN, Poincaré SD1/SD2, DFA Alpha
3. VO2 Max & Cardiorespiratory Fitness
4. Blood Glucose (CGM) — TIR, Variability, Risk Indices
5. Body Composition — BMI, Body Fat, Weight Trajectory
6. Sleep — Duration, Architecture, Efficiency
7. Activity — Steps, Exercise, WHO Guidelines
8. Nonlinear Dynamics — Sample Entropy, Multiscale Entropy
9. Circadian Rhythm — Cosinor, IS/IV
10. Causal Inference — Interpreting Granger, TE, CCM
11. Composite Models — Biological Age, Fitness Age, Allostatic Load
12. Audio Exposure
13. Respiratory — SpO2, Respiratory Rate

---

## 1. Cardiovascular

### Resting Heart Rate (bpm)
Source: Palatini 1999, J Hypertens; Fox et al. 2007, CMAJ

| Range | Rating | Clinical Significance |
|-------|--------|----------------------|
| <50 | Bradycardia | Normal in trained athletes; otherwise evaluate |
| 50-59 | Excellent | Strong parasympathetic tone |
| 60-69 | Good | Healthy, well-conditioned |
| 70-79 | Average | Room for improvement through aerobic training |
| 80-89 | Above average | Associated with increased cardiovascular risk |
| ≥90 | Elevated | Independent predictor of cardiovascular mortality (Fox 2007) |

RHR >80 bpm is an independent predictor of all-cause mortality even after adjusting for physical activity (Cooney et al. 2010, Eur Heart J). Each 10 bpm increase above 60 is associated with ~20% increase in mortality risk.

Training effect: expect ~1 bpm reduction per week of consistent aerobic exercise (first 4-8 weeks), with 2-week lag for visible change.

### Heart Rate Zones
Based on Tanaka formula for Max HR: **208 - 0.7 × age** (Tanaka et al. 2001, JACC)

| Zone | %HRmax | Physiological Effect |
|------|--------|---------------------|
| Zone 1 (50-60%) | Recovery | Active recovery, minimal cardiovascular stress |
| Zone 2 (60-70%) | Aerobic base | Peak fat oxidation (Achten 2002), mitochondrial biogenesis |
| Zone 3 (70-80%) | Tempo | Aerobic capacity development, lactate clearance |
| Zone 4 (80-90%) | Threshold | Anaerobic threshold, VO2 Max improvement |
| Zone 5 (90-100%) | Maximum | Neuromuscular power, short-burst capacity |

WHO target: ≥150 min/week Zone 2-3 OR ≥75 min/week Zone 4+ (WHO 2020 Guidelines)

### Heart Rate Recovery
Post-exercise HR recovery is a predictor of autonomic function and mortality (Cole et al. 1999, NEJM):
- HRR1 (drop in 1 min post-exercise): ≤12 bpm = abnormal, >12 bpm = normal
- HRR2 (drop in 2 min): ≤22 bpm = abnormal
- Wearable approximation: compare mean HR during final 5 min of workout vs 15 min post-workout. If still elevated well above pre-workout baseline, recovery is impaired.

### Day-Night HR Ratio (Circadian Index)
Source: Mancia et al. 1983, Hypertension; Hermida et al. 2013, Chronobiol Int

| Ratio | Pattern | Clinical Notes |
|-------|---------|---------------|
| <1.10 | Non-dipping (reverse) | Associated with increased CV risk, secondary hypertension |
| 1.10-1.19 | Non-dipping | Evaluate for sleep apnea, autonomic neuropathy |
| 1.20-1.59 | Normal dipping | Healthy circadian modulation |
| ≥1.60 | Extreme dipping | Usually benign; may indicate orthostatic hypotension |

### Nocturnal HR
Lowest physiological point: 3-5 AM (vagal predominance). Monthly trend of nocturnal HR is a sensitive proxy for:
- Training status (decreases with aerobic fitness)
- Weight change (increases with weight gain)
- Chronic stress (sustained elevation)
- Overtraining (paradoxical increase despite more training)

---

## 2. Heart Rate Variability

### SDNN (ms)
Source: Shaffer & Ginsberg 2017, Front Public Health; Task Force 1996, Circulation

| Age | Excellent | Good | Average | Low | Very Low |
|-----|-----------|------|---------|-----|----------|
| 18-25 | >65 | 45-65 | 30-45 | 20-30 | <20 |
| 25-35 | >55 | 40-55 | 25-40 | 15-25 | <15 |
| 35-50 | >45 | 30-45 | 20-30 | 12-20 | <12 |
| 50-65 | >40 | 25-40 | 15-25 | 10-15 | <10 |

SDNN reflects total variability (both sympathetic and parasympathetic). Lower SDNN = increased all-cause mortality (Tsuji et al. 1996, Circulation).

### Poincaré Plot Analysis
Source: Brennan et al. 2001, IEEE Trans Biomed Eng; Toichi et al. 1997

| Metric | Physiological Meaning | Interpretation |
|--------|----------------------|----------------|
| SD1 | Short-term variability (beat-to-beat, parasympathetic) | Low SD1 = reduced vagal tone |
| SD2 | Long-term variability (sympathetic + parasympathetic) | Low SD2 = overall autonomic depression |
| SD1/SD2 ratio | Sympathovagal balance | <0.5 = sympathetic dominant; 0.5-1.5 = balanced; >1.5 = parasympathetic dominant |
| CSI (SD2/SD1) | Cardiac Sympathetic Index | >3.0 = sympathetic overactivity |
| CVI (log(SD1×SD2)) | Cardiac Vagal Index | Higher = better vagal function |

### DFA Alpha Exponent
Source: Peng et al. 1994, Phys Rev E; Goldberger et al. 2002, PNAS

| Alpha | Pattern | Clinical Significance |
|-------|---------|----------------------|
| <0.5 | Anti-correlated | Abnormal; potentially pathological |
| 0.5 | White noise | Uncorrelated; loss of fractal structure |
| 0.75-1.05 | 1/f noise | **Healthy** — indicates complex, adaptive regulation |
| 1.0 | Ideal 1/f | Optimal cardiac complexity |
| 1.5 | Brownian motion | Over-correlated; loss of adaptability |
| >1.5 | Strong correlation | Pathological rigidity (seen in heart failure) |

Healthy young adults: α ≈ 1.0 (Peng 1994). Aging and disease shift α away from 1.0 in either direction. Loss of fractal complexity = reduced adaptability to physiological demands.

Note: DFA computed on daily HR means (as in our script) will differ from beat-to-beat DFA. Daily-mean DFA reflects longer-term regulatory dynamics.

---

## 3. VO2 Max & Cardiorespiratory Fitness

Source: ACSM 2021, Guidelines for Exercise Testing; Cooper Clinic normative data; Nes et al. 2013, MSSE

### Percentile Table (mL/min/kg)
| Percentile | 20-29 M | 20-29 F | 30-39 M | 30-39 F | 40-49 M | 40-49 F |
|------------|---------|---------|---------|---------|---------|---------|
| 95th | >56 | >49 | >54 | >45 | >52 | >43 |
| 75th | 48-56 | 41-49 | 45-54 | 38-45 | 42-52 | 36-43 |
| 50th | 42-48 | 37-41 | 39-45 | 34-38 | 36-42 | 32-36 |
| 25th | 37-42 | 33-37 | 35-39 | 30-34 | 32-36 | 28-32 |
| 5th | <37 | <33 | <35 | <30 | <32 | <28 |

### Fitness Age
Source: Nes et al. 2013, MSSE 45(11):2017 — HUNT study (N=37,000)

Formula: Fitness Age = age at which the population average VO2 Max matches your value.
- Male: Fitness Age ≈ (57.0 - VO2max) / 0.40
- Female: Fitness Age ≈ (48.0 - VO2max) / 0.35

Interpretation:
- Fitness Age < Chronological Age - 5: Excellent fitness for age
- Within ±5 years: Age-appropriate
- Fitness Age > Chronological Age + 5: Below expected; intervention warranted
- Fitness Age > Chronological Age + 20: Significantly impaired; clinical evaluation recommended

Apple Watch limitation: VO2 Max estimated from walking/running workouts only. Swimmers and cyclists may be underestimated.

---

## 4. Blood Glucose (CGM)

### Time-in-Range (International Consensus)
Source: Battelino et al. 2019, Diabetes Care 42(8):1593-1603

| Metric | Target (Type 1) | Target (Type 2) | Target (Non-diabetic) |
|--------|-----------------|------------------|-----------------------|
| TIR 70-180 mg/dL | >70% | >70% | >96% (Vigersky 2019) |
| TBR <70 mg/dL | <4% | <4% | <4% |
| TBR <54 mg/dL | <1% | <1% | <1% |
| TAR >180 mg/dL | <25% | <25% | <1% |
| TAR >250 mg/dL | <5% | <5% | 0% |

Note: Non-diabetic CGM users typically achieve TIR >96% (Shah et al. 2019, J Clin Endocrinol). TIR 90-96% in non-diabetics may suggest pre-diabetic glucose patterns.

### Glycemic Variability Metrics
| Metric | Formula/Method | Normal | Elevated | High | Source |
|--------|---------------|--------|----------|------|--------|
| CV% | SD/mean × 100 | <36% (stable) | 36-50% | >50% (unstable) | Monnier et al. 2017 |
| MAGE | Mean amplitude of glycemic excursions >1 SD | <40 mg/dL | 40-60 | >60 | Service et al. 1970 |
| MODD | Mean of daily glucose differences at same time | <20 mg/dL | 20-30 | >30 | Molnar et al. 1972 |
| J-Index | 0.001 × (mean + SD)² | <20 | 20-30 | >30 | Wójcicki 1995 |
| GRI | Weighted hypo+hyper risk | Zone A (0-20) | Zone B-C | Zone D-E (>60) | Klonoff et al. 2023 |

### Kovatchev Glucose Risk Indices
Source: Kovatchev et al. 2002, Diabetes Care 25:2058-2064; Kovatchev 2006, DTT 8:644-653

**LBGI (Low Blood Glucose Index)** — quantifies hypoglycemia risk:
| LBGI | Risk Level | Clinical Action |
|------|-----------|-----------------|
| <1.1 | Minimal | No concern |
| 1.1-2.5 | Low | Monitor |
| 2.5-5.0 | Moderate | Evaluate hypoglycemia causes |
| >5.0 | High | Urgent review |

**HBGI (High Blood Glucose Index)** — quantifies hyperglycemia risk:
| HBGI | Risk Level |
|------|-----------|
| <4.5 | Minimal |
| 4.5-9.0 | Low |
| 9.0-18.0 | Moderate |
| >18.0 | High |

**ADRR (Average Daily Risk Range)** — composite daily risk:
| ADRR | Risk |
|------|------|
| <20 | Low risk |
| 20-40 | Moderate risk |
| >40 | High risk |

### CONGA Reference Values
Source: McDonnell et al. 2005, DTT 7(2):253-263

Non-diabetic reference (approximate):
- CONGA-1: 15-25 mg/dL (healthy ambulatory)
- CONGA-2: 20-30 mg/dL
- CONGA-4: 25-35 mg/dL

### GVP (Glycemic Variability Percentage)
Source: Peyser et al. 2018, J Diabetes Sci Technol 12(4):718-726
- <15%: Low variability
- 15-30%: Moderate
- >30%: High variability

### GMI & eA1c
- GMI = 3.31 + 0.02392 × mean glucose (mg/dL) — Bergenstal et al. 2018, Diabetes Care
- eA1c = (mean glucose + 46.7) / 28.7 — Nathan et al. 2008
- Normal: <5.7%, Pre-diabetic: 5.7-6.4%, Diabetic: ≥6.5%

### Glucose Rate of Change
- Normal: ±1-2 mg/dL/min
- Rapid rise: >2 mg/dL/min (suggests high-GI meal)
- Rapid fall: <-2 mg/dL/min (overshoot risk, rebound hypoglycemia)

### CGM Data Quality Caveats
- Compression lows: readings <54 during sleep may be artifact from lying on sensor arm
- Warm-up period: first 12-24h after insertion may be inaccurate
- Interstitial lag: CGM reads interstitial glucose, lagging blood glucose by 5-15 min
- Calibration: some CGM systems need fingerstick calibration; uncalibrated readings may drift

---

## 5. Body Composition

### BMI (WHO Classification)
| BMI | Classification | Associated Risk |
|-----|---------------|-----------------|
| <18.5 | Underweight | Malnutrition, osteoporosis risk |
| 18.5-24.9 | Normal weight | Baseline risk |
| 25.0-29.9 | Overweight | Elevated cardiometabolic risk |
| 30.0-34.9 | Obese Class I | High risk |
| 35.0-39.9 | Obese Class II | Very high risk |
| ≥40.0 | Obese Class III | Extremely high risk |

BMI limitations: does not distinguish fat from muscle. Use alongside body fat % and lean mass. Athletes and muscular individuals may have elevated BMI without excess fat.

### Body Fat %
Source: ACSM Guidelines 2021

| Rating | Men 20-29 | Men 30-39 | Women 20-29 | Women 30-39 |
|--------|-----------|-----------|-------------|-------------|
| Essential | 2-5% | 2-5% | 10-13% | 10-13% |
| Athletic | 6-13% | 6-13% | 14-20% | 14-20% |
| Fitness | 14-17% | 14-17% | 21-24% | 21-24% |
| Average | 18-24% | 18-24% | 25-31% | 25-31% |
| Obese | >25% | >25% | >32% | >32% |

### Weight Trajectory Interpretation
- Use linear regression R² to assess trend strength: >0.7 = strong, consistent trend
- Rate >0.5 kg/month sustained = concerning if adult (past growth phase)
- Fat vs lean decomposition: healthy weight gain is ≥50% lean; if >70% fat, dietary intervention warranted
- Projection accuracy: only meaningful with R² >0.7 and ≥10 data points

---

## 6. Sleep

### Duration (National Sleep Foundation 2015)
| Age | Recommended | May Be Appropriate | Not Recommended |
|-----|-------------|--------------------|-----------------|
| 18-25 | 7-9h | 6h or 10-11h | <6h or >11h |
| 26-64 | 7-9h | 6h or 10h | <6h or >10h |

### Architecture
Source: Ohayon et al. 2004, Sleep; Hirshkowitz et al. 2015

| Stage | Typical % | Hours (7.5h sleep) | Function |
|-------|-----------|-------------------|----------|
| N1-N2 (Light/Core) | 50-60% | 3.75-4.5h | Memory encoding, basic restoration |
| N3 (Deep/SWS) | 15-25% | 1.1-1.9h | Physical recovery, growth hormone, immune function |
| REM | 20-25% | 1.5-1.9h | Emotional processing, memory consolidation, dreaming |

Deep sleep naturally declines with age (~2% per decade after 30). REM is relatively preserved.

### Sleep Efficiency
- ≥85%: Good (clinical standard for non-insomnia)
- 75-84%: Fair
- <75%: Poor — indicates significant time awake in bed

### Apple Watch Sleep Caveats
- "InBed" and "Asleep" categories may overlap → inflated totals
- Multiple apps (AutoSleep + native) can duplicate records
- Watch-off periods appear as data gaps, not zero sleep
- Deduplicate by grouping into sleep "nights" (18:00-18:00 window)

---

## 7. Activity

### Steps/Day
Source: Paluch et al. 2022, Lancet 7(3):E219 (meta-analysis, N=47,471)

| Steps/day | Mortality Risk Reduction (vs <4,000) | Category |
|-----------|--------------------------------------|----------|
| <4,000 | Reference | Sedentary |
| 4,000-5,999 | ~25% reduction | Low active |
| 6,000-7,999 | ~40% reduction | Somewhat active |
| 8,000-9,999 | ~50% reduction | Active |
| 10,000-11,999 | ~55% reduction | Very active |
| ≥12,000 | ~60% reduction (plateau) | Highly active |

Diminishing returns above ~10,000 for adults <60; above ~8,000 for adults ≥60.

### Exercise (WHO 2020)
- 150-300 min/week moderate-intensity aerobic, OR 75-150 min/week vigorous
- 2+ days/week muscle-strengthening
- Additional benefit from exceeding these targets
- Even small amounts > zero provide benefit

---

## 8. Nonlinear Dynamics

### Sample Entropy (SampEn)
Source: Richman & Moorman 2000, Am J Physiol; Costa et al. 2005

For daily HR means (m=2, r=0.2×SD):
| SampEn | Interpretation |
|--------|---------------|
| <0.5 | Very regular/predictable — potentially pathological rigidity |
| 0.5-1.0 | Low-moderate complexity |
| 1.0-2.0 | Moderate-high complexity — healthy |
| >2.0 | High complexity — healthy, rich dynamics |

For glucose (CGM, m=2, r=0.2×SD):
| SampEn | Interpretation |
|--------|---------------|
| <0.3 | Very regular — tight glucose control or limited meal variability |
| 0.3-0.8 | Normal for CGM data |
| >0.8 | High variability — chaotic glucose patterns |

### Multiscale Entropy (MSE)
Source: Costa et al. 2002, PRL 89:068102

Healthy systems show high entropy across multiple scales. Pathological states (heart failure, aging) show entropy loss preferentially at coarser scales. Plot SampEn vs scale factor — a healthy MSE curve is relatively flat or slowly declining; a steep decline suggests loss of long-range regulatory complexity.

---

## 9. Circadian Rhythm

### Cosinor Parameters
Source: Cornelissen 2014, Theor Biol Med Model 11:16

| Parameter | Definition | Typical Value (HR) |
|-----------|-----------|-------------------|
| MESOR | Rhythm-adjusted 24h mean | Close to overall mean HR |
| Amplitude | Peak-to-trough half-swing | 15-25 bpm (healthy adults) |
| Acrophase | Time of peak | 14:00-18:00 for HR |

HR amplitude <10 bpm may suggest blunted circadian rhythm (seen in aging, shift work, depression).
Acrophase outside 12:00-20:00 window may indicate circadian misalignment.

For glucose:
- Amplitude: 5-15 mg/dL (healthy); >20 may indicate meal-driven rather than endogenous rhythm
- Acrophase: typically 14:00-20:00 (post-meal driven)
- R² <0.10: weak circadian fit — glucose driven more by meals than endogenous rhythm

### Interdaily Stability (IS) / Intradaily Variability (IV)
Source: Witting et al. 1990, Biol Psychiatry

| IS | Interpretation |
|----|---------------|
| >0.6 | Very stable rhythm (strong day-to-day consistency) |
| 0.4-0.6 | Moderately stable |
| <0.4 | Unstable (irregular schedule, shift work, jet lag) |

| IV | Interpretation |
|----|---------------|
| <0.5 | Smooth, consolidated rhythm |
| 0.5-1.0 | Moderate fragmentation |
| >1.0 | Highly fragmented (frequent rest-activity transitions; seen in dementia, depression) |

---

## 10. Causal Inference Interpretation

### Granger Causality
Source: Granger 1969, Econometrica 37(3):424
- Tests if past values of X improve prediction of Y beyond Y's own history
- **Causal ≠ mechanistic**: Granger causality is predictive causality, not mechanism
- Significant (p<0.05) at any lag: X Granger-causes Y
- Optimal lag: the lag with lowest p-value indicates the time delay of causal effect
- Bidirectional: test both X→Y and Y→X to detect feedback loops

### Transfer Entropy
Source: Schreiber 2000, PRL 85(2):461
- Measures directed information flow in bits
- Captures nonlinear dependencies that Granger misses
- Significant TE(X→Y) with non-significant TE(Y→X): unidirectional causal flow
- Use shuffle significance test (p<0.05)

### Convergent Cross Mapping (CCM)
Source: Sugihara et al. 2012, Science 338(6106):496
- Tests dynamical coupling between systems
- **Key signature**: prediction skill (ρ) increases with library size L = convergence
- ρ >0.3 with convergence: moderate causal evidence
- ρ >0.5 with convergence: strong evidence
- No convergence: no evidence of dynamical coupling
- CCM can detect causality even in strongly coupled, nonlinear systems where Granger fails

### Triangulation
When all three methods agree (significant Granger + significant TE + CCM convergence): **Strong causal evidence (Grade A)**
When two agree: **Moderate evidence (Grade B)**
When only one is significant: **Suggestive (Grade C)**
When none: **No evidence of causal relationship (Grade D)**

---

## 11. Composite Models

### Biological Age
Multi-biomarker estimate based on Levine 2013 concept, adapted for wearable biomarkers. Components:
- RHR contribution: each bpm above population norm ≈ +0.12 years (capped ±3)
- HRV contribution: below expected for age ≈ +years (capped ±3)
- VO2 Max contribution: via fitness age, weighted ×0.25 (capped ±8)
- BMI contribution: each point above 24.5 ≈ +0.2 years (capped ±4)
- Activity contribution: steps deviation from 8,000 (capped ±3)
- Sleep contribution: deviation from 7.5h optimal (capped ±2)

**Interpret as directional, not precise.** Bio Age gap >5 years = meaningful; >10 years = significant concern.

### Allostatic Load
Source: McEwen 1998, NEJM 338:171 (concept); Seeman et al. 2001, PNAS

Count of biomarkers in "high risk" zone:
| Score | Risk Level |
|-------|-----------|
| 0-1 | Low allostatic load |
| 2-3 | Moderate — some physiological stress accumulation |
| 4+ | High — significant cumulative wear and tear |

---

## 12. Audio Exposure

### WHO Safe Listening
Source: WHO 2022, Global Standard for Safe Listening

| Duration | Max dB |
|----------|--------|
| 8h | 85 dB |
| 4h | 88 dB |
| 2h | 91 dB |
| 1h | 94 dB |
| 15 min | 100 dB |

Sustained >85 dB: risk of noise-induced hearing loss.
Apple Watch measures environmental and headphone exposure separately.

---

## 13. Respiratory

### SpO2
| Level | Interpretation |
|-------|---------------|
| ≥96% | Normal |
| 94-95% | Low-normal (acceptable at altitude >1500m) |
| 90-93% | Below normal — evaluate for respiratory pathology |
| <90% | Hypoxemia — urgent evaluation |

Nocturnal SpO2 dips <90%: screen for obstructive sleep apnea, especially with BMI >30.

### Respiratory Rate (resting/sleeping)
| Rate | Interpretation |
|------|---------------|
| 12-20 /min | Normal (awake) |
| 10-16 /min | Normal (sleeping) |
| >20 (rest) | Tachypnea — may indicate anxiety, fever, pain, respiratory condition |
| <10 (awake) | Bradypnea — unusual, evaluate |
