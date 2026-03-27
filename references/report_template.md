# Report Template — Clinical Health Assessment

Follow this structure exactly. Skip sections whose data is absent or has `reliability: "insufficient"`. Never invent content for missing sections — instead list them in the Data Availability table.

## Report Header

```
# Comprehensive Health Assessment Report
**Data Source**: Apple Health Export
**Analysis Date**: [today]
**Data Period**: [first date] — [last date] ([N] days)
**Subject**: [age] year-old [sex], [height if available]
**Methods Applied**: [N] statistical methods from [N] peer-reviewed publications

> **Disclaimer**: This report is generated from consumer wearable data for informational
> purposes only. It does not constitute medical advice. Consult a licensed healthcare
> provider before making health decisions based on this report.
```

---

## Section 0: Executive Summary (always first)

Write 3-5 bullet points summarizing the most important findings. Each bullet should be a complete insight, not a label. Lead with the most clinically significant finding.

**Format each bullet as:**
- [Finding in plain language] ([key metric], **Evidence: [A/B/C]**)

Example:
- Your cardiovascular fitness is significantly below age expectations, with a VO2 Max equivalent to a 64-year-old (VO2 Max 31.2 mL/min/kg, 15th percentile for 23M; **Evidence: A**)
- Weight has increased 18 kg over 21 months with no sign of plateauing (linear R²=0.87, +0.82 kg/month; **Evidence: A**)

---

## Section 1: Health Dashboard

Present as a table with ALL available dimensions. Use this exact format:

```
| Dimension              | Score | Grade | Key Metric                        | Trend    |
|------------------------|-------|-------|-----------------------------------|----------|
| Metabolic Health       | 90    | A     | TIR 97.8%, eA1c 5.4%             | →        |
| Resting Heart Rate     | 60    | C     | Mean 78 bpm (target: <70)         | ↑ worse  |
| ...                    | ...   | ...   | ...                               | ...      |
| **OVERALL**            | **47**| **D+**|                                   |          |
```

After the table, add one sentence: "This score reflects [N] of 8 possible dimensions. [List any missing dimensions and why.]"

---

## Section 2: Data Availability & Quality

Present as a table — this is essential for transparency:

```
| Data Type          | Records  | Coverage | Span              | Reliability | Notes                    |
|--------------------|----------|----------|-------------------|-------------|--------------------------|
| Heart Rate         | 159,427  | 94%      | 2024-05 — 2026-03 | High        |                          |
| Blood Glucose (CGM)| 8,040    | 90 days  | [start] — [end]   | High        | [CGM device name]        |
| Sleep              | 7,038    | 48%      | 2025-01 — 2026-03 | Moderate    | Gaps in tracking         |
| VO2 Max            | 25       | —        | 2025-01 — 2026-01 | Moderate    | Sparse; trend limited    |
| Body Weight        | 25       | —        | 2024-05 — 2026-02 | Low         | Infrequent measurements  |
| *(not available)*  |          |          |                   |             |                          |
| Blood Pressure     | 0        | —        | —                 | —           | Not collected            |
| ECG Interpretation | —        | —        | —                 | —           | Raw data only, no Dx     |
```

Below the table, list which advanced analyses could NOT be performed due to missing data.

---

## Section 3: Critical Findings & Risk Stratification

Present risk flags grouped by severity. Use visual markers:

```
### HIGH RISK
🔴 **[Title]** — [one-line explanation]
- Data: [specific numbers with units]
- Clinical significance: [why this matters, citing reference ranges]
- Evidence grade: [A/B/C]
- Recommended action: [specific, actionable]

### MODERATE RISK
🟡 **[Title]** — ...

### POSITIVE FINDINGS
🟢 **[Title]** — ...
```

Always include positive findings — not just problems. If metabolic health is excellent, say so.

---

## Section 4+: Dimension Deep Dives

For each dimension with sufficient data, use this structure:

```
## [Dimension Name]

### Key Metrics
| Metric | Value | Reference Range | Percentile | Assessment |
|--------|-------|-----------------|------------|------------|
| ...    | ...   | ...             | ...        | ...        |

### Temporal Trend
[Monthly trend table or description]
[Mann-Kendall result if available: "tau=X, p=Y — [significant/not significant] [direction] trend"]

### Patterns
[Circadian, weekly, seasonal patterns if applicable]

### Clinical Context
[1-2 paragraphs interpreting the metrics in the context of the user's age, sex, and other metrics.
 Connect to other dimensions where relevant. Cite specific papers for non-obvious claims.]

### Advanced Analytics (if available)
[Nonlinear dynamics, causal inference, or other advanced results for this dimension]
```

