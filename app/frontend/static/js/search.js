document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');

    if (!searchInput || !resultsContainer) return;

    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            resultsContainer.classList.remove('active');
            resultsContainer.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchResults(query);
        }, 300);
    });

    async function fetchResults(query) {
        try {
            const response = await fetch(`/books/api/search?q=${encodeURIComponent(query)}`);
            const books = await response.json();
            
            if (books.length > 0) {
                renderResults(books);
            } else {
                resultsContainer.innerHTML = '<div style="padding: 15px; color: var(--text-muted); text-align: center;">Нічого не знайдено</div>';
                resultsContainer.classList.add('active');
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    function renderResults(books) {
        resultsContainer.innerHTML = books.map(book => `
            <a href="${book.url}" class="search-item">
                <img src="${book.cover}" alt="${book.title}">
                <div>
                    <div style="font-weight: 600; font-size: 0.95rem;">${book.title}</div>
                    <div style="color: var(--text-muted); font-size: 0.85rem;">${book.author}</div>
                </div>
            </a>
        `).join('');
        
        resultsContainer.classList.add('active');
    }

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.classList.remove('active');
        }
    });
});