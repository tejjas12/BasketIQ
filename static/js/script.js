
// =====================================================
// BASKET IQ - MAIN JAVASCRIPT
// =====================================================

const form = document.getElementById("recommendForm");
const select = document.getElementById("productSelect");
const results = document.getElementById("results");
const button = document.getElementById("recommendBtn");

let allRules = [];
let filteredRules = [];


// =====================================================
// SECURITY HELPER
// =====================================================

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}


// =====================================================
// AI PRODUCT RECOMMENDATIONS
// =====================================================

if (form) {
    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        const selected = Array.from(select.selectedOptions)
            .map(option => option.value);

        if (!selected.length) {
            results.innerHTML = `
                <div class="empty">
                    Please select at least one product first.
                </div>
            `;
            return;
        }

        button.disabled = true;
        button.textContent = "Analyzing Basket...";

        results.innerHTML = `
            <div class="empty">
                Discovering product relationships...
            </div>
        `;

        try {
            const response = await fetch("/recommend", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({products: selected})
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Request failed");
            }

            if (!data.recommendations.length) {
                results.innerHTML = `
                    <div class="empty">
                        ${escapeHTML(data.message)}
                    </div>
                `;
                return;
            }

            results.innerHTML = data.recommendations.map((item, index) => `
                <div class="recommendation">
                    <div>
                        <div class="product-name">
                            ${index + 1}. ${escapeHTML(item.product)}
                        </div>
                        <div class="product-sub">
                            Confidence: ${item.confidence}% ·
                            Support: ${item.support}
                        </div>
                    </div>
                    <div class="lift-badge">
                        Lift ${item.lift}
                    </div>
                </div>
            `).join("");

        } catch (error) {
            results.innerHTML = `
                <div class="empty">
                    Error: ${escapeHTML(error.message)}
                </div>
            `;
        } finally {
            button.disabled = false;
            button.textContent = "✧ Generate AI Recommendations";
        }
    });
}


// =====================================================
// LOAD ACTUAL ASSOCIATION RULES
// =====================================================

