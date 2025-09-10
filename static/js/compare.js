/**
 * ROI Calculator Comparison View JavaScript
 * Handles calculation selection, comparison loading, and visualization
 */

// Global variables
let availableCalculations = [];
let selectedCalculations = [];
let comparisonData = null;
let charts = {};

// Chart.js configuration
const chartColors = ['#d4af37', '#00c853', '#ff1744', '#00b0ff'];
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#ffffff',
                font: {
                    family: 'Inter'
                }
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#b0b0b0'
            },
            grid: {
                color: '#333333'
            }
        },
        y: {
            ticks: {
                color: '#b0b0b0'
            },
            grid: {
                color: '#333333'
            }
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadAvailableCalculations();
    updateSelectionCounter();
    
    // Check if we have calculation IDs in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const ids = urlParams.get('ids');
    if (ids) {
        const calculationIds = ids.split(',').map(id => parseInt(id)).filter(id => !isNaN(id));
        if (calculationIds.length >= 2 && calculationIds.length <= 3) {
            selectedCalculations = calculationIds;
            updateSelectionCounter();
            // Auto-load comparison after calculations are loaded
            setTimeout(() => {
                loadComparison();
            }, 1000);
        }
    }
});

/**
 * Load available calculations from the API
 */
async function loadAvailableCalculations() {
    try {
        const response = await fetch('/api/calculations?limit=50');
        const result = await response.json();
        
        if (result.success) {
            availableCalculations = result.calculations;
            displayCalculationsList(availableCalculations);
        } else {
            showError('Failed to load calculations');
        }
    } catch (error) {
        console.error('Error loading calculations:', error);
        showError('Error loading calculations: ' + error.message);
    }
}

/**
 * Display the list of available calculations for selection
 */
