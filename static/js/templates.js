/**
 * Template Management JavaScript
 * Handles template CRUD operations and UI interactions
 */

let templates = [];
let selectedTemplate = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Templates page loading...');
    loadTemplates();
    setupEventListeners();
});

function setupEventListeners() {
    // Form submissions
    const createForm = document.getElementById('createTemplateForm');
    if (createForm) {
        createForm.addEventListener('submit', handleCreateTemplate);
    }
    
    const importForm = document.getElementById('importTemplateForm');
    if (importForm) {
        importForm.addEventListener('submit', handleImportTemplate);
    }
    
    // Custom mapping toggle
    const customMapping = document.getElementById('customMapping');
    if (customMapping) {
        customMapping.addEventListener('change', function(e) {
            const mappingSection = document.getElementById('mappingSection');
            if (mappingSection) {
                mappingSection.style.display = e.target.checked ? 'block' : 'none';
            }
        });
    }
    
    // Search and filter
    const searchFilter = document.getElementById('searchFilter');
    if (searchFilter) {
        searchFilter.addEventListener('input', debounce(applyFilters, 300));
    }
    
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', applyFilters);
    }
    
    const sourceFilter = document.getElementById('sourceFilter');
    if (sourceFilter) {
        sourceFilter.addEventListener('change', applyFilters);
    }
}

