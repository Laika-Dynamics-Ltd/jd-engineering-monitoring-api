/**
 * Enhanced Dashboard JavaScript
 * JD Engineering Tablet Monitoring System
 * 
 * Features:
 * - Real-time data updates with WebSocket fallback
 * - Enhanced error handling and retry mechanisms
 * - Advanced chart management with animations
 * - Performance optimizations and caching
 * - Mobile-responsive interactions
 */

class DashboardManager {
    constructor() {
        this.currentTab = 'business-intelligence';
        this.deviceData = [];
        this.charts = {};
        this.refreshInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.isOnline = navigator.onLine;
        this.lastUpdate = null;
        this.cachedData = new Map();
        
        // Configuration
        this.config = {
            refreshInterval: 60000, // 60 seconds
            retryDelay: 5000, // 5 seconds
            chartAnimationDuration: 750,
            maxCacheAge: 300000, // 5 minutes
            debounceDelay: 300
        };
        
        this.init();
    }

    async init() {
        try {
            this.setupEventListeners();
            this.initializeCharts();
            this.startPerformanceMonitoring();
            await this.loadInitialData();
            this.startAutoRefresh();
            this.setupOfflineDetection();
            this.showSuccessMessage('Dashboard initialized successfully');
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.showErrorMessage('Failed to initialize dashboard');
        }
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', this.debounce((e) => {
                this.switchTab(e.target.getAttribute('data-tab'));
            }, this.config.debounceDelay));
        });

        // Search functionality
        const searchInput = document.getElementById('device-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.filterDevices(e.target.value);
            }, this.config.debounceDelay));
        }

        // View toggle
        document.querySelectorAll('.view-toggle button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.toggleView(e.target.getAttribute('data-view'));
            });
        });

        // Refresh button
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.manualRefresh());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.manualRefresh();
                        break;
                    case '1':
                        e.preventDefault();
                        this.switchTab('business-intelligence');
                        break;
                    case '2':
                        e.preventDefault();
                        this.switchTab('device-monitoring');
                        break;
                    case '3':
                        e.preventDefault();
                        this.switchTab('analytics-charts');
                        break;
                    case '4':
                        e.preventDefault();
                        this.switchTab('system-logs');
                        break;
                }
            }
        });

        // Window visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
                this.manualRefresh();
            }
        });
    }

    switchTab(tabName) {
        if (tabName === this.currentTab) return;

        // Update UI
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.getAttribute('data-tab') === tabName);
        });

        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === tabName);
        });

        this.currentTab = tabName;

        // Load specific content
        switch (tabName) {
            case 'device-monitoring':
                this.loadDeviceData();
                break;
            case 'analytics-charts':
                this.updateCharts();
                break;
            case 'business-intelligence':
                this.loadBusinessIntelligence();
                break;
            case 'system-logs':
                this.loadSystemLogs();
                break;
        }

        // Analytics
        this.trackEvent('tab_switch', { tab: tabName });
    }

    async loadInitialData() {
        const loadingPromises = [
            this.loadDashboardStatus(),
            this.loadDashboardAlerts(),
            this.loadDeviceData()
        ];

        try {
            await Promise.allSettled(loadingPromises);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadDashboardStatus() {
        try {
            const response = await this.apiCall('/api/dashboard/status');
            if (response && !response.error) {
                this.updateStatusCards(response);
                this.updateSystemHealth(response.system_health);
            }
        } catch (error) {
            console.error('Error loading dashboard status:', error);
            this.showErrorMessage('Failed to load system status');
        }
    }

    async loadDashboardAlerts() {
        try {
            const response = await this.apiCall('/api/dashboard/alerts');
            if (response && !response.error) {
                this.updateAlerts(response.alerts);
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    async loadDeviceData() {
        const deviceGrid = document.getElementById('device-grid');
        if (!deviceGrid) return;

        try {
            this.showLoading(deviceGrid);
            
            const response = await this.apiCall('/api/dashboard/devices/enhanced');
            
            if (response && !response.error) {
                this.deviceData = response.devices || [];
                this.renderDeviceCards();
                this.updateDeviceStats(response);
            } else {
                throw new Error(response?.error || 'Failed to load device data');
            }
        } catch (error) {
            console.error('Error loading device data:', error);
            this.showDeviceError(deviceGrid, error.message);
        }
    }

    updateStatusCards(data) {
        const updates = {
            'total-devices': data.total_devices || 0,
            'online-now': data.online_devices || 0,
            'avg-battery': `${data.avg_battery || 0}%`,
            'myob-active': data.myob_active || 0,
            'scanner-active': data.scanner_active || 0,
            'timeout-risks': data.timeout_risks || 0
        };

        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Animate number changes
                this.animateValue(element, element.textContent, value);
            }
        });

        this.lastUpdate = new Date(data.last_updated);
    }

    updateAlerts(alerts) {
        const alertBanner = document.getElementById('system-alert');
        if (!alertBanner || !alerts.length) return;

        const primaryAlert = alerts.find(a => a.type === 'error') || alerts[0];
        
        alertBanner.className = `alert-banner ${primaryAlert.type}`;
        alertBanner.querySelector('.icon i').className = primaryAlert.icon;
        alertBanner.querySelector('.text').textContent = primaryAlert.message;
        
        // Update alert details if available
        if (primaryAlert.details && primaryAlert.details.length > 0) {
            const detailsText = primaryAlert.details.slice(0, 3).join(', ');
            alertBanner.querySelector('.text').textContent += ` (${detailsText})`;
        }
    }

    renderDeviceCards() {
        const deviceGrid = document.getElementById('device-grid');
        if (!deviceGrid) return;

        if (this.deviceData.length === 0) {
            deviceGrid.innerHTML = this.getEmptyDeviceMessage();
            return;
        }

        const cardHtml = this.deviceData.map(device => this.createDeviceCard(device)).join('');
        deviceGrid.innerHTML = cardHtml;

        // Add click handlers for device cards
        deviceGrid.querySelectorAll('.device-card').forEach(card => {
            card.addEventListener('click', () => {
                const deviceId = card.getAttribute('data-device-id');
                this.showDeviceDetails(deviceId);
            });
        });
    }

    createDeviceCard(device) {
        const statusClass = this.getDeviceStatusClass(device.status);
        const batteryIcon = this.getBatteryIcon(device.battery_level);
        const wifiIcon = this.getWifiIcon(device.wifi_signal_strength);
        
        return `
            <div class="device-card" data-device-id="${device.device_id}">
                <div class="device-card-header">
                    <div class="device-name">${this.escapeHtml(device.device_name)}</div>
                    <div class="device-status ${statusClass}">${device.status}</div>
                </div>
                <div class="device-metrics">
                    <div class="metric-item">
                        <div class="metric-icon" style="color: var(--warning-color);">
                            <i class="${batteryIcon}"></i>
                        </div>
                        <div class="metric-text">${device.battery_level || 'Unknown'}${device.battery_level ? '%' : ''}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-icon" style="color: var(--success-color);">
                            <i class="${wifiIcon}"></i>
                        </div>
                        <div class="metric-text">${device.wifi_signal_strength || 'Unknown'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-icon" style="color: var(--primary-color);">
                            <i class="fas fa-mobile-alt"></i>
                        </div>
                        <div class="metric-text">${device.screen_state || 'Unknown'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-icon" style="color: ${device.myob_active ? 'var(--success-color)' : 'var(--text-secondary)'};">
                            <i class="fas fa-user-clock"></i>
                        </div>
                        <div class="metric-text">${device.myob_active ? 'Active' : 'Inactive'}</div>
                    </div>
                </div>
                <div class="device-footer">
                    <div class="last-seen">Last seen: ${device.last_seen_text}</div>
                    <div class="health-score">Health: ${device.health_score}%</div>
                </div>
            </div>
        `;
    }

    initializeCharts() {
        this.initializeBatteryChart();
        this.initializeWifiChart();
        this.initializeMyobChart();
        this.initializeScannerChart();
    }

    initializeBatteryChart() {
        const ctx = document.getElementById('batteryChart');
        if (!ctx) return;

        this.charts.battery = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Average Battery %',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: this.config.chartAnimationDuration
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Battery Level (%)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    initializeWifiChart() {
        const ctx = document.getElementById('wifiChart');
        if (!ctx) return;

        this.charts.wifi = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'WiFi Signal (dBm)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: this.config.chartAnimationDuration
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `Signal: ${context.parsed.y} dBm`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        min: -100,
                        max: 0,
                        title: {
                            display: true,
                            text: 'Signal Strength (dBm)'
                        }
                    }
                }
            }
        });
    }

    initializeMyobChart() {
        const ctx = document.getElementById('myobChart');
        if (!ctx) return;

        this.charts.myob = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'MYOB Sessions',
                    data: [12, 19, 3, 5, 2, 3, 7],
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: '#2563eb',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: this.config.chartAnimationDuration
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Session Count'
                        }
                    }
                }
            }
        });
    }

    initializeScannerChart() {
        const ctx = document.getElementById('scannerChart');
        if (!ctx) return;

        this.charts.scanner = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Successful', 'Failed', 'Timeout'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: this.config.chartAnimationDuration
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    async updateCharts() {
        try {
            const response = await this.apiCall('/api/dashboard/charts/realtime');
            
            if (response && !response.error) {
                this.updateBatteryChart(response.battery_chart);
                this.updateWifiChart(response.wifi_chart);
                // Update other charts as needed
            }
        } catch (error) {
            console.error('Error updating charts:', error);
        }
    }

    updateBatteryChart(data) {
        if (!this.charts.battery || !data) return;

        this.charts.battery.data.labels = data.labels;
        this.charts.battery.data.datasets[0].data = data.datasets[0].data;
        this.charts.battery.update('smooth');
    }

    updateWifiChart(data) {
        if (!this.charts.wifi || !data) return;

        this.charts.wifi.data.labels = data.labels;
        this.charts.wifi.data.datasets[0].data = data.datasets[0].data;
        this.charts.wifi.update('smooth');
    }

    // Utility functions
    async apiCall(endpoint, options = {}) {
        const token = localStorage.getItem('auth_token');
        
        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        };

        try {
            const response = await fetch(endpoint, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                if (response.status === 401) {
                    this.handleAuthError();
                    return null;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                await this.delay(this.config.retryDelay);
                return this.apiCall(endpoint, options);
            }
            
            this.retryCount = 0;
            throw error;
        }
    }

    showLoading(container) {
        container.innerHTML = `
            <div class="loading-skeleton">
                <div class="loading-spinner"></div>
                <span style="margin-left: 1rem;">Loading...</span>
            </div>
        `;
    }

    showDeviceError(container, message) {
        container.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-secondary);">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem; color: var(--error-color);"></i>
                <p>${this.escapeHtml(message)}</p>
                <button onclick="dashboardManager.loadDeviceData()" 
                        style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary-color); color: white; border: none; border-radius: var(--radius-md); cursor: pointer;">
                    Try Again
                </button>
            </div>
        `;
    }

    getEmptyDeviceMessage() {
        return `
            <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-secondary);">
                <i class="fas fa-tablet-alt" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                <p>No devices found</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Devices will appear here when they start reporting data</p>
            </div>
        `;
    }

    getDeviceStatusClass(status) {
        const statusMap = {
            'online': 'online',
            'warning': 'warning',
            'offline': 'offline'
        };
        return statusMap[status] || 'offline';
    }

    getBatteryIcon(level) {
        if (!level) return 'fas fa-battery-empty';
        if (level > 75) return 'fas fa-battery-full';
        if (level > 50) return 'fas fa-battery-three-quarters';
        if (level > 25) return 'fas fa-battery-half';
        if (level > 10) return 'fas fa-battery-quarter';
        return 'fas fa-battery-empty';
    }

    getWifiIcon(strength) {
        if (!strength) return 'fas fa-wifi-slash';
        if (strength > -30) return 'fas fa-wifi';
        if (strength > -50) return 'fas fa-wifi';
        if (strength > -70) return 'fas fa-wifi';
        return 'fas fa-wifi';
    }

    // Auto-refresh functionality
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            if (!document.hidden && this.isOnline) {
                this.loadDashboardStatus();
                if (this.currentTab === 'device-monitoring') {
                    this.loadDeviceData();
                }
                if (this.currentTab === 'analytics-charts') {
                    this.updateCharts();
                }
            }
        }, this.config.refreshInterval);
    }

    pauseAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    resumeAutoRefresh() {
        if (!this.refreshInterval) {
            this.startAutoRefresh();
        }
    }

    async manualRefresh() {
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        }

        try {
            await this.loadInitialData();
            this.showSuccessMessage('Data refreshed successfully');
        } catch (error) {
            this.showErrorMessage('Failed to refresh data');
        } finally {
            if (refreshBtn) {
                setTimeout(() => {
                    refreshBtn.disabled = false;
                    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                }, 1000);
            }
        }
    }

    // Utility methods
    debounce(func, wait) {
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

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    animateValue(element, start, end) {
        const startNum = parseFloat(start) || 0;
        const endNum = parseFloat(end) || 0;
        const duration = 1000;
        const steps = 60;
        const stepValue = (endNum - startNum) / steps;
        let current = startNum;
        let step = 0;

        const timer = setInterval(() => {
            current += stepValue;
            step++;
            
            if (step >= steps) {
                current = endNum;
                clearInterval(timer);
            }
            
            element.textContent = typeof end === 'string' && end.includes('%') 
                ? `${Math.round(current)}%` 
                : Math.round(current);
        }, duration / steps);
    }

    // Messaging system
    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create or update notification element
        let notification = document.getElementById('notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'notification';
            document.body.appendChild(notification);
        }

        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#2563eb'};
        `;

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto hide
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    // Analytics and monitoring
    trackEvent(eventName, data = {}) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, data);
        }
        console.log('Event tracked:', eventName, data);
    }

    startPerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            this.trackEvent('page_load_time', {
                load_time: perfData.loadEventEnd - perfData.loadEventStart
            });
        });
    }

    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showSuccessMessage('Connection restored');
            this.manualRefresh();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showErrorMessage('Connection lost - working offline');
        });
    }

    handleAuthError() {
        localStorage.removeItem('auth_token');
        this.showErrorMessage('Session expired - redirecting to login');
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    // Device details modal (placeholder for future enhancement)
    showDeviceDetails(deviceId) {
        console.log('Show device details for:', deviceId);
        this.trackEvent('device_details_view', { device_id: deviceId });
        // TODO: Implement device details modal
    }

    filterDevices(searchTerm) {
        const deviceCards = document.querySelectorAll('.device-card');
        const term = searchTerm.toLowerCase();
        
        deviceCards.forEach(card => {
            const deviceName = card.querySelector('.device-name').textContent.toLowerCase();
            const isVisible = deviceName.includes(term);
            card.style.display = isVisible ? 'block' : 'none';
        });
    }

    toggleView(viewType) {
        document.querySelectorAll('.view-toggle button').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-view') === viewType);
        });

        const deviceGrid = document.getElementById('device-grid');
        if (deviceGrid) {
            if (viewType === 'list') {
                deviceGrid.style.gridTemplateColumns = '1fr';
            } else {
                deviceGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(320px, 1fr))';
            }
        }
    }

    // Cleanup
    destroy() {
        this.pauseAutoRefresh();
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize dashboard when DOM is ready
let dashboardManager;

document.addEventListener('DOMContentLoaded', function() {
    dashboardManager = new DashboardManager();
});

// Export for global access
window.dashboardManager = dashboardManager;

// Logout function
function logout() {
    localStorage.removeItem('auth_token');
    window.location.href = '/';
} 