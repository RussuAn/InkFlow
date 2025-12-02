document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    const body = document.body;

    const applyTheme = (theme) => {
        if (theme === 'dark') {
            body.setAttribute('data-theme', 'dark');
        } else {
            body.removeAttribute('data-theme');
        }
    };

    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        applyTheme(currentTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        applyTheme('dark');
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const isDark = body.hasAttribute('data-theme');
            const newTheme = isDark ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }

    const moonIcon = document.getElementById('moon-icon');
    const sunIcon = document.getElementById('sun-icon');
    const sunRays = document.getElementById('sun-rays');

    function updateThemeIcon() {
        const isDark = body.hasAttribute('data-theme');
        if (!moonIcon || !sunIcon) return; 

        if (isDark) {
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'block';
            sunRays.style.display = 'block';
        } else {
            moonIcon.style.display = 'block';
            sunIcon.style.display = 'none';
            sunRays.style.display = 'none';
        }
    }

    const observer = new MutationObserver(updateThemeIcon);
    observer.observe(body, { attributes: true, attributeFilter: ['data-theme'] });
    
    updateThemeIcon();
});