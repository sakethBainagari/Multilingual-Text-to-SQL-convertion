/* ==========================================================
   database.js – Database management (modal, upload, switch)
   ========================================================== */

let currentDatabase = null;
let uploadedDatabases = [];

function initializeDatabaseFeature() {
    loadCurrentDatabase();

    document.getElementById('dbFileInput').addEventListener('change', handleFileSelect);

    const zone = document.getElementById('dbUploadZone');
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', (e) => { e.preventDefault(); zone.classList.remove('dragover'); });
    zone.addEventListener('drop', (e) => {
        e.preventDefault(); zone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });

    document.getElementById('dbModal').addEventListener('click', (e) => {
        if (e.target.id === 'dbModal') closeDbModal();
    });
}

async function loadCurrentDatabase() {
    try {
        const resp = await apiGet('/api/db/current');
        const result = await resp.json();
        if (result.success) {
            currentDatabase = result.current_db;
            uploadedDatabases = result.uploaded_databases;
            document.getElementById('dbCurrentName').textContent = currentDatabase.name;
            document.getElementById('dbCurrentTables').textContent = `(${currentDatabase.table_count} tables)`;
            renderDatabaseList();
        }
    } catch (e) {
        console.error('Error loading DB info:', e);
        document.getElementById('dbCurrentTables').textContent = '(Error)';
    }
}

function openDbModal()  { document.getElementById('dbModal').classList.add('active'); loadCurrentDatabase(); }
function closeDbModal() { document.getElementById('dbModal').classList.remove('active'); }

function handleFileSelect(e) { if (e.target.files[0]) handleFileUpload(e.target.files[0]); }

async function handleFileUpload(file) {
    const valid = ['.db', '.sqlite', '.sqlite3'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!valid.includes(ext)) { showMessage('Invalid file type.', 'error'); return; }

    const prog = document.getElementById('dbUploadProgress');
    const fill = document.getElementById('dbProgressFill');
    const status = document.getElementById('dbUploadStatus');
    prog.classList.add('active'); status.textContent = `Uploading ${file.name}...`; fill.style.width = '30%';

    try {
        const fd = new FormData(); fd.append('file', file);
        fill.style.width = '60%';
        const resp = await apiFetch(`${API_BASE}/api/db/upload`, { method: 'POST', body: fd });
        fill.style.width = '90%';
        const result = await resp.json();
        fill.style.width = '100%';

        if (result.success) {
            status.textContent = 'Uploaded!';
            currentDatabase = result.database;
            document.getElementById('dbCurrentName').textContent = currentDatabase.name;
            document.getElementById('dbCurrentTables').textContent = `(${currentDatabase.table_count} tables)`;
            await loadCurrentDatabase();
            showMessage(`"${result.database.name}" uploaded. Tables: ${result.database.tables.join(', ')}`, 'success');
            setTimeout(() => { closeDbModal(); prog.classList.remove('active'); fill.style.width = '0%'; }, 1500);
        } else { throw new Error(result.error || 'Upload failed'); }
    } catch (e) {
        status.textContent = `Failed: ${e.message}`; fill.style.width = '0%';
        showMessage(`Upload failed: ${e.message}`, 'error');
        setTimeout(() => prog.classList.remove('active'), 3000);
    }
    document.getElementById('dbFileInput').value = '';
}

function renderDatabaseList() {
    const list = document.getElementById('dbList');
    let html = '';
    const isDefault = currentDatabase && currentDatabase.name === 'Default Database';
    html += `<div class="db-item ${isDefault ? 'active' : ''}">
        <div class="db-item-info"><span class="db-item-icon">🏠</span>
            <div class="db-item-details"><span class="db-item-name">Default Database</span><span class="db-item-meta">Built-in sample</span></div>
        </div><div class="db-item-actions">${!isDefault ? '<button class="db-item-btn use" onclick="switchDatabase(\'default\')">Use</button>' : '<span style="color:#4caf50;font-weight:bold">✓ Active</span>'}</div></div>`;

    uploadedDatabases.forEach(db => {
        const active = currentDatabase && currentDatabase.path === db.path;
        const kb = (db.size / 1024).toFixed(1);
        html += `<div class="db-item ${active ? 'active' : ''}">
            <div class="db-item-info"><span class="db-item-icon">📁</span>
                <div class="db-item-details"><span class="db-item-name">${db.name}</span><span class="db-item-meta">${kb} KB</span></div>
            </div><div class="db-item-actions">${!active ? `<button class="db-item-btn use" onclick="switchDatabase('${db.path}')">Use</button>` : '<span style="color:#4caf50;font-weight:bold">✓ Active</span>'}
            <button class="db-item-btn delete" onclick="deleteDatabase('${db.path}','${db.name}')">Delete</button></div></div>`;
    });

    if (!uploadedDatabases.length) {
        html += '<div style="text-align:center;padding:20px;color:#666"><p>No uploaded databases.</p></div>';
    }
    list.innerHTML = html;
}

