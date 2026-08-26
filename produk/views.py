from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .models import Produk, Kategori, Merek, Ulasan, Pesanan


def format_rupiah(value):
    try:
        value = int(value)
        formatted = f"{value:,}".replace(",", ".")
        return f"Rp {formatted}"
    except:
        return value


def beranda(request):
    produk_list = Produk.objects.filter(status='aktif').select_related('merek', 'kategori')[:6]
    merek_list = Merek.objects.all()
    for p in produk_list:
        p.harga_display = format_rupiah(p.harga)
    context = {
        'produk_list': produk_list,
        'merek_list': merek_list,
        'total_produk': Produk.objects.filter(status='aktif').count(),
        'total_merek': Merek.objects.count(),
    }
    return render(request, 'produk/index.html', context)


def produk_list(request):
    produk = Produk.objects.filter(status='aktif').select_related('merek', 'kategori')
    kategori_list = Kategori.objects.all()
    merek_list = Merek.objects.all()

    q = request.GET.get('q')
    if q:
        produk = produk.filter(nama__icontains=q)
    kategori = request.GET.get('kategori')
    if kategori:
        produk = produk.filter(kategori__slug=kategori)
    merek = request.GET.get('merek')
    if merek:
        produk = produk.filter(merek__id=merek)
    sort = request.GET.get('sort', 'terbaru')
    if sort == 'termurah':
        produk = produk.order_by('harga')
    elif sort == 'termahal':
        produk = produk.order_by('-harga')
    else:
        produk = produk.order_by('-created_at')

    for p in produk:
        p.harga_display = format_rupiah(p.harga)

    context = {
        'produk_list': produk,
        'kategori_list': kategori_list,
        'merek_list': merek_list,
    }
    return render(request, 'produk/produk_list.html', context)


def produk_detail(request, pk):
    produk = get_object_or_404(Produk, pk=pk, status='aktif')
    produk.harga_display = format_rupiah(produk.harga)
    if produk.harga_diskon:
        produk.harga_diskon_display = format_rupiah(produk.harga_diskon)

    produk_related = Produk.objects.filter(
        kategori=produk.kategori, status='aktif'
    ).exclude(pk=pk)[:3]
    for p in produk_related:
        p.harga_display = format_rupiah(p.harga)

    ulasan_list = Ulasan.objects.filter(produk=produk, disetujui=True)
    rating_rata = produk.rating_rata()
    jumlah_ulasan = produk.jumlah_ulasan()

    # Hitung distribusi rating
    distribusi = {}
    for i in range(5, 0, -1):
        jumlah = ulasan_list.filter(rating=i).count()
        persen = (jumlah / jumlah_ulasan * 100) if jumlah_ulasan > 0 else 0
        distribusi[i] = {'jumlah': jumlah, 'persen': round(persen)}

    context = {
        'produk': produk,
        'produk_related': produk_related,
        'ulasan_list': ulasan_list,
        'rating_rata': rating_rata,
        'jumlah_ulasan': jumlah_ulasan,
        'distribusi': distribusi,
    }
    return render(request, 'produk/produk_detail.html', context)


def tambah_ulasan(request, pk):
    produk = get_object_or_404(Produk, pk=pk, status='aktif')
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        email = request.POST.get('email', '').strip()
        rating = request.POST.get('rating')
        komentar = request.POST.get('komentar', '').strip()
        foto = request.FILES.get('foto')

        if not nama or not email or not rating or not komentar:
            messages.error(request, 'Semua field wajib diisi!')
            return redirect(f'/produk/{pk}/#ulasan')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except:
            messages.error(request, 'Rating tidak valid!')
            return redirect(f'/produk/{pk}/#ulasan')

        Ulasan.objects.create(
            produk=produk,
            nama_pengulas=nama,
            email_pengulas=email,
            rating=rating,
            komentar=komentar,
            foto=foto,
        )
        messages.success(request, 'Ulasan berhasil dikirim! Terima kasih.')
        return redirect(f'/produk/{pk}/#ulasan')

    return redirect(f'/produk/{pk}/')


