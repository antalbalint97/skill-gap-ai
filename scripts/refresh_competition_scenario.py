from __future__ import annotations

import csv
import json
import re
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BASE_MARKET_PATH = DATA_DIR / "market_trends.json"
OUTPUT_JSON_PATH = DATA_DIR / "competition_scenario.json"
OUTPUT_CSV_PATH = DATA_DIR / "competition_market_trends.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

EC_URL = "https://digital-strategy.ec.europa.eu/en/library/shaping-and-strengthening-european-ai-talent"
OECD_SKILLS_GAP_URL = "https://www.oecd.org/en/publications/bridging-the-ai-skills-gap_66d0702e-en.html"
OECD_UK_AI_URL = "https://www.oecd.org/en/publications/measuring-the-demand-for-ai-skills-in-the-united-kingdom_1d6474ef-en.html"
EURES_STATS_CSV_URL = "https://public.tableau.com/views/05_EURES_OCCUPATIONSSKILLSANDEXPERIENCE_2025_Q2/DOccupationSkillLv2ExpCountry.csv?:showVizHome=no"
EURES_SERVICES_URL = "https://eures.europa.eu/eures-services_en"


SOURCE_DEFS = [
    {
        "name": "European Commission AI talent briefing",
        "url": EC_URL,
        "published_at": "2025-10-28",
        "source_type": "Public report summary",
        "fallback_summary": (
            "The European Commission reports that AI talent in the EU more than doubled between 2016 and 2023, "
            "now representing 0.41% of the workforce, and warns that up to 6.5% of workers may need to transition "
            "roles by 2030 as AI adoption accelerates."
        ),
        "patterns": [r"0\.41%\s+of the EU workforce", r"up to 6\.5%\s+of the EU workforce"],
        "skill_boosts": {
            "GenAI orchestration": 4,
            "Prompt governance": 4,
            "AI risk compliance": 4,
            "LLM evaluation": 3,
            "Data governance": 3,
            "Change management": 3,
            "Cloud architecture": 1,
            "Product strategy": 1,
            "Stakeholder management": 1,
        },
    },
    {
        "name": "OECD AI skills gap brief",
        "url": OECD_SKILLS_GAP_URL,
        "published_at": "2025-04-24",
        "source_type": "Policy brief summary",
        "fallback_summary": (
            "The OECD says AI is driving demand for both specialised AI professionals and workers with general AI literacy, "
            "and argues that training supply may not be sufficient to meet the growing need for AI literacy."
        ),
        "patterns": [
            r"training supply may not be sufficient to meet the growing need for general AI literacy skills",
            r"demand for both specialised AI professionals and workers with a more general understanding of AI",
        ],
        "skill_boosts": {
            "Prompt governance": 4,
            "AI risk compliance": 3,
            "LLM evaluation": 3,
            "Responsible AI": 3,
            "Change management": 4,
            "Stakeholder management": 2,
            "Vendor management": 1,
        },
    },
    {
        "name": "OECD UK AI hiring intensity",
        "url": OECD_UK_AI_URL,
        "published_at": "2024-09-05",
        "source_type": "Working paper summary",
        "fallback_summary": (
            "The OECD reports that AI hiring intensity rose in the United Kingdom over 2012 to 2022 and that "
            "Finance and Insurance increasingly demanded AI skills, with data scientist and related engineering "
            "roles among the most AI-intensive occupations."
        ),
        "patterns": [
            r"Finance and Insurance industry increasingly demanding AI skills",
            r"data scientist, computer scientist, hardware engineer and robotics engineer",
        ],
        "skill_boosts": {
            "Machine learning": 3,
            "Python": 3,
            "NLP": 2,
            "MLOps": 3,
            "Model monitoring": 3,
            "Cloud architecture": 2,
            "API integration": 2,
            "Data governance": 2,
            "Statistics": 1,
            "Experiment design": 1,
        },
    },
]


def fetch_text(url: str) -> str:
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(content_type, errors="replace")


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<script.*?>.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?>.*?</style>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_title(html: str, fallback: str) -> str:
    match = re.search(r"(?is)<title>(.*?)</title>", html)
    if not match:
        return fallback
    return re.sub(r"\s+", " ", unescape(match.group(1))).strip()


def extract_summary(text: str, patterns: List[str], fallback: str) -> str:
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if not match:
            continue
        start = max(0, match.start() - 220)
        end = min(len(text), match.end() + 260)
        sentence_start = max(text.rfind(". ", 0, start), text.rfind("! ", 0, start), text.rfind("? ", 0, start))
        sentence_end_candidates = [index for index in (text.find(". ", end), text.find("! ", end), text.find("? ", end)) if index != -1]
        sentence_end = min(sentence_end_candidates) if sentence_end_candidates else min(len(text), end)
        if sentence_start == -1:
            sentence_start = 0
        else:
            sentence_start += 2
        snippet = text[sentence_start:sentence_end].strip(" .")
        return re.sub(r"\s+", " ", snippet)
    return fallback


