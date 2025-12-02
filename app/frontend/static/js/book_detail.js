document.addEventListener('DOMContentLoaded', () => {
    const descBox = document.getElementById('description-box');
    const toggleBtn = document.getElementById('description-toggle');
    
    if (descBox && toggleBtn) {
        if (descBox.scrollHeight <= 120) {
            toggleBtn.style.display = 'none';
            descBox.classList.remove('collapsed');
            descBox.style.maskImage = 'none';
        }

        toggleBtn.addEventListener('click', () => {
            if (descBox.classList.contains('collapsed')) {
                descBox.classList.remove('collapsed');
                descBox.classList.add('expanded');
                toggleBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>';
            } else {
                descBox.classList.remove('expanded');
                descBox.classList.add('collapsed');
                descBox.scrollTop = 0;
                toggleBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>';
            }
        });
    }

    const stars = document.querySelectorAll('.star-icon');
    const ratingInput = document.getElementById('rating-value');
    let currentRating = 5;
    
    function updateStars(value) {
        stars.forEach(star => {
            const starVal = parseInt(star.dataset.value);
            if (starVal <= value) { star.classList.add('filled'); } else { star.classList.remove('filled'); }
        });
    }
    
    if (stars.length > 0) {
        updateStars(currentRating);
        stars.forEach(star => {
            star.addEventListener('click', () => { currentRating = parseInt(star.dataset.value); ratingInput.value = currentRating; updateStars(currentRating); });
            star.addEventListener('mouseenter', () => { updateStars(parseInt(star.dataset.value)); });
            star.addEventListener('mouseleave', () => { updateStars(currentRating); });
        });
    }
});


const modal = document.getElementById('gift-modal');
function openGiftModal() { if(modal) modal.style.display = 'flex'; }
function closeGiftModal() { if(modal) modal.style.display = 'none'; }

if(modal) {
    modal.addEventListener('click', (e) => { if (e.target === modal) closeGiftModal(); });
}


window.openGiftModal = openGiftModal;
window.closeGiftModal = closeGiftModal;