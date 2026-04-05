/**
 * Alpha Stack Excel Add-in — Task Pane Logic
 *
 * Handles: tab switching, dynamic tool forms, API communication,
 * result display, and Office.js cell writing.
 */

const API_BASE = "http://localhost:8765";

// State
let toolsRegistry = {};   // Full registry from /tools
let categoriesOrder = [];  // Category display order
let currentToolKey = null; // Currently selected tool
let lastResult = null;     // Last tool execution result

// ── Initialization ──────────────────────────────────────────────────────

Office.onReady(function (info) {
    if (info.host === Office.HostType.Excel) {
        init();
    } else {
        // Running outside Excel (for development/testing)
        init();
    }
});

// Scenario and snapshot state
let scenarios = { base: { name: "Base Case", overrides: {} } };
let snapshots = [];  // [{name, date, params, result}]
let lastSensTable = null;
let lastAuditResults = null;

async function init() {
    setupTabs();
    setupEventListeners();
    await checkHealth();
    await loadTools();
    await loadTemplates();
    await loadSessions();
    loadSnapshots();
}

// ── Tab Switching ────────────────────────────────────────────────────────

function setupTabs() {
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var tab = this.getAttribute("data-tab");
            document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
            document.querySelectorAll(".tab-panel").forEach(function (p) { p.classList.remove("active"); });
            this.classList.add("active");
            document.getElementById(tab + "-tab").classList.add("active");
        });
    });
}

function setupEventListeners() {
    document.getElementById("tool-category").addEventListener("change", onCategoryChange);
    document.getElementById("tool-select").addEventListener("change", onToolChange);
    document.getElementById("btn-run").addEventListener("click", runTool);
    document.getElementById("btn-write").addEventListener("click", writeToSheet);
    document.getElementById("btn-save-session").addEventListener("click", saveCurrentSession);
    document.getElementById("wiki-search").addEventListener("keydown", function (e) {
        if (e.key === "Enter") searchWiki();
    });
    // Sensitivity
    document.getElementById("sens-tool").addEventListener("change", onSensToolChange);
    document.getElementById("btn-sens-generate").addEventListener("click", generateSensitivity);
    document.getElementById("btn-sens-write").addEventListener("click", writeSensToSheet);
    // Scenarios
    document.getElementById("btn-scenario-new").addEventListener("click", showScenarioEditor);
    document.getElementById("btn-scenario-save").addEventListener("click", saveScenario);
    document.getElementById("btn-scenario-cancel").addEventListener("click", hideScenarioEditor);
    document.getElementById("btn-scenario-compare").addEventListener("click", compareScenarios);
    document.getElementById("scenario-select").addEventListener("change", applyScenario);
    // Audit
    document.getElementById("btn-audit-run").addEventListener("click", runAudit);
    document.getElementById("btn-audit-write").addEventListener("click", writeAuditToSheet);
    // Snapshots
    document.getElementById("btn-snapshot").addEventListener("click", takeSnapshot);
    document.getElementById("btn-snapshot-diff").addEventListener("click", diffSnapshots);
}

// ── Health Check ─────────────────────────────────────────────────────────

async function checkHealth() {
    try {
        var resp = await fetch(API_BASE + "/health");
        var data = await resp.json();
        document.getElementById("status-text").textContent = "Connected";
        document.getElementById("status-text").className = "connected";
        document.getElementById("tool-count").textContent = data.tools + " tools";
    } catch (e) {
        document.getElementById("status-text").textContent = "Server offline";
        document.getElementById("status-text").className = "disconnected";
    }
}

// ── Load Tools ───────────────────────────────────────────────────────────

async function loadTools() {
    try {
        var resp = await fetch(API_BASE + "/tools");
        var data = await resp.json();
        categoriesOrder = data.categories;
        toolsRegistry = {};

        // Flatten tools by key for lookup
        Object.keys(data.tools).forEach(function (cat) {
            data.tools[cat].forEach(function (tool) {
                toolsRegistry[tool.key] = tool;
            });
        });

        // Populate category dropdown
        var catSelect = document.getElementById("tool-category");
        catSelect.innerHTML = '<option value="">Select category...</option>';
        categoriesOrder.forEach(function (cat) {
            if (data.tools[cat] && data.tools[cat].length > 0) {
                var opt = document.createElement("option");
                opt.value = cat;
                opt.textContent = cat;
                catSelect.appendChild(opt);
            }
        });

        // Populate sensitivity tool dropdown
        var sensSel = document.getElementById("sens-tool");
        sensSel.innerHTML = '<option value="">Select tool...</option>';
        Object.keys(toolsRegistry).forEach(function (key) {
            var opt = document.createElement("option");
            opt.value = key;
            opt.textContent = toolsRegistry[key].name;
            sensSel.appendChild(opt);
        });
    } catch (e) {
        console.error("Failed to load tools:", e);
    }
}

function onCategoryChange() {
    var cat = document.getElementById("tool-category").value;
    var toolSelect = document.getElementById("tool-select");
    toolSelect.innerHTML = '<option value="">Select tool...</option>';
    toolSelect.disabled = !cat;

    if (!cat) return;

    Object.keys(toolsRegistry).forEach(function (key) {
        var tool = toolsRegistry[key];
        if (tool.category === cat) {
            var opt = document.createElement("option");
            opt.value = key;
            opt.textContent = tool.name;
            toolSelect.appendChild(opt);
        }
    });
}

function onToolChange() {
    var key = document.getElementById("tool-select").value;
    currentToolKey = key;
    document.getElementById("btn-run").disabled = !key;
    buildParamForm(key);
}

// ── Dynamic Parameter Form ───────────────────────────────────────────────

function buildParamForm(toolKey) {
    var container = document.getElementById("param-form");
    container.innerHTML = "";
    if (!toolKey || !toolsRegistry[toolKey]) return;

    var tool = toolsRegistry[toolKey];
    tool.params.forEach(function (param) {
        var group = document.createElement("div");
        group.className = "form-group";

        var label = document.createElement("label");
        label.textContent = param.label;
        if (param.required) {
            var mark = document.createElement("span");
            mark.className = "required-mark";
            mark.textContent = " *";
            label.appendChild(mark);
        }
        group.appendChild(label);

        var input = document.createElement("input");
        input.type = (param.type === "float" || param.type === "int") ? "text" : "text";
        input.id = "param-" + param.name;
        input.placeholder = param.hint || (param.default != null ? "default: " + param.default : "");
        if (param.default != null) input.value = param.default;
        group.appendChild(input);

        if (param.hint) {
            var hint = document.createElement("div");
            hint.className = "hint";
            hint.textContent = param.hint;
            group.appendChild(hint);
        }

        container.appendChild(group);
    });
}

