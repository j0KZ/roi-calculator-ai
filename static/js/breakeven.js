/**
 * Break-Even Analysis JavaScript
 * Handles comprehensive break-even calculations and visualizations
 */

class BreakEvenAnalyzer {
    constructor() {
        this.currentResults = null;
        this.charts = {};
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('breakevenForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performAnalysis();
        });

        // Load example data
        document.getElementById('loadExample').addEventListener('click', () => {
            this.loadExampleData();
        });

        // Auto-calculate on input changes (debounced)
        const inputs = document.querySelectorAll('#breakevenForm input');
        inputs.forEach(input => {
            let timeout;
            input.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    if (this.currentResults) {
                        this.performQuickAnalysis();
                    }
                }, 1000);
            });
        });
    }

    loadExampleData() {
        // Load medium business example
        document.getElementById('annual_revenue').value = '2000000';
        document.getElementById('monthly_orders').value = '5000';
        document.getElementById('avg_order_value').value = '33.33';
        document.getElementById('labor_costs').value = '8000';
        document.getElementById('shipping_costs').value = '5000';
        document.getElementById('error_costs').value = '2000';
        document.getElementById('inventory_costs').value = '3000';
        document.getElementById('service_investment').value = '50000';
    }

    getFormData() {
        return {
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

    async performAnalysis() {
        const data = this.getFormData();
        
        if (!this.validateInputs(data)) {
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/breakeven-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            this.currentResults = results;
            
            this.hideLoading();
            this.displayResults(results);

        } catch (error) {
            console.error('Break-even analysis error:', error);
            this.hideLoading();
            this.showError('Failed to perform break-even analysis: ' + error.message);
        }
    }

    async performQuickAnalysis() {
        const data = this.getFormData();
        
        try {
            const response = await fetch('/api/breakeven-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const results = await response.json();
                this.updateSummaryMetrics(results.key_metrics);
            }
        } catch (error) {
            console.warn('Quick analysis failed:', error);
        }
    }

    validateInputs(data) {
        const errors = [];

        Object.entries(data).forEach(([key, value]) => {
            if (isNaN(value) || value < 0) {
                errors.push(`${key.replace('_', ' ')} must be a positive number`);
            }
        });

        if (errors.length > 0) {
            this.showError(errors.join('<br>'));
            return false;
        }

        return true;
    }

    showLoading() {
        document.getElementById('loadingSpinner').classList.remove('d-none');
        document.getElementById('resultsSection').classList.add('d-none');
    }

    hideLoading() {
        document.getElementById('loadingSpinner').classList.add('d-none');
        document.getElementById('resultsSection').classList.remove('d-none');
    }

    displayResults(results) {
        this.displaySummaryMetrics(results);
        this.displayBreakevenPoints(results.breakeven_points);
        this.displayTimeline(results.time_to_breakeven);
        this.displaySensitivityAnalysis(results.sensitivity_analysis);
        this.displayScenarios(results.scenario_comparisons);
        this.displayRiskAssessment(results.risk_assessment);
    }

    displaySummaryMetrics(results) {
        const summaryHTML = `
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-primary">${results.time_to_breakeven?.basic_payback_months?.toFixed(1) || 'N/A'}</h4>
                    <small class="text-muted">Months to Break-Even</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-${this.getRiskLevelClass(results.risk_assessment?.risk_level)}">${results.risk_assessment?.risk_level || 'N/A'}</h4>
                    <small class="text-muted">Risk Level</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-info">${results.uncertainty_analysis?.probability_positive_roi || 'N/A'}%</h4>
                    <small class="text-muted">Probability Positive ROI</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-success">${Object.keys(results.breakeven_points || {}).length}</h4>
                    <small class="text-muted">Variables Analyzed</small>
                </div>
            </div>
        `;
        
        document.getElementById('summaryMetrics').innerHTML = summaryHTML;
    }

    updateSummaryMetrics(metrics) {
        const paybackElement = document.querySelector('#summaryMetrics .col-md-3:first-child h4');
        const riskElement = document.querySelector('#summaryMetrics .col-md-3:nth-child(2) h4');
        
        if (paybackElement && metrics.payback_months) {
            paybackElement.textContent = metrics.payback_months.toFixed(1);
        }
        
        if (riskElement && metrics.risk_level) {
            riskElement.textContent = metrics.risk_level;
            riskElement.className = `text-${this.getRiskLevelClass(metrics.risk_level)}`;
        }
    }

    getRiskLevelClass(riskLevel) {
        switch(riskLevel) {
            case 'LOW': return 'success';
            case 'MEDIUM': return 'warning';
            case 'HIGH': return 'danger';
            default: return 'secondary';
        }
    }

    displayBreakevenPoints(breakeven_points) {
        if (!breakeven_points) return;

        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Variable</th>
                            <th>Current Value</th>
                            <th>Break-Even Value</th>
                            <th>Change Required</th>
                            <th>Interpretation</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(breakeven_points).map(([variable, data]) => `
                            <tr>
                                <td><strong>${this.formatVariableName(variable)}</strong></td>
                                <td>$${this.formatNumber(data.original_value)}</td>
                                <td>$${this.formatNumber(data.breakeven_value)}</td>
                                <td class="text-${data.change_percentage >= 0 ? 'success' : 'danger'}">
                                    ${data.change_percentage >= 0 ? '+' : ''}${data.change_percentage?.toFixed(1) || 'N/A'}%
                                </td>
                                <td><small>${data.interpretation || 'N/A'}</small></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        document.getElementById('breakevenPointsTable').innerHTML = tableHTML;
    }

    displayTimeline(timeline_data) {
        if (!timeline_data || !timeline_data.monthly_analysis) return;

        const canvas = document.getElementById('timelineChart');
        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }

        const monthlyData = timeline_data.monthly_analysis.slice(0, 24); // First 24 months
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(item => `Month ${item.month}`),
                datasets: [
                    {
                        label: 'Cumulative Savings',
                        data: monthlyData.map(item => item.cumulative_savings),
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Net Position',
                        data: monthlyData.map(item => item.net_position),
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    intersect: false,
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Break-Even Timeline'
                    }
                }
            }
        });

        // Display timeline details
        const detailsHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Conservative Scenario</h6>
                            <p class="h5 text-warning">${timeline_data.scenario_analysis?.conservative?.breakeven_months?.toFixed(1) || 'N/A'} months</p>
                            <small>80% of expected savings</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Realistic Scenario</h6>
                            <p class="h5 text-info">${timeline_data.scenario_analysis?.realistic?.breakeven_months?.toFixed(1) || 'N/A'} months</p>
                            <small>100% of expected savings</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Optimistic Scenario</h6>
                            <p class="h5 text-success">${timeline_data.scenario_analysis?.optimistic?.breakeven_months?.toFixed(1) || 'N/A'} months</p>
                            <small>120% of expected savings</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('timelineDetails').innerHTML = detailsHTML;
    }

    displaySensitivityAnalysis(sensitivity_data) {
        if (!sensitivity_data) return;

        let chartsHTML = '';
        
        Object.entries(sensitivity_data).forEach(([variable, data]) => {
            if (!data.analysis_points || data.analysis_points.length === 0) return;

            const chartId = `sensitivity_${variable}`;
            chartsHTML += `
                <div class="mb-4">
                    <h6>${this.formatVariableName(variable)} Sensitivity</h6>
                    <canvas id="${chartId}" width="400" height="200"></canvas>
                    <small class="text-muted">
                        Sensitivity Score: ${data.sensitivity_score?.toFixed(4) || 'N/A'} 
                        ${data.sensitivity_score > 1 ? '(High sensitivity)' : '(Low sensitivity)'}
                    </small>
                </div>
            `;
        });

        document.getElementById('sensitivityCharts').innerHTML = chartsHTML;

        // Create charts after DOM update
        setTimeout(() => {
            Object.entries(sensitivity_data).forEach(([variable, data]) => {
                if (!data.analysis_points || data.analysis_points.length === 0) return;

                const chartId = `sensitivity_${variable}`;
                const canvas = document.getElementById(chartId);
                if (!canvas) return;

                const ctx = canvas.getContext('2d');

                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.analysis_points.map(point => this.formatNumber(point.value)),
                        datasets: [{
                            label: 'ROI %',
                            data: data.analysis_points.map(point => point.roi_percentage),
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                ticks: {
                                    callback: function(value) {
                                        return value + '%';
                                    }
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            });
        }, 100);
    }

    displayScenarios(scenarios) {
        if (!scenarios) return;

        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            <th>ROI %</th>
                            <th>Payback (Months)</th>
                            <th>Annual Savings</th>
                            <th>NPV</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${scenarios.map(scenario => `
                            <tr>
                                <td>
                                    <strong>${scenario.name}</strong><br>
                                    <small class="text-muted">${scenario.description}</small>
                                </td>
                                <td>${scenario.results?.roi_metrics?.first_year_roi?.toFixed(1) || 'N/A'}%</td>
                                <td>${scenario.results?.roi_metrics?.payback_period_months?.toFixed(1) || 'N/A'}</td>
                                <td>$${this.formatNumber(scenario.results?.savings?.annual_total) || 'N/A'}</td>
                                <td>$${this.formatNumber(scenario.results?.financial_metrics?.npv) || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        document.getElementById('scenariosTable').innerHTML = tableHTML;
    }

    displayRiskAssessment(risk_data) {
        if (!risk_data) return;

        const riskHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card border-${this.getRiskLevelClass(risk_data.risk_level)}">
                        <div class="card-header">
                            <h6 class="mb-0">Overall Risk Level: 
                                <span class="badge bg-${this.getRiskLevelClass(risk_data.risk_level)}">${risk_data.risk_level}</span>
                            </h6>
                        </div>
                        <div class="card-body">
                            <p>Risk Score: ${risk_data.overall_risk_score}/10</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">Risk Factors</h6>
                        </div>
                        <div class="card-body">
                            ${this.formatRiskFactors(risk_data)}
                        </div>
                    </div>
                </div>
            </div>

            ${risk_data.high_risk_factors && risk_data.high_risk_factors.length > 0 ? `
                <div class="alert alert-danger mt-3">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>High Risk Factors</h6>
                    <ul class="mb-0">
                        ${risk_data.high_risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${risk_data.medium_risk_factors && risk_data.medium_risk_factors.length > 0 ? `
                <div class="alert alert-warning mt-3">
                    <h6><i class="fas fa-exclamation me-2"></i>Medium Risk Factors</h6>
                    <ul class="mb-0">
                        ${risk_data.medium_risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;

        document.getElementById('riskAssessment').innerHTML = riskHTML;
    }

    formatRiskFactors(risk_data) {
        const totalFactors = (risk_data.high_risk_factors?.length || 0) + 
                           (risk_data.medium_risk_factors?.length || 0) + 
                           (risk_data.low_risk_factors?.length || 0);

        return `
            <div class="d-flex justify-content-between">
                <span>High Risk:</span>
                <span class="badge bg-danger">${risk_data.high_risk_factors?.length || 0}</span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Medium Risk:</span>
                <span class="badge bg-warning">${risk_data.medium_risk_factors?.length || 0}</span>
            </div>
            <div class="d-flex justify-content-between">
                <span>Low Risk:</span>
                <span class="badge bg-success">${risk_data.low_risk_factors?.length || 0}</span>
            </div>
            <hr>
            <div class="d-flex justify-content-between">
                <strong>Total:</strong>
                <strong>${totalFactors}</strong>
            </div>
        `;
    }

    formatVariableName(variable) {
        return variable.replace(/_/g, ' ')
                      .replace(/\b\w/g, l => l.toUpperCase());
    }

    formatNumber(num) {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US').format(Math.round(num));
    }

    showError(message) {
        const alertHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        container.insertAdjacentHTML('afterbegin', alertHTML);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize the break-even analyzer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BreakEvenAnalyzer();
});