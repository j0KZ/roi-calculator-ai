/**
 * PowerPoint Export JavaScript
 * Handles PowerPoint presentation generation with template selection and customization
 */

// Global variables
let currentStep = 1;
let selectedTemplate = null;
let selectedColorScheme = null;
let roiData = null;
let templates = {};
let colorSchemes = {};

// Initialize when document is ready
$(document).ready(function() {
    initializePowerPoint();
    loadSavedCalculations();
    loadTemplates();
    loadColorSchemes();
});

/**
 * Initialize PowerPoint export functionality
 */
function initializePowerPoint() {
    console.log('Initializing PowerPoint export...');
    
    // Check if there's current ROI data in session storage
    const currentData = sessionStorage.getItem('currentROIData');
    if (currentData) {
        roiData = JSON.parse(currentData);
        updateCurrentCalculationDisplay();
    }
    
    // Set default company information
    setDefaultCompanyInfo();
}

/**
 * Set default company information
 */
function setDefaultCompanyInfo() {
    $('#company-name').val('ROI Solutions Inc.');
    $('#company-phone').val('+1 (555) 123-4567');
    $('#company-email').val('contact@roisolutions.com');
    $('#company-website').val('www.roisolutions.com');
    $('#company-tagline').val('Maximizing Your Investment Returns');
}

/**
 * Load saved calculations for selection
 */
function loadSavedCalculations() {
    $.get('/api/calculations')
        .done(function(response) {
            if (response.success) {
                const select = $('#saved-calculations-select');
                select.empty().append('<option value="">Select a saved calculation...</option>');
                
                response.calculations.forEach(function(calc) {
                    const option = $('<option></option>')
                        .attr('value', calc.id)
                        .text(`${calc.company_name || 'Unnamed'} - ${new Date(calc.created_at).toLocaleDateString()}`);
                    select.append(option);
                });
            }
        })
        .fail(function(xhr) {
            console.error('Failed to load saved calculations:', xhr.responseJSON?.message);
        });
}

/**
 * Load available PowerPoint templates
 */
function loadTemplates() {
    $.get('/api/powerpoint-templates')
        .done(function(response) {
            if (response.success) {
                templates = response.templates;
                displayTemplates();
            }
        })
        .fail(function(xhr) {
            console.error('Failed to load templates:', xhr.responseJSON?.message);
            showError('Failed to load templates. Please refresh the page.');
        });
}

/**
 * Load available color schemes
 */
function loadColorSchemes() {
    $.get('/api/powerpoint-color-schemes')
        .done(function(response) {
            if (response.success) {
                colorSchemes = response.color_schemes;
                displayColorSchemes();
            }
        })
        .fail(function(xhr) {
            console.error('Failed to load color schemes:', xhr.responseJSON?.message);
        });
}

/**
 * Display templates in the UI
 */
function displayTemplates() {
    const container = $('#templates-container');
    container.empty();
    
    Object.keys(templates).forEach(function(templateId) {
        const template = templates[templateId];
        
        const card = $(`
            <div class="col-md-4 mb-3">
                <div class="template-card" data-template="${templateId}" onclick="selectTemplate('${templateId}')">
                    <div class="text-center">
                        <i class="fas fa-file-powerpoint fa-3x mb-3" style="color: #D04A37;"></i>
                        <h5>${template.name}</h5>
                        <p class="text-muted">${template.description}</p>
                        <ul class="feature-list text-left">
                            <li>Professional design</li>
                            <li>Data visualizations</li>
                            <li>Speaker notes</li>
                            <li>Customizable colors</li>
                        </ul>
                    </div>
                </div>
            </div>
        `);
        
        container.append(card);
    });
}

/**
 * Display color schemes in the UI
 */
function displayColorSchemes() {
    const container = $('#color-schemes-container');
    container.empty();
    
    Object.keys(colorSchemes).forEach(function(schemeId) {
        const scheme = colorSchemes[schemeId];
        
        const card = $(`
            <div class="template-card mb-2" data-color-scheme="${schemeId}" onclick="selectColorScheme('${schemeId}')">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6>${scheme.name}</h6>
                        <small class="text-muted">${scheme.description}</small>
                    </div>
                    <div class="color-scheme-preview">
                        <div class="color-swatch" style="background-color: ${scheme.primary_color};"></div>
                        <div class="color-swatch ml-1" style="background-color: ${scheme.secondary_color};"></div>
                        <div class="color-swatch ml-1" style="background-color: ${scheme.accent_color};"></div>
                    </div>
                </div>
            </div>
        `);
        
        container.append(card);
    });
    
    // Select first color scheme by default
    if (Object.keys(colorSchemes).length > 0) {
        selectColorScheme(Object.keys(colorSchemes)[0]);
    }
}