function displayCalculationsList(calculations) {
    const container = document.getElementById('calculationsList');
    
    if (calculations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h5>No Saved Calculations</h5>
                <p>You need at least 2 saved calculations to use the comparison feature.</p>
                <a href="/" class="btn btn-primary mt-3">
                    <i class="fas fa-plus"></i> Create New Calculation
                </a>
            </div>
        `;
        return;
    }
    
    let html = '';
    calculations.forEach(calc => {
        const date = new Date(calc.created_at).toLocaleDateString();
        const roi = getROIValue(calc);
        const payback = getPaybackValue(calc);
        const isSelected = selectedCalculations.includes(calc.id);
        
        html += `
            <div class="calculation-checkbox ${isSelected ? 'selected' : ''}" 
                 onclick="toggleCalculationSelection(${calc.id})" 
                 id="calc-${calc.id}">
                <div class="row align-items-center">
                    <div class="col-1">
                        <input type="checkbox" class="form-check-input" 
                               ${isSelected ? 'checked' : ''} 
                               onchange="event.stopPropagation();">
                    </div>
                    <div class="col-md-5">
                        <h6 class="mb-1">${calc.company_name || 'Unnamed Company'}</h6>
                        <small class="text-muted">
                            <i class="fas fa-calendar me-1"></i> ${date}
                        </small>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <div class="fw-bold text-success">${roi.toFixed(1)}% ROI</div>
                            <small class="text-muted">${payback.toFixed(1)} months payback</small>
                        </div>
                    </div>
                    <div class="col-md-3 text-end">
                        <small class="text-muted">
                            <i class="fas fa-dollar-sign me-1"></i>
                            Revenue: $${formatNumber(calc.annual_revenue)}
                        </small>
                        <br>
                        <small class="text-muted">
                            Investment: $${formatNumber(calc.service_investment)}
                        </small>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Toggle calculation selection
 */
function toggleCalculationSelection(calcId) {
    const index = selectedCalculations.indexOf(calcId);
    const element = document.getElementById(`calc-${calcId}`);
    const checkbox = element.querySelector('input[type="checkbox"]');
    
    if (index > -1) {
        // Remove selection
        selectedCalculations.splice(index, 1);
        element.classList.remove('selected');
        checkbox.checked = false;
    } else {
        // Add selection (max 3)
        if (selectedCalculations.length >= 3) {
            showToast('You can select maximum 3 calculations for comparison', 'warning');
            return;
        }
        
        selectedCalculations.push(calcId);
        element.classList.add('selected');
        checkbox.checked = true;
    }
    
    updateSelectionCounter();
}

/**
 * Update selection counter and compare button state
 */
function updateSelectionCounter() {
    const counter = document.getElementById('selectionCounter');
    const compareBtn = document.getElementById('compareBtn');
    
    counter.textContent = `${selectedCalculations.length} / 3 selected`;
    compareBtn.disabled = selectedCalculations.length < 2;
    
    if (selectedCalculations.length >= 2) {
        compareBtn.classList.add('btn-success');
        compareBtn.classList.remove('btn-secondary');
    } else {
        compareBtn.classList.add('btn-secondary');
        compareBtn.classList.remove('btn-success');
    }
}

/**
 * Load and display comparison
 */
async function loadComparison() {
    if (selectedCalculations.length < 2) {
        showToast('Please select at least 2 calculations to compare', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                calculation_ids: selectedCalculations
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            comparisonData = result;
            displayComparison(result.calculations, result.comparison);
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('comparisonResults').style.display = 'block';
        } else {
            throw new Error(result.message || 'Comparison failed');
        }
        
    } catch (error) {
        console.error('Error loading comparison:', error);
        showError('Error loading comparison: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Display the comparison results
 */
function displayComparison(calculations, comparison) {
    displayCompanyColumns(calculations, comparison);
    displayComparisonTable(calculations, comparison);
    displayCharts(calculations, comparison);
    
    // Scroll to results
    document.getElementById('comparisonResults').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

/**
 * Display company columns with key metrics
 */
function displayCompanyColumns(calculations, comparison) {
    const container = document.getElementById('companyColumns');
    let html = '';
    
    calculations.forEach((calc, index) => {
        const roi = getROIValue(calc);
        const payback = getPaybackValue(calc);
        const savings = getAnnualSavings(calc);
        const npv = getNPVValue(calc);
        const investment = calc.service_investment;
        
        // Get rankings for badges
        const rankings = comparison.rankings || {};
        const differences = comparison.differences || {};
        
        html += `
            <div class="col-md-${calculations.length === 2 ? '6' : '4'}">
                <div class="company-column">
                    <div class="company-header">
                        <h5 class="mb-0">${calc.company_name || 'Company ' + (index + 1)}</h5>
                        ${isTopPerformer(index, 'roi', rankings) ? '<span class="best-badge ms-2">Best ROI</span>' : ''}
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-percentage me-2"></i>First Year ROI
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value roi-highlight">${roi.toFixed(1)}%</span>
                            ${getDifferenceIndicator(differences.roi, index, false)}
                        </div>
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-clock me-2"></i>Payback Period
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value">${payback.toFixed(1)} months</span>
                            ${getDifferenceIndicator(differences.payback_months, index, true)}
                        </div>
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-piggy-bank me-2"></i>Annual Savings
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value">$${formatNumber(savings)}</span>
                            ${getDifferenceIndicator(differences.annual_savings, index, false)}
                        </div>
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-dollar-sign me-2"></i>Net Present Value
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value">$${formatNumber(npv)}</span>
                            ${getDifferenceIndicator(differences.npv, index, false)}
                        </div>
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-handshake me-2"></i>Investment
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value">$${formatNumber(investment)}</span>
                            ${getDifferenceIndicator(differences.service_investment, index, true)}
                        </div>
                    </div>
                    
                    <div class="metric-row">
                        <span class="metric-label">
                            <i class="fas fa-building me-2"></i>Annual Revenue
                        </span>
                        <div class="d-flex align-items-center">
                            <span class="metric-value">$${formatNumber(calc.annual_revenue)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Display detailed comparison table
 */
function displayComparisonTable(calculations, comparison) {
    const table = document.getElementById('comparisonTable');
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');
    
    // Build header
    let headerHtml = '<th>Metric</th>';
    calculations.forEach((calc, index) => {
        headerHtml += `<th class="text-center">${calc.company_name || 'Company ' + (index + 1)}</th>`;
    });
    thead.innerHTML = headerHtml;
    
    // Build rows
    const metrics = [
        { key: 'roi', label: 'First Year ROI (%)', icon: 'fas fa-percentage', format: 'percentage' },
        { key: 'payback_months', label: 'Payback Period (months)', icon: 'fas fa-clock', format: 'decimal' },
        { key: 'annual_savings', label: 'Annual Savings', icon: 'fas fa-piggy-bank', format: 'currency' },
        { key: 'monthly_savings', label: 'Monthly Savings', icon: 'fas fa-calendar-alt', format: 'currency' },
        { key: 'npv', label: 'Net Present Value', icon: 'fas fa-dollar-sign', format: 'currency' },
        { key: 'irr', label: 'Internal Rate of Return (%)', icon: 'fas fa-chart-line', format: 'percentage' },
        { key: 'year_3_roi', label: '3-Year ROI (%)', icon: 'fas fa-calendar-plus', format: 'percentage' },
        { key: 'service_investment', label: 'Investment Required', icon: 'fas fa-handshake', format: 'currency' },
        { key: 'annual_revenue', label: 'Annual Revenue', icon: 'fas fa-building', format: 'currency' }
    ];
    
    let bodyHtml = '';
    metrics.forEach(metric => {
        bodyHtml += `
            <tr>
                <td>
                    <i class="${metric.icon} me-2"></i>
                    <strong>${metric.label}</strong>
                </td>
        `;
        
        calculations.forEach((calc, index) => {
            const value = getMetricValue(calc, metric.key);
            const formattedValue = formatMetricValue(value, metric.format);
            const rankings = comparison.rankings || {};
            const isTop = isTopPerformer(index, metric.key, rankings);
            
            bodyHtml += `
                <td class="text-center ${isTop ? 'table-warning' : ''}">
                    <span class="fw-bold">${formattedValue}</span>
                    ${isTop ? '<br><span class="best-badge">Best</span>' : ''}
                </td>
            `;
        });
        
        bodyHtml += '</tr>';
    });
    
    tbody.innerHTML = bodyHtml;
}

/**
 * Display charts
 */
function displayCharts(calculations, comparison) {
    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};
    
    const labels = calculations.map((calc, index) => calc.company_name || `Company ${index + 1}`);
    
    // ROI Chart
    charts.roi = createChart('roiChart', 'bar', {
        labels: labels,
        datasets: [{
            label: 'First Year ROI (%)',
            data: calculations.map(calc => getROIValue(calc).toFixed(1)),
            backgroundColor: chartColors.slice(0, calculations.length),
            borderColor: chartColors.slice(0, calculations.length),
            borderWidth: 2
        }]
    });
    
    // Annual Savings Chart
    charts.savings = createChart('savingsChart', 'bar', {
        labels: labels,
        datasets: [{
            label: 'Annual Savings ($)',
            data: calculations.map(calc => getAnnualSavings(calc)),
            backgroundColor: chartColors.slice(0, calculations.length),
            borderColor: chartColors.slice(0, calculations.length),
            borderWidth: 2
        }]
    });
    
    // Payback Period Chart
    charts.payback = createChart('paybackChart', 'bar', {
        labels: labels,
        datasets: [{
            label: 'Payback Period (months)',
            data: calculations.map(calc => getPaybackValue(calc).toFixed(1)),
            backgroundColor: chartColors.slice(0, calculations.length),
            borderColor: chartColors.slice(0, calculations.length),
            borderWidth: 2
        }]
    });
    
    // NPV Chart
    charts.npv = createChart('npvChart', 'bar', {
        labels: labels,
        datasets: [{
            label: 'Net Present Value ($)',
            data: calculations.map(calc => getNPVValue(calc)),
            backgroundColor: chartColors.slice(0, calculations.length),
            borderColor: chartColors.slice(0, calculations.length),
            borderWidth: 2
        }]
    });
}

/**
 * Create a chart
 */
function createChart(canvasId, type, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: type,
        data: data,
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            
                            if (label.includes('$')) {
                                label += '$' + formatNumber(context.parsed.y);
                            } else if (label.includes('%')) {
                                label += context.parsed.y + '%';
                            } else {
                                label += context.parsed.y + ' months';
                            }
                            
                            return label;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Utility functions
 */
function getROIValue(calc) {
    return calc.results?.roi_metrics?.first_year_roi || calc.results?.roi_percentage || 0;
}

function getPaybackValue(calc) {
    return calc.results?.roi_metrics?.payback_period_months || calc.results?.payback_months || 0;
}

function getAnnualSavings(calc) {
    return calc.results?.roi_metrics?.annual_savings || calc.results?.annual_savings || 0;
}

function getNPVValue(calc) {
    return calc.results?.financial_metrics?.npv || calc.results?.npv || 0;
}

function getMetricValue(calc, key) {
    switch (key) {
        case 'roi':
            return getROIValue(calc);
        case 'payback_months':
            return getPaybackValue(calc);
        case 'annual_savings':
            return getAnnualSavings(calc);
        case 'monthly_savings':
            return calc.results?.roi_metrics?.monthly_savings || 0;
        case 'npv':
            return getNPVValue(calc);
        case 'irr':
            return (calc.results?.financial_metrics?.irr || 0) * 100;
        case 'year_3_roi':
            return calc.results?.projections?.year_3?.roi_percentage || 0;
        case 'service_investment':
            return calc.service_investment || 0;
        case 'annual_revenue':
            return calc.annual_revenue || 0;
        default:
            return 0;
    }
}

function formatMetricValue(value, format) {
    switch (format) {
        case 'currency':
            return '$' + formatNumber(value);
        case 'percentage':
            return value.toFixed(1) + '%';
        case 'decimal':
            return value.toFixed(1);
        default:
            return value.toString();
    }
}

function isTopPerformer(index, metric, rankings) {
    return rankings[metric] && rankings[metric][0] === index;
}

function getDifferenceIndicator(differences, index, isInverse = false) {
    if (!differences || !differences[index]) {
        return '<i class="fas fa-equals arrow-icon arrow-equal"></i>';
    }
    
    const diff = differences[index];
    const absValue = Math.abs(diff);
    
    if (absValue < 0.1) {
        return '<i class="fas fa-equals arrow-icon arrow-equal"></i>';
    }
    
    let arrow, className, sign;
    if (diff > 0) {
        arrow = isInverse ? 'fas fa-arrow-down' : 'fas fa-arrow-up';
        className = isInverse ? 'arrow-down' : 'arrow-up';
        sign = '+';
    } else {
        arrow = isInverse ? 'fas fa-arrow-up' : 'fas fa-arrow-down';
        className = isInverse ? 'arrow-up' : 'arrow-down';
        sign = '';
    }
    
    return `
        <span class="metric-difference difference-${diff > 0 ? (isInverse ? 'worse' : 'better') : (isInverse ? 'better' : 'worse')}">
            ${sign}${absValue.toFixed(1)}%
        </span>
        <i class="${arrow} arrow-icon ${className}"></i>
    `;
}

function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    if (typeof num !== 'number') {
        num = parseFloat(num);
        if (isNaN(num)) return '0';
    }
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

function showLoading(show) {
    // Simple loading implementation
    const compareBtn = document.getElementById('compareBtn');
    if (show) {
        compareBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        compareBtn.disabled = true;
    } else {
        compareBtn.innerHTML = '<i class="fas fa-balance-scale"></i> Compare Selected';
        compareBtn.disabled = selectedCalculations.length < 2;
    }
}

function showError(message) {
    showToast(message, 'danger');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}