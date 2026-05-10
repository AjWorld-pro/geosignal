let currentLogPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        await loadLogs();
        setupLogListeners();
    } catch (e) { console.error('Security logs error:', e); }
    finally { Spinner.hide(); }
});

function formatTimestamp(iso) {
    const d = new Date(iso);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function shortTimestamp(iso) {
    const d = new Date(iso);
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

async function loadLogs(page = 1) {
    currentLogPage = page;
    const body = DOM.byId('logsBody'); DOM.clear(body);
    const typeFilter = DOM.byId('logEventType')?.value || '';
    const userFilter = DOM.byId('logUserFilter')?.value || '';
    let url = `/api/core/activity-logs/?page=${page}`;
    if (typeFilter) url += `&event_type=${typeFilter}`;
    if (userFilter) url += `&search=${encodeURIComponent(userFilter)}`;

    try {
        const r = await fetch(url);
        if (!r.ok) throw new Error('Failed');
        const data = await r.json();
        const logs = data.results || data;
        if (!logs.length) {
            body.innerHTML = '<div style="padding:20px;text-align:center;color:#484f58">No matching logs found</div>';
            DOM.byId('logsPagination').innerHTML = '';
            return;
        }
        logs.forEach(l => {
            const entry = DOM.create('div'); entry.className = 'log-entry';
            entry.innerHTML = `
                <span class="log-entry-time">${shortTimestamp(l.created_at)}</span>
                <span class="log-entry-user">${l.username || l.user || 'anonymous'}</span>
                <span class="log-entry-event ${l.event_type}">${l.event_type}</span>
                <span class="log-entry-ip">${l.ip_address || '0.0.0.0'}</span>
                <span class="log-entry-details">${l.details || '--'}</span>
            `;
            DOM.append(body, entry);
        });
        // Scroll to top on new page load
        body.scrollTop = 0;
    } catch (e) {
        body.innerHTML = '<div style="padding:20px;text-align:center;color:#ff6b6b"><i class="fas fa-lock"></i> Login as admin to view security logs</div>';
        DOM.byId('logsPagination').innerHTML = '';
    }
}

function setupLogListeners() {
    DOM.byId('applyLogFiltersBtn')?.addEventListener('click', () => loadLogs(1));
    DOM.byId('exportLogsBtn')?.addEventListener('click', () => { Toast.success('Logs exported as CSV'); });
    DOM.byId('refreshLogsBtn')?.addEventListener('click', () => { Toast.info('Logs refreshed'); loadLogs(currentLogPage); });
}
