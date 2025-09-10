/**
 * Sensitivity Analysis JavaScript Module
 * Handles calculations, visualizations, and interactions for sensitivity analysis
 */

// Global variables to store analysis results
let sensitivityData = null;
let charts = {};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sensitivity Analysis module loaded');
});

/**
 * Load example data for testing
 */
async function loadExample(example) {
    try {
        const response = await fetch('/api/examples');
        const examples = await response.json();
        
        if (examples[example]) {
            const data = examples[example].data;
            
            // Populate form with example data
            document.getElementById('company_name').value = data.company_name;
            document.getElementById('annual_revenue').value = data.annual_revenue;
            document.getElementById('monthly_orders').value = data.monthly_orders;
            document.getElementById('avg_order_value').value = data.avg_order_value;
            document.getElementById('labor_costs').value = data.labor_costs;
            document.getElementById('shipping_costs').value = data.shipping_costs;
            document.getElementById('error_costs').value = data.error_costs;
            document.getElementById('inventory_costs').value = data.inventory_costs;
            document.getElementById('service_investment').value = data.service_investment;
            
            // Show success message
            showToast('Example data loaded successfully', 'success');
        }
    } catch (error) {
        console.error('Error loading example:', error);
        showError('Failed to load example data');
    }
}

/**
 * Main function to run sensitivity analysis
 */