async function switchDatabase(path) {
    try {
        const resp = await apiPost('/api/db/switch', { path });
        const result = await resp.json();
        if (result.success) {
            currentDatabase = result.database;
            document.getElementById('dbCurrentName').textContent = currentDatabase.name;
            document.getElementById('dbCurrentTables').textContent = `(${currentDatabase.table_count} tables)`;
            await loadCurrentDatabase();
            showMessage(`Switched to "${result.database.name}". Tables: ${result.database.tables.join(', ')}`, 'success');
            startOver(); closeDbModal();
        } else { throw new Error(result.error); }
    } catch (e) { showMessage(`Switch failed: ${e.message}`, 'error'); }
}

async function deleteDatabase(path, name) {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
    try {
        const resp = await apiPost('/api/db/delete', { path });
        const result = await resp.json();
        if (result.success) { showMessage(`"${name}" deleted`, 'info'); await loadCurrentDatabase(); }
        else { throw new Error(result.error); }
    } catch (e) { showMessage(`Delete failed: ${e.message}`, 'error'); }
}

async function connectByPath() {
    const input = document.getElementById('dbPathInput');
    const dbPath = input.value.trim();
    if (!dbPath) { showMessage('Enter a file path', 'error'); return; }
    showMessage('Connecting...', 'info');
    try {
        const resp = await apiPost('/api/db/connect-path', { path: dbPath });
        const result = await resp.json();
        if (result.success) {
            currentDatabase = result.database;
            document.getElementById('dbCurrentName').textContent = currentDatabase.name;
            document.getElementById('dbCurrentTables').textContent = `(${currentDatabase.table_count} tables)`;
            showMessage(`✅ Connected to "${result.database.name}"!`, 'success');
            input.value = ''; startOver(); closeDbModal();
        } else { throw new Error(result.error); }
    } catch (e) { showMessage(`Connect failed: ${e.message}`, 'error'); }
}

/* ==========================================================
   Schema Viewer – Floating panel
   ========================================================== */

let schemaOpen = false;

function toggleSchemaPanel() {
    const panel = document.getElementById('schemaPanel');
    const fab = document.getElementById('schemaFab');
    schemaOpen = !schemaOpen;

    if (schemaOpen) {
        panel.classList.add('active');
        fab.classList.add('active');
        loadSchema();
    } else {
        panel.classList.remove('active');
        fab.classList.remove('active');
    }
}

async function loadSchema() {
    const body = document.getElementById('schemaPanelBody');
    body.innerHTML = '<div class="schema-loading">Loading schema...</div>';

    try {
        const resp = await apiGet('/api/db/schema');
        const result = await resp.json();

        if (!result.success) {
            body.innerHTML = `<div class="schema-error">❌ ${result.error}</div>`;
            return;
        }

        let html = `
            <div class="schema-db-info">
                <strong>🗄️ ${result.database}</strong>
                ${result.table_count} table(s)
            </div>
        `;

        if (result.tables.length === 0) {
            html += '<div class="schema-error">No tables found in this database.</div>';
        }

        result.tables.forEach((table, idx) => {
            html += `
                <div class="schema-table" id="schemaTable${idx}">
                    <div class="schema-table-header" onclick="toggleSchemaTable(${idx})">
                        <span class="schema-table-name">${table.name}</span>
                        <span class="schema-table-meta">
                            <span class="row-count">${table.row_count} rows</span>
                            <span class="toggle-icon">▼</span>
                        </span>
                    </div>
                    <div class="schema-table-columns">
            `;

            table.columns.forEach(col => {
                let badges = '';
                if (col.primary_key) badges += '<span class="schema-col-pk">PK</span>';
                if (col.not_null) badges += '<span class="schema-col-nn">NN</span>';

                html += `
                    <div class="schema-col">
                        <span class="schema-col-icon">${col.primary_key ? '🔑' : '•'}</span>
                        <span class="schema-col-name">${col.name}</span>
                        <span class="schema-col-type">${col.type || 'TEXT'}</span>
                        ${badges}
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        body.innerHTML = html;

        // Auto-expand first table
        if (result.tables.length > 0) {
            toggleSchemaTable(0);
        }

    } catch (e) {
        body.innerHTML = `<div class="schema-error">❌ Failed to load schema: ${e.message}</div>`;
    }
}

function toggleSchemaTable(idx) {
    const el = document.getElementById(`schemaTable${idx}`);
    if (el) el.classList.toggle('expanded');
}
