/* API Integration for GeoSignal */

const API_BASE_URL = '/api';

class GeoSignalAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    getCSRFToken() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el?.value) return el.value;
        const match = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return match ? match.pop() : '';
    }

    // ========== Networks API ==========

    async getNetworkProviders(params = {}) {
        return this.request('/networks/providers/' + this.buildQueryString(params));
    }

    async getNetworkTypes(params = {}) {
        return this.request('/networks/types/' + this.buildQueryString(params));
    }

    async getAvailableTypes() {
        return this.request('/networks/types/available_types/');
    }

    async getAvailableNetworks(params = {}) {
        return this.request('/networks/available/' + this.buildQueryString(params));
    }

    async getNetworksNearby(latitude, longitude, radius = 5) {
        return this.request(`/networks/available/by_location/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`);
    }

    async getBestNetwork(latitude, longitude) {
        return this.request(`/networks/available/best_network/?latitude=${latitude}&longitude=${longitude}`);
    }

    async getNetworkStats() {
        return this.request('/networks/available/stats/');
    }

    async createAvailableNetwork(data) {
        return this.request('/networks/available/', 'POST', data);
    }

    // ========== Coverage API ==========

    async getBTSLocations(params = {}) {
        return this.request('/coverage/bts/' + this.buildQueryString(params));
    }

    async getNearbyBTS(latitude, longitude, radius = 10) {
        return this.request(`/coverage/bts/nearby/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`);
    }

    async getCoverageAreas(params = {}) {
        return this.request('/coverage/coverage-areas/' + this.buildQueryString(params));
    }

    async getSignalMeasurements(params = {}) {
        return this.request('/coverage/measurements/' + this.buildQueryString(params));
    }

    async getMeasurementsByLocation(latitude, longitude, radius = 1) {
        return this.request(`/coverage/measurements/by_location/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`);
    }

    async getSignalStats(latitude, longitude, radius = 5) {
        return this.request(`/coverage/measurements/signal_stats/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`);
    }

    async getStabilityReport() {
        return this.request('/coverage/measurements/stability_report/');
    }

    async createSignalMeasurement(data) {
        return this.request('/coverage/measurements/', 'POST', data);
    }

    // ========== Simulation API ==========

    async getSimulatedBTS(params = {}) {
        return this.request('/coverage/sim-bts/' + this.buildQueryString(params));
    }

    async createSimulation(data) {
        return this.request('/coverage/sim-bts/simulate/', 'POST', data);
    }

    async clearSimulated() {
        return this.request('/coverage/sim-bts/clear_simulated/');
    }

    // ========== Analytics API ==========

    async getCoverageAnalysis(params = {}) {
        return this.request('/analytics/coverage/' + this.buildQueryString(params));
    }

    async getRegionalSummary() {
        return this.request('/analytics/coverage/regional_summary/');
    }

    async getCongestionMap() {
        return this.request('/analytics/coverage/congestion_map/');
    }

    async detectCongestion(params = {}) {
        let qs = this.buildQueryString(params);
        return this.request('/analytics/coverage/detect_congestion/' + qs);
    }

    async getNetworkComparisons(params = {}) {
        return this.request('/analytics/comparisons/' + this.buildQueryString(params));
    }

    async getComparisonSummary(provider1, provider2) {
        return this.request(`/analytics/comparisons/comparison_summary/?provider1=${provider1}&provider2=${provider2}`);
    }

    async getDailyMetrics(params = {}) {
        return this.request('/analytics/daily-metrics/' + this.buildQueryString(params));
    }

    async getMetricsTrend(provider, networkType, days = 30) {
        return this.request(`/analytics/daily-metrics/trend/?provider=${provider}&network_type=${networkType}&days=${days}`);
    }

    async getPerformanceReport() {
        return this.request('/analytics/daily-metrics/performance_report/');
    }

    // ========== Utility Methods ==========

    buildQueryString(params) {
        const query = new URLSearchParams(params);
        const queryString = query.toString();
        return queryString ? `?${queryString}` : '';
    }

    async getPaginatedData(endpoint, params = {}, allResults = false) {
        const results = [];
        let nextUrl = `${this.baseURL}${endpoint}${this.buildQueryString(params)}`;

        while (nextUrl) {
            try {
                const response = await fetch(nextUrl, {
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                    }
                });
                const data = await response.json();

                if (data.results) {
                    results.push(...data.results);
                    nextUrl = data.next;
                } else {
                    results.push(...(Array.isArray(data) ? data : [data]));
                    break;
                }

                if (!allResults) break;
            } catch (error) {
                console.error('Pagination Error:', error);
                break;
            }
        }

        return results;
    }
}

const api = new GeoSignalAPI();