async function runSensitivityAnalysis() {
    try {
        // Show loading modal
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();
        
        // Collect form data
        const formData = collectFormData();
        
        // Validate data
        if (!validateFormData(formData)) {
            loadingModal.hide();
            return;
        }
        
        // Call API
        const response = await fetch('/api/sensitivity-calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const data = await response.json();
        sensitivityData = data;
        
        // Hide loading modal
        loadingModal.hide();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Sensitivity analysis error:', error);
        document.getElementById('loadingModal').style.display = 'none';
        showError(error.message || 'Failed to run sensitivity analysis');
    }
}

/**
 * Collect form data
 */
function collectFormData() {
    return {
        company_name: document.getElementById('company_name').value || 'Sensitivity Analysis',
        annual_revenue: parseFloat(document.getElementById('annual_revenue').value),
        monthly_orders: parseFloat(document.getElementById('monthly_orders').value),
        avg_order_value: parseFloat(document.getElementById('avg_order_value').value),
        labor_costs: parseFloat(document.getElementById('labor_costs').value),
        shipping_costs: parseFloat(document.getElementById('shipping_costs').value),
        error_costs: parseFloat(document.getElementById('error_costs').value),
        inventory_costs: parseFloat(document.getElementById('inventory_costs').value),
        service_investment: parseFloat(document.getElementById('service_investment').value)
    };
}

/**
 * Validate form data
 */
function validateFormData(data) {
    const requiredFields = [
        'annual_revenue', 'monthly_orders', 'avg_order_value',
        'labor_costs', 'shipping_costs', 'error_costs', 
        'inventory_costs', 'service_investment'
    ];
    
    for (let field of requiredFields) {
        if (!data[field] || data[field] < 0) {
            showError(`Please provide a valid ${field.replace('_', ' ')}`);
            return false;
        }
    }
    
    return true;
}

/**
 * Display analysis results
 */
function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update summary
    updateSummary(data);
    
    // Create visualizations
    createTornadoDiagram(data);
    createRadarChart(data);
    createDistributionChart(data);
    createCorrelationMatrix(data);
    
    // Update tables
    updateRankingsTable(data);
    updateBreakEvenTable(data);
    updateMonteCarloResults(data);
    
    // Enable export button
    document.getElementById('pdfExportBtn').disabled = false;
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

/**
 * Update summary card
 */
function updateSummary(data) {
    const summaryCard = document.getElementById('summaryCard');
    const summaryContent = document.getElementById('summaryContent');
    
    const baseROI = data.base_roi;
    const topVariable = data.rankings[0];
    const monteCarloData = data.monte_carlo;
    
    summaryContent.innerHTML = `
        <div class="mb-3">
            <h6 class="text-primary">Base Case ROI</h6>
            <h4 class="text-success">${formatPercentage(baseROI)}%</h4>
        </div>
        <div class="mb-3">
            <h6 class="text-primary">Most Sensitive Variable</h6>
            <p class="mb-1"><strong>${topVariable[1]}</strong></p>
            <small class="text-muted">Coefficient: ${topVariable[2].toFixed(3)}</small>
        </div>
        <div class="mb-3">
            <h6 class="text-primary">Risk Assessment</h6>
            <p class="mb-1">Probability of Positive ROI: <strong>${formatPercentage(monteCarloData.risk_metrics.probability_positive * 100)}%</strong></p>
            <p class="mb-1">Probability of 15%+ ROI: <strong>${formatPercentage(monteCarloData.risk_metrics.probability_15_percent * 100)}%</strong></p>
        </div>
    `;
    
    summaryCard.style.display = 'block';
}

/**
 * Create tornado diagram showing variable impacts
 */
function createTornadoDiagram(data) {
    const ctx = document.getElementById('tornadoChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.tornado) {
        charts.tornado.destroy();
    }
    
    // Prepare data for tornado chart
    const variables = Object.keys(data.sensitivity_results);
    const labels = variables.map(v => data.sensitivity_results[v].label);
    
    // Get impact ranges for ±30% changes
    const positiveImpacts = [];
    const negativeImpacts = [];
    
    variables.forEach(variable => {
        const roiValues = data.sensitivity_results[variable].roi_values;
        const plus30 = roiValues.find(r => Math.abs(r.change_percent - 30) < 0.1);
        const minus30 = roiValues.find(r => Math.abs(r.change_percent - (-30)) < 0.1);
        
        const baseROI = data.base_roi;
        const positiveImpact = plus30 ? (plus30.roi - baseROI) : 0;
        const negativeImpact = minus30 ? (baseROI - minus30.roi) : 0;
        
        positiveImpacts.push(positiveImpact);
        negativeImpacts.push(-negativeImpact); // Negative for left side of tornado
    });
    
    charts.tornado = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '+30% Impact',
                data: positiveImpacts,
                backgroundColor: 'rgba(40, 167, 69, 0.8)',
                borderColor: 'rgba(40, 167, 69, 1)',
                borderWidth: 1
            }, {
                label: '-30% Impact',
                data: negativeImpacts,
                backgroundColor: 'rgba(220, 53, 69, 0.8)',
                borderColor: 'rgba(220, 53, 69, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'ROI Impact of ±30% Variable Changes',
                    color: '#fff'
                },
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        callback: function(value) {
                            return formatPercentage(Math.abs(value)) + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Create radar chart for multi-variable sensitivity
 */
function createRadarChart(data) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.radar) {
        charts.radar.destroy();
    }
    
    const variables = Object.keys(data.sensitivity_results);
    const labels = variables.map(v => data.sensitivity_results[v].label);
    const coefficients = variables.map(v => Math.abs(data.sensitivity_results[v].coefficient));
    
    charts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sensitivity Coefficient',
                data: coefficients,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Variable Sensitivity Overview',
                    color: '#fff'
                },
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff',
                        backdropColor: 'rgba(0, 0, 0, 0.5)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Create distribution chart for Monte Carlo results
 */
