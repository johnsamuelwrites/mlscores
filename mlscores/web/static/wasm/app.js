const state = {
  pyodide: null,
  ready: false,
};

const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const resultsEl = document.getElementById("results");
const form = document.getElementById("score-form");
const submitBtn = document.getElementById("submit-btn");
const identifiersInput = document.getElementById("identifiers");
const endpointInput = document.getElementById("endpoint");
const suggestionsList = document.getElementById("identifier-suggestions");

function setStatus(text) {
  statusEl.textContent = text;
}

function showError(message) {
  errorEl.classList.remove("hidden");
  errorEl.textContent = message;
}

function clearError() {
  errorEl.classList.add("hidden");
  errorEl.textContent = "";
}

function parseCsvInput(value) {
  return value
    .split(",")
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
}

function inferEntitySearchApi(endpointUrl) {
  const value = (endpointUrl || "").toLowerCase();
  if (value.includes("wikidata")) {
    return "https://www.wikidata.org/w/api.php";
  }
  if (value.includes("commons.wikimedia") || value.includes("wcqs-beta.wmflabs.org")) {
    return "https://commons.wikimedia.org/w/api.php";
  }
  return null;
}

function renderPercentagesTable(title, percentages) {
  const entries = Object.entries(percentages);
  if (!entries.length) {
    return `<h4>${title}</h4><p>No data</p>`;
  }

  entries.sort((a, b) => b[1] - a[1]);
  const rows = entries
    .map(([lang, pct]) => `<tr><td>${lang.toUpperCase()}</td><td>${pct.toFixed(2)}%</td></tr>`)
    .join("");

  return `
    <h4>${title}</h4>
    <table class="results-table">
      <thead><tr><th>Language</th><th>Score</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderMissingTable(title, byLanguage) {
  const entries = Object.entries(byLanguage || {});
  if (!entries.length) {
    return "";
  }

  const rows = entries
    .map(([lang, uris]) => `<tr><td>${lang.toUpperCase()}</td><td>${uris.join(", ")}</td></tr>`)
    .join("");

  return `
    <h4>${title}</h4>
    <table class="results-table">
      <thead><tr><th>Language</th><th>Missing URIs</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderResults(results) {
  if (!results.length) {
    resultsEl.innerHTML = "<p>No results.</p>";
    resultsEl.classList.remove("hidden");
    return;
  }

  const html = results
    .map((item) => {
      return `
        <article>
          <h3>${item.item_id}</h3>
          ${renderPercentagesTable("Property labels", item.property_labels.percentages)}
          ${renderPercentagesTable("Value labels", item.value_labels.percentages)}
          ${renderPercentagesTable("Combined", item.combined.percentages)}
          ${renderMissingTable("Missing property translations", item.missing_property_translations?.by_language)}
          ${renderMissingTable("Missing value translations", item.missing_value_translations?.by_language)}
        </article>
      `;
    })
    .join("<hr>");

  resultsEl.innerHTML = html;
  resultsEl.classList.remove("hidden");
}

async function initPyodideRuntime() {
  setStatus("Initializing Pyodide runtime...");
  state.pyodide = await loadPyodide();

  setStatus("Loading shared query builders...");
  const buildersResponse = await fetch("./query_builders.py");
  if (!buildersResponse.ok) {
    throw new Error("Failed to load query_builders.py");
  }
  const buildersCode = await buildersResponse.text();
  state.pyodide.globals.set("query_builders_code", buildersCode);
  await state.pyodide.runPythonAsync(`
import sys
import types
_mod = types.ModuleType("query_builders")
exec(query_builders_code, _mod.__dict__)
sys.modules["query_builders"] = _mod
`);

  setStatus("Loading mlscores WASM module...");
  const response = await fetch("./mlscores_wasm.py");
  if (!response.ok) {
    throw new Error("Failed to load mlscores_wasm.py");
  }

  const pythonCode = await response.text();
  await state.pyodide.runPythonAsync(pythonCode);
  state.ready = true;
  setStatus("Pyodide ready. You can run calculations.");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();
  resultsEl.classList.add("hidden");

  if (!state.ready) {
    showError("Pyodide is still loading. Please try again.");
    return;
  }

  const identifiers = parseCsvInput(document.getElementById("identifiers").value);
  const languages = parseCsvInput(document.getElementById("languages").value);
  const endpoint = document.getElementById("endpoint").value.trim();
  const includeMissing = document.getElementById("include-missing").checked;

  if (!identifiers.length) {
    showError("Please enter at least one item ID.");
    return;
  }

  submitBtn.disabled = true;
  setStatus("Running SPARQL queries in-browser...");

  try {
    const payload = {
      identifiers,
      languages,
      include_missing: includeMissing,
      endpoint,
    };

    state.pyodide.globals.set("mlscores_payload", JSON.stringify(payload));
    const output = await state.pyodide.runPythonAsync(
      "await calculate_scores_json(mlscores_payload)"
    );
    const parsed = JSON.parse(output);
    renderResults(parsed.results || []);
    setStatus("Completed.");
  } catch (error) {
    showError(error?.message || String(error));
    setStatus("Failed.");
  } finally {
    submitBtn.disabled = false;
  }
});

const identifierAutocomplete = window.MlscoresEntitySuggest?.attachAutocomplete({
  inputEl: identifiersInput,
  suggestionsEl: suggestionsList,
  shouldSuggest: () => Boolean(inferEntitySearchApi(endpointInput?.value || "")),
  fetchSuggestions: async (queryText) => {
    const apiUrl = inferEntitySearchApi(endpointInput?.value || "");
    if (!apiUrl) {
      return [];
    }

    const params = new URLSearchParams({
      action: "wbsearchentities",
      search: queryText,
      language: "en",
      limit: "8",
      format: "json",
      origin: "*",
    });
    const response = await fetch(`${apiUrl}?${params.toString()}`);
    if (!response.ok) {
      return [];
    }

    const payload = await response.json();
    return (payload.search || [])
      .filter((item) => item.id)
      .map((item) => ({
        id: item.id,
        label: item.label || item.id,
        description: item.description || "",
      }));
  },
});

endpointInput?.addEventListener("change", () => identifierAutocomplete?.hide());

initPyodideRuntime().catch((error) => {
  setStatus("Initialization failed.");
  showError(error?.message || String(error));
});
