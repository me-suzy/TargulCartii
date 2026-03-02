// ══════════════════════════════════════════════════════════════
// Targul Cartii - Adauga 4 carti in cos
// Ruleaza acest script in Console (F12) pe https://www.targulcartii.ro/
// ══════════════════════════════════════════════════════════════

(async function() {
    const BOOK_URLS = [
  "https://www.targulcartii.ro/ioan-caramazan/cine-roman-junimea-2002-10644594",
  "https://www.targulcartii.ro/karl-sutterlin/retus-tehnica-1974-9976644",
  "https://www.targulcartii.ro/cristina-corciovescu/secolul-cinematografului?an=1989&editura=Stiintifica si Enciclopedica&coperta=Cartonata (hardcover)&pid=217536",
  "https://www.targulcartii.ro/karel-capek/cum-se-face-teatru-cum-se-face-film-meridiane-1971-10642731"
];

    const DELAY_MS = 1500; // pauza intre requesturi (ms)

    let added = 0;
    let failed = 0;
    let errors = [];

    // Status display
    let statusDiv = document.createElement('div');
    statusDiv.id = 'tc_bulk_status';
    statusDiv.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;' +
        'background:#1a1a2e;color:#e0e0e0;padding:15px 20px;font-family:monospace;' +
        'font-size:14px;box-shadow:0 2px 10px rgba(0,0,0,0.5);';
    statusDiv.innerHTML = '<div id="tc_progress">Se pregatesc cartile... 0/' + BOOK_URLS.length + '</div>' +
        '<div id="tc_bar" style="background:#333;height:6px;margin-top:8px;border-radius:3px;">' +
        '<div id="tc_fill" style="background:#e94560;height:100%;width:0%;border-radius:3px;' +
        'transition:width 0.3s;"></div></div>' +
        '<div id="tc_current" style="margin-top:5px;font-size:11px;color:#888;"></div>';
    document.body.prepend(statusDiv);

    function updateStatus(msg, current) {
        document.getElementById('tc_progress').textContent = msg;
        let pct = ((added + failed) / BOOK_URLS.length * 100).toFixed(1);
        document.getElementById('tc_fill').style.width = pct + '%';
        if (current) document.getElementById('tc_current').textContent = current;
    }

    function sleep(ms) {
        return new Promise(r => setTimeout(r, ms));
    }

    // Fetch a book page and extract the addToCart2 product_id
    async function getProductId(url) {
        let resp = await fetch(url);
        let html = await resp.text();
        let match = html.match(/addToCart2\('(\d+)','(\d+)','([^']+)'\)/);
        if (match) {
            return { product_id: match[1], condition: match[2], condition_key: match[3] };
        }
        return null;
    }

    // Add a product to cart via the API
    async function addProduct(productId) {
        let resp = await fetch('https://www.targulcartii.ro/index.php?route=checkout/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'product_id=' + productId + '&quantity=1'
        });
        let data = await resp.json();
        return data;
    }

    console.log('=== Targul Cartii Bulk Add: Start (' + BOOK_URLS.length + ' carti) ===');

    for (let i = 0; i < BOOK_URLS.length; i++) {
        let url = BOOK_URLS[i];
        let bookName = decodeURIComponent(url.split('/').pop().split('?')[0].replace(/-/g, ' '));

        updateStatus(
            'Adaugare in cos: ' + (i + 1) + '/' + BOOK_URLS.length +
            ' (OK: ' + added + ', Erori: ' + failed + ')',
            bookName
        );

        try {
            // Get product ID from book page
            let info = await getProductId(url);
            if (!info) {
                console.warn('[' + (i+1) + '] NU s-a gasit product_id: ' + url);
                failed++;
                errors.push({ url: url, error: 'No product_id found' });
                await sleep(DELAY_MS);
                continue;
            }

            // Add to cart
            let result = await addProduct(info.product_id);

            if (result && !result.error) {
                added++;
                console.log('[' + (i+1) + '] OK: ' + bookName + ' (pid=' + info.product_id + ')');
            } else {
                failed++;
                let errMsg = result ? (result.error || JSON.stringify(result)) : 'Unknown error';
                console.warn('[' + (i+1) + '] EROARE: ' + bookName + ' - ' + errMsg);
                errors.push({ url: url, product_id: info.product_id, error: errMsg });
            }
        } catch (e) {
            failed++;
            console.error('[' + (i+1) + '] EXCEPTIE: ' + url + ' - ' + e.message);
            errors.push({ url: url, error: e.message });
        }

        await sleep(DELAY_MS);
    }

    // Final report
    let summary = '\n=== FINALIZAT ===' +
        '\nTotal carti: ' + BOOK_URLS.length +
        '\nAdaugate cu succes: ' + added +
        '\nErori: ' + failed;

    if (errors.length > 0) {
        summary += '\n\nCarti cu erori:';
        errors.forEach(e => { summary += '\n  - ' + e.url + ' (' + e.error + ')'; });
    }

    console.log(summary);

    updateStatus(
        'GATA! Adaugate: ' + added + '/' + BOOK_URLS.length +
        (failed > 0 ? ' (Erori: ' + failed + ')' : ''),
        'Reincarca pagina (F5) pentru a vedea cosul actualizat.'
    );
    document.getElementById('tc_fill').style.background = failed > 0 ? '#e67e22' : '#2ecc71';
    document.getElementById('tc_fill').style.width = '100%';

    // Save errors to console for easy copy
    if (errors.length > 0) {
        console.log('\nURL-uri cu erori (copy-paste pentru reincercare):');
        console.log(JSON.stringify(errors, null, 2));
    }
})();