/**
 * Use current calculation data
 */
function useCurrentCalculation() {
    if (!roiData) {
        showError('No current calculation found. Please run a calculation first.');
        return;
    }
    
    $('#current-calculation-info').show();
    updateCurrentCalculationDisplay();
    nextStep();
}

/**
 * Update display of current calculation info
 */
function updateCurrentCalculationDisplay() {
    if (!roiData) return;
    
    const info = $('#current-calculation-details');
    const companyName = roiData.inputs?.company_name || 'Unnamed';
    const investment = roiData.inputs?.service_investment || 0;
    const roi = roiData.roi_metrics?.first_year_roi || 0;
    const savings = roiData.roi_metrics?.annual_savings || 0;
    
    info.html(`
        <strong>${companyName}</strong><br>
        Investment: $${investment.toLocaleString()}<br>
        First Year ROI: ${(roi * 100).toFixed(1)}%<br>
        Annual Savings: $${savings.toLocaleString()}
    `);
}

/**
 * Load a saved calculation
 */
function loadSavedCalculation() {
    const calcId = $('#saved-calculations-select').val();
    if (!calcId) {
        showError('Please select a calculation to load.');
        return;
    }
    
    $.get(`/api/calculation/${calcId}`)
        .done(function(response) {
            if (response.success) {
                // Convert calculation data to ROI results format
                const calc = response.calculation;
                roiData = {
                    inputs: {
                        company_name: calc.company_name,
                        annual_revenue: calc.annual_revenue,
                        monthly_orders: calc.monthly_orders,
                        avg_order_value: calc.avg_order_value,
                        labor_costs: calc.labor_costs,
                        shipping_costs: calc.shipping_costs,
                        error_costs: calc.error_costs,
                        inventory_costs: calc.inventory_costs,
                        service_investment: calc.service_investment
                    },
                    ...calc.results
                };
                
                // Update company name in form
                $('#company-name').val(calc.company_name || '');
                
                showSuccess('Calculation loaded successfully!');
                nextStep();
            }
        })
        .fail(function(xhr) {
            showError('Failed to load calculation: ' + (xhr.responseJSON?.message || 'Unknown error'));
        });
}

/**
 * Select a template
 */
function selectTemplate(templateId) {
    selectedTemplate = templateId;
    
    // Update UI
    $('.template-card').removeClass('selected');
    $(`.template-card[data-template="${templateId}"]`).addClass('selected');
    
    // Enable next step
    nextStep();
}

/**
 * Select a color scheme
 */
function selectColorScheme(schemeId) {
    selectedColorScheme = schemeId;
    
    // Update UI
    $('[data-color-scheme]').removeClass('selected');
    $(`[data-color-scheme="${schemeId}"]`).addClass('selected');
}

/**
 * Generate PowerPoint presentation
 */
function generatePowerPoint() {
    if (!roiData) {
        showError('No calculation data available. Please select a calculation first.');
        return;
    }
    
    if (!selectedTemplate) {
        showError('Please select a template first.');
        return;
    }
    
    // Show generation status
    $('#generation-status').show();
    $('#step-4-content').hide();
    
    // Start progress animation
    animateProgress();
    
    // Prepare request data
    const requestData = {
        results: roiData,
        template: selectedTemplate,
        company_config: {
            name: $('#company-name').val() || 'Your Company',
            phone: $('#company-phone').val() || '',
            email: $('#company-email').val() || '',
            website: $('#company-website').val() || '',
            tagline: $('#company-tagline').val() || ''
        },
        color_scheme: selectedColorScheme ? colorSchemes[selectedColorScheme] : null,
        include_speaker_notes: $('#include-speaker-notes').is(':checked'),
        include_charts: $('#include-charts').is(':checked'),
        include_implementation_timeline: $('#include-implementation-timeline').is(':checked')
    };
    
    // Make request to generate PowerPoint
    $.ajax({
        url: '/api/generate-powerpoint',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(requestData),
        timeout: 120000 // 2 minutes timeout
    })
    .done(function(response) {
        if (response.success) {
            showGenerationSuccess(response.download_url, response.filename);
        } else {
            showError('Generation failed: ' + (response.error || 'Unknown error'));
        }
    })
    .fail(function(xhr) {
        let errorMessage = 'Failed to generate PowerPoint presentation';
        if (xhr.responseJSON?.error) {
            errorMessage += ': ' + xhr.responseJSON.error;
        } else if (xhr.status === 0) {
            errorMessage += ': Network error or timeout';
        }
        showError(errorMessage);
    })
    .always(function() {
        $('#generation-status').hide();
        $('#step-4-content').show();
    });
}

