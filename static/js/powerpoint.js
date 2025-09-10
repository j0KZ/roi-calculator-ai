/**
 * PowerPoint Export JavaScript - Fixed Version
 * Handles PowerPoint presentation generation with template selection and customization
 */

// Global variables
let currentStep = 1;
let selectedTemplate = 'executive';
let selectedColorScheme = 'corporate_blue';
let roiData = null;
let templates = {
    'executive': {
        'name': 'Executive',
        'description': 'Clean, minimal design for C-level presentations'
    },
    'sales': {
        'name': 'Sales',
        'description': 'Dynamic, persuasive design for sales presentations'
    },
    'technical': {
        'name': 'Technical',
        'description': 'Professional design for detailed technical analysis'
    }
};
let colorSchemes = {};

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing PowerPoint export...');
    initializePowerPoint();
    loadSavedCalculations();
    loadTemplates();
    loadColorSchemes();
    setupEventListeners();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Step navigation
    const nextBtn = document.getElementById('next-step-btn');
    const prevBtn = document.getElementById('prev-step-btn');
    const generateBtn = document.getElementById('generate-presentation-btn');
    
    if (nextBtn) {
        nextBtn.addEventListener('click', nextStep);
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', prevStep);
    }
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generatePresentation);
    }
    
    // Saved calculation selection
    const calcSelect = document.getElementById('saved-calculations-select');
    if (calcSelect) {
        calcSelect.addEventListener('change', function(e) {
            if (e.target.value) {
                loadCalculationData(e.target.value);
            }
        });
    }
}

/**
 * Initialize PowerPoint export functionality
 */
function initializePowerPoint() {
    // Check if there's current ROI data in session storage
    const currentData = sessionStorage.getItem('currentROIData');
    if (currentData) {
        try {
            roiData = JSON.parse(currentData);
            updateCurrentCalculationDisplay();
        } catch (e) {
            console.error('Error parsing ROI data:', e);
        }
    }
    
    // Set default company information
    setDefaultCompanyInfo();
}

/**
 * Set default company information
 */
function setDefaultCompanyInfo() {
    const defaults = {
        'company-name': 'ROI Solutions Inc.',
        'company-phone': '+1 (555) 123-4567',
        'company-email': 'contact@roisolutions.com',
        'company-website': 'www.roisolutions.com',
        'company-tagline': 'Maximizing Your Investment Returns'
    };
    
    Object.keys(defaults).forEach(id => {
        const element = document.getElementById(id);
        if (element && !element.value) {
            element.value = defaults[id];
        }
    });
}

/**
 * Load saved calculations for selection
 */
