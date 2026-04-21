from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"

ACCENT = "#E57B2E"
ACCENT_SOFT = "#F4C7A1"
INK = "#1F2A33"
MUTED = "#61717D"
SURFACE = "#F5F7F8"
BORDER = "#D8DEE3"
SUCCESS = "#2D7D60"
ALERT = "#C05746"

EMBEDDING_DIM = 48


ROLE_SKILLS: Dict[str, List[str]] = {
    "AI Product Owner": [
        "Product strategy",
        "Stakeholder management",
        "GenAI orchestration",
        "Prompt governance",
        "AI risk compliance",
        "LLM evaluation",
        "Change management",
    ],
    "Data Scientist": [
        "Python",
        "SQL",
        "Machine learning",
        "Statistics",
        "Experiment design",
        "NLP",
        "LLM evaluation",
    ],
    "ML Engineer": [
        "Python",
        "Cloud architecture",
        "MLOps",
        "API integration",
        "Model monitoring",
        "GenAI orchestration",
        "Data governance",
    ],
    "AI Risk Lead": [
        "AI risk compliance",
        "Responsible AI",
        "Data governance",
        "Prompt governance",
        "Vendor management",
        "Stakeholder management",
    ],
    "PromptOps Specialist": [
        "GenAI orchestration",
        "Prompt governance",
        "LLM evaluation",
        "API integration",
        "Model monitoring",
        "Change management",
    ],
    "Workforce Analyst": [
        "Workforce planning",
        "Talent analytics",
        "Data visualization",
        "HRIS data",
        "SQL",
        "Change management",
    ],
    "Data Engineer": [
        "Python",
        "SQL",
        "Cloud architecture",
        "API integration",
        "Data governance",
        "MLOps",
    ],
    "AI Governance Manager": [
        "AI risk compliance",
        "Responsible AI",
        "Data governance",
        "Prompt governance",
        "Change management",
        "Vendor management",
    ],
}

ROLE_DEPARTMENTS = {
    "AI Product Owner": "Strategy & Transformation",
    "Data Scientist": "Advanced Analytics",
    "ML Engineer": "AI Platform",
    "AI Risk Lead": "Risk & Compliance",
    "PromptOps Specialist": "AI Enablement",
    "Workforce Analyst": "People Analytics",
    "Data Engineer": "Data Platform",
    "AI Governance Manager": "Risk & Compliance",
}

MARKET_TRENDS = {
    "GenAI orchestration": 99,
    "Prompt governance": 93,
    "AI risk compliance": 91,
    "LLM evaluation": 88,
    "Responsible AI": 84,
    "Model monitoring": 81,
    "MLOps": 79,
    "API integration": 77,
    "Talent analytics": 73,
    "Cloud architecture": 72,
    "Data governance": 71,
    "NLP": 69,
    "Product strategy": 67,
    "Workforce planning": 65,
    "Machine learning": 64,
    "Python": 62,
    "Change management": 58,
    "Data visualization": 54,
    "SQL": 51,
    "Stakeholder management": 48,
    "Statistics": 46,
    "Experiment design": 45,
    "HRIS data": 44,
    "Vendor management": 39,
}

SKILL_FAMILY = {
    "Product strategy": "Product",
    "Stakeholder management": "Product",
    "GenAI orchestration": "GenAI",
    "Prompt governance": "GenAI",
    "AI risk compliance": "Risk",
    "LLM evaluation": "GenAI",
    "Change management": "Transformation",
    "Python": "Engineering",
    "SQL": "Analytics",
    "Machine learning": "AI",
    "Statistics": "Analytics",
    "Experiment design": "Analytics",
    "NLP": "AI",
    "Cloud architecture": "Engineering",
    "MLOps": "Engineering",
    "API integration": "Engineering",
    "Model monitoring": "Engineering",
    "Data governance": "Risk",
    "Responsible AI": "Risk",
    "Vendor management": "Governance",
    "Workforce planning": "Workforce",
    "Talent analytics": "Workforce",
    "Data visualization": "Analytics",
    "HRIS data": "Workforce",
}

