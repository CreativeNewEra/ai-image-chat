/**
 * AI Image Chat - Main JavaScript Entry Point
 *
 * This file initializes all JavaScript modules for the application.
 * It serves as the single entry point loaded by Gradio's gr.Blocks(js=...)
 *
 * Module Structure:
 * - toast.js: Toast notification system
 * - keyboard_shortcuts.js: Keyboard shortcuts (with stopPropagation fix)
 * - main.js: This file - initialization and global exports
 */

import { showToast } from './toast.js';
import { setupKeyboardShortcuts } from './keyboard_shortcuts.js';

/**
 * Initialize all modules when DOM is ready
 */
function initializeApp() {
    console.log('[AI Image Chat] Initializing JavaScript modules...');

    // Make showToast globally available for Gradio's JS callbacks
    // This allows inline .click(js="...") handlers to use showToast()
    window.showToast = showToast;
    console.log('[AI Image Chat] ✓ Toast system initialized');

    // Setup keyboard shortcuts with proper event handling
    setupKeyboardShortcuts();
    console.log('[AI Image Chat] ✓ Keyboard shortcuts initialized');

    console.log('[AI Image Chat] All modules loaded successfully!');
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // DOM already loaded, run immediately
    initializeApp();
}

// Export showToast for use in other modules if needed
export { showToast };
