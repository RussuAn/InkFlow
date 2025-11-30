pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

const config = window.readerConfig;
const container = document.getElementById('viewer-container');

let pdfDoc = null,
    scale = 1.0; 

let observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            let pageNum = parseInt(entry.target.getAttribute('data-page-number'));
            updateCurrentPageDisplay(pageNum);
            saveProgress(pageNum);
        }
    });
}, {
    root: container,
    threshold: 0.5 
});

async function renderAllPages() {
    container.innerHTML = '';
    for (let num = 1; num <= pdfDoc.numPages; num++) {

        const div = document.createElement("div");
        div.className = "page-wrapper";
        div.setAttribute("data-page-number", num);
        div.id = `page-${num}`; 
        
        const canvas = document.createElement("canvas");
        div.appendChild(canvas);
        container.appendChild(div);

        await renderPage(num, canvas);

        observer.observe(div);
    }

    if (config.startPage > 1) {
        setTimeout(() => {
            const startDiv = document.getElementById(`page-${config.startPage}`);
            if (startDiv) startDiv.scrollIntoView();
        }, 500); 
    }
}

async function renderPage(num, canvas) {
    const page = await pdfDoc.getPage(num);

    const dpr = window.devicePixelRatio || 1;

    const viewport = page.getViewport({scale: scale});

    const ctx = canvas.getContext('2d');

    canvas.width = Math.floor(viewport.width * dpr);
    canvas.height = Math.floor(viewport.height * dpr);

    canvas.style.width = Math.floor(viewport.width) + "px";
    canvas.style.height = Math.floor(viewport.height) + "px";

    const transform = dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null;

    const renderContext = {
        canvasContext: ctx,
        viewport: viewport,
        transform: transform
    };
    
    await page.render(renderContext).promise;
}

function updateCurrentPageDisplay(num) {
    document.getElementById('page_num').textContent = num;
}

function saveProgress(page) {
    fetch('/api/save_progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: config.bookId,
            page: page,
            total_pages: pdfDoc.numPages
        })
    }).catch(err => console.error('Error:', err));
}

document.getElementById('zoom_in').addEventListener('click', () => {
    scale += 0.2;
    let currentPage = document.getElementById('page_num').textContent;
    config.startPage = parseInt(currentPage); 
    renderAllPages();
});

document.getElementById('zoom_out').addEventListener('click', () => {
    if (scale > 0.4) {
        scale -= 0.2;
        let currentPage = document.getElementById('page_num').textContent;
        config.startPage = parseInt(currentPage);
        renderAllPages();
    }
});

document.getElementById('prev').addEventListener('click', () => {
    let current = parseInt(document.getElementById('page_num').textContent);
    if (current > 1) document.getElementById(`page-${current - 1}`).scrollIntoView({behavior: "smooth"});
});

document.getElementById('next').addEventListener('click', () => {
    let current = parseInt(document.getElementById('page_num').textContent);
    if (current < pdfDoc.numPages) document.getElementById(`page-${current + 1}`).scrollIntoView({behavior: "smooth"});
});

pdfjsLib.getDocument(config.url).promise.then(function(pdfDoc_) {
    pdfDoc = pdfDoc_;
    document.getElementById('page_count').textContent = pdfDoc.numPages;
    renderAllPages();
});