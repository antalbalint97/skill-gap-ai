"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";

import competitionScenarioSeed from "../data/competition_scenario.json";
import employeesSeed from "../data/employees.json";
import marketSeed from "../data/market_trends.json";
import rolesSeed from "../data/roles.json";
import {
  buildAnalysisResponse,
  csvFromRecords,
  parseCsv,
  validateDataset,
} from "../lib/analytics";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <div className="chart-loading">Rendering chart...</div>,
});

const DEMO_DATA = {
  employees: employeesSeed,
  roles: rolesSeed,
  market: marketSeed,
};

const DEMO_EVIDENCE_NOTE = `AI Product Owner profiles are now expected to carry GenAI orchestration, prompt governance, and AI risk compliance capabilities within transformation programs. External demand is rising faster than internal enablement capacity.

PromptOps and governance-oriented roles increasingly require LLM evaluation, policy controls, and model monitoring. Internal mobility from workforce analytics into data science remains attractive when statistics, Python, and experiment design are already present.`;

const DEFAULT_SCENARIO = {
  id: "default",
  name: "Bundled synthetic demo",
  summary:
    "Synthetic enterprise workforce with a lightweight analyst note for quick walkthroughs.",
  analystNoteName: "Demo analyst note",
  analystNote: DEMO_EVIDENCE_NOTE,
  documents: [],
  data: DEMO_DATA,
};

const COMPETITION_SCENARIO = {
  ...competitionScenarioSeed,
  data: {
    employees: employeesSeed,
    roles: rolesSeed,
    market: competitionScenarioSeed.market,
  },
};

const ARCHITECTURE_DESCRIPTION = `Data Layer
- HR employee records, role templates, market trend signals, and uploaded evidence sources land as structured inputs.
- Bundled synthetic data mirrors an enterprise workforce and can be replaced with uploaded CSVs.

Embedding Layer
- Employee skill profiles and role requirement sets are transformed into lightweight vectors.
- The placeholder vectorizer keeps the app offline-friendly while preserving an OpenAI-ready structure.

Evidence Retrieval Layer
- Analyst notes, text uploads, and PDFs are converted into text, chunked, scored against workforce questions, and attached to the highest-priority insights.

Agent Reasoning Layer
- Skill Extraction Agent structures free-form skill strings.
- Market Intelligence Agent weights external demand signals.
- Gap Reasoning Agent compares internal coverage to role requirements.

Recommendation Engine
- Reskilling routes, hiring priorities, and risk skills are ranked with similarity, readiness, urgency, and supporting evidence.`;

function buildScenarioDocuments(scenario) {
  const documents = (scenario.documents || []).map((document) => ({ ...document }));

  if (scenario.analystNote?.trim()) {
    documents.unshift({
      name: scenario.analystNoteName || "Analyst note",
      text: scenario.analystNote,
      sourceType: "Analyst note",
      mimeType: "text/plain",
    });
  }

  return documents;
}

const INITIAL_DOCUMENTS = buildScenarioDocuments(DEFAULT_SCENARIO);

function MetricCard({ label, value, note }) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{note}</span>
    </div>
  );
}

function SectionHeading({ eyebrow, title, copy }) {
  return (
    <div className="section-heading">
      <p>{eyebrow}</p>
      <h2>{title}</h2>
      <span>{copy}</span>
    </div>
  );
}

