/**
 * Currency and Tax Configuration JavaScript
 * Handles multi-currency support and tax calculations
 */

class CurrencyTaxManager {
    constructor() {
        this.currencies = {};
        this.exchangeRates = {};
        this.taxJurisdictions = {};
        this.currentResults = null;
        
        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // Main form submission
        document.getElementById('currencyTaxForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateWithCurrencyTax();
        });

        // Load example data
        document.getElementById('loadExampleBtn').addEventListener('click', () => {
            this.loadExampleData();
        });

        // Update exchange rates
        document.getElementById('updateRatesBtn').addEventListener('click', () => {
            this.updateExchangeRates();
        });

        // Enable/disable tax configuration
        document.getElementById('enableTax').addEventListener('change', (e) => {
            this.toggleTaxConfig(e.target.checked);
        });

        // Tax jurisdiction change
        document.getElementById('tax_jurisdiction').addEventListener('change', (e) => {
            this.loadTaxRegions(e.target.value);
        });

        // Tax region change
        document.getElementById('tax_region').addEventListener('change', () => {
            this.updateTaxRateInfo();
        });

        // Currency converter
        document.getElementById('convertBtn').addEventListener('click', () => {
            this.convertCurrency();
        });

        // Auto-convert on input changes
        ['convertAmount', 'fromCurrency', 'toCurrency'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => {
                this.convertCurrency();
            });
        });
    }

    async loadInitialData() {
        try {
            // Load currencies and exchange rates
            await this.loadCurrencies();
            
            // Load tax jurisdictions
            await this.loadTaxJurisdictions();
            
            // Initialize currency selectors
            this.populateCurrencySelectors();
            
            // Set initial exchange rate info
            this.updateExchangeRateInfo();

        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load currency and tax data: ' + error.message);
        }
    }

    async loadCurrencies() {
        try {
            const response = await fetch('/api/currencies');
            if (!response.ok) throw new Error('Failed to load currencies');
            
            const data = await response.json();
            this.currencies = data.currencies;
            this.exchangeRates = data.rates.rates;
            
        } catch (error) {
            console.error('Error loading currencies:', error);
            throw error;
        }
    }

    async loadTaxJurisdictions() {
        try {
            const response = await fetch('/api/tax-jurisdictions');
            if (!response.ok) throw new Error('Failed to load tax jurisdictions');
            
            const data = await response.json();
            this.taxJurisdictions = data.jurisdictions;
            
            this.populateTaxJurisdictions();
            
        } catch (error) {
            console.error('Error loading tax jurisdictions:', error);
            throw error;
        }
    }

    populateCurrencySelectors() {
        const selectors = ['target_currency', 'fromCurrency', 'toCurrency'];
        
        selectors.forEach(selectorId => {
            const select = document.getElementById(selectorId);
            select.innerHTML = ''; // Clear existing options
            
            Object.entries(this.currencies).forEach(([code, info]) => {
                const option = document.createElement('option');
                option.value = code;
                option.textContent = `${code} - ${info.name}`;
                
                // Set default selections
                if (selectorId === 'target_currency' && code === 'USD') {
                    option.selected = true;
                } else if (selectorId === 'fromCurrency' && code === 'USD') {
                    option.selected = true;
                } else if (selectorId === 'toCurrency' && code === 'EUR') {
                    option.selected = true;
                }
                
                select.appendChild(option);
            });
        });
    }

    populateTaxJurisdictions() {
        const select = document.getElementById('tax_jurisdiction');
        select.innerHTML = '<option value="">Select Jurisdiction...</option>';
        
        Object.entries(this.taxJurisdictions).forEach(([code, info]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = `${info.name} (${info.tax_type} - ${(info.default_rate * 100).toFixed(1)}%)`;
            select.appendChild(option);
        });
    }

    async loadTaxRegions(jurisdiction) {
        if (!jurisdiction) {
            document.getElementById('tax_region').innerHTML = '<option value="">Select Region...</option>';
            return;
        }

        try {
            const response = await fetch(`/api/tax-regions/${jurisdiction}`);
            if (!response.ok) throw new Error('Failed to load tax regions');
            
            const data = await response.json();
            
            const select = document.getElementById('tax_region');
            select.innerHTML = '<option value="">No specific region</option>';
            
            data.regions.forEach(region => {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                select.appendChild(option);
            });
            
            this.updateTaxRateInfo();
            
        } catch (error) {
            console.error('Error loading tax regions:', error);
        }
    }

    updateTaxRateInfo() {
        const jurisdiction = document.getElementById('tax_jurisdiction').value;
        const region = document.getElementById('tax_region').value;
        
        if (!jurisdiction || !this.taxJurisdictions[jurisdiction]) {
            document.getElementById('taxRateInfo').textContent = 'Select jurisdiction to see tax rate';
            return;
        }
        
        const jurisdictionData = this.taxJurisdictions[jurisdiction];
        let rate = jurisdictionData.default_rate;
        
        // This is a simplified lookup - in a real implementation,
        // you'd want to fetch the specific rate from the server
        const rateText = `${jurisdictionData.tax_type}: ${(rate * 100).toFixed(1)}%`;
        document.getElementById('taxRateInfo').textContent = rateText;
    }

    toggleTaxConfig(enabled) {
        const taxConfig = document.getElementById('taxConfig');
        if (enabled) {
            taxConfig.classList.remove('d-none');
        } else {
            taxConfig.classList.add('d-none');
        }
    }

    async updateExchangeRates() {
        const button = document.getElementById('updateRatesBtn');
        const originalText = button.innerHTML;
        
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Updating...';
        button.disabled = true;
        
        try {
            const response = await fetch('/api/update-exchange-rates', {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error('Failed to update exchange rates');
            
            const data = await response.json();
            this.exchangeRates = data.rates.rates;
            
            this.updateExchangeRateInfo();
            this.showSuccess('Exchange rates updated successfully');
            
        } catch (error) {
            console.error('Error updating exchange rates:', error);
            this.showError('Failed to update exchange rates: ' + error.message);
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    updateExchangeRateInfo() {
        const now = new Date().toLocaleString();
        document.getElementById('rateUpdateTime').textContent = now;
    }

    loadExampleData() {
        // Load example business data
        document.getElementById('company_name').value = 'Example E-commerce Ltd.';
        document.getElementById('annual_revenue').value = '2000000';
        document.getElementById('monthly_orders').value = '5000';
        document.getElementById('avg_order_value').value = '33.33';
        document.getElementById('labor_costs').value = '8000';
        document.getElementById('shipping_costs').value = '5000';
        document.getElementById('error_costs').value = '2000';
        document.getElementById('inventory_costs').value = '3000';
        document.getElementById('service_investment').value = '50000';
        
        // Set example currency and tax config
        document.getElementById('target_currency').value = 'EUR';
        document.getElementById('enableTax').checked = true;
        this.toggleTaxConfig(true);
        document.getElementById('tax_jurisdiction').value = 'EU';
        this.loadTaxRegions('EU');
    }

    getFormData() {
        const taxEnabled = document.getElementById('enableTax').checked;
        
        const data = {
            // Business data
            company_name: document.getElementById('company_name').value,
            annual_revenue: parseFloat(document.getElementById('annual_revenue').value),
            monthly_orders: parseFloat(document.getElementById('monthly_orders').value),
            avg_order_value: parseFloat(document.getElementById('avg_order_value').value),
            labor_costs: parseFloat(document.getElementById('labor_costs').value),
            shipping_costs: parseFloat(document.getElementById('shipping_costs').value),
            error_costs: parseFloat(document.getElementById('error_costs').value),
            inventory_costs: parseFloat(document.getElementById('inventory_costs').value),
            service_investment: parseFloat(document.getElementById('service_investment').value),
            
            // Currency configuration
            target_currency: document.getElementById('target_currency').value
        };
        
        // Tax configuration (if enabled)
        if (taxEnabled) {
            data.tax_config = {
                jurisdiction: document.getElementById('tax_jurisdiction').value,
                region: document.getElementById('tax_region').value || null,
                investment_deductible: document.getElementById('investment_deductible').checked
            };
        }
        
        return data;
    }

    async calculateWithCurrencyTax() {
        const data = this.getFormData();
        
        if (!this.validateInputs(data)) {
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/calculate-with-currency-tax', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            this.currentResults = results;
            
            this.hideLoading();
            this.displayResults(results);

        } catch (error) {
            console.error('Currency/Tax calculation error:', error);
            this.hideLoading();
            this.showError('Failed to calculate ROI: ' + error.message);
        }
    }

    validateInputs(data) {
        const errors = [];

        // Validate numeric fields
        const numericFields = [
            'annual_revenue', 'monthly_orders', 'avg_order_value',
            'labor_costs', 'shipping_costs', 'error_costs', 
            'inventory_costs', 'service_investment'
        ];

        numericFields.forEach(field => {
            if (isNaN(data[field]) || data[field] < 0) {
                errors.push(`${field.replace('_', ' ')} must be a positive number`);
            }
        });

        // Validate tax configuration if enabled
        if (data.tax_config && !data.tax_config.jurisdiction) {
            errors.push('Please select a tax jurisdiction');
        }

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
        this.displayROIMetrics(results);
        this.displayCurrencyImpact(results);
        this.displayTaxImpact(results);
        this.displayComparison(results);
        this.updateConversionInfo(results);
    }

    displayROIMetrics(results) {
        const metrics = results.roi_metrics;
        const currency = results.currency || 'USD';
        const symbol = this.currencies[currency]?.symbol || '$';

        const metricsHTML = `
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-primary">${metrics.first_year_roi?.toFixed(1) || 'N/A'}%</h4>
                    <small class="text-muted">First Year ROI</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-info">${metrics.payback_period_months?.toFixed(1) || 'N/A'}</h4>
                    <small class="text-muted">Payback (Months)</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-success">${symbol}${this.formatNumber(metrics.annual_savings) || 'N/A'}</h4>
                    <small class="text-muted">Annual Savings</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="text-center">
                    <h4 class="text-warning">${symbol}${this.formatNumber(results.financial_metrics?.npv) || 'N/A'}</h4>
                    <small class="text-muted">Net Present Value</small>
                </div>
            </div>
        `;

        document.getElementById('roiMetrics').innerHTML = metricsHTML;
    }

    updateConversionInfo(results) {
        const metadata = results.calculation_metadata;
        let infoText = '';

        if (metadata.currency_converted) {
            infoText += `<i class="fas fa-exchange-alt me-1"></i>Converted to ${metadata.target_currency} `;
        }

        if (metadata.tax_applied) {
            const taxConfig = metadata.tax_config;
            infoText += `<i class="fas fa-receipt me-1"></i>Tax: ${taxConfig.jurisdiction}${taxConfig.region ? ` (${taxConfig.region})` : ''} `;
        }

        if (!infoText) {
            infoText = '<i class="fas fa-info-circle me-1"></i>Base USD calculation, no tax applied';
        }

        document.getElementById('conversionInfo').innerHTML = infoText;
    }

    displayCurrencyImpact(results) {
        const conversionInfo = results.conversion_info;
        const card = document.getElementById('currencyImpactCard');

        if (!conversionInfo || results.currency === 'USD') {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'block';

        const impactHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Currency Conversion</h6>
                    <p>From: ${conversionInfo.original_currency} → ${conversionInfo.target_currency}</p>
                    <p>Exchange Rate: ${conversionInfo.exchange_rate || 'N/A'}</p>
                    <p>Conversion Date: ${new Date(conversionInfo.conversion_date).toLocaleString()}</p>
                </div>
                <div class="col-md-6">
                    <h6>Currency Impact</h6>
                    <p class="text-muted">All monetary values have been converted to ${results.currency} using current exchange rates.</p>
                </div>
            </div>
        `;

        document.getElementById('currencyImpactDetails').innerHTML = impactHTML;
    }

    displayTaxImpact(results) {
        const taxAnalysis = results.tax_analysis;
        const card = document.getElementById('taxImpactCard');

        if (!taxAnalysis) {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'block';

        const currency = results.currency || 'USD';
        const symbol = this.currencies[currency]?.symbol || '$';
        const taxConfig = taxAnalysis.tax_config;

        const impactHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Tax Configuration</h6>
                    <p><strong>Jurisdiction:</strong> ${taxConfig.jurisdiction_name}</p>
                    <p><strong>Tax Type:</strong> ${taxConfig.tax_type}</p>
                    <p><strong>Tax Rate:</strong> ${(taxConfig.tax_rate * 100).toFixed(1)}%</p>
                    ${taxConfig.region ? `<p><strong>Region:</strong> ${taxConfig.region}</p>` : ''}
                </div>
                <div class="col-md-6">
                    <h6>Tax Impact on ROI</h6>
                    ${taxAnalysis.tax_adjusted_metrics ? `
                        <p><strong>ROI After Tax:</strong> ${taxAnalysis.tax_adjusted_metrics.roi_percentage?.toFixed(1) || 'N/A'}%</p>
                        <p><strong>Annual Savings After Tax:</strong> ${symbol}${this.formatNumber(taxAnalysis.tax_adjusted_metrics.annual_savings_after_tax)}</p>
                        <p><strong>Effective Investment:</strong> ${symbol}${this.formatNumber(taxAnalysis.tax_adjusted_metrics.effective_investment)}</p>
                    ` : '<p class="text-muted">Tax impact calculated - see comparison table for details.</p>'}
                </div>
            </div>
            
            ${taxAnalysis.savings_tax_impact ? `
                <hr>
                <div class="row">
                    <div class="col-12">
                        <h6>Tax Liability on Savings</h6>
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <tr>
                                    <td>Annual Tax Liability:</td>
                                    <td>${symbol}${this.formatNumber(taxAnalysis.savings_tax_impact.annual.tax_amount)}</td>
                                </tr>
                                <tr>
                                    <td>Monthly Tax Liability:</td>
                                    <td>${symbol}${this.formatNumber(taxAnalysis.savings_tax_impact.monthly.tax_amount)}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            ` : ''}
        `;

        document.getElementById('taxImpactDetails').innerHTML = impactHTML;
    }

    displayComparison(results) {
        // This would compare base USD results with currency/tax adjusted results
        // For now, we'll show key metrics in different scenarios

        const currency = results.currency || 'USD';
        const symbol = this.currencies[currency]?.symbol || '$';
        const taxAnalysis = results.tax_analysis;

        const rows = [
            {
                metric: 'Annual Revenue',
                base: this.formatCurrency(results.inputs.annual_revenue, 'USD'),
                adjusted: this.formatCurrency(results.inputs.annual_revenue, currency),
                impact: results.currency !== 'USD' ? 'Currency converted' : '-'
            },
            {
                metric: 'Service Investment',
                base: this.formatCurrency(results.inputs.service_investment, 'USD'),
                adjusted: taxAnalysis?.tax_adjusted_metrics ? 
                    this.formatCurrency(taxAnalysis.tax_adjusted_metrics.effective_investment, currency) :
                    this.formatCurrency(results.inputs.service_investment, currency),
                impact: taxAnalysis?.tax_adjusted_metrics ? 'Tax deduction applied' : 
                    (results.currency !== 'USD' ? 'Currency converted' : '-')
            },
            {
                metric: 'Annual Savings',
                base: this.formatCurrency(results.savings.annual_total, 'USD'),
                adjusted: taxAnalysis?.tax_adjusted_metrics ? 
                    this.formatCurrency(taxAnalysis.tax_adjusted_metrics.annual_savings_after_tax, currency) :
                    this.formatCurrency(results.savings.annual_total, currency),
                impact: taxAnalysis?.tax_adjusted_metrics ? 'After tax liability' : 
                    (results.currency !== 'USD' ? 'Currency converted' : '-')
            },
            {
                metric: 'First Year ROI',
                base: `${results.roi_metrics.first_year_roi?.toFixed(1) || 'N/A'}%`,
                adjusted: taxAnalysis?.tax_adjusted_metrics ? 
                    `${taxAnalysis.tax_adjusted_metrics.roi_percentage?.toFixed(1) || 'N/A'}%` :
                    `${results.roi_metrics.first_year_roi?.toFixed(1) || 'N/A'}%`,
                impact: taxAnalysis?.tax_adjusted_metrics ? 
                    `${((taxAnalysis.tax_adjusted_metrics.roi_percentage - results.roi_metrics.first_year_roi) || 0).toFixed(1)}% change` :
                    '-'
            }
        ];

        const tableBody = document.getElementById('comparisonTableBody');
        tableBody.innerHTML = rows.map(row => `
            <tr>
                <td><strong>${row.metric}</strong></td>
                <td>${row.base}</td>
                <td>${row.adjusted}</td>
                <td><small class="text-muted">${row.impact}</small></td>
            </tr>
        `).join('');
    }

    async convertCurrency() {
        const amount = parseFloat(document.getElementById('convertAmount').value);
        const fromCurrency = document.getElementById('fromCurrency').value;
        const toCurrency = document.getElementById('toCurrency').value;

        if (isNaN(amount) || amount <= 0) {
            document.getElementById('conversionResult').classList.add('d-none');
            return;
        }

        try {
            const response = await fetch('/api/currency-convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: amount,
                    from_currency: fromCurrency,
                    to_currency: toCurrency
                })
            });

            if (!response.ok) throw new Error('Conversion failed');

            const result = await response.json();

            const resultElement = document.getElementById('conversionResult');
            resultElement.innerHTML = `
                <strong>${this.formatCurrency(result.original_amount, result.from_currency)} = 
                ${this.formatCurrency(result.converted_amount, result.to_currency)}</strong><br>
                <small>Exchange Rate: 1 ${result.from_currency} = ${result.exchange_rate} ${result.to_currency}</small>
            `;
            resultElement.classList.remove('d-none');

        } catch (error) {
            console.error('Currency conversion error:', error);
            const resultElement = document.getElementById('conversionResult');
            resultElement.innerHTML = `<span class="text-danger">Conversion failed: ${error.message}</span>`;
            resultElement.classList.remove('d-none');
        }
    }

    formatCurrency(amount, currency) {
        if (amount === null || amount === undefined) return 'N/A';
        const symbol = this.currencies[currency]?.symbol || '$';
        return `${symbol}${this.formatNumber(amount)}`;
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

        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }

    showSuccess(message) {
        const alertHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        container.insertAdjacentHTML('afterbegin', alertHTML);

        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) alert.remove();
        }, 3000);
    }
}

// Initialize the currency tax manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CurrencyTaxManager();
});