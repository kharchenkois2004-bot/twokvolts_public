// Основные JavaScript функции для проекта

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Confirm before deleting
    const deleteButtons = document.querySelectorAll('.btn-delete, a[href*="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить эту запись?')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // Add error message
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    errorDiv.textContent = 'Это поле обязательно для заполнения';
                    
                    if (!field.nextElementSibling?.classList.contains('invalid-feedback')) {
                        field.parentNode.insertBefore(errorDiv, field.nextSibling);
                    }
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
    
    // Real-time calculations for meter readings
    const meterValueInputs = document.querySelectorAll('.meter-value-input');
    meterValueInputs.forEach(input => {
        input.addEventListener('input', function() {
            const rate = parseFloat(this.dataset.rate) || 0;
            const prevValue = parseFloat(this.dataset.prevValue) || 0;
            const currentValue = parseFloat(this.value) || 0;
            
            if (currentValue > prevValue) {
                const consumption = currentValue - prevValue;
                const amount = consumption * rate;
                
                const amountElement = document.getElementById(this.dataset.amountId);
                if (amountElement) {
                    amountElement.textContent = amount.toFixed(2) + ' ₽';
                }
            }
        });
    });
    
    // Date picker enhancements
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set max date to today
        const today = new Date().toISOString().split('T')[0];
        if (!input.max) {
            input.max = today;
        }
        
        // Add calendar icon
        const wrapper = document.createElement('div');
        wrapper.className = 'input-group';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        const iconSpan = document.createElement('span');
        iconSpan.className = 'input-group-text';
        iconSpan.innerHTML = '<i class="fas fa-calendar-alt"></i>';
        wrapper.appendChild(iconSpan);
    });
    
    // Currency formatting
    const currencyElements = document.querySelectorAll('.currency');
    currencyElements.forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        if (!isNaN(value)) {
            element.textContent = new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB',
                minimumFractionDigits: 2
            }).format(value);
        }
    });
    
    // Number formatting
    const numberElements = document.querySelectorAll('.number-format');
    numberElements.forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        if (!isNaN(value)) {
            element.textContent = new Intl.NumberFormat('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }
    });
    
    // AJAX form submissions
    const ajaxForms = document.querySelectorAll('form.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Обработка...';
            submitBtn.disabled = true;
            
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success alert-dismissible fade show';
                    alertDiv.innerHTML = `
                        <i class="fas fa-check-circle me-2"></i>
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    
                    form.parentNode.insertBefore(alertDiv, form);
                    
                    // Reset form if needed
                    if (data.reset) {
                        form.reset();
                    }
                    
                    // Redirect if needed
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1500);
                    }
                } else {
                    // Show error message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                    alertDiv.innerHTML = `
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    
                    form.parentNode.insertBefore(alertDiv, form);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                alertDiv.innerHTML = `
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Произошла ошибка при отправке формы
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                form.parentNode.insertBefore(alertDiv, form);
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    });
    
    // Auto-refresh for dashboard (every 60 seconds)
    if (window.location.pathname.includes('/dashboard')) {
        setInterval(() => {
            // Only refresh if user is active
            if (!document.hidden) {
                fetch('/api/dashboard/stats/')
                    .then(response => response.json())
                    .then(data => {
                        // Update statistics cards
                        document.querySelectorAll('.stat-card').forEach(card => {
                            const statId = card.dataset.stat;
                            if (data[statId]) {
                                const valueElement = card.querySelector('.stat-value');
                                if (valueElement) {
                                    valueElement.textContent = data[statId];
                                }
                            }
                        });
                    })
                    .catch(error => console.error('Error updating stats:', error));
            }
        }, 60000);
    }
    
    // Print functionality
    const printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });
    
    // Copy to clipboard
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy || this.previousElementSibling?.textContent;
            
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success tooltip
                    const tooltip = new bootstrap.Tooltip(this, {
                        title: 'Скопировано!',
                        trigger: 'manual'
                    });
                    
                    tooltip.show();
                    
                    setTimeout(() => {
                        tooltip.hide();
                    }, 1000);
                });
            }
        });
    });
    
    // Initialize tooltips
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(el => {
        new bootstrap.Tooltip(el);
    });
    
    // Initialize popovers
    const popoverElements = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverElements.forEach(el => {
        new bootstrap.Popover(el);
    });
});

// Utility functions
const App = {
    // Format date
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    },
    
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 2
        }).format(amount);
    },
    
    // Format number
    formatNumber(number, decimals = 2) {
        return new Intl.NumberFormat('ru-RU', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },
    
    // Calculate days between dates
    daysBetween(date1, date2) {
        const diffTime = Math.abs(new Date(date2) - new Date(date1));
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    },
    
    // Validate email
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validate phone
    validatePhone(phone) {
        const re = /^\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$/;
        return re.test(phone);
    },
    
    // Show loading indicator
    showLoading(selector = 'body') {
        const element = document.querySelector(selector);
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = '<div class="spinner-border text-primary"></div>';
        element.appendChild(loader);
    },
    
    // Hide loading indicator
    hideLoading(selector = 'body') {
        const loader = document.querySelector(`${selector} .loading-overlay`);
        if (loader) {
            loader.remove();
        }
    },
    
    // Show toast notification
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || (() => {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            return container;
        })();
        
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
};

// Make App available globally
window.App = App;

// Chart.js defaults
Chart.defaults.font.family = "'Roboto', sans-serif";
Chart.defaults.color = '#666';
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
Chart.defaults.plugins.tooltip.borderRadius = 8;
Chart.defaults.plugins.tooltip.padding = 10;

// Initialize charts if needed
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        // You can add chart initialization logic here
        console.log('Chart.js is ready');
    }
});