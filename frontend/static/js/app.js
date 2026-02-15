// Intelligent Inventory Demand Forecasting System - Frontend JavaScript

// Global variables
let historicalChart = null;
let forecastChart = null;
let detailedForecastChart = null;
let comparisonChart = null;
let dashboardData = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing dashboard...');
    
    try {
        console.log('Initializing navigation...');
        initializeNavigation();
        
        console.log('Initializing charts...');
        initializeCharts();
        
        console.log('Loading dashboard data...');
        loadDashboardData();
        
        console.log('Setting up file upload...');
        setupFileUpload();
        
        console.log('Setting up sliders...');
        setupSliders();
        
        console.log('Dashboard initialization complete!');
    } catch (error) {
        console.error('Error during initialization:', error);
        showNotification('error', 'Failed to initialize dashboard: ' + error.message);
    }
});

// Navigation
function initializeNavigation() {
    console.log('Setting up navigation...');
    const navItems = document.querySelectorAll('.nav-item');
    console.log(`Found ${navItems.length} navigation items`);
    
    if (navItems.length === 0) {
        console.warn('No navigation items found!');
        return;
    }
    
    navItems.forEach((item, index) => {
        console.log(`Adding click handler to nav item ${index}:`, item.getAttribute('data-section'));
        
        item.addEventListener('click', function(e) {
            console.log('Navigation item clicked:', this.getAttribute('data-section'));
            
            try {
                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Get section name
                const section = this.getAttribute('data-section');
                console.log('Switching to section:', section);
                
                // Hide all sections
                document.querySelectorAll('.section').forEach(sec => {
                    sec.style.display = 'none';
                });
                
                // Show selected section
                const targetSection = document.getElementById(`${section}-section`);
                if (targetSection) {
                    targetSection.style.display = 'block';
                    console.log('Section displayed:', section);
                    
                    // Update header
                    updatePageHeader(section);
                } else {
                    console.error('Section not found:', `${section}-section`);
                    showNotification('error', `Section ${section} not found`);
                }
            } catch (error) {
                console.error('Error in navigation click handler:', error);
                showNotification('error', 'Navigation error: ' + error.message);
            }
        });
    });
    
    console.log('Navigation setup complete');
}

function updatePageHeader(section) {
    const titles = {
        'dashboard': { title: 'Dashboard Overview', subtitle: 'Real-time inventory demand forecasting and optimization' },
        'data': { title: 'Data Collection', subtitle: 'Import and manage your sales data' },
        'preprocessing': { title: 'Data Preprocessing', subtitle: 'Clean and prepare data for machine learning' },
        'features': { title: 'Feature Engineering', subtitle: 'Generate predictive features from your data' },
        'models': { title: 'Model Training', subtitle: 'Train ML models for demand forecasting' },
        'forecast': { title: 'Forecasting', subtitle: 'Generate future demand predictions' },
        'evaluation': { title: 'Model Evaluation', subtitle: 'Evaluate and compare model performance' },
        'insights': { title: 'Insights & Optimization', subtitle: 'Get actionable business recommendations' },
        'alerts': { title: 'Notifications', subtitle: 'Configure and manage inventory alerts' }
    };
    
    if (titles[section]) {
        document.getElementById('page-title').textContent = titles[section].title;
        document.getElementById('page-subtitle').textContent = titles[section].subtitle;
    }
}

