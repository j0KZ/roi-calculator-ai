/**
 * ROI Calculator JavaScript
 * Handles form interactions, API calls, and result display
 */

// Global variables
let currentResults = null;
let examples = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadExamples();
    setupFormValidation();
    setupEventListeners();
});

/**
 * Load example scenarios from API
 */
async function loadExamples() {
    try {
        const response = await fetch('/api/examples');
        examples = await response.json();
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}

/**
 * Load an example scenario into the form
 */
function loadExample(exampleKey) {
    if (!examples[exampleKey]) {
        console.error('Example not found:', exampleKey);
        return;
    }
    
    const example = examples[exampleKey];
    const form = document.getElementById('roiForm');
    
    // Fill form fields with example data
    Object.keys(example.data).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = example.data[key];
            // Trigger change event for validation
            input.dispatchEvent(new Event('change'));
        }
    });
    
    // Show success message
    showToast(`Loaded ${example.name} example`, 'success');
    
    // Auto-calculate if all fields are filled
    setTimeout(() => {
        if (validateForm()) {
            calculateROI();
        }
    }, 500);
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const form = document.getElementById('roiForm');
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Auto-calculate AOV when revenue and orders change
    const revenueInput = document.getElementById('annual_revenue');
    const ordersInput = document.getElementById('monthly_orders');
    const aovInput = document.getElementById('avg_order_value');
    
    function updateAOV() {
        const revenue = parseFloat(revenueInput.value) || 0;
        const orders = parseFloat(ordersInput.value) || 0;
        
        if (revenue > 0 && orders > 0) {
            const monthlyRevenue = revenue / 12;
            const aov = monthlyRevenue / orders;
            aovInput.value = aov.toFixed(2);
        }
    }
    
    revenueInput.addEventListener('change', updateAOV);
    ordersInput.addEventListener('change', updateAOV);
    
    // Format currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', formatCurrencyInput);
    });
}

/**
 * Validate individual form field
 */
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove existing feedback
    clearFieldError(event);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (field.type === 'number' && value) {
        const num = parseFloat(value);
        if (isNaN(num) || num < 0) {
            showFieldError(field, 'Please enter a valid positive number');
            return false;
        }
        
        // Specific validations
        if (field.name === 'annual_revenue' && num < 10000) {
            showFieldError(field, 'Annual revenue seems too low (minimum $10,000)');
            return false;
        }
        
        if (field.name === 'service_investment' && num < 1000) {
            showFieldError(field, 'Service investment seems too low (minimum $1,000)');
            return false;
        }
    }
    
    // Show success
    showFieldSuccess(field);
    return true;
}

/**
 * Clear field error styling
 */
function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('is-invalid', 'is-valid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
}

/**
 * Show field success
 */
function showFieldSuccess(field) {
    field.classList.add('is-valid');
}

/**
 * Format currency input on blur
 */
function formatCurrencyInput(event) {
    const input = event.target;
    const value = parseFloat(input.value);
    
    if (!isNaN(value) && value >= 0) {
        // Don't format if user is still typing
        if (document.activeElement !== input) {
            input.value = value.toFixed(2);
        }
    }
}

/**
 * Validate entire form
 */
function validateForm() {
    const form = document.getElementById('roiForm');
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        const event = { target: input };
        if (!validateField(event)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Collect form data
 */
function getFormData() {
    const form = document.getElementById('roiForm');
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            data[key] = parseFloat(value) || value;
        }
    }
    
    return data;
}

/**
 * Main ROI calculation function
 */
async function calculateROI() {
    // Validate form
    if (!validateForm()) {
        showError('Please correct the form errors before calculating.');
        return;
    }
    
    // Get form data
    const formData = getFormData();
    
    // Show loading
    showLoading(true);
    
    try {
        // Validate inputs on server
        const validationResponse = await fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const validation = await validationResponse.json();
        
        if (!validation.valid) {
            showError('Validation errors:<br>' + validation.errors.join('<br>'));
            return;
        }
        
        // Calculate ROI
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Calculation failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            currentResults = result.results;
            console.log('Calculation successful, displaying results...');
            
            // Save results to session storage for PowerPoint generation
            sessionStorage.setItem('currentROIData', JSON.stringify(result.results));
            
            // Hide loading before displaying results to prevent stuck state
            console.log('Hiding loading modal before displaying results...');
            showLoading(false);
            
            // Small delay to ensure modal is fully hidden
            setTimeout(() => {
                try {
                    displayResults(result.results, formData);
                    showToast('ROI calculation completed successfully!', 'success');
                } catch (displayError) {
                    console.error('Error displaying results:', displayError);
                    showError('Error displaying results: ' + displayError.message);
                }
            }, 100);
            
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Calculation error:', error);
        showError('Calculation failed: ' + error.message);
    } finally {
        console.log('Finally block: ensuring loading modal is hidden');
        // Force hide loading with multiple attempts
        showLoading(false);
        setTimeout(() => showLoading(false), 200);
        setTimeout(() => showLoading(false), 500);
    }
}

