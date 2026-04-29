/* ==========================================================
   workflow.js – Main UI workflow (steps, generate, execute)
   ========================================================== */

let currentStep = 1;
let selectedLLMType = 'gemini';
let selectedModel = 'models/gemini-2.0-flash';
let currentQuery = '';
let similarQueries = [];
let generatedSQL = '';
let selectedSimilarIndex = null;

// ---- Initialise on DOM ready ----------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    initializeVoiceRecognition();
    initializeDatabaseFeature();
    selectedLLMType = 'gemini';
    selectedModel = 'models/gemini-2.0-flash';
});

function setupEventListeners() {
    document.getElementById('checkSimilarityBtn').addEventListener('click', checkSimilarity);
    document.getElementById('useSimilarBtn').addEventListener('click', useSimilarQuery);
    document.getElementById('proceedToModelBtn').addEventListener('click', proceedToModelSelection);
    document.getElementById('generateSqlBtnGemini').addEventListener('click', () => generateSQL('gemini'));
    document.getElementById('generateSqlBtnOllama').addEventListener('click', () => generateSQL('ollama'));
    document.getElementById('ollamaModelSelect').addEventListener('change', updateOllamaButton);
    document.getElementById('executeSqlBtn').addEventListener('click', executeSQL);
    document.getElementById('editSqlBtn').addEventListener('click', editSQL);
    document.getElementById('startOverBtn').addEventListener('click', startOver);
    document.getElementById('micButton').addEventListener('click', toggleVoiceRecognition);
    document.getElementById('languageSelector').addEventListener('change', onLanguageChange);
}

// ---- Step management -------------------------------------------------

function updateStepStatus(stepNum, status) {
    const el = document.getElementById(`step${stepNum}`);
    const num = document.getElementById(`step${stepNum}-number`);
    el.classList.remove('active', 'completed', 'error');
    num.classList.remove('completed', 'error');
    if (status === 'active')    el.classList.add('active');
    else if (status === 'completed') { el.classList.add('completed'); num.classList.add('completed'); num.textContent = '✓'; }
    else if (status === 'error')     { el.classList.add('error'); num.classList.add('error'); num.textContent = '✗'; }
    else num.textContent = stepNum;
}

function showMessage(message, type) {
    let el = document.getElementById('globalMessage');
    if (!el) { el = document.createElement('div'); el.id = 'globalMessage'; document.querySelector('.workflow-container').prepend(el); }
    el.className = `message ${type}`; el.textContent = message;
    if (type === 'success' || type === 'info') setTimeout(() => { if (el) el.remove(); }, 5000);
}

function setQuery(q) { document.getElementById('naturalQuery').value = q; }

// ---- Similarity check ------------------------------------------------

async function checkSimilarity() {
    const query = document.getElementById('naturalQuery').value.trim();
    if (!query) { showMessage('Please enter a query', 'error'); return; }
    currentQuery = query;
    updateStepStatus(1, 'completed');
    updateStepStatus(2, 'active');
    try {
        const resp = await apiPost('/api/similarity-check', { query });
        const ct = resp.headers.get('content-type') || '';
        let result;
        if (ct.includes('application/json')) { result = await resp.json(); }
        else { const t = await resp.text(); throw new Error('Non-JSON: ' + t.slice(0, 500)); }
        if (!resp.ok || !result.success) throw new Error(result.error || 'Similarity check failed');
        similarQueries = result.similar_queries || [];
        displaySimilarityResults(similarQueries);
    } catch (e) { updateStepStatus(2, 'error'); showMessage('Similarity check failed: ' + e.message, 'error'); }
}

function displaySimilarityResults(similar) {
    const div = document.getElementById('similarityResults');
    const actions = document.getElementById('similarityActions');

    if (!similar.length) {
        div.innerHTML = '<div class="message info">🔍 No similar queries found. Proceeding to model selection...</div>';
        actions.style.display = 'none';
        setTimeout(() => { updateStepStatus(2, 'completed'); proceedToModelSelection(); }, 1500);
        return;
    }

    selectedSimilarIndex = 0;
    const best = similar[0];
    const score = (best.similarity * 100).toFixed(1);
    const queryInput = document.getElementById('naturalQuery');
    if (!queryInput) return;
    const cq = queryInput.value.trim();

    showMessage('🔄 Found similar query, adapting...', 'info');

    apiPost('/api/swap-entities', {
        original_query: best.query.natural_query,
        new_query: cq,
        original_sql: best.query.sql_query,
    }).then(r => r.json()).then(result => {
        if (!result.success) throw new Error(result.error || 'Swap failed');
        const adapted = result.adapted_sql;
        const structural = result.structural_change || false;

        if (structural) {
            // Structural change → cache can't help, auto-proceed to Generate New SQL
            div.innerHTML = '<div class="message info">🔄 Similar query found but structure differs (filter/aggregation change). Generating fresh SQL...</div>';
            actions.style.display = 'none';
            updateStepStatus(2, 'completed');
            setTimeout(proceedToModelSelection, 1200);
            return;
        }

        let html = '<div class="similarity-results"><h4>⚡ Smart Cache Hit!</h4><div class="best-match-info">';
        html += `<p><strong>Match Score:</strong> ${score}%</p>`;
        if (result.swapped) {
            html += `<p style="color:#28a745"><strong>✓ Smart Adaptation:</strong> ${result.message}</p>`;
        }
        html += `<p><strong>Adapted SQL:</strong></p><div class="sql-preview">${adapted}</div>`;
        html += '</div></div>';
        div.innerHTML = html; actions.style.display = 'block'; updateStepStatus(2, 'completed');
    }).catch(() => {
        div.innerHTML = `<div class="similarity-results"><h4>✅ Similar Query Found!</h4><div class="best-match-info"><p><strong>Score:</strong> ${score}%</p></div></div>`;
        actions.style.display = 'block'; updateStepStatus(2, 'completed');
    });
}

