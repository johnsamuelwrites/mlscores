/**
 * mlscores Web Interface JavaScript
 * Modern, futuristic UI interactions with theme support
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('score-form');
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const resultsContent = document.getElementById('results-content');
    const error = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const retryBtn = document.getElementById('retry-btn');
    const exportJsonBtn = document.getElementById('export-json');
    const themeToggle = document.getElementById('theme-toggle');

    let lastResultsData = null;

    // Theme Management
    function getPreferredTheme() {
        const savedTheme = localStorage.getItem('mlscores-theme');
        if (savedTheme) {
            return savedTheme;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('mlscores-theme', theme);
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }

    // Initialize theme
    setTheme(getPreferredTheme());

    // Theme toggle button
    themeToggle?.addEventListener('click', toggleTheme);

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('mlscores-theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await calculateScores();
    });

    retryBtn?.addEventListener('click', async function() {
        await calculateScores();
    });

    exportJsonBtn?.addEventListener('click', function() {
        if (lastResultsData) {
            exportAsJson(lastResultsData);
        }
    });

    async function calculateScores() {
        // Get form values
        const identifiersInput = document.getElementById('identifiers').value;
        const languagesInput = document.getElementById('languages').value;
        const includeMissing = document.getElementById('include-missing').checked;

        // Parse inputs
        const identifiers = identifiersInput
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0);

        const languages = languagesInput
            ? languagesInput.split(',').map(s => s.trim()).filter(s => s.length > 0)
            : null;

        if (identifiers.length === 0) {
            showError('Please enter at least one Wikidata item ID');
            return;
        }

        // Show loading, hide results/error
        showLoading();

        try {
            const response = await fetch('/api/scores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    identifiers: identifiers,
                    languages: languages,
                    include_missing: includeMissing
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to calculate scores');
            }

            const data = await response.json();
            lastResultsData = data.results;
            displayResults(data.results);

        } catch (err) {
            showError(err.message);
        }
    }

    function showLoading() {
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        error.classList.add('hidden');
        submitBtn.disabled = true;
    }

    function hideLoading() {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }

    function showError(message) {
        hideLoading();
        error.classList.remove('hidden');
        results.classList.add('hidden');
        errorMessage.textContent = message;
    }

    function displayResults(data) {
        hideLoading();
        results.classList.remove('hidden');
        error.classList.add('hidden');

        resultsContent.innerHTML = '';

        data.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'item-result';
            itemDiv.style.animationDelay = `${index * 0.1}s`;

            let html = `<h3>Item: ${escapeHtml(item.item_id)}</h3>`;

            // Property Labels Table
            html += createScoreTable(
                'Property Label Percentages',
                item.property_labels.percentages
            );

            // Value Labels Table
            html += createScoreTable(
                'Value Label Percentages',
                item.value_labels.percentages
            );

            // Combined Table
            html += createScoreTable(
                'Combined Percentages',
                item.combined.percentages
            );

            // Missing Translations
            if (item.missing_property_translations) {
                html += createMissingTable(
                    'Missing Property Translations',
                    item.missing_property_translations.by_language
                );
            }

            if (item.missing_value_translations) {
                html += createMissingTable(
                    'Missing Value Translations',
                    item.missing_value_translations.by_language
                );
            }

            itemDiv.innerHTML = html;
            resultsContent.appendChild(itemDiv);
        });
    }

    function createScoreTable(title, percentages) {
        const entries = Object.entries(percentages);
        if (entries.length === 0) {
            return `<p class="no-data"><strong>${escapeHtml(title)}:</strong> No data available</p>`;
        }

        let html = `
            <table class="score-table">
                <caption>${escapeHtml(title)}</caption>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
        `;

        entries
            .sort((a, b) => b[1] - a[1])  // Sort by percentage descending
            .forEach(([lang, pct]) => {
                const colorClass = getScoreColorClass(pct);
                html += `
                    <tr>
                        <td>
                            <span class="lang-code">${escapeHtml(lang.toUpperCase())}</span>
                        </td>
                        <td>
                            <div class="progress-cell">
                                <div class="progress-bar">
                                    <div class="progress-fill ${colorClass}" style="width: ${pct}%"></div>
                                </div>
                                <span class="progress-value">${pct.toFixed(2)}%</span>
                            </div>
                        </td>
                    </tr>
                `;
            });

        html += '</tbody></table>';
        return html;
    }

    function getScoreColorClass(percentage) {
        if (percentage >= 90) return 'score-excellent';
        if (percentage >= 70) return 'score-good';
        if (percentage >= 50) return 'score-fair';
        return 'score-low';
    }

    function createMissingTable(title, byLanguage) {
        const entries = Object.entries(byLanguage);
        if (entries.length === 0) {
            return '';  // No missing translations
        }

        let html = `
            <table class="score-table missing-table">
                <caption>${escapeHtml(title)}</caption>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Missing Items</th>
                    </tr>
                </thead>
                <tbody>
        `;

        entries.forEach(([lang, items]) => {
            // Shorten URIs for display
            const shortItems = items.map(uri => {
                return uri
                    .replace('http://www.wikidata.org/prop/direct/', '')
                    .replace('http://www.wikidata.org/entity/', '');
            });

            html += `
                <tr>
                    <td>
                        <span class="lang-code">${escapeHtml(lang.toUpperCase())}</span>
                    </td>
                    <td>
                        <div class="missing-items">
                            ${shortItems.map(item => `<span class="missing-item">${escapeHtml(item)}</span>`).join('')}
                        </div>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        return html;
    }

    function exportAsJson(data) {
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `mlscores-results-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Add visual feedback for input focus
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (!submitBtn.disabled) {
                form.dispatchEvent(new Event('submit'));
            }
        }
        // Ctrl/Cmd + Shift + L to toggle theme
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
            e.preventDefault();
            toggleTheme();
        }
    });
});