// ── Run Tool ─────────────────────────────────────────────────────────────

async function runTool() {
    if (!currentToolKey) return;
    var tool = toolsRegistry[currentToolKey];
    var preview = document.getElementById("result-preview");
    preview.innerHTML = '<span class="loading"><span class="spinner"></span>Running ' + tool.name + '...</span>';
    document.getElementById("btn-write").disabled = true;

    // Collect params
    var params = {};
    var hasError = false;

    tool.params.forEach(function (param) {
        var input = document.getElementById("param-" + param.name);
        var val = input ? input.value.trim() : "";

        if (!val && param.required) {
            input.style.borderColor = "#cc0000";
            hasError = true;
            return;
        }
        if (input) input.style.borderColor = "";
        if (!val) return;

        // Parse value by type
        if (param.type === "float") {
            params[param.name] = parseFloat(val);
        } else if (param.type === "int") {
            params[param.name] = parseInt(val, 10);
        } else if (param.type === "list[float]") {
            params[param.name] = val.split(",").map(function (s) { return parseFloat(s.trim()); });
        } else if (param.type === "str") {
            params[param.name] = val;
        } else {
            // Complex types — send as string, server will parse
            params[param.name] = val;
        }
    });

    if (hasError) {
        preview.innerHTML = '<span class="negative">Please fill in all required fields.</span>';
        return;
    }

    try {
        var resp = await fetch(API_BASE + "/tools/" + currentToolKey + "/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params)
        });
        var data = await resp.json();

        if (data.ok) {
            lastResult = data.result;
            preview.innerHTML = formatResult(tool.name, data.result);
            document.getElementById("btn-write").disabled = false;
            document.getElementById("btn-save-session").disabled = false;
        } else {
            lastResult = null;
            preview.innerHTML = '<span class="negative">Error: ' + escapeHtml(data.error) + '</span>';
        }
    } catch (e) {
        preview.innerHTML = '<span class="negative">Failed to connect to server: ' + escapeHtml(e.message) + '</span>';
    }
}

async function saveCurrentSession() {
    if (!lastResult || !currentToolKey) return;
    var name = prompt("Session name:", currentToolKey + "-" + new Date().toISOString().slice(0, 10));
    if (!name) return;
    try {
        await fetch(API_BASE + "/sessions/" + encodeURIComponent(name), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ data: lastResult, tags: [currentToolKey] })
        });
        document.getElementById("result-preview").innerHTML +=
            '\n\n<span class="positive">✓ Saved as "' + escapeHtml(name) + '"</span>';
        await loadSessions();
    } catch (e) {
        alert("Save failed: " + e.message);
    }
}

// ── Format Result for Preview ────────────────────────────────────────────

function formatResult(toolName, result) {
    var lines = [];
    lines.push('<span class="section">═══ ' + escapeHtml(toolName) + ' ═══</span>\n');

    Object.keys(result).forEach(function (key) {
        var val = result[key];
        var label = key.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });

        if (val === null || val === undefined) {
            lines.push('<span class="label">' + padRight(label, 24) + '</span>  —');
        } else if (typeof val === "object" && !Array.isArray(val)) {
            lines.push('\n<span class="section">' + label + '</span>');
            Object.keys(val).forEach(function (sk) {
                var sv = val[sk];
                var sl = sk.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                lines.push('  <span class="label">' + padRight(sl, 22) + '</span>  ' + formatValue(sk, sv));
            });
        } else if (Array.isArray(val)) {
            if (val.length > 0 && typeof val[0] === "object") {
                lines.push('\n<span class="section">' + label + '</span>');
                // Table header
                var headers = Object.keys(val[0]);
                lines.push('  ' + headers.map(function (h) {
                    return padRight(h.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); }), 14);
                }).join(""));
                val.slice(0, 20).forEach(function (row) {
                    lines.push('  ' + headers.map(function (h) { return padRight(String(formatNum(h, row[h])), 14); }).join(""));
                });
                if (val.length > 20) lines.push('  ... (' + val.length + ' rows total)');
            } else {
                var display = val.slice(0, 10).map(function (v) { return formatNum(key, v); }).join(", ");
                if (val.length > 10) display += " ...(" + val.length + ")";
                lines.push('<span class="label">' + padRight(label, 24) + '</span>  ' + display);
            }
        } else {
            lines.push('<span class="label">' + padRight(label, 24) + '</span>  ' + formatValue(key, val));
        }
    });

    return lines.join("\n");
}

function formatValue(key, val) {
    if (typeof val === "boolean") return val ? "Yes" : "No";
    if (typeof val === "string") return escapeHtml(val);
    if (typeof val !== "number") return String(val);

    var k = key.toLowerCase();
    var cls = val > 0 ? "positive" : val < 0 ? "negative" : "value";

    if (k.match(/pct|rate|return|yield|margin|growth|irr|wacc|spread|probability/)) {
        var pct = Math.abs(val) < 2 ? (val * 100).toFixed(2) : val.toFixed(2);
        return '<span class="' + cls + '">' + pct + '%</span>';
    }
    if (k.match(/price|value|cost|debt|equity|ev|loan|noi|revenue|ebitda|income|payment|balance|distribution|promote|terminal/)) {
        return '<span class="' + cls + '">$' + numberWithCommas(val.toFixed(2)) + '</span>';
    }
    if (k.match(/moic|multiple|tvpi|dpi|rvpi|sharpe|sortino|ratio|leverage/)) {
        return '<span class="' + cls + '">' + val.toFixed(2) + 'x</span>';
    }

    return '<span class="' + cls + '">' + numberWithCommas(val.toFixed(4)) + '</span>';
}

function formatNum(key, val) {
    if (typeof val !== "number") return String(val);
    var k = key.toLowerCase();
    if (k.match(/pct|rate|return|yield|irr|wacc/)) return (val * 100).toFixed(1) + "%";
    if (k.match(/price|value|cost|debt|equity|loan|noi/)) return "$" + numberWithCommas(val.toFixed(0));
    if (k.match(/moic|multiple/)) return val.toFixed(2) + "x";
    return numberWithCommas(val.toFixed(2));
}

