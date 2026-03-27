#!/usr/bin/env python3
"""
Apple Health Report -- HTML Generator
Produces a self-contained, richly visualized HTML report using Claude's design language.
Takes JSON output from analyze_health.py and advanced_analytics.py.

Usage:
    python3 generate_report_html.py <base.json> <advanced.json> [-o report.html]
"""

import json
import sys
import argparse
import math
import html as html_mod
from datetime import datetime

# ============================================================================
# Internationalization
# ============================================================================
I18N = {
    "en": {
        "title": "Comprehensive Health Assessment Report",
        "disclaimer": "This report is for informational purposes only. It does not constitute medical advice. Consult a licensed healthcare provider before making health decisions.",
        "executive_summary": "Executive Summary",
        "health_dashboard": "Health Dashboard",
        "overall_score": "Overall",
        "risk_stratification": "Risk Stratification",
        "body_composition": "Body Composition",
        "cardiovascular": "Cardiovascular",
        "autonomic_ns": "Autonomic Nervous System",
        "glucose_cgm": "Blood Glucose (CGM)",
        "activity": "Activity & Exercise",
        "sleep": "Sleep Analysis",
        "circadian": "Circadian Rhythm",
        "causal_inference": "Causal Inference",
        "nonlinear": "Nonlinear Dynamics",
        "bio_age": "Biological & Fitness Age",
        "correlations": "Cross-Metric Correlations",
        "trend_momentum": "Trend Momentum",
        "data_quality": "Data Quality",
        "methodology": "Methodology & References",
        "recommendations": "Recommendations",
        "evidence": "Evidence",
        "current": "Current",
        "target": "Target",
        "trend": "Trend",
        "mean": "Mean",
        "months": "months",
        "days": "days",
        "records": "records",
        "methods": "statistical methods",
        "age": "Age",
        "sex": "Sex",
        "data_period": "Data",
        "high_risk": "HIGH RISK",
        "moderate_risk": "MODERATE RISK",
        "positive": "POSITIVE",
        "clinical_significance": "Clinical Significance",
        "recommendation": "Recommendation",
        "weight_kg": "Weight (kg)",
        "resting_hr": "Resting HR",
        "hrv_recovery": "HRV / Recovery",
        "cardio_fitness": "Cardio Fitness",
        "activity_level": "Activity",
        "exercise_consistency": "Exercise",
        "body_comp": "Body Comp",
        "metabolic_health": "Metabolic",
        "sleep_quality": "Sleep",
        "fitness_age": "Fitness Age",
        "biological_age": "Biological Age",
        "chronological_age": "Chronological Age",
        "allostatic_load": "Allostatic Load",
        "steps_per_day": "Steps/Day",
        "monthly_avg": "Monthly Average",
        "weekly_pattern": "Weekly Pattern",
        "reliability": "Reliability",
        "coverage": "Coverage",
        "stream": "Data Stream",
        "footer_generated": "Generated",
        "footer_methods_from": "methods from",
        "footer_publications": "peer-reviewed publications",
        "disease_screening": "Disease Risk Screening",
        "screening_disclaimer": "These are screening estimates based on consumer wearable data, NOT clinical diagnoses. A positive screen means further clinical evaluation is recommended.",
        "conditions_screened": "Conditions Screened",
        "elevated_risks": "Elevated Risks",
        "moderate_risks": "Moderate Risks",
        "low_risks": "Low Risks",
        "risk_factors": "Risk Factors",
        "clinical_recommendation": "Clinical Recommendation",
        "paper_references": "References",
        "screening_not_diagnosis": "Screening, not diagnosis",
        "no_screening_data": "No conditions had sufficient data for screening.",
    },
    "zh": {
        "title": "综合健康评估报告",
        "disclaimer": "本报告仅供参考，不构成医疗建议。请在做出健康决策前咨询持证医疗专业人员。",
        "executive_summary": "执行摘要",
        "health_dashboard": "健康仪表盘",
        "overall_score": "综合评分",
        "risk_stratification": "风险分层",
        "body_composition": "体成分分析",
        "cardiovascular": "心血管功能",
        "autonomic_ns": "自主神经系统",
        "glucose_cgm": "血糖分析 (CGM)",
        "activity": "活动与运动",
        "sleep": "睡眠分析",
        "circadian": "昼夜节律",
        "causal_inference": "因果推断分析",
        "nonlinear": "非线性动力学",
        "bio_age": "生物年龄与体能年龄",
        "correlations": "跨指标相关性",
        "trend_momentum": "趋势动量",
        "data_quality": "数据质量",
        "methodology": "方法论与参考文献",
        "recommendations": "建议",
        "evidence": "证据",
        "current": "当前",
        "target": "目标",
        "trend": "趋势",
        "mean": "均值",
        "months": "月",
        "days": "天",
        "records": "条记录",
        "methods": "种统计方法",
        "age": "年龄",
        "sex": "性别",
        "data_period": "数据",
        "high_risk": "高风险",
        "moderate_risk": "中等风险",
        "positive": "正面发现",
        "clinical_significance": "临床意义",
        "recommendation": "建议",
        "weight_kg": "体重 (kg)",
        "resting_hr": "静息心率",
        "hrv_recovery": "心率变异性",
        "cardio_fitness": "心肺适能",
        "activity_level": "活动水平",
        "exercise_consistency": "运动规律",
        "body_comp": "体成分",
        "metabolic_health": "代谢健康",
        "sleep_quality": "睡眠质量",
        "fitness_age": "体能年龄",
        "biological_age": "生物年龄",
        "chronological_age": "实际年龄",
        "allostatic_load": "负荷指数",
        "steps_per_day": "日均步数",
        "monthly_avg": "月均值",
        "weekly_pattern": "周模式",
        "reliability": "可靠性",
        "coverage": "覆盖率",
        "stream": "数据流",
        "footer_generated": "生成于",
        "footer_methods_from": "种方法，引用",
        "footer_publications": "篇同行评审论文",
        "disease_screening": "疾病风险筛查",
        "screening_disclaimer": "以下为基于消费级可穿戴设备数据的筛查估计，并非临床诊断。筛查阳性意味着建议进一步临床评估。",
        "conditions_screened": "筛查病种",
        "elevated_risks": "升高风险",
        "moderate_risks": "中等风险",
        "low_risks": "低风险",
        "risk_factors": "风险因素",
        "clinical_recommendation": "临床建议",
        "paper_references": "参考文献",
        "screening_not_diagnosis": "筛查非诊断",
        "no_screening_data": "无足够数据进行疾病筛查。",
    },
}

_LANG = "en"  # Module-level language; set by generate_html()

def t(key, lang=None):
    """Get translated string."""
    lang = lang or _LANG
    return I18N.get(lang, I18N["en"]).get(key, I18N["en"].get(key, key))

# ============================================================================
# Claude Design Tokens
# ============================================================================
COLORS = {
    "primary": "#D97757",
    "primary_light": "#E8A88C",
    "primary_dark": "#B85C3A",
    "bg": "#FDFAF7",
    "bg_card": "#FFFFFF",
    "bg_alt": "#F5F0EB",
    "text": "#1A1A1A",
    "text_secondary": "#6B6157",
    "text_muted": "#9B9189",
    "border": "#E8E0D8",
    "border_light": "#F0EBE5",
    "success": "#2D8B4E",
    "success_bg": "#E8F5ED",
    "warning": "#C68A17",
    "warning_bg": "#FDF3E0",
    "danger": "#C44536",
    "danger_bg": "#FDEAE8",
    "info": "#3B7DD8",
    "info_bg": "#E8F0FD",
    "purple": "#9B59B6",
    "purple_bg": "#F3E8F9",
    "grade_a": "#2D8B4E",
    "grade_b": "#4AA86B",
    "grade_c": "#C68A17",
    "grade_d": "#D97757",
    "grade_e": "#C44536",
    "grade_f": "#8B2E20",
    "chart_1": "#D97757",
    "chart_2": "#3B7DD8",
    "chart_3": "#2D8B4E",
    "chart_4": "#9B59B6",
    "chart_5": "#C68A17",
    "chart_6": "#C44536",
}

# ============================================================================
# Utility helpers
# ============================================================================

def _s(val):
    """Safe HTML escape."""
    if val is None:
        return ""
    return html_mod.escape(str(val))

def fmt(val, decimals=1):
    if val is None:
        return "\u2014"
    if isinstance(val, float):
        return f"{val:.{decimals}f}"
    return str(val)

def grade_color(score):
    if score is None:
        return COLORS["text_muted"]
    if score >= 90:
        return COLORS["grade_a"]
    if score >= 75:
        return COLORS["grade_b"]
    if score >= 60:
        return COLORS["grade_c"]
    if score >= 45:
        return COLORS["grade_d"]
    if score >= 30:
        return COLORS["grade_e"]
    return COLORS["grade_f"]

def grade_letter(score):
    if score is None:
        return "?"
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    if score >= 30:
        return "E"
    return "F"

def risk_color(level):
    level = (level or "").upper()
    if level == "HIGH":
        return COLORS["danger"]
    if level == "MODERATE":
        return COLORS["warning"]
    return COLORS["success"]

def risk_bg(level):
    level = (level or "").upper()
    if level == "HIGH":
        return COLORS["danger_bg"]
    if level == "MODERATE":
        return COLORS["warning_bg"]
    return COLORS["success_bg"]

def risk_icon(level):
    level = (level or "").upper()
    if level == "HIGH":
        return "\u26a0"
    if level == "MODERATE":
        return "\u25b2"
    return "\u2713"

def safe_get(d, *keys, default=None):
    """Safely traverse nested dicts."""
    cur = d
    for k in keys:
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return default
        if cur is None:
            return default
    return cur

def trend_arrow(recent, older):
    """Return trend arrow comparing two values."""
    if recent is None or older is None:
        return ""
    diff_pct = ((recent - older) / abs(older) * 100) if older != 0 else 0
    if diff_pct > 5:
        return '<span style="color:#C44536">\u2191</span>'
    elif diff_pct < -5:
        return '<span style="color:#2D8B4E">\u2193</span>'
    else:
        return '<span style="color:#9B9189">\u2192</span>'

def evidence_badge(grade):
    """Return an HTML badge for evidence grade A/B/C/D."""
    colors = {"A": COLORS["grade_a"], "B": COLORS["grade_b"], "C": COLORS["grade_c"], "D": COLORS["grade_d"]}
    c = colors.get(grade, COLORS["text_muted"])
    return f'<span class="evidence-badge" style="background:{c}">{_s(grade)}</span>'

# ============================================================================
# CSS Generation
# ============================================================================

