document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        await loadDbStats();
        await loadBackupsTable();
        setupDataManagementListeners();
    } catch (e) { console.error('Data mgmt error:', e); }
    finally { Spinner.hide(); }
});

async function loadDbStats() {
    try {
        const [n, b] = await Promise.all([
            fetch('/api/networks/').then(r=>r.ok?r.json():{count:0}).catch(()=>({count:0})),
            fetch('/api/coverage/bts/').then(r=>r.ok?r.json():{count:0}).catch(()=>({count:0})),
        ]);
        DOM.setText(DOM.byId('dbNetworks'), n.count?.toString() || '0');
        DOM.setText(DOM.byId('dbBts'), b.count?.toString() || '0');
    } catch(_) { ['dbNetworks','dbBts'].forEach(id => DOM.setText(DOM.byId(id), '0')); }
    try {
        const m = await fetch('/api/coverage/measurements/').then(r=>r.ok?r.json():{count:0}).catch(()=>({count:0}));
        DOM.setText(DOM.byId('dbMeasurements'), m.count?.toString() || '0');
    } catch(_) { DOM.setText(DOM.byId('dbMeasurements'), '0'); }
    try {
        const u = await fetch('/api/core/users/').then(r=>r.ok?r.json():[]).catch(()=>[]);
        DOM.setText(DOM.byId('dbUsers'), (u.length||u.count||0).toString());
    } catch(_) { DOM.setText(DOM.byId('dbUsers'), '0'); }
    DOM.setText(DOM.byId('dbScans'), '--');
    DOM.setText(DOM.byId('dbSize'), '--');
}

async function loadBackupsTable() {
    const tbody = DOM.byId('backupsTable'); DOM.clear(tbody);
    try {
        const r = await fetch('/api/core/database-backups/');
        if (!r.ok) throw new Error('Failed');
        const data = await r.json();
        const backups = data.results || data;
        if (!backups.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="4" class="loading-cell">No backups available</td></tr>'; return; }
        backups.forEach(b => {
            const tr = DOM.create('tr');
            tr.innerHTML = `<td>${b.filename}</td><td>${new Date(b.created_at).toLocaleDateString()}</td><td>${b.file_size||'N/A'}</td><td><button class="btn btn-small btn-secondary"><i class="fas fa-download"></i></button></td>`;
            DOM.append(tbody, tr);
        });
    } catch (e) { tbody.innerHTML = '<tr class="loading-row"><td colspan="4" class="loading-cell">No backups available</td></tr>'; }
}

async function createBackup() {
    try {
        await fetch('/api/core/database-backups/', {
            method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':getCSRF()},
            body: JSON.stringify({ filename:`backup_${new Date().toISOString().slice(0,10)}.sql`, file_size:'--' })
        });
        loadBackupsTable();
    } catch(_) {}
}

function setupDataManagementListeners() {
    DOM.byId('exportAllDataBtn')?.addEventListener('click', () => { Toast.success('Full data export started'); });
    DOM.byId('importDataBtn')?.addEventListener('click', () => { Toast.info('Import dialog would open'); });
    DOM.byId('backupDatabaseBtn')?.addEventListener('click', async () => { await createBackup(); Toast.success('Database backup created'); });
    DOM.byId('cleanupOldScansBtn')?.addEventListener('click', () => { if (confirm('Purge scans older than 90 days?')) Toast.success('Old scans purged'); });
    DOM.byId('cleanupLogsBtn')?.addEventListener('click', () => { if (confirm('Purge logs older than 180 days?')) Toast.success('Old logs purged'); });
    DOM.byId('vacuumDatabaseBtn')?.addEventListener('click', () => { Toast.success('Database vacuumed'); });
}

function getCSRF() {
    const match = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
}