// ── Write to Excel ───────────────────────────────────────────────────────

async function writeToSheet() {
    if (!lastResult || !currentToolKey) return;

    try {
        await Excel.run(async function (context) {
            var sheet = context.workbook.worksheets.getActiveWorksheet();
            var toolName = toolsRegistry[currentToolKey].name;

            // Header
            var header = sheet.getRange("A1");
            header.values = [["Alpha Stack: " + toolName]];
            header.format.font.bold = true;
            header.format.font.size = 14;
            header.format.font.color = "#1a2332";

            var dateCell = sheet.getRange("A2");
            dateCell.values = [[new Date().toLocaleDateString()]];
            dateCell.format.font.color = "#888888";
            dateCell.format.font.size = 10;

            // Write result key-value pairs
            var row = 4;
            Object.keys(lastResult).forEach(function (key) {
                var val = lastResult[key];
                var label = key.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });

                if (typeof val === "object" && val !== null && !Array.isArray(val)) {
                    // Section header
                    var secHeader = sheet.getRange("A" + row);
                    secHeader.values = [[label]];
                    secHeader.format.font.bold = true;
                    secHeader.format.font.color = "#ff9900";
                    row++;

                    Object.keys(val).forEach(function (sk) {
                        var sv = val[sk];
                        if (typeof sv === "number" || typeof sv === "string" || typeof sv === "boolean") {
                            writeKV(sheet, row, sk, sv);
                            row++;
                        }
                    });
                    row++; // blank row
                } else if (Array.isArray(val) && val.length > 0 && typeof val[0] === "object") {
                    // Table
                    var secHeader = sheet.getRange("A" + row);
                    secHeader.values = [[label]];
                    secHeader.format.font.bold = true;
                    secHeader.format.font.color = "#ff9900";
                    row++;

                    var headers = Object.keys(val[0]);
                    headers.forEach(function (h, ci) {
                        var col = String.fromCharCode(65 + ci);
                        var cell = sheet.getRange(col + row);
                        cell.values = [[h.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); })]];
                        cell.format.font.bold = true;
                        cell.format.font.color = "#666666";
                        cell.format.borders.getItem("EdgeBottom").color = "#1a2332";
                    });
                    row++;

                    val.slice(0, 50).forEach(function (item) {
                        headers.forEach(function (h, ci) {
                            var col = String.fromCharCode(65 + ci);
                            var cell = sheet.getRange(col + row);
                            cell.values = [[item[h]]];
                            cell.numberFormat = [[detectExcelFormat(h, item[h])]];
                        });
                        row++;
                    });
                    row++;
                } else if (Array.isArray(val)) {
                    writeKV(sheet, row, key, val.join(", "));
                    row++;
                } else if (val !== null && val !== undefined) {
                    writeKV(sheet, row, key, val);
                    row++;
                }
            });

            // Auto-fit columns
            sheet.getRange("A1:F" + row).format.autofitColumns();
            await context.sync();
        });

        document.getElementById("result-preview").innerHTML += '\n\n<span class="positive">✓ Written to active sheet</span>';
    } catch (e) {
        document.getElementById("result-preview").innerHTML += '\n\n<span class="negative">Write failed: ' + escapeHtml(e.message) + '</span>';
    }
}

function writeKV(sheet, row, key, val) {
    var label = key.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    var labelCell = sheet.getRange("A" + row);
    labelCell.values = [[label]];
    labelCell.format.font.color = "#808080";

    var valueCell = sheet.getRange("B" + row);
    valueCell.values = [[val]];
    valueCell.numberFormat = [[detectExcelFormat(key, val)]];

    if (typeof val === "number") {
        valueCell.format.font.color = val < 0 ? "#cc0000" : "#1a2332";
    }
}

function detectExcelFormat(key, val) {
    if (typeof val !== "number") return "@";
    var k = key.toLowerCase();
    if (k.match(/pct|rate|return|yield|margin|growth|irr|wacc|spread|probability|occupancy/)) return "0.0%";
    if (k.match(/price|value|cost|debt|equity|ev|loan|noi|revenue|ebitda|income|payment|balance|distribution|promote|terminal/)) {
        return Math.abs(val) >= 1000000 ? "$#,##0" : "$#,##0.00";
    }
    if (k.match(/moic|multiple|tvpi|dpi|rvpi|sharpe|sortino|ratio|leverage/)) return '0.00"x"';
    if (k.match(/year|month|day|period/)) return "0";
    return "#,##0.0000";
}

// ── Templates ────────────────────────────────────────────────────────────

async function loadTemplates() {
    try {
        var resp = await fetch(API_BASE + "/templates");
        var data = await resp.json();
        var grid = document.getElementById("template-grid");
        grid.innerHTML = "";

        data.templates.forEach(function (t) {
            var card = document.createElement("div");
            card.className = "template-card";
            card.innerHTML =
                '<div class="name">' + escapeHtml(t.name) + '</div>' +
                '<div class="desc">' + escapeHtml(t.description) + '</div>' +
                '<div class="sheets">' + t.sheets.join(" → ") + '</div>';
            card.addEventListener("click", function () { generateTemplate(t.key); });
            grid.appendChild(card);
        });
    } catch (e) {
        document.getElementById("template-grid").innerHTML =
            '<div class="loading">Templates unavailable — check server connection</div>';
    }
}

