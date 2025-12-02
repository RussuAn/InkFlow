document.addEventListener('DOMContentLoaded', () => {
    const paymentForm = document.getElementById('payment-form');
    const amountOptions = document.querySelectorAll('.amount-option input[type="radio"]');
    const summaryDiv = document.querySelector('.payment-summary');

    const priceMap = {
        50: { coins: 50, price: 50, label: "50 грн" },
        100: { coins: 100, price: 95, label: "95 грн" },
        250: { coins: 250, price: 225, label: "225 грн" },
        500: { coins: 500, price: 425, label: "425 грн" }
    };

    function updateSummary() {
        let selectedAmount = document.querySelector('.amount-option input:checked').value;
        let data = priceMap[selectedAmount];

        summaryDiv.innerHTML = `
            <div class="summary-row">
                <span style="color: var(--text-muted);">Монети</span>
                <span style="font-weight: 600;">${data.coins} 🪙</span>
            </div>
            <div class="summary-total">
                <span style="color: var(--text-muted);">До сплати</span>
                <span class="summary-price">
                    ${data.price} грн
                </span>
            </div>
        `;
    }

    amountOptions.forEach(radio => {
        radio.addEventListener('change', updateSummary);
    });

    updateSummary();
});