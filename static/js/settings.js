document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        await loadUserSettings();
        await loadApiStatus();
        setupSettingsListeners();
    } catch (e) { console.error('Settings error:', e); }
    finally { Spinner.hide(); }
});

async function loadUserSettings() {
    try {
        const r = await fetch('/api/core/user-settings/');
        if (!r.ok) throw new Error('Failed');
        const s = await r.json();
        if (DOM.byId('defaultLat')) DOM.byId('defaultLat').value = s.default_map_center_lat;
        if (DOM.byId('defaultLon')) DOM.byId('defaultLon').value = s.default_map_center_lon;
        if (DOM.byId('defaultZoom')) DOM.byId('defaultZoom').value = s.default_zoom;
        document.querySelectorAll('.theme-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.theme === s.theme);
        });
    } catch(e) { /* use defaults */ }
}

async function loadApiStatus() {
    const list = DOM.byId('apiStatusList'); DOM.clear(list);
    const endpoints = [
        { name:'Networks API', url:'/api/networks/' },
        { name:'Coverage API', url:'/api/coverage/' },
        { name:'Analytics API', url:'/api/analytics/' },
        { name:'Core API', url:'/api/core/' },
        { name:'Database', url:'/api/status/' },
    ];
    for (const api of endpoints) {
        let status = 'offline', color = 'var(--danger)';
        try {
            const r = await fetch(api.url, { signal: AbortSignal.timeout(3000) });
            status = r.ok ? 'online' : 'error';
            color = r.ok ? 'var(--success)' : 'var(--warning)';
        } catch (e) { status = 'offline'; color = 'var(--danger)'; }
        const item = DOM.create('div', { className: 'api-status-item' });
        item.innerHTML = `<div class="api-status-name"><span class="status-dot" style="background:${color}"></span><span>${api.name}</span></div><span class="api-status-value" style="color:${color}">${status}</span>`;
        DOM.append(list, item);
    }
}

function setupSettingsListeners() {
    DOM.byId('saveMapCenterBtn')?.addEventListener('click', async () => {
        const lat = parseFloat(DOM.byId('defaultLat')?.value);
        const lon = parseFloat(DOM.byId('defaultLon')?.value);
        const zoom = parseInt(DOM.byId('defaultZoom')?.value) || 10;
        try {
            await fetch('/api/core/user-settings/', {
                method:'PATCH', headers:{'Content-Type':'application/json','X-CSRFToken':getCSRF()},
                body: JSON.stringify({ default_map_center_lat: lat, default_map_center_lon: lon, default_zoom: zoom })
            });
            Toast.success('Map center saved');
        } catch(e) { Toast.error('Failed to save'); }
    });

    DOM.byId('runHealthCheckBtn')?.addEventListener('click', async () => {
        const grid = DOM.byId('healthGrid');
        grid.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i><p>Running health checks...</p></div>';
        try {
            const r = await fetch('/api/core/run-health-check/', { method:'POST', headers:{'X-CSRFToken':getCSRF()} });
            const checks = await r.json();
            grid.innerHTML = '';
            checks.forEach(c => {
                const colors = { passed:'var(--success)', warning:'var(--warning)', failed:'var(--danger)' };
                const item = DOM.create('div', { className: `health-item ${c.status}` });
                item.innerHTML = `<div class="health-name"><span class="status-dot" style="background:${colors[c.status]}"></span><span>${c.check_type}</span></div><span class="health-detail">${c.detail||c.status}</span>`;
                DOM.append(grid, item);
            });
            Toast.success('Health check complete');
        } catch(e) { grid.innerHTML = '<div class="alert alert-error">Health check failed</div>'; }
    });

    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            try {
                await fetch('/api/core/user-settings/', {
                    method:'PATCH', headers:{'Content-Type':'application/json','X-CSRFToken':getCSRF()},
                    body: JSON.stringify({ theme: btn.dataset.theme })
                });
            } catch(_) {}
            Toast.success(`Theme set to ${btn.dataset.theme}`);
        });
    });
}

function getCSRF() {
    const match = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
}
