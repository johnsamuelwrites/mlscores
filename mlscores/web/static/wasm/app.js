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

let suggestions = [];
let activeSuggestionIndex = -1;
let suggestionDebounceTimer = null;
let suggestionRequestId = 0;

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

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function isLikelyIdentifier(token) {
  return /^[QPM]\\d+$/i.test(token.trim());
}

function getCurrentToken(value, caretPos) {
  const before = value.slice(0, caretPos);
  const tokenStart = before.lastIndexOf(",") + 1;
  const after = value.slice(caretPos);
  const nextComma = after.indexOf(",");
  const tokenEnd = nextComma === -1 ? value.length : caretPos + nextComma;

  const rawToken = value.slice(tokenStart, tokenEnd);
  const leadingWhitespace = (rawToken.match(/^\\s*/) || [""])[0];
  const trailingWhitespace = (rawToken.match(/\\s*$/) || [""])[0];

  return {
    token: rawToken.trim(),
    start: tokenStart + leadingWhitespace.length,
    end: tokenEnd - trailingWhitespace.length,
  };
}

function hideSuggestions() {
  suggestions = [];
  activeSuggestionIndex = -1;
  if (!suggestionsList) {
    return;
  }
  suggestionsList.innerHTML = "";
  suggestionsList.classList.add("hidden");
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

function setActiveSuggestion(index) {
  if (!suggestionsList) {
    return;
  }
  const buttons = suggestionsList.querySelectorAll(".suggestion-item");
  buttons.forEach((button) => button.classList.remove("active"));
  if (index >= 0 && index < buttons.length) {
    activeSuggestionIndex = index;
    buttons[index].classList.add("active");
  }
}

function selectSuggestion(index) {
  if (!identifiersInput || index < 0 || index >= suggestions.length) {
    return;
  }
  const currentValue = identifiersInput.value;
  const caretPos = identifiersInput.selectionStart ?? currentValue.length;
  const tokenInfo = getCurrentToken(currentValue, caretPos);
  const selectedId = suggestions[index].id;
  let updatedValue =
    currentValue.slice(0, tokenInfo.start) +
    selectedId +
    currentValue.slice(tokenInfo.end);

  const insertionPoint = tokenInfo.start + selectedId.length;
  if (tokenInfo.end === currentValue.length) {
    updatedValue = `${updatedValue.trimEnd()}, `;
    identifiersInput.value = updatedValue;
    identifiersInput.focus();
    identifiersInput.setSelectionRange(updatedValue.length, updatedValue.length);
  } else {
    identifiersInput.value = updatedValue;
    identifiersInput.focus();
    identifiersInput.setSelectionRange(insertionPoint, insertionPoint);
  }
  hideSuggestions();
}

function renderSuggestions(items) {
  if (!suggestionsList || !items.length) {
    hideSuggestions();
    return;
  }

  suggestions = items;
  activeSuggestionIndex = -1;
  suggestionsList.innerHTML = "";

  items.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion-item";
    button.setAttribute("role", "option");
    button.innerHTML = `
      <div class="suggestion-main">
        <span class="suggestion-id">${escapeHtml(item.id)}</span>
        <span class="suggestion-label">${escapeHtml(item.label || item.id)}</span>
      </div>
      ${item.description ? `<div class="suggestion-description">${escapeHtml(item.description)}</div>` : ""}
    `;
    button.addEventListener("click", () => selectSuggestion(index));
    suggestionsList.appendChild(button);
  });

  suggestionsList.classList.remove("hidden");
}

async function fetchIdentifierSuggestions(queryText) {
  const apiUrl = inferEntitySearchApi(endpointInput?.value || "");
  if (!apiUrl) {
    hideSuggestions();
    return;
  }

  const requestId = ++suggestionRequestId;
  const params = new URLSearchParams({
    action: "wbsearchentities",
    search: queryText,
    language: "en",
    limit: "8",
    format: "json",
    origin: "*",
  });

  try {
    const response = await fetch(`${apiUrl}?${params.toString()}`);
    if (!response.ok) {
      hideSuggestions();
      return;
    }

    const payload = await response.json();
    if (requestId !== suggestionRequestId) {
      return;
    }

    const items = (payload.search || [])
      .filter((item) => item.id)
      .map((item) => ({
        id: item.id,
        label: item.label || item.id,
        description: item.description || "",
      }));
    renderSuggestions(items);
  } catch {
    hideSuggestions();
  }
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

identifiersInput?.addEventListener("input", function onInput() {
  const value = this.value;
  const caretPos = this.selectionStart ?? value.length;
  const tokenInfo = getCurrentToken(value, caretPos);

  if (suggestionDebounceTimer) {
    clearTimeout(suggestionDebounceTimer);
  }

  if (tokenInfo.token.length < 2 || isLikelyIdentifier(tokenInfo.token)) {
    hideSuggestions();
    return;
  }

  suggestionDebounceTimer = setTimeout(() => {
    fetchIdentifierSuggestions(tokenInfo.token);
  }, 220);
});

identifiersInput?.addEventListener("keydown", function onKeyDown(event) {
  if (!suggestions.length || suggestionsList?.classList.contains("hidden")) {
    return;
  }

  if (event.key === "ArrowDown") {
    event.preventDefault();
    const nextIndex =
      activeSuggestionIndex + 1 >= suggestions.length ? 0 : activeSuggestionIndex + 1;
    setActiveSuggestion(nextIndex);
    return;
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    const previousIndex =
      activeSuggestionIndex - 1 < 0 ? suggestions.length - 1 : activeSuggestionIndex - 1;
    setActiveSuggestion(previousIndex);
    return;
  }

  if (event.key === "Enter" || event.key === "Tab") {
    if (activeSuggestionIndex >= 0) {
      event.preventDefault();
      selectSuggestion(activeSuggestionIndex);
    }
    return;
  }

  if (event.key === "Escape") {
    hideSuggestions();
  }
});

document.addEventListener("click", (event) => {
  if (!suggestionsList || !identifiersInput) {
    return;
  }
  const insideSuggestions = suggestionsList.contains(event.target);
  const insideInput = identifiersInput.contains(event.target);
  if (!insideSuggestions && !insideInput) {
    hideSuggestions();
  }
});

endpointInput?.addEventListener("change", hideSuggestions);

initPyodideRuntime().catch((error) => {
  setStatus("Initialization failed.");
  showError(error?.message || String(error));
});
