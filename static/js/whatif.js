/**
 * What-If Analysis JavaScript
 * Interactive ROI calculator with real-time adjustments
 */

// Global variables
let baselineData = null;
let currentData = null;
let baselineResults = null;
let currentResults = null;
let examples = {};
let impactChart = null;
let presetScenarios = {};

// Predefined scenarios
const scenarioPresets = {
    worst: {
        name: 'Worst Case',
        description: 'Conservative estimates with challenges',
        multipliers: {
            annual_revenue: 0.85,
            monthly_orders: 0.80,
            avg_order_value: 0.90,
            labor_costs: 1.20,
            shipping_costs: 1.15,
            error_costs: 1.30,
            inventory_costs: 1.25,
            service_investment: 1.20
        }
    },
    likely: {
        name: 'Most Likely',
        description: 'Realistic expectations',
        multipliers: {
            annual_revenue: 1.0,
            monthly_orders: 1.0,
            avg_order_value: 1.0,
            labor_costs: 1.0,
            shipping_costs: 1.0,
            error_costs: 1.0,
            inventory_costs: 1.0,
            service_investment: 1.0
        }
    },
    best: {
        name: 'Best Case',
        description: 'Optimistic projections',
        multipliers: {
            annual_revenue: 1.15,
            monthly_orders: 1.20,
            avg_order_value: 1.10,
            labor_costs: 0.85,
            shipping_costs: 0.90,
            error_costs: 0.70,
            inventory_costs: 0.80,
            service_investment: 0.90
        }
    }
};

// Variable definitions with display names and ranges
const variables = [
    {
        key: 'annual_revenue',
        name: 'Annual Revenue',
        icon: 'fas fa-chart-line',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'monthly_orders',
        name: 'Monthly Orders',
        icon: 'fas fa-shopping-cart',
        format: 'number',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'avg_order_value',
        name: 'Average Order Value',
        icon: 'fas fa-dollar-sign',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'labor_costs',
        name: 'Labor Costs',
        icon: 'fas fa-users',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'shipping_costs',
        name: 'Shipping Costs',
        icon: 'fas fa-shipping-fast',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'error_costs',
        name: 'Error Costs',
        icon: 'fas fa-bug',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'inventory_costs',
        name: 'Inventory Costs',
        icon: 'fas fa-boxes',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    },
    {
        key: 'service_investment',
        name: 'Service Investment',
        icon: 'fas fa-handshake',
        format: 'currency',
        min: 0.5,
        max: 1.5,
        step: 0.01
    }
];

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing What-If Analysis...');
    
    // Check for loader utilities
    if (typeof fetchWithLoader === 'undefined') {
        console.error('Loader utilities not found. Loading fallback...');
        // Define fallback fetch function
        window.fetchWithLoader = async function(url, options, message) {
            console.log(message);
            const response = await fetch(url, options);
            return await response.json();
        };
    }
    
    loadExamples();
    loadPresetScenarios();
});

/**
 * Load example scenarios from API
 */
async function loadExamples() {
    try {
        examples = await fetchWithLoader('/api/examples', {}, 'Loading examples...');
    } catch (error) {
        console.error('Error loading examples:', error);
        // Error already shown by fetchWithLoader
    }
}

/**
 * Load preset scenarios
 */
async function loadPresetScenarios() {
    try {
        const response = await fetch('/api/whatif-scenarios');
        presetScenarios = await response.json();
        displayPresetScenarios();
    } catch (error) {
        console.error('Error loading preset scenarios:', error);
    }
}

/**
 * Display preset scenarios
 */
