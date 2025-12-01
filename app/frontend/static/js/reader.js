// InkFlow/app/frontend/static/js/reader.js

pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

const config = window.readerConfig;
const container = document.getElementById('viewer-container');
const pageNumInput = document.getElementById('page-num-input');
const pageCountSpan = document.getElementById('page-count');
const zoomDisplay = document.getElementById('zoom-display');

let pdfDoc = null,
    scale = 1.5,
    isProgrammaticScroll = false;

let saveTimeout = null;

// --- ЗБЕРЕЖЕННЯ ПРОГРЕСУ (На сервер) ---
function saveProgress(page) {
    if (!pdfDoc || page < 1 || page > pdfDoc.numPages) return;

    console.log(`Saving progress: Page ${page}`);

    fetch(config.saveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: config.bookId,
            page: page,
            total_pages: pdfDoc.numPages
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.completed) console.log("Book finished!");
    })
    .catch(err => console.error(err));
}

// --- ІНІЦІАЛІЗАЦІЯ ---
async function initReader() {
    if (!pdfDoc) return;

    container.innerHTML = '';
    if (zoomDisplay) zoomDisplay.textContent = `${Math.round(scale * 100)}%`;
    if (pageCountSpan) pageCountSpan.textContent = pdfDoc.numPages;

    // 1. Отримуємо розміри першої сторінки для скелета
    const firstPage = await pdfDoc.getPage(1);
    const viewport = firstPage.getViewport({ scale: scale });
    const pageWidth = Math.floor(viewport.width);
    const pageHeight = Math.floor(viewport.height);

    // 2. Створюємо всі контейнери
    for (let num = 1; num <= pdfDoc.numPages; num++) {
        const wrapper = document.createElement("div");
        wrapper.className = "page-wrapper";
        wrapper.id = `page-wrapper-${num}`;
        wrapper.setAttribute('data-page-number', num);
        
        // Встановлюємо точні розміри
        wrapper.style.width = `${pageWidth}px`;
        wrapper.style.height = `${pageHeight}px`;
        
        const canvas = document.createElement("canvas");
        canvas.id = `page-${num}`;
        canvas.className = 'book-page';
        
        wrapper.appendChild(canvas);
        container.appendChild(wrapper);
        
        // Спостерігаємо для рендерингу
        renderObserver.observe(wrapper);
    }

    // 3. Скролимо до стартової позиції
    if (config.startPage > 1) {
        requestAnimationFrame(() => {
            scrollToPage(config.startPage, false);
        });
    } else {
        // Якщо сторінка 1, оновлюємо інпут відразу
        if (pageNumInput) pageNumInput.value = 1;
    }
}

// --- РЕНДЕРИНГ ---
async function renderPage(num) {
    const canvas = document.getElementById(`page-${num}`);
    if (!canvas || canvas.getAttribute('data-rendered') === 'true') return;

    try {
        const page = await pdfDoc.getPage(num);
        const viewport = page.getViewport({ scale: scale });
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;

        canvas.width = Math.floor(viewport.width * dpr);
        canvas.height = Math.floor(viewport.height * dpr);
        
        // Стилі CSS мають точно співпадати з wrapper
        canvas.style.width = '100%';
        canvas.style.height = '100%';

        const transform = dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null;
        canvas.setAttribute('data-rendered', 'true');

        await page.render({
            canvasContext: ctx,
            viewport: viewport,
            transform: transform
        }).promise;

    } catch (err) {
        console.error(`Error rendering page ${num}:`, err);
    }
}

// --- ЛІНИВИЙ РЕНДЕРИНГ (Observer) ---
const renderObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const num = parseInt(entry.target.getAttribute('data-page-number'));
            renderPage(num);
        }
    });
}, { root: container, rootMargin: "1000px" }); // Рендеримо далеко наперед

// --- ВІДСТЕЖЕННЯ АКТИВНОЇ СТОРІНКИ (SCROLL) ---
container.addEventListener('scroll', () => {
    if (isProgrammaticScroll || !pdfDoc) return;

    // Знаходимо середину в'юпорта контейнера
    const containerRect = container.getBoundingClientRect();
    const containerCenter = containerRect.top + (containerRect.height / 2);
    
    // Знаходимо всі видимі елементи через document.elementFromPoint
    // Це набагато швидше, ніж перебирати всі сторінки
    // Беремо елемент по центру екрана
    const centerElement = document.elementFromPoint(
        containerRect.left + (containerRect.width / 2), 
        containerCenter
    );
    
    // Шукаємо найближчий батьківський .page-wrapper
    const wrapper = centerElement?.closest('.page-wrapper');
    
    if (wrapper) {
        const currentPage = parseInt(wrapper.getAttribute('data-page-number'));
        
        // МИТТЄВЕ ОНОВЛЕННЯ ІНПУТА
        if (pageNumInput && parseInt(pageNumInput.value) !== currentPage) {
            pageNumInput.value = currentPage;
            
            // Зберігаємо на сервер із затримкою (debounce)
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveProgress(currentPage);
            }, 500);
        }
    }
    
    // Перевірка на кінець книги (для надійності)
    if (container.scrollHeight - container.scrollTop <= container.clientHeight + 100) {
        if (parseInt(pageNumInput.value) !== pdfDoc.numPages) {
            pageNumInput.value = pdfDoc.numPages;
            saveProgress(pdfDoc.numPages);
        }
    }
});

// --- НАВІГАЦІЯ ---
function scrollToPage(num, save = true) {
    const target = document.getElementById(`page-wrapper-${num}`);
    if (target) {
        isProgrammaticScroll = true;
        
        // Відступ зверху
        const offset = target.offsetTop - 20;
        
        container.scrollTo({
            top: offset,
            behavior: 'auto' // Миттєво для точності
        });

        if (pageNumInput) pageNumInput.value = num;
        if (save) saveProgress(num);

        // Знімаємо прапорець
        setTimeout(() => { isProgrammaticScroll = false; }, 100);
    }
}

// --- КНОПКИ ---
document.getElementById('prev-btn')?.addEventListener('click', () => {
    let current = parseInt(pageNumInput.value) || 1;
    if (current > 1) scrollToPage(current - 1);
});

document.getElementById('next-btn')?.addEventListener('click', () => {
    let current = parseInt(pageNumInput.value) || 1;
    if (pdfDoc && current < pdfDoc.numPages) scrollToPage(current + 1);
});

document.getElementById('zoom-in-btn')?.addEventListener('click', () => {
    scale = Math.min(scale + 0.2, 3.0);
    initReader();
});

document.getElementById('zoom-out-btn')?.addEventListener('click', () => {
    scale = Math.max(scale - 0.2, 0.5);
    initReader();
});

pageNumInput?.addEventListener('change', (e) => {
    let val = parseInt(e.target.value);
    val = Math.max(1, Math.min(val, pdfDoc.numPages));
    scrollToPage(val);
});

document.addEventListener('keydown', (e) => {
    let current = parseInt(pageNumInput.value) || 1;
    if (e.key === 'ArrowLeft') {
        if (current > 1) scrollToPage(current - 1);
    } else if (e.key === 'ArrowRight') {
        if (current < pdfDoc.numPages) scrollToPage(current + 1);
    }
});

// --- ЗАПУСК ---
pdfjsLib.getDocument(config.url).promise.then(pdf => {
    pdfDoc = pdf;
    initReader();
}).catch(err => {
    console.error(err);
    container.innerHTML = `<div style="padding:2rem; color:red; text-align:center;">Error: ${err.message}</div>`;
});