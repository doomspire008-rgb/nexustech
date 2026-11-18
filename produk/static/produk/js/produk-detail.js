const produkData = document.getElementById('produk-detail-data').dataset;
const produkItemData = {
    id: Number(produkData.id),
    nama: produkData.nama,
    merek: produkData.merek,
    harga: Number(produkData.harga),
    gambar: produkData.gambar,
    sku: produkData.sku
};

function showDetailToast(pesan) {
    const toast = document.getElementById('toastDetail');
    const msg = document.getElementById('toastDetailMsg');
    if (!toast || !msg) return;
    msg.textContent = pesan;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2800);
}

// KERANJANG
function tambahKeKeranjangDetail() {
    let keranjang = JSON.parse(localStorage.getItem('keranjang') || '[]');
    const idx = keranjang.findIndex(i => i.id === produkItemData.id);
    if (idx >= 0) {
        keranjang[idx].qty += 1;
    } else {
        keranjang.push({ ...produkItemData, qty: 1 });
    }
    localStorage.setItem('keranjang', JSON.stringify(keranjang));
    if (typeof refreshCartBadge === 'function') refreshCartBadge();
    showDetailToast(produkItemData.nama + ' berhasil ditambahkan ke keranjang!');
}

// WISHLIST
function toggleWishlistDetail() {
    let wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    const idx = wishlist.findIndex(i => i.id === produkItemData.id);
    const btn = document.getElementById('btnWishlistDetail');
    const text = document.getElementById('wishlistText');

    if (idx >= 0) {
        wishlist.splice(idx, 1);
        btn.classList.remove('active-wishlist');
        text.textContent = 'Simpan Wishlist';
        showDetailToast('Dihapus dari Wishlist');
    } else {
        wishlist.push(produkItemData);
        btn.classList.add('active-wishlist');
        text.textContent = 'Tersimpan di Wishlist';
        showDetailToast('Disimpan ke Wishlist!');
    }
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
}

// COMPARE
function toggleCompareDetail() {
    let compare = JSON.parse(localStorage.getItem('compare') || '[]');
    const idx = compare.findIndex(i => i.id === produkItemData.id);
    const btn = document.getElementById('btnCompareDetail');
    const text = document.getElementById('compareText');

    if (idx >= 0) {
        compare.splice(idx, 1);
        btn.classList.remove('active-compare');
        text.textContent = 'Bandingkan';
        showDetailToast('Dihapus dari perbandingan');
    } else {
        if (compare.length >= 4) {
            showDetailToast('Maksimal 4 produk untuk dibandingkan!');
            return;
        }
        compare.push(produkItemData);
        btn.classList.add('active-compare');
        text.textContent = 'Dalam Komparasi';
        showDetailToast('Ditambahkan ke komparasi!');
    }
    localStorage.setItem('compare', JSON.stringify(compare));
    renderCompareFloatingBar();
}

function renderCompareFloatingBar() {
    const compare = JSON.parse(localStorage.getItem('compare') || '[]');
    const bar = document.getElementById('compareFloatingBar');
    const container = document.getElementById('comparePillsContainer');
    const count = document.getElementById('compareCountNum');

    if (!bar || !container || !count) return;

    count.textContent = compare.length;
    if (compare.length > 0) {
        bar.classList.add('show');
        container.innerHTML = compare.map(p => `
            <div class="compare-pill-item">
                <span>${p.nama}</span>
                <span class="compare-pill-remove" onclick="hapusSatuCompare(${p.id})">✕</span>
            </div>
        `).join('');
    } else {
        bar.classList.remove('show');
    }
}

function hapusSatuCompare(id) {
    let compare = JSON.parse(localStorage.getItem('compare') || '[]');
    compare = compare.filter(i => i.id !== id);
    localStorage.setItem('compare', JSON.stringify(compare));
    renderCompareFloatingBar();
    if (id === produkItemData.id) {
        const btn = document.getElementById('btnCompareDetail');
        const text = document.getElementById('compareText');
        if (btn && text) {
            btn.classList.remove('active-compare');
            text.textContent = 'Bandingkan';
        }
    }
}

function resetKomparasi() {
    localStorage.removeItem('compare');
    renderCompareFloatingBar();
    const btn = document.getElementById('btnCompareDetail');
    const text = document.getElementById('compareText');
    if (btn && text) {
        btn.classList.remove('active-compare');
        text.textContent = 'Bandingkan';
    }
}

function keHalamanBandingkan() {
    let compare = JSON.parse(localStorage.getItem('compare') || '[]');
    if (compare.length < 2) {
        showDetailToast('Pilih minimal 2 laptop untuk dibandingkan!');
        return;
    }
    const ids = compare.map(i => i.id).join(',');
    window.location.href = '/bandingkan/?ids=' + ids;
}

// SHARE UTILS
function shareWA() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent('Cek laptop ' + produkData.nama + ' di NexusTech seharga ' + produkData.hargaDisplay + ': ');
    window.open('https://wa.me/?text=' + text + url, '_blank');
}

function shareCopy() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        showDetailToast('Tautan link berhasil disalin!');
    });
}

function shareIG() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        showDetailToast('Tautan disalin! Silakan tempel di Story Instagram Anda.');
    });
}

// LIGHTBOX MODAL
function bukaModalFoto(src) {
    const modal = document.getElementById('imageLightbox');
    const img = document.getElementById('lightboxImgTarget');
    if (modal && img) {
        img.src = src;
        modal.classList.add('active');
    }
}

function tutupModalFoto() {
    const modal = document.getElementById('imageLightbox');
    if (modal) modal.classList.remove('active');
}

// INITIAL CHECK ON LOAD
window.addEventListener('DOMContentLoaded', () => {
    let wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    if (wishlist.find(i => i.id === produkItemData.id)) {
        const btn = document.getElementById('btnWishlistDetail');
        const text = document.getElementById('wishlistText');
        if (btn && text) {
            btn.classList.add('active-wishlist');
            text.textContent = 'Tersimpan di Wishlist';
        }
    }

    let compare = JSON.parse(localStorage.getItem('compare') || '[]');
    if (compare.find(i => i.id === produkItemData.id)) {
        const btn = document.getElementById('btnCompareDetail');
        const text = document.getElementById('compareText');
        if (btn && text) {
            btn.classList.add('active-compare');
            text.textContent = 'Dalam Komparasi';
        }
    }
    renderCompareFloatingBar();
});
