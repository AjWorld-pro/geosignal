/* Main Page - Search location, see all network data */

let mainMap;

document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        mainMap = initializeMap('map', DEFAULT_LOCATION.latitude, DEFAULT_LOCATION.longitude, DEFAULT_LOCATION.zoom);
        await loadBTSMarkers();
        setupListeners();
    } catch (e) { Toast.error('Error: ' + e.message); }
    finally { Spinner.hide(); }
});

async function loadBTSMarkers() {
    try {
        const r = await api.getBTSLocations({ status: 'active' });
        (r.results || r).forEach(b => addMarker(mainMap, b.latitude, b.longitude, `${b.name} (${b.provider_name || b.provider})`, '#059669'));
    } catch (e) { console.error(e); }
}

async function searchLocation(query) {
    if (!query || query.trim().length < 2) { Toast.error('Enter a location'); return; }
    const container = DOM.byId('locationResults');
    DOM.setHTML(container, '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i><p>Searching this location...</p></div>');
    container.style.display = 'block';
    const welcome = DOM.byId('welcomeCard'); if (welcome) welcome.style.display = 'none';
    let lat, lon, display_name;
    try {
        const match = query.trim().match(/^(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)$/);
        if (match) {
            [lat, lon] = [match[1], match[2]];
            const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10`);
            const d = r.ok ? await r.json() : {};
            display_name = d.display_name || `Location (${lat}, ${lon})`;
        } else {
            const r = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`);
            if (!r.ok) throw new Error('Geocoding failed');
            const data = await r.json();
            if (!data || !data.length) { DOM.setHTML(container, '<div class="alert alert-error">Location not found</div>'); return; }
            [lat, lon, display_name] = [data[0].lat, data[0].lon, data[0].display_name];
        }

        const [networkResult, congestion, signalStats, nearbyBTS] = await Promise.all([
            api.getBestNetwork(lat, lon),
            api.detectCongestion({ latitude: lat, longitude: lon, radius: 5 }),
            api.getSignalStats(lat, lon, 5),
            api.getNearbyBTS(lat, lon, 10),
        ]);

        if (mainMap) {
            mainMap.setView([lat, lon], 10);
            mainMap.eachLayer(l => l instanceof L.CircleMarker && l.remove());
            const btsList = nearbyBTS.results || nearbyBTS;
            btsList.forEach(b => addMarker(mainMap, b.latitude, b.longitude, `${b.name} (${b.provider_name || b.provider})`, '#06b6d4'));
        }

        const qualityLabels = { excellent:'Excellent', good:'Good', fair:'Fair', poor:'Poor' };
        const levelColors = { low:'badge-success', moderate:'badge-warning', high:'badge-danger', severe:'badge-danger' };
        const sig = v => v ? v.toFixed(1) + ' dBm' : 'N/A';

        let html = `<div class="location-results-card"><h3><i class="fas fa-map-pin"></i> ${display_name}</h3>`;

        // Networks section
        html += '<h4 style="margin-top:16px;margin-bottom:10px">Available Networks</h4>';
        if (networkResult.top_networks && networkResult.top_networks.length) {
            html += '<div class="network-result-grid">';
            networkResult.top_networks.forEach(n => {
                html += `<div class="network-result-item">
                    <div class="provider-name"><i class="fas fa-signal"></i> ${n.provider_name || n.provider}</div>
                    <div class="detail-row"><span class="label">Network</span><span class="value">${n.network_type_display || n.network_type}</span></div>
                    <div class="detail-row"><span class="label">Signal</span><span class="value">${n.signal_strength} dBm</span></div>
                    <div class="detail-row"><span class="label">Speed</span><span class="value">${n.max_speed || 'N/A'}</span></div>
                    <div class="detail-row"><span class="label">Frequency</span><span class="value">${n.frequency_band || 'N/A'}</span></div>
                    <div class="detail-row"><span class="label">Quality</span><span class="value">${qualityLabels[n.signal_quality] || n.signal_quality}</span></div>
                    <div class="detail-row"><span class="label">Status</span><span class="value">${n.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}</span></div>
                </div>`;
            });
            html += '</div>';
        } else html += '<p>No networks found at this location.</p>';

        // Nearest BTS
        if (networkResult.nearest_bts) {
            html += `<p style="margin-top:14px;font-size:0.875rem;color:var(--slate-600)"><i class="fas fa-tower-cell"></i> <strong>Nearest BTS:</strong> ${networkResult.nearest_bts.name} — ${networkResult.nearest_bts.distance_km} km away</p>`;
        }

        // Signal Stats + Congestion in a 2-col grid
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px">';

        // Signal Stats
        html += '<div style="background:var(--slate-50);border-radius:var(--radius-sm);padding:14px;border:1px solid var(--slate-200)">';
        html += '<strong style="font-size:0.813rem;color:var(--slate-600)">Signal Performance</strong>';
        if (signalStats && signalStats.count) {
            html += `<div class="detail-row" style="margin-top:8px"><span class="label">Average</span><span class="value">${sig(signalStats.avg_signal)}</span></div>
                <div class="detail-row"><span class="label">Max</span><span class="value">${sig(signalStats.max_signal)}</span></div>
                <div class="detail-row"><span class="label">Min</span><span class="value">${sig(signalStats.min_signal)}</span></div>
                <div class="detail-row"><span class="label">Variance</span><span class="value">${signalStats.avg_variance ? signalStats.avg_variance.toFixed(1) : 'N/A'}</span></div>
                <div class="detail-row"><span class="label">Jitter</span><span class="value">${signalStats.avg_jitter ? signalStats.avg_jitter.toFixed(1) + ' ms' : 'N/A'}</span></div>
                <div class="detail-row"><span class="label">Samples</span><span class="value">${signalStats.count}</span></div>`;
        } else html += '<p style="font-size:0.813rem;color:var(--slate-400);margin-top:8px">No data</p>';
        html += '</div>';

        // Congestion
        html += '<div style="background:var(--slate-50);border-radius:var(--radius-sm);padding:14px;border:1px solid var(--slate-200)">';
        html += '<strong style="font-size:0.813rem;color:var(--slate-600)">Congestion</strong>';
        if (congestion && congestion.congestion_score !== undefined) {
            html += `<div class="detail-row" style="margin-top:8px"><span class="label">Score</span><span class="value" style="font-weight:700">${congestion.congestion_score}/100</span></div>
                <div class="detail-row"><span class="label">Level</span><span class="value"><span class="badge ${levelColors[congestion.congestion_level] || 'badge-info'}">${congestion.congestion_level}</span></span></div>
                <div class="detail-row"><span class="label">BTS Towers</span><span class="value">${congestion.total_bts}</span></div>
                <div class="detail-row"><span class="label">Networks</span><span class="value">${congestion.total_networks}</span></div>
                <div class="detail-row"><span class="label" style="white-space:normal">Assessment</span><span class="value">${congestion.assessment || 'N/A'}</span></div>`;
        } else html += '<p style="font-size:0.813rem;color:var(--slate-400);margin-top:8px">No data</p>';
        html += '</div></div>';

        // Recommendation
        if (networkResult.recommendation) {
            html += `<p class="recommendation" style="margin-top:14px"><i class="fas fa-info-circle"></i> ${networkResult.recommendation}</p>`;
        }

        html += '</div>';
        DOM.setHTML(container, html);
    } catch (e) { DOM.setHTML(container, `<div class="alert alert-error">Error: ${e.message}</div>`); }
}

function setupListeners() {
    const input = DOM.byId('locationSearch'), btn = DOM.byId('searchBtn'), geo = DOM.byId('geolocateBtn');
    if (btn && input) {
        btn.addEventListener('click', () => searchLocation(input.value));
        input.addEventListener('keydown', e => { if (e.key === 'Enter') searchLocation(input.value); });
    }
    if (geo) geo.addEventListener('click', async () => {
        try { const p = await Geolocation.getCurrentPosition(); searchLocation(`${p.latitude},${p.longitude}`); }
        catch (e) { Toast.error('Location denied'); }
    });
}