### Dimension Order (by clinical priority):
1. **Body Composition & Anthropometrics** — weight trajectory with linear regression projection, BMI, body fat decomposition (lean vs fat gain), Mann-Kendall trend significance
2. **Cardiovascular Function** — resting HR (monthly trend), HR zones (% time in each), VO2 Max (percentile for age/sex), walking HR, exercise HR recovery analysis
3. **Autonomic Nervous System** — HRV SDNN stats, Poincaré plot (SD1/SD2/ratio — sympathovagal balance), nocturnal HR trend (parasympathetic recovery proxy), day/night HR ratio (dipping pattern)
4. **Metabolic / Glucose** — Full CGM panel: TIR (international consensus targets), GMI, eA1c, MAGE, MODD, CV%, J-index, GRI, LBGI/HBGI (Kovatchev), ADRR, CONGA-1/2/4h, GVP, glucose rate of change. Circadian glucose curve. Weekly pattern. Glucose-exercise interaction.
5. **Nonlinear Dynamics & Complexity** — Sample Entropy (HR and glucose), DFA alpha, Multiscale Entropy profile. These are presented as a dedicated subsection because they require specialized interpretation.
6. **Activity & Exercise** — Daily steps (stats + trend), workout analysis (type comparison, HR during, recovery), activity rings, weekly pattern, exercise consistency
7. **Sleep Architecture** — Total duration, deep/REM/core breakdown, efficiency, nightly timeline, monthly trend
8. **Circadian Rhythm** — Cosinor (MESOR, amplitude, acrophase for HR and glucose), Interdaily Stability, Intradaily Variability
9. **Respiratory & SpO2** — Blood oxygen, respiratory rate, wrist temperature
10. **Audio Exposure** — Headphone and environmental noise risk assessment

---

## Section N-3: Causal Inference Analysis

This section presents CAUSAL (not just correlational) findings from three independent methods. Frame it clearly:

```
## Causal Inference Analysis

The following results test whether one metric **causes** changes in another —
a stronger claim than correlation. Three independent methods were applied:

| Causal Hypothesis         | Granger (F, p)     | Transfer Entropy | CCM Convergence | Verdict        |
|---------------------------|--------------------|------------------|-----------------|----------------|
| Steps → Heart Rate        | F=18.8, p<0.001 ✓  | 0.18 bits, p=0.01 ✓ | weak           | **Causal** (A)  |
| Steps → Resting HR        | F=9.6, p=0.002 ✓   | 0.13 bits, p=0.34   | no convergence | **Likely** (B)  |
| Steps → Glucose           | F=2.3, p=0.55      | —                | —               | Not causal (D)  |

**Interpretation:** [Explain what the significant causal links mean for the user's health.
 The strongest finding should be explained in plain language.]
```

When methods disagree, explain why — Granger tests linear causality, TE captures nonlinear information flow, CCM detects dynamical coupling. Different methods capture different aspects of causality.

---

## Section N-2: Biological & Fitness Age

```
## Biological Age Assessment

| Model                  | Estimated Age | Chronological Age | Gap     | Key Drivers              |
|------------------------|---------------|-------------------|---------|--------------------------|
| Fitness Age (VO2 Max)  | 64.4 yr       | 23.8 yr          | +40.6   | Low VO2 Max              |
| Biological Age (multi) | 35.3 yr       | 23.8 yr          | +11.5   | VO2 (+8), BMI (+1.2), ...  |
| Allostatic Load        | 2/7           | —                | Moderate | RHR, activity flagged    |

**Note:** Fitness Age is derived from VO2 Max using the HUNT study regression (Nes et al. 2013,
MSSE 45:2017). It represents the age at which the average person has your VO2 Max level.
The biological age model is a simplified multi-biomarker estimate — treat as directional, not precise.
```

If VO2 Max data is absent, state: "Fitness Age cannot be calculated without VO2 Max data."

---

## Section N-1: Cross-Metric Correlation Matrix

Present the full matrix with significance markers, then highlight the 3-5 most clinically meaningful correlations with physiological explanations. Include lagged correlations.

---

## Section N: Personalized Recommendations

Number recommendations by priority. Each must be:
1. **Specific** — not "exercise more" but "add 3 sessions of 30-min elliptical per week (your data shows this activity maintains Zone 3 HR most effectively)"
2. **Evidence-grounded** — tied to a specific finding in the report
3. **Quantified where possible** — "aim for 8,000+ steps/day (current: 4,200)"
4. **Time-framed** — "based on your lag-2-week Steps→RHR correlation, expect measurable RHR improvement within 14 days of sustained increase"

End with: "These recommendations are based on patterns in your wearable data. Discuss significant changes to your exercise or diet with your healthcare provider."

---

## Formatting Rules

1. **Tables**: Use markdown tables for all dense data (monthly trends, daily glucose, metrics comparisons). Always include units.
2. **Statistical results**: Always report test statistic AND p-value: "(F=18.8, p<0.001)" not just "significant."
3. **Numbers**: Report to clinically meaningful precision — HR to 1 decimal, glucose to integers, p-values to 3-4 significant figures, correlation coefficients to 3 decimals.
4. **Paper citations**: When referencing a method's paper, use inline format: "(Kovatchev et al. 2002, Diabetes Care)" — the full reference list is in the advanced analysis JSON.
5. **Confidence intervals**: When bootstrap CIs are available, report them: "Mean RHR: 78.0 bpm (95% CI: 76.2–79.8)"
6. **Effect sizes**: When Cohen's d is available, report it with interpretation: "(d=0.65, medium effect)"
7. **Sample sizes**: Always state n for any statistic: "(n=240 days)"
8. **Trend arrows**: Use ↑/↓/→ for trends in tables. Add "worse"/"better" when directionality is clear.

## Tone

Write as a clinical data scientist would for a health-literate patient — precise but accessible. Avoid:
- Alarmist language ("dangerous", "alarming")
- Vague hedging ("might possibly suggest")
- Unsupported claims (no stat backing)
- Unnecessary reassurance ("don't worry about...")

Use instead:
- Direct assessment ("below age-expected range", "clinically elevated")
- Specific quantification ("15th percentile for your age group")
- Clear conditional language ("if this trend continues at current rate, projected BMI at 12 months is 34.7")
