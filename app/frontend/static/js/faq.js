function toggleFaq(button) {
    const answer = button.nextElementSibling;
    button.classList.toggle('active');
    answer.classList.toggle('show');
}