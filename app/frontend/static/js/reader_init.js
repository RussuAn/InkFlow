document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('reader-theme-toggle');
    const body = document.body;
    const sun = btn.querySelector('.sun-icon');
    const moon = btn.querySelector('.moon-icon');
    
    const saved = localStorage.getItem('theme');
    if(saved) body.setAttribute('data-theme', saved);
    
    const updateIcons = () => {
        const isDark = body.getAttribute('data-theme') === 'dark';
        sun.style.display = isDark ? 'block' : 'none';
        moon.style.display = isDark ? 'none' : 'block';
    };
    updateIcons();

    btn.addEventListener('click', () => {
        const isDark = body.getAttribute('data-theme') === 'dark';
        if(isDark) {
            body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        } else {
            body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        }
        updateIcons();
    });
});