/**
 * Animate progress bar during generation
 */
function animateProgress() {
    let progress = 0;
    const steps = [
        { progress: 25, text: 'Loading ROI data...', id: 'step-load-data' },
        { progress: 50, text: 'Creating data visualizations...', id: 'step-create-charts' },
        { progress: 75, text: 'Building presentation slides...', id: 'step-build-slides' },
        { progress: 95, text: 'Finalizing presentation...', id: 'step-finalize' }
    ];
    
    let currentStepIndex = 0;
    
    const interval = setInterval(function() {
        if (currentStepIndex < steps.length) {
            const step = steps[currentStepIndex];
            progress = step.progress;
            
            $('#progress-bar').css('width', progress + '%');
            $('.generation-step').removeClass('active').css('color', '#666');
            $('#' + step.id).addClass('active').css('color', '#2196f3');
            
            currentStepIndex++;
        } else {
            clearInterval(interval);
        }
    }, 2000);
}

/**
 * Show generation success message
 */
function showGenerationSuccess(downloadUrl, filename) {
    $('#success-message').show();
    $('#download-link').attr('href', downloadUrl).show();
    
    // Scroll to success message
    $('html, body').animate({
        scrollTop: $('#success-message').offset().top - 100
    }, 500);
}

/**
 * Generate another presentation
 */
function generateAnother() {
    $('#success-message').hide();
    currentStep = 1;
    updateStepDisplay();
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
function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

/**
 * Update step display and navigation
 */
function updateStepDisplay() {
    // Hide all step content
    $('[id^="step-"][id$="-content"]').hide();
    
    // Show current step content
    $(`#step-${currentStep}-content`).show();
    
    // Update step indicators
    $('.step').removeClass('active completed');
    for (let i = 1; i <= 4; i++) {
        if (i < currentStep) {
            $(`#step-${i}`).addClass('completed');
        } else if (i === currentStep) {
            $(`#step-${i}`).addClass('active');
        }
    }
    
    // Update navigation buttons
    if (currentStep === 1) {
        $('#prev-btn').hide();
        $('#next-btn').hide();
    } else if (currentStep === 4) {
        $('#prev-btn').show();
        $('#next-btn').hide();
    } else {
        $('#prev-btn').show();
        $('#next-btn').show();
    }
    
    // Validate step completion
    validateCurrentStep();
}

/**
 * Validate current step for enabling next button
 */
function validateCurrentStep() {
    let canProceed = false;
    
    switch (currentStep) {
        case 1:
            canProceed = roiData !== null;
            break;
        case 2:
            canProceed = selectedTemplate !== null;
            break;
        case 3:
            canProceed = true; // Customization is optional
            break;
        case 4:
            canProceed = true; // Can always generate
            break;
    }
    
    $('#next-btn').prop('disabled', !canProceed);
}

/**
 * Show error message
 */
function showError(message) {
    $('#error-text').text(message);
    $('#error-message').show();
    
    // Hide after 10 seconds
    setTimeout(function() {
        $('#error-message').hide();
    }, 10000);
    
    // Scroll to error message
    $('html, body').animate({
        scrollTop: $('#error-message').offset().top - 100
    }, 500);
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Create temporary success alert
    const successAlert = $(`
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `);
    
    $('body').prepend(successAlert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        successAlert.fadeOut(function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Export current session data for other components
 */
function exportCurrentData() {
    return {
        roiData: roiData,
        selectedTemplate: selectedTemplate,
        selectedColorScheme: selectedColorScheme
    };
}

/**
 * Import session data from other components
 */
function importCurrentData(data) {
    if (data.roiData) {
        roiData = data.roiData;
        updateCurrentCalculationDisplay();
    }
    if (data.selectedTemplate) {
        selectTemplate(data.selectedTemplate);
    }
    if (data.selectedColorScheme) {
        selectColorScheme(data.selectedColorScheme);
    }
}