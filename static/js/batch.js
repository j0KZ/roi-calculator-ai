/**
 * Batch Processing JavaScript
 * Handles bulk ROI calculations and comparison analysis
 */

let uploadedScenarios = [];
let processingResults = [];
let comparisonData = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupDropZone();
});

function setupEventListeners() {
    // File input change
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    
    // Custom mapping toggle
    document.getElementById('customMapping').addEventListener('change', function(e) {
        const mappingSection = document.getElementById('mappingSection');
        mappingSection.style.display = e.target.checked ? 'block' : 'none';
    });
    
    // Export buttons
    document.getElementById('exportExcelBtn').addEventListener('click', exportToExcel);
    document.getElementById('saveResultsBtn').addEventListener('click', saveResults);
}

function setupDropZone() {
    const dropZone = document.getElementById('dropZone');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click to browse
    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    document.getElementById('dropZone').classList.add('dragover');
}

function unhighlight() {
    document.getElementById('dropZone').classList.remove('dragover');
}

function handleDrop(e) {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload({ target: { files: files } });
    }
}

// Handle file upload
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['.csv', '.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!allowedTypes.includes(fileExtension)) {
        showError('Unsupported file type. Please upload CSV or Excel files.');
        return;
    }
    
    try {
        showUploadProgress(true);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Add sheet name for Excel files
        if (['.xlsx', '.xls'].includes(fileExtension)) {
            const sheetName = document.getElementById('sheetName').value || 'Sheet1';
            formData.append('sheet_name', sheetName);
        }
        
        // Add custom mapping if enabled
        if (document.getElementById('customMapping').checked) {
            const mapping = getColumnMapping();
            formData.append('mapping', JSON.stringify(mapping));
        }
        
        // Choose upload endpoint based on file type
        const endpoint = fileExtension === '.csv' ? '/api/batch/upload-csv' : '/api/batch/upload-excel';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            uploadedScenarios = data.scenarios;
            showPreview(data.scenarios);
            showSuccess(`Successfully imported ${data.count} scenarios`);
        } else {
            showError('Upload failed: ' + data.error);
        }
        
    } catch (error) {
        showError('Error uploading file: ' + error.message);
    } finally {
        showUploadProgress(false);
    }
}

function getColumnMapping() {
    return {
        company_name: document.getElementById('mapCompanyName').value || 'company_name',
        annual_revenue: document.getElementById('mapAnnualRevenue').value || 'annual_revenue',
        monthly_orders: document.getElementById('mapMonthlyOrders').value || 'monthly_orders'
        // Add more mappings as needed
    };
}

// Show preview of uploaded scenarios
function showPreview(scenarios) {
    const previewSection = document.getElementById('previewSection');
    const tableBody = document.getElementById('previewTableBody');
    const scenarioCount = document.getElementById('scenarioCount');
    
    scenarioCount.textContent = `${scenarios.length} scenarios loaded`;
    
    // Populate preview table
    tableBody.innerHTML = scenarios.slice(0, 10).map((scenario, index) => `
        <tr>
            <td>${escapeHtml(scenario.company_name || `Scenario ${index + 1}`)}</td>
            <td>$${formatNumber(scenario.annual_revenue)}</td>
            <td>${formatNumber(scenario.monthly_orders)}</td>
            <td>$${scenario.avg_order_value.toFixed(2)}</td>
            <td>$${formatNumber(scenario.labor_costs)}</td>
            <td>$${formatNumber(scenario.service_investment)}</td>
            <td><span class="badge bg-secondary">Ready</span></td>
        </tr>
    `).join('');
    
    if (scenarios.length > 10) {
        tableBody.innerHTML += `
            <tr>
                <td colspan="7" class="text-muted text-center">
                    <em>... and ${scenarios.length - 10} more scenarios</em>
                </td>
            </tr>
        `;
    }
    
    previewSection.style.display = 'block';
}