async function generateTemplate(templateKey) {
    try {
        var resp = await fetch(API_BASE + "/templates/" + templateKey);
        var template = await resp.json();

        await Excel.run(async function (context) {
            // Create sheets
            for (var i = 0; i < template.sheets.length; i++) {
                var name = template.sheets[i];
                var ws = context.workbook.worksheets.add(name);

                // Title
                var title = ws.getRange("A1");
                title.values = [[template.name + " — " + name]];
                title.format.font.bold = true;
                title.format.font.size = 14;
                title.format.font.color = "#1a2332";
                title.format.borders.getItem("EdgeBottom").color = "#ff9900";
                title.format.borders.getItem("EdgeBottom").weight = "thick";
            }

            // Populate input cells on the Assumptions sheet
            if (template.inputs && template.inputs.cells) {
                var inputSheet = context.workbook.worksheets.getItem(template.inputs.sheet);
                template.inputs.cells.forEach(function (input) {
                    // Label in column A
                    var labelCol = "A" + input.cell.substring(1);
                    var lbl = inputSheet.getRange(labelCol);
                    lbl.values = [[input.label]];
                    lbl.format.font.color = "#808080";

                    // Value in column B with yellow background
                    var val = inputSheet.getRange(input.cell);
                    val.values = [[input.default]];
                    val.numberFormat = [[input.format]];
                    val.format.fill.color = "#FFF2CC"; // Banker yellow
                    val.format.font.color = "#0000CC"; // Blue for hardcodes
                    val.format.font.bold = true;
                });

                // Set column widths
                inputSheet.getRange("A:A").format.columnWidth = 180;
                inputSheet.getRange("B:B").format.columnWidth = 120;

                // Activate the assumptions sheet
                inputSheet.activate();
            }

            await context.sync();
        });

        // Switch to Tools tab with the right tool selected
        document.querySelector('[data-tab="tools"]').click();
        var toolKey = template.tools[0];
        if (toolKey) {
            document.getElementById("tool-category").value = toolsRegistry[toolKey].category;
            onCategoryChange();
            document.getElementById("tool-select").value = toolKey;
            onToolChange();
        }

        alert("Template '" + template.name + "' created! Fill in the yellow cells on the Assumptions sheet, then click Run.");

    } catch (e) {
        alert("Failed to create template: " + e.message);
    }
}

// ── Library: Sessions & Wiki ─────────────────────────────────────────────

async function loadSessions() {
    try {
        var resp = await fetch(API_BASE + "/sessions");
        var data = await resp.json();
        var list = document.getElementById("sessions-list");

        if (!data.sessions || data.sessions.length === 0) {
            list.innerHTML = '<div class="loading">No saved sessions</div>';
            return;
        }

        list.innerHTML = "";
        data.sessions.forEach(function (s) {
            var item = document.createElement("div");
            item.className = "session-item";
            var tags = s.tags && s.tags.length ? s.tags.join(", ") : "";
            item.innerHTML =
                '<div><div class="name">' + escapeHtml(s.name) + '</div>' +
                (tags ? '<div class="tags">' + escapeHtml(tags) + '</div>' : '') + '</div>' +
                '<div class="date">' + (s.saved_at || "").substring(0, 10) + '</div>';
            item.addEventListener("click", function () { loadSessionToPreview(s.name); });
            list.appendChild(item);
        });
    } catch (e) {
        document.getElementById("sessions-list").innerHTML =
            '<div class="loading">Sessions unavailable</div>';
    }
}

async function loadSessionToPreview(name) {
    try {
        var resp = await fetch(API_BASE + "/sessions/" + encodeURIComponent(name));
        var data = await resp.json();
        lastResult = data.data;
        currentToolKey = currentToolKey || "dcf"; // fallback

        // Switch to tools tab and show result
        document.querySelector('[data-tab="tools"]').click();
        document.getElementById("result-preview").innerHTML = formatResult("Session: " + name, data.data);
        document.getElementById("btn-write").disabled = false;
    } catch (e) {
        alert("Failed to load session: " + e.message);
    }
}

async function searchWiki() {
    var query = document.getElementById("wiki-search").value.trim();
    if (!query) return;

    try {
        var resp = await fetch(API_BASE + "/wiki/search?q=" + encodeURIComponent(query));
        var data = await resp.json();
        var container = document.getElementById("wiki-results");

        if (!data.matches || data.matches.length === 0) {
            container.innerHTML = '<div class="loading">No results for "' + escapeHtml(query) + '"</div>';
            return;
        }

        container.innerHTML = "";
        data.matches.forEach(function (m) {
            var item = document.createElement("div");
            item.className = "session-item";
            item.innerHTML =
                '<div><div class="name">' + escapeHtml(m.slug) + '</div>' +
                '<div class="tags">' + escapeHtml(m.category) + '</div></div>';
            item.addEventListener("click", function () { loadWikiPage(m.category, m.slug); });
            container.appendChild(item);
        });
    } catch (e) {
        document.getElementById("wiki-results").innerHTML =
            '<div class="loading">Wiki search failed</div>';
    }
}

async function loadWikiPage(category, slug) {
    try {
        var resp = await fetch(API_BASE + "/wiki/pages/" + encodeURIComponent(category) + "/" + encodeURIComponent(slug));
        var data = await resp.json();
        // Show in result preview on tools tab
        document.querySelector('[data-tab="tools"]').click();
        document.getElementById("result-preview").innerHTML =
            '<span class="section">Wiki: ' + escapeHtml(category) + '/' + escapeHtml(slug) + '</span>\n\n' +
            escapeHtml(data.content || "Empty page");
    } catch (e) {
        alert("Failed to load wiki page: " + e.message);
    }
}

// ── Sensitivity Table Generator ──────────────────────────────────────────

function onSensToolChange() {
    var key = document.getElementById("sens-tool").value;
    if (!key || !toolsRegistry[key]) return;

    var tool = toolsRegistry[key];
    var numParams = tool.params.filter(function (p) { return p.type === "float" || p.type === "int"; });

    // Populate row/col param selects
    ["sens-row-param", "sens-col-param"].forEach(function (id) {
        var sel = document.getElementById(id);
        sel.innerHTML = '<option value="">Select parameter...</option>';
        numParams.forEach(function (p) {
            var opt = document.createElement("option");
            opt.value = p.name;
            opt.textContent = p.label;
            sel.appendChild(opt);
        });
    });

    // Populate output metric (from last result if same tool, otherwise common keys)
    var outSel = document.getElementById("sens-output");
    outSel.innerHTML = '<option value="">Select output...</option>';
    if (lastResult && currentToolKey === key) {
        Object.keys(lastResult).forEach(function (k) {
            if (typeof lastResult[k] === "number") {
                var opt = document.createElement("option");
                opt.value = k;
                opt.textContent = k.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                outSel.appendChild(opt);
            }
        });
    } else {
        ["irr", "moic", "price_per_share", "enterprise_value", "max_loan"].forEach(function (k) {
            var opt = document.createElement("option");
            opt.value = k;
            opt.textContent = k.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
            outSel.appendChild(opt);
        });
    }
}

