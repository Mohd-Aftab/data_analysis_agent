import { useState } from "react";
import {
  chartCards,
  conclusionFallback,
  datasetSnapshot,
  decisionTrace,
  featureSentences,
  intentLabel,
  modelCards,
  patternBlocks,
  preparationLines,
  workflowSteps,
} from "./format";

function Section({ title, kicker, children }) {
  return (
    <section className="card">
      <div className="section-header">
        {kicker ? <p className="kicker">{kicker}</p> : null}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function ChipList({ items }) {
  const [expanded, setExpanded] = useState(false);
  if (!items.length) return <p className="muted">None</p>;
  const visible = expanded ? items : items.slice(0, 14);
  const hidden = items.length - visible.length;

  return (
    <div className="chip-row">
      {visible.map((item) => (
        <span className="chip" key={item}>{item}</span>
      ))}
      {hidden > 0 ? (
        <button type="button" className="chip chip-button" onClick={() => setExpanded(true)}>
          +{hidden} more
        </button>
      ) : null}
    </div>
  );
}

function Bars({ rows }) {
  return (
    <div className="bar-list">
      {rows.map((row) => (
        <div className="bar-row" key={`${row.label}-${row.value}`}>
          <span className="bar-label">{row.label}</span>
          <div className="bar-track" aria-hidden="true">
            <div className="bar-fill" style={{ width: `${Math.max(row.share || 0, 2)}%` }} />
          </div>
          <span className="bar-value">
            {row.value}
            {row.showShare ? ` · ${row.share}%` : ""}
          </span>
        </div>
      ))}
    </div>
  );
}

function PatternBlock({ block }) {
  if (block.kind === "table") {
    return (
      <div className="pattern-block">
        <h3>{block.title}</h3>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                {block.columns.map((column) => <th key={column}>{column}</th>)}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row) => (
                <tr key={row.column}>
                  <td>{row.column}</td>
                  <td>{row.mean}</td>
                  <td>{row.median}</td>
                  <td>{row.min}</td>
                  <td>{row.max}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (block.kind === "categories") {
    return (
      <div className="pattern-block">
        <h3>{block.title}</h3>
        <div className="category-grid">
          {block.groups.map((group) => (
            <article key={group.name} className="category-card">
              <h4>{group.name}</h4>
              <Bars rows={group.items.map((item) => ({
                label: item.label,
                value: item.count,
                share: item.share,
                showShare: true,
              }))}
              />
              {group.hidden > 0 ? <p className="muted">{group.hidden} more values hidden</p> : null}
            </article>
          ))}
        </div>
        {block.skipped.length ? (
          <p className="muted">
            {block.skipped.map((item) => `${item.column} (${item.count.toLocaleString()} distinct values)`).join(", ")}
            {" "}left out of the breakdown because those columns behave like identifiers.
          </p>
        ) : null}
      </div>
    );
  }

  if (block.kind === "bars") {
    return (
      <div className="pattern-block">
        <h3>{block.title}</h3>
        <Bars rows={block.rows} />
      </div>
    );
  }

  return (
    <div className="pattern-block">
      <h3>{block.title}</h3>
      {block.note ? <p className="muted">{block.note}</p> : null}
      {block.empty ? <p>{block.empty}</p> : null}
      {block.rows?.length ? (
        <ul className="plain-list">
          {block.rows.map((row) => (
            <li key={row.label}>
              <strong>{row.label}</strong>
              <span>{row.value}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export default function Results({ results, query, apiBaseUrl }) {
  const summary = results.insights?.summary;
  const findings = results.insights?.key_findings || [];
  const recommendations = results.insights?.recommendations || [];
  const steps = workflowSteps(results);
  const dataset = datasetSnapshot(results.profile);
  const models = modelCards(results);
  const patterns = patternBlocks(results);
  const charts = chartCards(results, apiBaseUrl);
  const preparation = preparationLines(results);
  const features = featureSentences(results);
  const trace = decisionTrace(results);
  const bestModel = models.find((model) => model.best);

  return (
    <main className="results-grid">
      <section className="card answer-card">
        <p className="kicker">Conclusion</p>
        {query ? <p className="asked">You asked: {query}</p> : null}
        <p className="conclusion">{summary || conclusionFallback(results)}</p>
        <p className="intent-line">{intentLabel(results.intent)}</p>

        {(findings.length || recommendations.length) ? (
          <div className="findings-grid">
            {findings.length ? (
              <div>
                <h3>Findings</h3>
                <ul>
                  {findings.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            ) : null}
            {recommendations.length ? (
              <div>
                <h3>What to do next</h3>
                <ul>
                  {recommendations.map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}
      </section>

      {steps.length ? (
        <section className="card step-card">
          <h2>What ran</h2>
          <ol className="step-list">
            {steps.map((step) => <li key={step}>{step}</li>)}
          </ol>
        </section>
      ) : null}

      {dataset ? (
        <Section title="Dataset" kicker="At a glance">
          <div className="stats-grid">
            <div className="stat-card">
              <span className="label">Rows</span>
              <strong>{dataset.rows}</strong>
            </div>
            <div className="stat-card">
              <span className="label">Columns</span>
              <strong>{dataset.columns}</strong>
            </div>
            <div className="stat-card">
              <span className="label">Duplicate rows</span>
              <strong>{dataset.duplicates}</strong>
            </div>
            <div className="stat-card">
              <span className="label">Memory</span>
              <strong>{dataset.memory}</strong>
            </div>
          </div>

          <div className="column-block">
            <span className="label">Missing values</span>
            {dataset.missingColumns.length ? (
              <ul className="plain-list compact">
                {dataset.missingColumns.map((item) => (
                  <li key={item.column}>
                    <strong>{item.column}</strong>
                    <span>{item.count.toLocaleString()} missing</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No missing values.</p>
            )}
          </div>

          <div className="split-columns">
            <div>
              <span className="label">Numeric columns</span>
              <ChipList items={dataset.numerical} />
            </div>
            <div>
              <span className="label">Other columns</span>
              <ChipList items={dataset.categorical} />
            </div>
          </div>
        </Section>
      ) : null}

      {charts.length ? (
        <Section title="Charts" kicker="Saved by the plotting tool">
          <div className="charts-grid">
            {charts.map((chart) => (
              <figure key={chart.src} className="chart-card">
                <img src={chart.src} alt={chart.title} />
                <figcaption>{chart.title}</figcaption>
              </figure>
            ))}
          </div>
        </Section>
      ) : null}

      {models.length ? (
        <Section title="Models" kicker="Held-out test metrics">
          {bestModel ? (
            <p className="lead">{bestModel.name} was selected as the best model.</p>
          ) : null}
          <div className="model-grid">
            {models.map((model) => (
              <article key={model.key} className={model.best ? "model-card is-best" : "model-card"}>
                <header>
                  <h3>{model.name}</h3>
                  {model.best ? <span className="best-badge">Best</span> : null}
                </header>
                <dl className="metric-list">
                  {model.metrics.map((metric) => (
                    <div key={metric.label}>
                      <dt>{metric.label}</dt>
                      <dd>{metric.value}</dd>
                    </div>
                  ))}
                </dl>
              </article>
            ))}
          </div>
        </Section>
      ) : null}

      {patterns.length ? (
        <Section title="Patterns" kicker="Computed from the file">
          {patterns.map((block) => <PatternBlock key={block.title} block={block} />)}
        </Section>
      ) : null}

      {(preparation.length || features.length) ? (
        <Section title="Data preparation" kicker="Changes applied before modeling">
          {preparation.length ? (
            <div>
              <span className="label">Cleaning</span>
              <ul>
                {preparation.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          ) : null}
          {features.length ? (
            <div className={preparation.length ? "stacked" : ""}>
              <span className="label">New features</span>
              <ul>
                {features.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
          ) : null}
        </Section>
      ) : null}

      {trace.length ? (
        <details className="card trace">
          <summary>How the agent decided</summary>
          <dl className="trace-list">
            {trace.map((item) => (
              <div key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </details>
      ) : null}
    </main>
  );
}
