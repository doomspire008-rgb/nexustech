// Init AOS animations without layout flickering
AOS.init({
    duration: 600,
    once: true,
    offset: 40,
    easing: 'ease-out-cubic'
});

// Theme Toggle System
const savedTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
updateToggleBtn(savedTheme);

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateToggleBtn(next);
}

function updateToggleBtn(theme) {
    const icon = document.getElementById('themeIcon');
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'bi bi-sun-fill';
    } else {
        icon.className = 'bi bi-moon-stars-fill';
    }
}

// Mobile Menu Drawer
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const icon = document.getElementById('menuToggleIcon');
    if (!menu || !icon) return;
    const isOpen = menu.classList.toggle('open');
    icon.className = isOpen ? 'bi bi-x-lg' : 'bi bi-list';
}

// Global Cart Counter
function refreshCartBadge() {
    try {
        const keranjang = JSON.parse(localStorage.getItem('keranjang') || '[]');
        const totalCount = keranjang.reduce((sum, item) => sum + (item.qty || 1), 0);
        const badge = document.getElementById('cartCount');
        if (badge) badge.textContent = totalCount;
    } catch (e) {}
}
refreshCartBadge();

// Chatbot Script
const CB_STORAGE_KEY = 'nexustech_chat_history_v1';
const CB_MAX_STORED = 40;
const CB_GREETING = 'Halo! Saya asisten NexusTech. Ada yang bisa dibantu untuk mencari laptop yang sesuai dengan kebutuhan dan budget Anda?';

let cbMessages = [];
let cbLoading = false;

function cbSaveHistory() {
    try {
        localStorage.setItem(CB_STORAGE_KEY, JSON.stringify(cbMessages.slice(-CB_MAX_STORED)));
    } catch (e) {}
}

function cbLoadHistory() {
    try {
        const raw = localStorage.getItem(CB_STORAGE_KEY);
        if (!raw) return null;
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) && parsed.length ? parsed : null;
    } catch (e) {
        return null;
    }
}

function cbToggle() {
    document.getElementById('chatbot-panel').classList.toggle('open');
}

function cbEscapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function cbAddBubble(text, cls) {
    const body = document.getElementById('cb-body');
    const bubble = document.createElement('div');
    bubble.className = 'cb-bubble ' + cls;
    bubble.innerHTML = cbEscapeHtml(text);
    body.appendChild(bubble);
    body.scrollTop = body.scrollHeight;
    return bubble;
}

function cbAddProdukCards(produkList) {
    const body = document.getElementById('cb-body');
    produkList.forEach(p => {
        const a = document.createElement('a');
        a.href = p.url;
        a.className = 'cb-produk-card';
        a.innerHTML = `
            <img src="${cbEscapeHtml(p.gambar_url || '')}" onerror="this.style.visibility='hidden'" alt="">
            <div>
                <div class="cb-pnama">${cbEscapeHtml(p.nama)}</div>
                <div class="cb-pmerek">${cbEscapeHtml(p.merek)}</div>
                <div class="cb-pharga">${cbEscapeHtml(p.harga)}</div>
            </div>`;
        body.appendChild(a);
    });
    body.scrollTop = body.scrollHeight;
}

function cbRenderStoredMessage(msg) {
    cbAddBubble(msg.content, msg.role === 'user' ? 'user' : 'bot');
    if (msg.role === 'assistant' && msg.produk && msg.produk.length) {
        cbAddProdukCards(msg.produk);
    }
}

(function cbInit() {
    const body = document.getElementById('cb-body');
    const stored = cbLoadHistory();
    if (stored) {
        body.innerHTML = '';
        cbMessages = stored;
        cbMessages.forEach(cbRenderStoredMessage);
    } else {
        cbMessages = [{ role: 'assistant', content: CB_GREETING }];
        cbSaveHistory();
        cbAddBubble(CB_GREETING, 'bot');
    }
})();

document.getElementById('cb-reset').addEventListener('click', function () {
    if (!confirm('Hapus seluruh riwayat percakapan asisten?')) return;
    localStorage.removeItem(CB_STORAGE_KEY);
    document.getElementById('cb-body').innerHTML = '';
    cbMessages = [{ role: 'assistant', content: CB_GREETING }];
    cbAddBubble(CB_GREETING, 'bot');
    cbSaveHistory();
});

document.getElementById('cb-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    if (cbLoading) return;

    const input = document.getElementById('cb-input');
    const pesan = input.value.trim();
    if (!pesan) return;

    cbAddBubble(pesan, 'user');
    cbMessages.push({ role: 'user', content: pesan });
    cbSaveHistory();
    input.value = '';

    cbLoading = true;
    document.getElementById('cb-send').disabled = true;
    const typing = document.createElement('div');
    typing.className = 'cb-typing';
    typing.innerHTML = '<i class="bi bi-three-dots"></i> Asisten sedang mengetik...';
    document.getElementById('cb-body').appendChild(typing);
    document.getElementById('cb-body').scrollTop = document.getElementById('cb-body').scrollHeight;

    try {
        const csrfToken = document.querySelector('#cb-form [name=csrfmiddlewaretoken]').value;
        const historyToSend = cbMessages.map(m => ({ role: m.role, content: m.content }));
        const res = await fetch(document.getElementById('cb-form').dataset.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ message: pesan, history: historyToSend }),
        });
        const data = await res.json();
        typing.remove();

        if (data.error) {
            cbAddBubble(data.error, 'error');
        } else {
            cbAddBubble(data.reply, 'bot');
            const newMsg = { role: 'assistant', content: data.reply };
            if (data.produk && data.produk.length) {
                cbAddProdukCards(data.produk);
                newMsg.produk = data.produk;
            }
            cbMessages.push(newMsg);
            cbSaveHistory();
        }
    } catch (err) {
        typing.remove();
        cbAddBubble('Maaf, terjadi kendala saat menghubungi asisten AI. Silakan coba kembali.', 'error');
    } finally {
        cbLoading = false;
        document.getElementById('cb-send').disabled = false;
    }
});