async function loadRules() {
    const tableBody = document.getElementById("rulesTableBody");

    try {
        const response = await fetch("/api/rules");
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error("Could not load association rules.");
        }

        allRules = data.rules || [];

        applyFilters();

    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty">
                    ${escapeHTML(error.message)}
                </td>
            </tr>
        `;
    }
}


// =====================================================
// FILTER ASSOCIATION RULES
// =====================================================

function applyFilters() {
    const minSupport = Number(
        document.getElementById("supportFilter").value
    );

    const minConfidence = Number(
        document.getElementById("confidenceFilter").value
    );

    const minLift = Number(
        document.getElementById("liftFilter").value
    );

    filteredRules = allRules.filter(rule => {
        const support = Number(rule.support);
        const confidence = Number(rule.confidence) * 100;
        const lift = Number(rule.lift);

        return (
            support >= minSupport &&
            confidence >= minConfidence &&
            lift >= minLift
        );
    });

    filteredRules.sort(
        (a, b) => Number(b.lift) - Number(a.lift)
    );

    renderRules();
    renderRulesChart();
    renderMetricsChart();
    renderStrongestRule();
}


// =====================================================
// RENDER ASSOCIATION RULES TABLE
// =====================================================

function renderRules() {
    const tableBody = document.getElementById("rulesTableBody");
    const count = document.getElementById("rulesCount");

    count.textContent =
        `${filteredRules.length} of ${allRules.length} rules displayed`;

    if (!filteredRules.length) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty">
                    No rules match these filters. Try lowering the thresholds.
                </td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = filteredRules.map((rule, index) => `
        <tr>
            <td>${index + 1}</td>
            <td class="rule-product">${escapeHTML(rule.antecedents)}</td>
            <td class="rule-product">${escapeHTML(rule.consequents)}</td>
            <td class="metric-value">${Number(rule.support).toFixed(6)}</td>
            <td class="metric-value">${(Number(rule.confidence) * 100).toFixed(2)}%</td>
            <td class="metric-value">${Number(rule.lift).toFixed(3)}</td>
        </tr>
    `).join("");
}


// =====================================================
// PLOTLY COMMON LAYOUT
// =====================================================

const chartLayout = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {
        color: "#aab5c8",
        family: "DM Sans"
    },
    margin: {
        t: 20,
        r: 20,
        b: 65,
        l: 50
    },
    xaxis: {
        gridcolor: "#252d3e",
        automargin: true
    },
    yaxis: {
        gridcolor: "#252d3e",
        zeroline: false
    }
};

const chartConfig = {
    responsive: true,
    displayModeBar: false
};


// =====================================================
// TOP PRODUCT RELATIONSHIPS CHART
// =====================================================

function renderRulesChart() {
    const element = document.getElementById("rulesChart");

    if (!element) return;

    if (!filteredRules.length) {
        Plotly.purge(element);
        element.innerHTML = "No matching rules available.";
        return;
    }

    const topRules = filteredRules.slice(0, 10).reverse();

    const labels = topRules.map(rule =>
        `${rule.antecedents} → ${rule.consequents}`
    );

    const values = topRules.map(rule => Number(rule.lift));

    Plotly.react(element, [{
        x: values,
        y: labels,
        type: "bar",
        orientation: "h",
        marker: {
            color: "#9575ff"
        },
        hovertemplate: "Lift: %{x:.3f}<extra></extra>"
    }], {
        ...chartLayout,
        margin: {t: 10, r: 20, b: 35, l: 150},
        xaxis: {
            ...chartLayout.xaxis,
            title: "Lift"
        },
        yaxis: {
            ...chartLayout.yaxis,
            automargin: true
        }
    }, chartConfig);
}


// =====================================================
// ACTUAL METRICS CHART
// =====================================================

function renderMetricsChart() {
    const element = document.getElementById("metricsChart");

    if (!element) return;

    if (!filteredRules.length) {
        Plotly.purge(element);
        element.innerHTML = "No matching rules available.";
        return;
    }

    const supportValues = filteredRules.map(
        rule => Number(rule.support)
    );

    const confidenceValues = filteredRules.map(
        rule => Number(rule.confidence)
    );

    const liftValues = filteredRules.map(
        rule => Number(rule.lift)
    );

    Plotly.react(element, [
        {
            x: supportValues,
            name: "Support",
            type: "box",
            marker: {color: "#43d9e8"},
            boxpoints: "all"
        },
        {
            x: confidenceValues,
            name: "Confidence",
            type: "box",
            marker: {color: "#9575ff"},
            boxpoints: "all"
        },
        {
            x: liftValues,
            name: "Lift",
            type: "box",
            marker: {color: "#43d6a0"},
            boxpoints: "all"
        }
    ], {
        ...chartLayout,
        boxmode: "group",
        showlegend: true,
        legend: {
            orientation: "h",
            y: -0.25
        },
        yaxis: {
            ...chartLayout.yaxis,
            title: "Metric Value"
        },
        xaxis: {
            ...chartLayout.xaxis,
            title: "Association Rule Metrics"
        }
    }, chartConfig);
}


// =====================================================
// STRONGEST PRODUCT ASSOCIATION
// =====================================================

function renderStrongestRule() {
    const element = document.getElementById("strongestRule");

    if (!element) return;

    if (!filteredRules.length) {
        element.textContent = "No matching associations found.";
        return;
    }

    const rule = filteredRules[0];

    element.innerHTML = `
        <strong>
            ${escapeHTML(rule.antecedents)}
            → ${escapeHTML(rule.consequents)}
        </strong>
        <div>
            Support: ${Number(rule.support).toFixed(6)}<br>
            Confidence: ${(Number(rule.confidence) * 100).toFixed(2)}%<br>
            <span class="lift-highlight">
                Lift: ${Number(rule.lift).toFixed(3)}
            </span>
        </div>
    `;
}


// =====================================================
// EXPORT FILTERED RULES TO CSV
// =====================================================

function exportRules() {
    if (!filteredRules.length) {
        alert("There are no rules to export.");
        return;
    }

    const columns = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift"
    ];

    const csvRows = [
        columns.join(","),
        ...filteredRules.map(rule =>
            columns.map(column => {
                const value = rule[column] ?? "";
                return `"${String(value).replace(/"/g, '""')}"`;
            }).join(",")
        )
    ];

    const blob = new Blob(
        [csvRows.join("\n")],
        {type: "text/csv;charset=utf-8;"}
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "basket_iq_association_rules.csv";
    link.click();

    URL.revokeObjectURL(url);
}


// =====================================================
// EVENT LISTENERS
// =====================================================

document.getElementById("applyFiltersBtn")
    ?.addEventListener("click", applyFilters);

document.getElementById("exportRulesBtn")
    ?.addEventListener("click", exportRules);


// =====================================================
// INITIALIZE DASHBOARD
// =====================================================

document.addEventListener("DOMContentLoaded", loadRules);
