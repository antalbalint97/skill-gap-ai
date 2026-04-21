# Skill Gap Radar Agent

Skill Gap Radar Agent is a demo workforce intelligence application that helps teams identify critical skill gaps, prioritize hiring, and surface internal reskilling opportunities.

The current primary experience is a Next.js dashboard with evidence-backed reasoning traces. The repository also includes an earlier Streamlit prototype in `app.py`.

## What the app does

- Loads bundled synthetic workforce data for instant demo mode.
- Accepts uploaded CSV datasets for employees, roles, and market trends.
- Accepts analyst notes plus `.txt`, `.md`, and `.pdf` evidence files.
- Computes skill coverage, top missing skills, hiring priority, and reskilling recommendations.
- Attaches retrieved evidence snippets and confidence labels to the main recommendations.
- Visualizes results with heatmaps, bar charts, scatter plots, and summary tables.

## Tech stack

- Next.js 16 (App Router)
- React 19
- Plotly via `react-plotly.js`
- PDF parsing with `pdfjs-dist` and `pdf-parse`
- JavaScript analytics engine in `lib/analytics.js`
- Legacy Streamlit prototype with pandas, numpy, and plotly

## Project structure

```text
skill_gap_ai/
|- app/
|  |- api/analyze/route.js     # API endpoint for analysis requests
|  |- globals.css             # Dashboard styling
|  |- layout.jsx              # App shell metadata/layout
|  |- page.jsx                # Main dashboard UI
|- data/
|  |- employees.csv/json      # Demo employee data
|  |- roles.csv/json          # Demo role requirements
|  |- market_trends.csv/json  # Demo market demand signals
|- lib/
|  |- analytics.js            # Core scoring, recommendation, and evidence logic
|- app.py                     # Legacy Streamlit version
|- package.json               # Next.js scripts and frontend dependencies
|- requirements.txt           # Python dependencies for Streamlit prototype
```

## Main application flow

1. The UI loads bundled synthetic JSON data or lets the user upload three CSV files.
2. Evidence documents are collected from a text note and optional uploaded files.
3. `POST /api/analyze` validates the datasets and builds the response.
4. `lib/analytics.js` computes:
   - skill coverage heatmap
   - missing skill urgency
   - hiring priority index
   - reskilling trajectories
   - trend alignment
   - evidence retrieval and confidence scoring
5. The dashboard renders charts, tables, and trace cards from the returned analysis payload.

## Running the Next.js app

### Prerequisites

- Node.js 20+ recommended
- npm

### Install dependencies

```bash
npm install
```

### Start the development server

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

### Production build

```bash
npm run build
npm start
```

## Running the Streamlit prototype

The Streamlit app is kept as an earlier standalone prototype of the same concept.

### Prerequisites

- Python 3.11+ recommended

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start Streamlit

```bash
streamlit run app.py
```

## Expected dataset format

### `employees.csv`

Required columns:

- `employee_id`
- `role`
- `department`
- `skills`
- `experience_years`
- `performance_score`

Example:

```csv
employee_id,role,department,skills,experience_years,performance_score
Employee_01,AI Product Owner,Strategy & Transformation,"Change management, Data visualization, Product strategy, Stakeholder management",9,4.5
```

### `roles.csv`

Required columns:

- `role`
- `required_skills`

Example:

```csv
role,required_skills
AI Product Owner,"AI risk compliance, Change management, GenAI orchestration, LLM evaluation, Product strategy, Prompt governance, Stakeholder management"
```

### `market_trends.csv`

Required columns:

- `skill`
- `trend_score`

Example:

```csv
skill,trend_score
GenAI orchestration,99
```

If uploaded CSV headers do not match the expected schema exactly, the analysis route returns a validation error.

## Key files

- `app/page.jsx`: main dashboard, uploads, analysis trigger, and chart rendering
- `app/api/analyze/route.js`: request validation and response generation
- `lib/analytics.js`: core business logic for scoring and evidence retrieval
- `data/*.json`: bundled demo data used by the Next.js app
- `app.py`: legacy Python prototype with similar analytics and visualizations

## Notes and limitations

- The analytics engine is deterministic and offline-friendly; it does not call an external LLM.
- Evidence retrieval is based on local text chunking and heuristic scoring.
- The Next.js app is the main implementation in this repository.
- The Streamlit app is useful for comparison, experimentation, or fallback demos.