// Process all scenarios
async function processScenarios() {
    if (uploadedScenarios.length === 0) {
        showError('No scenarios to process');
        return;
    }
    
    try {
        // Show processing section
        const processingSection = document.getElementById('processingSection');
        processingSection.style.display = 'block';
        
        // Disable process button
        document.getElementById('processBtn').disabled = true;
        
        // Start processing
        const response = await fetch('/api/batch/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scenarios: uploadedScenarios
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            processingResults = data.results;
            comparisonData = data.comparison;
            
            updateProcessingProgress(100);
            showProcessingResults(data.results);
            showComparisonResults(data.comparison);
            
            showSuccess(`Successfully processed ${data.results.length} scenarios`);
        } else {
            showError('Processing failed: ' + data.error);
        }
        
    } catch (error) {
        showError('Error processing scenarios: ' + error.message);
    } finally {
        document.getElementById('processBtn').disabled = false;
    }
}

function updateProcessingProgress(percentage) {
    const progressBar = document.getElementById('processProgress');
    const statusText = document.getElementById('processStatus');
    
    progressBar.style.width = percentage + '%';
    statusText.textContent = percentage === 100 ? 'Processing complete!' : `Processing... ${percentage}%`;
}

// Show processing results
function showProcessingResults(results) {
    const resultsContainer = document.getElementById('processResults');
    
    const successCount = results.filter(r => r.success).length;
    const errorCount = results.filter(r => !r.success).length;
    
    resultsContainer.innerHTML = `
        <div class="col-md-6">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <h5><i class="fas fa-check-circle me-2"></i>Successful</h5>
                    <h3>${successCount}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card bg-danger text-white">
                <div class="card-body">
                    <h5><i class="fas fa-exclamation-circle me-2"></i>Failed</h5>
                    <h3>${errorCount}</h3>
                </div>
            </div>
        </div>
    `;
    
    if (errorCount > 0) {
        const errorDetails = results
            .filter(r => !r.success)
            .map(r => `${r.scenario_id}: ${r.error}`)
            .join('\n');
        
        resultsContainer.innerHTML += `
            <div class="col-12 mt-3">
                <div class="alert alert-warning">
                    <strong>Processing Errors:</strong>
                    <pre class="mt-2 mb-0">${errorDetails}</pre>
                </div>
            </div>
        `;
    }
}

// Show comparison results
function showComparisonResults(comparison) {
    if (!comparison || !comparison.comparison_matrix) {
        return;
    }
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Summary statistics
    showSummaryStats(comparison);
    
    // Comparison table
    showComparisonMatrix(comparison.comparison_matrix);
    
    // Top performers
    showTopPerformers(comparison.top_performers);
    
    // Risk analysis
    showRiskAnalysis(comparison.risk_analysis);
}

function showSummaryStats(comparison) {
    const container = document.getElementById('summaryStats');
    const stats = comparison.statistical_summary;
    
    if (!stats) return;
    
    // ROI statistics
    const roiStats = stats.roi_year_1 || {};
    
    container.innerHTML = `
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="text-primary">${(roiStats.mean || 0).toFixed(1)}%</h5>
                    <small class="text-muted">Average ROI</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="text-success">${(roiStats.max || 0).toFixed(1)}%</h5>
                    <small class="text-muted">Best ROI</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="text-info">${(roiStats.median || 0).toFixed(1)}%</h5>
                    <small class="text-muted">Median ROI</small>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="text-warning">${comparison.successful_scenarios || 0}</h5>
                    <small class="text-muted">Scenarios</small>
                </div>
            </div>
        </div>
    `;
}

