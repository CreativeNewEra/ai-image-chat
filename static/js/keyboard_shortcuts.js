/**
 * Keyboard Shortcuts Module
 *
 * Provides keyboard shortcuts for AI Image Chat application.
 *
 * IMPORTANT FIX: Uses e.stopPropagation() instead of e.preventDefault()
 * ----------------------------------------------------------------------
 * The previous implementation used e.preventDefault() which blocked ALL
 * default browser behavior, including button clicks. This caused issues
 * where buttons would not respond when clicked.
 *
 * The fix: Use e.stopPropagation() to prevent event bubbling while still
 * allowing the default action to occur. This way:
 * - Keyboard shortcuts still work
 * - Button clicks are not blocked
 * - Form inputs function normally
 * - Text selection and other browser features work
 *
 * See TROUBLESHOOTING.md Issue #1 for full details.
 */

/**
 * Helper function to find button by text content
 * @param {string} text - Text to search for in button
 * @returns {HTMLElement|undefined} Button element or undefined
 */
function findButtonByText(text) {
    const buttons = Array.from(document.querySelectorAll('button'));
    return buttons.find(btn => btn.textContent.includes(text));
}

/**
 * Setup keyboard shortcuts for the application
 *
 * Shortcuts:
 * - Alt+I: Switch to Idle mode
 * - Alt+C: Switch to Text Chat mode
 * - Alt+V: Switch to Vision Chat mode
 * - Alt+G: Switch to Generate mode
 * - Ctrl+Enter: Send chat message (when in textarea)
 * - Ctrl+G: Generate image
 * - Ctrl+K: Copy prompt
 * - Ctrl+L: Use last seed
 * - Ctrl+1-4: Quick presets
 * - Ctrl+Shift+C: Clear chat
 * - ?: Show help
 */
export function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Don't trigger shortcuts if user is typing in an input/textarea
        // EXCEPT for Ctrl+Enter which should submit
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            // Allow Ctrl+Enter in textareas to submit
            if (e.ctrlKey && e.key === 'Enter') {
                // USE stopPropagation() NOT preventDefault()
                // This allows the Enter key to work but stops event bubbling
                e.stopPropagation();
                const sendBtn = findButtonByText('Send');
                if (sendBtn) {
                    sendBtn.click();
                }
                return;
            }
            // Don't process other shortcuts when typing
            return;
        }

        // Mode switching (Alt+key)
        if (e.altKey && !e.ctrlKey && !e.shiftKey) {
            let btn = null;
            switch(e.key.toLowerCase()) {
                case 'i':
                    // USE stopPropagation() to prevent event bubbling
                    e.stopPropagation();
                    btn = findButtonByText('🔵 Idle');
                    break;
                case 'c':
                    e.stopPropagation();
                    btn = findButtonByText('💬 Text Chat');
                    break;
                case 'v':
                    e.stopPropagation();
                    btn = findButtonByText('👁️ Vision Chat');
                    break;
                case 'g':
                    e.stopPropagation();
                    btn = findButtonByText('🎨 Generate');
                    break;
            }
            if (btn) btn.click();
        }

        // Actions (Ctrl+key)
        if (e.ctrlKey && !e.altKey && !e.shiftKey) {
            let btn = null;
            switch(e.key.toLowerCase()) {
                case 'g':
                    e.stopPropagation();
                    btn = findButtonByText('🎨 Generate Image');
                    break;
                case 'k':
                    e.stopPropagation();
                    btn = findButtonByText('📋 Copy Prompt');
                    break;
                case 'l':
                    e.stopPropagation();
                    btn = findButtonByText('🔄 Use Last');
                    break;
                case '1':
                    e.stopPropagation();
                    btn = findButtonByText('⚡ Fast Draft');
                    break;
                case '2':
                    e.stopPropagation();
                    btn = findButtonByText('⚖️ Balanced');
                    break;
                case '3':
                    e.stopPropagation();
                    btn = findButtonByText('✨ High Quality');
                    break;
                case '4':
                    e.stopPropagation();
                    btn = findButtonByText('🔥 Ultra Detail');
                    break;
            }
            if (btn) btn.click();
        }

        // Clear chat (Ctrl+Shift+C)
        if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'c') {
            e.stopPropagation();
            const btn = findButtonByText('🗑️ Clear Chat');
            if (btn) btn.click();
        }

        // Show help (? or Shift+/)
        if (e.key === '?' || (e.shiftKey && e.key === '/')) {
            e.stopPropagation();
            const btn = findButtonByText('⌨️ Shortcuts');
            if (btn) btn.click();
        }
    });
}
