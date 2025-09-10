/**
 * Version Control JavaScript
 * Handles version history, comparison, and rollback functionality
 */

let calculations = [];
let selectedCalculationId = null;
let versions = [];
let selectedVersion = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadCalculations();
    setupEventListeners();
});

function setupEventListeners() {
    // Calculation selector
    document.getElementById('calculationSelector').addEventListener('change', function(e) {
        selectedCalculationId = e.target.value;
        if (selectedCalculationId) {
            loadVersionHistory(selectedCalculationId);
            showMainContent(true);
        } else {
            showMainContent(false);
        }
    });
    
    // Forms
    document.getElementById('createVersionForm').addEventListener('submit', handleCreateVersion);
    
    // Modal events
    const createVersionModal = document.getElementById('createVersionModal');
    createVersionModal.addEventListener('show.bs.modal', populateCreateVersionForm);
}

// Load available calculations
async function loadCalculations() {
    try {
        const response = await fetch('/api/calculations');
        const data = await response.json();
        
        if (data.success) {
            calculations = data.calculations;
            populateCalculationSelector(calculations);
        } else {
            showError('Failed to load calculations: ' + data.message);
        }
    } catch (error) {
        showError('Error loading calculations: ' + error.message);
    }
}

function populateCalculationSelector(calculationsList) {
    const selector = document.getElementById('calculationSelector');
    
    selector.innerHTML = '<option value="">Select a calculation...</option>';
    
    calculationsList.forEach(calc => {
        const option = document.createElement('option');
        option.value = calc.id;
        option.textContent = `${calc.company_name || 'Unnamed'} (${new Date(calc.created_at).toLocaleDateString()})`;
        selector.appendChild(option);
    });
}

// Load version history for a calculation
async function loadVersionHistory(calculationId) {
    try {
        showVersionsLoading(true);
        
        const response = await fetch(`/api/versions/${calculationId}/history`);
        const data = await response.json();
        
        if (data.success) {
            versions = data.versions;
            renderVersionTimeline(versions);
            populateVersionSelectors(versions);
            updateVersionStats(versions);
        } else {
            showError('Failed to load version history: ' + data.error);
        }
    } catch (error) {
        showError('Error loading version history: ' + error.message);
    } finally {
        showVersionsLoading(false);
    }
}

// Render version timeline
function renderVersionTimeline(versionList) {
    const timeline = document.getElementById('versionTimeline');
    
    if (versionList.length === 0) {
        timeline.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-history fa-2x text-muted mb-2"></i>
                <p class="text-muted">No version history available</p>
                <button class="btn btn-sm btn-primary" onclick="createNewVersion()">Create First Version</button>
            </div>
        `;
        return;
    }
    
    timeline.innerHTML = versionList.map((version, index) => {
        const isLatest = index === 0;
        const isRollback = version.created_by && version.created_by.includes('rollback');
        const versionClass = isLatest ? 'version-current' : (isRollback ? 'version-rollback' : '');
        
        return `
            <div class="version-item ${versionClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">
                            Version ${version.version_number}
                            ${isLatest ? '<span class="badge bg-success ms-2">Current</span>' : ''}
                            ${isRollback ? '<span class="badge bg-warning ms-2">Rollback</span>' : ''}
                        </h6>
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${new Date(version.created_at).toLocaleString()}
                            by ${version.created_by || 'Unknown'}
                        </small>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewVersion(${selectedCalculationId}, ${version.version_number})" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="selectForComparison(${version.version_number})" title="Select for Comparison">
                            <i class="fas fa-balance-scale"></i>
                        </button>
                        ${!isLatest ? `
                            <button class="btn btn-outline-warning" onclick="rollbackToVersion(${version.version_number})" title="Rollback">
                                <i class="fas fa-undo"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
                
                ${version.notes ? `
                    <div class="mt-2">
                        <small class="text-muted">
                            <i class="fas fa-sticky-note me-1"></i>
                            ${escapeHtml(version.notes)}
                        </small>
                    </div>
                ` : ''}
                
                <div class="version-actions">
                    <small class="text-muted">
                        ${version.changes_count || 0} changes • 
                        Checksum: <code>${version.checksum || 'N/A'}</code>
                    </small>
                </div>
            </div>
        `;
    }).join('');
}

