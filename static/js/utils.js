/* Utility Functions for Geosginal */

// Toast notification system
class Toast {
    static show(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, duration);
    }

    static success(message) {
        this.show(message, 'success');
    }

    static error(message) {
        this.show(message, 'error');
    }

    static info(message) {
        this.show(message, 'info');
    }
}

// Loading spinner
class Spinner {
    static show() {
        document.getElementById('loadingSpinner').classList.add('active');
    }

    static hide() {
        document.getElementById('loadingSpinner').classList.remove('active');
    }
}

// Format functions
const Formatter = {
    formatSignalStrength: (dBm) => {
        if (dBm >= -70) return 'Excellent';
        if (dBm >= -85) return 'Good';
        if (dBm >= -100) return 'Fair';
        return 'Poor';
    },

    formatSignalColor: (dBm) => {
        if (dBm >= -70) return '#27ae60'; // Green
        if (dBm >= -85) return '#3498db'; // Blue
        if (dBm >= -100) return '#f39c12'; // Orange
        return '#e74c3c'; // Red
    },

    formatDate: (dateString) => {
        return new Date(dateString).toLocaleString();
    },

    formatCoordinate: (coord, type) => {
        if (!coord) return 'N/A';
        const rounded = Math.abs(coord).toFixed(4);
        const direction = type === 'lat' ? (coord >= 0 ? 'N' : 'S') : (coord >= 0 ? 'E' : 'W');
        return `${rounded}° ${direction}`;
    },

    formatDistance: (meters) => {
        if (meters < 1000) return `${Math.round(meters)} m`;
        return `${(meters / 1000).toFixed(2)} km`;
    },

    formatPercent: (value) => {
        return `${Math.round(value || 0)}%`;
    },

    formatNumber: (num) => {
        return new Intl.NumberFormat().format(num);
    },

    getSignalQualityBadge: (quality) => {
        const badges = {
            'excellent': '<span class="badge badge-success">Excellent</span>',
            'good': '<span class="badge badge-info">Good</span>',
            'fair': '<span class="badge badge-warning">Fair</span>',
            'poor': '<span class="badge badge-danger">Poor</span>',
            'no_signal': '<span class="badge badge-danger">No Signal</span>',
        };
        return badges[quality] || '<span class="badge">Unknown</span>';
    },

    getStatusBadge: (status) => {
        const badges = {
            'active': '<span class="badge badge-success">Active</span>',
            'inactive': '<span class="badge badge-danger">Inactive</span>',
            'maintenance': '<span class="badge badge-warning">Maintenance</span>',
            'planned': '<span class="badge badge-info">Planned</span>',
        };
        return badges[status] || '<span class="badge">Unknown</span>';
    },
};

// DOM helpers
const DOM = {
    byId: (id) => document.getElementById(id),
    byClass: (className) => document.querySelectorAll(`.${className}`),
    bySelector: (selector) => document.querySelector(selector),
    bySelectors: (selector) => document.querySelectorAll(selector),

    on: (element, event, handler) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.addEventListener(event, handler));
        } else {
            element.addEventListener(event, handler);
        }
    },

    off: (element, event, handler) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.removeEventListener(event, handler));
        } else {
            element.removeEventListener(event, handler);
        }
    },

    show: (element) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.style.display = '');
        } else {
            element.style.display = '';
        }
    },

    hide: (element) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.style.display = 'none');
        } else {
            element.style.display = 'none';
        }
    },

    addClass: (element, className) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.classList.add(className));
        } else {
            element.classList.add(className);
        }
    },

    removeClass: (element, className) => {
        if (Array.isArray(element)) {
            element.forEach(el => el.classList.remove(className));
        } else {
            element.classList.remove(className);
        }
    },

    hasClass: (element, className) => {
        return element.classList.contains(className);
    },

    setText: (element, text) => {
        element.textContent = text;
    },

    setHTML: (element, html) => {
        element.innerHTML = html;
    },

    clear: (element) => {
        element.innerHTML = '';
    },

    create: (tag, attributes = {}, content = '') => {
        const element = document.createElement(tag);
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'innerHTML') {
                element.innerHTML = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        if (content) {
            element.textContent = content;
        }
        return element;
    },

    append: (parent, child) => {
        if (Array.isArray(child)) {
            child.forEach(c => parent.appendChild(c));
        } else {
            parent.appendChild(child);
        }
    },
};

// Geolocation helper
class Geolocation {
    static getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported'));
            }
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                    });
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }

    static watchPosition(callback) {
        if (!navigator.geolocation) {
            console.error('Geolocation is not supported');
            return;
        }
        return navigator.geolocation.watchPosition((position) => {
            callback({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
            });
        });
    }

    static clearWatch(watchId) {
        navigator.geolocation.clearWatch(watchId);
    }
}

// Chart configuration
const ChartConfig = {
    getDefaultOptions: () => ({
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                labels: {
                    font: { family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" },
                    color: '#2c3e50',
                }
            }
        },
        scales: {
            y: {
                ticks: { color: '#2c3e50' },
                grid: { color: 'rgba(0, 0, 0, 0.05)' }
            },
            x: {
                ticks: { color: '#2c3e50' },
                grid: { color: 'rgba(0, 0, 0, 0.05)' }
            }
        }
    }),

    colors: {
        emerald: '#27ae60',
        blue: '#3498db',
        purple: '#9b59b6',
        orange: '#f39c12',
        amber: '#d97706',
        red: '#e74c3c',
    }
};

// Array/Object utilities
const ArrayUtils = {
    groupBy: (array, key) => {
        return array.reduce((result, obj) => {
            const group = obj[key];
            if (!result[group]) result[group] = [];
            result[group].push(obj);
            return result;
        }, {});
    },

    countBy: (array, key) => {
        return array.reduce((result, obj) => {
            const group = obj[key];
            result[group] = (result[group] || 0) + 1;
            return result;
        }, {});
    },

    sumBy: (array, key) => {
        return array.reduce((sum, obj) => sum + (obj[key] || 0), 0);
    },

    averageBy: (array, key) => {
        if (array.length === 0) return 0;
        return ArrayUtils.sumBy(array, key) / array.length;
    },

    unique: (array, key) => {
        const seen = new Set();
        return array.filter(obj => {
            const id = key ? obj[key] : obj;
            if (seen.has(id)) return false;
            seen.add(id);
            return true;
        });
    },
};

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Sleep utility
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export for use in modules
console.log('Utilities loaded successfully');
