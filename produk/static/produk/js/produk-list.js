function applySort(sortVal) {
    const url = new URL(window.location);
    url.searchParams.set('sort', sortVal);
    window.location.href = url.toString();
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

    if (typeof refreshCartBadge === 'function') {
        refreshCartBadge();
    }

    showToast(nama + ' berhasil ditambahkan ke keranjang!');
}

function showToast(pesan) {
    const toast = document.getElementById('toastNotif');
    const msg = document.getElementById('toastMsg');
    if (!toast || !msg) return;

    msg.textContent = pesan;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
}
