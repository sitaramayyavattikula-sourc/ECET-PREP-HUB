/**
 * ECET-PREPHUB — Light Mode / Night Mode Controller
 * Handles client-side theme switching, localStorage persistence, and toggle UI states.
 */

(function () {
    'use strict';

    var STORAGE_KEY = 'ecet-prephub-theme';
    var THEME_LIGHT = 'light';
    var THEME_DARK = 'dark';

    // 1. Get stored theme or default to LIGHT mode
    function getSavedTheme() {
        try {
            var saved = localStorage.getItem(STORAGE_KEY);
            if (saved === THEME_DARK) {
                return THEME_DARK;
            }
            return THEME_LIGHT;
        } catch (e) {
            return THEME_LIGHT;
        }
    }

    // 2. Apply theme attribute to <html> element
    function applyTheme(theme) {
        var root = document.documentElement;
        if (theme === THEME_DARK) {
            root.setAttribute('data-theme', THEME_DARK);
        } else {
            root.setAttribute('data-theme', THEME_LIGHT);
        }

        // Update all toggle buttons on the page
        updateToggleButtons(theme);
    }

    // 3. Update all toggle button elements
    function updateToggleButtons(theme) {
        var buttons = document.querySelectorAll('.theme-toggle-btn');
        var isDark = (theme === THEME_DARK);

        buttons.forEach(function (btn) {
            btn.setAttribute('aria-checked', isDark ? 'true' : 'false');
            var nextThemeText = isDark ? 'Light' : 'Night';
            btn.setAttribute('aria-label', 'Switch to ' + nextThemeText + ' Mode');
            btn.setAttribute('title', 'Switch to ' + nextThemeText + ' Mode (Currently ' + (isDark ? 'Night' : 'Light') + ' Mode)');

            if (isDark) {
                btn.classList.add('is-dark');
                btn.classList.remove('is-light');
            } else {
                btn.classList.add('is-light');
                btn.classList.remove('is-dark');
            }
        });
    }

    // 4. Toggle function
    function toggleTheme() {
        var current = document.documentElement.getAttribute('data-theme') || THEME_LIGHT;
        var nextTheme = (current === THEME_DARK) ? THEME_LIGHT : THEME_DARK;

        try {
            localStorage.setItem(STORAGE_KEY, nextTheme);
        } catch (e) {
            console.warn('localStorage is not available for theme persistence:', e);
        }

        applyTheme(nextTheme);

        // Dispatch custom event for any listeners
        try {
            window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: nextTheme } }));
        } catch (e) {}
    }

    // 5. Expose toggle function globally
    window.toggleECETTheme = toggleTheme;

    // 6. Initialize on DOM ready
    function initThemeUI() {
        var currentTheme = getSavedTheme();
        applyTheme(currentTheme);

        // Bind click events to any .theme-toggle-btn
        document.addEventListener('click', function (e) {
            var toggleBtn = e.target.closest('.theme-toggle-btn');
            if (toggleBtn) {
                e.preventDefault();
                toggleTheme();
            }
        });

        // Keyboard accessibility: Enter and Space
        document.addEventListener('keydown', function (e) {
            var toggleBtn = e.target.closest('.theme-toggle-btn');
            if (toggleBtn && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                toggleTheme();
            }
        });
    }

    // 7. Sync across browser tabs
    window.addEventListener('storage', function (e) {
        if (e.key === STORAGE_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeUI);
    } else {
        initThemeUI();
    }
})();