async function loadSavedCalculations() {
    try {
        const response = await fetchWithLoader('/api/calculations', {}, 'Loading saved calculations...');
        
        if (response.success && response.calculations) {
            const select = document.getElementById('saved-calculations-select');
            if (select) {
                select.innerHTML = '<option value="">Select a saved calculation...</option>';
                
                response.calculations.forEach(calc => {
                    const option = document.createElement('option');
                    option.value = calc.id;
                    option.textContent = `${calc.company_name || 'Unnamed'} - ${new Date(calc.created_at).toLocaleDateString()}`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Failed to load saved calculations:', error);
    }
}

/**
 * Load calculation data
 */
async function loadCalculationData(calcId) {
    try {
        const response = await fetchWithLoader(`/api/calculations/${calcId}`, {}, 'Loading calculation...');
        
        if (response.success && response.calculation) {
            roiData = response.calculation;
            updateCurrentCalculationDisplay();
            loaderManager.showSuccess('Calculation loaded successfully!');
        }
    } catch (error) {
        console.error('Failed to load calculation:', error);
        loaderManager.showError('Failed to load calculation');
    }
}

/**
 * Update current calculation display
 */
function updateCurrentCalculationDisplay() {
    const display = document.getElementById('current-calculation-display');
    if (display && roiData) {
        display.innerHTML = `
            <div class="alert alert-info">
                <strong>Current Calculation:</strong> ${roiData.company_name || 'Unnamed'}
                <br>ROI: ${(roiData.roi_metrics?.first_year_roi || 0).toFixed(1)}%
                <br>Annual Savings: $${(roiData.roi_metrics?.annual_savings || 0).toLocaleString()}
            </div>
        `;
    }
}

/**
 * Load available PowerPoint templates
 */
async function loadTemplates() {
    try {
        const response = await fetch('/api/powerpoint-templates');
        const data = await response.json();
        
        if (data.success && data.templates) {
            templates = data.templates;
            console.log('Loaded templates:', templates);
        }
    } catch (error) {
        console.error('Failed to load templates, using defaults:', error);
    }
    
    displayTemplates();
    
    // Auto-select first template
    if (!selectedTemplate && Object.keys(templates).length > 0) {
        selectTemplate(Object.keys(templates)[0]);
    }
}

/**
 * Display templates in the UI
 */
function displayTemplates() {
    const container = document.getElementById('templates-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.keys(templates).forEach(templateId => {
        const template = templates[templateId];
        
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-3';
        card.innerHTML = `
            <div class="template-card ${selectedTemplate === templateId ? 'selected' : ''}" 
                 data-template="${templateId}" 
                 onclick="selectTemplate('${templateId}')">
                <div class="text-center p-3">
                    <i class="fas fa-file-powerpoint fa-3x mb-3" style="color: #D04A37;"></i>
                    <h5>${template.name}</h5>
                    <p class="text-muted small">${template.description}</p>
                    <ul class="feature-list text-left list-unstyled mt-3">
                        <li><i class="fas fa-check text-success me-2"></i>Professional design</li>
                        <li><i class="fas fa-check text-success me-2"></i>Data visualizations</li>
                        <li><i class="fas fa-check text-success me-2"></i>Speaker notes</li>
                        <li><i class="fas fa-check text-success me-2"></i>Customizable colors</li>
                    </ul>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Load available color schemes
 */
async function loadColorSchemes() {
    try {
        const response = await fetch('/api/powerpoint-color-schemes');
        const data = await response.json();
        
        if (data.success && data.color_schemes) {
            colorSchemes = data.color_schemes;
            displayColorSchemes();
            
            // Auto-select first color scheme
            if (!selectedColorScheme && Object.keys(colorSchemes).length > 0) {
                selectColorScheme(Object.keys(colorSchemes)[0]);
            }
        }
    } catch (error) {
        console.error('Failed to load color schemes:', error);
    }
}

/**
 * Display color schemes in the UI
 */
function displayColorSchemes() {
    const container = document.getElementById('color-schemes-container');
    if (!container || !colorSchemes) return;
    
    container.innerHTML = '';
    
    Object.keys(colorSchemes).forEach(schemeId => {
        const scheme = colorSchemes[schemeId];
        
        const card = document.createElement('div');
        card.className = `template-card mb-2 ${selectedColorScheme === schemeId ? 'selected' : ''}`;
        card.setAttribute('data-color-scheme', schemeId);
        card.onclick = () => selectColorScheme(schemeId);
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center p-3">
                <div>
                    <h6 class="mb-1">${scheme.name}</h6>
                    <small class="text-muted">${scheme.description}</small>
                </div>
                <div class="color-scheme-preview d-flex">
                    <div class="color-swatch" style="background-color: ${scheme.primary_color}; width: 30px; height: 30px; border-radius: 4px;"></div>
                    <div class="color-swatch ms-1" style="background-color: ${scheme.secondary_color}; width: 30px; height: 30px; border-radius: 4px;"></div>
                    <div class="color-swatch ms-1" style="background-color: ${scheme.accent_color}; width: 30px; height: 30px; border-radius: 4px;"></div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

/**
 * Select a template
 */
function selectTemplate(templateId) {
    console.log('Selecting template:', templateId);
    selectedTemplate = templateId;
    
    // Update UI
    document.querySelectorAll('.template-card').forEach(card => {
        if (card.dataset.template === templateId) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    // Update preview
    updatePreview();
}

/**
 * Select a color scheme
 */
function selectColorScheme(schemeId) {
    console.log('Selecting color scheme:', schemeId);
    selectedColorScheme = schemeId;
    
    // Update UI
    document.querySelectorAll('[data-color-scheme]').forEach(card => {
        if (card.dataset.colorScheme === schemeId) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
    
    // Update preview
    updatePreview();
}

/**
 * Update preview
 */
function updatePreview() {
    const preview = document.getElementById('presentation-preview');
    if (preview) {
        preview.innerHTML = `
            <div class="text-center">
                <h5>Selected Template: ${templates[selectedTemplate]?.name || 'None'}</h5>
                <p>Color Scheme: ${colorSchemes[selectedColorScheme]?.name || 'Default'}</p>
            </div>
        `;
    }
}

/**
 * Navigate to next step
 */
function nextStep() {
    if (currentStep < 4) {
        currentStep++;
        updateStepDisplay();
    }
}

/**
 * Navigate to previous step
 */
function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

/**
 * Update step display
 */
function updateStepDisplay() {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(step => {
        step.style.display = 'none';
    });
    
    // Show current step
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    if (currentStepElement) {
        currentStepElement.style.display = 'block';
    }
    
    // Update progress
    updateProgress();
    
    // Update buttons
    updateNavigationButtons();
}

/**
 * Update progress indicator
 */
function updateProgress() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const progress = (currentStep / 4) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }
    
    // Update step indicators
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
        if (index < currentStep) {
            indicator.classList.add('completed');
            indicator.classList.remove('active');
        } else if (index === currentStep - 1) {
            indicator.classList.add('active');
            indicator.classList.remove('completed');
        } else {
            indicator.classList.remove('active', 'completed');
        }
    });
}

/**
 * Update navigation buttons
 */
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-step-btn');
    const nextBtn = document.getElementById('next-step-btn');
    const generateBtn = document.getElementById('generate-presentation-btn');
    
    if (prevBtn) {
        prevBtn.style.display = currentStep > 1 ? 'inline-block' : 'none';
    }
    
    if (nextBtn) {
        nextBtn.style.display = currentStep < 4 ? 'inline-block' : 'none';
    }
    
    if (generateBtn) {
        generateBtn.style.display = currentStep === 4 ? 'inline-block' : 'none';
    }
}

/**
 * Generate PowerPoint presentation
 */
async function generatePresentation() {
    console.log('Generating presentation with template:', selectedTemplate);
    
    if (!roiData) {
        loaderManager.showError('Please select or load ROI calculation data first');
        return;
    }
    
    if (!selectedTemplate) {
        loaderManager.showError('Please select a template');
        return;
    }
    
    // Gather all form data
    const formData = {
        template: selectedTemplate,
        color_scheme: selectedColorScheme,
        roi_data: roiData,
        company_info: {
            name: document.getElementById('company-name')?.value || '',
            phone: document.getElementById('company-phone')?.value || '',
            email: document.getElementById('company-email')?.value || '',
            website: document.getElementById('company-website')?.value || '',
            tagline: document.getElementById('company-tagline')?.value || ''
        },
        include_slides: {
            title: document.getElementById('include-title')?.checked !== false,
            summary: document.getElementById('include-summary')?.checked !== false,
            roi_metrics: document.getElementById('include-roi')?.checked !== false,
            savings_breakdown: document.getElementById('include-savings')?.checked !== false,
            projections: document.getElementById('include-projections')?.checked !== false,
            next_steps: document.getElementById('include-next-steps')?.checked !== false
        }
    };
    
    try {
        const response = await fetchWithLoader(
            '/api/generate-powerpoint',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            },
            'Generating PowerPoint presentation...'
        );
        
        if (response.success && response.file_url) {
            // Download the file
            window.location.href = response.file_url;
            loaderManager.showSuccess('PowerPoint presentation generated successfully!');
        } else {
            throw new Error(response.error || 'Failed to generate presentation');
        }
    } catch (error) {
        console.error('Error generating presentation:', error);
        loaderManager.showError('Failed to generate presentation: ' + error.message);
    }
}

// Additional functions needed by HTML
function useCurrentCalculation() {
    const currentData = sessionStorage.getItem('currentROIData');
    if (currentData) {
        roiData = JSON.parse(currentData);
        updateCurrentCalculationDisplay();
        nextStep();
    } else {
        loaderManager.showError('No current calculation found. Please run a calculation first.');
    }
}

function loadSavedCalculation() {
    const calcSelect = document.getElementById('saved-calculations-select');
    if (calcSelect && calcSelect.value) {
        loadCalculationData(calcSelect.value);
        nextStep();
    } else {
        loaderManager.showError('Please select a calculation to load.');
    }
}

function previousStep() {
    prevStep();
}

function generatePowerPoint() {
    generatePresentation();
}

function generateAnother() {
    currentStep = 1;
    updateStepDisplay();
    const successMessage = document.getElementById('success-message');
    if (successMessage) {
        successMessage.style.display = 'none';
    }
}

// Export functions for global use
window.selectTemplate = selectTemplate;
window.selectColorScheme = selectColorScheme;
window.generatePresentation = generatePresentation;
window.nextStep = nextStep;
window.prevStep = prevStep;
window.previousStep = previousStep;
window.useCurrentCalculation = useCurrentCalculation;
window.loadSavedCalculation = loadSavedCalculation;
window.generatePowerPoint = generatePowerPoint;
window.generateAnother = generateAnother;