function useSimilarQuery() {
    if (selectedSimilarIndex === null) { showMessage('Check similarity first', 'error'); return; }
    const sel = similarQueries[selectedSimilarIndex];
    const queryInput = document.getElementById('naturalQuery');
    if (!queryInput) return;
    const cq = queryInput.value.trim();
    showMessage('⚡ Using cached query...', 'info');

    apiPost('/api/swap-entities', {
        original_query: sel.query.natural_query,
        new_query: cq,
        original_sql: sel.query.sql_query,
    }).then(r => r.json()).then(result => {
        if (!result.success) throw new Error(result.error);
        generatedSQL = result.adapted_sql;
        updateStepStatus(2, 'completed'); updateStepStatus(3, 'completed'); updateStepStatus(4, 'active');
        document.getElementById('generatedSQL').textContent = generatedSQL;
        document.getElementById('sqlActions').style.display = 'block';
        updateStepStatus(4, 'completed');
        if (result.structural_change) showMessage('⚠️ Cached query used; aggregation changes detected.', 'warning');
        else if (result.swapped) showMessage('✅ ' + result.message + ' ⚡ (Instant)', 'success');
        else showMessage('✅ Exact cached query! ⚡', 'success');
    }).catch(e => {
        showMessage('Adaptation failed: ' + e.message, 'error');
        generatedSQL = sel.query.sql_query;
        document.getElementById('generatedSQL').textContent = generatedSQL;
        updateStepStatus(2, 'completed'); updateStepStatus(3, 'completed'); updateStepStatus(4, 'completed');
    });
}

function proceedToModelSelection() {
    updateStepStatus(3, 'active');
    document.getElementById('llmChoiceContainer').style.display = 'block';
}

function updateOllamaButton() {
    const s = document.getElementById('ollamaModelSelect');
    document.getElementById('generateSqlBtnOllama').disabled = !s.value;
}

// ---- SQL generation --------------------------------------------------

async function generateSQL(modelType) {
    updateStepStatus(3, 'completed'); updateStepStatus(4, 'active');
    document.getElementById('loadingSQL').style.display = 'flex';
    try {
        let body;
        if (modelType === 'gemini') {
            body = { query: currentQuery, model: 'models/gemini-2.0-flash', use_ollama: false };
        } else {
            const m = document.getElementById('ollamaModelSelect').value;
            if (!m) { showMessage('Select an Ollama model', 'error'); document.getElementById('loadingSQL').style.display = 'none'; updateStepStatus(4, 'error'); return; }
            body = { query: currentQuery, model: m, use_ollama: true };
        }
        const resp = await apiPost('/api/generate-sql', body);
        const result = await resp.json();
        document.getElementById('loadingSQL').style.display = 'none';
        if (result.success) {
            generatedSQL = result.sql_query;
            document.getElementById('generatedSQL').textContent = generatedSQL;
            document.getElementById('sqlActions').style.display = 'block';
            updateStepStatus(4, 'completed');
            showMessage(`SQL generated with ${modelType === 'gemini' ? 'Gemini 2.0 Flash' : body.model}!`, 'success');
        } else { updateStepStatus(4, 'error'); showMessage('Generate failed: ' + result.error, 'error'); }
    } catch (e) { document.getElementById('loadingSQL').style.display = 'none'; updateStepStatus(4, 'error'); showMessage('Error: ' + e.message, 'error'); }
}

// ---- Execution -------------------------------------------------------

