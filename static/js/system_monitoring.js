let usageChart, trafficChart;

document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        await loadMonitoringStats();
        await loadMostScanned();
        initUsageChart();
        initTrafficChart();
        setupMonitoringListeners();
    } catch (e) { console.error('Monitoring error:', e); }
    finally { Spinner.hide(); }
});

async function loadMonitoringStats() {
    try {
        const r = await fetch('/api/core/monitoring-summary/');
        if (r.ok) {
            const s = await r.json();
            DOM.setText(DOM.byId('activeUsersToday'), s.active_users_today?.toString() || '0');
            DOM.setText(DOM.byId('totalScans'), s.total_scans?.toString() || '0');
            DOM.setText(DOM.byId('locationsScanned'), s.locations_scanned_today?.toString() || '0');
            DOM.setText(DOM.byId('apiCallsToday'), s.api_calls_today?.toString() || '0');
            return;
        }
    } catch(_) {}
    ['activeUsersToday','totalScans','locationsScanned','apiCallsToday'].forEach(id => DOM.setText(DOM.byId(id), '0'));
}

async function loadMostScanned() {
    const list = DOM.byId('mostScannedList'); DOM.clear(list);
    try {
        const r = await fetch('/api/core/scan-locations/');
        if (!r.ok) throw new Error('Failed');
        const data = await r.json();
        const locations = data.results || data;
        if (!locations.length) { list.innerHTML = '<div class="empty-state"><i class="fas fa-map-marker-alt"></i><h3>No data yet</h3></div>'; return; }
        const maxCount = Math.max(...locations.map(l => l.scan_count), 1);
        locations.forEach((loc, i) => {
            const pct = Math.round((loc.scan_count / maxCount) * 100);
            const item = DOM.create('div', { className: 'scan-location-item' });
            item.innerHTML = `<span class="scan-location-rank">#${i+1}</span><div class="scan-location-info"><span class="scan-location-name">${loc.location_name}</span><div class="scan-location-bar"><div class="scan-location-fill" style="width:${pct}%"></div></div></div><span class="scan-location-count">${loc.scan_count}</span>`;
            DOM.append(list, item);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state"><i class="fas fa-map-marker-alt"></i><h3>No scan data yet</h3></div>';
    }
}

function initUsageChart() {
    const ctx = DOM.byId('usageChart')?.getContext('2d');
    if (!ctx) return;
    if (usageChart) usageChart.destroy();
    usageChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels:['Network Scans','Coverage Views','Analytics','Reports','Other'], datasets:[{ data:[45,25,18,8,4], backgroundColor:['#06b6d4','#10b981','#8b5cf6','#f59e0b','#94a3b8'] }] },
        options: { ...ChartConfig.getDefaultOptions(), plugins: { legend: { position:'bottom' } } }
    });
}

function initTrafficChart() {
    const ctx = DOM.byId('trafficChart')?.getContext('2d');
    if (!ctx) return;
    if (trafficChart) trafficChart.destroy();
    const days = Array.from({length:30}, (_,i) => `Day ${i+1}`);
    const data = Array.from({length:30}, () => Math.floor(Math.random()*200)+50);
    trafficChart = new Chart(ctx, {
        type: 'line',
        data: { labels: days, datasets: [{ label:'API Requests', data, borderColor:'#06b6d4', backgroundColor:'rgba(6,182,212,0.1)', fill:true, tension:0.3 }] },
        options: { ...ChartConfig.getDefaultOptions(), plugins: { legend: { display:false } }, scales: { y: { beginAtZero:true } } }
    });
}

function setupMonitoringListeners() {
    DOM.byId('trafficPeriod')?.addEventListener('change', () => { Toast.info('Traffic period updated'); initTrafficChart(); });
}