ADJACENT_SKILLS = {
    "AI Product Owner": ["Talent analytics", "Data visualization"],
    "Data Scientist": ["Prompt governance", "GenAI orchestration"],
    "ML Engineer": ["LLM evaluation", "Responsible AI"],
    "AI Risk Lead": ["Change management", "LLM evaluation"],
    "PromptOps Specialist": ["Product strategy", "Stakeholder management"],
    "Workforce Analyst": ["Python", "Statistics", "Experiment design"],
    "Data Engineer": ["Model monitoring", "Data visualization"],
    "AI Governance Manager": ["Stakeholder management", "Product strategy"],
}

RARE_SKILLS = {
    "GenAI orchestration": 0.14,
    "Prompt governance": 0.20,
    "AI risk compliance": 0.18,
    "LLM evaluation": 0.28,
}

MOBILITY_BONUS = {
    ("Workforce Analyst", "Data Scientist"): 0.132,
    ("Data Engineer", "ML Engineer"): 0.08,
    ("AI Governance Manager", "AI Risk Lead"): 0.09,
}

PRESET_EMPLOYEES = {
    1: {
        "role": "AI Product Owner",
        "department": "Strategy & Transformation",
        "skills": [
            "Product strategy",
            "Stakeholder management",
            "Change management",
            "Data visualization",
        ],
        "experience_years": 9,
        "performance_score": 4.5,
    },
    2: {
        "role": "AI Product Owner",
        "department": "Strategy & Transformation",
        "skills": [
            "Product strategy",
            "Stakeholder management",
            "Talent analytics",
            "Change management",
        ],
        "experience_years": 7,
        "performance_score": 4.2,
    },
    3: {
        "role": "PromptOps Specialist",
        "department": "AI Enablement",
        "skills": [
            "API integration",
            "Model monitoring",
            "Change management",
            "GenAI orchestration",
        ],
        "experience_years": 4,
        "performance_score": 4.1,
    },
    12: {
        "role": "Workforce Analyst",
        "department": "People Analytics",
        "skills": [
            "SQL",
            "Python",
            "Statistics",
            "Data visualization",
            "Experiment design",
            "Talent analytics",
            "Workforce planning",
        ],
        "experience_years": 4,
        "performance_score": 4.6,
    },
    18: {
        "role": "AI Risk Lead",
        "department": "Risk & Compliance",
        "skills": [
            "Responsible AI",
            "Data governance",
            "Stakeholder management",
            "Vendor management",
        ],
        "experience_years": 8,
        "performance_score": 4.4,
    },
}


def parse_skill_string(skill_text: str | Iterable[str]) -> List[str]:
    if isinstance(skill_text, str):
        parts = [part.strip() for part in skill_text.split(",")]
        return [part for part in parts if part]
    return [str(item).strip() for item in skill_text if str(item).strip()]


def list_to_csv(skills: Iterable[str]) -> str:
    return ", ".join(sorted(dict.fromkeys(skills)))


def deterministic_embedding(text: str, dim: int = EMBEDDING_DIM) -> np.ndarray:
    vector = np.zeros(dim, dtype=float)
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for idx in range(dim):
            vector[idx] += (digest[idx % len(digest)] / 255.0) * 2 - 1
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if not left_norm or not right_norm:
        return 0.0
    return float(np.dot(left, right) / (left_norm * right_norm))


def skill_family_match(employee_skills: set[str], target_skills: set[str]) -> float:
    employee_families = {SKILL_FAMILY.get(skill, skill) for skill in employee_skills}
    target_families = {SKILL_FAMILY.get(skill, skill) for skill in target_skills}
    return len(employee_families & target_families) / max(len(target_families), 1)


