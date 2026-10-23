import { useEffect, useMemo, useRef, useState } from "react";
import Results from "./Results";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const SUGGESTED_REQUESTS = [
  "Explore this dataset and summarize the main patterns.",
  "Build a prediction model and compare the candidate models.",
  "Create charts for the most important distributions and relationships.",
  "Clean this dataset and prepare it for modeling.",
];

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function errorMessage(data) {
  if (!data) return "Analysis failed.";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    const messages = data.detail.map((item) => item?.msg).filter(Boolean);
    if (messages.length) return messages.join(" ");
  }
  return "Analysis failed.";
}

export default function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const [submittedQuery, setSubmittedQuery] = useState("");
  const resultsRef = useRef(null);

  const fileMeta = useMemo(() => {
    if (!file) return null;
    return {
      name: file.name,
      size: formatBytes(file.size),
    };
  }, [file]);

  useEffect(() => {
    if (results) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [results]);

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
        throw new Error(errorMessage(data));
      }

      setSubmittedQuery(query.trim());
      setResults(data);
    } catch (requestError) {
      setError(requestError.message || "Analysis failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Agentic Data Analyst</p>
        <h1>Agentic Data Analyst</h1>
        <p className="subtitle">
          Upload a CSV. The agent plans the work, and the tools calculate the numbers.
        </p>
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
          <label htmlFor="query">Analysis request</label>
          <textarea
            id="query"
            rows="5"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Explore this dataset and summarize the main patterns."
          />
        </div>

        <div className="prompt-row" aria-label="Suggested requests">
          {SUGGESTED_REQUESTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="prompt-chip"
              onClick={() => setQuery(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>

        <p className="scope-note">
          Ask about the uploaded file: explore it, chart it, clean it, or train a model.
        </p>

        <button className="primary-button" onClick={handleAnalyze} disabled={loading}>
          {loading ? "Running the analysis..." : "Analyze dataset"}
        </button>
        {loading ? (
          <p className="scope-note">
            Profiling the file, choosing a plan, then running only the tools that plan needs.
          </p>
        ) : null}
      </section>

      {error && (
        <section className="card error-card">
          <h2>Something went wrong</h2>
          <p>{error}</p>
        </section>
      )}

      {results && (
        <div ref={resultsRef}>
          <Results results={results} query={submittedQuery} apiBaseUrl={API_BASE_URL} />
        </div>
      )}
    </div>
  );
}