function DataTable({ columns, rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${row[columns[0].key]}-${index}`}>
              {columns.map((column) => (
                <td key={column.key}>{row[column.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UploadField({ id, label, onChange, accept = ".csv", multiple = false }) {
  return (
    <label className="upload-field" htmlFor={id}>
      <span>{label}</span>
      <input id={id} type="file" accept={accept} multiple={multiple} onChange={onChange} />
    </label>
  );
}

function formatConfidence(item) {
  if (!item) {
    return "";
  }
  return `${item.confidenceLabel} confidence (${item.confidenceScore}%)`;
}

function TraceCard({ label, item }) {
  if (!item) {
    return null;
  }

  return (
    <article className="trace-card">
      <div className="trace-head">
        <p className="trace-label">{label}</p>
        <span className={`confidence-pill ${item.confidenceLabel?.toLowerCase()}`}>
          {formatConfidence(item)}
        </span>
      </div>
      <h3>{item.label}</h3>
      <p className="trace-meta">
        {item.sourceCount} evidence source{item.sourceCount === 1 ? "" : "s"} attached
      </p>
      <div className="trace-copy">
        <strong>Why flagged</strong>
        <p>{item.whyFlagged}</p>
      </div>
      <div className="trace-copy">
        <strong>Suggested action</strong>
        <p>{item.suggestedAction}</p>
      </div>
      <div className="trace-copy">
        <strong>Evidence</strong>
        {item.evidence?.map((evidence, index) => (
          <div className="evidence-snippet" key={`${evidence.sourceName}-${index}`}>
            <span>
              {evidence.sourceName} | {evidence.confidence} confidence ({evidence.confidenceScore}%)
            </span>
            <p>{evidence.snippet}</p>
          </div>
        ))}
      </div>
    </article>
  );
}

export default function Home() {
  const [sourceMode, setSourceMode] = useState("synthetic");
  const [selectedScenario, setSelectedScenario] = useState(DEFAULT_SCENARIO.id);
  const [uploadedData, setUploadedData] = useState({
    employees: null,
    roles: null,
    market: null,
  });
  const [uploadError, setUploadError] = useState("");
  const [documentText, setDocumentText] = useState(DEFAULT_SCENARIO.analystNote);
  const [uploadedDocuments, setUploadedDocuments] = useState(DEFAULT_SCENARIO.documents);
  const [analysisResult, setAnalysisResult] = useState(() =>
    buildAnalysisResponse(DEMO_DATA, INITIAL_DOCUMENTS)
  );
  const [analysisError, setAnalysisError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const syntheticDataset = useMemo(
    () => (selectedScenario === COMPETITION_SCENARIO.id ? COMPETITION_SCENARIO.data : DEFAULT_SCENARIO.data),
    [selectedScenario]
  );
  const hasCompleteUpload = uploadedData.employees && uploadedData.roles && uploadedData.market;
  const activeDataset = useMemo(
    () => (sourceMode === "upload" && hasCompleteUpload ? uploadedData : syntheticDataset),
    [sourceMode, hasCompleteUpload, syntheticDataset, uploadedData]
  );

  const activeDocuments = useMemo(() => {
    const documents = [...uploadedDocuments];
    if (documentText.trim()) {
      documents.unshift({
        name: "Analyst note",
        text: documentText,
        sourceType: "Analyst note",
        mimeType: "text/plain",
      });
    }
    return documents;
  }, [documentText, uploadedDocuments]);

  const performAnalysis = useCallback(async (datasets, documents) => {
    setIsLoading(true);
    setAnalysisError("");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          datasets,
          documents,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Unable to analyze the current workforce inputs.");
      }

      setAnalysisResult(payload);
    } catch (error) {
      setAnalysisError(error.message || "Unable to analyze the current workforce inputs.");
      setAnalysisResult(buildAnalysisResponse(datasets, documents));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void performAnalysis(DEFAULT_SCENARIO.data, INITIAL_DOCUMENTS);
  }, [performAnalysis]);

  async function handleDatasetFile(kind, file) {
    if (!file) {
      return;
    }

    try {
      const records = parseCsv(await file.text());
      validateDataset(kind, records);
      setUploadedData((current) => ({ ...current, [kind]: records }));
      setUploadError("");
    } catch (error) {
      setUploadError(error.message || "Could not parse CSV file.");
    }
  }

  async function handleEvidenceFiles(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length) {
      return;
    }
    try {
      const needsPdfSupport = files.some((file) => {
        const lowerName = file.name.toLowerCase();
        return file.type === "application/pdf" || lowerName.endsWith(".pdf");
      });
      const pdfjs = needsPdfSupport ? await import("pdfjs-dist/legacy/build/pdf.mjs") : null;

      const loaded = await Promise.all(
        files.map(async (file) => {
          const lowerName = file.name.toLowerCase();
          if (file.type === "application/pdf" || lowerName.endsWith(".pdf")) {
            const loadingTask = pdfjs.getDocument({
              data: await file.arrayBuffer(),
              useWorkerFetch: false,
              isEvalSupported: false,
              disableFontFace: true,
            });
            const pdf = await loadingTask.promise;
            const pages = [];

            for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
              const page = await pdf.getPage(pageNumber);
              const content = await page.getTextContent();
              const text = content.items
                .map((item) => ("str" in item ? item.str : ""))
                .join(" ")
                .replace(/\s+/g, " ")
                .trim();
              if (text) {
                pages.push(text);
              }
            }

            return {
              name: file.name,
              text: pages.join("\n\n"),
              mimeType: "application/pdf",
              sourceType: "Uploaded PDF",
            };
          }

          return {
            name: file.name,
            text: await file.text(),
            mimeType: file.type || "text/plain",
            sourceType: "Uploaded text",
          };
        })
      );

      setUploadedDocuments(loaded.filter((document) => document.text?.trim()));
      setAnalysisError("");
    } catch (error) {
      setAnalysisError(error.message || "Could not extract text from the uploaded evidence files.");
    }
  }

  const dashboard = analysisResult.dashboard;
  const evidence = analysisResult.evidence;
  const meta = analysisResult.meta;
  const analyzeDisabled = sourceMode === "upload" && !hasCompleteUpload;
  const scenarioMeta =
    sourceMode === "upload"
      ? {
          name: "Custom upload bundle",
          summary: "User-provided workforce CSV files with optional uploaded evidence documents.",
        }
      : selectedScenario === COMPETITION_SCENARIO.id
        ? COMPETITION_SCENARIO
        : DEFAULT_SCENARIO;

  function loadScenario(scenario) {
    const scenarioDocuments = buildScenarioDocuments(scenario);
    setSourceMode("synthetic");
    setSelectedScenario(scenario.id);
    setDocumentText(scenario.analystNote || "");
    setUploadedDocuments((scenario.documents || []).map((document) => ({ ...document })));
    setUploadError("");
    setAnalysisError("");
    void performAnalysis(scenario.data, scenarioDocuments);
  }

  return (
    <div className="app-shell">
      <aside className="control-rail">
        <div className="rail-intro">
          <p className="eyebrow">Enterprise Workforce Intelligence</p>
          <h1>Skill Gap Radar Agent</h1>
          <span>
            Consulting-style workforce dashboard for skill extraction, market comparison, gap
            detection, recommendation logic, and evidence-backed decision traceability.
          </span>
        </div>

        <div className="control-group">
          <p className="group-label">Dataset Mode</p>
          <div className="toggle-row">
            <button
              className={sourceMode === "synthetic" ? "is-active" : ""}
              onClick={() => setSourceMode("synthetic")}
              type="button"
            >
              Use synthetic data
            </button>
            <button
              className={sourceMode === "upload" ? "is-active" : ""}
              onClick={() => setSourceMode("upload")}
              type="button"
            >
              Upload CSV bundle
            </button>
          </div>
        </div>

        <div className="control-group">
          <p className="group-label">Competition Scenario</p>
          <div className="scenario-card">
            <strong>{COMPETITION_SCENARIO.name}</strong>
            <p>{COMPETITION_SCENARIO.summary}</p>
          </div>
          <div className="scenario-actions">
            <button
              className={selectedScenario === COMPETITION_SCENARIO.id ? "scenario-button is-active" : "scenario-button"}
              onClick={() => loadScenario(COMPETITION_SCENARIO)}
              type="button"
            >
              Load one-click demo
            </button>
            <button
              className={selectedScenario === DEFAULT_SCENARIO.id ? "scenario-button is-active" : "scenario-button"}
              onClick={() => loadScenario(DEFAULT_SCENARIO)}
              type="button"
            >
              Reset default demo
            </button>
          </div>
          <span className="helper-copy">
            The competition scenario loads recent public OECD and EU evidence summaries directly into
            the trace pipeline.
          </span>
        </div>

        <div className="control-group">
          <p className="group-label">Input Files</p>
          <UploadField
            id="employees"
            label="employees.csv"
            onChange={(event) => handleDatasetFile("employees", event.target.files?.[0])}
          />
          <UploadField
            id="roles"
            label="roles.csv"
            onChange={(event) => handleDatasetFile("roles", event.target.files?.[0])}
          />
          <UploadField
            id="market"
            label="market_trends.csv"
            onChange={(event) => handleDatasetFile("market", event.target.files?.[0])}
          />
          <span className="helper-copy">
            {sourceMode === "upload" && !hasCompleteUpload
              ? "Upload all three files to replace the bundled demo scenario."
              : "Bundled synthetic data remains available for instant demo mode."}
          </span>
          {uploadError ? <p className="error-copy">{uploadError}</p> : null}
        </div>

        <div className="control-group">
          <p className="group-label">Evidence Inputs</p>
          <label className="text-block" htmlFor="analyst-note">
            <span>Analyst note</span>
            <textarea
              id="analyst-note"
              value={documentText}
              onChange={(event) => setDocumentText(event.target.value)}
              placeholder="Paste role profiles, market notes, or policy excerpts here."
            />
          </label>
          <UploadField
            id="evidence-files"
            label="Upload PDF / text evidence"
            accept=".txt,.md,.pdf"
            multiple
            onChange={(event) => handleEvidenceFiles(event.target.files)}
          />
          <span className="helper-copy">
            {activeDocuments.length} evidence source{activeDocuments.length === 1 ? "" : "s"} queued
            for retrieval.
          </span>
          {meta?.sourceNames?.length ? (
            <div className="source-list">
              {meta.sourceNames.map((sourceName) => (
                <span key={sourceName}>{sourceName}</span>
              ))}
            </div>
          ) : null}
          <button
            className="analyze-button"
            disabled={analyzeDisabled || isLoading}
            onClick={() => void performAnalysis(activeDataset, activeDocuments)}
            type="button"
          >
            {isLoading ? "Running analysis..." : "Run evidence-backed analysis"}
          </button>
          {analysisError ? <p className="error-copy">{analysisError}</p> : null}
        </div>

        <div className="control-group">
          <p className="group-label">Sample Data</p>
          <a
            className="download-link"
            download="employees.csv"
            href={`data:text/csv;charset=utf-8,${encodeURIComponent(csvFromRecords(syntheticDataset.employees))}`}
          >
            Download employees.csv
          </a>
          <a
            className="download-link"
            download="roles.csv"
            href={`data:text/csv;charset=utf-8,${encodeURIComponent(csvFromRecords(syntheticDataset.roles))}`}
          >
            Download roles.csv
          </a>
          <a
            className="download-link"
            download="market_trends.csv"
            href={`data:text/csv;charset=utf-8,${encodeURIComponent(csvFromRecords(syntheticDataset.market))}`}
          >
            Download market_trends.csv
          </a>
        </div>

        <details className="details-panel">
          <summary>How this demo works</summary>
          <div>
            <p>
              The bundled dataset simulates an enterprise workforce across AI, analytics, platform,
              and governance roles.
            </p>
            <p>
              A thin backend route analyzes the dataset, extracts text from uploaded PDFs and text
              files, and scores the best evidence snippets against the highest-priority workforce
              questions.
            </p>
            <p>
              The flow mirrors the product story: skill extraction, market intelligence, gap
              reasoning, recommendation logic, and evidence retrieval.
            </p>
          </div>
        </details>

        <details className="details-panel">
          <summary>Architecture diagram description</summary>
          <pre>{ARCHITECTURE_DESCRIPTION}</pre>
        </details>
      </aside>

      <main className="dashboard">
        <header className="hero-band">
          <div className="hero-copy">
            <p>{meta.recommendationMode}</p>
            <h2>Decision-ready workforce intelligence with evidence-backed reasoning traces.</h2>
            <span className="hero-subcopy">{scenarioMeta.summary}</span>
          </div>
          <div className="hero-pills">
            <span>Scenario: {scenarioMeta.name}</span>
            <span>{meta.evidenceMode}</span>
            <span>{meta.documentsProcessed} sources indexed</span>
            <span>{meta.chunksIndexed} evidence chunks scored</span>
            <span>Top Missing Skill: {dashboard.summary.topMissing}</span>
            <span>Reskilling: {dashboard.summary.reskilling}</span>
            <span>Hiring Priority: {dashboard.summary.hiring}</span>
          </div>
        </header>

        <section className="metric-grid">
          <MetricCard
            label="Employees in Scope"
            value={dashboard.summary.employeeCount}
            note="Scenario workforce population"
          />
          <MetricCard
            label="Critical Skill Gaps"
            value={dashboard.summary.criticalSkills}
            note="Weighted by market urgency and low coverage"
          />
          <MetricCard
            label="High Priority Roles"
            value={dashboard.summary.highPriorityRoles}
            note="External hiring roles above the urgency threshold"
          />
          <MetricCard
            label="Best Reskilling Match"
            value={`${Math.round(dashboard.summary.bestReskillingMatch)}%`}
            note="Top internal mobility trajectory match"
          />
        </section>

        <section className="trace-grid">
          <TraceCard label="Top Missing Skill Trace" item={evidence.summary.topMissing} />
          <TraceCard label="Reskilling Route Trace" item={evidence.summary.topReskilling} />
          <TraceCard label="Hiring Priority Trace" item={evidence.summary.topHiring} />
        </section>

        <section className="content-band">
          <SectionHeading
            eyebrow="SECTION 1"
            title="Skill Coverage Heatmap"
            copy="Role-by-role readiness across required capabilities."
          />
          <Plot
            className="chart-shell"
            data={[
              {
                type: "heatmap",
                z: dashboard.heatmap.values,
                x: dashboard.heatmap.skills,
                y: dashboard.heatmap.roles,
                colorscale: [
                  [0, "#EEF2F5"],
                  [0.55, "#F4C7A1"],
                  [1, "#E57B2E"],
                ],
                hovertemplate: "%{y}<br>%{x}<br>Coverage %{z}%<extra></extra>",
              },
            ]}
            layout={{
              autosize: true,
              height: 430,
              margin: { l: 110, r: 20, t: 20, b: 120 },
              paper_bgcolor: "#FFFFFF",
              plot_bgcolor: "#FFFFFF",
              xaxis: { tickangle: -35 },
            }}
            config={{ displayModeBar: false, responsive: true }}
            useResizeHandler
          />
        </section>

        <section className="dual-band">
          <div className="content-band">
            <SectionHeading
              eyebrow="SECTION 2"
              title="Top Missing Skills"
              copy="Highest weighted gaps after internal coverage, market pressure, and evidence scoring."
            />
            <Plot
              className="chart-shell"
              data={[
                {
                  type: "bar",
                  orientation: "h",
                  x: dashboard.missingSkills.slice(0, 10).map((item) => item.urgencyScore),
                  y: dashboard.missingSkills.slice(0, 10).map((item) => item.skill),
                  marker: {
                    color: dashboard.missingSkills.slice(0, 10).map((item) => item.marketTrend),
                    colorscale: [
                      [0, "#F6EADF"],
                      [1, "#E57B2E"],
                    ],
                  },
                  hovertemplate:
                    "%{y}<br>Urgency %{x}<br>Trend %{marker.color}<extra></extra>",
                },
              ]}
              layout={{
                autosize: true,
                height: 370,
                margin: { l: 150, r: 20, t: 10, b: 40 },
                paper_bgcolor: "#FFFFFF",
                plot_bgcolor: "#FFFFFF",
              }}
              config={{ displayModeBar: false, responsive: true }}
              useResizeHandler
            />
          </div>

          <div className="content-band">
            <SectionHeading
              eyebrow="Signal Table"
              title="Gap Summary"
              copy="Internal coverage, market pressure, and role exposure in one view."
            />
            <DataTable
              columns={[
                { key: "skill", label: "Skill" },
                { key: "avgInternalCoverage", label: "Internal Coverage %" },
                { key: "marketTrend", label: "Trend Score" },
                { key: "roleExposure", label: "Roles Exposed" },
                { key: "urgencyLabel", label: "Urgency" },
              ]}
              rows={dashboard.missingSkills.slice(0, 8)}
            />
          </div>
        </section>

        <section className="dual-band">
          <div className="content-band">
            <SectionHeading
              eyebrow="SECTION 3"
              title="Recommended Reskilling Candidates"
              copy="Internal mobility matches ranked by trajectory fit, urgency, and evidence-supported rationale."
            />
            <DataTable
              columns={[
                { key: "employee_id", label: "Employee" },
                { key: "current_role", label: "Current Role" },
                { key: "target_role", label: "Target Role" },
                { key: "trajectory_match_pct", label: "Trajectory Match %" },
                { key: "matched_skills", label: "Matched Skills" },
                { key: "primary_missing_skills", label: "Primary Missing Skills" },
              ]}
              rows={dashboard.reskillingCandidates}
            />
          </div>

          <div className="snapshot-panel">
            <p className="snapshot-label">Recommendation Snapshot</p>
            <div>
              <h3>Top Missing Skills</h3>
              <p>GenAI orchestration</p>
              <p>Prompt governance</p>
              <p>AI risk compliance</p>
            </div>
            <div>
              <h3>Reskilling Candidate</h3>
              <p>{dashboard.summary.reskilling}</p>
            </div>
            <div>
              <h3>Hiring Priority</h3>
              <p>{dashboard.summary.hiring}</p>
            </div>
          </div>
        </section>

        <section className="content-band">
          <SectionHeading
            eyebrow="SECTION 4"
            title="Hiring Priority Index"
            copy="Urgency score for external hiring when internal coverage remains below threshold."
          />
          <Plot
            className="chart-shell"
            data={[
              {
                type: "bar",
                orientation: "h",
                x: dashboard.hiringPriority
                  .slice()
                  .reverse()
                  .map((item) => item.hiringPriorityIndex),
                y: dashboard.hiringPriority
                  .slice()
                  .reverse()
                  .map((item) => item.role),
                marker: {
                  color: dashboard.hiringPriority
                    .slice()
                    .reverse()
                    .map((item) =>
                      item.priority === "HIGH"
                        ? "#E57B2E"
                        : item.priority === "MEDIUM"
                          ? "#F4C7A1"
                          : "#B1BDC6"
                    ),
                },
                customdata: dashboard.hiringPriority
                  .slice()
                  .reverse()
                  .map((item) => [item.primaryGapSkill, item.priority]),
                hovertemplate:
                  "%{y}<br>Index %{x}<br>%{customdata[1]}<br>Primary gap %{customdata[0]}<extra></extra>",
              },
            ]}
            layout={{
              autosize: true,
              height: 360,
              margin: { l: 150, r: 20, t: 10, b: 40 },
              paper_bgcolor: "#FFFFFF",
              plot_bgcolor: "#FFFFFF",
            }}
            config={{ displayModeBar: false, responsive: true }}
            useResizeHandler
          />
        </section>

        <section className="content-band">
          <SectionHeading
            eyebrow="SECTION 5"
            title="Skill Trend Alignment Chart"
            copy="External market demand versus current internal skill coverage."
          />
          <Plot
            className="chart-shell"
            data={[
              {
                type: "scatter",
                mode: "markers+text",
                x: dashboard.trendAlignment.map((item) => item.trendScore),
                y: dashboard.trendAlignment.map((item) => item.internalCoveragePct),
                text: dashboard.trendAlignment.map((item) => item.skill),
                textposition: "top center",
                marker: {
                  size: dashboard.trendAlignment.map((item) => Math.max(item.alignmentGap / 2, 10)),
                  color: dashboard.trendAlignment.map((item) =>
                    item.riskBand === "At Risk"
                      ? "#C05746"
                      : item.riskBand === "Develop"
                        ? "#F4C7A1"
                        : "#2D7D60"
                  ),
                  opacity: 0.85,
                },
                hovertemplate:
                  "%{text}<br>Trend %{x}<br>Coverage %{y}%<extra></extra>",
              },
            ]}
            layout={{
              autosize: true,
              height: 500,
              margin: { l: 70, r: 20, t: 10, b: 60 },
              paper_bgcolor: "#FFFFFF",
              plot_bgcolor: "#FFFFFF",
              shapes: [
                {
                  type: "line",
                  x0: 75,
                  x1: 75,
                  y0: 0,
                  y1: 100,
                  line: { color: "#B8C3CB", width: 1, dash: "dot" },
                },
                {
                  type: "line",
                  x0: 35,
                  x1: 100,
                  y0: 45,
                  y1: 45,
                  line: { color: "#B8C3CB", width: 1, dash: "dot" },
                },
              ],
              xaxis: { title: "Market Trend Score", range: [35, 100] },
              yaxis: { title: "Internal Coverage %", range: [0, 100] },
            }}
            config={{ displayModeBar: false, responsive: true }}
            useResizeHandler
          />
        </section>
      </main>
    </div>
  );
}