// Load templates from API
async function loadTemplates() {
    const grid = document.getElementById('templatesGrid');
    
    try {
        console.log('Fetching templates from API...');
        const data = await fetchWithLoader('/api/templates/list', {}, 'Loading templates...');
        
        console.log('API Response:', data);
        
        if (data.success && data.templates) {
            templates = data.templates;
            console.log(`Loaded ${templates.length} templates`);
            renderTemplates(templates);
        } else {
            console.error('Failed to load templates:', data.error);
            loaderManager.showError('Failed to load templates: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading templates:', error);
        // Error is already shown by fetchWithLoader
    }
}

// Render templates grid
function renderTemplates(templatesData) {
    const grid = document.getElementById('templatesGrid');
    
    if (!grid) {
        console.error('Templates grid element not found');
        return;
    }
    
    if (!templatesData || templatesData.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fas fa-layer-group fa-3x text-muted mb-3"></i>
                <h4>No Templates Found</h4>
                <p class="text-muted">Create your first template to get started.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = templatesData.map(template => {
        // Handle template data safely
        const templateData = template.template_data || {};
        const tags = Array.isArray(template.tags) ? template.tags : [];
        const metadata = template.meta_data || {};
        
        // Calculate monthly revenue
        const monthlyRevenue = (templateData.annual_revenue || 0) / 12;
        const avgOrderValue = templateData.avg_order_value || 
            (monthlyRevenue && templateData.monthly_orders ? 
                monthlyRevenue / templateData.monthly_orders : 0);
        
        // Calculate ROI if possible
        const totalMonthlyCosts = (templateData.labor_costs || 0) + 
                                 (templateData.shipping_costs || 0) + 
                                 (templateData.error_costs || 0) + 
                                 (templateData.inventory_costs || 0);
        const monthlyProfit = monthlyRevenue - totalMonthlyCosts;
        const roi = templateData.service_investment > 0 ? 
            ((monthlyProfit * 12) / templateData.service_investment * 100).toFixed(1) : 0;
        
        // Determine template icon based on category
        const categoryIcons = {
            'retail': 'fa-store',
            'technology': 'fa-microchip',
            'fashion': 'fa-tshirt',
            'food_delivery': 'fa-utensils',
            'b2b': 'fa-building',
            'subscription': 'fa-sync',
            'ecommerce': 'fa-shopping-cart',
            'service': 'fa-concierge-bell',
            'manufacturing': 'fa-industry'
        };
        const icon = categoryIcons[template.category] || 'fa-layer-group';
        
        return `
            <div class="col-12 mb-2">
                <div class="template-card-wide">
                    <div class="row g-0 align-items-center">
                        <div class="col-auto template-icon-col">
                            <i class="fas ${icon} template-icon-large"></i>
                        </div>
                        <div class="col">
                            <div class="template-info">
                                <div class="d-flex align-items-center mb-1">
                                    <h6 class="template-name mb-0">${escapeHtml(template.name || 'Unnamed Template')}</h6>
                                    <span class="badge badge-${template.source || 'user'} ms-2">
                                        ${template.source || 'user'}
                                    </span>
                                    ${template.category ? 
                                        `<span class="category-pill ms-2">${template.category.replace('_', ' ')}</span>` : ''}
                                </div>
                                <div class="template-desc">${escapeHtml(template.description || 'No description available')}</div>
                                ${tags.length > 0 ? 
                                    `<div class="template-tags-inline mt-1">
                                        ${tags.map(tag => `<span class="tag-inline">${escapeHtml(tag)}</span>`).join('')}
                                    </div>` : ''}
                            </div>
                        </div>
                        <div class="col-auto">
                            <div class="template-metrics-horizontal">
                                <div class="metric-horizontal">
                                    <span class="metric-h-label">Revenue</span>
                                    <span class="metric-h-value">$${formatNumber(templateData.annual_revenue || 0)}/yr</span>
                                </div>
                                <div class="metric-horizontal">
                                    <span class="metric-h-label">Orders</span>
                                    <span class="metric-h-value">${formatNumber(templateData.monthly_orders || 0)}/mo</span>
                                </div>
                                <div class="metric-horizontal">
                                    <span class="metric-h-label">AOV</span>
                                    <span class="metric-h-value">$${avgOrderValue.toFixed(0)}</span>
                                </div>
                                <div class="metric-horizontal">
                                    <span class="metric-h-label">Costs</span>
                                    <span class="metric-h-value">$${formatNumber(totalMonthlyCosts)}/mo</span>
                                </div>
                                <div class="metric-horizontal">
                                    <span class="metric-h-label">Investment</span>
                                    <span class="metric-h-value">$${formatNumber(templateData.service_investment || 0)}</span>
                                </div>
                                ${roi > 0 ? `
                                <div class="metric-horizontal metric-roi-h">
                                    <span class="metric-h-label">ROI</span>
                                    <span class="metric-h-value-roi">${roi}%</span>
                                </div>` : ''}
                            </div>
                        </div>
                        <div class="col-auto template-actions-col">
                            <button class="btn btn-primary btn-sm d-block mb-1" onclick="useTemplate('${template.id || template.name}')">
                                <i class="fas fa-play me-1"></i> Use
                            </button>
                            <button class="btn btn-outline-secondary btn-sm d-block" onclick="viewTemplate('${template.id || template.name}')">
                                <i class="fas fa-eye me-1"></i> View
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Apply filters
function applyFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const sourceFilter = document.getElementById('sourceFilter');
    const searchFilter = document.getElementById('searchFilter');
    
    const category = categoryFilter ? categoryFilter.value : '';
    const source = sourceFilter ? sourceFilter.value : '';
    const search = searchFilter ? searchFilter.value.toLowerCase() : '';
    
    let filtered = templates;
    
    if (category) {
        filtered = filtered.filter(t => t.category === category);
    }
    
    if (source) {
        filtered = filtered.filter(t => (t.source || 'user') === source);
    }
    
    if (search) {
        filtered = filtered.filter(t => {
            const name = (t.name || '').toLowerCase();
            const description = (t.description || '').toLowerCase();
            const tags = Array.isArray(t.tags) ? t.tags : [];
            
            return name.includes(search) ||
                   description.includes(search) ||
                   tags.some(tag => tag.toLowerCase().includes(search));
        });
    }
    
    renderTemplates(filtered);
}

// View template details
async function viewTemplate(templateId) {
    try {
        console.log('Viewing template:', templateId);
        const data = await fetchWithLoader(`/api/templates/${templateId}`, {}, 'Loading template details...');
        
        if (data.success && data.template) {
            selectedTemplate = data.template;
            showTemplateDetails(data.template);
        } else {
            loaderManager.showError('Failed to load template: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading template:', error);
        // Error is already shown by fetchWithLoader
    }
}

// Show template details modal
function showTemplateDetails(template) {
    const modal = document.getElementById('templateDetailsModal');
    if (!modal) {
        console.error('Template details modal not found');
        return;
    }
    
    const bsModal = new bootstrap.Modal(modal);
    const title = document.getElementById('templateDetailsTitle');
    const content = document.getElementById('templateDetailsContent');
    
    if (title) title.textContent = template.name || 'Template Details';
    
    const templateData = template.template_data || {};
    const tags = Array.isArray(template.tags) ? template.tags : [];
    
    if (content) {
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Template Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Name:</strong></td><td>${escapeHtml(template.name || 'N/A')}</td></tr>
                        <tr><td><strong>Category:</strong></td><td>${template.category || 'N/A'}</td></tr>
                        <tr><td><strong>Source:</strong></td><td>${template.source || 'user'}</td></tr>
                        <tr><td><strong>Created:</strong></td><td>${template.created_at ? new Date(template.created_at).toLocaleDateString() : 'N/A'}</td></tr>
                    </table>
                    
                    <h6>Description</h6>
                    <p class="text-muted">${escapeHtml(template.description || 'No description provided')}</p>
                    
                    ${tags.length > 0 ? `
                        <h6>Tags</h6>
                        <div>${tags.map(tag => `<span class="badge bg-secondary me-1">${escapeHtml(tag)}</span>`).join('')}</div>
                    ` : ''}
                </div>
                
                <div class="col-md-6">
                    <h6>Template Data</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Annual Revenue:</strong></td><td>$${formatNumber(templateData.annual_revenue || 0)}</td></tr>
                        <tr><td><strong>Monthly Orders:</strong></td><td>${formatNumber(templateData.monthly_orders || 0)}</td></tr>
                        <tr><td><strong>Avg Order Value:</strong></td><td>$${(templateData.avg_order_value || 0).toFixed(2)}</td></tr>
                        <tr><td><strong>Labor Costs:</strong></td><td>$${formatNumber(templateData.labor_costs || 0)}/month</td></tr>
                        <tr><td><strong>Shipping Costs:</strong></td><td>$${formatNumber(templateData.shipping_costs || 0)}/month</td></tr>
                        <tr><td><strong>Error Costs:</strong></td><td>$${formatNumber(templateData.error_costs || 0)}/month</td></tr>
                        <tr><td><strong>Inventory Costs:</strong></td><td>$${formatNumber(templateData.inventory_costs || 0)}/month</td></tr>
                        <tr><td><strong>Service Investment:</strong></td><td>$${formatNumber(templateData.service_investment || 0)}</td></tr>
                    </table>
                </div>
            </div>
        `;
    }
    
    // Setup action buttons
    const useBtn = document.getElementById('useTemplateBtn');
    if (useBtn) useBtn.onclick = () => useTemplate(template.id || template.name);
    
    const cloneBtn = document.getElementById('cloneTemplateBtn');
    if (cloneBtn) cloneBtn.onclick = () => cloneTemplate(template.id || template.name);
    
    const exportBtn = document.getElementById('exportTemplateBtn');
    if (exportBtn) exportBtn.onclick = () => exportTemplate(template.id || template.name);
    
    bsModal.show();
}

// Use template in calculator
function useTemplate(templateId) {
    console.log('Using template:', templateId);
    
    const template = templates.find(t => (t.id == templateId || t.name === templateId));
    if (!template) {
        showError('Template not found');
        return;
    }
    
    // Store template data in sessionStorage and redirect to calculator
    sessionStorage.setItem('templateData', JSON.stringify(template.template_data));
    sessionStorage.setItem('templateName', template.name);
    window.location.href = '/?template=' + encodeURIComponent(templateId);
}

// Clone template
async function cloneTemplate(templateId) {
    const newName = prompt('Enter name for cloned template:');
    if (!newName) return;
    
    try {
        const data = await fetchWithLoader(
            `/api/templates/${templateId}/clone`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: newName })
            },
            'Cloning template...'
        );
        
        if (data.success) {
            loaderManager.showSuccess('Template cloned successfully!');
            loadTemplates(); // Refresh templates
            
            // Close modal if open
            const modal = bootstrap.Modal.getInstance(document.getElementById('templateDetailsModal'));
            if (modal) modal.hide();
        } else {
            loaderManager.showError('Failed to clone template: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        // Error is already shown by fetchWithLoader
    }
}

// Export template
async function exportTemplate(templateId) {
    try {
        const response = await fetch(`/api/templates/${templateId}/export?format=json`);
        const data = await response.json();
        
        if (data.success && data.export) {
            const blob = new Blob([data.export.data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.export.filename || 'template.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showSuccess('Template exported successfully!');
        } else {
            showError('Failed to export template: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        showError('Error exporting template: ' + error.message);
    }
}

// Handle create template form
async function handleCreateTemplate(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('templateName').value,
        description: document.getElementById('templateDescription').value,
        category: document.getElementById('templateCategory').value,
        tags: document.getElementById('templateTags').value.split(',').map(t => t.trim()).filter(t => t),
        template_data: {
            annual_revenue: parseFloat(document.getElementById('annualRevenue').value) || 0,
            monthly_orders: parseInt(document.getElementById('monthlyOrders').value) || 0,
            avg_order_value: parseFloat(document.getElementById('avgOrderValue').value) || 0,
            labor_costs: parseFloat(document.getElementById('laborCosts').value) || 0,
            shipping_costs: parseFloat(document.getElementById('shippingCosts').value) || 0,
            error_costs: parseFloat(document.getElementById('errorCosts').value) || 0,
            inventory_costs: parseFloat(document.getElementById('inventoryCosts').value) || 0,
            service_investment: parseFloat(document.getElementById('serviceInvestment').value) || 0
        }
    };
    
    try {
        const response = await fetch('/api/templates/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Template created successfully!');
            loadTemplates(); // Refresh templates
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTemplateModal'));
            if (modal) modal.hide();
            document.getElementById('createTemplateForm').reset();
        } else {
            if (data.validation_errors) {
                showError('Validation errors: ' + data.validation_errors.join(', '));
            } else {
                showError('Failed to create template: ' + (data.error || 'Unknown error'));
            }
        }
    } catch (error) {
        showError('Error creating template: ' + error.message);
    }
}

// Handle import template form
async function handleImportTemplate(e) {
    e.preventDefault();
    
    const jsonData = document.getElementById('templateJson').value;
    
    try {
        const templateData = JSON.parse(jsonData);
        
        const response = await fetch('/api/templates/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(templateData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Template imported successfully!');
            loadTemplates(); // Refresh templates
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('importTemplateModal'));
            if (modal) modal.hide();
            document.getElementById('importTemplateForm').reset();
        } else {
            showError('Failed to import template: ' + (data.error || 'Unknown error'));
        }
    } catch (jsonError) {
        showError('Invalid JSON format: ' + jsonError.message);
    }
}

// Utility functions
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const grid = document.getElementById('templatesGrid');
    
    if (spinner) spinner.style.display = show ? 'block' : 'none';
    if (grid) grid.style.display = show ? 'none' : 'block';
}

function showError(message) {
    console.error(message);
    loaderManager.showError(message);
}

function showSuccess(message) {
    console.log(message);
    loaderManager.showSuccess(message);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num || 0);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

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