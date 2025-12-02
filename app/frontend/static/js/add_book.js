document.addEventListener('DOMContentLoaded', () => {
    window.updateFileName = function(input, targetId) {
        const fileName = input.files[0]?.name;
        const target = document.getElementById(targetId);
        if (fileName) {
            target.innerHTML = `<span style="color: #B58A59; font-weight: 500;">${fileName}</span>`;
            target.parentElement.style.borderColor = '#B58A59';
        }
    }
});