function showComparisonMatrix(matrix) {
    const table = document.getElementById('comparisonTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    
    if (!matrix || matrix.length === 0) return;
    
    // Create headers
    const headers = ['Scenario', 'ROI Y1', 'ROI Y3', 'Payback', 'Annual Savings', 'NPV', 'IRR', 'Rank'];
    thead.innerHTML = `
        <tr>
            ${headers.map(h => `<th>${h}</th>`).join('')}
        </tr>
    `;
    
    // Create rows
    tbody.innerHTML = matrix.map((row, index) => {
        const avgRank = (
            (row.roi_year_1_rank || 0) + 
            (row.roi_year_3_rank || 0) + 
            (row.annual_savings_rank || 0)
        ) / 3;
        
        const rankClass = avgRank <= 1 ? 'rank-1' : avgRank <= 2 ? 'rank-2' : avgRank <= 3 ? 'rank-3' : '';
        
        return `
            <tr class="${rankClass}">
                <td><strong>${escapeHtml(row.scenario_id)}</strong></td>
                <td>${(row.roi_year_1 || 0).toFixed(1)}%</td>
                <td>${(row.roi_year_3 || 0).toFixed(1)}%</td>
                <td>${(row.payback_months || 0).toFixed(0)} mo</td>
                <td>$${formatNumber(row.annual_savings || 0)}</td>
                <td>$${formatNumber(row.npv || 0)}</td>
                <td>${(row.irr || 0).toFixed(1)}%</td>
                <td>#${avgRank.toFixed(0)}</td>
            </tr>
        `;
    }).join('');
}

function showTopPerformers(performers) {
    if (!performers) return;
    
    const container = document.getElementById('topPerformers');
    
    container.innerHTML = `
        <div class="col-12">
            <h6>Top Performers</h6>
        </div>
        ${Object.entries(performers).map(([category, performer]) => `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">${category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
                        <p class="card-text">
                            <strong>${escapeHtml(performer.scenario_id)}</strong><br>
                            ROI: ${(performer.roi_year_1 || 0).toFixed(1)}%<br>
                            Savings: $${formatNumber(performer.annual_savings || 0)}
                        </p>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

function showRiskAnalysis(riskData) {
    if (!riskData) return;
    
    const container = document.getElementById('riskAnalysis').querySelector('.row');
    
    container.innerHTML = Object.entries(riskData).map(([key, data]) => {
        if (typeof data !== 'object' || !data.risk_level) return '';
        
        const colorClass = {
            'Low': 'success',
            'Medium': 'warning', 
            'High': 'danger'
        }[data.risk_level] || 'secondary';
        
        return `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
                        <span class="badge bg-${colorClass}">${data.risk_level} Risk</span>
                        <p class="card-text mt-2 small">
                            ${Object.entries(data).filter(([k, v]) => k !== 'risk_level').map(([k, v]) => 
                                `${k.replace(/_/g, ' ')}: ${typeof v === 'number' ? v.toFixed(2) : v}`
                            ).join('<br>')}
                        </p>
                    </div>
                </div>
            </div>
        `;
    }).filter(html => html).join('');
}

// Export to Excel
async function exportToExcel() {
    if (!comparisonData) {
        showError('No comparison data to export');
        return;
    }
    
    try {
        const response = await fetch('/api/batch/export-excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comparison_data: comparisonData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create download link
            const a = document.createElement('a');
            a.href = data.download_url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            showSuccess('Excel report generated successfully!');
        } else {
            showError('Export failed: ' + data.error);
        }
        
    } catch (error) {
        showError('Error exporting to Excel: ' + error.message);
    }
}

// Save results
function saveResults() {
    if (!processingResults) {
        showError('No results to save');
        return;
    }
    
    const jsonData = JSON.stringify({
        results: processingResults,
        comparison: comparisonData,
        generated_at: new Date().toISOString()
    }, null, 2);
    
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch_results_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess('Results saved successfully!');
}

// Utility functions
function showUploadProgress(show) {
    document.querySelector('.progress-container').style.display = show ? 'block' : 'none';
}

function showError(message) {
    const toast = new bootstrap.Toast(document.getElementById('errorToast'));
    document.getElementById('errorMessage').textContent = message;
    toast.show();
}

function showSuccess(message) {
    const toast = new bootstrap.Toast(document.getElementById('successToast'));
    document.getElementById('successMessage').textContent = message;
    toast.show();
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(Math.round(num));
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}