/**
 * Display calculation results
 */
function displayResults(results, formData) {
    try {
        console.log('Starting displayResults with:', { results, formData });
        
        // Check if required elements exist
        if (!document.getElementById('resultsCard')) {
            console.error('resultsCard element not found');
            return;
        }
        
        if (!document.getElementById('detailedResults')) {
            console.error('detailedResults element not found');
            return;
        }
        
        // Display summary results
        console.log('Displaying summary results...');
        displaySummaryResults(results);
        console.log('Summary results displayed successfully');
        
        // Display detailed results
        console.log('Displaying detailed results...');
        displayDetailedResults(results);
        console.log('Detailed results displayed successfully');
        
        // Show results sections
        console.log('Showing results sections...');
        document.getElementById('resultsCard').style.display = 'block';
        document.getElementById('detailedResults').style.display = 'block';
        
        // Enable action buttons if they exist
        const pdfButton = document.getElementById('pdfButton');
        if (pdfButton) {
            pdfButton.disabled = false;
        }
        
        const proposalButton = document.getElementById('proposalButton');
        if (proposalButton) {
            proposalButton.disabled = false;
        }
        
        const optimizeButton = document.getElementById('optimizeButton');
        if (optimizeButton) {
            optimizeButton.disabled = false;
        }
        
        // Store latest calculation for save functionality
        window.lastCalculation = {
            inputs: formData,
            results: results
        };
        console.log('Stored last calculation');
        
        // Add save button if not already present
        console.log('Adding save button...');
        try {
            addSaveButton();
            console.log('Save button added/verified');
        } catch (saveError) {
            console.error('Error adding save button:', saveError);
            // Don't fail the entire function if save button fails
        }
        
        // Smooth scroll to results
        console.log('Scrolling to results...');
        const resultsCard = document.getElementById('resultsCard');
        if (resultsCard) {
            resultsCard.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
        
        console.log('displayResults completed successfully');
    } catch (error) {
        console.error('Critical error in displayResults:', error);
        console.error('Error stack:', error.stack);
        // Re-throw to ensure finally block in calculateROI still executes
        throw error;
    }
}

/**
 * Display summary results
 */
function displaySummaryResults(results) {
    try {
        console.log('displaySummaryResults called with:', results);
        
        if (!results) {
            console.error('No results provided to displaySummaryResults');
            return;
        }
        
        const roi = results.roi_metrics || {};
        const projections = results.projections || {};
        const financial = results.financial_metrics || {};
    
    const summaryHtml = `
        <div class="roi-summary">
            <div class="row">
                <div class="col-6">
                    <div class="roi-metric">
                        <h3>$${formatNumber(roi.annual_savings)}</h3>
                        <p>Annual Savings</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="roi-metric">
                        <h3>${roi.payback_period_text}</h3>
                        <p>Payback Period</p>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-6">
                    <div class="roi-metric">
                        <h3>${(projections.year_3 && projections.year_3.roi_percentage ? projections.year_3.roi_percentage.toFixed(1) : '0')}%</h3>
                        <p>3-Year ROI</p>
                    </div>
                </div>
                <div class="col-6">
                    <div class="roi-metric">
                        <h3>$${formatNumber(financial.npv)}</h3>
                        <p>Net Present Value</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <h6><i class="fas fa-chart-pie me-2"></i>Monthly Savings Breakdown</h6>
            ${generateSavingsBreakdown(results.savings)}
        </div>
    `;
    
    document.getElementById('resultsContent').innerHTML = summaryHtml;
    console.log('Summary HTML inserted successfully');
    
    } catch (error) {
        console.error('Error in displaySummaryResults:', error);
        console.error('Error stack:', error.stack);
        // Show a basic error message instead of crashing
        document.getElementById('resultsContent').innerHTML = '<div class="alert alert-warning">Error displaying summary results. Check console for details.</div>';
    }
}

/**
 * Generate savings breakdown HTML
 */
function generateSavingsBreakdown(savings) {
    const categories = [
        { key: 'labor', name: 'Labor Optimization', icon: 'fas fa-users' },
        { key: 'shipping', name: 'Shipping Optimization', icon: 'fas fa-shipping-fast' },
        { key: 'errors', name: 'Error Elimination', icon: 'fas fa-bug' },
        { key: 'inventory', name: 'Inventory Management', icon: 'fas fa-boxes' }
    ];
    
    let html = '';
    
    categories.forEach(category => {
        const data = savings[category.key];
        html += `
            <div class="savings-item">
                <div>
                    <i class="${category.icon} me-2"></i>
                    <span class="savings-category">${category.name}</span>
                    <span class="savings-percentage">(${(data.percentage * 100).toFixed(0)}%)</span>
                </div>
                <div class="savings-amount">
                    $${formatNumber(data.monthly)}
                </div>
            </div>
        `;
    });
    
    return html;
}

/**
 * Display detailed results
 */
function displayDetailedResults(results) {
    // Savings breakdown
    document.getElementById('savingsBreakdown').innerHTML = generateDetailedSavingsTable(results);
    
    // 3-year projections
    document.getElementById('projectionTable').innerHTML = generateProjectionTable(results.projections);
    
    // Financial metrics
    document.getElementById('financialMetrics').innerHTML = generateFinancialMetricsCards(results);
}

/**
 * Generate detailed savings table
 */
function generateDetailedSavingsTable(results) {
    const current = results.current_costs;
    const savings = results.savings;
    
    return `
        <h6><i class="fas fa-cut me-2"></i>Cost Reduction Analysis</h6>
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Current</th>
                        <th>Reduction</th>
                        <th>Savings</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><i class="fas fa-users me-1"></i> Labor</td>
                        <td>$${formatNumber(current.labor.monthly)}</td>
                        <td><span class="badge bg-primary">60%</span></td>
                        <td class="text-success fw-bold">$${formatNumber(savings.labor.monthly)}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-shipping-fast me-1"></i> Shipping</td>
                        <td>$${formatNumber(current.shipping.monthly)}</td>
                        <td><span class="badge bg-info">25%</span></td>
                        <td class="text-success fw-bold">$${formatNumber(savings.shipping.monthly)}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-bug me-1"></i> Errors</td>
                        <td>$${formatNumber(current.errors.monthly)}</td>
                        <td><span class="badge bg-success">80%</span></td>
                        <td class="text-success fw-bold">$${formatNumber(savings.errors.monthly)}</td>
                    </tr>
                    <tr>
                        <td><i class="fas fa-boxes me-1"></i> Inventory</td>
                        <td>$${formatNumber(current.inventory.monthly)}</td>
                        <td><span class="badge bg-warning">30%</span></td>
                        <td class="text-success fw-bold">$${formatNumber(savings.inventory.monthly)}</td>
                    </tr>
                    <tr class="table-success">
                        <th>TOTAL</th>
                        <th>$${formatNumber(current.total.monthly)}</th>
                        <th></th>
                        <th class="text-success">$${formatNumber(savings.monthly_total)}</th>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Generate projection table
 */
function generateProjectionTable(projections) {
    return `
        <h6><i class="fas fa-chart-line me-2"></i>3-Year Financial Projections</h6>
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Savings</th>
                        <th>Cumulative ROI</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Year 1</td>
                        <td>$${formatNumber(projections.year_1.savings)}</td>
                        <td class="fw-bold ${projections.year_1.roi_percentage >= 0 ? 'text-success' : 'text-danger'}">
                            ${projections.year_1.roi_percentage.toFixed(1)}%
                        </td>
                    </tr>
                    <tr>
                        <td>Year 2</td>
                        <td>$${formatNumber(projections.year_2.savings)}</td>
                        <td class="fw-bold text-success">${projections.year_2.roi_percentage.toFixed(1)}%</td>
                    </tr>
                    <tr>
                        <td>Year 3</td>
                        <td>$${formatNumber(projections.year_3.savings)}</td>
                        <td class="fw-bold text-success">${projections.year_3.roi_percentage.toFixed(1)}%</td>
                    </tr>
                    <tr class="table-info">
                        <th>Total</th>
                        <th>$${formatNumber(projections.year_3.cumulative_savings)}</th>
                        <th>-</th>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Generate financial metrics cards
 */
function generateFinancialMetricsCards(results) {
    const financial = results.financial_metrics;
    const chilean = results.chilean_specifics;
    
    return `
        <div class="row">
            <div class="col-md-3">
                <div class="financial-metric">
                    <h4><i class="fas fa-percentage me-2"></i>IRR</h4>
                    <p class="value">${(financial.irr * 100).toFixed(1)}%</p>
                    <p class="description">Internal Rate of Return</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="financial-metric">
                    <h4><i class="fas fa-dollar-sign me-2"></i>NPV</h4>
                    <p class="value">$${formatNumber(financial.npv)}</p>
                    <p class="description">Net Present Value</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="financial-metric">
                    <h4><i class="fas fa-flag me-2 chilean-blue"></i>With IVA</h4>
                    <p class="value">$${formatNumber(chilean.savings_with_iva.amount_with_iva)}</p>
                    <p class="description">Annual Savings + 19% IVA</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="financial-metric">
                    <h4><i class="fas fa-chart-line me-2"></i>Payback</h4>
                    <p class="value">${results.roi_metrics.payback_period_text}</p>
                    <p class="description">Investment Recovery</p>
                </div>
            </div>
        </div>
    `;
}

/**
 * Generate PDF report
 */
async function generatePDF() {
    if (!currentResults) {
        showError('No calculation results available. Please calculate ROI first.');
        return;
    }
    
    showLoading(true, 'Generating PDF report...');
    
    try {
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: currentResults })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'PDF generation failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Create download link
            const downloadUrl = result.download_url;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.click();
            
            showToast('PDF report generated successfully!', 'success');
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('PDF generation error:', error);
        showError('PDF generation failed: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Reset form
 */
function resetForm() {
    const form = document.getElementById('roiForm');
    form.reset();
    
    // Clear validation states
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
    });
    
    // Clear feedback messages
    const feedbacks = form.querySelectorAll('.invalid-feedback');
    feedbacks.forEach(feedback => feedback.remove());
    
    // Hide results
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('detailedResults').style.display = 'none';
    
    // Disable action buttons
    document.getElementById('pdfButton').disabled = true;
    const proposalButton = document.getElementById('proposalButton');
    if (proposalButton) proposalButton.disabled = true;
    const optimizeButton = document.getElementById('optimizeButton');
    if (optimizeButton) optimizeButton.disabled = true;
    
    currentResults = null;
    
    showToast('Form cleared', 'info');
}

/**
 * Show loading modal
 */
function showLoading(show, message = 'Calculating ROI...') {
    const modal = document.getElementById('loadingModal');
    if (!modal) {
        console.error('Loading modal not found');
        return;
    }
    
    const modalBody = modal.querySelector('.modal-body p');
    
    if (show) {
        if (modalBody) modalBody.textContent = message;
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        // Try multiple ways to hide the modal
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
        // Force hide using jQuery if available
        if (typeof $ !== 'undefined') {
            $('#loadingModal').modal('hide');
        }
        // Force remove backdrop if stuck
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
        document.body.classList.remove('modal-open');
        modal.style.display = 'none';
        modal.classList.remove('show');
    }
}

/**
 * Show error modal
 */
function showError(message) {
    const modal = document.getElementById('errorModal');
    const messageEl = document.getElementById('errorMessage');
    
    messageEl.innerHTML = message;
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
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
 * Format currency
 */
function formatCurrency(num) {
    if (typeof num !== 'number') return '$0';
    return '$' + formatNumber(num);
}

/**
 * Export functions for external use
 */
window.calculateROI = calculateROI;
window.loadExample = loadExample;
window.resetForm = resetForm;
window.generatePDF = generatePDF;

/**
 * Add save button to results section
 */
function addSaveButton() {
    const cardHeader = document.querySelector('#resultsCard .card-header');
    
    // Check if save button already exists
    if (!document.getElementById('saveCalculationBtn')) {
        // First, modify the header to have proper flexbox layout
        cardHeader.className = 'card-header d-flex justify-content-between align-items-center';
        
        // Get the existing h5 title
        const title = cardHeader.querySelector('h5');
        if (title) {
            title.className = 'mb-0'; // Remove bottom margin
        }
        
        // Create a button group for the buttons
        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'btn-group btn-group-sm';
        buttonGroup.setAttribute('role', 'group');
        
        const historyBtn = document.createElement('a');
        historyBtn.href = '/history';
        historyBtn.className = 'btn btn-outline-info';
        historyBtn.innerHTML = '<i class="fas fa-history"></i> History';
        
        const saveBtn = document.createElement('button');
        saveBtn.id = 'saveCalculationBtn';
        saveBtn.className = 'btn btn-outline-success';
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save';
        saveBtn.onclick = saveCalculation;
        
        // Add buttons to group
        buttonGroup.appendChild(historyBtn);
        buttonGroup.appendChild(saveBtn);
        
        // Add the button group to the header
        cardHeader.appendChild(buttonGroup);
    }
}

/**
 * Save calculation to database
 */
function saveCalculation() {
    if (!window.lastCalculation) {
        showToast('No calculation to save', 'warning');
        return;
    }
    
    // Clear the form fields
    document.getElementById('saveNotes').value = '';
    document.getElementById('saveTags').value = '';
    
    // Show the save modal
    const saveModal = new bootstrap.Modal(document.getElementById('saveModal'));
    saveModal.show();
}

/**
 * Confirm and save the calculation with modal data
 */
async function confirmSaveCalculation() {
    if (!window.lastCalculation) {
        showToast('No calculation to save', 'warning');
        return;
    }
    
    const { inputs, results } = window.lastCalculation;
    const notes = document.getElementById('saveNotes').value || '';
    const tags = document.getElementById('saveTags').value || '';
    
    // Combine inputs and results for saving
    const dataToSave = {
        ...inputs,
        results: results,
        notes: notes,
        tags: tags
    };
    
    // Hide the modal first
    const saveModal = bootstrap.Modal.getInstance(document.getElementById('saveModal'));
    saveModal.hide();
    
    try {
        const response = await fetch('/api/save-calculation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToSave)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Calculation saved successfully!', 'success');
            
            // Update save button
            const saveBtn = document.getElementById('saveCalculationBtn');
            if (saveBtn) {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved';
                saveBtn.classList.remove('btn-outline-success');
                saveBtn.classList.add('btn-success');
                saveBtn.disabled = true;
                setTimeout(() => {
                    saveBtn.innerHTML = '<i class="fas fa-save"></i> Save';
                    saveBtn.classList.remove('btn-success');
                    saveBtn.classList.add('btn-outline-success');
                    saveBtn.disabled = false;
                }, 3000);
            }
        } else {
            throw new Error(result.message || 'Failed to save calculation');
        }
    } catch (error) {
        console.error('Error saving calculation:', error);
        showToast('Error saving calculation: ' + error.message, 'danger');
    }
}

/**
 * Generate professional proposal from current ROI results
 */
function generateProposal() {
    if (!currentResults) {
        showToast('No calculation results available. Please calculate ROI first.', 'warning');
        return;
    }
    
    // Store results in session storage for the proposal generator
    sessionStorage.setItem('roiResults', JSON.stringify(currentResults));
    
    // Open proposal generator in new tab
    const proposalWindow = window.open('/proposal', '_blank');
    
    // Send data to the new window when it loads
    if (proposalWindow) {
        const checkWindow = setInterval(() => {
            try {
                if (proposalWindow.document && proposalWindow.document.readyState === 'complete') {
                    proposalWindow.postMessage({
                        type: 'ROI_RESULTS',
                        results: currentResults
                    }, window.location.origin);
                    clearInterval(checkWindow);
                }
            } catch (e) {
                // Window may not be ready yet, continue checking
            }
        }, 500);
        
        // Clear interval after 10 seconds if window doesn't load
        setTimeout(() => clearInterval(checkWindow), 10000);
        
        showToast('Opening proposal generator...', 'info');
    } else {
        showToast('Please allow pop-ups to generate proposals', 'warning');
    }
}

/**
 * Open cost optimizer with current ROI data
 */
function optimizeCosts() {
    if (!currentResults) {
        showToast('No calculation results available. Please calculate ROI first.', 'warning');
        return;
    }
    
    // Store results in session storage for the cost optimizer
    sessionStorage.setItem('roiResults', JSON.stringify(currentResults));
    
    // Open cost optimizer in new tab
    const optimizeWindow = window.open('/optimize', '_blank');
    
    if (optimizeWindow) {
        showToast('Opening cost optimizer...', 'info');
    } else {
        showToast('Please allow pop-ups to access the cost optimizer', 'warning');
    }
}