async function generateSensitivity() {
    var toolKey = document.getElementById("sens-tool").value;
    var outputKey = document.getElementById("sens-output").value;
    var rowParam = document.getElementById("sens-row-param").value;
    var colParam = document.getElementById("sens-col-param").value;
    var rowVals = document.getElementById("sens-row-values").value.split(",").map(function (s) { return parseFloat(s.trim()); });
    var colVals = document.getElementById("sens-col-values").value.split(",").map(function (s) { return parseFloat(s.trim()); });

    if (!toolKey || !outputKey || !rowParam || !colParam || rowVals.length < 2 || colVals.length < 2) {
        document.getElementById("sens-preview").innerHTML = '<span class="negative">Fill in all fields above.</span>';
        return;
    }

    // Collect base params from the Tools tab form
    var baseParams = {};
    if (currentToolKey === toolKey) {
        var tool = toolsRegistry[toolKey];
        tool.params.forEach(function (p) {
            var input = document.getElementById("param-" + p.name);
            if (input && input.value.trim()) {
                if (p.type === "float") baseParams[p.name] = parseFloat(input.value);
                else if (p.type === "int") baseParams[p.name] = parseInt(input.value, 10);
                else if (p.type === "list[float]") baseParams[p.name] = input.value.split(",").map(function (s) { return parseFloat(s.trim()); });
                else baseParams[p.name] = input.value.trim();
            }
        });
    }

    var preview = document.getElementById("sens-preview");
    preview.innerHTML = '<span class="loading"><span class="spinner"></span>Computing sensitivity grid...</span>';

    // Generate the grid by calling the tool for each combination
    var grid = [];
    for (var r = 0; r < rowVals.length; r++) {
        var row = [];
        for (var c = 0; c < colVals.length; c++) {
            var params = Object.assign({}, baseParams);
            params[rowParam] = rowVals[r];
            params[colParam] = colVals[c];

            try {
                var resp = await fetch(API_BASE + "/tools/" + toolKey + "/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(params)
                });
                var data = await resp.json();
                row.push(data.ok ? data.result[outputKey] : null);
            } catch (e) {
                row.push(null);
            }
        }
        grid.push(row);
    }

    lastSensTable = { toolKey: toolKey, outputKey: outputKey, rowParam: rowParam, colParam: colParam, rowVals: rowVals, colVals: colVals, grid: grid };

    // Render preview
    var rowLabel = rowParam.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    var colLabel = colParam.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });

    var html = '<table class="sens-table"><tr><th>' + escapeHtml(rowLabel) + ' \\ ' + escapeHtml(colLabel) + '</th>';
    colVals.forEach(function (cv) { html += '<th>' + formatNum(colParam, cv) + '</th>'; });
    html += '</tr>';

    for (var r = 0; r < rowVals.length; r++) {
        html += '<tr><th>' + formatNum(rowParam, rowVals[r]) + '</th>';
        for (var c = 0; c < colVals.length; c++) {
            var val = grid[r][c];
            var isBase = (rowVals[r] === baseParams[rowParam] && colVals[c] === baseParams[colParam]);
            var cls = isBase ? ' class="base-case"' : '';
            html += '<td' + cls + '>' + (val !== null ? formatNum(outputKey, val) : '—') + '</td>';
        }
        html += '</tr>';
    }
    html += '</table>';
    preview.innerHTML = html;
}

async function writeSensToSheet() {
    if (!lastSensTable) return;
    var s = lastSensTable;

    try {
        await Excel.run(async function (context) {
            var sheet = context.workbook.worksheets.getActiveWorksheet();
            var startRow = 2;
            var outputLabel = s.outputKey.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });

            // Title
            sheet.getRange("A1").values = [["Sensitivity: " + outputLabel]];
            sheet.getRange("A1").format.font.bold = true;
            sheet.getRange("A1").format.font.size = 12;

            // Column headers
            for (var c = 0; c < s.colVals.length; c++) {
                var col = String.fromCharCode(66 + c); // B, C, D, ...
                var cell = sheet.getRange(col + startRow);
                cell.values = [[s.colVals[c]]];
                cell.format.font.bold = true;
                cell.format.font.color = "#666666";
                cell.numberFormat = [[detectExcelFormat(s.colParam, s.colVals[c])]];
            }

            // Row headers + data
            for (var r = 0; r < s.rowVals.length; r++) {
                var row = startRow + 1 + r;
                var rowHead = sheet.getRange("A" + row);
                rowHead.values = [[s.rowVals[r]]];
                rowHead.format.font.bold = true;
                rowHead.format.font.color = "#666666";
                rowHead.numberFormat = [[detectExcelFormat(s.rowParam, s.rowVals[r])]];

                for (var c = 0; c < s.colVals.length; c++) {
                    var col = String.fromCharCode(66 + c);
                    var cell = sheet.getRange(col + row);
                    var val = s.grid[r][c];
                    cell.values = [[val !== null ? val : ""]];
                    cell.numberFormat = [[detectExcelFormat(s.outputKey, val)]];

                    // Highlight base case
                    if (val !== null && s.grid[r][c] === s.grid[Math.floor(s.rowVals.length / 2)][Math.floor(s.colVals.length / 2)]) {
                        cell.format.fill.color = "#FFF2CC";
                        cell.format.font.bold = true;
                    }
                }
            }

            sheet.getRange("A1:H" + (startRow + s.rowVals.length + 1)).format.autofitColumns();
            await context.sync();
        });

        document.getElementById("sens-preview").innerHTML += '<br><span class="positive">✓ Written to sheet</span>';
    } catch (e) {
        document.getElementById("sens-preview").innerHTML += '<br><span class="negative">Write failed: ' + escapeHtml(e.message) + '</span>';
    }
}

// ── Scenario Manager ─────────────────────────────────────────────────────

function showScenarioEditor() {
    if (!currentToolKey) {
        alert("Select a tool on the Tools tab first.");
        return;
    }
    var editor = document.getElementById("scenario-editor");
    editor.style.display = "block";
    document.getElementById("scenario-name").value = "";

    // Build override fields from current tool params
    var container = document.getElementById("scenario-overrides");
    container.innerHTML = "";
    var tool = toolsRegistry[currentToolKey];
    tool.params.forEach(function (p) {
        if (p.type !== "float" && p.type !== "int") return;
        var row = document.createElement("div");
        row.className = "override-row";

        var label = document.createElement("label");
        label.textContent = p.label;
        row.appendChild(label);

        var input = document.createElement("input");
        input.type = "text";
        input.id = "override-" + p.name;
        input.placeholder = "same as base";
        row.appendChild(input);

        container.appendChild(row);
    });
}