def generate_css():
    C = COLORS
    return f"""
    :root {{
        --primary: {C["primary"]};
        --primary-light: {C["primary_light"]};
        --primary-dark: {C["primary_dark"]};
        --bg: {C["bg"]};
        --bg-card: {C["bg_card"]};
        --bg-alt: {C["bg_alt"]};
        --text: {C["text"]};
        --text-secondary: {C["text_secondary"]};
        --text-muted: {C["text_muted"]};
        --border: {C["border"]};
        --border-light: {C["border_light"]};
        --success: {C["success"]};
        --warning: {C["warning"]};
        --danger: {C["danger"]};
        --info: {C["info"]};
        --purple: {C["purple"]};
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 15px;
        line-height: 1.6;
        color: var(--text);
        background: var(--bg);
    }}
    /* Navigation */
    .nav-sidebar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 260px;
        height: 100vh;
        background: var(--bg-card);
        border-right: 1px solid var(--border);
        overflow-y: auto;
        z-index: 1000;
        padding: 20px 0;
    }}
    .nav-sidebar .nav-title {{
        font-size: 14px;
        font-weight: 700;
        color: var(--primary);
        padding: 8px 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .nav-sidebar a {{
        display: block;
        padding: 7px 20px 7px 24px;
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 13px;
        border-left: 3px solid transparent;
        transition: all 0.15s;
    }}
    .nav-sidebar a:hover {{
        color: var(--primary);
        background: {C["bg_alt"]};
        border-left-color: var(--primary-light);
    }}
    .nav-sidebar a.active {{
        color: var(--primary-dark);
        font-weight: 600;
        border-left-color: var(--primary);
        background: {C["bg_alt"]};
    }}
    .main-content {{
        margin-left: 260px;
        padding: 0;
    }}
    /* Header */
    .report-header {{
        background: linear-gradient(135deg, {C["primary"]} 0%, {C["primary_dark"]} 100%);
        color: #fff;
        padding: 48px 48px 36px;
    }}
    .report-header h1 {{
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 6px;
    }}
    .report-header .subtitle {{
        font-size: 15px;
        opacity: 0.85;
        margin-bottom: 24px;
    }}
    .header-stats {{
        display: flex;
        gap: 32px;
        flex-wrap: wrap;
    }}
    .header-stat {{
        text-align: center;
    }}
    .header-stat .stat-value {{
        font-size: 24px;
        font-weight: 700;
    }}
    .header-stat .stat-label {{
        font-size: 12px;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    /* Sections */
    .section {{
        padding: 32px 48px;
    }}
    .section + .section {{
        border-top: 1px solid var(--border-light);
    }}
    .section-title {{
        font-size: 20px;
        font-weight: 700;
        color: var(--text);
        padding-left: 16px;
        border-left: 4px solid var(--primary);
        margin-bottom: 24px;
        line-height: 1.3;
    }}
    .section-subtitle {{
        font-size: 15px;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 12px;
        margin-top: 20px;
    }}
    /* Cards */
    .card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .card-header {{
        font-size: 14px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }}
    .card-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
    }}
    .card-grid-2 {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 16px;
    }}
    .card-grid-3 {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }}
    .card-grid-4 {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }}
    /* Metric cards */
    .metric-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .metric-label {{
        font-size: 12px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 700;
        color: var(--text);
        line-height: 1.2;
    }}
    .metric-unit {{
        font-size: 14px;
        color: var(--text-muted);
        font-weight: 400;
    }}
    .metric-note {{
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
    }}
    /* Alert cards */
    .alert-card {{
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }}
    .alert-card.alert-high {{
        background: {C["danger_bg"]};
        border-left-color: {C["danger"]};
    }}
    .alert-card.alert-moderate {{
        background: {C["warning_bg"]};
        border-left-color: {C["warning"]};
    }}
    .alert-card.alert-low {{
        background: {C["success_bg"]};
        border-left-color: {C["success"]};
    }}
    .alert-card .alert-title {{
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }}
    .alert-card .alert-detail {{
        font-size: 13px;
        color: var(--text-secondary);
    }}
    /* Evidence badges */
    .evidence-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        color: #fff;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
        vertical-align: middle;
    }}
    /* Tables */
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }}
    .data-table th {{
        background: var(--bg-alt);
        color: var(--text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 10px 12px;
        border-bottom: 2px solid var(--border);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    .data-table td {{
        padding: 8px 12px;
        border-bottom: 1px solid var(--border-light);
        vertical-align: middle;
    }}
    .data-table tr:hover {{
        background: var(--bg-alt);
    }}
    /* Interpretation text */
    .interpretation {{
        background: var(--bg-alt);
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 16px;
        margin-bottom: 16px;
        font-size: 14px;
        line-height: 1.7;
        color: var(--text-secondary);
        border-left: 3px solid var(--primary-light);
    }}
    .interpretation strong {{
        color: var(--text);
    }}
    /* AI Narrative placeholders */
    .ai-narrative {{
        padding: 16px 20px;
        margin: 12px 0;
        border-left: 3px solid {C["primary"]};
        background: {C["bg_alt"]};
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        line-height: 1.7;
        min-height: 20px;
    }}
    .ai-narrative:empty::before {{
        content: '';
    }}
    .ai-narrative h4 {{ margin: 12px 0 6px; font-size: 15px; font-weight: 600; }}
    .ai-narrative ul, .ai-narrative ol {{ margin: 8px 0; padding-left: 20px; }}
    .ai-narrative li {{ margin: 4px 0; }}
    .ai-narrative strong {{ color: {C["primary_dark"]}; }}
    .ai-narrative p {{ margin: 8px 0; }}
    .recommendation {{
        background: {C["info_bg"]};
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 12px;
        font-size: 13px;
        line-height: 1.6;
        border-left: 3px solid {C["info"]};
        color: var(--text-secondary);
    }}
    .recommendation::before {{
        content: "\\1F4A1 ";
    }}
    /* Collapsible */
    .collapsible-toggle {{
        cursor: pointer;
        user-select: none;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--primary-dark);
    }}
    .collapsible-toggle::before {{
        content: "\\25B6";
        font-size: 10px;
        transition: transform 0.2s;
    }}
    .collapsible-toggle.open::before {{
        transform: rotate(90deg);
    }}
    .collapsible-content {{
        display: none;
        padding-top: 8px;
    }}
    .collapsible-content.open {{
        display: block;
    }}
    /* Gauge grid */
    .gauge-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }}
    .gauge-item {{
        text-align: center;
    }}
    .gauge-item .gauge-label {{
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 8px;
        font-weight: 500;
    }}
    .gauge-item .gauge-score {{
        font-size: 13px;
        color: var(--text-muted);
    }}
    /* Comparison */
    .comparison-row {{
        display: flex;
        gap: 24px;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
    }}
    .comparison-box {{
        text-align: center;
        padding: 24px 32px;
        border-radius: 12px;
        min-width: 180px;
    }}
    .comparison-box .comp-value {{
        font-size: 48px;
        font-weight: 800;
        line-height: 1.1;
    }}
    .comparison-box .comp-label {{
        font-size: 13px;
        margin-top: 6px;
        font-weight: 500;
    }}
    .comparison-vs {{
        font-size: 24px;
        font-weight: 300;
        color: var(--text-muted);
    }}
    /* Reliability badges */
    .badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 100px;
        font-size: 11px;
        font-weight: 600;
    }}
    .badge-high {{ background: {C["success_bg"]}; color: {C["success"]}; }}
    .badge-moderate {{ background: {C["warning_bg"]}; color: {C["warning"]}; }}
    .badge-low {{ background: {C["danger_bg"]}; color: {C["danger"]}; }}
    /* Footer */
    .report-footer {{
        padding: 32px 48px;
        background: var(--bg-alt);
        border-top: 1px solid var(--border);
        font-size: 12px;
        color: var(--text-muted);
        line-height: 1.8;
    }}
    /* SVG responsive */
    svg {{ max-width: 100%; height: auto; }}
    /* Print */
    @media print {{
        .nav-sidebar {{ display: none; }}
        .main-content {{ margin-left: 0; }}
        .report-header {{ padding: 24px; }}
        .section {{ padding: 20px 24px; }}
        .card {{ box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; }}
        .collapsible-content {{ display: block !important; }}
    }}
    /* Mobile */
    @media (max-width: 900px) {{
        .nav-sidebar {{ display: none; }}
        .main-content {{ margin-left: 0; }}
        .section {{ padding: 20px 16px; }}
        .report-header {{ padding: 24px 16px; }}
        .card-grid, .card-grid-2, .card-grid-3, .card-grid-4, .gauge-grid {{
            grid-template-columns: 1fr;
        }}
        .header-stats {{ gap: 16px; }}
        .comparison-row {{ flex-direction: column; gap: 12px; }}
    }}
    @media (max-width: 1200px) and (min-width: 901px) {{
        .gauge-grid {{ grid-template-columns: repeat(2, 1fr); }}
        .card-grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    """

# ============================================================================
# SVG Chart Generators
# ============================================================================

def svg_circular_gauge(score, label="", size=140, stroke_width=12):
    """Circular gauge for scores 0-100 with letter grade."""
    if score is None:
        score = 0
    score = max(0, min(100, score))
    r = (size - stroke_width) / 2
    cx = cy = size / 2
    circumference = 2 * math.pi * r
    filled = circumference * score / 100
    gap = circumference - filled
    color = grade_color(score)
    letter = grade_letter(score)
    return f'''<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" style="display:block;margin:0 auto;">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{COLORS["border_light"]}" stroke-width="{stroke_width}" />
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke_width}"
    stroke-dasharray="{filled:.1f} {gap:.1f}" stroke-dashoffset="{circumference * 0.25:.1f}"
    stroke-linecap="round" transform="rotate(-90 {cx} {cy})" />
  <text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="28" font-weight="800" fill="{color}">{letter}</text>
  <text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="16" font-weight="600" fill="{COLORS["text"]}">{score}</text>
  <text x="{cx}" y="{cy + 30}" text-anchor="middle" font-size="10" fill="{COLORS["text_muted"]}">/ 100</text>
</svg>'''


