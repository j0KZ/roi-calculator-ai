/**
 * Universal Loader Utilities
 * Provides consistent loading state management across all pages
 */

class LoaderManager {
    constructor() {
        this.activeLoaders = new Set();
        this.timeout = 30000; // 30 second timeout
        this.createGlobalLoader();
    }

    /**
     * Create a global loading overlay
     */
    createGlobalLoader() {
        if (document.getElementById('globalLoader')) return;
        
        const loader = document.createElement('div');
        loader.id = 'globalLoader';
        loader.className = 'global-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner-border text-warning" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="loader-message mt-3">Processing...</div>
            </div>
        `;
        document.body.appendChild(loader);
    }

    /**
     * Show loading state with timeout protection
     */
    show(message = 'Loading...', loaderId = 'default') {
        this.activeLoaders.add(loaderId);
        
        const loader = document.getElementById('globalLoader');
        if (loader) {
            loader.style.display = 'flex';
            const messageEl = loader.querySelector('.loader-message');
            if (messageEl) messageEl.textContent = message;
        }

        // Auto-hide after timeout to prevent stuck states
        setTimeout(() => {
            if (this.activeLoaders.has(loaderId)) {
                console.warn(`Loader timeout for: ${loaderId}`);
                this.hide(loaderId);
                this.showError('Operation timed out. Please try again.');
            }
        }, this.timeout);

        return loaderId;
    }

    /**
     * Hide loading state
     */
    hide(loaderId = 'default') {
        this.activeLoaders.delete(loaderId);
        
        if (this.activeLoaders.size === 0) {
            const loader = document.getElementById('globalLoader');
            if (loader) {
                loader.style.display = 'none';
            }
        }
    }

    /**
     * Hide all loaders immediately
     */
    hideAll() {
        this.activeLoaders.clear();
        const loader = document.getElementById('globalLoader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        // Create or update error toast
        let toast = document.getElementById('errorToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'errorToast';
            toast.className = 'error-toast';
            document.body.appendChild(toast);
        }
        
        toast.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
            </div>
        `;
        toast.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (toast) toast.style.display = 'none';
        }, 5000);
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        let toast = document.getElementById('successToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'successToast';
            toast.className = 'success-toast';
            document.body.appendChild(toast);
        }
        
        toast.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
            </div>
        `;
        toast.style.display = 'block';
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (toast) toast.style.display = 'none';
        }, 3000);
    }
}

// Create global instance
const loaderManager = new LoaderManager();

/**
 * Enhanced fetch with error handling and loading states
 */
async function fetchWithLoader(url, options = {}, loadingMessage = 'Loading...') {
    const loaderId = `fetch-${Date.now()}`;
    loaderManager.show(loadingMessage, loaderId);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 25000); // 25 second timeout
        
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        loaderManager.hide(loaderId);
        return data;
        
    } catch (error) {
        loaderManager.hide(loaderId);
        
        if (error.name === 'AbortError') {
            loaderManager.showError('Request timed out. Please check your connection and try again.');
        } else {
            loaderManager.showError(`Error: ${error.message}`);
        }
        
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * Debounce function to prevent too many API calls
 */
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

/**
 * Initialize loader on all pages
 */
document.addEventListener('DOMContentLoaded', function() {
    // Hide any stuck loaders on page load
    loaderManager.hideAll();
    
    // Add global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        loaderManager.hideAll();
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        loaderManager.hideAll();
        loaderManager.showError('An unexpected error occurred. Please refresh the page.');
    });
});

// Export for use in other scripts
window.loaderManager = loaderManager;
window.fetchWithLoader = fetchWithLoader;
window.debounce = debounce;