pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

const config = window.readerConfig;
const container = document.getElementById('viewer-container');
const pageNumInput = document.getElementById('page-num-input');
const pageCountSpan = document.getElementById('page-count');
const zoomDisplay = document.getElementById('zoom-display');

let pdfDoc = null,
    scale = 1.2,
    isProgrammaticScroll = false,
    saveTimeout = null,
    isBookFinished = false; // Прапорець, щоб не відправляти запит багато разів

// --- ЗБЕРЕЖЕННЯ ПРОГРЕСУ ---
function saveProgress(page) {
    if (!pdfDoc || page < 1 || page > pdfDoc.numPages) return;
    
    if (document.activeElement !== pageNumInput) {
        pageNumInput.value = page;
    }

    fetch(config.saveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: config.bookId,
            page: page,
            total_pages: pdfDoc.numPages
        })
    }).catch(err => console.error(err));
}

// --- АВТОМАТИЧНЕ ЗАВЕРШЕННЯ ---
function markAsCompleted() {
    if (isBookFinished) return; // Якщо вже позначено, виходимо
    
    isBookFinished = true; // Ставимо прапорець

    fetch(config.finishUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book_id: config.bookId })
    })
    .then(r => r.json())
    .then(data => {
        if(data.status === 'success') {
            // Використовуємо системний showToast з utils.js, якщо він доступний
            if (window.showToast) {
                window.showToast('Вітаємо! Книгу прочитано 🏆', 'success');
            } else {
                console.log('Книгу завершено!');
            }
        }
    })
    .catch(err => {
        console.error("Помилка завершення:", err);
        isBookFinished = false; // Скидаємо прапорець, якщо помилка, щоб спробувати знову
    });
}

// --- ІНІЦІАЛІЗАЦІЯ ---
async function initReader() {
    container.innerHTML = '';
    if(pageCountSpan) pageCountSpan.textContent = pdfDoc.numPages;
    if(zoomDisplay) zoomDisplay.textContent = `${Math.round(scale * 100)}%`;

    // Створюємо сторінки
    for (let num = 1; num <= pdfDoc.numPages; num++) {
        const wrapper = document.createElement("div");
        wrapper.className = "page-wrapper";
        wrapper.id = `page-wrapper-${num}`;
        wrapper.setAttribute('data-page-number', num);
        
        // Гнучкий контейнер
        wrapper.style.minHeight = "600px"; 
        wrapper.style.position = "relative";
        wrapper.style.marginBottom = "20px";
        wrapper.style.display = "flex";
        wrapper.style.justifyContent = "center";
        
        const canvas = document.createElement("canvas");
        canvas.id = `page-${num}`;
        canvas.className = 'book-page';
        
        wrapper.appendChild(canvas);
        container.appendChild(wrapper);
        
        renderObserver.observe(wrapper);
    }

    // МИ ПРИБРАЛИ КНОПКУ "ЗАВЕРШИТИ", ТЕПЕР ЦЕ ПРАЦЮЄ АВТОМАТИЧНО

    // Додаємо відступ знизу, щоб було зручно дочитати останню сторінку
    const spacer = document.createElement('div');
    spacer.style.height = "100px";
    container.appendChild(spacer);

    // Скрол до збереженої позиції
    if (config.startPage > 1) {
        await renderPage(config.startPage);
        setTimeout(() => {
            scrollToPage(config.startPage, false);
        }, 300);
    } else {
        renderPage(1);
    }
}

// --- РЕНДЕР СТОРІНКИ ---
async function renderPage(num) {
    const canvas = document.getElementById(`page-${num}`);
    if (!canvas || canvas.getAttribute('data-rendered')) return;

    try {
        const page = await pdfDoc.getPage(num);
        const viewport = page.getViewport({scale: scale});
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;

        canvas.width = Math.floor(viewport.width * dpr);
        canvas.height = Math.floor(viewport.height * dpr);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;

        const wrapper = document.getElementById(`page-wrapper-${num}`);
        if (wrapper) {
            wrapper.style.minHeight = "auto";
            wrapper.style.width = "100%";
        }

        const transform = dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null;
        
        canvas.setAttribute('data-rendered', 'true');
        await page.render({ canvasContext: ctx, viewport, transform }).promise;
    } catch (e) { console.error(e); }
}

const renderObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            renderPage(parseInt(entry.target.getAttribute('data-page-number')));
        }
    });
}, { root: container, rootMargin: "1000px" });

// --- ЛОГІКА СКРОЛУ ТА АВТО-ЗАВЕРШЕННЯ ---
container.addEventListener('scroll', () => {
    if (isProgrammaticScroll || !pdfDoc) return;

    const viewLine = container.scrollTop + 100; 
    const wrappers = document.getElementsByClassName('page-wrapper');
    let current = 1;

    for(let i=0; i<wrappers.length; i++) {
        const w = wrappers[i];
        if (w.offsetTop <= viewLine && (w.offsetTop + w.offsetHeight) > viewLine) {
            current = parseInt(w.getAttribute('data-page-number'));
            break;
        }
    }

    // Оновлення сторінки в UI
    if (parseInt(pageNumInput.value) !== current) {
        pageNumInput.value = current;
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => saveProgress(current), 1000);
    }

    // --- ПЕРЕВІРКА НА ЗАВЕРШЕННЯ ---
    // Якщо поточна сторінка остання - зараховуємо прочитання
    if (current === pdfDoc.numPages) {
        markAsCompleted();
    }
});

function scrollToPage(num, save = true) {
    const target = document.getElementById(`page-wrapper-${num}`);
    if (target) {
        isProgrammaticScroll = true;
        container.scrollTop = target.offsetTop - 10;
        
        if (pageNumInput) pageNumInput.value = num;
        if (save) saveProgress(num);
        
        // Якщо стрибаємо на останню сторінку програмно (наприклад, з історії), 
        // теж можна зарахувати, або закоментувати цей рядок, якщо хочете лише при скролі
        if (num === pdfDoc.numPages) markAsCompleted();

        setTimeout(() => { isProgrammaticScroll = false; }, 500);
    }
}

// --- КНОПКИ ---
document.getElementById('prev-btn').addEventListener('click', () => {
    let cur = parseInt(pageNumInput.value);
    if (cur > 1) scrollToPage(cur - 1);
});
document.getElementById('next-btn').addEventListener('click', () => {
    let cur = parseInt(pageNumInput.value);
    if (cur < pdfDoc.numPages) scrollToPage(cur + 1);
});
document.getElementById('zoom-in-btn').addEventListener('click', () => {
    scale = Math.min(scale + 0.2, 3.0);
    initReader();
});
document.getElementById('zoom-out-btn').addEventListener('click', () => {
    scale = Math.max(scale - 0.2, 0.5);
    initReader();
});
pageNumInput.addEventListener('change', (e) => {
    let val = Math.max(1, Math.min(parseInt(e.target.value), pdfDoc.numPages));
    scrollToPage(val);
});

// --- ЗАПУСК ---
pdfjsLib.getDocument(config.url).promise.then(pdf => {
    pdfDoc = pdf;
    initReader();
}).catch(err => {
    container.innerHTML = `<div style="padding:20px;color:red">Помилка завантаження: ${err.message}</div>`;
});