function createDistributionChart(data) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.distribution) {
        charts.distribution.destroy();
    }
    
    const distributionData = data.monte_carlo.distribution;
    const percentiles = data.monte_carlo.percentiles;
    
    // Create histogram bins
    const minROI = Math.min(...distributionData);
    const maxROI = Math.max(...distributionData);
    const binCount = 20;
    const binSize = (maxROI - minROI) / binCount;
    
    const bins = [];
    const binLabels = [];
    
    for (let i = 0; i < binCount; i++) {
        const binStart = minROI + (i * binSize);
        const binEnd = binStart + binSize;
        const count = distributionData.filter(roi => roi >= binStart && roi < binEnd).length;
        
        bins.push(count);
        binLabels.push(`${formatPercentage(binStart)}%-${formatPercentage(binEnd)}%`);
    }
    
    charts.distribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: binLabels,
            datasets: [{
                label: 'Frequency',
                data: bins,
                backgroundColor: 'rgba(255, 159, 64, 0.8)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'ROI Distribution (1000 Monte Carlo Simulations)',
                    color: '#fff'
                },
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#fff',
                        maxRotation: 45
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Create correlation matrix heat map
 */
function createCorrelationMatrix(data) {
    const ctx = document.getElementById('correlationChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.correlation) {
        charts.correlation.destroy();
    }
    
    // For now, create a placeholder correlation matrix
    // In a real implementation, this would analyze correlations between variables
    const variables = Object.keys(data.sensitivity_results);
    const correlationData = [];
    
    variables.forEach((var1, i) => {
        variables.forEach((var2, j) => {
            // Simulate correlation (in reality, this would be calculated from data)
            let correlation;
            if (i === j) {
                correlation = 1.0; // Perfect correlation with itself
            } else {
                // Revenue variables positively correlated, cost variables negatively correlated
                const var1IsRevenue = ['annual_revenue', 'monthly_orders', 'avg_order_value'].includes(var1);
                const var2IsRevenue = ['annual_revenue', 'monthly_orders', 'avg_order_value'].includes(var2);
                
                if (var1IsRevenue === var2IsRevenue) {
                    correlation = 0.3 + Math.random() * 0.4; // 0.3 to 0.7
                } else {
                    correlation = -0.1 - Math.random() * 0.3; // -0.1 to -0.4
                }
            }
            
            correlationData.push({
                x: j,
                y: i,
                v: correlation
            });
        });
    });
    
    charts.correlation = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Correlation',
                data: correlationData,
                backgroundColor: function(context) {
                    const value = context.parsed.v;
                    const alpha = Math.abs(value);
                    if (value > 0) {
                        return `rgba(40, 167, 69, ${alpha})`;
                    } else {
                        return `rgba(220, 53, 69, ${Math.abs(alpha)})`;
                    }
                },
                pointRadius: function(context) {
                    return Math.abs(context.parsed.v) * 20 + 5;
                }
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Variable Correlation Matrix (Estimated)',
                    color: '#fff'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const point = context[0];
                            return `${variables[point.parsed.y]} vs ${variables[point.parsed.x]}`;
                        },
                        label: function(context) {
                            return `Correlation: ${context.parsed.v.toFixed(3)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: -0.5,
                    max: variables.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        color: '#fff',
                        callback: function(value) {
                            return variables[value] ? data.sensitivity_results[variables[value]].label : '';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: variables.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        color: '#fff',
                        callback: function(value) {
                            return variables[value] ? data.sensitivity_results[variables[value]].label : '';
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Update rankings table
 */
function updateRankingsTable(data) {
    const container = document.getElementById('rankingsTable');
    
    let html = `
        <div class="table-responsive">
            <table class="table table-dark table-striped">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Variable</th>
                        <th>Sensitivity Coefficient</th>
                        <th>Impact Level</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.rankings.forEach((ranking, index) => {
        const [variable, label, coefficient] = ranking;
        const impactLevel = getImpactLevel(Math.abs(coefficient));
        const impactClass = getImpactClass(Math.abs(coefficient));
        
        html += `
            <tr>
                <td><span class="badge bg-secondary">${index + 1}</span></td>
                <td>${label}</td>
                <td>${coefficient.toFixed(3)}</td>
                <td><span class="badge ${impactClass}">${impactLevel}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

/**
 * Update break-even table
 */
function updateBreakEvenTable(data) {
    const container = document.getElementById('breakEvenTable');
    
    let html = `
        <div class="table-responsive">
            <table class="table table-dark table-striped">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Break-even Point</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    Object.keys(data.sensitivity_results).forEach(variable => {
        const result = data.sensitivity_results[variable];
        const breakEvenPercent = result.break_even_percent;
        
        let breakEvenText, riskClass, riskText;
        
        if (breakEvenPercent === null) {
            breakEvenText = 'No break-even found';
            riskClass = 'bg-success';
            riskText = 'Very Low Risk';
        } else if (Math.abs(breakEvenPercent) > 50) {
            breakEvenText = `${formatPercentage(breakEvenPercent)}%`;
            riskClass = 'bg-success';
            riskText = 'Low Risk';
        } else if (Math.abs(breakEvenPercent) > 25) {
            breakEvenText = `${formatPercentage(breakEvenPercent)}%`;
            riskClass = 'bg-warning';
            riskText = 'Medium Risk';
        } else {
            breakEvenText = `${formatPercentage(breakEvenPercent)}%`;
            riskClass = 'bg-danger';
            riskText = 'High Risk';
        }
        
        html += `
            <tr>
                <td>${result.label}</td>
                <td>${breakEvenText}</td>
                <td><span class="badge ${riskClass}">${riskText}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

/**
 * Update Monte Carlo results
 */
function updateMonteCarloResults(data) {
    const container = document.getElementById('monteCarloResults');
    const mc = data.monte_carlo;
    
    container.innerHTML = `
        <div class="row text-center">
            <div class="col-md-6 mb-3">
                <div class="metric-card">
                    <h4 class="text-primary">${formatPercentage(mc.mean_roi)}%</h4>
                    <p class="mb-0">Mean ROI</p>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="metric-card">
                    <h4 class="text-success">${formatPercentage(mc.risk_metrics.probability_positive * 100)}%</h4>
                    <p class="mb-0">Probability Positive ROI</p>
                </div>
            </div>
        </div>
        <div class="row text-center">
            <div class="col-md-6 mb-3">
                <div class="metric-card">
                    <h4 class="text-warning">${formatPercentage(mc.percentiles.p10)}%</h4>
                    <p class="mb-0">10th Percentile (VaR)</p>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="metric-card">
                    <h4 class="text-info">${formatPercentage(mc.percentiles.p90)}%</h4>
                    <p class="mb-0">90th Percentile</p>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <h6>Risk Percentiles:</h6>
                <ul class="list-unstyled">
                    <li>25th percentile: ${formatPercentage(mc.percentiles.p25)}%</li>
                    <li>50th percentile (median): ${formatPercentage(mc.percentiles.p50)}%</li>
                    <li>75th percentile: ${formatPercentage(mc.percentiles.p75)}%</li>
                </ul>
            </div>
        </div>
    `;
}

/**
 * Export chart as image
 */
function exportChart(chartId) {
    const chart = charts[chartId.replace('Chart', '')];
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}.png`;
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Export data to CSV
 */
function exportToCSV() {
    if (!sensitivityData) return;
    
    let csvContent = "Variable,Label,Sensitivity Coefficient,Break-even Point\n";
    
    Object.keys(sensitivityData.sensitivity_results).forEach(variable => {
        const result = sensitivityData.sensitivity_results[variable];
        csvContent += `${variable},${result.label},${result.coefficient},${result.break_even_percent || 'N/A'}\n`;
    });
    
    downloadFile(csvContent, 'sensitivity_analysis.csv', 'text/csv');
}

/**
 * Export data to JSON
 */
function exportToJSON() {
    if (!sensitivityData) return;
    
    const jsonContent = JSON.stringify(sensitivityData, null, 2);
    downloadFile(jsonContent, 'sensitivity_analysis.json', 'application/json');
}

/**
 * Export to PDF (placeholder - would need backend implementation)
 */
function exportToPDF() {
    showToast('PDF export functionality would be implemented with backend support', 'info');
}

/**
 * Helper Functions
 */

function getImpactLevel(coefficient) {
    if (coefficient > 2.0) return 'Very High';
    if (coefficient > 1.0) return 'High';
    if (coefficient > 0.5) return 'Medium';
    if (coefficient > 0.1) return 'Low';
    return 'Very Low';
}

function getImpactClass(coefficient) {
    if (coefficient > 2.0) return 'bg-danger';
    if (coefficient > 1.0) return 'bg-warning';
    if (coefficient > 0.5) return 'bg-info';
    return 'bg-secondary';
}

function formatPercentage(value) {
    return Math.round(value * 100) / 100;
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    errorModal.show();
}

function showToast(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}