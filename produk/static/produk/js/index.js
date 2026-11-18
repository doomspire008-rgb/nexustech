// Filter Produk Berdasarkan Kategori
function filterProduk(btn, kategori) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.product-card').forEach(card => {
        if (kategori === 'semua' || card.dataset.kategori === kategori) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Tambah ke Keranjang Belanja
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