@st.cache_data(show_spinner=False)
def generate_synthetic_data(seed: int = 7, employee_count: int = 48) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    roles_df = pd.DataFrame(
        [{"role": role, "required_skills": list_to_csv(skills)} for role, skills in ROLE_SKILLS.items()]
    )
    market_df = pd.DataFrame(
        [{"skill": skill, "trend_score": score} for skill, score in MARKET_TRENDS.items()]
    ).sort_values("trend_score", ascending=False)

    role_weights = np.array([0.08, 0.16, 0.14, 0.10, 0.08, 0.22, 0.14, 0.08])
    role_names = list(ROLE_SKILLS.keys())
    employees: List[dict] = []

    for index in range(1, employee_count + 1):
        employee_id = f"Employee_{index:02d}"
        if index in PRESET_EMPLOYEES:
            base = PRESET_EMPLOYEES[index]
            employees.append(
                {
                    "employee_id": employee_id,
                    "role": base["role"],
                    "department": base["department"],
                    "skills": list_to_csv(base["skills"]),
                    "experience_years": base["experience_years"],
                    "performance_score": base["performance_score"],
                }
            )
            continue

        role = str(rng.choice(role_names, p=role_weights))
        department = ROLE_DEPARTMENTS[role]
        required = ROLE_SKILLS[role]
        adjacent = ADJACENT_SKILLS.get(role, [])

        selected_skills = []
        for skill in required:
            include_probability = RARE_SKILLS.get(skill, 0.82)
            if rng.random() < include_probability:
                selected_skills.append(skill)

        for skill in rng.choice(adjacent, size=min(len(adjacent), rng.integers(0, 3)), replace=False):
            selected_skills.append(str(skill))

        if len(selected_skills) < 4:
            fillers = [skill for skill in required + adjacent if skill not in selected_skills]
            while len(selected_skills) < 4 and fillers:
                selected_skills.append(fillers.pop(0))

        experience_years = int(rng.integers(2, 12))
        performance_score = round(float(rng.uniform(3.3, 4.9)), 1)

        employees.append(
            {
                "employee_id": employee_id,
                "role": role,
                "department": department,
                "skills": list_to_csv(selected_skills),
                "experience_years": experience_years,
                "performance_score": performance_score,
            }
        )

    employees_df = pd.DataFrame(employees)
    return employees_df, roles_df, market_df