async function executeSQL() {
    updateStepStatus(5, 'active');
    document.getElementById('loadingExecution').style.display = 'flex';
    const viz = document.getElementById('visualizeCheck').checked;
    const ct = document.getElementById('chartType').value;
    try {
        const resp = await apiPost('/api/execute-sql', { sql_query: generatedSQL, natural_query: currentQuery, visualize: viz, chart_type: ct });
        const result = await resp.json();
        document.getElementById('loadingExecution').style.display = 'none';
        if (result.success) { displayExecutionResults(result); updateStepStatus(5, 'completed'); }
        else { updateStepStatus(5, 'error'); showMessage('Execution failed: ' + result.error, 'error'); }
    } catch (e) { document.getElementById('loadingExecution').style.display = 'none'; updateStepStatus(5, 'error'); showMessage('Execution error: ' + e.message, 'error'); }
}

function displayExecutionResults(result) {
    const div = document.getElementById('executionResults');
    let html = '';
    if (result.database_used) {
        const n = result.database_used.split('/').pop().split('\\').pop();
        html += `<div class="message info" style="margin-bottom:10px">🗄️ Database: <strong>${n}</strong></div>`;
    }
    html += `<div class="message success">✅ Executed in ${result.execution_time}s</div>`;
    if (result.data && result.data.length) { html += createDataTable(result.data) + createExportButtons(); }
    else { html += '<div class="message info">📋 No rows returned.</div>'; }
    if (result.visualization_data) {
        html += '<div id="plotlyDiv" style="width:100%;height:500px;margin-top:20px"></div>';
        setTimeout(() => Plotly.newPlot('plotlyDiv', result.visualization_data.data, result.visualization_data.layout), 100);
    }
    div.innerHTML = html;
}

function createDataTable(data) {
    if (!data || !data.length) return '';
    const cols = Object.keys(data[0]);
    let html = '<table class="data-table"><thead><tr>';
    cols.forEach(c => html += `<th>${c}</th>`);
    html += '</tr></thead><tbody>';
    data.slice(0, 100).forEach(row => { html += '<tr>'; cols.forEach(c => html += `<td>${row[c] !== null ? row[c] : ''}</td>`); html += '</tr>'; });
    html += '</tbody></table>';
    if (data.length > 100) html += `<div class="message info">Showing 100 of ${data.length} rows.</div>`;
    return html;
}

function createExportButtons() {
    return `<div class="export-buttons">
        <button class="export-btn" onclick="exportData('csv')">📄 CSV</button>
        <button class="export-btn" onclick="exportData('excel')">📊 Excel</button>
        <button class="export-btn" onclick="exportData('json')">📋 JSON</button>
    </div>`;
}

// ---- Export (working implementation) ---------------------------------

async function exportData(format) {
    const div = document.getElementById('executionResults');
    const table = div ? div.querySelector('.data-table') : null;
    if (!table) { showMessage('No data to export', 'error'); return; }

    // Extract data from the rendered table
    const headers = [...table.querySelectorAll('th')].map(th => th.textContent);
    const rows = [...table.querySelectorAll('tbody tr')].map(tr =>
        [...tr.querySelectorAll('td')].reduce((obj, td, i) => { obj[headers[i]] = td.textContent; return obj; }, {})
    );
    if (!rows.length) { showMessage('No data to export', 'error'); return; }

    try {
        const resp = await apiPost('/api/export', { data: rows, format, filename: 'query_results' });
        if (!resp.ok) { const err = await resp.json(); throw new Error(err.error || 'Export failed'); }
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const ext = { csv: 'csv', excel: 'xlsx', json: 'json' }[format] || 'txt';
        a.href = url; a.download = `query_results.${ext}`; document.body.appendChild(a); a.click(); a.remove();
        URL.revokeObjectURL(url);
        showMessage(`Exported as ${format.toUpperCase()}!`, 'success');
    } catch (e) { showMessage('Export error: ' + e.message, 'error'); }
}

// ---- Misc ------------------------------------------------------------

function editSQL() {
    const s = prompt('Edit SQL Query:', generatedSQL);
    if (s && s.trim()) { generatedSQL = s.trim(); document.getElementById('generatedSQL').textContent = generatedSQL; showMessage('SQL updated!', 'success'); }
}

function startOver() {
    if (isRecording && recognition) recognition.stop();
    for (let i = 1; i <= 5; i++) updateStepStatus(i, i === 1 ? 'active' : 'inactive');
    document.getElementById('naturalQuery').value = '';
    document.getElementById('similarityResults').innerHTML = '';
    document.getElementById('similarityActions').style.display = 'none';
    document.getElementById('llmChoiceContainer').style.display = 'none';
    document.getElementById('generatedSQL').textContent = '';
    document.getElementById('sqlActions').style.display = 'none';
    document.getElementById('executionResults').innerHTML = '';
    document.getElementById('voiceTranscript').style.display = 'none';
    updateVoiceUI('idle');
    voiceTranscript = '';
    currentStep = 1; selectedLLMType = 'gemini'; selectedModel = 'models/gemini-2.0-flash';
    currentQuery = ''; similarQueries = []; generatedSQL = ''; selectedSimilarIndex = null;
    showMessage('Ready for a new query!', 'info');
}