function displayPresetScenarios() {
    const container = document.getElementById('presetScenarios');
    
    let html = '';
    Object.keys(presetScenarios).forEach(key => {
        const scenario = presetScenarios[key];
        html += `
            <div class="scenario-card card d-inline-block me-2" style="width: 200px; vertical-align: top;" onclick="applyPresetScenario('${key}')">
                <div class="card-body p-2">
                    <h6 class="card-title mb-1" style="font-size: 0.9rem;">${scenario.name}</h6>
                    <p class="card-text small text-muted mb-0" style="font-size: 0.8rem;">${scenario.description}</p>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Load baseline example
 */
function loadBaselineExample(exampleKey) {
    if (!examples[exampleKey]) {
        showToast('Example not found', 'error');
        return;
    }
    
    const example = examples[exampleKey];
    baselineData = { ...example.data };
    
    calculateBaseline();
    showToast(`Loaded ${example.name} as baseline`, 'success');
}

/**
 * Show baseline input form
 */
function showBaselineInputForm() {
    document.getElementById('baselineInputForm').style.display = 'block';
}

/**
 * Set baseline from manual input
 */
function setBaseline() {
    const form = document.getElementById('baselineForm');
    const formData = new FormData(form);
    
    baselineData = {};
    for (const [key, value] of formData.entries()) {
        const cleanKey = key.replace('baseline_', '');
        baselineData[cleanKey] = parseFloat(value);
    }
    
    baselineData.company_name = 'What-If Baseline';
    
    if (validateBaselineData()) {
        calculateBaseline();
        document.getElementById('baselineInputForm').style.display = 'none';
        showToast('Baseline data set successfully', 'success');
    }
}

/**
 * Validate baseline data
 */
function validateBaselineData() {
    const required = ['annual_revenue', 'monthly_orders', 'avg_order_value', 'labor_costs', 'shipping_costs', 'error_costs', 'inventory_costs', 'service_investment'];
    
    for (const field of required) {
        if (!baselineData[field] || baselineData[field] <= 0) {
            showToast(`Invalid value for ${field}`, 'error');
            return false;
        }
    }
    
    return true;
}

/**
 * Calculate baseline ROI
 */
async function calculateBaseline() {
    if (!baselineData) return;
    
    // Don't show loading for baseline calculation as it's fast
    try {
        const response = await fetch('/api/whatif-calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(baselineData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            baselineResults = result.results;
            currentData = { ...baselineData };
            currentResults = { ...result.results };
            
            setupWhatIfInterface();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Error calculating baseline:', error);
        showToast('Error calculating baseline: ' + error.message, 'error');
    }
}

/**
 * Setup what-if interface
 */
function setupWhatIfInterface() {
    generateVariableControls();
    updateResults();
    initializeChart();
    document.getElementById('whatifInterface').style.display = 'block';
    
    // Calculate all three scenarios
    calculateAllScenarios();
}

/**
 * Generate variable control sliders
 */
function generateVariableControls() {
    const container = document.getElementById('variableControls');
    
    let html = '';
    variables.forEach(variable => {
        const currentValue = currentData[variable.key];
        const baselineValue = baselineData[variable.key];
        const percentage = ((currentValue - baselineValue) / baselineValue) * 100;
        
        html += `
            <div class="col-lg-4 col-md-6 mb-3">
                <div class="slider-container">
                    <div class="slider-label">
                        <div>
                            <i class="${variable.icon} me-2"></i>
                            <strong>${variable.name}</strong>
                        </div>
                        <div class="slider-value" id="value_${variable.key}">
                            ${formatValue(currentValue, variable.format)}
                            <span class="impact-indicator ms-2" id="impact_${variable.key}">
                                (${percentage >= 0 ? '+' : ''}${percentage.toFixed(1)}%)
                            </span>
                        </div>
                    </div>
                    <input type="range" class="range-input mt-2" 
                           id="slider_${variable.key}"
                           min="${variable.min}" 
                           max="${variable.max}" 
                           step="${variable.step}" 
                           value="1.0"
                           oninput="updateVariable('${variable.key}', this.value)">
                    <div class="d-flex justify-content-between small text-muted mt-1">
                        <span>-50%</span>
                        <span class="text-primary">Baseline</span>
                        <span>+50%</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Update variable value and recalculate
 */
async function updateVariable(variableKey, multiplier) {
    const baselineValue = baselineData[variableKey];
    const newValue = baselineValue * parseFloat(multiplier);
    
    currentData[variableKey] = newValue;
    
    // Update display
    updateVariableDisplay(variableKey, newValue, multiplier);
    
    // Recalculate with debouncing
    debounceRecalculate();
}

/**
 * Update variable display
 */
function updateVariableDisplay(variableKey, newValue, multiplier) {
    const variable = variables.find(v => v.key === variableKey);
    const baselineValue = baselineData[variableKey];
    const percentage = ((newValue - baselineValue) / baselineValue) * 100;
    
    // Update value display
    const valueEl = document.getElementById(`value_${variableKey}`);
    const impactEl = document.getElementById(`impact_${variableKey}`);
    
    valueEl.innerHTML = `
        ${formatValue(newValue, variable.format)}
        <span class="impact-indicator ms-1 ${getImpactClass(percentage)}" id="impact_${variableKey}">
            (${percentage >= 0 ? '+' : ''}${percentage.toFixed(1)}%)
        </span>
    `;
}

/**
 * Get CSS class for impact indicator
 */
function getImpactClass(percentage) {
    if (Math.abs(percentage) < 0.1) return 'impact-neutral';
    return percentage > 0 ? 'impact-positive' : 'impact-negative';
}

/**
 * Debounced recalculation
 */
let recalculateTimeout;
function debounceRecalculate() {
    clearTimeout(recalculateTimeout);
    recalculateTimeout = setTimeout(recalculateROI, 300);
}

/**
 * Recalculate ROI with current data
 */
async function recalculateROI() {
    try {
        const response = await fetch('/api/whatif-calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentResults = result.results;
            updateResults();
        }
    } catch (error) {
        console.error('Error recalculating:', error);
    }
}

/**
 * Update all results displays
 */
function updateResults() {
    updateBaselineComparison();
    updateCurrentResults();
    updateSensitivityAnalysis();
    updateChart();
}

/**
 * Update baseline comparison
 */
function updateBaselineComparison() {
    const container = document.getElementById('comparisonMetrics');
    
    const baselineROI = baselineResults.roi_metrics.first_year_roi;
    const currentROI = currentResults.roi_metrics.first_year_roi;
    const roiDiff = currentROI - baselineROI;
    
    const baselineSavings = baselineResults.roi_metrics.annual_savings;
    const currentSavings = currentResults.roi_metrics.annual_savings;
    const savingsDiff = currentSavings - baselineSavings;
    
    const baselinePayback = baselineResults.roi_metrics.payback_period_months;
    const currentPayback = currentResults.roi_metrics.payback_period_months;
    const paybackDiff = currentPayback - baselinePayback;
    
    const baselineNPV = baselineResults.financial_metrics.npv;
    const currentNPV = currentResults.financial_metrics.npv;
    const npvDiff = currentNPV - baselineNPV;
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <div class="comparison-metric">
                    <div class="d-flex justify-content-between">
                        <span>ROI:</span>
                        <div>
                            <span class="fw-bold">${currentROI.toFixed(1)}%</span>
                            <span class="impact-indicator ms-1 ${getImpactClass(roiDiff)}">
                                (${roiDiff >= 0 ? '+' : ''}${roiDiff.toFixed(1)}%)
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="comparison-metric">
                    <div class="d-flex justify-content-between">
                        <span>Annual Savings:</span>
                        <div>
                            <span class="fw-bold">${formatCurrency(currentSavings)}</span>
                            <span class="impact-indicator ms-1 ${getImpactClass(savingsDiff)}">
                                (${savingsDiff >= 0 ? '+' : ''}${formatCurrency(savingsDiff)})
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="comparison-metric">
                    <div class="d-flex justify-content-between">
                        <span>Payback:</span>
                        <div>
                            <span class="fw-bold">${currentPayback.toFixed(1)} mo</span>
                            <span class="impact-indicator ms-1 ${getImpactClass(-paybackDiff)}">
                                (${paybackDiff >= 0 ? '+' : ''}${paybackDiff.toFixed(1)} mo)
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="comparison-metric">
                    <div class="d-flex justify-content-between">
                        <span>NPV:</span>
                        <div>
                            <span class="fw-bold">${formatCurrency(currentNPV)}</span>
                            <span class="impact-indicator ms-1 ${getImpactClass(npvDiff)}">
                                (${npvDiff >= 0 ? '+' : ''}${formatCurrency(npvDiff)})
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Update current results display
 */
function updateCurrentResults() {
    const container = document.getElementById('currentResults');
    const roi = currentResults.roi_metrics;
    const financial = currentResults.financial_metrics;
    const projections = currentResults.projections;
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-chart-bar me-2"></i>Key Metrics</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <tbody>
                            <tr>
                                <td>First Year ROI</td>
                                <td class="fw-bold">${roi.first_year_roi.toFixed(1)}%</td>
                            </tr>
                            <tr>
                                <td>Annual Savings</td>
                                <td class="fw-bold">${formatCurrency(roi.annual_savings)}</td>
                            </tr>
                            <tr>
                                <td>Monthly Savings</td>
                                <td class="fw-bold">${formatCurrency(roi.monthly_savings)}</td>
                            </tr>
                            <tr>
                                <td>Payback Period</td>
                                <td class="fw-bold">${roi.payback_period_text}</td>
                            </tr>
                            <tr>
                                <td>Net Present Value</td>
                                <td class="fw-bold">${formatCurrency(financial.npv)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-chart-line me-2"></i>3-Year Projections</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Year</th>
                                <th>ROI</th>
                                <th>Cumulative Savings</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Year 1</td>
                                <td>${projections.year_1.roi_percentage.toFixed(1)}%</td>
                                <td>${formatCurrency(projections.year_1.cumulative_savings)}</td>
                            </tr>
                            <tr>
                                <td>Year 2</td>
                                <td>${projections.year_2.roi_percentage.toFixed(1)}%</td>
                                <td>${formatCurrency(projections.year_2.cumulative_savings)}</td>
                            </tr>
                            <tr>
                                <td>Year 3</td>
                                <td>${projections.year_3.roi_percentage.toFixed(1)}%</td>
                                <td>${formatCurrency(projections.year_3.cumulative_savings)}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

/**
 * Update sensitivity analysis
 */
function updateSensitivityAnalysis() {
    const container = document.getElementById('sensitivityAnalysis');
    
    // Calculate sensitivity for each variable
    const sensitivities = [];
    
    variables.forEach(variable => {
        const currentValue = currentData[variable.key];
        const baselineValue = baselineData[variable.key];
        const variableChange = ((currentValue - baselineValue) / baselineValue) * 100;
        
        if (Math.abs(variableChange) > 0.1) {
            const baselineROI = baselineResults.roi_metrics.first_year_roi;
            const currentROI = currentResults.roi_metrics.first_year_roi;
            const roiChange = currentROI - baselineROI;
            
            const sensitivity = variableChange !== 0 ? (roiChange / variableChange) : 0;
            
            sensitivities.push({
                variable: variable.name,
                icon: variable.icon,
                variableChange: variableChange,
                roiChange: roiChange,
                sensitivity: sensitivity
            });
        }
    });
    
    // Sort by absolute sensitivity
    sensitivities.sort((a, b) => Math.abs(b.sensitivity) - Math.abs(a.sensitivity));
    
    let html = '<p class="mb-3">Impact of current changes on ROI:</p>';
    
    if (sensitivities.length === 0) {
        html += '<p class="text-muted">No changes detected from baseline.</p>';
    } else {
        sensitivities.forEach(item => {
            html += `
                <div class="sensitivity-item">
                    <div>
                        <i class="${item.icon} me-2"></i>
                        <span>${item.variable}: ${item.variableChange >= 0 ? '+' : ''}${item.variableChange.toFixed(1)}%</span>
                    </div>
                    <div class="impact-indicator ${getImpactClass(item.roiChange)}">
                        ROI ${item.roiChange >= 0 ? '+' : ''}${item.roiChange.toFixed(1)}%
                        ${Math.abs(item.sensitivity) > 0.01 ? `(${item.sensitivity.toFixed(2)}x)` : ''}
                    </div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

/**
 * Initialize Chart.js impact chart
 */
function initializeChart() {
    const ctx = document.getElementById('impactChart').getContext('2d');
    
    impactChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['ROI', 'Annual Savings', 'Payback Period', 'NPV'],
            datasets: [{
                label: 'Baseline',
                data: [0, 0, 0, 0],
                backgroundColor: 'rgba(108, 117, 125, 0.7)',
                borderColor: 'rgba(108, 117, 125, 1)',
                borderWidth: 1
            }, {
                label: 'Current',
                data: [0, 0, 0, 0],
                backgroundColor: 'rgba(0, 123, 255, 0.7)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Baseline vs Current Comparison'
                },
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                }
            }
        }
    });
    
    updateChart();
}

/**
 * Update chart with current data
 */
function updateChart() {
    if (!impactChart) return;
    
    const baselineROI = baselineResults.roi_metrics.first_year_roi;
    const currentROI = currentResults.roi_metrics.first_year_roi;
    
    const baselineSavings = baselineResults.roi_metrics.annual_savings / 1000; // Convert to thousands
    const currentSavings = currentResults.roi_metrics.annual_savings / 1000;
    
    const baselinePayback = baselineResults.roi_metrics.payback_period_months;
    const currentPayback = currentResults.roi_metrics.payback_period_months;
    
    const baselineNPV = baselineResults.financial_metrics.npv / 1000; // Convert to thousands
    const currentNPV = currentResults.financial_metrics.npv / 1000;
    
    impactChart.data.datasets[0].data = [baselineROI, baselineSavings, baselinePayback, baselineNPV];
    impactChart.data.datasets[1].data = [currentROI, currentSavings, currentPayback, currentNPV];
    
    // Update colors based on improvement
    const improvements = [
        currentROI > baselineROI,
        currentSavings > baselineSavings,
        currentPayback < baselinePayback, // Lower is better for payback
        currentNPV > baselineNPV
    ];
    
    const colors = improvements.map(improved => 
        improved ? 'rgba(40, 167, 69, 0.7)' : 'rgba(220, 53, 69, 0.7)'
    );
    
    impactChart.data.datasets[1].backgroundColor = colors;
    impactChart.update();
}

/**
 * Apply preset scenario
 */
function applyPresetScenario(scenarioKey) {
    const scenario = presetScenarios[scenarioKey];
    if (!scenario) return;
    
    // Remove active class from all scenarios
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to selected scenario
    event.target.closest('.scenario-card').classList.add('active');
    
    // Apply adjustments
    Object.keys(scenario.adjustments).forEach(key => {
        const multiplier = scenario.adjustments[key];
        currentData[key] = baselineData[key] * multiplier;
        
        // Update slider
        const slider = document.getElementById(`slider_${key}`);
        if (slider) {
            slider.value = multiplier;
            updateVariableDisplay(key, currentData[key], multiplier);
        }
    });
    
    // Recalculate
    recalculateROI();
    showToast(`Applied ${scenario.name}`, 'success');
}

/**
 * Reset to baseline
 */
function resetToBaseline() {
    // Remove active class from scenarios
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Reset all variables
    variables.forEach(variable => {
        currentData[variable.key] = baselineData[variable.key];
        
        const slider = document.getElementById(`slider_${variable.key}`);
        if (slider) {
            slider.value = 1.0;
            updateVariableDisplay(variable.key, currentData[variable.key], 1.0);
        }
    });
    
    // Reset results
    currentResults = { ...baselineResults };
    updateResults();
    
    showToast('Reset to baseline values', 'info');
}

/**
 * Save current scenario
 */
function saveScenario() {
    // Clear the form
    document.getElementById('scenarioName').value = '';
    document.getElementById('scenarioNotes').value = '';
    document.getElementById('scenarioTags').value = 'what-if';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('saveScenarioModal'));
    modal.show();
}

/**
 * Confirm save scenario
 */
async function confirmSaveScenario() {
    const name = document.getElementById('scenarioName').value || 'What-If Scenario';
    const notes = document.getElementById('scenarioNotes').value || '';
    const tags = document.getElementById('scenarioTags').value || 'what-if';
    
    const dataToSave = {
        ...currentData,
        company_name: name,
        results: currentResults,
        notes: notes,
        tags: tags
    };
    
    // Hide modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('saveScenarioModal'));
    modal.hide();
    
    try {
        const response = await fetch('/api/whatif-save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToSave)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Scenario saved successfully!', 'success');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('Error saving scenario:', error);
        showToast('Error saving scenario: ' + error.message, 'error');
    }
}

/**
 * Format value based on type
 */
function formatValue(value, format) {
    if (format === 'currency') {
        return formatCurrency(value);
    } else if (format === 'number') {
        return formatNumber(value);
    }
    return value.toString();
}

/**
 * Format currency
 */
function formatCurrency(num) {
    if (typeof num !== 'number') return '$0';
    return '$' + formatNumber(num);
}

/**
 * Format number with commas
 */
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

/**
 * Show loading modal
 */
function showLoading(show, message = 'Processing...') {
    // Use loaderManager if available, otherwise handle locally
    if (typeof loaderManager !== 'undefined') {
        if (show) {
            loaderManager.showLoader(message);
        } else {
            loaderManager.hideLoader();
        }
        return;
    }
    
    const modal = document.getElementById('loadingModal');
    if (!modal) return;
    const modalBody = modal.querySelector('.modal-body p');
    
    if (show) {
        if (modalBody) modalBody.textContent = message;
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) bsModal.hide();
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Create container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Apply a predefined scenario (worst, likely, best)
 */
async function applyScenario(scenarioType) {
    if (!baselineData) {
        showToast('Please set baseline data first', 'warning');
        return;
    }
    
    const scenario = scenarioPresets[scenarioType];
    if (!scenario) return;
    
    // Apply multipliers to current data
    Object.keys(scenario.multipliers).forEach(key => {
        if (baselineData[key]) {
            currentData[key] = baselineData[key] * scenario.multipliers[key];
            
            // Update slider if it exists
            const slider = document.getElementById(`slider_${key}`);
            if (slider) {
                slider.value = scenario.multipliers[key];
            }
        }
    });
    
    // Recalculate and update display
    await calculateWhatIf();
    generateVariableControls();
    showToast(`Applied ${scenario.name} scenario`, 'success');
}

/**
 * Calculate all three scenarios and display results
 */
async function calculateAllScenarios() {
    if (!baselineData) return;
    
    // Calculate each scenario
    for (const [type, scenario] of Object.entries(scenarioPresets)) {
        const scenarioData = {};
        
        // Apply multipliers
        Object.keys(scenario.multipliers).forEach(key => {
            if (baselineData[key]) {
                scenarioData[key] = baselineData[key] * scenario.multipliers[key];
            }
        });
        
        // Calculate ROI for this scenario
        try {
            const response = await fetch('/api/whatif-calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scenarioData)
            });
            
            const results = await response.json();
            
            // Update display for this scenario
            updateScenarioDisplay(type, results);
        } catch (error) {
            console.error(`Error calculating ${type} scenario:`, error);
        }
    }
}

/**
 * Update scenario display with results
 */
function updateScenarioDisplay(type, results) {
    if (!results || !results.roi_metrics) return;
    
    const roi = (results.roi_metrics.first_year_roi * 100).toFixed(1);
    const payback = results.roi_metrics.payback_period_months.toFixed(1);
    const savings = results.roi_metrics.annual_savings;
    
    document.getElementById(`${type}-roi`).textContent = `${roi}%`;
    document.getElementById(`${type}-payback`).textContent = `${payback} months`;
    document.getElementById(`${type}-savings`).textContent = `$${savings.toLocaleString()}`;
}

// Export functions for global use
window.loadBaselineExample = loadBaselineExample;
window.showBaselineInputForm = showBaselineInputForm;
window.setBaseline = setBaseline;
window.updateVariable = updateVariable;
window.applyPresetScenario = applyPresetScenario;
window.resetToBaseline = resetToBaseline;
window.saveScenario = saveScenario;
window.confirmSaveScenario = confirmSaveScenario;
window.applyScenario = applyScenario;