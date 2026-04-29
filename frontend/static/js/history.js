/* ==========================================================
   history.js – Query history with localStorage persistence
   ========================================================== */

const HISTORY_KEY = 'text2sql_history';
const MAX_HISTORY = 50;

function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
    catch { return []; }
}

function saveHistory(entries) {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(entries.slice(0, MAX_HISTORY)));
}

function addToHistory(natural, sql, rowCount, executionTime) {
    const entries = getHistory();
    entries.unshift({
        natural,
        sql,
        rowCount,
        executionTime,
        timestamp: new Date().toISOString(),
    });
    saveHistory(entries);
    renderHistoryPanel();
}

function clearHistory() {
    if (!confirm('Clear all query history?')) return;
    localStorage.removeItem(HISTORY_KEY);
    renderHistoryPanel();
    showMessage('History cleared.', 'info');
}

function renderHistoryPanel() {
    const panel = document.getElementById('historyPanel');
    if (!panel) return;

    const entries = getHistory();
    if (!entries.length) {
        panel.innerHTML = '<p class="history-empty">No recent queries.</p>';
        return;
    }

    let html = '<div class="history-list">';
    entries.slice(0, 10).forEach((e, i) => {
        const ts = new Date(e.timestamp).toLocaleTimeString();
        html += `<div class="history-item" onclick="replayHistory(${i})" title="${e.sql}">
            <span class="history-query">${e.natural}</span>
            <span class="history-meta">${ts} · ${e.rowCount ?? '?'} rows · ${e.executionTime ?? '?'}s</span>
        </div>`;
    });
    html += '</div>';
    if (entries.length > 0) html += '<button class="btn-link" onclick="clearHistory()">Clear History</button>';
    panel.innerHTML = html;
}

function replayHistory(index) {
    const entries = getHistory();
    const e = entries[index];
    if (!e) return;
    document.getElementById('naturalQuery').value = e.natural;
    showMessage('Query loaded from history. Click "Check Similarity" to proceed.', 'info');
}

// Auto-render on load
document.addEventListener('DOMContentLoaded', renderHistoryPanel);
