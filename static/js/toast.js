/**
 * Toast Notification System
 *
 * Provides non-intrusive toast notifications for user feedback.
 * Supports multiple types: info, success, warning, error.
 */

/**
 * Create the toast container if it doesn't exist
 * @returns {HTMLElement} The toast container element
 */
function createToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';

        // Add styles for toast container
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;

        document.body.appendChild(container);
    }
    return container;
}

/**
 * Show a toast notification
 *
 * @param {string} message - The message to display (can include HTML)
 * @param {string} type - Type of toast: 'info', 'success', 'warning', or 'error'
 * @param {number} duration - How long to show the toast in milliseconds (0 = no auto-dismiss)
 * @param {Object} options - Additional options
 * @param {string} options.title - Optional title for the toast
 * @param {boolean} options.showProgress - Show progress bar (default: true if duration > 0)
 * @param {boolean} options.showClose - Show close button (default: true)
 *
 * @example
 * showToast('Image generated successfully!', 'success');
 * showToast('Failed to connect to ComfyUI', 'error', 5000);
 * showToast('Processing image...', 'info', 0, { showClose: true });
 * showToast('Workflow loaded', 'success', 3000, { title: 'Success!' });
 */
export function showToast(message, type = 'info', duration = 3000, options = {}) {
    const {
        title = null,
        showProgress = duration > 0,
        showClose = true
    } = options;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Icon mapping
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    const icon = icons[type] || icons.info;

    // Build toast HTML
    const titleHtml = title ? `<div class="toast-title">${title}</div>` : '';
    const closeButton = showClose ? '<button class="toast-close" aria-label="Close">×</button>' : '';
    const progressBar = showProgress ? '<div class="toast-progress"></div>' : '';

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <div class="toast-content">
            ${titleHtml}
            <div class="toast-message">${message}</div>
        </div>
        ${closeButton}
        ${progressBar}
    `;

    // Add to container
    const container = createToastContainer();
    container.appendChild(toast);

    // Trigger slide-in animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Setup progress bar animation
    if (showProgress && duration > 0) {
        const progressEl = toast.querySelector('.toast-progress');
        if (progressEl) {
            progressEl.style.width = '100%';
            progressEl.style.transition = `width ${duration}ms linear`;
            setTimeout(() => {
                progressEl.style.width = '0%';
            }, 10);
        }
    }

    // Function to remove toast
    const removeToast = () => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    };

    // Auto remove after duration
    if (duration > 0) {
        setTimeout(removeToast, duration);
    }

    // Close button handler
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            removeToast();
        });
    }

    // Optional: Click toast to dismiss (except close button)
    toast.addEventListener('click', (e) => {
        if (!e.target.classList.contains('toast-close')) {
            removeToast();
        }
    });

    return toast;
}