function hideScenarioEditor() {
    document.getElementById("scenario-editor").style.display = "none";
}

function saveScenario() {
    var name = document.getElementById("scenario-name").value.trim();
    if (!name) { alert("Enter a scenario name."); return; }

    var key = name.toLowerCase().replace(/\s+/g, "_");
    var overrides = {};

    if (currentToolKey) {
        var tool = toolsRegistry[currentToolKey];
        tool.params.forEach(function (p) {
            var input = document.getElementById("override-" + p.name);
            if (input && input.value.trim()) {
                overrides[p.name] = p.type === "int" ? parseInt(input.value, 10) : parseFloat(input.value);
            }
        });
    }

    scenarios[key] = { name: name, overrides: overrides, tool: currentToolKey };

    // Update dropdown
    var sel = document.getElementById("scenario-select");
    var opt = document.createElement("option");
    opt.value = key;
    opt.textContent = name;
    sel.appendChild(opt);

    hideScenarioEditor();
    document.getElementById("scenario-preview").innerHTML =
        '<span class="positive">✓ Scenario "' + escapeHtml(name) + '" saved with ' +
        Object.keys(overrides).length + ' overrides</span>';
}

async function applyScenario() {
    var key = document.getElementById("scenario-select").value;
    if (!key || !scenarios[key]) return;
    var scenario = scenarios[key];

    if (!scenario.tool || !toolsRegistry[scenario.tool]) return;

    // Apply overrides to the form inputs
    var tool = toolsRegistry[scenario.tool];
    tool.params.forEach(function (p) {
        var input = document.getElementById("param-" + p.name);
        if (input && scenario.overrides[p.name] !== undefined) {
            input.value = scenario.overrides[p.name];
            input.style.background = "#fff2cc"; // Yellow to show it was changed
        }
    });

    document.getElementById("scenario-preview").innerHTML =
        '<span class="positive">Applied "' + escapeHtml(scenario.name) + '" — ' +
        Object.keys(scenario.overrides).length + ' overrides set. Click Run on Tools tab.</span>';
}

async function compareScenarios() {
    var scenarioKeys = Object.keys(scenarios);
    if (scenarioKeys.length < 2) {
        document.getElementById("scenario-preview").innerHTML =
            '<span class="negative">Need at least 2 scenarios to compare. Create scenarios first.</span>';
        return;
    }

    if (!currentToolKey) {
        alert("Select a tool on the Tools tab first.");
        return;
    }

    var preview = document.getElementById("scenario-preview");
    preview.innerHTML = '<span class="loading"><span class="spinner"></span>Running scenarios...</span>';

    // Collect base params
    var baseParams = {};
    var tool = toolsRegistry[currentToolKey];
    tool.params.forEach(function (p) {
        var input = document.getElementById("param-" + p.name);
        if (input && input.value.trim()) {
            if (p.type === "float") baseParams[p.name] = parseFloat(input.value);
            else if (p.type === "int") baseParams[p.name] = parseInt(input.value, 10);
            else if (p.type === "list[float]") baseParams[p.name] = input.value.split(",").map(function (s) { return parseFloat(s.trim()); });
            else baseParams[p.name] = input.value.trim();
        }
    });

    // Run each scenario
    var results = {};
    for (var i = 0; i < scenarioKeys.length; i++) {
        var sKey = scenarioKeys[i];
        var scenario = scenarios[sKey];
        var params = Object.assign({}, baseParams, scenario.overrides);

        try {
            var resp = await fetch(API_BASE + "/tools/" + currentToolKey + "/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(params)
            });
            var data = await resp.json();
            results[sKey] = data.ok ? data.result : null;
        } catch (e) {
            results[sKey] = null;
        }
    }

    // Build comparison table
    var numericKeys = [];
    var firstResult = results[scenarioKeys[0]];
    if (firstResult) {
        Object.keys(firstResult).forEach(function (k) {
            if (typeof firstResult[k] === "number") numericKeys.push(k);
        });
    }

    var html = '<table class="diff-table"><tr><th>Metric</th>';
    scenarioKeys.forEach(function (sk) {
        html += '<th>' + escapeHtml(scenarios[sk].name) + '</th>';
    });
    html += '</tr>';

    numericKeys.forEach(function (metric) {
        html += '<tr><th>' + escapeHtml(metric.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); })) + '</th>';
        scenarioKeys.forEach(function (sk) {
            var val = results[sk] ? results[sk][metric] : null;
            html += '<td>' + (val !== null ? formatNum(metric, val) : '—') + '</td>';
        });
        html += '</tr>';
    });

    html += '</table>';
    preview.innerHTML = html;
}

// ── Model Audit Engine ───────────────────────────────────────���───────────