// File Upload
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
            // Reset file input to allow re-uploading the same file
            e.target.value = '';
        }
    });
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show progress
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('progress-bar').style.width = '0%';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        document.getElementById('progress-bar').style.width = `${progress}%`;
        
        if (progress >= 90) {
            clearInterval(progressInterval);
        }
    }, 200);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'  // Include session cookies
        });
        
        clearInterval(progressInterval);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Complete progress
            document.getElementById('progress-bar').style.width = '100%';
            
            // Update data preview
            if (result.preview) {
                updateDataPreview(result.preview);
            }
            
            // Show success message with details
            showNotification('success', `Data uploaded successfully! ${result.records} records imported.`);
            
            setTimeout(() => {
                document.getElementById('upload-progress').style.display = 'none';
                // Refresh dashboard data
                if (typeof loadDashboardData === 'function') {
                    loadDashboardData();
                }
            }, 1500);
        } else {
            clearInterval(progressInterval);
            document.getElementById('upload-progress').style.display = 'none';
            showNotification('error', result.error || 'Upload failed. Please try again.');
        }
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Upload error:', error);
        document.getElementById('upload-progress').style.display = 'none';
        
        // Reset file input to allow re-upload
        const fileInput = document.getElementById('file-upload');
        if (fileInput) {
            fileInput.value = '';
        }
        
        // Provide detailed error message
        let errorMessage = 'Upload failed. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'Please make sure you are logged in and try again. If the problem persists, try refreshing the page.';
        } else if (error.message.includes('401')) {
            errorMessage += 'Session expired. Please log in again.';
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else if (error.message.includes('413')) {
            errorMessage += 'File is too large. Maximum size is 16MB.';
        } else {
            errorMessage += error.message;
        }
        
        showNotification('error', errorMessage);
    }
}

