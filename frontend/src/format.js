const INTENT_LABELS = {
  prediction: "Trained a prediction model",
  eda: "Explored the dataset",
  visualization: "Created charts",
  preprocessing: "Prepared the dataset",
  unknown: "Could not match this request to a dataset task",
};

const PREP_LABELS = {
  convert_numeric: "Converted text numbers into numeric values.",
  remove_duplicates: "Removed duplicate rows.",
  handle_missing_values: "Filled missing values.",
  remove_constant_columns: "Removed columns that contained only one value.",
};

const METRIC_LABELS = {
  accuracy: "Accuracy",
  precision: "Precision",
  recall: "Recall",
  f1: "F1 score",
  mae: "MAE",
  rmse: "RMSE",
  r2: "R²",
};

const CLASSIFICATION_METRICS = new Set(["accuracy", "precision", "recall", "f1"]);

export function prettifyLabel(value) {
  if (value === null || value === undefined || value === "") return "";
  const text = String(value).replace(/_/g, " ").trim();
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export function formatNumber(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  const abs = Math.abs(value);
  if (abs >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
  if (abs >= 10) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
  if (abs >= 1) return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
}

function formatCount(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return Math.round(value).toLocaleString();
}

function formatMetric(key, value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  if (CLASSIFICATION_METRICS.has(key) && Math.abs(value) <= 1) {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (key === "r2") return value.toFixed(3);
  return formatNumber(value);
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function intentLabel(intent) {
  return INTENT_LABELS[intent] || prettifyLabel(intent) || "Analysis finished";
}

export function workflowSteps(results) {
  const steps = [];
  if (results?.profile) steps.push("Profiled the file");
  if (results?.preprocessing_plan?.length) steps.push("Prepared columns");
  if (featureActions(results).length) steps.push("Engineered features");
  if (results?.eda_plan?.length || isRecord(results?.eda_result)) steps.push("Looked for patterns");
  if (isRecord(results?.model_results)) steps.push("Compared models");
  if (results?.chart_paths?.length) steps.push("Drew charts");
  if (results?.insights?.summary) steps.push("Wrote a conclusion");
  return steps;
}

export function featureActions(results) {
  const plan = results?.feature_engineering_plan;
  if (Array.isArray(plan)) return plan.filter(isRecord);
  if (isRecord(plan) && Array.isArray(plan.actions)) return plan.actions.filter(isRecord);
  return [];
}

export function featureSentences(results) {
  return featureActions(results).map((action) => {
    const column = action.column || "a column";
    const second = action.second_column || "another column";
    switch (action.action) {
      case "log_transform":
        return `Log-transformed ${column}.`;
      case "bin_numeric":
        return `Grouped ${column} into bins.`;
      case "combine_rare_categories":
        return `Combined rare categories in ${column}.`;
      case "create_ratio":
        return `Created a ratio of ${column} to ${second}.`;
      case "create_interaction":
        return `Created an interaction between ${column} and ${second}.`;
      default:
        return prettifyLabel(action.action);
    }
  }).filter(Boolean);
}

export function preparationLines(results) {
  const plan = Array.isArray(results?.preprocessing_plan) ? results.preprocessing_plan : [];
  if (!plan.length) return [];

  const summary = Array.isArray(results?.preprocessing_summary) ? results.preprocessing_summary : [];
  const usefulSummary = summary.filter((line) => !isProfilingNote(line));

  if (usefulSummary.length) return usefulSummary;
  return plan.map((action) => PREP_LABELS[action] || prettifyLabel(action));
}

function isProfilingNote(line) {
  const text = String(line);
  return (
    text.startsWith("Dataset contains")
    || text === "No duplicate rows found."
    || text.endsWith("duplicate rows detected.")
    || text === "Missing values detected."
    || text === "No missing values detected."
  );
}

function columnGroups(profile) {
  const dtypes = isRecord(profile?.dtypes) ? profile.dtypes : {};
  const numericTokens = ["int", "float", "uint"];
  const numerical = [];
  const categorical = [];

  Object.entries(dtypes).forEach(([column, type]) => {
    const typeName = String(type).toLowerCase();
    if (numericTokens.some((token) => typeName.includes(token))) numerical.push(column);
    else categorical.push(column);
  });

  return { numerical, categorical };
}

export function datasetSnapshot(profile) {
  if (!isRecord(profile) || profile.rows === undefined) return null;

  const missing = isRecord(profile.missing_values) ? profile.missing_values : {};
  const missingColumns = Object.entries(missing)
    .filter(([, count]) => Number(count) > 0)
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .map(([column, count]) => ({ column, count: Number(count) }));

  const memory = typeof profile.memory_usage_mb === "number"
    ? `${profile.memory_usage_mb.toFixed(2)} MB`
    : "—";

  return {
    rows: formatCount(profile.rows),
    columns: formatCount(profile.columns),
    duplicates: formatCount(profile.duplicates),
    memory,
    ...columnGroups(profile),
    missingColumns,
  };
}

function numericTable(summary) {
  const rows = Object.entries(summary)
    .filter(([, stats]) => isRecord(stats))
    .map(([column, stats]) => ({
      column,
      mean: formatNumber(stats.mean),
      median: formatNumber(stats["50%"]),
      min: formatNumber(stats.min),
      max: formatNumber(stats.max),
    }));

  if (!rows.length) return null;
  return {
    kind: "table",
    title: "Numeric overview",
    columns: ["Column", "Mean", "Median", "Min", "Max"],
    rows,
  };
}

function categoryGroups(summary) {
  const groups = [];
  const skipped = [];

  Object.entries(summary).forEach(([column, counts]) => {
    if (!isRecord(counts)) return;
    const entries = Object.entries(counts).filter(([, count]) => typeof count === "number");
    if (entries.length > 12) {
      skipped.push({ column, count: entries.length });
      return;
    }
    const total = entries.reduce((sum, [, count]) => sum + count, 0) || 1;
    const items = entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([label, count]) => ({
        label: String(label),
        count: formatCount(count),
        share: Math.round((count / total) * 100),
      }));
    groups.push({ name: column, items, hidden: Math.max(entries.length - items.length, 0) });
  });

  if (!groups.length && !skipped.length) return null;
  return { kind: "categories", title: "Category breakdown", groups, skipped };
}

function correlationRows(matrix) {
  const seen = new Set();
  const pairs = [];

  Object.entries(matrix).forEach(([left, row]) => {
    if (!isRecord(row)) return;
    Object.entries(row).forEach(([right, value]) => {
      if (left === right || typeof value !== "number" || Number.isNaN(value)) return;
      const key = [left, right].sort().join("|");
      if (seen.has(key)) return;
      seen.add(key);
      pairs.push({ left, right, value });
    });
  });

  pairs.sort((a, b) => Math.abs(b.value) - Math.abs(a.value));
  const top = pairs.slice(0, 6).map((pair) => ({
    label: `${pair.left} and ${pair.right}`,
    value: pair.value.toFixed(2),
    share: Math.round(Math.abs(pair.value) * 100),
  }));

  if (!top.length) return null;
  return { kind: "bars", title: "Strongest correlations", rows: top };
}

function outlierRows(outliers) {
  const rows = Object.entries(outliers)
    .filter(([, count]) => Number(count) > 0)
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .slice(0, 8)
    .map(([column, count]) => ({
      label: column,
      value: `${formatCount(Number(count))} rows`,
    }));

  return {
    kind: "list",
    title: "Outliers",
    empty: rows.length ? "" : "No numeric column has values outside the usual 1.5 IQR range.",
    rows,
  };
}

function targetBlock(target) {
  const distribution = isRecord(target?.distribution) ? target.distribution : target;
  if (!isRecord(distribution)) return null;

  const entries = Object.entries(distribution).filter(([, count]) => typeof count === "number");
  if (!entries.length) return null;
  const total = entries.reduce((sum, [, count]) => sum + count, 0) || 1;
  const rows = entries
    .sort((a, b) => b[1] - a[1])
    .map(([label, count]) => ({
      label: String(label),
      value: formatCount(count),
      share: Math.round((count / total) * 100),
      showShare: true,
    }));

  return { kind: "bars", title: "Target balance", rows };
}

function relationshipRows(relationships) {
  const ranked = Object.entries(relationships)
    .filter(([, groups]) => isRecord(groups))
    .map(([feature, groups]) => {
      const entries = Object.entries(groups).filter(([, value]) => typeof value === "number");
      const values = entries.map(([, value]) => value);
      const spread = values.length > 1 ? Math.max(...values) - Math.min(...values) : 0;
      return { feature, entries, spread };
    })
    .sort((a, b) => b.spread - a.spread)
    .slice(0, 6);

  const rows = ranked.map(({ feature, entries }) => {
    const shown = [...entries].sort((a, b) => b[1] - a[1]).slice(0, 4);
    const detail = shown.map(([label, value]) => `${label}: ${formatNumber(value)}`).join(" · ");
    return { label: feature, value: detail };
  });

  if (!rows.length) return null;
  return {
    kind: "list",
    title: "How features differ by outcome",
    note: "Numbers are group averages, or the share of the positive class for categories.",
    rows,
  };
}

export function patternBlocks(results) {
  const result = results?.eda_result;
  if (!isRecord(result)) return [];

  const blocks = [
    result.target_analysis ? targetBlock(result.target_analysis) : null,
    result.correlation_analysis ? correlationRows(result.correlation_analysis) : null,
    result.outlier_detection ? outlierRows(result.outlier_detection) : null,
    result.feature_target_relationship ? relationshipRows(result.feature_target_relationship) : null,
    result.numerical_summary ? numericTable(result.numerical_summary) : null,
    result.categorical_summary ? categoryGroups(result.categorical_summary) : null,
  ].filter(Boolean);

  return blocks;
}

export function modelCards(results) {
  if (!isRecord(results?.model_results)) return [];
  const best = results.best_model;

  return Object.entries(results.model_results)
    .map(([name, info]) => {
      const metrics = isRecord(info?.metrics) ? info.metrics : {};
      return {
        name: prettifyLabel(name),
        key: name,
        best: name === best,
        metrics: Object.entries(metrics).map(([key, value]) => ({
          label: METRIC_LABELS[key] || prettifyLabel(key),
          value: formatMetric(key, value),
        })),
      };
    })
    .sort((a, b) => Number(b.best) - Number(a.best));
}

export function chartCards(results, apiBaseUrl) {
  return (results?.chart_paths || []).map((path) => {
    const fileName = String(path).split("/").pop() || "chart";
    const stem = fileName.replace(/\.[a-z0-9]+$/i, "");
    let title = prettifyLabel(stem);
    if (stem === "target_distribution") title = "Target distribution";
    else if (stem === "correlation_heatmap") title = "Correlation heatmap";
    else if (stem.endsWith("_vs_target")) title = `${prettifyLabel(stem.replace(/_vs_target$/, ""))} and the target`;
    else if (stem.endsWith("_distribution")) title = `Distribution of ${prettifyLabel(stem.replace(/_distribution$/, ""))}`;

    return {
      src: `${apiBaseUrl}${path}`,
      title,
    };
  });
}

export function decisionTrace(results) {
  const items = [];
  if (results?.intent) items.push({ label: "Intent", value: intentLabel(results.intent) });
  if (results?.target_column) items.push({ label: "Target column", value: results.target_column });

  const plans = [
    ["Preparation steps", results?.preprocessing_plan],
    ["Exploration steps", results?.eda_plan],
  ];

  plans.forEach(([label, plan]) => {
    if (Array.isArray(plan) && plan.length) {
      items.push({ label, value: plan.map((item) => prettifyLabel(item)).join(", ") });
    }
  });

  const features = featureActions(results).map((action) => prettifyLabel(action.action)).filter(Boolean);
  if (features.length) items.push({ label: "Feature steps", value: features.join(", ") });

  const charts = Array.isArray(results?.visualization_plan)
    ? results.visualization_plan
        .map((chart) => {
          if (!isRecord(chart)) return "";
          const name = prettifyLabel(chart.chart_type);
          return chart.column ? `${name} (${chart.column})` : name;
        })
        .filter(Boolean)
    : [];
  if (charts.length) items.push({ label: "Charts requested", value: charts.join(", ") });

  return items;
}

export function conclusionFallback(results) {
  if (results?.intent === "unknown" || !results?.intent) {
    return "This request did not match a task the analyst can run on the file. Ask it to explore the dataset, create charts, clean the data, or train a model.";
  }
  return "The run finished without a written conclusion. The sections below show the measurements the tools actually produced.";
}