async function runAudit() {
    var results = document.getElementById("audit-results");
    results.innerHTML = '<span class="loading"><span class="spinner"></span>Auditing active sheet...</span>';

    try {
        var issues = await Excel.run(async function (context) {
            var sheet = context.workbook.worksheets.getActiveWorksheet();
            var usedRange = sheet.getUsedRange();
            usedRange.load("values,formulas,numberFormat,address,rowCount,columnCount");
            await context.sync();

            var findings = [];
            var values = usedRange.values;
            var formulas = usedRange.formulas;
            var rows = usedRange.rowCount;
            var cols = usedRange.columnCount;

            for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                    var val = values[r][c];
                    var formula = formulas[r][c];
                    var cellRef = String.fromCharCode(65 + c) + (r + 1);

                    // Skip empty cells
                    if (val === "" || val === null) continue;

                    // Check 1: Hardcoded numbers that look like they should be formulas
                    if (typeof val === "number" && typeof formula === "number") {
                        // It's a literal number, not a formula
                        // Flag large round numbers that might be hardcoded assumptions
                        if (Math.abs(val) > 100 && val === Math.round(val) && val !== 0) {
                            // Check if neighboring cells have formulas (suggesting this one should too)
                            var hasFormulaNeighbor = false;
                            if (r > 0 && typeof formulas[r - 1][c] === "string" && formulas[r - 1][c].startsWith("=")) hasFormulaNeighbor = true;
                            if (r < rows - 1 && typeof formulas[r + 1][c] === "string" && formulas[r + 1][c].startsWith("=")) hasFormulaNeighbor = true;

                            if (hasFormulaNeighbor) {
                                findings.push({
                                    severity: "warning",
                                    cell: cellRef,
                                    message: "Hardcoded value (" + numberWithCommas(val) + ") in a column with formulas — should this be a formula?",
                                });
                            }
                        }
                    }

                    // Check 2: Formula containing hardcoded numbers
                    if (typeof formula === "string" && formula.startsWith("=")) {
                        var hardcodeMatch = formula.match(/[^A-Z\$](\d{3,})/g);
                        if (hardcodeMatch) {
                            findings.push({
                                severity: "warning",
                                cell: cellRef,
                                message: "Formula contains embedded constant: " + escapeHtml(formula.substring(0, 40)),
                            });
                        }
                    }

                    // Check 3: #REF! errors
                    if (typeof val === "string" && val.indexOf("#REF!") >= 0) {
                        findings.push({
                            severity: "error",
                            cell: cellRef,
                            message: "Broken reference (#REF! error)",
                        });
                    }

                    // Check 4: #DIV/0! errors
                    if (typeof val === "string" && val.indexOf("#DIV/0!") >= 0) {
                        findings.push({
                            severity: "error",
                            cell: cellRef,
                            message: "Division by zero (#DIV/0! error)",
                        });
                    }

                    // Check 5: #VALUE! errors
                    if (typeof val === "string" && val.indexOf("#VALUE!") >= 0) {
                        findings.push({
                            severity: "error",
                            cell: cellRef,
                            message: "Value error (#VALUE!)",
                        });
                    }

                    // Check 6: Negative cash flows that might have wrong sign
                    if (typeof val === "number" && c > 0) {
                        // Check for sign inconsistency in a row (common in cash flow models)
                        var prevVal = values[r][c - 1];
                        if (typeof prevVal === "number" && prevVal !== 0 && val !== 0) {
                            if ((prevVal > 0 && val < 0) || (prevVal < 0 && val > 0)) {
                                // Only flag in rows that look like time series (3+ consecutive numbers)
                                var numericCount = 0;
                                for (var cc = 0; cc < cols; cc++) {
                                    if (typeof values[r][cc] === "number" && values[r][cc] !== 0) numericCount++;
                                }
                                if (numericCount >= 5) {
                                    findings.push({
                                        severity: "info",
                                        cell: cellRef,
                                        message: "Sign change in time series row — verify sign convention is intentional",
                                    });
                                }
                            }
                        }
                    }
                }
            }

            // Check 7: Formula consistency — compare formulas in adjacent cells
            for (var r = 1; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                    var f = formulas[r][c];
                    var fPrev = formulas[r - 1][c];
                    if (typeof f === "string" && f.startsWith("=") &&
                        typeof fPrev === "string" && fPrev.startsWith("=")) {
                        // Normalize: strip row numbers to compare formula patterns
                        var pattern = f.replace(/\d+/g, "N");
                        var prevPattern = fPrev.replace(/\d+/g, "N");
                        if (pattern !== prevPattern && r > 1) {
                            // Check the cell above the previous to confirm the pattern was consistent before
                            var fPrevPrev = r >= 2 ? formulas[r - 2][c] : null;
                            if (typeof fPrevPrev === "string" && fPrevPrev.replace(/\d+/g, "N") === prevPattern) {
                                findings.push({
                                    severity: "warning",
                                    cell: String.fromCharCode(65 + c) + (r + 1),
                                    message: "Formula pattern breaks from cells above — possible copy error",
                                });
                            }
                        }
                    }
                }
            }

            return findings;
        });

        lastAuditResults = issues;

        if (issues.length === 0) {
            results.innerHTML = '<span class="positive">✓ No issues found! Model looks clean.</span>';
        } else {
            var errorCount = issues.filter(function (i) { return i.severity === "error"; }).length;
            var warnCount = issues.filter(function (i) { return i.severity === "warning"; }).length;
            var infoCount = issues.filter(function (i) { return i.severity === "info"; }).length;

            var html = '<div style="margin-bottom: 8px;">';
            if (errorCount) html += '<span class="severity error">' + errorCount + ' errors</span> ';
            if (warnCount) html += '<span class="severity warning">' + warnCount + ' warnings</span> ';
            if (infoCount) html += '<span class="severity info">' + infoCount + ' info</span>';
            html += '</div>';

            issues.slice(0, 50).forEach(function (issue) {
                html += '<div class="audit-item">' +
                    '<span class="severity ' + issue.severity + '">' + issue.severity.toUpperCase() + '</span>' +
                    '<span class="cell-ref">' + issue.cell + '</span>' +
                    '<div class="message">' + escapeHtml(issue.message) + '</div>' +
                    '</div>';
            });

            if (issues.length > 50) {
                html += '<div class="hint-text">' + (issues.length - 50) + ' more issues not shown</div>';
            }

            results.innerHTML = html;
        }
    } catch (e) {
        results.innerHTML = '<span class="negative">Audit failed: ' + escapeHtml(e.message) + '</span>';
    }
}

async function writeAuditToSheet() {
    if (!lastAuditResults || lastAuditResults.length === 0) return;

    try {
        await Excel.run(async function (context) {
            var ws = context.workbook.worksheets.add("Audit Report");

            // Header
            ws.getRange("A1").values = [["Alpha Stack Model Audit"]];
            ws.getRange("A1").format.font.bold = true;
            ws.getRange("A1").format.font.size = 14;

            ws.getRange("A2").values = [[new Date().toLocaleString()]];
            ws.getRange("A2").format.font.color = "#888888";

            // Column headers
            var headers = ws.getRange("A4:D4");
            headers.values = [["Severity", "Cell", "Message", ""]];
            headers.format.font.bold = true;
            headers.format.font.color = "#666666";
            headers.format.borders.getItem("EdgeBottom").color = "#1a2332";

            // Data
            lastAuditResults.forEach(function (issue, i) {
                var row = 5 + i;
                ws.getRange("A" + row).values = [[issue.severity.toUpperCase()]];
                ws.getRange("B" + row).values = [[issue.cell]];
                ws.getRange("C" + row).values = [[issue.message]];

                if (issue.severity === "error") {
                    ws.getRange("A" + row).format.font.color = "#cc0000";
                } else if (issue.severity === "warning") {
                    ws.getRange("A" + row).format.font.color = "#e68a00";
                }
            });

            ws.getRange("A1:D" + (5 + lastAuditResults.length)).format.autofitColumns();
            ws.activate();
            await context.sync();
        });

        document.getElementById("audit-results").innerHTML +=
            '<br><span class="positive">✓ Audit report written to new sheet</span>';
    } catch (e) {
        alert("Failed to write audit report: " + e.message);
    }
}