def fetch_source_documents() -> List[Dict[str, str]]:
    documents = []
    for source in SOURCE_DEFS:
        title = source["name"]
        summary = source["fallback_summary"]
        fetch_mode = "fallback summary"

        try:
            html = fetch_text(source["url"])
            text = strip_html(html)
            title = extract_title(html, source["name"])
            summary = extract_summary(text, source["patterns"], source["fallback_summary"])
            fetch_mode = "live page fetch"
        except (HTTPError, URLError, OSError):
            pass

        documents.append(
            {
                "name": f"{source['name']} | {source['published_at']}",
                "sourceType": source["source_type"],
                "mimeType": "text/plain",
                "url": source["url"],
                "publishedAt": source["published_at"],
                "text": (
                    f"Source summary based on {title}. Published on {source['published_at']}. "
                    f"Refresh mode: {fetch_mode}. "
                    f"{summary}"
                ),
            }
        )
    return documents


def fetch_eures_snapshot() -> Dict[str, str]:
    csv_text = fetch_text(EURES_STATS_CSV_URL)
    rows = list(csv.DictReader(csv_text.splitlines()))
    if not rows:
        raise ValueError("EURES export returned no rows.")
    first_row = rows[0]
    dmax = first_row.get("Day of dmax", "").strip()
    dmin = first_row.get("Day of dmin", "").strip()
    return {
        "windowStart": dmin,
        "windowEnd": dmax,
    }


def build_analyst_note(eures_snapshot: Dict[str, str]) -> str:
    return (
        "Competition setup refreshed from public sources for a European financial-services AI transformation demo.\n\n"
        f"The EURES job-vacancy dashboard currently exposes a reporting window from {eures_snapshot['windowStart']} "
        f"to {eures_snapshot['windowEnd']}. The EURES services portal also states that it provides a large European "
        "database of job vacancies and CVs.\n\n"
        "European Commission and OECD signals point in the same direction: AI talent demand is rising, broad AI literacy "
        "is becoming a workforce-wide requirement, and regulated sectors such as finance need stronger governance, "
        "evaluation, and monitoring capabilities in addition to pure engineering skills.\n\n"
        "For this demo, the most decision-relevant bottlenecks remain GenAI orchestration, prompt governance, AI risk "
        "compliance, LLM evaluation, model monitoring, and the change-management capacity needed to reskill adjacent teams."
    )


def load_base_market() -> List[Dict[str, int]]:
    with BASE_MARKET_PATH.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    return [{"skill": row["skill"], "trend_score": int(row["trend_score"])} for row in records]


def build_market(base_market: List[Dict[str, int]]) -> List[Dict[str, int]]:
    boosts: Dict[str, int] = {}
    for source in SOURCE_DEFS:
        for skill, amount in source["skill_boosts"].items():
            boosts[skill] = boosts.get(skill, 0) + amount

    boosts["GenAI orchestration"] = boosts.get("GenAI orchestration", 0) + 2
    boosts["Prompt governance"] = boosts.get("Prompt governance", 0) + 2
    boosts["AI risk compliance"] = boosts.get("AI risk compliance", 0) + 2
    boosts["Change management"] = boosts.get("Change management", 0) + 2

    adjusted = []
    for record in base_market:
        score = int(record["trend_score"])
        score += boosts.get(record["skill"], 0)
        score = max(35, min(99, score))
        adjusted.append({"skill": record["skill"], "trend_score": score})

    adjusted.sort(key=lambda row: (-row["trend_score"], row["skill"]))
    return adjusted


def write_market_csv(records: List[Dict[str, int]]) -> None:
    with OUTPUT_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["skill", "trend_score"])
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    eures_snapshot = fetch_eures_snapshot()
    documents = fetch_source_documents()
    documents.append(
        {
            "name": "EURES vacancy window snapshot",
            "sourceType": "Public labour-market snapshot",
            "mimeType": "text/plain",
            "url": EURES_SERVICES_URL,
            "publishedAt": datetime.now(UTC).date().isoformat(),
            "text": (
                f"Snapshot refreshed on {datetime.now(UTC).date().isoformat()}. "
                f"The public EURES job-vacancy Tableau export currently reports a data window from "
                f"{eures_snapshot['windowStart']} to {eures_snapshot['windowEnd']}. "
                "The EURES services portal describes EURES as providing a large European database of job vacancies and CVs."
            ),
        }
    )

    market = build_market(load_base_market())
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    payload = {
        "id": "competition",
        "name": "EU Financial Services AI Shift",
        "summary": (
            f"One-click competition scenario seeded with public OECD, European Commission, and EURES workforce signals "
            f"refreshed on {datetime.now(UTC).date().isoformat()}."
        ),
        "generatedAt": generated_at,
        "analystNoteName": "Competition scenario brief",
        "analystNote": build_analyst_note(eures_snapshot),
        "documents": documents,
        "market": market,
    }

    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_market_csv(market)

    print(f"Wrote {OUTPUT_JSON_PATH}")
    print(f"Wrote {OUTPUT_CSV_PATH}")
    print(f"EURES window: {eures_snapshot['windowStart']} -> {eures_snapshot['windowEnd']}")


if __name__ == "__main__":
    main()
