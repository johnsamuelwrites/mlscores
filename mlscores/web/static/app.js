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

    // Endpoint configurations for different Wikibase instances
    const ENDPOINT_CONFIGS = {
        wikidata: {
            name: 'Wikidata',
            entityBaseUrl: 'https://www.wikidata.org/wiki/',
            propertyPrefix: 'http://www.wikidata.org/prop/direct/',
            entityPrefix: 'http://www.wikidata.org/entity/',
            sparqlEndpoint: 'https://query.wikidata.org/sparql'
        },
        commons: {
            name: 'Wikimedia Commons',
            entityBaseUrl: 'https://commons.wikimedia.org/wiki/',
            propertyPrefix: 'http://www.wikidata.org/prop/direct/',
            entityPrefix: 'http://commons.wikimedia.org/entity/',
            sparqlEndpoint: 'https://wcqs-beta.wmflabs.org/sparql'
        },
        custom: {
            name: 'Custom',
            entityBaseUrl: null,  // Will be set based on user input
            propertyPrefix: 'http://www.wikidata.org/prop/direct/',
            entityPrefix: 'http://www.wikidata.org/entity/',
            sparqlEndpoint: null
        }
    };

    // Current active endpoint configuration
    let currentEndpoint = ENDPOINT_CONFIGS.wikidata;

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

    // Endpoint selection handling
    const endpointSelect = document.getElementById('endpoint');
    const customEndpointGroup = document.getElementById('custom-endpoint-group');
    const customEndpointUrl = document.getElementById('custom-endpoint-url');

    endpointSelect?.addEventListener('change', function() {
        const selectedEndpoint = this.value;

        if (selectedEndpoint === 'custom') {
            customEndpointGroup?.classList.remove('hidden');
        } else {
            customEndpointGroup?.classList.add('hidden');
            currentEndpoint = ENDPOINT_CONFIGS[selectedEndpoint] || ENDPOINT_CONFIGS.wikidata;
        }
    });

    customEndpointUrl?.addEventListener('change', function() {
        if (this.value) {
            // For custom endpoints, try to derive entity URL from SPARQL endpoint
            const sparqlUrl = this.value;
            currentEndpoint = {
                ...ENDPOINT_CONFIGS.custom,
                sparqlEndpoint: sparqlUrl,
                entityBaseUrl: deriveEntityUrlFromSparql(sparqlUrl)
            };
        }
    });

    function deriveEntityUrlFromSparql(sparqlUrl) {
        // Try to derive a reasonable entity URL from SPARQL endpoint
        // Common patterns:
        // https://query.wikidata.org/sparql -> https://www.wikidata.org/wiki/
        // https://example.org/sparql -> https://example.org/entity/

        try {
            const url = new URL(sparqlUrl);
            // If it looks like Wikidata, use Wikidata pattern
            if (url.hostname.includes('wikidata')) {
                return 'https://www.wikidata.org/wiki/';
            }
            if (url.hostname.includes('commons.wikimedia')) {
                return 'https://commons.wikimedia.org/wiki/';
            }
            // For other endpoints, construct a basic entity URL
            return `${url.protocol}//${url.hostname}/entity/`;
        } catch {
            return null;
        }
    }

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
        const endpointValue = document.getElementById('endpoint')?.value || 'wikidata';
        const customEndpointUrlValue = document.getElementById('custom-endpoint-url')?.value;

        // Update current endpoint based on selection
        if (endpointValue === 'custom' && customEndpointUrlValue) {
            currentEndpoint = {
                ...ENDPOINT_CONFIGS.custom,
                sparqlEndpoint: customEndpointUrlValue,
                entityBaseUrl: deriveEntityUrlFromSparql(customEndpointUrlValue)
            };
        } else {
            currentEndpoint = ENDPOINT_CONFIGS[endpointValue] || ENDPOINT_CONFIGS.wikidata;
        }

        // Parse inputs
        const identifiers = identifiersInput
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0);

        const languages = languagesInput
            ? languagesInput.split(',').map(s => s.trim()).filter(s => s.length > 0)
            : null;

        if (identifiers.length === 0) {
            showError('Please enter at least one item ID');
            return;
        }

        // Show loading, hide results/error
        showLoading();

        // Build request body
        const requestBody = {
            identifiers: identifiers,
            languages: languages,
            include_missing: includeMissing
        };

        // Add endpoint URL if custom
        if (endpointValue === 'custom' && customEndpointUrlValue) {
            requestBody.endpoint_url = customEndpointUrlValue;
        } else if (endpointValue !== 'wikidata') {
            requestBody.endpoint = endpointValue;
        }

        try {
            const response = await fetch('/api/scores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
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

            let html = `<h3>Item: ${createItemLink(item.item_id)}</h3>`;

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
            // Shorten URIs for display and create clickable links
            const itemLinks = items.map(uri => {
                const shortId = uri
                    .replace(currentEndpoint.propertyPrefix, '')
                    .replace(currentEndpoint.entityPrefix, '');
                return createMissingItemLink(shortId);
            });

            html += `
                <tr>
                    <td>
                        <span class="lang-code">${escapeHtml(lang.toUpperCase())}</span>
                    </td>
                    <td>
                        <div class="missing-items">
                            ${itemLinks.join('')}
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

    function createWikidataUrl(identifier) {
        // Handle both Q-items and P-properties
        // identifier can be like "Q42", "P31", or full URIs
        let id = identifier;

        // If it's a full URI, extract just the ID
        if (identifier.startsWith('http')) {
            id = identifier
                .replace(currentEndpoint.propertyPrefix, '')
                .replace(currentEndpoint.entityPrefix, '');
        }

        // If no entity base URL is configured, return null (no link)
        if (!currentEndpoint.entityBaseUrl) {
            return null;
        }

        // Properties go to Property: namespace, items go directly
        // This works for Wikidata-style instances
        if (id.startsWith('P')) {
            return `${currentEndpoint.entityBaseUrl}Property:${id}`;
        }
        // For Commons, items start with M
        if (id.startsWith('M') && currentEndpoint.name === 'Wikimedia Commons') {
            return `${currentEndpoint.entityBaseUrl}File:${id}`;
        }
        return `${currentEndpoint.entityBaseUrl}${id}`;
    }

    function createItemLink(identifier) {
        const url = createWikidataUrl(identifier);
        if (url) {
            return `<a href="${url}" target="_blank" rel="noopener" class="item-link">${escapeHtml(identifier)}</a>`;
        }
        return escapeHtml(identifier);
    }

    function createMissingItemLink(identifier) {
        const url = createWikidataUrl(identifier);
        if (url) {
            return `<a href="${url}" target="_blank" rel="noopener" class="missing-item">${escapeHtml(identifier)}</a>`;
        }
        return `<span class="missing-item">${escapeHtml(identifier)}</span>`;
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