def bandingkan(request):
    raw_ids = request.GET.get('ids', '').strip()
    id_list = []
    if raw_ids:
        for part in raw_ids.split(','):
            part = part.strip()
            if part.isdigit():
                id_list.append(int(part))

    # Batasi maksimal 4 produk untuk dibandingkan
    id_list = id_list[:4]

    produk_list = []
    if id_list:
        produk_dict = {
            p.id: p for p in Produk.objects.filter(id__in=id_list, status='aktif').select_related('merek', 'kategori')
        }
        for pid in id_list:
            if pid in produk_dict:
                p = produk_dict[pid]
                p.harga_display = format_rupiah(p.harga)
                if p.harga_diskon:
                    p.harga_diskon_display = format_rupiah(p.harga_diskon)
                p.rating = p.rating_rata()
                p.total_ulasan = p.jumlah_ulasan()
                produk_list.append(p)

    semua_produk = Produk.objects.filter(status='aktif').select_related('merek', 'kategori').order_by('nama')
    for p in semua_produk:
        p.harga_display = format_rupiah(p.harga)

    context = {
        'produk_list': produk_list,
        'semua_produk': semua_produk,
        'selected_ids': [p.id for p in produk_list],
    }
    return render(request, 'produk/bandingkan.html', context)


def keranjang(request):
    return render(request, 'produk/keranjang.html', {})


