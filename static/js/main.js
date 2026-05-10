/* Main JavaScript - Global Functionality */

const DEFAULT_LOCATION = { latitude: 52.52, longitude: 13.405, zoom: 12 };

document.addEventListener('DOMContentLoaded', () => {
    initializeSidebar();
    initializeGlobalListeners();
    console.log('Geosginal frontend loaded');
});

function initializeSidebar() {
    const toggleMobile = document.getElementById('sidebarToggleMobile');
    const toggleDesktop = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function openSidebar() {
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('active');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
    }

    if (toggleMobile) {
        toggleMobile.addEventListener('click', openSidebar);
    }

    if (toggleDesktop) {
        toggleDesktop.addEventListener('click', closeSidebar);
    }

    // Close sidebar when clicking overlay
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar on nav link click (mobile)
    const sidebarLinks = document.querySelectorAll('.sidebar .sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar?.classList.contains('open')) {
            closeSidebar();
        }
    });
}

// Global Event Listeners
function initializeGlobalListeners() {
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
    });

    // Keyboard shortcut: Ctrl+F to focus search
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'f') {
            const search = document.querySelector('.search-input');
            if (search) {
                e.preventDefault();
                search.focus();
            }
        }
    });
}

// Search functionality
function setupSearch(searchInputId, dataFunction, renderFunction) {
    const input = DOM.byId(searchInputId);
    if (!input) return;

    const handleSearch = debounce(async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2 && query.length > 0) return;

        Spinner.show();
        try {
            const results = await dataFunction(query);
            renderFunction(results);
        } catch (error) {
            Toast.error('Search failed: ' + error.message);
        } finally {
            Spinner.hide();
        }
    }, 300);

    input.addEventListener('input', handleSearch);
}

// Filter functionality
function setupFilters(filterButtonId, resetButtonId, filterFunction) {
    const applyBtn = DOM.byId(filterButtonId);
    const resetBtn = DOM.byId(resetButtonId);

    if (applyBtn) {
        applyBtn.addEventListener('click', async () => {
            Spinner.show();
            try {
                await filterFunction();
                Toast.success('Filters applied');
            } catch (error) {
                Toast.error('Filter error: ' + error.message);
            } finally {
                Spinner.hide();
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            document.querySelectorAll('.filter-panel select, .filter-panel input').forEach(el => {
                el.value = '';
            });
            Toast.info('Filters reset');
        });
    }
}

// Pagination helper
function createPagination(container, currentPage, totalPages, onPageChange) {
    DOM.clear(container);

    if (totalPages <= 1) return;

    const pagination = DOM.create('div', { className: 'pagination' });

    // Previous button
    if (currentPage > 1) {
        const prevBtn = DOM.create('button', {}, '← Previous');
        prevBtn.addEventListener('click', () => onPageChange(currentPage - 1));
        DOM.append(pagination, prevBtn);
    }

    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    if (startPage > 1) {
        const btn = DOM.create('button', {}, '1');
        btn.addEventListener('click', () => onPageChange(1));
        DOM.append(pagination, btn);

        if (startPage > 2) {
            DOM.append(pagination, DOM.create('span', {}, '...'));
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const btn = DOM.create('button', {}, String(i));
        if (i === currentPage) btn.classList.add('active');
        btn.addEventListener('click', () => onPageChange(i));
        DOM.append(pagination, btn);
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            DOM.append(pagination, DOM.create('span', {}, '...'));
        }

        const btn = DOM.create('button', {}, String(totalPages));
        btn.addEventListener('click', () => onPageChange(totalPages));
        DOM.append(pagination, btn);
    }

    // Next button
    if (currentPage < totalPages) {
        const nextBtn = DOM.create('button', {}, 'Next →');
        nextBtn.addEventListener('click', () => onPageChange(currentPage + 1));
        DOM.append(pagination, nextBtn);
    }

    DOM.append(container, pagination);
}

// Table rendering helper
function renderTable(tableId, data, columns) {
    const tbody = DOM.byId(tableId);
    if (!tbody) return;

    DOM.clear(tbody);

    if (!data || data.length === 0) {
        const row = DOM.create('tr', { className: 'loading-row' });
        const cell = DOM.create('td', {
            colSpan: columns.length,
            style: 'text-align: center; padding: 40px;'
        }, 'No data available');
        DOM.append(row, cell);
        DOM.append(tbody, row);
        return;
    }

    data.forEach(item => {
        const row = DOM.create('tr');
        columns.forEach(col => {
            const cell = DOM.create('td');
            const value = typeof col.render === 'function'
                ? col.render(item[col.key], item)
                : item[col.key];
            DOM.setHTML(cell, value);
            DOM.append(row, cell);
        });
        DOM.append(tbody, row);
    });
}

// Map initialization helper
function initializeMap(mapId, latitude = 52.52, longitude = 13.405, zoom = 12) {
    const mapContainer = DOM.byId(mapId);
    if (!mapContainer || !window.L) {
        console.warn(`Map ${mapId} or Leaflet not available`);
        return null;
    }

    const map = L.map(mapId).setView([latitude, longitude], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);

    return map;
}

// Add marker to map
function addMarker(map, latitude, longitude, title, color = '#0891b2') {
    if (!map) return;

    const marker = L.circleMarker([latitude, longitude], {
        radius: 6,
        fillColor: color,
        color: color,
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).bindPopup(title);

    marker.addTo(map);
    return marker;
}

// Export data to CSV
function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        Toast.error('No data to export');
        return;
    }

    const headers = Object.keys(data[0]);
    const csv = [headers.join(',')];

    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return `"${String(value || '').replace(/"/g, '""')}"`;
        });
        csv.push(values.join(','));
    });

    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = DOM.create('a', { href: url, download: filename });
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    Toast.success('Data exported successfully');
}

// Status check
async function checkAPIStatus() {
    try {
        const response = await fetch('/api/status/');
        return await response.json();
    } catch (error) {
        console.error('API status check failed:', error);
        return null;
    }
}

// Initialize on page load
window.addEventListener('load', async () => {
    const status = await checkAPIStatus();
    if (status) {
        console.log('API Status:', status);
    }
});
