function showCompareToast(pesan) {
    const toast = document.getElementById('toastCompare');
    const msg = document.getElementById('toastCompareMsg');
    if (!toast || !msg) return;
    msg.textContent = pesan;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
}

function getCompareIds() {
    const urlParams = new URLSearchParams(window.location.search);
    const raw = urlParams.get('ids');
    if (raw) {
        return raw.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    }
    const stored = JSON.parse(localStorage.getItem('compare') || '[]');
    return stored.map(i => i.id);
}

function setCompareUrlAndStorage(ids) {
    let stored = JSON.parse(localStorage.getItem('compare') || '[]');
    stored = stored.filter(i => ids.includes(i.id));
    localStorage.setItem('compare', JSON.stringify(stored));

    if (ids.length > 0) {
        window.location.href = '/bandingkan/?ids=' + ids.join(',');
    } else {
        window.location.href = '/bandingkan/';
    }
}

function tambahDariSelect() {
    const select = document.getElementById('pilihProdukSelect');
    const val = parseInt(select.value);
    if (!val) {
        showCompareToast('Silakan pilih laptop terlebih dahulu');
        return;
    }
    const currentIds = getCompareIds();
    if (currentIds.includes(val)) {
        showCompareToast('Produk sudah ada dalam perbandingan');
        return;
    }
    if (currentIds.length >= 4) {
        showCompareToast('Maksimal 4 produk untuk dibandingkan');
        return;
    }
    currentIds.push(val);
    setCompareUrlAndStorage(currentIds);
}

function pilihCepat(id) {
    const currentIds = getCompareIds();
    if (!currentIds.includes(id)) {
        currentIds.push(id);
    }
    setCompareUrlAndStorage(currentIds);
}

function hapusProduk(id) {
    const currentIds = getCompareIds().filter(i => i !== id);
    setCompareUrlAndStorage(currentIds);
}

function kosongkanSemua() {
    localStorage.removeItem('compare');
    window.location.href = '/bandingkan/';
}

function tambahKeKeranjang(id, nama, merek, harga, gambar, sku) {
    let keranjang = JSON.parse(localStorage.getItem('keranjang') || '[]');
    const idx = keranjang.findIndex(i => i.id === id);
    if (idx >= 0) {
        keranjang[idx].qty += 1;
    } else {
        keranjang.push({ id, nama, merek, harga, gambar, sku, qty: 1 });
    }
    localStorage.setItem('keranjang', JSON.stringify(keranjang));
    if (typeof refreshCartBadge === 'function') refreshCartBadge();
    showCompareToast(nama + ' berhasil ditambahkan ke keranjang!');
}

// Auto-sync query params jika membuka /bandingkan/ tanpa param tapi ada localStorage
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.get('ids')) {
        const stored = JSON.parse(localStorage.getItem('compare') || '[]');
        if (stored.length > 0) {
            const ids = stored.map(i => i.id).join(',');
            window.location.replace('/bandingkan/?ids=' + ids);
        }
    }
});