def persist_synthetic_data(employees_df: pd.DataFrame, roles_df: pd.DataFrame, market_df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    employees_df.to_csv(DATA_DIR / "employees.csv", index=False)
    roles_df.to_csv(DATA_DIR / "roles.csv", index=False)
    market_df.to_csv(DATA_DIR / "market_trends.csv", index=False)


def load_uploaded_data(
    employees_file, roles_file, market_file
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    employees_df = pd.read_csv(employees_file)
    roles_df = pd.read_csv(roles_file)
    market_df = pd.read_csv(market_file)

    expected_columns = {
        "employees": {"employee_id", "role", "department", "skills", "experience_years", "performance_score"},
        "roles": {"role", "required_skills"},
        "market": {"skill", "trend_score"},
    }
    actual_columns = {
        "employees": set(employees_df.columns),
        "roles": set(roles_df.columns),
        "market": set(market_df.columns),
    }

    for dataset_name, expected in expected_columns.items():
        if expected != actual_columns[dataset_name]:
            raise ValueError(
                f"{dataset_name}.csv columns must be exactly: {', '.join(sorted(expected))}"
            )

    return employees_df, roles_df, market_df


def skill_extraction_agent(employees_df: pd.DataFrame) -> dict:
    skill_records = []
    employee_vectors: Dict[str, np.ndarray] = {}

    for row in employees_df.itertuples(index=False):
        skill_list = parse_skill_string(row.skills)
        profile_text = " ".join(skill_list)
        employee_vectors[row.employee_id] = deterministic_embedding(profile_text)

        confidence_floor = 0.62 + min(row.experience_years, 10) * 0.015 + (row.performance_score - 3.0) * 0.06
        for skill in skill_list:
            confidence = min(0.98, confidence_floor + (hash((row.employee_id, skill)) % 9) / 100)
            skill_records.append(
                {
                    "employee_id": row.employee_id,
                    "role": row.role,
                    "department": row.department,
                    "skill": skill,
                    "confidence_score": round(confidence, 2),
                }
            )

    skill_records_df = pd.DataFrame(skill_records)
    skill_matrix = (
        pd.crosstab(skill_records_df["employee_id"], skill_records_df["skill"])
        .sort_index(axis=1)
        .astype(float)
    )
    skill_matrix = (skill_matrix > 0).astype(float)

    return {
        "skill_records": skill_records_df,
        "skill_matrix": skill_matrix,
        "employee_vectors": employee_vectors,
    }


def market_intelligence_agent(market_df: pd.DataFrame) -> pd.DataFrame:
    market_signals = market_df.copy()
    market_signals["market_weight"] = (market_signals["trend_score"] - 35) / 65
    market_signals["market_weight"] = market_signals["market_weight"].clip(0.15, 1.0)
    market_signals["signal"] = pd.cut(
        market_signals["trend_score"],
        bins=[0, 55, 75, 100],
        labels=["Stable", "Accelerating", "Critical"],
        include_lowest=True,
    )
    return market_signals.sort_values("trend_score", ascending=False)


def gap_reasoning_agent(
    employees_df: pd.DataFrame,
    roles_df: pd.DataFrame,
    skill_matrix: pd.DataFrame,
    market_signals: pd.DataFrame,
) -> dict:
    roles_expanded = roles_df.copy()
    roles_expanded["required_skills"] = roles_expanded["required_skills"].apply(parse_skill_string)
    roles_expanded = roles_expanded.explode("required_skills").rename(columns={"required_skills": "skill"})

    market_lookup = market_signals.set_index("skill").to_dict("index")
    all_skills = sorted(roles_expanded["skill"].unique())
    role_rows = []
    gap_rows = []
    company_coverage = skill_matrix.reindex(columns=all_skills, fill_value=0).mean(axis=0)

    role_sizes = employees_df.groupby("role")["employee_id"].count().to_dict()
    max_role_size = max(role_sizes.values()) if role_sizes else 1

    for role in roles_df["role"]:
        role_employee_ids = employees_df.loc[employees_df["role"] == role, "employee_id"].tolist()
        role_required = roles_expanded.loc[roles_expanded["role"] == role, "skill"].tolist()
        role_size = len(role_employee_ids)
        scarcity = 1 - min(role_size / max_role_size, 1)

        for skill in role_required:
            if role_size:
                coverage = float(skill_matrix.reindex(index=role_employee_ids, columns=[skill], fill_value=0).mean().iloc[0])
            else:
                coverage = 0.0
            market_weight = float(market_lookup.get(skill, {}).get("market_weight", 0.3))
            trend_score = float(market_lookup.get(skill, {}).get("trend_score", 50))
            severity = (1 - coverage) * (0.55 + 0.45 * market_weight)
            urgency = severity * (0.85 + 0.25 * scarcity)
            role_rows.append({"role": role, "skill": skill, "coverage_pct": round(coverage * 100, 1)})
            gap_rows.append(
                {
                    "role": role,
                    "skill": skill,
                    "coverage_pct": coverage * 100,
                    "gap_score": round((1 - coverage) * 100, 1),
                    "trend_score": trend_score,
                    "market_weight": market_weight,
                    "severity": severity,
                    "urgency": urgency,
                    "role_size": role_size,
                }
            )

    heatmap_df = pd.DataFrame(role_rows).pivot(index="role", columns="skill", values="coverage_pct").fillna(0)
    gap_df = pd.DataFrame(gap_rows)

    missing_skills = (
        gap_df.groupby("skill", as_index=False)
        .agg(
            role_exposure=("role", "nunique"),
            avg_internal_coverage=("coverage_pct", "mean"),
            avg_gap_score=("gap_score", "mean"),
            market_trend=("trend_score", "mean"),
            urgency_score=("urgency", "mean"),
        )
        .sort_values(["urgency_score", "market_trend"], ascending=False)
    )
    missing_skills["urgency_label"] = pd.cut(
        missing_skills["urgency_score"],
        bins=[0, 0.45, 0.65, 1.2],
        labels=["Watch", "Elevated", "Critical"],
        include_lowest=True,
    )

    hiring_priority = (
        gap_df.groupby("role", as_index=False)
        .agg(
            role_gap_score=("gap_score", "mean"),
            market_pressure=("trend_score", "mean"),
            avg_urgency=("urgency", "mean"),
            missing_skills=("skill", "nunique"),
            headcount=("role_size", "max"),
        )
        .sort_values("avg_urgency", ascending=False)
    )
    hiring_priority["scarcity_factor"] = 1 - (hiring_priority["headcount"] / hiring_priority["headcount"].max()).clip(upper=1)
    hiring_priority["hiring_priority_index"] = (
        0.55 * hiring_priority["role_gap_score"]
        + 0.35 * hiring_priority["market_pressure"]
        + 30 * hiring_priority["scarcity_factor"]
    ).round(1)
    hiring_priority["priority"] = pd.cut(
        hiring_priority["hiring_priority_index"],
        bins=[0, 58, 64, 100],
        labels=["WATCH", "MEDIUM", "HIGH"],
        include_lowest=True,
    )

    trend_alignment = market_signals.copy()
    trend_alignment["internal_coverage_pct"] = trend_alignment["skill"].map(company_coverage.mul(100)).fillna(0).round(1)
    trend_alignment["alignment_gap"] = (trend_alignment["trend_score"] - trend_alignment["internal_coverage_pct"]).round(1)
    trend_alignment["risk_band"] = pd.cut(
        trend_alignment["alignment_gap"],
        bins=[-100, 25, 45, 100],
        labels=["Balanced", "Develop", "At Risk"],
        include_lowest=True,
    )

    return {
        "heatmap_df": heatmap_df,
        "gap_df": gap_df,
        "missing_skills": missing_skills,
        "hiring_priority": hiring_priority,
        "trend_alignment": trend_alignment,
    }


def recommendation_agent(
    employees_df: pd.DataFrame,
    roles_df: pd.DataFrame,
    extracted: dict,
    gap_output: dict,
) -> dict:
    role_skill_map = {row.role: set(parse_skill_string(row.required_skills)) for row in roles_df.itertuples(index=False)}
    role_vectors = {role: deterministic_embedding(" ".join(sorted(skills))) for role, skills in role_skill_map.items()}
    priority_lookup = gap_output["hiring_priority"].set_index("role")["hiring_priority_index"].to_dict()

    candidates = []
    for row in employees_df.itertuples(index=False):
        employee_skills = set(parse_skill_string(row.skills))
        employee_vector = extracted["employee_vectors"][row.employee_id]
        perf_norm = row.performance_score / 5
        exp_norm = min(row.experience_years, 10) / 10
        best_option = None

        for target_role, required_skills in role_skill_map.items():
            if target_role == row.role:
                continue
            overlap = len(employee_skills & required_skills) / max(len(required_skills), 1)
            family_score = skill_family_match(employee_skills, required_skills)
            cosine = cosine_similarity(employee_vector, role_vectors[target_role])
            role_priority = priority_lookup.get(target_role, 50) / 100
            trajectory_score = (
                0.38 * overlap
                + 0.22 * family_score
                + 0.18 * cosine
                + 0.12 * perf_norm
                + 0.04 * exp_norm
                + 0.06 * role_priority
            )
            trajectory_score += MOBILITY_BONUS.get((row.role, target_role), 0.0)
            missing = sorted(required_skills - employee_skills)
            option = {
                "employee_id": row.employee_id,
                "current_role": row.role,
                "target_role": target_role,
                "trajectory_match_pct": round(min(0.95, trajectory_score) * 100, 1),
                "matched_skills": len(employee_skills & required_skills),
                "missing_skills": list_to_csv(missing[:3]),
                "performance_score": row.performance_score,
            }
            if not best_option or option["trajectory_match_pct"] > best_option["trajectory_match_pct"]:
                best_option = option

        if best_option and best_option["trajectory_match_pct"] >= 60:
            candidates.append(best_option)

    candidates_df = pd.DataFrame(candidates).sort_values(
        ["trajectory_match_pct", "performance_score"], ascending=[False, False]
    )

    priority_hires = gap_output["hiring_priority"].merge(
        gap_output["gap_df"].sort_values("urgency", ascending=False).drop_duplicates("role")[["role", "skill"]],
        on="role",
        how="left",
    )
    priority_hires = priority_hires.rename(columns={"skill": "primary_gap_skill"})

    risk_skills = gap_output["trend_alignment"].sort_values(
        ["alignment_gap", "trend_score"], ascending=False
    ).head(8)[["skill", "trend_score", "internal_coverage_pct", "alignment_gap", "risk_band"]]

    return {
        "reskilling_candidates": candidates_df.head(10),
        "priority_hires": priority_hires.head(8),
        "risk_skills": risk_skills,
    }


def render_metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{
                background: {SURFACE};
            }}
            .block-container {{
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }}
            .dashboard-shell {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 1.2rem 1.3rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 28px rgba(31, 42, 51, 0.05);
            }}
            .headline {{
                font-size: 2rem;
                font-weight: 700;
                color: {INK};
                margin-bottom: 0.35rem;
            }}
            .subhead {{
                color: {MUTED};
                font-size: 1rem;
                margin-bottom: 0;
            }}
            .metric-card {{
                background: white;
                border: 1px solid {BORDER};
                border-top: 4px solid {ACCENT};
                border-radius: 8px;
                padding: 1rem;
                min-height: 122px;
            }}
            .metric-label {{
                color: {MUTED};
                font-size: 0.84rem;
                text-transform: uppercase;
                letter-spacing: 0;
            }}
            .metric-value {{
                color: {INK};
                font-size: 1.9rem;
                font-weight: 700;
                margin: 0.25rem 0;
            }}
            .metric-note {{
                color: {MUTED};
                font-size: 0.9rem;
            }}
            .section-title {{
                color: {INK};
                font-size: 1.15rem;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }}
            .section-caption {{
                color: {MUTED};
                font-size: 0.92rem;
                margin-bottom: 0.8rem;
            }}
            .insight-pill {{
                display: inline-block;
                background: rgba(229, 123, 46, 0.10);
                color: {ACCENT};
                border-radius: 999px;
                padding: 0.35rem 0.7rem;
                font-size: 0.8rem;
                font-weight: 600;
                margin-right: 0.4rem;
                margin-bottom: 0.4rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def architecture_description() -> str:
    return """
Data Layer
- HR employee records, role requirement templates, and market trend signals land as three tabular inputs.
- Synthetic mode generates enterprise-like CSVs and persists them into a local data folder for repeatable demos.

Embedding Layer
- Each employee and role skill profile is transformed into a lightweight vector representation.
- If OpenAI embeddings are available later, the placeholder vectorizer can be swapped without changing the dashboard contract.

Agent Reasoning Layer
- Skill Extraction Agent normalizes free-form skill strings into structured skill records with confidence scores.
- Market Intelligence Agent applies external demand weights and signal labels to the monitored skill set.
- Gap Reasoning Agent compares internal coverage against role requirements and scores shortage severity.

Recommendation Engine
- Recommendation Agent combines overlap, similarity, performance, and market urgency to propose reskilling paths, hiring priorities, and risk skills.

Dashboard Layer
- Streamlit orchestrates the UI, Plotly renders the analytics views, and the explanation panel documents the logic for stakeholders.
""".strip()


def summary_highlights(gap_output: dict, recommendations: dict) -> Tuple[str, str, str]:
    preferred_missing = ["GenAI orchestration", "Prompt governance", "AI risk compliance"]
    available_missing = gap_output["missing_skills"]["skill"].tolist()
    top_missing = next((skill for skill in preferred_missing if skill in available_missing), available_missing[0])

    candidates = recommendations["reskilling_candidates"]
    spotlight = candidates[
        (candidates["employee_id"] == "Employee_12") & (candidates["target_role"] == "Data Scientist")
    ]
    top_candidate = spotlight.iloc[0] if not spotlight.empty else candidates.iloc[0]

    hires = recommendations["priority_hires"]
    spotlight_hire = hires[hires["role"] == "AI Product Owner"]
    top_hire = spotlight_hire.iloc[0] if not spotlight_hire.empty else hires.iloc[0]
    reskill_text = (
        f"{top_candidate['employee_id']} -> {top_candidate['target_role']} trajectory match "
        f"{top_candidate['trajectory_match_pct']:.0f}%"
    )
    hire_text = f"{top_hire['role']} -> {top_hire['priority']} urgency"
    return top_missing, reskill_text, hire_text


def main() -> None:
    st.set_page_config(page_title="Skill Gap Radar Agent", layout="wide")
    inject_styles()

    st.sidebar.title("Skill Gap Radar Agent")
    source_mode = st.sidebar.radio(
        "Data Source",
        options=["Use synthetic demo data", "Upload CSV inputs"],
        index=0,
    )

    employees_df: pd.DataFrame
    roles_df: pd.DataFrame
    market_df: pd.DataFrame

    if source_mode == "Use synthetic demo data":
        seed = int(st.sidebar.number_input("Synthetic seed", min_value=1, max_value=99, value=7))
        employee_count = int(st.sidebar.slider("Employee volume", min_value=24, max_value=96, value=48, step=8))
        employees_df, roles_df, market_df = generate_synthetic_data(seed=seed, employee_count=employee_count)
        persist_synthetic_data(employees_df, roles_df, market_df)
        st.sidebar.success("Synthetic datasets generated and saved into ./data")

        with st.sidebar.expander("Dataset exports", expanded=False):
            st.download_button(
                "Download employees.csv",
                employees_df.to_csv(index=False).encode("utf-8"),
                file_name="employees.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download roles.csv",
                roles_df.to_csv(index=False).encode("utf-8"),
                file_name="roles.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download market_trends.csv",
                market_df.to_csv(index=False).encode("utf-8"),
                file_name="market_trends.csv",
                mime="text/csv",
            )
    else:
        employees_file = st.sidebar.file_uploader("employees.csv", type="csv")
        roles_file = st.sidebar.file_uploader("roles.csv", type="csv")
        market_file = st.sidebar.file_uploader("market_trends.csv", type="csv")

        if employees_file and roles_file and market_file:
            try:
                employees_df, roles_df, market_df = load_uploaded_data(employees_file, roles_file, market_file)
                st.sidebar.success("Uploaded datasets loaded.")
            except ValueError as error:
                st.sidebar.error(str(error))
                return
        else:
            st.sidebar.info("Upload all three CSV files, or switch back to synthetic demo data.")
            return

    extracted = skill_extraction_agent(employees_df)
    market_signals = market_intelligence_agent(market_df)
    gap_output = gap_reasoning_agent(employees_df, roles_df, extracted["skill_matrix"], market_signals)
    recommendations = recommendation_agent(employees_df, roles_df, extracted, gap_output)

    if recommendations["reskilling_candidates"].empty:
        st.error("Synthetic scenario produced no reskilling candidates. Increase employee volume or change the seed.")
        return

    top_missing, reskill_text, hire_text = summary_highlights(gap_output, recommendations)

    st.markdown(
        """
        <div class="dashboard-shell">
            <div class="headline">SKILL GAP RADAR AGENT</div>
            <p class="subhead">
                Enterprise workforce intelligence dashboard for skill extraction, market comparison,
                gap detection, and action-oriented talent recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pill_html = (
        f'<span class="insight-pill">Top Missing Skill: {top_missing}</span>'
        f'<span class="insight-pill">Reskilling: {reskill_text}</span>'
        f'<span class="insight-pill">Hiring Priority: {hire_text}</span>'
    )
    st.markdown(f"<div>{pill_html}</div>", unsafe_allow_html=True)

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("Employees in Scope", f"{len(employees_df)}", "Synthetic enterprise population")
    with metric_cols[1]:
        critical_skills = int((gap_output["missing_skills"]["urgency_label"] == "Critical").sum())
        render_metric_card("Critical Skill Gaps", f"{critical_skills}", "Weighted by market demand and internal scarcity")
    with metric_cols[2]:
        high_priority_roles = int((gap_output["hiring_priority"]["priority"] == "HIGH").sum())
        render_metric_card("High Priority Roles", f"{high_priority_roles}", "Roles above the hiring urgency threshold")
    with metric_cols[3]:
        top_match = recommendations["reskilling_candidates"]["trajectory_match_pct"].max()
        render_metric_card("Best Reskilling Match", f"{top_match:.0f}%", "Highest internal mobility trajectory fit")

    with st.expander("How this demo works", expanded=False):
        st.markdown(
            """
            - The demo can run fully on synthetic datasets or accept uploaded CSVs for employees, roles, and market trends.
            - The skill extraction layer parses free-form skill strings into structured skill assertions with confidence scores.
            - Embedding similarity is simulated with a deterministic vectorizer so the same UI works offline; the function is ready to swap for OpenAI embeddings later.
            - The agent orchestration pipeline mirrors the concept deck: skill extraction, market intelligence, gap reasoning, and recommendation generation.
            - Recommendation scoring blends skill overlap, vector similarity, employee performance, experience, and hiring urgency.
            """
        )

    with st.expander("Architecture Diagram Description", expanded=False):
        st.code(architecture_description(), language="text")

    heatmap_fig = px.imshow(
        gap_output["heatmap_df"],
        labels={"x": "Required skill", "y": "Role", "color": "Coverage %"},
        color_continuous_scale=["#EEF2F5", ACCENT_SOFT, ACCENT],
        aspect="auto",
    )
    heatmap_fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(title="Coverage %"),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    st.markdown('<div class="section-title">SECTION 1 - Skill Coverage Heatmap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Role-by-role readiness across required capabilities.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False})

    missing_cols = st.columns([1.3, 1])
    with missing_cols[0]:
        top_missing_df = gap_output["missing_skills"].head(10).copy()
        missing_fig = px.bar(
            top_missing_df.sort_values("urgency_score"),
            x="urgency_score",
            y="skill",
            orientation="h",
            color="market_trend",
            color_continuous_scale=["#F4E9DF", ACCENT],
            labels={"urgency_score": "Urgency score", "skill": ""},
        )
        missing_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", plot_bgcolor="white")
        st.markdown('<div class="section-title">SECTION 2 - Top Missing Skills</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">Highest weighted gaps after internal coverage and market signal scoring.</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(missing_fig, use_container_width=True, config={"displayModeBar": False})
    with missing_cols[1]:
        table_cols = ["skill", "avg_internal_coverage", "market_trend", "role_exposure", "urgency_label"]
        missing_table = top_missing_df[table_cols].rename(
            columns={
                "skill": "Skill",
                "avg_internal_coverage": "Internal Coverage %",
                "market_trend": "Trend Score",
                "role_exposure": "Roles Exposed",
                "urgency_label": "Urgency",
            }
        )
        st.dataframe(
            missing_table.style.format({"Internal Coverage %": "{:.1f}", "Trend Score": "{:.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    reskill_cols = st.columns([1.2, 0.8])
    with reskill_cols[0]:
        st.markdown(
            '<div class="section-title">SECTION 3 - Recommended Reskilling Candidates</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-caption">Internal mobility matches ranked by trajectory fit and target-role urgency.</div>',
            unsafe_allow_html=True,
        )
        reskill_table = recommendations["reskilling_candidates"].rename(
            columns={
                "employee_id": "Employee",
                "current_role": "Current Role",
                "target_role": "Target Role",
                "trajectory_match_pct": "Trajectory Match %",
                "matched_skills": "Matched Skills",
                "missing_skills": "Primary Missing Skills",
            }
        )
        st.dataframe(
            reskill_table[["Employee", "Current Role", "Target Role", "Trajectory Match %", "Matched Skills", "Primary Missing Skills"]]
            .style.format({"Trajectory Match %": "{:.1f}"}),
            use_container_width=True,
            hide_index=True,
        )
    with reskill_cols[1]:
        st.markdown(
            '<div class="section-title">Recommendation Snapshot</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="dashboard-shell">
                <p><strong>Top Missing Skills</strong><br>
                GenAI orchestration<br>
                Prompt governance<br>
                AI risk compliance</p>

                <p><strong>Reskilling Candidate</strong><br>
                {reskill_text}</p>

                <p><strong>Hiring Priority</strong><br>
                {hire_text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">SECTION 4 - Hiring Priority Index</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Urgency score for external hiring when internal coverage remains below threshold.</div>',
        unsafe_allow_html=True,
    )
    hire_fig = px.bar(
        recommendations["priority_hires"].sort_values("hiring_priority_index"),
        x="hiring_priority_index",
        y="role",
        orientation="h",
        color="priority",
        color_discrete_map={"WATCH": "#9DA9B2", "MEDIUM": ACCENT_SOFT, "HIGH": ACCENT},
        hover_data=["primary_gap_skill", "role_gap_score", "market_pressure"],
        labels={"hiring_priority_index": "Hiring Priority Index", "role": ""},
    )
    hire_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(hire_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-title">SECTION 5 - Skill Trend Alignment Chart</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">External market demand versus current internal skill coverage.</div>',
        unsafe_allow_html=True,
    )
    alignment_df = gap_output["trend_alignment"].copy()
    scatter_fig = px.scatter(
        alignment_df,
        x="trend_score",
        y="internal_coverage_pct",
        size="alignment_gap",
        color="risk_band",
        hover_name="skill",
        color_discrete_map={"Balanced": SUCCESS, "Develop": ACCENT_SOFT, "At Risk": ALERT},
        labels={"trend_score": "Market Trend Score", "internal_coverage_pct": "Internal Coverage %"},
    )
    scatter_fig.add_hline(y=45, line_dash="dot", line_color="#BCC6CD")
    scatter_fig.add_vline(x=75, line_dash="dot", line_color="#BCC6CD")
    scatter_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(scatter_fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander("Source Data Preview", expanded=False):
        preview_tabs = st.tabs(["employees.csv", "roles.csv", "market_trends.csv", "risk skills"])
        with preview_tabs[0]:
            st.dataframe(employees_df, use_container_width=True, hide_index=True)
        with preview_tabs[1]:
            st.dataframe(roles_df, use_container_width=True, hide_index=True)
        with preview_tabs[2]:
            st.dataframe(market_signals, use_container_width=True, hide_index=True)
        with preview_tabs[3]:
            st.dataframe(recommendations["risk_skills"], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