function populateVersionSelectors(versionList) {
    const selectors = ['compareVersion1', 'compareVersion2', 'rollbackTargetVersion'];
    
    selectors.forEach(selectorId => {
        const selector = document.getElementById(selectorId);
        selector.innerHTML = '<option value="">Select version...</option>';
        
        versionList.forEach(version => {
            const option = document.createElement('option');
            option.value = version.version_number;
            option.textContent = `Version ${version.version_number} (${new Date(version.created_at).toLocaleDateString()})`;
            selector.appendChild(option);
        });
    });
}

function updateVersionStats(versionList) {
    const statsContainer = document.getElementById('versionStats');
    
    const totalVersions = versionList.length;
    const rollbackCount = versionList.filter(v => v.created_by && v.created_by.includes('rollback')).length;
    const latestVersion = versionList[0];
    
    statsContainer.innerHTML = `
        <div class="row g-2">
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-primary">${totalVersions}</h4>
                    <small class="text-muted">Total Versions</small>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-warning">${rollbackCount}</h4>
                    <small class="text-muted">Rollbacks</small>
                </div>
            </div>
            <div class="col-12 mt-3">
                <small class="text-muted">
                    <strong>Latest:</strong> Version ${latestVersion ? latestVersion.version_number : 'N/A'}<br>
                    <strong>Created:</strong> ${latestVersion ? new Date(latestVersion.created_at).toLocaleDateString() : 'N/A'}
                </small>
            </div>
        </div>
    `;
}

// View version details
async function viewVersion(calculationId, versionNumber) {
    try {
        const response = await fetch(`/api/versions/${calculationId}/${versionNumber}`);
        const data = await response.json();
        
        if (data.success) {
            selectedVersion = data.version;
            showVersionDetails(data.version);
        } else {
            showError('Failed to load version details: ' + data.error);
        }
    } catch (error) {
        showError('Error loading version details: ' + error.message);
    }
}

function showVersionDetails(version) {
    alert(`Version ${version.version_number} Details:\n\n` +
          `Created: ${new Date(version.created_at).toLocaleString()}\n` +
          `By: ${version.created_by}\n` +
          `Notes: ${version.notes || 'None'}\n` +
          `Changes: ${version.changes.length}\n` +
          `Checksum: ${version.checksum}`);
    
    // TODO: Replace with proper modal
}

// Compare versions
async function compareVersions() {
    const version1 = document.getElementById('compareVersion1').value;
    const version2 = document.getElementById('compareVersion2').value;
    
    if (!version1 || !version2) {
        showError('Please select two versions to compare');
        return;
    }
    
    if (version1 === version2) {
        showError('Please select different versions to compare');
        return;
    }
    
    try {
        const response = await fetch(`/api/versions/${selectedCalculationId}/compare?version1=${version1}&version2=${version2}`);
        const data = await response.json();
        
        if (data.success) {
            showComparisonResults(data.comparison);
        } else {
            showError('Failed to compare versions: ' + data.error);
        }
    } catch (error) {
        showError('Error comparing versions: ' + error.message);
    }
}

