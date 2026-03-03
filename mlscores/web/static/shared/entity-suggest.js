/*
 * Shared entity suggestion/autocomplete for comma-separated ID inputs.
 */
(function () {
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function isLikelyIdentifier(token) {
    return /^[QPM]\d+$/i.test((token || "").trim());
  }

  function getCurrentToken(value, caretPos) {
    const before = value.slice(0, caretPos);
    const tokenStart = before.lastIndexOf(",") + 1;
    const after = value.slice(caretPos);
    const nextComma = after.indexOf(",");
    const tokenEnd = nextComma === -1 ? value.length : caretPos + nextComma;

    const rawToken = value.slice(tokenStart, tokenEnd);
    const leadingWhitespace = (rawToken.match(/^\s*/) || [""])[0];
    const trailingWhitespace = (rawToken.match(/\s*$/) || [""])[0];

    return {
      token: rawToken.trim(),
      start: tokenStart + leadingWhitespace.length,
      end: tokenEnd - trailingWhitespace.length,
    };
  }

  function attachAutocomplete(config) {
    const inputEl = config?.inputEl;
    const suggestionsEl = config?.suggestionsEl;
    const fetchSuggestions = config?.fetchSuggestions;
    const shouldSuggest = config?.shouldSuggest || (() => true);
    const minTokenLength = config?.minTokenLength ?? 2;
    const debounceMs = config?.debounceMs ?? 220;

    if (!inputEl || !suggestionsEl || typeof fetchSuggestions !== "function") {
      return { hide: () => {} };
    }

    let suggestions = [];
    let activeIndex = -1;
    let requestId = 0;
    let debounceTimer = null;

    function hide() {
      suggestions = [];
      activeIndex = -1;
      suggestionsEl.innerHTML = "";
      suggestionsEl.classList.add("hidden");
    }

    function render(items) {
      if (!items.length) {
        hide();
        return;
      }

      suggestions = items;
      activeIndex = -1;
      suggestionsEl.innerHTML = "";

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
        button.addEventListener("click", () => select(index));
        suggestionsEl.appendChild(button);
      });

      suggestionsEl.classList.remove("hidden");
    }

    function setActive(index) {
      const buttons = suggestionsEl.querySelectorAll(".suggestion-item");
      buttons.forEach((button) => button.classList.remove("active"));
      if (index >= 0 && index < buttons.length) {
        activeIndex = index;
        buttons[index].classList.add("active");
      }
    }

    function select(index) {
      if (index < 0 || index >= suggestions.length) {
        return;
      }

      const currentValue = inputEl.value;
      const caretPos = inputEl.selectionStart ?? currentValue.length;
      const tokenInfo = getCurrentToken(currentValue, caretPos);
      const selectedId = suggestions[index].id;
      let updatedValue =
        currentValue.slice(0, tokenInfo.start) +
        selectedId +
        currentValue.slice(tokenInfo.end);

      const insertionPoint = tokenInfo.start + selectedId.length;
      if (tokenInfo.end === currentValue.length) {
        updatedValue = `${updatedValue.trimEnd()}, `;
        inputEl.value = updatedValue;
        inputEl.focus();
        inputEl.setSelectionRange(updatedValue.length, updatedValue.length);
      } else {
        inputEl.value = updatedValue;
        inputEl.focus();
        inputEl.setSelectionRange(insertionPoint, insertionPoint);
      }

      hide();
    }

    inputEl.addEventListener("input", function onInput() {
      const value = inputEl.value;
      const caretPos = inputEl.selectionStart ?? value.length;
      const tokenInfo = getCurrentToken(value, caretPos);

      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      if (
        tokenInfo.token.length < minTokenLength ||
        isLikelyIdentifier(tokenInfo.token) ||
        !shouldSuggest(tokenInfo.token)
      ) {
        hide();
        return;
      }

      debounceTimer = setTimeout(async () => {
        const currentRequestId = ++requestId;
        try {
          const items = (await fetchSuggestions(tokenInfo.token)) || [];
          if (currentRequestId !== requestId) {
            return;
          }
          render(items);
        } catch {
          hide();
        }
      }, debounceMs);
    });

    inputEl.addEventListener("keydown", function onKeyDown(event) {
      if (!suggestions.length || suggestionsEl.classList.contains("hidden")) {
        return;
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();
        const nextIndex = activeIndex + 1 >= suggestions.length ? 0 : activeIndex + 1;
        setActive(nextIndex);
        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        const previousIndex = activeIndex - 1 < 0 ? suggestions.length - 1 : activeIndex - 1;
        setActive(previousIndex);
        return;
      }

      if (event.key === "Enter" || event.key === "Tab") {
        if (activeIndex >= 0) {
          event.preventDefault();
          select(activeIndex);
        }
        return;
      }

      if (event.key === "Escape") {
        hide();
      }
    });

    document.addEventListener("click", (event) => {
      const insideSuggestions = suggestionsEl.contains(event.target);
      const insideInput = inputEl.contains(event.target);
      if (!insideSuggestions && !insideInput) {
        hide();
      }
    });

    return { hide };
  }

  window.MlscoresEntitySuggest = {
    attachAutocomplete,
  };
})();