@staff_member_required
def admin_invoice_pdf(request, pk):
    """Generate invoice PDF untuk sebuah pesanan (dipakai dari halaman admin)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib.enums import TA_RIGHT

    pesanan = get_object_or_404(Pesanan, pk=pk)
    items = pesanan.item_set.select_related('produk', 'produk__merek').all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )

    ACCENT = colors.HexColor('#059669')
    DARK = colors.HexColor('#111827')
    MUTED = colors.HexColor('#6b7280')
    LIGHT_BG = colors.HexColor('#f3f4f6')

    styles = getSampleStyleSheet()
    style_brand = ParagraphStyle('brand', parent=styles['Normal'], fontSize=20, textColor=ACCENT, fontName='Helvetica-Bold')
    style_muted = ParagraphStyle('muted', parent=styles['Normal'], fontSize=9, textColor=MUTED, leading=13)
    style_h1 = ParagraphStyle('h1', parent=styles['Normal'], fontSize=22, textColor=DARK, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    style_label = ParagraphStyle('label', parent=styles['Normal'], fontSize=9, textColor=MUTED, fontName='Helvetica-Bold')
    style_value = ParagraphStyle('value', parent=styles['Normal'], fontSize=10, textColor=DARK, leading=14)

    elements = []

    # Header: brand + judul invoice
    header_data = [[
        Paragraph('NexusTech', style_brand),
        Paragraph('INVOICE', style_h1),
    ]]
    header_table = Table(header_data, colWidths=[100 * mm, 70 * mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(header_table)
    elements.append(Paragraph('Toko Laptop Online Terpercaya', style_muted))
    elements.append(Spacer(1, 14 * mm))

    # Info nomor invoice, tanggal, status & data pelanggan
    status_display = pesanan.get_status_display()
    info_data = [
        [Paragraph('NO. INVOICE', style_label), Paragraph('DITAGIHKAN KEPADA', style_label)],
        [Paragraph(pesanan.no_pesanan, style_value), Paragraph(pesanan.pelanggan.nama, style_value)],
        [Paragraph('TANGGAL', style_label), Paragraph(pesanan.pelanggan.email, style_value)],
        [Paragraph(pesanan.created_at.strftime('%d %B %Y'), style_value),
         Paragraph(pesanan.pelanggan.telpon or '-', style_value)],
        [Paragraph('STATUS', style_label), Paragraph(pesanan.pelanggan.alamat or '-', style_value)],
        [Paragraph(status_display, style_value), Paragraph('', style_value)],
    ]
    info_table = Table(info_data, colWidths=[80 * mm, 90 * mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12 * mm))

    # Tabel item pesanan
    def rp(val):
        return f"Rp {int(val):,}".replace(',', '.')

    table_head_style = ParagraphStyle('thead', parent=styles['Normal'], fontSize=9, textColor=colors.white, fontName='Helvetica-Bold')
    table_cell_style = ParagraphStyle('tcell', parent=styles['Normal'], fontSize=9.5, textColor=DARK, leading=13)
    table_cell_style_r = ParagraphStyle('tcellr', parent=styles['Normal'], fontSize=9.5, textColor=DARK, leading=13, alignment=TA_RIGHT)

    rows = [[
        Paragraph('PRODUK', table_head_style),
        Paragraph('MEREK', table_head_style),
        Paragraph('QTY', table_head_style),
        Paragraph('HARGA SATUAN', table_head_style),
        Paragraph('SUBTOTAL', table_head_style),
    ]]
    for item in items:
        rows.append([
            Paragraph(item.produk.nama, table_cell_style),
            Paragraph(item.produk.merek.nama, table_cell_style),
            Paragraph(str(item.qty), table_cell_style),
            Paragraph(rp(item.harga_satuan), table_cell_style_r),
            Paragraph(rp(item.subtotal), table_cell_style_r),
        ])

    item_table = Table(rows, colWidths=[55 * mm, 30 * mm, 15 * mm, 33 * mm, 37 * mm], repeatRows=1)
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 8 * mm))

    # Ringkasan total
    summary_data = [
        ['Subtotal', rp(pesanan.subtotal)],
        ['Ongkos Kirim', rp(pesanan.ongkir)],
        ['TOTAL', rp(pesanan.total)],
    ]
    summary_table = Table(summary_data, colWidths=[140 * mm, 30 * mm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 1), 10),
        ('TEXTCOLOR', (0, 0), (-1, 1), MUTED),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 13),
        ('TEXTCOLOR', (0, 2), (-1, 2), ACCENT),
        ('LINEABOVE', (0, 2), (-1, 2), 1, DARK),
        ('TOPPADDING', (0, 2), (-1, 2), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary_table)

    if pesanan.catatan:
        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph('CATATAN', style_label))
        elements.append(Paragraph(pesanan.catatan, style_value))

    elements.append(Spacer(1, 16 * mm))
    elements.append(Paragraph('Terima kasih telah berbelanja di NexusTech.', style_muted))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice-{pesanan.no_pesanan}.pdf"'
    return response

# ============================================================
# CHATBOT REKOMENDASI LAPTOP (pakai Google Gemini API)
# ============================================================

import json
import re
import urllib.request
import urllib.error
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse


CHATBOT_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{CHATBOT_MODEL}:generateContent"
)


def _build_katalog_context():
    """Ambil daftar produk aktif untuk dikasih ke Gemini sebagai konteks katalog."""
    produk_qs = Produk.objects.filter(status='aktif').select_related('merek', 'kategori')
    katalog = []
    for p in produk_qs:
        harga_final = p.harga_diskon if p.harga_diskon else p.harga
        deskripsi_singkat = (p.deskripsi or '').strip().replace('\n', ' ')
        if len(deskripsi_singkat) > 160:
            deskripsi_singkat = deskripsi_singkat[:160] + '...'
        katalog.append({
            'id': p.id,
            'nama': p.nama,
            'merek': p.merek.nama,
            'kategori': p.kategori.nama,
            'harga': int(harga_final),
            'deskripsi': deskripsi_singkat,
        })
    return katalog


def _build_system_prompt(katalog):
    katalog_text = json.dumps(katalog, ensure_ascii=False)
    return (
        "Kamu adalah asisten belanja di toko laptop online bernama NexusTech. "
        "Tugasmu membantu pembeli menemukan laptop yang paling cocok berdasarkan kebutuhan "
        "(misalnya: gaming, kerja/perkantoran, desain/editing, kuliah/pelajar) dan budget mereka. "
        "Jawab dengan ramah, singkat, dan jelas dalam Bahasa Indonesia. "
        "SANGAT PENTING: hanya rekomendasikan produk yang benar-benar ada di daftar katalog di bawah ini. "
        "Jangan pernah mengarang nama produk, merek, atau harga yang tidak ada di katalog. "
        "Jika informasi dari pembeli masih kurang (misalnya budget belum disebutkan), boleh tanya balik "
        "dulu sebelum merekomendasikan produk.\n\n"
        f"KATALOG PRODUK (format JSON):\n{katalog_text}\n\n"
        "ATURAN FORMAT JAWABAN (WAJIB DIIKUTI):\n"
        "Di akhir SETIAP jawabanmu, selalu tambahkan baris baru berisi blok kode seperti ini:\n"
        "```json\n"
        '{"produk_ids": [id_produk_yang_direkomendasikan]}\n'
        "```\n"
        "Isi produk_ids dengan id produk (field 'id' di katalog) yang kamu rekomendasikan pada jawaban ini. "
        "Kosongkan array-nya (produk_ids: []) jika kamu belum merekomendasikan produk spesifik, "
        "misalnya saat kamu masih bertanya balik ke pembeli."
    )


def _extract_produk_ids(reply_text):
    """Cari blok ```json {produk_ids: [...]}``` di akhir jawaban, lalu pisahkan dari teks tampilan."""
    match = re.search(r"```json\s*(\{.*?\})\s*```", reply_text, re.DOTALL)
    produk_ids = []
    clean_text = reply_text
    if match:
        try:
            parsed = json.loads(match.group(1))
            produk_ids = parsed.get('produk_ids', []) or []
        except (json.JSONDecodeError, AttributeError):
            produk_ids = []
        clean_text = (reply_text[:match.start()] + reply_text[match.end():]).strip()
    return clean_text, produk_ids


@require_POST
@csrf_protect
def chatbot_api(request):
    if not settings.GEMINI_API_KEY:
        return JsonResponse({
            'error': (
                'GEMINI_API_KEY belum diset. Tambahkan environment variable '
                'GEMINI_API_KEY di komputer/server kamu, lalu restart server Django.'
            )
        }, status=500)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Format request tidak valid.'}, status=400)

    user_message = (body.get('message') or '').strip()
    history = body.get('history') or []  # list of {role, content}

    if not user_message:
        return JsonResponse({'error': 'Pesan tidak boleh kosong.'}, status=400)
    if len(user_message) > 1000:
        return JsonResponse({'error': 'Pesan terlalu panjang.'}, status=400)

    # Batasi riwayat percakapan yang dikirim ulang, biar hemat token.
    # Gemini memakai role 'user' dan 'model' (bukan 'assistant' seperti Claude/OpenAI).
    clean_history = []
    for h in history[-10:]:
        role = h.get('role')
        content = h.get('content')
        if role in ('user', 'assistant') and isinstance(content, str) and content.strip():
            gemini_role = 'model' if role == 'assistant' else 'user'
            clean_history.append({'role': gemini_role, 'parts': [{'text': content[:1000]}]})

    contents = clean_history + [{'role': 'user', 'parts': [{'text': user_message}]}]
    katalog = _build_katalog_context()
    system_prompt = _build_system_prompt(katalog)

    payload = {
        'system_instruction': {'parts': [{'text': system_prompt}]},
        'contents': contents,
        'generationConfig': {'maxOutputTokens': 1024},
    }

    req = urllib.request.Request(
        f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}",
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={
            'content-type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        return JsonResponse({'error': f'Gagal menghubungi AI (HTTP {e.code}): {error_body}'}, status=502)
    except urllib.error.URLError as e:
        return JsonResponse({'error': f'Gagal menghubungi AI: {e.reason}'}, status=502)

    reply_text = ''
    candidates = data.get('candidates', [])
    if candidates:
        parts = candidates[0].get('content', {}).get('parts', [])
        for part in parts:
            reply_text += part.get('text', '')

    clean_text, produk_ids = _extract_produk_ids(reply_text)

    produk_data = []
    if produk_ids:
        produk_qs = Produk.objects.filter(id__in=produk_ids, status='aktif').select_related('merek')
        for p in produk_qs:
            harga_final = p.harga_diskon if p.harga_diskon else p.harga
            produk_data.append({
                'id': p.id,
                'nama': p.nama,
                'merek': p.merek.nama,
                'harga': format_rupiah(harga_final),
                'gambar_url': p.gambar_url or '',
                'url': reverse('produk_detail', args=[p.id]),
            })

    return JsonResponse({'reply': clean_text, 'produk': produk_data})