function showComparisonResults(comparison) {
    const resultsSection = document.getElementById('comparisonResults');
    const content = document.getElementById('comparisonContent');
    
    content.innerHTML = `
        <div class="comparison-container">
            <div class="row">
                <div class="col-md-6">
                    <h6>Version ${comparison.version1.number}</h6>
                    <small class="text-muted">Created: ${new Date(comparison.version1.created_at).toLocaleString()}</small>
                    <p class="mt-2">${escapeHtml(comparison.version1.notes || 'No notes')}</p>
                </div>
                <div class="col-md-6">
                    <h6>Version ${comparison.version2.number}</h6>
                    <small class="text-muted">Created: ${new Date(comparison.version2.created_at).toLocaleString()}</small>
                    <p class="mt-2">${escapeHtml(comparison.version2.notes || 'No notes')}</p>
                </div>
            </div>
            
            <hr>
            
            <h6>Input Differences</h6>
            ${comparison.input_differences.length > 0 ? `
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Version ${comparison.version1.number}</th>
                                <th>Version ${comparison.version2.number}</th>
                                <th>Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${comparison.input_differences.map(diff => `
                                <tr>
                                    <td><strong>${diff.field_label}</strong></td>
                                    <td>${formatValue(diff.value1)}</td>
                                    <td>${formatValue(diff.value2)}</td>
                                    <td>
                                        <span class="badge bg-${getChangeColor(diff.change_type)}">${diff.change_type.replace(/_/g, ' ')}</span>
                                        ${diff.difference !== null ? `<br><small>(${diff.difference > 0 ? '+' : ''}${formatValue(diff.difference)})</small>` : ''}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            ` : '<p class="text-muted">No input differences found.</p>'}
            
            <hr>
            
            <h6>Results Differences</h6>
            ${comparison.results_differences.length > 0 ? `
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Version ${comparison.version1.number}</th>
                                <th>Version ${comparison.version2.number}</th>
                                <th>Change</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${comparison.results_differences.map(diff => `
                                <tr>
                                    <td><strong>${diff.label}</strong></td>
                                    <td>${formatValue(diff.value1)}</td>
                                    <td>${formatValue(diff.value2)}</td>
                                    <td>
                                        ${diff.difference !== null ? `${diff.difference > 0 ? '+' : ''}${formatValue(diff.difference)}` : 'N/A'}
                                        ${diff.percent_change !== null ? `<br><small>(${diff.percent_change > 0 ? '+' : ''}${diff.percent_change.toFixed(1)}%)</small>` : ''}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            ` : '<p class="text-muted">No significant result differences found.</p>'}
            
            <hr>
            
            <h6>Summary</h6>
            <div class="alert alert-info">
                <pre class="mb-0">${escapeHtml(comparison.summary)}</pre>
            </div>
        </div>
    `;
    
    resultsSection.style.display = 'block';
}

function getChangeColor(changeType) {
    const colors = {
        'major_increase': 'success',
        'moderate_increase': 'info',
        'minor_increase': 'light',
        'major_decrease': 'danger',
        'moderate_decrease': 'warning',
        'minor_decrease': 'light',
        'initialized': 'primary',
        'cleared': 'secondary',
        'text_change': 'secondary'
    };
    return colors[changeType] || 'secondary';
}

function formatValue(value) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
        return new Intl.NumberFormat().format(value);
    }
    return value.toString();
}

// Select version for comparison
function selectForComparison(versionNumber) {
    const selector1 = document.getElementById('compareVersion1');
    const selector2 = document.getElementById('compareVersion2');
    
    if (!selector1.value) {
        selector1.value = versionNumber;
    } else if (!selector2.value) {
        selector2.value = versionNumber;
    } else {
        // Both are filled, replace the first one
        selector1.value = versionNumber;
        selector2.value = '';
    }
}

// Create new version
function createNewVersion() {
    const modal = new bootstrap.Modal(document.getElementById('createVersionModal'));
    modal.show();
}

function populateCreateVersionForm() {
    // Pre-fill with current data if available
    document.getElementById('useCurrentData').checked = true;
}

