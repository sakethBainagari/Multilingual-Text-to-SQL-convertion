/* ==========================================================
   api.js – API communication layer with timeout wrapper
   ========================================================== */

const API_BASE = (window.location.port === '5000')
    ? window.location.origin
    : 'http://localhost:5000';

/**
 * Fetch wrapper with configurable timeout (default 60 s).
 */
async function apiFetch(url, options = {}, timeoutMs = 60000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const resp = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(timer);
        return resp;
    } catch (err) {
        clearTimeout(timer);
        if (err.name === 'AbortError') throw new Error('Request timed out');
        throw err;
    }
}

/**
 * POST JSON helper.
 */
async function apiPost(path, body, timeoutMs) {
    return apiFetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    }, timeoutMs);
}

/**
 * GET JSON helper.
 */
async function apiGet(path, timeoutMs) {
    return apiFetch(`${API_BASE}${path}`, {}, timeoutMs);
}
