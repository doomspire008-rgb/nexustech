function getKeranjang() {
    return JSON.parse(localStorage.getItem('keranjang') || '[]');
}

function saveKeranjang(data) {
    localStorage.setItem('keranjang', JSON.stringify(data));
    if (typeof refreshCartBadge === 'function') {
        refreshCartBadge();
    }
}

function formatRupiah(angka) {
    return 'Rp ' + parseInt(angka).toLocaleString('id-ID');
}

function hapusItem(id) {
    let keranjang = getKeranjang().filter(i => i.id !== id);
    saveKeranjang(keranjang);
    renderKeranjang();
}

function ubahQty(id, delta) {
    let keranjang = getKeranjang();
    const idx = keranjang.findIndex(i => i.id === id);
    if (idx >= 0) {
        keranjang[idx].qty += delta;
        if (keranjang[idx].qty <= 0) keranjang.splice(idx, 1);
    }
    saveKeranjang(keranjang);
    renderKeranjang();
}

function buildPesanWA(keranjang) {
    let lines = ['Halo NexusTech, saya ingin memesan laptop:', ''];
    keranjang.forEach((item, index) => {
        lines.push(`${index + 1}. *${item.nama}* (${item.qty}x = ${formatRupiah(item.harga * item.qty)})`);
    });
    const total = keranjang.reduce((s, i) => s + i.harga * i.qty, 0);
    lines.push('');
    lines.push(`*Total Belanja:* ${formatRupiah(total)}`);
    lines.push('Mohon info ketersediaan stok & pengiriman. Terima kasih!');

    const pesanEncoded = encodeURIComponent(lines.join('\n'));
    return `https://wa.me/6281299779053?text=${pesanEncoded}`;
}

function renderKeranjang() {
    const keranjang = getKeranjang();
    const app = document.getElementById('keranjang-app');

    if (keranjang.length === 0) {
        app.innerHTML = `
        <div class="empty-cart">
            <div class="empty-icon"><i class="bi bi-bag-x"></i></div>
            <div class="empty-title">Keranjang Belanja Masih Kosong</div>
            <div class="empty-desc">Anda belum menambahkan produk laptop pilihan ke dalam keranjang.</div>
            <a href="/produk/" class="btn-primary-tech" style="display:inline-flex;">
                <i class="bi bi-grid"></i> Jelajahi Produk Sekarang
            </a>
        </div>`;
        return;
    }

    const total = keranjang.reduce((s, i) => s + i.harga * i.qty, 0);
    const totalItem = keranjang.reduce((s, i) => s + i.qty, 0);

    const itemsHTML = keranjang.map(item => `
        <div class="item-card">
            <div class="item-img">
                ${item.gambar
                    ? `<img src="${item.gambar}" alt="${item.nama}" onerror="this.parentElement.innerHTML='<i class=\\'bi bi-laptop placeholder-mini\\'></i>'">`
                    : `<i class="bi bi-laptop placeholder-mini"></i>`
                }
            </div>
            <div class="item-info">
                <div class="item-brand">${item.merek}</div>
                <div class="item-name">${item.nama}</div>
                <div class="item-sku">SKU: ${item.sku || '-'}</div>
                <div class="item-price">${formatRupiah(item.harga * item.qty)}</div>
            </div>
            <div class="item-actions">
                <div class="qty-control">
                    <button class="qty-btn" onclick="ubahQty(${item.id}, -1)" aria-label="Kurangi">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span class="qty-num">${item.qty}</span>
                    <button class="qty-btn" onclick="ubahQty(${item.id}, 1)" aria-label="Tambah">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>
                <button class="btn-hapus" onclick="hapusItem(${item.id})">
                    <i class="bi bi-trash3"></i> Hapus
                </button>
            </div>
        </div>
    `).join('');

    app.innerHTML = `
    <div class="keranjang-content">
        <div>
            <div class="item-list">${itemsHTML}</div>
        </div>
        <div>
            <div class="ringkasan">
                <div class="ringkasan-title">
                    <i class="bi bi-receipt" style="color:var(--accent);"></i> Ringkasan Belanja
                </div>
                <div class="ringkasan-row">
                    <span class="ringkasan-label">Total Kuantitas</span>
                    <span class="ringkasan-val">${totalItem} unit</span>
                </div>
                <div class="ringkasan-row">
                    <span class="ringkasan-label">Subtotal Produk</span>
                    <span class="ringkasan-val">${formatRupiah(total)}</span>
                </div>
                <div class="ringkasan-row">
                    <span class="ringkasan-label">Estimasi Pengiriman</span>
                    <span class="ringkasan-val" style="color:var(--accent); font-size:12px;">Konfirmasi via WA</span>
                </div>
                <div class="ringkasan-total">
                    <span class="ringkasan-total-label">Total Estimasi</span>
                    <span class="ringkasan-total-val">${formatRupiah(total)}</span>
                </div>
                <a href="${buildPesanWA(keranjang)}" target="_blank" class="btn-wa-checkout">
                    <i class="bi bi-whatsapp"></i> Pesan via WhatsApp
                </a>
                <a href="/produk/" class="btn-lanjut">
                    <i class="bi bi-arrow-left"></i> Lanjut Belanja
                </a>
                <div class="note">
                    <i class="bi bi-shield-check" style="color:#10b981;"></i> Transaksi langsung dan aman dipandu oleh tim admin NexusTech.
                </div>
            </div>
        </div>
    </div>`;
}

renderKeranjang();