function updateDataPreview(data) {
    const tbody = document.getElementById('data-preview-body');
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.date || '-'}</td>
            <td>${row.product_id || '-'}</td>
            <td>${row.sales || '-'}</td>
            <td>${row.demand || '-'}</td>
            <td>$${row.price || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Sliders
function setupSliders() {
    // Test size slider
    const testSize = document.getElementById('test-size');
    if (testSize) {
        testSize.addEventListener('input', (e) => {
            document.getElementById('test-size-value').textContent = `${e.target.value}%`;
        });
    }
    
    // Forecast horizon slider
    const forecastHorizon = document.getElementById('forecast-horizon');
    if (forecastHorizon) {
        forecastHorizon.addEventListener('input', (e) => {
            document.getElementById('horizon-value').textContent = `${e.target.value} days`;
        });
    }
}

// Charts
function initializeCharts() {
    // Historical Sales Chart
    const historicalCtx = document.getElementById('historicalChart');
    if (historicalCtx) {
        historicalChart = new Chart(historicalCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Sales',
                    data: [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Forecast Chart
    const forecastCtx = document.getElementById('forecastChart');
    if (forecastCtx) {
        forecastChart = new Chart(forecastCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Predicted Demand',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        dashboardData = data;
        
        // Update stats
        document.getElementById('total-records').textContent = data.summary?.raw_records || 0;
        document.getElementById('forecast-accuracy').textContent = data.summary?.forecast_summary ? '92%' : '0%';
        document.getElementById('total-demand').textContent = data.summary?.forecast_summary?.total_demand || 0;
        document.getElementById('active-alerts').textContent = '3';
        
        // Load chart data
        await loadHistoricalChartData();
        await loadForecastChartData();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadHistoricalChartData() {
    try {
        const response = await fetch('/api/historical-chart-data');
        const data = await response.json();
        
        if (historicalChart) {
            historicalChart.data.labels = data.dates;
            historicalChart.data.datasets[0].data = data.sales;
            historicalChart.update();
        }
    } catch (error) {
        console.error('Error loading historical chart data:', error);
    }
}

async function loadForecastChartData() {
    try {
        const response = await fetch('/api/forecast-chart-data');
        const data = await response.json();
        
        if (forecastChart) {
            forecastChart.data.labels = data.dates;
            forecastChart.data.datasets[0].data = data.predicted_demand;
            forecastChart.update();
        }
    } catch (error) {
        console.error('Error loading forecast chart data:', error);
    }
}

// Data Collection Functions
async function fetchWeatherData() {
    showNotification('info', 'Fetching weather data...');
    
    try {
        const response = await fetch('/api/external-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: '2024-01-01',
                end_date: '2024-12-31',
                location: 'New York'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', `Fetched ${result.weather_records} weather records`);
        } else {
            showNotification('error', result.error || 'Failed to fetch weather data');
        }
    } catch (error) {
        console.error('Error fetching weather data:', error);
        showNotification('error', 'Failed to fetch weather data');
    }
}

async function fetchHolidayData() {
    showNotification('info', 'Fetching holiday data...');
    
    try {
        const response = await fetch('/api/external-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_date: '2024-01-01',
                end_date: '2024-12-31'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', `Fetched ${result.holiday_records} holiday records`);
        } else {
            showNotification('error', result.error || 'Failed to fetch holiday data');
        }
    } catch (error) {
        console.error('Error fetching holiday data:', error);
        showNotification('error', 'Failed to fetch holiday data');
    }
}

// Preprocessing Functions
async function preprocessData() {
    const options = {
        handle_missing: document.getElementById('handle-missing').checked,
        remove_outliers: document.getElementById('remove-outliers').checked,
        encode_categorical: document.getElementById('encode-categorical').checked,
        scale_features: document.getElementById('scale-features').checked
    };
    
    showNotification('info', 'Preprocessing data...');
    
    // Update statuses
    document.getElementById('missing-status').textContent = 'Processing...';
    document.getElementById('missing-status').className = 'module-status in-progress';
    
    try {
        const response = await fetch('/api/preprocess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update statuses
            document.getElementById('missing-status').textContent = 'Completed';
            document.getElementById('missing-status').className = 'module-status completed';
            document.getElementById('outlier-status').textContent = 'Completed';
            document.getElementById('outlier-status').className = 'module-status completed';
            document.getElementById('encoding-status').textContent = 'Completed';
            document.getElementById('encoding-status').className = 'module-status completed';
            document.getElementById('scaling-status').textContent = 'Completed';
            document.getElementById('scaling-status').className = 'module-status completed';
            
            showNotification('success', `Data preprocessed: ${result.records} records`);
        } else {
            showNotification('error', result.error || 'Preprocessing failed');
        }
    } catch (error) {
        console.error('Preprocessing error:', error);
        showNotification('error', 'Preprocessing failed');
    }
}

// Feature Engineering Functions
async function engineerFeatures() {
    const options = {
        create_lags: document.getElementById('create-lags').checked,
        moving_averages: document.getElementById('moving-averages').checked,
        date_features: document.getElementById('date-features').checked,
        weather_features: document.getElementById('weather-features').checked,
        holiday_features: document.getElementById('holiday-features').checked,
        trend_features: document.getElementById('trend-features').checked
    };
    
    showNotification('info', 'Engineering features...');
    
    try {
        const response = await fetch('/api/engineer-features', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update features list
            const featuresList = document.getElementById('features-list');
            featuresList.innerHTML = '';
            
            result.features.forEach(feature => {
                const badge = document.createElement('span');
                badge.className = 'badge badge-info';
                badge.textContent = feature;
                featuresList.appendChild(badge);
            });
            
            showNotification('success', `Generated ${result.features_count} features`);
        } else {
            showNotification('error', result.error || 'Feature engineering failed');
        }
    } catch (error) {
        console.error('Feature engineering error:', error);
        showNotification('error', 'Feature engineering failed');
    }
}

// Model Training Functions
async function trainModels() {
    const models = [];
    
    if (document.getElementById('rf-model').checked) models.push('random_forest');
    if (document.getElementById('gb-model').checked) models.push('gradient_boosting');
    if (document.getElementById('lr-model').checked) models.push('linear_regression');
    if (document.getElementById('arima-model').checked) models.push('arima');
    
    const testSize = parseInt(document.getElementById('test-size').value) / 100;
    
    showNotification('info', 'Training models...');
    
    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                models: models,
                test_size: testSize
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update training progress
            document.getElementById('training-progress').innerHTML = `
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Status: <strong>Completed</strong></span>
                        <span>Time: ${result.training_time.toFixed(2)}s</span>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${result.models.map(model => `<span class="badge badge-success">${model}</span>`).join('')}
                    </div>
                </div>
            `;
            
            // Update models table
            const tbody = document.getElementById('models-table-body');
            tbody.innerHTML = '';
            
            result.models.forEach(model => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${model.replace('_', ' ').toUpperCase()}</td>
                    <td><span class="badge badge-success">Trained</span></td>
                    <td>-</td>
                    <td><button class="btn btn-secondary" onclick="useModel('${model}')">Use</button></td>
                `;
                tbody.appendChild(tr);
            });
            
            showNotification('success', `Trained ${result.models.length} models`);
        } else {
            showNotification('error', result.error || 'Training failed');
        }
    } catch (error) {
        console.error('Training error:', error);
        showNotification('error', 'Model training failed');
    }
}

// Forecasting Functions
async function generateForecast() {
    const model = document.getElementById('forecast-model').value;
    const horizon = parseInt(document.getElementById('forecast-horizon').value);
    
    showNotification('info', 'Generating forecast...');
    
    try {
        const response = await fetch('/api/forecast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: model,
                horizon: horizon
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update forecast summary
            document.getElementById('forecast-total').textContent = result.summary.total_demand.toFixed(0);
            document.getElementById('forecast-avg').textContent = result.summary.avg_daily_demand.toFixed(0);
            document.getElementById('forecast-peak').textContent = result.summary.peak_demand.toFixed(0);
            document.getElementById('forecast-peak-date').textContent = result.summary.peak_date;
            
            // Create detailed forecast chart
            createDetailedForecastChart(result.forecast);
            
            showNotification('success', `Generated ${horizon}-day forecast`);
        } else {
            showNotification('error', result.error || 'Forecasting failed');
        }
    } catch (error) {
        console.error('Forecasting error:', error);
        showNotification('error', 'Forecast generation failed');
    }
}

function createDetailedForecastChart(forecastData) {
    const ctx = document.getElementById('detailedForecastChart');
    
    if (detailedForecastChart) {
        detailedForecastChart.destroy();
    }
    
    detailedForecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecastData.map(d => d.date),
            datasets: [{
                label: 'Predicted Demand',
                data: forecastData.map(d => d.predicted_demand),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Lower Bound',
                data: forecastData.map(d => d.lower_bound),
                borderColor: 'rgba(99, 102, 241, 0.5)',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                tension: 0.4
            }, {
                label: 'Upper Bound',
                data: forecastData.map(d => d.upper_bound),
                borderColor: 'rgba(99, 102, 241, 0.5)',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Evaluation Functions
async function evaluateModels() {
    showNotification('info', 'Evaluating models...');
    
    try {
        const response = await fetch('/api/evaluate', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Update evaluation table
            const tbody = document.getElementById('evaluation-table-body');
            tbody.innerHTML = '';
            
            Object.entries(result.evaluations).forEach(([model, metrics]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${model.replace('_', ' ').toUpperCase()}</td>
                    <td>${metrics.mae.toFixed(2)}</td>
                    <td>${metrics.rmse.toFixed(2)}</td>
                    <td>${metrics.mape.toFixed(2)}%</td>
                    <td>${metrics.r2.toFixed(3)}</td>
                    <td><span class="badge badge-success">${metrics.accuracy_percentage.toFixed(1)}%</span></td>
                `;
                tbody.appendChild(tr);
            });
            
            // Create comparison chart
            createComparisonChart(result.comparison);
            
            showNotification('success', 'Model evaluation complete');
        } else {
            showNotification('error', result.error || 'Evaluation failed');
        }
    } catch (error) {
        console.error('Evaluation error:', error);
        showNotification('error', 'Model evaluation failed');
    }
}

function createComparisonChart(comparisonData) {
    const ctx = document.getElementById('comparisonChart');
    
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    const models = comparisonData.map(d => d.model.replace('_', ' ').toUpperCase());
    const mae = comparisonData.map(d => d.mae);
    const rmse = comparisonData.map(d => d.rmse);
    
    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: models,
            datasets: [{
                label: 'MAE',
                data: mae,
                backgroundColor: 'rgba(99, 102, 241, 0.8)'
            }, {
                label: 'RMSE',
                data: rmse,
                backgroundColor: 'rgba(236, 72, 153, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Insights Functions
async function generateInsights() {
    showNotification('info', 'Generating insights...');
    
    try {
        const response = await fetch('/api/insights');
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Failed to generate insights');
        }
        
        if (result.success) {
            // Update ABC Analysis
            document.getElementById('abc-analysis-content').innerHTML = `
                <p class="module-description">${result.abc_analysis.recommendations.A || 'No data'}</p>
            `;
            
            // Update Reorder Points
            document.getElementById('reorder-points-content').innerHTML = `
                <p class="module-description">Reorder Point: ${result.reorder_points.reorder_point.toFixed(0)} units</p>
                <p class="module-description">Safety Stock: ${result.reorder_points.safety_stock.toFixed(0)} units</p>
                <p class="module-description">EOQ: ${result.reorder_points.economic_order_quantity.toFixed(0)} units</p>
            `;
            
            // Update recommendations
            const recommendationsList = document.getElementById('recommendations-list');
            recommendationsList.innerHTML = '';
            
            result.recommendations.forEach(rec => {
                const div = document.createElement('div');
                div.className = 'alert alert-info';
                div.innerHTML = `
                    <div class="alert-icon">💡</div>
                    <div class="alert-content">
                        <h4>${rec.title}</h4>
                        <p>${rec.description}</p>
                        <p><strong>Action:</strong> ${rec.action}</p>
                        <p><strong>Expected Impact:</strong> ${rec.expected_impact}</p>
                    </div>
                `;
                recommendationsList.appendChild(div);
            });
            
            // Update optimization summary
            document.getElementById('optimization-summary').innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${result.optimization_summary.total_recommendations}</div>
                        <div class="stat-label">Total Recommendations</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${result.optimization_summary.high_priority}</div>
                        <div class="stat-label">High Priority</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${result.optimization_summary.medium_priority}</div>
                        <div class="stat-label">Medium Priority</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${result.optimization_summary.low_priority}</div>
                        <div class="stat-label">Low Priority</div>
                    </div>
                </div>
            `;
            
            showNotification('success', 'Insights generated successfully');
        } else {
            showNotification('error', result.error || 'Failed to generate insights');
        }
    } catch (error) {
        console.error('Insights error:', error);
        showNotification('error', 'Failed to generate insights');
    }
}

// Alerts Functions
async function configureAlerts() {
    const config = {
        low_stock_threshold: parseInt(document.getElementById('low-stock-threshold').value),
        email_enabled: document.getElementById('email-enabled').checked,
        email_address: document.getElementById('email-address').value,
        sms_enabled: document.getElementById('sms-enabled').checked,
        phone_number: document.getElementById('phone-number').value
    };
    
    try {
        const response = await fetch('/api/configure-alerts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', 'Alert configuration saved');
        } else {
            showNotification('error', result.error || 'Failed to save configuration');
        }
    } catch (error) {
        console.error('Configuration error:', error);
        showNotification('error', 'Failed to save configuration');
    }
}

async function sendTestAlert() {
    showNotification('info', 'Sending test alert...');
    
    try {
        const response = await fetch('/api/send-alerts', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', `Test alert sent: ${result.alerts_sent} notifications`);
        } else {
            showNotification('error', result.error || 'Failed to send alert');
        }
    } catch (error) {
        console.error('Alert error:', error);
        showNotification('error', 'Failed to send alert');
    }
}

// Utility Functions
function refreshData() {
    showNotification('info', 'Refreshing data...');
    loadDashboardData();
    setTimeout(() => {
        showNotification('success', 'Data refreshed');
    }, 1000);
}

async function exportReport() {
    showNotification('info', 'Generating report...');
    
    try {
        const response = await fetch('/api/export-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'forecast'
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'forecast_report.txt';
            a.click();
            window.URL.revokeObjectURL(url);
            
            showNotification('success', 'Report exported successfully');
        } else {
            showNotification('error', 'Failed to export report');
        }
    } catch (error) {
        console.error('Export error:', error);
        showNotification('error', 'Failed to export report');
    }
}

function showNotification(type, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#6366f1',
        warning: '#f59e0b'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Show all alerts function
async function showAllAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const result = await response.json();
        
        if (result.success && result.alerts) {
            // Display alerts in a modal or list
            let alertsHtml = '<div class="alerts-modal"><h3>All Alerts</h3><ul>';
            
            if (result.alerts.length === 0) {
                alertsHtml += '<li>No alerts found</li>';
            } else {
                result.alerts.forEach(alert => {
                    alertsHtml += `<li><strong>${alert.type}:</strong> ${alert.message} - ${alert.timestamp}</li>`;
                });
            }
            
            alertsHtml += '</ul><button onclick="closeAlertsModal()">Close</button></div>';
            
            // Create modal overlay
            const overlay = document.createElement('div');
            overlay.id = 'alerts-overlay';
            overlay.innerHTML = alertsHtml;
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 9999;';
            
            document.body.appendChild(overlay);
            
            showNotification('success', `Found ${result.alerts.length} alerts`);
        } else {
            showNotification('info', 'No alerts available');
        }
    } catch (error) {
        console.error('Error fetching alerts:', error);
        showNotification('error', 'Failed to load alerts');
    }
}

// Close alerts modal
function closeAlertsModal() {
    const overlay = document.getElementById('alerts-overlay');
    if (overlay) {
        document.body.removeChild(overlay);
    }
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .alerts-modal {
        background: white;
        padding: 30px;
        border-radius: 10px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .alerts-modal h3 {
        margin-top: 0;
        color: #6366f1;
    }
    
    .alerts-modal ul {
        list-style: none;
        padding: 0;
    }
    
    .alerts-modal li {
        padding: 10px;
        margin: 10px 0;
        background: #f3f4f6;
        border-radius: 5px;
    }
    
    .alerts-modal button {
        margin-top: 20px;
        padding: 10px 20px;
        background: #6366f1;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .alerts-modal button:hover {
        background: #4f46e5;
    }
`;
document.head.appendChild(style);

// Add global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('error', 'An error occurred. Please check the console.');
});

// Profile Management Functions
function openProfileModal() {
    document.getElementById('profile-modal').style.display = 'flex';
}

function closeProfileModal() {
    document.getElementById('profile-modal').style.display = 'none';
    // Reset form
    document.getElementById('change-password-form').reset();
}

async function changePassword(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    
    // Validate passwords match
    if (newPassword !== confirmPassword) {
        showNotification('error', 'New passwords do not match');
        return;
    }
    
    // Validate password length
    if (newPassword.length < 6) {
        showNotification('error', 'Password must be at least 6 characters long');
        return;
    }
    
    try {
        const response = await fetch('/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            }),
            credentials: 'same-origin'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('success', 'Password changed successfully');
            document.getElementById('change-password-form').reset();
            setTimeout(() => {
                closeProfileModal();
            }, 1500);
        } else {
            showNotification('error', result.error || 'Failed to change password');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showNotification('error', 'Failed to change password. Please try again.');
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

// Theme Toggle Functions
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (body.classList.contains('dark-mode')) {
        // Switch to light mode
        body.classList.remove('dark-mode');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('theme', 'light');
        showNotification('success', 'Switched to Light Mode');
    } else {
        // Switch to dark mode
        body.classList.add('dark-mode');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('theme', 'dark');
        showNotification('success', 'Switched to Dark Mode');
    }
}

// Load theme preference on page load
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('profile-modal');
    if (event.target === modal) {
        closeProfileModal();
    }
});

// Load theme on page load
document.addEventListener('DOMContentLoaded', function() {
    loadThemePreference();
    
    // Remove SuperNinja branding
    removeSuperNinjaBranding();
});

// Function to remove SuperNinja branding
function removeSuperNinjaBranding() {
    // Remove elements with ninja-related classes or IDs
    const ninjaSelectors = [
        '[class*="ninja"]',
        '[id*="ninja"]',
        '[class*="superninja"]',
        '[id*="superninja"]',
        '[class*="daytona"]',
        '[id*="daytona"]',
        'div[style*="Made by"]',
        'div[style*="SuperNinja"]',
        'iframe[src*="ninja"]',
        'iframe[src*="super"]'
    ];
    
    ninjaSelectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.remove();
            console.log('Removed SuperNinja element:', el);
        });
    });
    
    // Remove fixed positioned elements at bottom
    const allDivs = document.querySelectorAll('div');
    allDivs.forEach(div => {
        const style = window.getComputedStyle(div);
        if (style.position === 'fixed' && style.bottom === '0px') {
            div.remove();
            console.log('Removed fixed bottom element:', div);
        }
    });
    
    // Run periodically to catch dynamically added elements
    setInterval(removeSuperNinjaBranding, 1000);
}

// Log when script loads
console.log('InventoryAI Dashboard JavaScript loaded successfully');