// ── Version Snapshots ────────────────────────────────────────────────────

function takeSnapshot() {
    if (!currentToolKey || !lastResult) {
        alert("Run a tool first, then take a snapshot.");
        return;
    }

    var name = prompt("Snapshot name:", "v" + (snapshots.length + 1));
    if (!name) return;

    // Collect current params
    var params = {};
    var tool = toolsRegistry[currentToolKey];
    tool.params.forEach(function (p) {
        var input = document.getElementById("param-" + p.name);
        if (input && input.value.trim()) {
            params[p.name] = input.value.trim();
        }
    });

    var snapshot = {
        name: name,
        date: new Date().toISOString(),
        tool: currentToolKey,
        params: params,
        result: lastResult,
    };

    snapshots.push(snapshot);
    localStorage.setItem("alpha_snapshots", JSON.stringify(snapshots));
    renderSnapshots();
}

function loadSnapshots() {
    try {
        var saved = localStorage.getItem("alpha_snapshots");
        if (saved) snapshots = JSON.parse(saved);
    } catch (e) {
        snapshots = [];
    }
    renderSnapshots();
}

function renderSnapshots() {
    var list = document.getElementById("snapshots-list");
    if (!snapshots.length) {
        list.innerHTML = '<div class="hint-text">No snapshots yet. Run a tool and take a snapshot.</div>';
        return;
    }

    list.innerHTML = "";
    snapshots.forEach(function (snap, i) {
        var item = document.createElement("div");
        item.className = "snapshot-item";
        item.innerHTML =
            '<span class="snap-name">' + escapeHtml(snap.name) + '</span>' +
            '<span class="snap-date">' + snap.date.substring(0, 10) + '</span>';
        item.addEventListener("click", function () { restoreSnapshot(i); });
        list.appendChild(item);
    });
}

function restoreSnapshot(index) {
    var snap = snapshots[index];
    if (!snap) return;

    // Switch to the right tool
    if (snap.tool && toolsRegistry[snap.tool]) {
        document.getElementById("tool-category").value = toolsRegistry[snap.tool].category;
        onCategoryChange();
        document.getElementById("tool-select").value = snap.tool;
        onToolChange();

        // Fill in params
        Object.keys(snap.params).forEach(function (name) {
            var input = document.getElementById("param-" + name);
            if (input) input.value = snap.params[name];
        });
    }

    // Show result
    lastResult = snap.result;
    currentToolKey = snap.tool;
    document.querySelector('[data-tab="tools"]').click();
    document.getElementById("result-preview").innerHTML = formatResult("Snapshot: " + snap.name, snap.result);
    document.getElementById("btn-write").disabled = false;
    document.getElementById("btn-save-session").disabled = false;
}

function diffSnapshots() {
    if (snapshots.length < 2) {
        alert("Need at least 2 snapshots to diff.");
        return;
    }

    // Pick the last two by default
    var a = snapshots[snapshots.length - 2];
    var b = snapshots[snapshots.length - 1];

    var html = '<div class="section-header">Diff: ' + escapeHtml(a.name) + ' vs ' + escapeHtml(b.name) + '</div>';

    // Params diff
    html += '<table class="diff-table"><tr><th>Parameter</th><th>' + escapeHtml(a.name) + '</th><th>' + escapeHtml(b.name) + '</th><th>Δ</th></tr>';
    var allParams = new Set(Object.keys(a.params).concat(Object.keys(b.params)));
    allParams.forEach(function (p) {
        var va = a.params[p] || "—";
        var vb = b.params[p] || "—";
        var changed = va !== vb;
        var cls = changed ? ' class="changed"' : '';
        html += '<tr' + cls + '><th>' + escapeHtml(p.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); })) + '</th>';
        html += '<td>' + escapeHtml(String(va)) + '</td><td>' + escapeHtml(String(vb)) + '</td>';
        if (changed && !isNaN(parseFloat(va)) && !isNaN(parseFloat(vb))) {
            var delta = parseFloat(vb) - parseFloat(va);
            var cls2 = delta > 0 ? "delta-positive" : "delta-negative";
            html += '<td class="' + cls2 + '">' + (delta > 0 ? "+" : "") + delta.toFixed(4) + '</td>';
        } else {
            html += '<td>' + (changed ? "changed" : "") + '</td>';
        }
        html += '</tr>';
    });
    html += '</table>';

    // Results diff
    html += '<br><table class="diff-table"><tr><th>Output</th><th>' + escapeHtml(a.name) + '</th><th>' + escapeHtml(b.name) + '</th><th>Δ</th></tr>';
    var allKeys = new Set(Object.keys(a.result || {}).concat(Object.keys(b.result || {})));
    allKeys.forEach(function (k) {
        var va = a.result ? a.result[k] : null;
        var vb = b.result ? b.result[k] : null;
        if (typeof va !== "number" || typeof vb !== "number") return;
        var changed = va !== vb;
        var cls = changed ? ' class="changed"' : '';
        var label = k.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
        html += '<tr' + cls + '><th>' + escapeHtml(label) + '</th>';
        html += '<td>' + formatNum(k, va) + '</td><td>' + formatNum(k, vb) + '</td>';
        if (changed) {
            var delta = vb - va;
            var pctChange = va !== 0 ? ((delta / Math.abs(va)) * 100).toFixed(1) + "%" : "N/A";
            var cls2 = delta > 0 ? "delta-positive" : "delta-negative";
            html += '<td class="' + cls2 + '">' + (delta > 0 ? "+" : "") + formatNum(k, delta) + ' (' + pctChange + ')</td>';
        } else {
            html += '<td></td>';
        }
        html += '</tr>';
    });
    html += '</table>';

    document.getElementById("snapshots-list").innerHTML += html;
}

// ── Utilities ────────────────────────────────────────────────────────────

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function padRight(str, len) {
    while (str.length < len) str += " ";
    return str.substring(0, len);
}

function escapeHtml(str) {
    if (typeof str !== "string") return String(str);
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
