function updateBioCounter(textarea) {
    const counter = document.getElementById('bio-counter');
    const maxLength = 500;
    const currentLength = textarea.value.length;
    counter.textContent = `${currentLength} / ${maxLength} символів`;
    
    if (currentLength > maxLength) {
        counter.style.color = '#DC2626'; 
    } else {
        counter.style.color = 'var(--text-muted)';
    }
}


function previewAvatar(input) {
    let preview = document.getElementById('avatar-preview');
    const fileNameDisplay = document.getElementById('avatar-file-name');
    const wrapper = preview.parentNode;

    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (preview.tagName === 'DIV') {
                const img = document.createElement('img');
                img.id = 'avatar-preview';
                img.src = e.target.result;
                img.alt = 'Avatar Preview';
                img.style.cssText = 'width: 100%; height: 100%; object-fit: cover; display: block;';
                wrapper.replaceChild(img, preview);
                preview = img;
            } else {
                preview.src = e.target.result;
            }
        }
        
        reader.readAsDataURL(input.files[0]);
        fileNameDisplay.textContent = `Новий файл: ${input.files[0].name}`;
        fileNameDisplay.style.color = 'var(--text-main)';

    } else {
        fileNameDisplay.textContent = 'Виберіть новий файл';
        fileNameDisplay.style.color = 'var(--text-muted)';
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const bioTextarea = document.getElementById('bio');
    if (bioTextarea) {
            updateBioCounter(bioTextarea);
    }
});