def svg_line_chart(data_points, width=600, height=200, color=None, fill=True,
                   x_labels=None, y_min=None, y_max=None, title="",
                   show_dots=True, trend_line=None, secondary_data=None, secondary_color=None):
    """Line chart with optional area fill, trend line, and secondary series.
    data_points: list of numeric values
    x_labels: list of label strings (same length)
    trend_line: list of (x_index, y_value) for regression line endpoints
    """
    if not data_points or len(data_points) < 2:
        return ""
    c = color or COLORS["chart_1"]
    sc = secondary_color or COLORS["chart_2"]
    padding_top = 30
    padding_bottom = 40
    padding_left = 50
    padding_right = 20
    chart_w = width - padding_left - padding_right
    chart_h = height - padding_top - padding_bottom

    vals = [v for v in data_points if v is not None]
    if not vals:
        return ""
    all_vals = list(vals)
    if secondary_data:
        all_vals += [v for v in secondary_data if v is not None]
    data_min = y_min if y_min is not None else min(all_vals)
    data_max = y_max if y_max is not None else max(all_vals)
    if data_min == data_max:
        data_min -= 1
        data_max += 1
    data_range = data_max - data_min

    def to_x(i):
        return padding_left + (i / (len(data_points) - 1)) * chart_w

    def to_y(v):
        return padding_top + chart_h - ((v - data_min) / data_range) * chart_h

    # Build paths
    points = []
    for i, v in enumerate(data_points):
        if v is not None:
            points.append((to_x(i), to_y(v)))

    if not points:
        return ""

    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    fill_path = ""
    if fill:
        first_x = points[0][0]
        last_x = points[-1][0]
        base_y = padding_top + chart_h
        fill_d = path_d + f" L {last_x:.1f},{base_y:.1f} L {first_x:.1f},{base_y:.1f} Z"
        fill_path = f'<path d="{fill_d}" fill="{c}" opacity="0.12" />'

    # Secondary series
    sec_path = ""
    if secondary_data and len(secondary_data) >= 2:
        sec_points = []
        for i, v in enumerate(secondary_data):
            if v is not None and i < len(data_points):
                sec_points.append((to_x(i), to_y(v)))
        if len(sec_points) >= 2:
            sec_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in sec_points)
            sec_path = f'<path d="{sec_d}" fill="none" stroke="{sc}" stroke-width="2" stroke-dasharray="6,3" />'

    # Trend line
    trend_path = ""
    if trend_line and len(trend_line) >= 2:
        t0, t1 = trend_line[0], trend_line[-1]
        tx0, ty0 = to_x(t0[0]), to_y(t0[1])
        tx1, ty1 = to_x(t1[0]), to_y(t1[1])
        trend_path = f'<line x1="{tx0:.1f}" y1="{ty0:.1f}" x2="{tx1:.1f}" y2="{ty1:.1f}" stroke="{COLORS["danger"]}" stroke-width="2" stroke-dasharray="8,4" />'

    # Dots
    dots = ""
    if show_dots and len(points) <= 30:
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{c}" />' for x, y in points)

    # Y axis labels
    y_labels_svg = ""
    n_yticks = 4
    for i in range(n_yticks + 1):
        val = data_min + (data_range * i / n_yticks)
        y_pos = to_y(val)
        y_labels_svg += f'<text x="{padding_left - 8}" y="{y_pos + 4:.1f}" text-anchor="end" font-size="10" fill="{COLORS["text_muted"]}">{val:.0f}</text>'
        y_labels_svg += f'<line x1="{padding_left}" y1="{y_pos:.1f}" x2="{padding_left + chart_w}" y2="{y_pos:.1f}" stroke="{COLORS["border_light"]}" stroke-width="0.5" />'

    # X labels
    x_labels_svg = ""
    if x_labels:
        step = max(1, len(x_labels) // 8)
        for i in range(0, len(x_labels), step):
            x_pos = to_x(i)
            lbl = x_labels[i] if i < len(x_labels) else ""
            # Shorten labels
            if len(lbl) > 7:
                lbl = lbl[-5:]
            x_labels_svg += f'<text x="{x_pos:.1f}" y="{padding_top + chart_h + 20}" text-anchor="middle" font-size="10" fill="{COLORS["text_muted"]}">{_s(lbl)}</text>'

    # Title
    title_svg = ""
    if title:
        title_svg = f'<text x="{padding_left}" y="16" font-size="12" font-weight="600" fill="{COLORS["text_secondary"]}">{_s(title)}</text>'

    return f'''<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">
  {title_svg}
  {y_labels_svg}
  {x_labels_svg}
  {fill_path}
  <path d="{path_d}" fill="none" stroke="{c}" stroke-width="2.5" stroke-linejoin="round" />
  {sec_path}
  {trend_path}
  {dots}
</svg>'''


def svg_donut_chart(segments, size=200, inner_ratio=0.6, title=""):
    """Donut chart. segments: list of (label, value, color)."""
    if not segments:
        return ""
    total = sum(v for _, v, _ in segments)
    if total <= 0:
        return ""
    cx = cy = size / 2
    r = (size - 20) / 2
    inner_r = r * inner_ratio

    paths = ""
    legend = ""
    angle = -90  # start from top

    for label, value, color in segments:
        if value <= 0:
            continue
        pct = value / total
        sweep = pct * 360
        end_angle = angle + sweep

        # Outer arc
        a1_rad = math.radians(angle)
        a2_rad = math.radians(end_angle)
        x1_o = cx + r * math.cos(a1_rad)
        y1_o = cy + r * math.sin(a1_rad)
        x2_o = cx + r * math.cos(a2_rad)
        y2_o = cy + r * math.sin(a2_rad)
        # Inner arc
        x1_i = cx + inner_r * math.cos(a2_rad)
        y1_i = cy + inner_r * math.sin(a2_rad)
        x2_i = cx + inner_r * math.cos(a1_rad)
        y2_i = cy + inner_r * math.sin(a1_rad)

        large = 1 if sweep > 180 else 0

        d = (f"M {x1_o:.2f},{y1_o:.2f} "
             f"A {r:.2f},{r:.2f} 0 {large},1 {x2_o:.2f},{y2_o:.2f} "
             f"L {x1_i:.2f},{y1_i:.2f} "
             f"A {inner_r:.2f},{inner_r:.2f} 0 {large},0 {x2_i:.2f},{y2_i:.2f} Z")
        paths += f'<path d="{d}" fill="{color}" />'

        # Legend item
        pct_str = f"{pct * 100:.1f}%"
        legend += f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:14px;font-size:12px;color:{COLORS["text_secondary"]}"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{color}"></span>{_s(label)} ({pct_str})</span>'

        angle = end_angle

    title_svg = ""
    if title:
        title_svg = f'<text x="{cx}" y="{cy}" text-anchor="middle" font-size="11" font-weight="600" fill="{COLORS["text_muted"]}">{_s(title)}</text>'

    return f'''<div style="text-align:center">
<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" style="display:block;margin:0 auto">
  {paths}
  {title_svg}
</svg>
<div style="margin-top:8px;text-align:center;line-height:2">{legend}</div>
</div>'''


def svg_horizontal_bar(items, width=500, bar_height=28, max_val=None, show_values=True):
    """Horizontal bar chart. items: list of (label, value, color)."""
    if not items:
        return ""
    if max_val is None:
        max_val = max(v for _, v, _ in items) or 1
    padding_left = 100
    chart_w = width - padding_left - 40
    total_h = len(items) * (bar_height + 8) + 10

    bars = ""
    for i, (label, value, color) in enumerate(items):
        y = i * (bar_height + 8) + 5
        bw = (value / max_val) * chart_w if max_val else 0
        bars += f'<text x="{padding_left - 8}" y="{y + bar_height / 2 + 4:.1f}" text-anchor="end" font-size="12" fill="{COLORS["text_secondary"]}">{_s(label)}</text>'
        bars += f'<rect x="{padding_left}" y="{y}" width="{bw:.1f}" height="{bar_height}" fill="{color}" rx="4" />'
        if show_values:
            bars += f'<text x="{padding_left + bw + 6:.1f}" y="{y + bar_height / 2 + 4:.1f}" font-size="11" fill="{COLORS["text_muted"]}">{fmt(value)}</text>'

    return f'''<svg viewBox="0 0 {width} {total_h}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">
  {bars}
</svg>'''


def svg_stacked_bar(segments, width=400, height=36, labels=True):
    """Single stacked horizontal bar. segments: list of (label, value, color)."""
    if not segments:
        return ""
    total = sum(v for _, v, _ in segments)
    if total <= 0:
        return ""
    bar_svg = ""
    legend_html = ""
    x = 0
    for label, value, color in segments:
        w = (value / total) * width
        bar_svg += f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="{height}" fill="{color}" />'
        x += w
        pct = value / total * 100
        legend_html += f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;font-size:12px;color:{COLORS["text_secondary"]}"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{color}"></span>{_s(label)} ({pct:.0f}%)</span>'

    return f'''<div>
<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block;border-radius:6px;overflow:hidden">
  {bar_svg}
</svg>
{"<div style='margin-top:8px;line-height:2'>" + legend_html + "</div>" if labels else ""}
</div>'''


def svg_sparkline(values, width=120, height=30, color=None):
    """Tiny inline sparkline."""
    if not values or len(values) < 2:
        return ""
    c = color or COLORS["primary"]
    vals = [v for v in values if v is not None]
    if not vals:
        return ""
    vmin, vmax = min(vals), max(vals)
    if vmin == vmax:
        vmin -= 1
        vmax += 1
    vrange = vmax - vmin
    points = []
    for i, v in enumerate(values):
        if v is not None:
            x = (i / (len(values) - 1)) * width
            y = height - ((v - vmin) / vrange) * (height - 4) - 2
            points.append(f"{x:.1f},{y:.1f}")
    if len(points) < 2:
        return ""
    d = "M " + " L ".join(points)
    return f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="display:inline-block;vertical-align:middle"><path d="{d}" fill="none" stroke="{c}" stroke-width="1.5" /></svg>'


def svg_heatmap(matrix, row_labels, col_labels, width=500, cell_size=52, title=""):
    """Color-coded heatmap for correlation matrix."""
    if not matrix or not row_labels or not col_labels:
        return ""
    n_rows = len(row_labels)
    n_cols = len(col_labels)
    label_w = 70
    label_h = 70
    total_w = label_w + n_cols * cell_size
    total_h = label_h + n_rows * cell_size

    cells = ""
    for r in range(n_rows):
        for c in range(n_cols):
            val = matrix[r][c] if r < len(matrix) and c < len(matrix[r]) else 0
            # Color: positive = primary, negative = info
            intensity = min(abs(val), 1.0)
            if val > 0:
                # Warm
                red = int(255 - (255 - 217) * intensity)
                green = int(255 - (255 - 119) * intensity)
                blue = int(255 - (255 - 87) * intensity)
            else:
                # Cool
                red = int(255 - (255 - 59) * intensity)
                green = int(255 - (255 - 125) * intensity)
                blue = int(255 - (255 - 216) * intensity)
            bg = f"rgb({red},{green},{blue})"
            x = label_w + c * cell_size
            y = label_h + r * cell_size
            text_color = "#fff" if intensity > 0.5 else COLORS["text"]
            cells += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{bg}" stroke="#fff" stroke-width="1" />'
            cells += f'<text x="{x + cell_size / 2}" y="{y + cell_size / 2 + 4}" text-anchor="middle" font-size="11" font-weight="600" fill="{text_color}">{val:.2f}</text>'

    # Row labels
    for r in range(n_rows):
        y = label_h + r * cell_size + cell_size / 2 + 4
        cells += f'<text x="{label_w - 6}" y="{y}" text-anchor="end" font-size="11" fill="{COLORS["text_secondary"]}">{_s(row_labels[r])}</text>'

    # Col labels
    for c in range(n_cols):
        x = label_w + c * cell_size + cell_size / 2
        cells += f'<text x="{x}" y="{label_h - 8}" text-anchor="middle" font-size="11" fill="{COLORS["text_secondary"]}" transform="rotate(-35 {x} {label_h - 8})">{_s(col_labels[c])}</text>'

    return f'''<svg viewBox="0 0 {total_w} {total_h}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">
  {cells}
</svg>'''


def svg_circadian_curve(hourly_data, width=600, height=220, color=None, label="", y_unit=""):
    """24-hour circadian curve from hourly data dict {hour_str: {mean, p10/p25/p75/p90}}."""
    if not hourly_data:
        return ""
    c = color or COLORS["chart_1"]
    padding_top = 30
    padding_bottom = 35
    padding_left = 50
    padding_right = 20
    chart_w = width - padding_left - padding_right
    chart_h = height - padding_top - padding_bottom

    hours = sorted(hourly_data.keys(), key=lambda h: int(h))
    means = [hourly_data[h].get("mean") or hourly_data[h].get("median", 0) for h in hours]
    p25s = [hourly_data[h].get("p25", hourly_data[h].get("mean", 0)) for h in hours]
    p75s = [hourly_data[h].get("p75", hourly_data[h].get("mean", 0)) for h in hours]

    all_vals = means + p25s + p75s
    vmin = min(all_vals) - 2
    vmax = max(all_vals) + 2
    vrange = vmax - vmin if vmax > vmin else 1

    def to_x(i):
        return padding_left + (i / 23) * chart_w

    def to_y(v):
        return padding_top + chart_h - ((v - vmin) / vrange) * chart_h

    # Band (p25-p75)
    band_top = []
    band_bot = []
    for i in range(24):
        idx = str(i).zfill(2)
        if idx in hourly_data:
            hi = hours.index(idx)
            band_top.append(f"{to_x(i):.1f},{to_y(p75s[hi]):.1f}")
            band_bot.append(f"{to_x(i):.1f},{to_y(p25s[hi]):.1f}")
    band_d = ""
    if band_top and band_bot:
        band_d = "M " + " L ".join(band_top) + " L " + " L ".join(reversed(band_bot)) + " Z"

    # Mean line
    mean_points = []
    for i in range(24):
        idx = str(i).zfill(2)
        if idx in hourly_data:
            hi = hours.index(idx)
            mean_points.append(f"{to_x(i):.1f},{to_y(means[hi]):.1f}")
    mean_d = "M " + " L ".join(mean_points) if mean_points else ""

    # Night shading
    night_x1 = padding_left
    night_x2 = to_x(6)
    night_x3 = to_x(22)
    night_x4 = padding_left + chart_w
    night = f'<rect x="{night_x1}" y="{padding_top}" width="{night_x2 - night_x1:.1f}" height="{chart_h}" fill="{COLORS["info"]}" opacity="0.04" />'
    night += f'<rect x="{night_x3:.1f}" y="{padding_top}" width="{night_x4 - night_x3:.1f}" height="{chart_h}" fill="{COLORS["info"]}" opacity="0.04" />'

    # Y axis
    y_labels = ""
    for i in range(5):
        val = vmin + vrange * i / 4
        yp = to_y(val)
        y_labels += f'<text x="{padding_left - 8}" y="{yp + 4:.1f}" text-anchor="end" font-size="10" fill="{COLORS["text_muted"]}">{val:.0f}</text>'
        y_labels += f'<line x1="{padding_left}" y1="{yp:.1f}" x2="{padding_left + chart_w}" y2="{yp:.1f}" stroke="{COLORS["border_light"]}" stroke-width="0.5" />'

    # X axis
    x_labels = ""
    for h in range(0, 24, 3):
        xp = to_x(h)
        x_labels += f'<text x="{xp:.1f}" y="{padding_top + chart_h + 18}" text-anchor="middle" font-size="10" fill="{COLORS["text_muted"]}">{h:02d}:00</text>'

    # Label
    lbl = f'<text x="{padding_left}" y="16" font-size="12" font-weight="600" fill="{COLORS["text_secondary"]}">{_s(label)}</text>' if label else ""

    return f'''<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">
  {lbl}
  {night}
  {y_labels}
  {x_labels}
  <path d="{band_d}" fill="{c}" opacity="0.15" />
  <path d="{mean_d}" fill="none" stroke="{c}" stroke-width="2.5" stroke-linejoin="round" />
  <text x="{padding_left + chart_w}" y="{padding_top + chart_h + 18}" text-anchor="end" font-size="9" fill="{COLORS["text_muted"]}">shaded = night</text>
</svg>'''


def svg_poincare(sd1, sd2, cx_val=0, cy_val=0, size=200):
    """Poincare plot ellipse visualization."""
    if sd1 is None or sd2 is None:
        return ""
    cx = cy = size / 2
    # Scale to fit
    max_sd = max(sd1, sd2, 1)
    scale = (size / 2 - 20) / max_sd
    rx = sd2 * scale
    ry = sd1 * scale
    return f'''<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" style="display:block;margin:0 auto">
  <line x1="10" y1="{cy}" x2="{size-10}" y2="{cy}" stroke="{COLORS["border"]}" stroke-width="0.5" />
  <line x1="{cx}" y1="10" x2="{cx}" y2="{size-10}" stroke="{COLORS["border"]}" stroke-width="0.5" />
  <line x1="10" y1="{size-10}" x2="{size-10}" y2="10" stroke="{COLORS["text_muted"]}" stroke-width="0.5" stroke-dasharray="4,4" />
  <ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{COLORS["primary"]}" fill-opacity="0.2" stroke="{COLORS["primary"]}" stroke-width="2" />
  <text x="{cx + rx + 4:.1f}" y="{cy + 4}" font-size="10" fill="{COLORS["chart_2"]}">SD2={fmt(sd2)}ms</text>
  <text x="{cx + 4}" y="{cy - ry - 4:.1f}" font-size="10" fill="{COLORS["chart_1"]}">SD1={fmt(sd1)}ms</text>
</svg>'''


def svg_bar_chart_vertical(data_points, x_labels, width=600, height=200, color=None, title=""):
    """Vertical bar chart for monthly data."""
    if not data_points or not x_labels:
        return ""
    c = color or COLORS["chart_1"]
    padding_top = 25
    padding_bottom = 40
    padding_left = 50
    padding_right = 20
    chart_w = width - padding_left - padding_right
    chart_h = height - padding_top - padding_bottom

    vals = [v for v in data_points if v is not None]
    if not vals:
        return ""
    vmax = max(vals)
    vmin = 0
    vrange = vmax - vmin if vmax > vmin else 1

    n = len(data_points)
    bar_w = max(chart_w / n * 0.7, 4)
    gap = chart_w / n

    bars = ""
    for i, v in enumerate(data_points):
        if v is None:
            continue
        x = padding_left + i * gap + (gap - bar_w) / 2
        bh = ((v - vmin) / vrange) * chart_h
        y = padding_top + chart_h - bh
        bars += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{c}" rx="2" opacity="0.85" />'

    # X labels
    x_labels_svg = ""
    step = max(1, n // 10)
    for i in range(0, n, step):
        x = padding_left + i * gap + gap / 2
        lbl = x_labels[i] if i < len(x_labels) else ""
        if len(lbl) > 5:
            lbl = lbl[-5:]
        x_labels_svg += f'<text x="{x:.1f}" y="{padding_top + chart_h + 18}" text-anchor="middle" font-size="10" fill="{COLORS["text_muted"]}">{_s(lbl)}</text>'

    # Y axis
    y_labels_svg = ""
    for i in range(5):
        val = vmin + vrange * i / 4
        yp = padding_top + chart_h - (val / vrange) * chart_h
        y_labels_svg += f'<text x="{padding_left - 8}" y="{yp + 4:.1f}" text-anchor="end" font-size="10" fill="{COLORS["text_muted"]}">{val:.0f}</text>'
        y_labels_svg += f'<line x1="{padding_left}" y1="{yp:.1f}" x2="{padding_left + chart_w}" y2="{yp:.1f}" stroke="{COLORS["border_light"]}" stroke-width="0.5" />'

    title_svg = f'<text x="{padding_left}" y="16" font-size="12" font-weight="600" fill="{COLORS["text_secondary"]}">{_s(title)}</text>' if title else ""

    return f'''<svg viewBox="0 0 {width} {height}" width="100%" preserveAspectRatio="xMidYMid meet" style="display:block">
  {title_svg}
  {y_labels_svg}
  {x_labels_svg}
  {bars}
</svg>'''


def svg_multiscale_entropy(mse_data, width=400, height=180):
    """Bar chart for multiscale entropy profile."""
    if not mse_data:
        return ""
    scales = sorted(mse_data.keys(), key=lambda k: int(k.split("_")[1]) if "_" in k else 0)
    vals = [mse_data[s] for s in scales]
    labels = [s.replace("scale_", "Scale ") for s in scales]
    items = [(l, v, COLORS["chart_4"]) for l, v in zip(labels, vals)]
    return svg_horizontal_bar(items, width=width, bar_height=24, max_val=max(vals) * 1.2 if vals else 1)


# ============================================================================
# Section Generators
# ============================================================================

def section_header(base, adv):
    """Report header with gradient and key stats strip."""
    pi = base.get("personal_info", {})
    do = base.get("data_overview", {})
    age = fmt(pi.get("age"), 1)
    sex = pi.get("sex", "Unknown")
    total_records = do.get("total_records", 0)
    total_types = do.get("total_record_types", 0)
    methods_count = len(adv.get("methods_applied", []))
    # Data period
    dq = base.get("data_quality", {})
    first_date = ""
    last_date = ""
    for stream in dq.get("streams", {}).values():
        span = stream.get("data_span", {})
        f_d = span.get("first", "")
        l_d = span.get("last", "")
        if f_d and (not first_date or f_d < first_date):
            first_date = f_d
        if l_d and (not last_date or l_d > last_date):
            last_date = l_d
    period = f"{first_date} to {last_date}" if first_date and last_date else "Unknown"

    return f'''<div class="report-header" id="top">
  <h1>Apple Health Analysis Report</h1>
  <div class="subtitle">Comprehensive health metrics analysis with {methods_count} analytical methods</div>
  <div class="header-stats">
    <div class="header-stat"><div class="stat-value">{_s(age)}</div><div class="stat-label">Age (years)</div></div>
    <div class="header-stat"><div class="stat-value">{_s(sex)}</div><div class="stat-label">Sex</div></div>
    <div class="header-stat"><div class="stat-value">{total_records:,}</div><div class="stat-label">Total Records</div></div>
    <div class="header-stat"><div class="stat-value">{total_types}</div><div class="stat-label">Data Types</div></div>
    <div class="header-stat"><div class="stat-value">{methods_count}</div><div class="stat-label">Methods Applied</div></div>
    <div class="header-stat"><div class="stat-value" style="font-size:14px">{_s(period)}</div><div class="stat-label">Data Period</div></div>
  </div>
</div>'''


def section_executive_summary(base, adv):
    """Executive summary with empty narrative placeholder for AI to fill."""
    return f'''<div class="section" id="executive-summary">
  <h2 class="section-title">{t("executive_summary")}</h2>
  <div class="ai-narrative" id="narrative-executive-summary"></div>
</div>'''


def section_health_dashboard(base):
    """Health dashboard with central gauge and 8 dimension gauges."""
    cs = base.get("composite_scores", {})
    if not cs:
        return ""
    overall = cs.get("overall", 0)
    dims = cs.get("dimensions", {})

    dim_labels = {
        "cardio_fitness": "Cardio Fitness",
        "resting_hr": "Resting HR",
        "activity_level": "Activity Level",
        "exercise_consistency": "Exercise",
        "body_composition": "Body Comp",
        "metabolic_health": "Metabolic",
        "sleep_quality": "Sleep Quality",
        "hrv_recovery": "HRV Recovery",
    }

    dim_gauges = ""
    for key, label in dim_labels.items():
        score = dims.get(key, 0)
        dim_gauges += f'''<div class="gauge-item">
  {svg_circular_gauge(score, size=110, stroke_width=10)}
  <div class="gauge-label">{_s(label)}</div>
  <div class="gauge-score">{score}/100</div>
</div>'''

    return f'''<div class="section" id="health-dashboard">
  <h2 class="section-title">{t("health_dashboard")}</h2>
  <div class="card" style="text-align:center;margin-bottom:24px">
    <div class="card-header">{t("overall_score")}</div>
    {svg_circular_gauge(overall, size=180, stroke_width=16)}
  </div>
  <div class="gauge-grid">{dim_gauges}</div>
</div>'''


def section_risk_stratification(base):
    """Risk stratification alert cards."""
    risks = base.get("risk_stratification", [])
    if not risks:
        return ""

    cards = ""
    for r in risks:
        level = r.get("level", "LOW")
        level_class = {"HIGH": "alert-high", "MODERATE": "alert-moderate"}.get(level, "alert-low")
        icon = risk_icon(level)
        title = r.get("title", "")
        detail = r.get("detail", "")

        cards += f'''<div class="alert-card {level_class}">
  <div class="alert-title">{icon} [{level}] {_s(title)}</div>
  <div class="alert-detail"><strong>Data:</strong> {_s(detail)}</div>
</div>'''

    return f'''<div class="section" id="risk-stratification">
  <h2 class="section-title">Risk Stratification</h2>
  {cards}
</div>'''


def section_disease_screening(adv):
    """Disease Risk Screening section -- prominent, clinically actionable cards."""
    C = COLORS
    drs = adv.get("disease_risk_screening")
    if not drs or not isinstance(drs, dict):
        return ""
    if "error" in drs:
        return ""
    screenings = drs.get("screenings", [])

    # -- Summary counts --
    total = drs.get("conditions_screened", len(screenings))
    elevated_count = 0
    moderate_count = 0
    low_count = 0
    for s in screenings:
        rl = (s.get("risk_level") or "").lower()
        if rl in ("elevated", "high"):
            elevated_count += 1
        elif rl == "moderate":
            moderate_count += 1
        else:
            low_count += 1

    # -- Empty screenings guard --
    if not screenings:
        return f'''<div class="section" id="disease-screening">
  <h2 class="section-title">{_s(t("disease_screening"))}</h2>
  <div style="padding:16px 20px;background:{C["warning_bg"]};border-left:4px solid {C["warning"]};border-radius:8px;margin-bottom:20px;font-size:14px;color:{C["text"]}">
    {_s(t("screening_disclaimer"))}
  </div>
  <p style="text-align:center;color:{C["text_muted"]};padding:40px 0;font-size:15px;">{_s(t("no_screening_data"))}</p>
</div>'''

    # -- Group and sort by risk level --
    order = {"elevated": 0, "high": 0, "moderate": 1, "low": 2}
    sorted_screenings = sorted(
        screenings,
        key=lambda s: (order.get((s.get("risk_level") or "low").lower(), 2), -(s.get("risk_pct") or 0))
    )

    # -- Helper: bar color based on percentage --
    def bar_color(pct):
        if pct >= 75:
            return C["danger"]
        if pct >= 50:
            return C["primary"]  # orange
        if pct >= 25:
            return C["warning"]
        return C["success"]

    # -- Helper: risk level styling --
    def level_border(rl):
        rl = (rl or "").lower()
        if rl in ("elevated", "high"):
            return C["danger"]
        if rl == "moderate":
            return C["warning"]
        return C["success"]

    def level_bg(rl):
        rl = (rl or "").lower()
        if rl in ("elevated", "high"):
            return C["danger_bg"]
        if rl == "moderate":
            return C["warning_bg"]
        return C["success_bg"]

    def level_text_color(rl):
        rl = (rl or "").lower()
        if rl in ("elevated", "high"):
            return C["danger"]
        if rl == "moderate":
            return C["warning"]
        return C["success"]

    # -- Build condition cards --
    cards_html = ""
    for idx, sc in enumerate(sorted_screenings):
        condition = sc.get("condition", "Unknown")
        risk_level = (sc.get("risk_level") or "low").lower()
        score = sc.get("score", 0)
        max_score = sc.get("max_score", 1)
        risk_pct = sc.get("risk_pct", 0)
        factors = sc.get("factors", [])
        recommendation = sc.get("recommendation", "")
        references = sc.get("references", [])

        border_c = level_border(risk_level)
        bg_c = level_bg(risk_level)
        text_c = level_text_color(risk_level)
        b_color = bar_color(risk_pct)
        bar_width = min(risk_pct, 100)
        level_display = risk_level.upper()

        # Factors list
        factors_html = ""
        if factors:
            items = "".join(f"<li style='margin-bottom:3px;'>{_s(f)}</li>" for f in factors)
            factors_html = f"""<div style="margin-top:10px;">
  <div style="font-weight:600;font-size:13px;color:{C['text_secondary']};margin-bottom:4px;">{_s(t("risk_factors"))}</div>
  <ul style="margin:0;padding-left:20px;font-size:13px;color:{C['text']};line-height:1.6;">{items}</ul>
</div>"""

        # Recommendation box
        rec_html = ""
        if recommendation:
            rec_html = f"""<div style="margin-top:10px;padding:10px 14px;background:{C['bg_alt']};border-radius:6px;font-size:13px;">
  <span style="font-weight:600;color:{C['text_secondary']};">{_s(t("clinical_recommendation"))}:</span>
  <span style="color:{C['text']};">{_s(recommendation)}</span>
</div>"""

        # References (collapsible)
        refs_html = ""
        if references:
            ref_items = "".join(f"<li style='margin-bottom:2px;'>{_s(r)}</li>" for r in references)
            refs_html = f"""<details style="margin-top:10px;">
  <summary style="font-size:12px;color:{C['text_muted']};cursor:pointer;font-weight:600;">{_s(t("paper_references"))} ({len(references)})</summary>
  <ul style="margin:6px 0 0 0;padding-left:20px;font-size:11px;color:{C['text_muted']};line-height:1.5;">{ref_items}</ul>
</details>"""

        cards_html += f"""<div style="background:{C['bg_card']};border:1px solid {C['border']};border-left:5px solid {border_c};border-radius:10px;padding:20px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <div style="font-size:17px;font-weight:700;color:{C['text']};">{_s(condition)}</div>
    <span style="display:inline-block;padding:3px 12px;border-radius:20px;font-size:12px;font-weight:700;color:#fff;background:{text_c};">{level_display}</span>
  </div>
  <div style="margin-top:14px;">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="flex:1;background:{C['border_light']};border-radius:6px;height:14px;overflow:hidden;">
        <div style="width:{bar_width:.1f}%;height:100%;background:{b_color};border-radius:6px;transition:width 0.3s;"></div>
      </div>
      <div style="font-size:13px;font-weight:700;color:{C['text']};white-space:nowrap;">{score}/{max_score}</div>
      <div style="font-size:13px;color:{C['text_muted']};white-space:nowrap;">{risk_pct:.1f}%</div>
    </div>
  </div>
  {factors_html}
  {rec_html}
  {refs_html}
</div>
"""

    # -- Assemble section --
    return f'''<div class="section" id="disease-screening">
  <h2 class="section-title">{_s(t("disease_screening"))}</h2>

  <!-- Disclaimer banner -->
  <div style="padding:16px 20px;background:{C["warning_bg"]};border-left:4px solid {C["warning"]};border-radius:8px;margin-bottom:24px;font-size:14px;color:{C["text"]};line-height:1.6;">
    <strong style="color:{C["warning"]};">{_s(t("screening_not_diagnosis"))}</strong><br>
    {_s(t("screening_disclaimer"))}
  </div>

  <!-- Summary dashboard -->
  <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:16px;margin-bottom:28px;">
    <div style="background:{C["bg_card"]};border:1px solid {C["border"]};border-radius:10px;padding:20px;text-align:center;">
      <div style="font-size:36px;font-weight:800;color:{C["primary"]};">{total}</div>
      <div style="font-size:13px;color:{C["text_secondary"]};margin-top:4px;">{_s(t("conditions_screened"))}</div>
    </div>
    <div style="background:{C["danger_bg"]};border:1px solid {C["danger"]}33;border-radius:10px;padding:20px;text-align:center;">
      <div style="font-size:36px;font-weight:800;color:{C["danger"]};">{elevated_count}</div>
      <div style="font-size:13px;color:{C["danger"]};margin-top:4px;">{_s(t("elevated_risks"))}</div>
    </div>
    <div style="background:{C["warning_bg"]};border:1px solid {C["warning"]}33;border-radius:10px;padding:20px;text-align:center;">
      <div style="font-size:36px;font-weight:800;color:{C["warning"]};">{moderate_count}</div>
      <div style="font-size:13px;color:{C["warning"]};margin-top:4px;">{_s(t("moderate_risks"))}</div>
    </div>
    <div style="background:{C["success_bg"]};border:1px solid {C["success"]}33;border-radius:10px;padding:20px;text-align:center;">
      <div style="font-size:36px;font-weight:800;color:{C["success"]};">{low_count}</div>
      <div style="font-size:13px;color:{C["success"]};margin-top:4px;">{_s(t("low_risks"))}</div>
    </div>
  </div>

  <!-- Condition cards -->
  {cards_html}
  <div class="ai-narrative" id="narrative-disease-screening"></div>
</div>'''


def section_body_composition(base, adv):
    """Body composition with weight chart, BMI, gain decomposition."""
    bc = base.get("body_composition", {})
    if not bc or not bc.get("weight", {}).get("history"):
        return ""

    wt = bc["weight"]
    history = wt.get("history", [])
    stats = wt.get("stats", {})
    regression = wt.get("regression", {})
    bf = bc.get("body_fat_pct", {})
    lbm = bc.get("lean_body_mass", {})
    decomp = bc.get("gain_decomposition", {})

    # Deduplicate weight history by date (take last per date)
    seen = {}
    for entry in history:
        seen[entry["date"]] = entry["kg"]
    dates_sorted = sorted(seen.keys())
    weights = [seen[d] for d in dates_sorted]

    # Weight line chart with trend
    trend_line = None
    if regression.get("kg_per_month") and len(dates_sorted) >= 2:
        # Simple linear trend from first to last
        first_w = weights[0]
        n_months = len(dates_sorted) - 1
        last_pred = first_w + regression["kg_per_month"] * (n_months * 30 / 30)  # approximate
        # Actually compute from regression
        kg_per_month = regression["kg_per_month"]
        # Estimate: y = first + slope * months_from_start
        from datetime import datetime as dt
        d0 = dt.strptime(dates_sorted[0], "%Y-%m-%d")
        dn = dt.strptime(dates_sorted[-1], "%Y-%m-%d")
        months_span = (dn - d0).days / 30.44
        trend_line = [(0, first_w), (len(weights) - 1, first_w + kg_per_month * months_span)]

    weight_chart = svg_line_chart(
        weights, width=650, height=220, color=COLORS["chart_1"],
        x_labels=dates_sorted, title="Weight Trend (kg)",
        trend_line=trend_line, fill=True
    )

    # BMI
    pi = base.get("personal_info", {})
    height_m = pi.get("height_m", 1.85)
    latest_w = weights[-1] if weights else 0
    bmi = latest_w / (height_m ** 2) if height_m else 0
    bmi_cat = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese I" if bmi < 35 else "Obese II"
    bmi_color = COLORS["success"] if bmi < 25 else COLORS["warning"] if bmi < 30 else COLORS["danger"]

    # Gain decomposition stacked bar
    decomp_bar = ""
    if decomp:
        decomp_bar = svg_stacked_bar([
            ("Fat Mass", decomp.get("fat_kg", 0), COLORS["danger"]),
            ("Lean Mass", decomp.get("lean_kg", 0), COLORS["chart_2"]),
        ], width=400, height=32)

    # Body fat trend
    bf_chart = ""
    if bf.get("history"):
        bf_seen = {}
        for entry in bf["history"]:
            bf_seen[entry["date"]] = entry["pct"]
        bf_dates = sorted(bf_seen.keys())
        bf_vals = [bf_seen[d] for d in bf_dates]
        bf_chart = svg_line_chart(bf_vals, width=650, height=180, color=COLORS["chart_6"],
                                  x_labels=bf_dates, title="Body Fat % Trend", fill=True)

    # Mann-Kendall
    mk = safe_get(adv, "trend_tests", "weight", default={})
    mk_html = ""
    if mk:
        mk_html = f'''<div class="metric-card">
  <div class="metric-label">Mann-Kendall Trend Test</div>
  <div class="metric-value" style="font-size:18px">{_s(mk.get("trend", "N/A")).replace("_", " ").title()}</div>
  <div class="metric-note">tau={fmt(mk.get("tau"), 3)}, p={fmt(mk.get("p_value"), 4)}, n={mk.get("n", "?")}</div>
</div>'''

    r2 = regression.get("r_squared", 0)

    return f'''<div class="section" id="body-composition">
  <h2 class="section-title">{t("body_composition")}</h2>
  <div class="card">{weight_chart}</div>
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">Current Weight</div>
      <div class="metric-value">{fmt(latest_w)} <span class="metric-unit">kg</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">BMI</div>
      <div class="metric-value" style="color:{bmi_color}">{fmt(bmi)} <span class="metric-unit">{_s(bmi_cat)}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Weight Change Rate</div>
      <div class="metric-value" style="color:{COLORS["danger"]}">{fmt(regression.get("kg_per_month"))} <span class="metric-unit">kg/mo</span></div>
      <div class="metric-note">R\u00b2 = {fmt(r2, 3)}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Body Fat</div>
      <div class="metric-value">{fmt(safe_get(bf, "stats", "mean", default=None))} <span class="metric-unit">%</span></div>
      <div class="metric-note">Latest: {fmt(safe_get(bf, "stats", "p95", default=None))}% (p95)</div>
    </div>
  </div>
  {"<div class='card'><div class='card-header'>Weight Gain Decomposition</div>" + decomp_bar + "</div>" if decomp_bar else ""}
  {mk_html}
  {"<div class='card'>" + bf_chart + "</div>" if bf_chart else ""}
  <div class="ai-narrative" id="narrative-body-composition"></div>
</div>'''


def section_cardiovascular(base, adv):
    """Cardiovascular section with RHR chart, HR zones, VO2 max."""
    hr = base.get("heart_rate", {})
    if not hr:
        return ""

    rhr = hr.get("resting_hr", {})
    rhr_monthly = hr.get("resting_hr_monthly", {})
    zones = hr.get("zone_distribution", {})
    vo2 = safe_get(base, "respiratory", "vo2max", default={})
    workouts = base.get("workouts", {})

    # RHR monthly line chart
    rhr_chart = ""
    if rhr_monthly:
        months = sorted(rhr_monthly.keys())
        rhr_vals = [rhr_monthly[m].get("mean") for m in months]
        rhr_chart = svg_line_chart(rhr_vals, width=650, height=200, color=COLORS["chart_1"],
                                   x_labels=months, title="Resting Heart Rate Monthly Trend (bpm)", fill=True)

    # HR zone donut
    zone_donut = ""
    if zones:
        zone_items = [
            ("Below Zone 1", zones.get("below_zone1", {}).get("pct", 0), COLORS["text_muted"]),
            ("Recovery (50-60%)", zones.get("zone1_recovery_50_60", {}).get("pct", 0), COLORS["chart_2"]),
            ("Fat Burn (60-70%)", zones.get("zone2_fatburn_60_70", {}).get("pct", 0), COLORS["chart_3"]),
            ("Aerobic (70-80%)", zones.get("zone3_aerobic_70_80", {}).get("pct", 0), COLORS["chart_5"]),
            ("Threshold (80-90%)", zones.get("zone4_threshold_80_90", {}).get("pct", 0), COLORS["chart_1"]),
            ("Max (90-100%)", zones.get("zone5_max_90_100", {}).get("pct", 0), COLORS["chart_6"]),
        ]
        zone_items = [(l, v, c) for l, v, c in zone_items if v > 0]
        zone_donut = svg_donut_chart(zone_items, size=220, title="")

    # VO2 Max assessment
    vo2_html = ""
    if vo2:
        vo2_val = vo2.get("mean", 0)
        # Percentile assessment for male 20-29
        # Poor < 34, Fair 34-40, Good 40-46, Excellent 46-52, Superior > 52
        if vo2_val < 34:
            vo2_cat = "Poor"
            vo2_color = COLORS["danger"]
        elif vo2_val < 40:
            vo2_cat = "Fair"
            vo2_color = COLORS["warning"]
        elif vo2_val < 46:
            vo2_cat = "Good"
            vo2_color = COLORS["chart_3"]
        elif vo2_val < 52:
            vo2_cat = "Excellent"
            vo2_color = COLORS["success"]
        else:
            vo2_cat = "Superior"
            vo2_color = COLORS["success"]
        vo2_html = f'''<div class="metric-card">
  <div class="metric-label">VO2 Max</div>
  <div class="metric-value" style="color:{vo2_color}">{fmt(vo2_val)} <span class="metric-unit">mL/kg/min</span></div>
  <div class="metric-note">Category: {vo2_cat} | Range: {fmt(vo2.get("min"))}-{fmt(vo2.get("max"))}</div>
</div>'''

    # HR Recovery from workouts
    recovery_html = ""
    wo = workouts.get("individual", [])
    recoveries = [(w.get("type", "?"), w.get("recovery_delta", None)) for w in wo if w.get("recovery_delta") is not None]
    if recoveries:
        rec_items = [(t[:15], abs(d), COLORS["chart_2"] if d < 20 else COLORS["chart_3"]) for t, d in recoveries[:8]]
        recovery_html = f'<div class="card"><div class="card-header">HR Recovery (bpm drop in 15 min post-workout)</div>{svg_horizontal_bar(rec_items, width=500, bar_height=24)}</div>'

    # Circadian
    circ = base.get("circadian_rhythm", {})
    day_night_ratio = circ.get("day_night_ratio")
    dipping = circ.get("dipping_pattern", "")
    dn_diff = circ.get("day_night_difference")

    # RHR assessment for metric card display
    rhr_mean = rhr.get("mean", 0)
    rhr_cat = "Excellent" if rhr_mean < 60 else "Good" if rhr_mean < 70 else "Average" if rhr_mean < 80 else "Above Average" if rhr_mean < 90 else "High"

    return f'''<div class="section" id="cardiovascular">
  <h2 class="section-title">{t("cardiovascular")}</h2>
  {"<div class='card'>" + rhr_chart + "</div>" if rhr_chart else ""}
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">Resting Heart Rate</div>
      <div class="metric-value">{fmt(rhr_mean)} <span class="metric-unit">bpm</span></div>
      <div class="metric-note">Range: {fmt(rhr.get("p5"))}-{fmt(rhr.get("p95"))} | Category: {rhr_cat}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Max HR (est.)</div>
      <div class="metric-value">{hr.get("estimated_max_hr", "?")} <span class="metric-unit">bpm</span></div>
      <div class="metric-note">Observed max: {fmt(hr.get("overall", {}).get("max"))} bpm</div>
    </div>
    {vo2_html}
    <div class="metric-card">
      <div class="metric-label">Day/Night HR Ratio</div>
      <div class="metric-value">{fmt(day_night_ratio, 2)}</div>
      <div class="metric-note">Pattern: {_s(dipping)} | Diff: {fmt(dn_diff, 0)} bpm</div>
    </div>
  </div>
  {"<div class='card'><div class='card-header'>Heart Rate Zone Distribution</div>" + zone_donut + "</div>" if zone_donut else ""}
  {recovery_html}
  <div class="ai-narrative" id="narrative-cardiovascular"></div>
</div>'''


def section_autonomic(base, adv):
    """Autonomic nervous system: HRV, Poincare, DFA, nocturnal HR."""
    hrv = base.get("heart_rate_variability", {})
    if not hrv:
        return ""

    overall = hrv.get("overall", {})
    monthly = hrv.get("monthly", {})
    nd = adv.get("nonlinear_dynamics", {})
    poincare = nd.get("hrv_poincare", {})
    dfa = nd.get("hr_dfa", {})
    circ = base.get("circadian_rhythm", {})
    noct_monthly = circ.get("nocturnal_hr_monthly_trend", {})

    # HRV monthly line chart
    hrv_chart = ""
    if monthly:
        months = sorted(monthly.keys())
        hrv_vals = [monthly[m].get("mean") for m in months]
        hrv_chart = svg_line_chart(hrv_vals, width=650, height=200, color=COLORS["chart_4"],
                                   x_labels=months, title="HRV SDNN Monthly Trend (ms)", fill=True)

    # Nocturnal HR monthly
    noct_chart = ""
    if noct_monthly:
        noct_months = sorted(noct_monthly.keys())
        noct_vals = [noct_monthly[m].get("mean") for m in noct_months]
        noct_chart = svg_line_chart(noct_vals, width=650, height=180, color=COLORS["chart_2"],
                                    x_labels=noct_months, title="Nocturnal HR Monthly Trend (bpm)", fill=True)

    # Poincare plot
    poincare_svg = ""
    if poincare:
        poincare_svg = svg_poincare(poincare.get("sd1_ms"), poincare.get("sd2_ms"), size=200)

    mean_hrv = overall.get("mean", 0)

    return f'''<div class="section" id="autonomic-nervous-system">
  <h2 class="section-title">{t("autonomic_ns")}</h2>
  {"<div class='card'>" + hrv_chart + "</div>" if hrv_chart else ""}
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label"><abbr title="Standard Deviation of NN intervals">SDNN</abbr> Mean</div>
      <div class="metric-value">{fmt(mean_hrv)} <span class="metric-unit">ms</span></div>
      <div class="metric-note">Median: {fmt(overall.get("median"))} | p5-p95: {fmt(overall.get("p5"))}-{fmt(overall.get("p95"))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">DFA \u03b1</div>
      <div class="metric-value">{fmt(dfa.get("alpha"), 3) if dfa else "\u2014"}</div>
      <div class="metric-note">{_s(dfa.get("interpretation", "").replace("_", " ")) if dfa else ""}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">CSI / CVI</div>
      <div class="metric-value" style="font-size:20px">{fmt(poincare.get("csi"), 2)} / {fmt(poincare.get("cvi"), 2)}</div>
      <div class="metric-note">Sympatho-vagal balance indices</div>
    </div>
  </div>
  {"<div class='card'><div class='card-header'>Poincar&eacute; Plot (SD1 vs SD2)</div>" + poincare_svg + "</div>" if poincare_svg else ""}
  {"<div class='card'>" + noct_chart + "</div>" if noct_chart else ""}
  <div class="ai-narrative" id="narrative-autonomic"></div>
</div>'''


def section_glucose(base, adv):
    """Blood glucose / CGM section."""
    glucose = base.get("glucose", {})
    if not glucose:
        return ""

    overall = glucose.get("overall", {})
    tir = glucose.get("time_in_range", {})
    weekly = glucose.get("weekly_pattern", {})
    daily = glucose.get("daily_summaries", [])
    circ = base.get("circadian_rhythm", {})
    glucose_24h = circ.get("glucose_24h", {})
    adv_g = adv.get("advanced_glucose", {})
    wo_resp = glucose.get("workout_response", [])

    # TIR donut
    tir_donut = ""
    if tir:
        tir_items = [
            ("Very Low (<54)", tir.get("very_low_lt54", {}).get("pct", 0), COLORS["danger"]),
            ("Low (54-70)", tir.get("low_54_70", {}).get("pct", 0), COLORS["chart_1"]),
            ("Target (70-180)", tir.get("target_70_180", {}).get("pct", 0), COLORS["success"]),
            ("High (181-250)", tir.get("high_181_250", {}).get("pct", 0), COLORS["warning"]),
            ("Very High (>250)", tir.get("very_high_gt250", {}).get("pct", 0), COLORS["chart_6"]),
        ]
        tir_items = [(l, v, c) for l, v, c in tir_items if v > 0]
        tir_donut = svg_donut_chart(tir_items, size=220)

    # TIR stacked bar
    tir_bar = ""
    if tir:
        tir_bar_items = [
            ("Very Low", tir.get("very_low_lt54", {}).get("pct", 0), COLORS["danger"]),
            ("Low", tir.get("low_54_70", {}).get("pct", 0), COLORS["chart_1"]),
            ("In Range", tir.get("target_70_180", {}).get("pct", 0), COLORS["success"]),
            ("High", tir.get("high_181_250", {}).get("pct", 0), COLORS["warning"]),
            ("Very High", tir.get("very_high_gt250", {}).get("pct", 0), COLORS["chart_6"]),
        ]
        tir_bar = svg_stacked_bar(tir_bar_items, width=500, height=28)

    # 24h glucose circadian curve
    circadian_chart = ""
    if glucose_24h:
        circadian_chart = svg_circadian_curve(glucose_24h, width=650, height=220,
                                               color=COLORS["chart_5"], label="24-Hour Glucose Profile (mg/dL)")

    # Metric cards
    lbgi_hbgi = adv_g.get("lbgi_hbgi", {})
    conga = {k: adv_g.get(k, {}) for k in ["conga_1h", "conga_2h", "conga_4h"]}
    gvp = adv_g.get("gvp", {})
    roc = adv_g.get("rate_of_change", {})

    # Weekly pattern heatmap
    weekly_html = ""
    if weekly:
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        rows = ""
        for day in days_order:
            d = weekly.get(day, {})
            mean_g = d.get("mean", 0)
            tir_pct = d.get("tir_pct", 0)
            above = d.get("above_180_pct", 0)
            # Color coding based on mean
            if mean_g < 100:
                bg = COLORS["success_bg"]
            elif mean_g < 110:
                bg = "#fff"
            else:
                bg = COLORS["warning_bg"]
            rows += f'<tr><td>{day}</td><td style="background:{bg};font-weight:600">{fmt(mean_g)}</td><td>{fmt(d.get("sd"))}</td><td>{fmt(tir_pct)}%</td><td>{fmt(above)}%</td></tr>'
        weekly_html = f'''<table class="data-table">
<thead><tr><th>Day</th><th>Mean (mg/dL)</th><th>SD</th><th>TIR %</th><th>&gt;180 %</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    # Daily summaries table (last 10)
    daily_html = ""
    if daily:
        rows = ""
        for d in daily[-10:]:
            cv_color = COLORS["danger"] if d.get("cv_pct", 0) > 36 else COLORS["warning"] if d.get("cv_pct", 0) > 25 else COLORS["text"]
            rows += f'''<tr>
  <td>{_s(d.get("date"))}</td>
  <td>{fmt(d.get("mean"))}</td>
  <td>{fmt(d.get("min"))}-{fmt(d.get("max"))}</td>
  <td>{fmt(d.get("range"))}</td>
  <td style="color:{cv_color}">{fmt(d.get("cv_pct"))}%</td>
  <td>{fmt(d.get("tir_pct"))}%</td>
  <td>{d.get("n", "?")}</td>
</tr>'''
        daily_html = f'''<table class="data-table">
<thead><tr><th>Date</th><th>Mean</th><th>Range</th><th>Swing</th><th>CV%</th><th>TIR%</th><th>Readings</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    # Workout response
    wo_html = ""
    if wo_resp:
        rows = ""
        for w in wo_resp:
            rows += f'<tr><td>{_s(w.get("date",""))}</td><td>{_s(w.get("type",""))}</td><td>{fmt(w.get("pre_mean"))}</td><td>{fmt(w.get("during_mean"))}</td><td>{fmt(w.get("post_mean"))}</td></tr>'
        wo_html = f'''<div class="section-subtitle">Glucose-Exercise Interaction</div>
<table class="data-table">
<thead><tr><th>Date</th><th>Type</th><th>Pre</th><th>During</th><th>Post</th></tr></thead>
<tbody>{rows}</tbody></table>'''

    return f'''<div class="section" id="blood-glucose">
  <h2 class="section-title">{t("glucose_cgm")}</h2>
  <div class="card-grid-2">
    <div class="card"><div class="card-header">Time in Range</div>{tir_donut}{tir_bar}</div>
    <div class="card">{circadian_chart if circadian_chart else "<p>No 24h glucose data</p>"}</div>
  </div>
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">Mean Glucose</div>
      <div class="metric-value">{fmt(overall.get("mean"))} <span class="metric-unit">mg/dL</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">eA1c / GMI</div>
      <div class="metric-value" style="font-size:20px">{fmt(glucose.get("eA1c"))}% / {fmt(glucose.get("gmi"))}%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">CV%</div>
      <div class="metric-value">{fmt(glucose.get("cv_pct"))}% <span class="metric-unit">{_s(glucose.get("cv_stability",""))}</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Mean Amplitude of Glycemic Excursions">MAGE</abbr></div>
      <div class="metric-value">{fmt(glucose.get("mage"))} <span class="metric-unit">mg/dL</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Mean of Daily Differences">MODD</abbr></div>
      <div class="metric-value">{fmt(glucose.get("modd"))} <span class="metric-unit">mg/dL</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">GRI</div>
      <div class="metric-value">{fmt(glucose.get("gri"))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Low Blood Glucose Index">LBGI</abbr> / <abbr title="High Blood Glucose Index">HBGI</abbr></div>
      <div class="metric-value" style="font-size:20px">{fmt(lbgi_hbgi.get("lbgi"))} / {fmt(lbgi_hbgi.get("hbgi"))}</div>
      <div class="metric-note">{_s(lbgi_hbgi.get("lbgi_risk",""))} / {_s(lbgi_hbgi.get("hbgi_risk",""))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Continuous Overall Net Glycemic Action">CONGA</abbr> 1h/2h/4h</div>
      <div class="metric-value" style="font-size:16px">{fmt(conga.get("conga_1h",{}).get("conga"))} / {fmt(conga.get("conga_2h",{}).get("conga"))} / {fmt(conga.get("conga_4h",{}).get("conga"))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Glycemic Variability Percentage">GVP</abbr></div>
      <div class="metric-value">{fmt(gvp.get("gvp_pct"))}%</div>
      <div class="metric-note">{_s(gvp.get("interpretation","").replace("_"," "))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Rate of Change</div>
      <div class="metric-value" style="font-size:14px">Rise: +{fmt(roc.get("max_rise"))} | Fall: {fmt(roc.get("max_fall"))}</div>
      <div class="metric-note">Rapid rise >2: {fmt(roc.get("pct_rapid_rise_gt2"))}% | Rapid fall: {fmt(roc.get("pct_rapid_fall_lt_neg2"))}%</div>
    </div>
  </div>
  {"<div class='card'><div class='card-header'>Weekly Glucose Pattern</div>" + weekly_html + "</div>" if weekly_html else ""}
  {"<div class='card'><div class='card-header'>Daily Summaries (Last 10 Days)</div>" + daily_html + "</div>" if daily_html else ""}
  {"<div class='card'>" + wo_html + "</div>" if wo_html else ""}
  <div class="ai-narrative" id="narrative-glucose"></div>
</div>'''


def section_activity(base, adv):
    """Activity & Exercise section."""
    activity = base.get("activity", {})
    if not activity:
        return ""

    steps = activity.get("daily_steps", {})
    stats = steps.get("stats", {})
    monthly = steps.get("monthly", {})
    weekly = steps.get("weekly_pattern", {})
    workouts = base.get("workouts", {})
    act_sum = activity.get("activity_summaries", {})
    act_cal = activity.get("active_calories", {})
    mk = safe_get(adv, "trend_tests", "steps_weekly", default={})

    # Monthly steps bar chart
    steps_chart = ""
    if monthly:
        months = sorted(monthly.keys())
        step_vals = [monthly[m].get("mean", 0) for m in months]
        steps_chart = svg_bar_chart_vertical(step_vals, months, width=650, height=220,
                                              color=COLORS["chart_1"], title="Monthly Average Daily Steps")

    # Weekly pattern (Mon-Sun) horizontal bars
    weekly_chart = ""
    if weekly:
        days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_items = [(d, weekly.get(d, {}).get("mean", 0), COLORS["chart_2"]) for d in days_order]
        weekly_chart = svg_horizontal_bar(weekly_items, width=450, bar_height=26,
                                          max_val=max(v for _, v, _ in weekly_items) * 1.1 if weekly_items else 1)

    # Workout type comparison
    wo_chart = ""
    if workouts.get("individual"):
        type_stats = {}
        for w in workouts["individual"]:
            wtype = w.get("type", "Unknown")
            if wtype not in type_stats:
                type_stats[wtype] = {"count": 0, "total_dur": 0}
            type_stats[wtype]["count"] += 1
            type_stats[wtype]["total_dur"] += w.get("duration_min", 0)
        wo_items = [(wt, s["count"], COLORS["chart_3"]) for wt, s in sorted(type_stats.items(), key=lambda x: -x[1]["count"])]
        if wo_items:
            wo_chart = svg_horizontal_bar(wo_items[:8], width=450, bar_height=26)

    mean_steps = stats.get("mean", 0)
    over_10k = steps.get("days_over_10k_pct", 0)
    under_5k = steps.get("days_under_5k", 0)
    total_days = stats.get("count", 1)

    # Exercise minutes
    ex_min = safe_get(act_sum, "exercise_min", "mean", default=0)
    stand_h = safe_get(act_sum, "stand_hours", "mean", default=0)
    wo_total = workouts.get("total", 0)

    return f'''<div class="section" id="activity-exercise">
  <h2 class="section-title">{t("activity")}</h2>
  {"<div class='card'>" + steps_chart + "</div>" if steps_chart else ""}
  <div class="card-grid-2">
    {"<div class='card'><div class='card-header'>Weekly Step Pattern (Mon\u2013Sun)</div>" + weekly_chart + "</div>" if weekly_chart else ""}
    {"<div class='card'><div class='card-header'>Workout Types</div>" + wo_chart + "</div>" if wo_chart else ""}
  </div>
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">Avg Daily Steps</div>
      <div class="metric-value">{fmt(mean_steps, 0)}</div>
      <div class="metric-note">Median: {fmt(stats.get("median"), 0)} | Max: {fmt(stats.get("max"), 0)}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Days Over 10K</div>
      <div class="metric-value">{fmt(over_10k)}%</div>
      <div class="metric-note">{steps.get("days_over_10k", 0)} of {total_days} days</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Exercise Minutes</div>
      <div class="metric-value">{fmt(ex_min)} <span class="metric-unit">min/day</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Standing Hours</div>
      <div class="metric-value">{fmt(stand_h)} <span class="metric-unit">hr/day</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Active Calories</div>
      <div class="metric-value">{fmt(safe_get(act_cal, "daily_stats", "mean", default=0), 0)} <span class="metric-unit">kcal/day</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Workouts</div>
      <div class="metric-value">{wo_total}</div>
      <div class="metric-note">{fmt(wo_total / max(total_days / 30, 1), 1)}/month avg</div>
    </div>
  </div>
  <div class="ai-narrative" id="narrative-activity"></div>
</div>'''


def section_sleep(base):
    """Sleep section with architecture donut, duration chart, efficiency."""
    sleep = base.get("sleep", {})
    if not sleep or not sleep.get("total_nights"):
        return ""

    dur = sleep.get("duration_stats", {})
    deep = sleep.get("deep_stats", {})
    rem = sleep.get("rem_stats", {})
    core = sleep.get("core_stats", {})
    eff = sleep.get("efficiency_stats", {})
    monthly = sleep.get("monthly_trend", {})
    recent = sleep.get("recent_nights", [])

    # Sleep architecture donut
    arch_donut = ""
    deep_h = deep.get("mean", 0)
    rem_h = rem.get("mean", 0)
    core_h = core.get("mean", 0)
    if deep_h or rem_h or core_h:
        arch_items = [
            ("Deep", deep_h, COLORS["chart_2"]),
            ("REM", rem_h, COLORS["chart_4"]),
            ("Core/Light", core_h, COLORS["chart_5"]),
        ]
        arch_donut = svg_donut_chart(arch_items, size=220)

    # Monthly duration line chart
    dur_chart = ""
    if monthly:
        months = sorted(monthly.keys())
        dur_vals = [monthly[m].get("total_h") for m in months]
        eff_vals = [monthly[m].get("efficiency_pct") for m in months]
        dur_chart = svg_line_chart(dur_vals, width=650, height=200, color=COLORS["chart_2"],
                                   x_labels=months, title="Monthly Sleep Duration (hours)", fill=True)

    # Recent nights
    recent_chart = ""
    if recent and len(recent) >= 3:
        r_vals = [n.get("total_h", 0) for n in recent[-20:]]
        r_labels = [n.get("night", "")[-5:] for n in recent[-20:]]
        recent_chart = svg_line_chart(r_vals, width=650, height=180, color=COLORS["chart_4"],
                                      x_labels=r_labels, title="Recent Nightly Duration (hours)", fill=True)

    mean_dur = dur.get("mean", 0)
    mean_eff = eff.get("mean", 0)

    return f'''<div class="section" id="sleep">
  <h2 class="section-title">{t("sleep")}</h2>
  <div class="card-grid-2">
    <div class="card"><div class="card-header">Sleep Architecture (Average Night)</div>{arch_donut}</div>
    <div class="card">{dur_chart if dur_chart else "<p>No monthly sleep data</p>"}</div>
  </div>
  {"<div class='card'>" + recent_chart + "</div>" if recent_chart else ""}
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">Avg Duration</div>
      <div class="metric-value">{fmt(mean_dur)} <span class="metric-unit">hours</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Efficiency</div>
      <div class="metric-value">{fmt(mean_eff)}%</div>
      <div class="metric-note">Target: &gt;85%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Deep Sleep</div>
      <div class="metric-value">{fmt(deep_h)} <span class="metric-unit">hours</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">REM Sleep</div>
      <div class="metric-value">{fmt(rem_h)} <span class="metric-unit">hours</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Nights Tracked</div>
      <div class="metric-value">{sleep.get("total_nights", 0)}</div>
    </div>
  </div>
  <div class="ai-narrative" id="narrative-sleep"></div>
</div>'''


def section_circadian(base, adv):
    """Circadian rhythm quantification."""
    circ = base.get("circadian_rhythm", {})
    cq = adv.get("circadian_quantification", {})
    if not cq and not circ:
        return ""

    hr_cosinor = cq.get("hr_cosinor", {})
    gl_cosinor = cq.get("glucose_cosinor", {})
    stability = cq.get("hr_rhythm_stability", {})
    hr_24h = circ.get("heart_rate_24h", {})

    # HR 24h circadian curve
    hr_curve = ""
    if hr_24h:
        hr_curve = svg_circadian_curve(hr_24h, width=650, height=220,
                                        color=COLORS["chart_1"], label="24-Hour Heart Rate Profile (bpm)")

    return f'''<div class="section" id="circadian-rhythm">
  <h2 class="section-title">Circadian Rhythm Quantification</h2>
  {"<div class='card'>" + hr_curve + "</div>" if hr_curve else ""}
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label"><abbr title="Midline Estimating Statistic of Rhythm">MESOR</abbr> (HR)</div>
      <div class="metric-value">{fmt(hr_cosinor.get("mesor"))} <span class="metric-unit">bpm</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Amplitude (HR)</div>
      <div class="metric-value">{fmt(hr_cosinor.get("amplitude"))} <span class="metric-unit">bpm</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Acrophase (HR)</div>
      <div class="metric-value">{_s(hr_cosinor.get("acrophase_time", "\u2014"))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label"><abbr title="Interdaily Stability">IS</abbr> / <abbr title="Intradaily Variability">IV</abbr></div>
      <div class="metric-value" style="font-size:18px">{fmt(stability.get("interdaily_stability"), 3)} / {fmt(stability.get("intradaily_variability"), 3)}</div>
      <div class="metric-note">{_s(stability.get("IS_interpretation",""))} / {_s(stability.get("IV_interpretation",""))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Glucose Acrophase</div>
      <div class="metric-value">{_s(gl_cosinor.get("acrophase_time", "\u2014"))}</div>
      <div class="metric-note">Amplitude: {fmt(gl_cosinor.get("amplitude"))} mg/dL</div>
    </div>
  </div>
  <div class="ai-narrative" id="narrative-circadian"></div>
</div>'''


def section_causal_inference(base, adv):
    """Causal inference: Granger, Transfer Entropy, CCM."""
    ci = adv.get("causal_inference", {})
    lag_corr = base.get("lagged_correlations", {})
    if not ci:
        return ""

    # Build comparison table
    rows = ""
    test_pairs = [
        ("Steps \u2192 HR", "granger_steps_causes_hr", "transfer_entropy_steps_to_hr", "ccm_steps_causes_rhr"),
        ("Steps \u2192 RHR", "granger_steps_causes_rhr", "transfer_entropy_steps_to_rhr", "ccm_steps_causes_rhr"),
        ("RHR \u2192 Steps", None, None, "ccm_rhr_causes_steps"),
    ]

    for label, granger_key, te_key, ccm_key in test_pairs:
        # Granger
        g = ci.get(granger_key, {})
        g_result = ""
        if g:
            # Get lag_1 result
            g1 = g.get("lag_1", {})
            sig = "\u2713" if g1.get("significant") else "\u2717"
            color = COLORS["success"] if g1.get("significant") else COLORS["text_muted"]
            g_result = f'<span style="color:{color}">{sig}</span> F={fmt(g1.get("f_statistic"), 2)}, p={fmt(g1.get("p_value"), 4)}'
        else:
            g_result = "\u2014"

        # Transfer Entropy
        te = ci.get(te_key, {})
        te_result = ""
        if te:
            sig = "\u2713" if te.get("significant") else "\u2717"
            color = COLORS["success"] if te.get("significant") else COLORS["text_muted"]
            te_result = f'<span style="color:{color}">{sig}</span> TE={fmt(te.get("te_bits"), 3)} bits, z={fmt(te.get("z_score"), 2)}'
        else:
            te_result = "\u2014"

        # CCM
        ccm = ci.get(ccm_key, {})
        ccm_result = ""
        if ccm:
            evidence = ccm.get("causal_evidence", "none")
            color = COLORS["success"] if evidence != "none" else COLORS["text_muted"]
            sig = "\u2713" if evidence != "none" else "\u2717"
            ccm_result = f'<span style="color:{color}">{sig}</span> {_s(evidence)} (max \u03c1={fmt(ccm.get("max_rho"), 3)})'
        else:
            ccm_result = "\u2014"

        rows += f'<tr><td style="font-weight:600">{_s(label)}</td><td>{g_result}</td><td>{te_result}</td><td>{ccm_result}</td></tr>'

    # Lagged correlations
    lag_html = ""
    if lag_corr:
        lag_items = []
        steps_rhr = lag_corr.get("weekly_steps_to_rhr", {})
        if steps_rhr:
            for lag_key, lag_data in sorted(steps_rhr.items()):
                lag_items.append(f'{lag_key.replace("_", " ")}: r={fmt(lag_data.get("r"), 3)} (n={lag_data.get("n", "?")})')
        sleep_hrv = lag_corr.get("sleep_to_next_day_hrv", {})
        if sleep_hrv:
            lag_items.append(f'Sleep\u2192HRV: r={fmt(sleep_hrv.get("r"), 3)}')
            lag_items.append(f'Short sleep HRV: {fmt(sleep_hrv.get("short_sleep_lt6h_hrv"))} ms | Normal: {fmt(sleep_hrv.get("normal_sleep_6_8h_hrv"))} ms | Long: {fmt(sleep_hrv.get("long_sleep_gt8h_hrv"))} ms')
        if lag_items:
            lag_html = '<div class="section-subtitle">Lagged Correlations</div><ul style="font-size:13px;color:' + COLORS["text_secondary"] + ';line-height:2">'
            lag_html += "".join(f"<li>{_s(item)}</li>" for item in lag_items) + "</ul>"

    return f'''<div class="section" id="causal-inference">
  <h2 class="section-title">Causal Inference</h2>
  <div class="card">
    <div class="card-header">Three-Method Causal Analysis Comparison</div>
    <table class="data-table">
      <thead><tr><th>Relationship</th><th>Granger Causality</th><th>Transfer Entropy</th><th>Convergent Cross Mapping</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  {lag_html}
  <div class="ai-narrative" id="narrative-causal-inference"></div>
</div>'''


def section_nonlinear_dynamics(base, adv):
    """Nonlinear dynamics: Sample Entropy, DFA, MSE, Poincare."""
    nd = adv.get("nonlinear_dynamics", {})
    if not nd:
        return ""

    hr_se = nd.get("hr_sample_entropy", {})
    gl_se = nd.get("glucose_sample_entropy", {})
    hr_dfa = nd.get("hr_dfa", {})
    poincare = nd.get("hrv_poincare", {})
    mse = nd.get("multiscale_entropy", {})

    # MSE chart
    mse_chart = ""
    if mse:
        mse_chart = svg_multiscale_entropy(mse, width=400, height=140)

    # DFA interpretation scale
    dfa_scale = ""
    if hr_dfa:
        alpha = hr_dfa.get("alpha", 0)
        # Build a visual scale
        pos_pct = min(max(alpha / 2.0 * 100, 0), 100)
        dfa_scale = f'''<div style="margin:12px 0">
<div style="display:flex;justify-content:space-between;font-size:10px;color:{COLORS["text_muted"]}">
  <span>0 (white noise)</span><span>0.5 (anti-corr)</span><span>1.0 (1/f noise)</span><span>1.5 (Brownian)</span><span>2.0</span>
</div>
<div style="background:{COLORS["border_light"]};height:12px;border-radius:6px;position:relative;margin-top:4px">
  <div style="position:absolute;left:{pos_pct:.1f}%;top:-2px;width:16px;height:16px;border-radius:50%;background:{COLORS["primary"]};border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,0.3);transform:translateX(-50%)"></div>
  <div style="background:linear-gradient(to right,{COLORS["info"]},{COLORS["success"]},{COLORS["warning"]},{COLORS["danger"]});height:100%;border-radius:6px;opacity:0.3"></div>
</div>
<div style="text-align:center;margin-top:6px;font-size:13px;font-weight:600;color:{COLORS["primary"]}">\u03b1 = {fmt(alpha, 4)}</div>
</div>'''

    return f'''<div class="section" id="nonlinear-dynamics">
  <h2 class="section-title">Nonlinear Dynamics</h2>
  <div class="card-grid" style="margin-bottom:16px">
    <div class="metric-card">
      <div class="metric-label">HR Sample Entropy</div>
      <div class="metric-value">{fmt(hr_se.get("value"), 3)}</div>
      <div class="metric-note">{_s(hr_se.get("interpretation","").replace("_"," "))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Glucose Sample Entropy</div>
      <div class="metric-value">{fmt(gl_se.get("value"), 3)}</div>
      <div class="metric-note">{_s(gl_se.get("interpretation","").replace("_"," "))}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">DFA \u03b1 (HR)</div>
      <div class="metric-value">{fmt(hr_dfa.get("alpha"), 4)}</div>
      <div class="metric-note">{_s(hr_dfa.get("interpretation","").replace("_"," "))}</div>
    </div>
  </div>
  {"<div class='card'><div class='card-header'>DFA Alpha Scale</div>" + dfa_scale + "</div>" if dfa_scale else ""}
  {"<div class='card'><div class='card-header'>Multiscale Entropy Profile</div>" + mse_chart + "</div>" if mse_chart else ""}
  <div class="ai-narrative" id="narrative-nonlinear"></div>
</div>'''


def section_biological_age(base, adv):
    """Biological and fitness age comparison."""
    bio_models = adv.get("biological_age_models", {})
    if not bio_models:
        return ""

    fitness = bio_models.get("fitness_age", {})
    bio = bio_models.get("biological_age", {})
    allo = bio_models.get("allostatic_load", {})
    chrono = bio.get("chronological_age", 0)
    bio_age = bio.get("biological_age", 0)
    fit_age = fitness.get("fitness_age", 0)

    # Big number comparison
    bio_color = COLORS["danger"] if bio_age > chrono + 5 else COLORS["warning"] if bio_age > chrono else COLORS["success"]
    fit_color = COLORS["danger"] if fit_age > chrono + 10 else COLORS["warning"] if fit_age > chrono else COLORS["success"]

    # Component breakdown
    components = bio.get("components", {})
    comp_rows = ""
    comp_labels = {
        "rhr_delta": "Resting Heart Rate",
        "hrv_delta": "Heart Rate Variability",
        "vo2max_delta": "VO2 Max",
        "bmi_delta": "BMI",
        "activity_delta": "Activity Level",
        "sleep_delta": "Sleep Quality",
    }
    for key, label in comp_labels.items():
        delta = components.get(key, 0)
        color = COLORS["danger"] if delta > 2 else COLORS["warning"] if delta > 0 else COLORS["success"]
        comp_rows += f'<tr><td>{_s(label)}</td><td style="color:{color};font-weight:600">{fmt(delta, 1)} years</td></tr>'

    # Allostatic load bar
    allo_html = ""
    if allo:
        score = allo.get("score", 0)
        max_score = allo.get("max_score", 7)
        details = allo.get("details", {})
        bar_items = []
        for key, info in details.items():
            flagged = info.get("flagged", False)
            bar_items.append((key.upper(), 1, COLORS["danger"] if flagged else COLORS["success"]))
        allo_bar = svg_stacked_bar(bar_items, width=400, height=24, labels=True)

        allo_html = f'''<div class="card">
  <div class="card-header">Allostatic Load Index</div>
  <div class="metric-value" style="margin-bottom:8px">{score} <span class="metric-unit">/ {max_score} ({_s(allo.get("risk_level",""))})</span></div>
  {allo_bar}
  <div style="margin-top:8px;font-size:12px;color:{COLORS["text_muted"]}">Green = within normal limits, Red = flagged</div>
</div>'''

    return f'''<div class="section" id="biological-age">
  <h2 class="section-title">Biological &amp; Fitness Age</h2>
  <div class="card" style="margin-bottom:16px">
    <div class="comparison-row">
      <div class="comparison-box" style="background:{COLORS["info_bg"]}">
        <div class="comp-value" style="color:{COLORS["info"]}">{fmt(chrono, 1)}</div>
        <div class="comp-label" style="color:{COLORS["info"]}">Chronological Age</div>
      </div>
      <div class="comparison-vs">vs</div>
      <div class="comparison-box" style="background:{COLORS["warning_bg"] if bio_age > chrono else COLORS["success_bg"]}">
        <div class="comp-value" style="color:{bio_color}">{fmt(bio_age, 1)}</div>
        <div class="comp-label" style="color:{bio_color}">Biological Age</div>
      </div>
      <div class="comparison-vs">vs</div>
      <div class="comparison-box" style="background:{COLORS["danger_bg"] if fit_age > chrono + 10 else COLORS["warning_bg"]}">
        <div class="comp-value" style="color:{fit_color}">{fmt(fit_age, 1)}</div>
        <div class="comp-label" style="color:{fit_color}">Fitness Age</div>
      </div>
    </div>
  </div>
  <div class="card-grid-2">
    <div class="card">
      <div class="card-header">Component Breakdown (Biological Age)</div>
      <table class="data-table">
        <thead><tr><th>Component</th><th>Age Delta</th></tr></thead>
        <tbody>{comp_rows}</tbody>
      </table>
    </div>
    {allo_html}
  </div>
  <div class="ai-narrative" id="narrative-biological-age"></div>
</div>'''


def section_correlation_matrix(base):
    """Cross-metric correlation heatmap."""
    corr = base.get("correlations", {})
    if not corr:
        return ""

    labels = list(corr.keys())
    matrix = []
    for row_key in labels:
        row = []
        for col_key in labels:
            row.append(corr.get(row_key, {}).get(col_key, 0))
        matrix.append(row)

    heatmap = svg_heatmap(matrix, labels, labels, width=520, cell_size=60)

    # Find top 3 significant off-diagonal correlations
    pairs = []
    for i, rk in enumerate(labels):
        for j, ck in enumerate(labels):
            if i < j:
                val = corr.get(rk, {}).get(ck, 0)
                pairs.append((rk, ck, val))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)

    top3_html = ""
    explanations = {
        ("Steps", "ActiveCal"): "More steps naturally burn more active calories -- these track together.",
        ("AvgHR", "RHR"): "Higher average heart rate elevates resting measurements; both reflect cardiovascular load.",
        ("RHR", "HRV"): "Strong inverse relationship: lower resting HR allows greater beat-to-beat variability (vagal tone).",
        ("AvgHR", "HRV"): "Higher average HR is associated with lower HRV, reflecting sympathetic dominance.",
        ("Steps", "AvgHR"): "Physical activity raises heart rate proportionally to effort.",
        ("RHR", "Glucose"): "Inverse relationship may reflect metabolic efficiency: lower RHR associated with better glucose regulation.",
        ("HRV", "Glucose"): "Higher HRV (better autonomic function) correlates with glucose levels, possibly mediated by parasympathetic regulation of insulin secretion.",
    }

    for rk, ck, val in pairs[:3]:
        direction = "positive" if val > 0 else "negative"
        strength = "strong" if abs(val) > 0.5 else "moderate" if abs(val) > 0.3 else "weak"
        explanation = explanations.get((rk, ck), explanations.get((ck, rk), ""))
        top3_html += f'''<div style="margin-bottom:8px;font-size:13px;color:{COLORS["text_secondary"]}">
  <strong>{_s(rk)} \u2194 {_s(ck)}</strong>: r={fmt(val, 3)} ({strength} {direction}).
  {_s(explanation)}
</div>'''

    return f'''<div class="section" id="correlation-matrix">
  <h2 class="section-title">Cross-Metric Correlation Matrix</h2>
  <div class="card" style="text-align:center">{heatmap}</div>
  <div class="card">
    <div class="card-header">Top 3 Significant Correlations</div>
    {top3_html}
  </div>
  <div class="ai-narrative" id="narrative-correlations"></div>
</div>'''


def section_trend_momentum(base):
    """Trend momentum table with sparklines."""
    tm = base.get("trend_momentum", {})
    if not tm:
        return ""

    metric_labels = {
        "steps": ("Daily Steps", "steps"),
        "active_cal": ("Active Calories", "kcal"),
        "avg_hr": ("Average HR", "bpm"),
        "rhr": ("Resting HR", "bpm"),
    }

    rows = ""
    for key, (label, unit) in metric_labels.items():
        d = tm.get(key, {})
        if not d:
            continue
        v30 = d.get("last_30d")
        v90 = d.get("last_90d")
        v180 = d.get("last_180d")
        v_all = d.get("all_time")

        # Sparkline from available periods
        spark_vals = [v for v in [v_all, v180, v90, v30] if v is not None]
        spark = svg_sparkline(spark_vals, width=80, height=24, color=COLORS["primary"])

        # Trend arrow (30d vs all-time)
        arrow = trend_arrow(v30, v_all) if v30 and v_all else ""

        rows += f'''<tr>
  <td style="font-weight:600">{_s(label)}</td>
  <td>{fmt(v30)} {_s(unit)}</td>
  <td>{fmt(v90)} {_s(unit)}</td>
  <td>{fmt(v180)} {_s(unit)}</td>
  <td>{fmt(v_all)} {_s(unit)}</td>
  <td>{arrow}</td>
  <td>{spark}</td>
</tr>'''

    return f'''<div class="section" id="trend-momentum">
  <h2 class="section-title">Trend Momentum</h2>
  <div class="card">
    <table class="data-table">
      <thead><tr><th>Metric</th><th>Last 30d</th><th>Last 90d</th><th>Last 180d</th><th>All Time</th><th>Trend</th><th>Sparkline</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>'''


def section_data_quality(base):
    """Data quality stream table with badges and warnings."""
    dq = base.get("data_quality", {})
    if not dq:
        return ""

    streams = dq.get("streams", {})
    warnings = dq.get("warnings", [])

    # Stream table
    rows = ""
    for name, info in sorted(streams.items()):
        reliability = info.get("reliability_grade", "unknown")
        badge_class = f"badge-{reliability}" if reliability in ["high", "moderate", "low"] else "badge-low"
        span = info.get("data_span", {})
        rows += f'''<tr>
  <td style="font-weight:600">{_s(name.replace("_"," ").title())}</td>
  <td>{info.get("total_readings", 0):,}</td>
  <td>{fmt(info.get("completeness_pct"))}%</td>
  <td>{_s(span.get("first",""))} \u2013 {_s(span.get("last",""))}</td>
  <td>{info.get("longest_gap_days", "\u2014")} days</td>
  <td><span class="badge {badge_class}">{_s(reliability)}</span></td>
</tr>'''

    # Warnings
    warn_html = ""
    if warnings:
        warn_items = "".join(f'<li style="margin-bottom:4px">{_s(w)}</li>' for w in warnings)
        warn_html = f'''<div class="section-subtitle" style="color:{COLORS["warning"]}">Data Quality Warnings</div>
<ul style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.8">{warn_items}</ul>'''

    # Missing sections note
    missing = []
    all_keys = ["heart_rate", "heart_rate_variability", "glucose", "sleep", "activity",
                "body_composition", "workouts", "respiratory"]
    for k in all_keys:
        if not base.get(k):
            missing.append(k.replace("_", " ").title())
    missing_html = ""
    if missing:
        missing_html = f'''<div style="margin-top:12px;font-size:13px;color:{COLORS["text_muted"]}">
<strong>Sections not available:</strong> {", ".join(missing)}</div>'''

    return f'''<div class="section" id="data-quality">
  <h2 class="section-title">Data Quality Assessment</h2>
  <div class="card">
    <table class="data-table">
      <thead><tr><th>Stream</th><th>Readings</th><th>Completeness</th><th>Period</th><th>Longest Gap</th><th>Reliability</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  {warn_html}
  {missing_html}
</div>'''


def section_methodology(adv):
    """Methodology: methods applied and references."""
    methods = adv.get("methods_applied", [])
    refs = adv.get("references", [])
    reqs = adv.get("data_requirements", {})
    if not methods and not refs:
        return ""

    methods_list = "".join(f'<li>{_s(m)}</li>' for m in methods)
    refs_list = "".join(f'<li style="font-size:12px">{_s(r)}</li>' for r in refs)

    # Data requirements
    req_rows = ""
    if reqs:
        for key, info in sorted(reqs.items()):
            met = info.get("met", False)
            badge = f'<span class="badge badge-high">Met</span>' if met else f'<span class="badge badge-low">Not Met</span>'
            req_rows += f'<tr><td>{_s(key.replace("_"," "))}</td><td style="font-size:12px">{_s(info.get("required",""))}</td><td style="font-size:12px">{_s(info.get("actual",""))}</td><td>{badge}</td></tr>'

    return f'''<div class="section" id="methodology">
  <h2 class="section-title">Methodology &amp; References</h2>
  <div class="collapsible-toggle" onclick="this.classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
    {len(methods)} Analytical Methods Applied
  </div>
  <div class="collapsible-content">
    <ol style="font-size:13px;line-height:2;padding-left:20px;color:{COLORS["text_secondary"]}">{methods_list}</ol>
  </div>
  <div class="collapsible-toggle" onclick="this.classList.toggle('open');this.nextElementSibling.classList.toggle('open')">
    {len(refs)} Academic References
  </div>
  <div class="collapsible-content">
    <ol style="font-size:12px;line-height:2;padding-left:20px;color:{COLORS["text_muted"]}">{refs_list}</ol>
  </div>
  {"<div class='collapsible-toggle' onclick=\"this.classList.toggle(&apos;open&apos;);this.nextElementSibling.classList.toggle(&apos;open&apos;)\">Data Requirements</div><div class='collapsible-content'><table class='data-table'><thead><tr><th>Test</th><th>Required</th><th>Actual</th><th>Status</th></tr></thead><tbody>" + req_rows + "</tbody></table></div>" if req_rows else ""}
</div>'''


def section_footer():
    """Report footer with disclaimer."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f'''<div class="report-footer" id="footer">
  <strong>Disclaimer:</strong> This report is generated for informational purposes only and does not constitute medical advice.
  All analyses are based on consumer-grade wearable data (Apple Watch) and should not be used for clinical decision-making.
  Consult a healthcare professional for medical concerns. Reference ranges are population-based and may not apply to all individuals.<br>
  <br>
  Generated on {_s(now)} using Apple Health Analysis Pipeline.<br>
  Analytical methods include Mann-Kendall trend tests, Granger causality, transfer entropy, convergent cross mapping,
  sample entropy, DFA, Poincar&eacute; analysis, cosinor modeling, bootstrap confidence intervals, and Bayesian change point detection.
</div>'''


def generate_navigation():
    """Generate sticky sidebar navigation."""
    sections = [
        ("top", "Report Header"),
        ("executive-summary", "Executive Summary"),
        ("health-dashboard", "Health Dashboard"),
        ("risk-stratification", "Risk Stratification"),
        ("disease-screening", "Disease Screening"),
        ("body-composition", "Body Composition"),
        ("cardiovascular", "Cardiovascular"),
        ("autonomic-nervous-system", "Autonomic / HRV"),
        ("blood-glucose", "Blood Glucose"),
        ("activity-exercise", "Activity & Exercise"),
        ("sleep", "Sleep"),
        ("circadian-rhythm", "Circadian Rhythm"),
        ("causal-inference", "Causal Inference"),
        ("nonlinear-dynamics", "Nonlinear Dynamics"),
        ("biological-age", "Bio & Fitness Age"),
        ("correlation-matrix", "Correlations"),
        ("trend-momentum", "Trend Momentum"),
        ("data-quality", "Data Quality"),
        ("methodology", "Methodology"),
        ("overall-recommendations", "Recommendations"),
    ]
    links = "".join(f'<a href="#{sid}">{_s(label)}</a>' for sid, label in sections)
    return f'''<nav class="nav-sidebar">
  <div class="nav-title">Health Report</div>
  {links}
</nav>'''


# ============================================================================
# Main Assembly
# ============================================================================

def generate_html(base, adv, lang="en"):
    """Assemble the full HTML report."""
    global _LANG
    _LANG = lang
    css = generate_css()
    nav = generate_navigation()

    sections = []
    sections.append(section_header(base, adv))
    sections.append(section_executive_summary(base, adv))

    # Only add sections that have data
    s = section_health_dashboard(base)
    if s:
        sections.append(s)

    s = section_risk_stratification(base)
    if s:
        sections.append(s)

    s = section_disease_screening(adv)
    if s:
        sections.append(s)

    s = section_body_composition(base, adv)
    if s:
        sections.append(s)

    s = section_cardiovascular(base, adv)
    if s:
        sections.append(s)

    s = section_autonomic(base, adv)
    if s:
        sections.append(s)

    s = section_glucose(base, adv)
    if s:
        sections.append(s)

    s = section_activity(base, adv)
    if s:
        sections.append(s)

    s = section_sleep(base)
    if s:
        sections.append(s)

    s = section_circadian(base, adv)
    if s:
        sections.append(s)

    s = section_causal_inference(base, adv)
    if s:
        sections.append(s)

    s = section_nonlinear_dynamics(base, adv)
    if s:
        sections.append(s)

    s = section_biological_age(base, adv)
    if s:
        sections.append(s)

    s = section_correlation_matrix(base)
    if s:
        sections.append(s)

    s = section_trend_momentum(base)
    if s:
        sections.append(s)

    s = section_data_quality(base)
    if s:
        sections.append(s)

    s = section_methodology(adv)
    if s:
        sections.append(s)

    # Recommendations section (AI-filled narrative)
    sections.append(f'''<div class="section" id="overall-recommendations">
  <h2 class="section-title">{t("recommendations")}</h2>
  <div class="ai-narrative" id="narrative-recommendations"></div>
</div>''')

    sections.append(section_footer())

    body = "\n".join(sections)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Apple Health Analysis Report</title>
<style>{css}</style>
</head>
<body>
{nav}
<div class="main-content">
{body}
</div>
<script>
// Highlight active nav link on scroll
(function() {{
  var links = document.querySelectorAll('.nav-sidebar a');
  var sections = [];
  links.forEach(function(link) {{
    var id = link.getAttribute('href').substring(1);
    var el = document.getElementById(id);
    if (el) sections.push({{el: el, link: link}});
  }});
  function onScroll() {{
    var scrollY = window.scrollY + 100;
    var active = sections[0];
    for (var i = 0; i < sections.length; i++) {{
      if (sections[i].el.offsetTop <= scrollY) active = sections[i];
    }}
    links.forEach(function(l) {{ l.classList.remove('active'); }});
    if (active) active.link.classList.add('active');
  }}
  window.addEventListener('scroll', onScroll);
  onScroll();
}})();
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate Apple Health HTML Report")
    parser.add_argument("base_json", help="Path to base analysis JSON (from analyze_health.py)")
    parser.add_argument("advanced_json", help="Path to advanced analysis JSON (from advanced_analytics.py)")
    parser.add_argument("-o", "--output", default="health_report.html", help="Output HTML file path")
    parser.add_argument("--lang", default="en", choices=["en", "zh"], help="Report language (en/zh)")
    args = parser.parse_args()

    with open(args.base_json, "r") as f:
        base = json.load(f)
    with open(args.advanced_json, "r") as f:
        adv = json.load(f)

    # Auto-detect language from XML locale if not specified
    locale = base.get("data_overview", {}).get("locale", "")
    if args.lang == "en" and "zh" in locale.lower():
        args.lang = "zh"

    html = generate_html(base, adv, lang=args.lang)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {args.output}")
    print(f"  Base data keys: {len(base)}")
    print(f"  Advanced data keys: {len(adv)}")
    import os
    size_kb = os.path.getsize(args.output) / 1024
    print(f"  File size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
