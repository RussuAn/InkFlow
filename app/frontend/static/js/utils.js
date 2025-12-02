document.addEventListener('DOMContentLoaded', () => {
    initNavbarScroll(); 
    initUserMenu(); 

    initTabs();
    initPasswordToggle();

});


function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    const handleScroll = () => {
        if (window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };
    
    window.addEventListener('scroll', handleScroll);
    handleScroll();
}


function initUserMenu() {
    const trigger = document.getElementById('user-menu-btn'); 
    const dropdown = document.getElementById('user-dropdown'); 

    if (trigger && dropdown) {
        const toggleMenu = (forceClose = false) => {
            const isOpen = dropdown.classList.contains('active');
            if (forceClose || isOpen) {
                dropdown.classList.remove('active'); 
            } else {
                dropdown.classList.add('active');
            }
        };

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMenu();
        });

        document.addEventListener('click', (e) => {
            if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
                toggleMenu(true);
            }
        });
    }
}


function initTabs() {
    const triggers = document.querySelectorAll('.tab-trigger');
    
    triggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const container = trigger.closest('.tabs-container');
            if (!container) return;

            const targetValue = trigger.dataset.value;

            container.querySelectorAll('.tab-trigger').forEach(t => {
                t.removeAttribute('data-state');
            });
            trigger.setAttribute('data-state', 'active');

            container.querySelectorAll('.tab-content').forEach(content => {
                if (content.dataset.value === targetValue) {
                    content.setAttribute('data-state', 'active');
                    content.style.display = 'block';
                } else {
                    content.removeAttribute('data-state');
                    content.style.display = 'none';
                }
            });
        });
    });
}


function initPasswordToggle() {
    window.togglePassword = function(inputId, btn) {
        const input = document.getElementById(inputId);
        if (!input) return;
        
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        btn.innerHTML = isPassword 
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path><path d="M6.61 6.61A13.56 13.56 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.37-1.39"></path><line x1="2" y1="2" x2="22" y2="22"></line></svg>'
            : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-50"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>';

    };
}


window.updateFileName = function(input, textId) {
    const textEl = document.getElementById(textId);
    if (input.files && input.files.length > 0) {
        textEl.textContent = input.files[0].name;
        textEl.style.color = "var(--accent)";
        textEl.style.fontWeight = "600";
    }
};


window.showToast = function(message, type = 'info') {
    let container = document.getElementById('flash-messages-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'flash-messages-container';
        container.className = 'flash-messages-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    let iconHTML = '';
    let category = type; 

    if (type === 'success') { 
        iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #10B981;"><polyline points="20 6 9 17 4 12"></polyline></svg>'; 
    } else if (type === 'error') { 
        iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #DC2626;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'; 
    } else {
         iconHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent);"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'; 
         category = 'info';
    }

    toast.className = `flash-message flash-${category}`;
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';

    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            ${iconHTML}
            <span style="flex: 1;">${message}</span>
        </div>
        <button class="flash-message-close" onclick="this.closest('.flash-message').remove()">
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted);"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
        </button>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
};