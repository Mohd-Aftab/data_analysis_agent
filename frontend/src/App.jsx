import { useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const examplePlaceholder =
  "Analyze customer churn, identify important patterns, create useful visualizations, and build a prediction model.";

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function prettifyLabel(value) {
  if (!value) return "N/A";
  return String(value).replace(/_/g, " ");
}

function renderValue(value) {
  if (value === null || value === undefined) return "N/A";
  if (typeof value === "object") {
    return <pre className="code-block">{JSON.stringify(value, null, 2)}</pre>;
  }
  return String(value);
}

function Section({ title, children }) {
  return (
    <section className="card">
      <div className="section-header">
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  const fileMeta = useMemo(() => {
    if (!file) return null;
    return {
      name: file.name,
      size: formatBytes(file.size),
    };
  }, [file]);

  async function handleAnalyze() {
    if (!file) {
      setError("Please upload a CSV file.");
      return;
    }

    if (!query.trim()) {
      setError("Please enter an analysis request.");
      return;
    }

    setLoading(true);
    setError("");
    setResults(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_query", query.trim());

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setResults(data);
    } catch (requestError) {
      setError(requestError.message || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  const charts = results?.chart_paths || [];
  const profile = results?.profile || {};
  const missingValues = profile?.missing_values || {};
  const dtypes = profile?.dtypes || {};
  const numericalColumns = Object.entries(dtypes)
    .filter(([, type]) => ["int64", "float64", "int32", "float32"].some((token) => String(type).includes(token)))
    .map(([column]) => column);
  const categoricalColumns = Object.entries(dtypes)
    .filter(([, type]) => !["int64", "float64", "int32", "float32", "bool"].some((token) => String(type).includes(token)))
    .map(([column]) => column);

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Agentic Data Analyst</p>
        <h1>Agentic Data Analyst</h1>
        <p className="subtitle">LLM-driven autonomous data analysis</p>
      </header>

      <section className="card form-card">
        <div className="input-group">
          <label htmlFor="csv-upload">Upload CSV</label>
          <input
            id="csv-upload"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
          {fileMeta && (
            <div className="file-meta">
              <span>{fileMeta.name}</span>
              <span>{fileMeta.size}</span>
            </div>
          )}
        </div>

        <div className="input-group">
          <label htmlFor="query">Analysis Request</label>
          <textarea
            id="query"
            rows="6"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={examplePlaceholder}
          />
        </div>

        <button className="primary-button" onClick={handleAnalyze} disabled={loading}>
          {loading ? "Analyzing Dataset..." : "Analyze Dataset"}
        </button>
      </section>

      {error && (
        <section className="card error-card">
          <h2>Error</h2>
          <p>{error}</p>
        </section>
      )}

      {results && (
        <main className="results-grid">
          <Section title="Planner">
            <div className="key-value-grid">
              <div>
                <span className="label">Intent</span>
                <strong>{results.intent || "N/A"}</strong>
              </div>
              <div>
                <span className="label">Target Column</span>
                <strong>{results.target_column || "N/A"}</strong>
              </div>
            </div>
          </Section>

          <Section title="Dataset Profile">
            <div className="stats-grid">
              <div className="stat-card">
                <span className="label">Rows</span>
                <strong>{profile.rows ?? "N/A"}</strong>
              </div>
              <div className="stat-card">
                <span className="label">Columns</span>
                <strong>{profile.columns ?? "N/A"}</strong>
              </div>
              <div className="stat-card">
                <span className="label">Duplicates</span>
                <strong>{profile.duplicates ?? "N/A"}</strong>
              </div>
              <div className="stat-card">
                <span className="label">Memory Usage</span>
                <strong>{profile.memory_usage_mb ?? "N/A"} MB</strong>
              </div>
            </div>
            <div className="split-columns">
              <div>
                <span className="label">Numerical Columns</span>
                <ul>
                  {numericalColumns.length ? numericalColumns.map((column) => <li key={column}>{column}</li>) : <li>N/A</li>}
                </ul>
              </div>
              <div>
                <span className="label">Categorical Columns</span>
                <ul>
                  {categoricalColumns.length ? categoricalColumns.map((column) => <li key={column}>{column}</li>) : <li>N/A</li>}
                </ul>
              </div>
            </div>
            <div>
              <span className="label">Missing Values</span>
              <pre className="code-block">{JSON.stringify(missingValues, null, 2)}</pre>
            </div>
          </Section>

          <Section title="Preprocessing">
            <span className="label">Selected Actions</span>
            <ul>
              {(results.preprocessing_plan || []).length
                ? results.preprocessing_plan.map((item) => <li key={item}>{prettifyLabel(item)}</li>)
                : <li>N/A</li>}
            </ul>
            <span className="label">Summary</span>
            <ul>
              {(results.preprocessing_summary || []).length
                ? results.preprocessing_summary.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)
                : <li>N/A</li>}
            </ul>
          </Section>

          <Section title="EDA">
            <span className="label">Selected EDA Actions</span>
            <ul>
              {(results.eda_plan || []).length
                ? results.eda_plan.map((item) => <li key={item}>{prettifyLabel(item)}</li>)
                : <li>N/A</li>}
            </ul>
            <span className="label">Important EDA Results</span>
            {renderValue(results.eda_result)}
          </Section>

          <Section title="Feature Engineering">
            <span className="label">Selected Transformations</span>
            {renderValue(results.feature_engineering_plan)}
          </Section>

          <Section title="Model Comparison">
            {results.model_results ? (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Metrics</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(results.model_results).map(([modelName, modelInfo]) => (
                      <tr key={modelName} className={results.best_model === modelName ? "best-row" : ""}>
                        <td>
                          {modelName}
                          {results.best_model === modelName ? <span className="best-badge">Best</span> : null}
                        </td>
                        <td>
                          <pre className="table-metrics">{JSON.stringify(modelInfo.metrics || {}, null, 2)}</pre>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>N/A</p>
            )}
          </Section>

          <Section title="Visualizations">
            {charts.length ? (
              <div className="charts-grid">
                {charts.map((path) => (
                  <figure key={path} className="chart-card">
                    <img src={`${API_BASE_URL}${path}`} alt={path.split("/").pop()} />
                    <figcaption>{path.split("/").pop()}</figcaption>
                  </figure>
                ))}
              </div>
            ) : (
              <p>No charts were generated.</p>
            )}
          </Section>

          <Section title="AI Insights">
            <div className="insights-block">
              <span className="label">Summary</span>
              <p>{results.insights?.summary || "N/A"}</p>
            </div>
            <div className="insights-block">
              <span className="label">Key Findings</span>
              <ul>
                {(results.insights?.key_findings || []).length
                  ? results.insights.key_findings.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)
                  : <li>N/A</li>}
              </ul>
            </div>
            <div className="insights-block">
              <span className="label">Recommendations</span>
              <ul>
                {(results.insights?.recommendations || []).length
                  ? results.insights.recommendations.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)
                  : <li>N/A</li>}
              </ul>
            </div>
          </Section>
        </main>
      )}
    </div>
  );
}