async function handleCreateVersion(e) {
    e.preventDefault();
    
    const formData = {
        notes: document.getElementById('versionNotes').value,
        use_current_data: document.getElementById('useCurrentData').checked
    };
    
    try {
        const response = await fetch(`/api/versions/${selectedCalculationId}/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Version created successfully!');
            loadVersionHistory(selectedCalculationId); // Refresh timeline
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('createVersionModal'));
            modal.hide();
            document.getElementById('createVersionForm').reset();
        } else {
            showError('Failed to create version: ' + data.error);
        }
    } catch (error) {
        showError('Error creating version: ' + error.message);
    }
}

// Show audit trail
async function showAuditTrail() {
    if (!selectedCalculationId) {
        showError('Please select a calculation first');
        return;
    }
    
    try {
        const response = await fetch(`/api/versions/${selectedCalculationId}/audit-trail`);
        const data = await response.json();
        
        if (data.success) {
            displayAuditTrail(data.audit_trail);
        } else {
            showError('Failed to load audit trail: ' + data.error);
        }
    } catch (error) {
        showError('Error loading audit trail: ' + error.message);
    }
}

function displayAuditTrail(auditTrail) {
    const modal = new bootstrap.Modal(document.getElementById('auditTrailModal'));
    const content = document.getElementById('auditTrailContent');
    
    content.innerHTML = `
        <div class="table-responsive">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Version</th>
                        <th>Action</th>
                        <th>Date</th>
                        <th>User</th>
                        <th>Changes</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    ${auditTrail.map(entry => `
                        <tr>
                            <td>v${entry.version_number}</td>
                            <td>
                                <span class="badge bg-${getActionColor(entry.action)}">${entry.action.replace('_', ' ')}</span>
                            </td>
                            <td>${new Date(entry.created_at).toLocaleDateString()}</td>
                            <td>${escapeHtml(entry.created_by || 'Unknown')}</td>
                            <td>
                                <small>${entry.changes_count} changes</small>
                                ${entry.significant_changes.length > 0 ? `
                                    <br><small class="text-muted">${entry.significant_changes.join(', ')}</small>
                                ` : ''}
                            </td>
                            <td><small>${escapeHtml(entry.notes || 'No notes')}</small></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    modal.show();
}

function getActionColor(action) {
    const colors = {
        'created': 'success',
        'modified': 'primary',
        'rollback': 'warning',
        'batch_update': 'info'
    };
    return colors[action] || 'secondary';
}

// Rollback functionality
function showRollbackOptions() {
    if (!selectedCalculationId) {
        showError('Please select a calculation first');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('rollbackModal'));
    modal.show();
}

function rollbackToVersion(versionNumber) {
    document.getElementById('rollbackTargetVersion').value = versionNumber;
    showRollbackOptions();
}

async function confirmRollback() {
    const targetVersion = document.getElementById('rollbackTargetVersion').value;
    const notes = document.getElementById('rollbackNotes').value;
    
    if (!targetVersion) {
        showError('Please select a target version');
        return;
    }
    
    try {
        const response = await fetch(`/api/versions/${selectedCalculationId}/rollback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_version: parseInt(targetVersion),
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadVersionHistory(selectedCalculationId); // Refresh timeline
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('rollbackModal'));
            modal.hide();
            document.getElementById('rollbackNotes').value = '';
        } else {
            showError('Rollback failed: ' + data.error);
        }
    } catch (error) {
        showError('Error during rollback: ' + error.message);
    }
}

// Validate versions integrity
async function validateVersions() {
    if (!selectedCalculationId) {
        showError('Please select a calculation first');
        return;
    }
    
    // For now, just show a simple message
    // In a full implementation, this would call an API endpoint
    showSuccess('Version integrity validation is not yet implemented');
}

function refreshVersions() {
    if (selectedCalculationId) {
        loadVersionHistory(selectedCalculationId);
    }
}

// Utility functions
function showMainContent(show) {
    document.getElementById('noCalculationSelected').style.display = show ? 'none' : 'block';
    document.getElementById('mainContent').style.display = show ? 'block' : 'none';
}

function showVersionsLoading(show) {
    document.getElementById('versionsLoading').style.display = show ? 'block' : 'none';
    document.getElementById('versionTimeline').style.display = show ? 'none' : 'block';
}

function showError(message) {
    // Simple alert for now - could be enhanced with toast notifications
    alert('Error: ' + message);
}

function showSuccess(message) {
    // Simple alert for now - could be enhanced with toast notifications
    alert('Success: ' + message);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}