from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Merek, Kategori, Produk, Pelanggan, Pesanan, ItemPesanan, Ulasan

admin.site.site_header = "NexusTech Admin Panel"
admin.site.site_title = "NexusTech Admin"
admin.site.index_title = "Manajemen Toko Laptop NexusTech"

admin.site.register(Merek)
admin.site.register(Kategori)
admin.site.register(Pelanggan)


@admin.register(Ulasan)
class UlasanAdmin(admin.ModelAdmin):
    list_display = ['nama_pengulas', 'produk', 'rating_stars', 'foto_preview', 'disetujui', 'created_at']
    list_filter = ['rating', 'disetujui', 'created_at']
    search_fields = ['nama_pengulas', 'email_pengulas', 'komentar', 'produk__nama']
    list_editable = ['disetujui']
    readonly_fields = ['foto_preview_detail', 'created_at']

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#f59e0b;font-size:14px;">{} ({})</span>', stars, obj.rating)
    rating_stars.short_description = 'Rating'

    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:4px;border:1px solid #ccc;"/></a>',
                obj.foto.url, obj.foto.url
            )
        return '-'
    foto_preview.short_description = 'Foto'

    def foto_preview_detail(self, obj):
        if obj.foto:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;border:1px solid #ccc;"/></a>',
                obj.foto.url, obj.foto.url
            )
        return 'Tidak ada foto'
    foto_preview_detail.short_description = 'Pratinjau Foto'


@admin.register(Produk)
class ProdukAdmin(admin.ModelAdmin):
    list_display = ['nama', 'merek', 'harga', 'status']
    search_fields = ['nama', 'sku']


class ItemPesananInline(admin.TabularInline):
    model = ItemPesanan
    extra = 1
    autocomplete_fields = ['produk']
    fields = ['produk', 'qty', 'harga_satuan', 'subtotal_display']
    readonly_fields = ['subtotal_display']

    def subtotal_display(self, obj):
        if obj.pk:
            return f"Rp {obj.subtotal:,.0f}".replace(',', '.')
        return '-'
    subtotal_display.short_description = 'Subtotal'


@admin.register(Pesanan)
class PesananAdmin(admin.ModelAdmin):
    list_display = ['no_pesanan', 'pelanggan', 'total_display', 'status', 'created_at', 'invoice_link']
    list_filter = ['status', 'created_at']
    search_fields = ['no_pesanan', 'pelanggan__nama', 'pelanggan__email']
    readonly_fields = ['no_pesanan', 'total_display', 'created_at', 'invoice_button']
    fields = ['no_pesanan', 'pelanggan', 'status', 'ongkir', 'catatan', 'total_display', 'created_at', 'invoice_button']
    inlines = [ItemPesananInline]

    def total_display(self, obj):
        if obj.pk:
            return f"Rp {obj.total:,.0f}".replace(',', '.')
        return '-'
    total_display.short_description = 'Total Pesanan'

    def invoice_link(self, obj):
        if obj.pk:
            url = reverse('admin_invoice_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">📄 Invoice</a>', url)
        return '-'
    invoice_link.short_description = 'Invoice'

    def invoice_button(self, obj):
        if not obj.pk:
            return 'Simpan pesanan terlebih dahulu untuk membuat invoice.'
        url = reverse('admin_invoice_pdf', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" target="_blank" '
            'style="background:#34d399;color:#fff;padding:8px 16px;'
            'border-radius:6px;text-decoration:none;font-weight:700;">'
            '📄 Download Invoice PDF</a>',
            url
        )
    invoice_button.short_description = 'Invoice'

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        # Setiap kali item pesanan disimpan/diubah, hitung ulang total pesanan
        form.instance.hitung_ulang_total()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.pk:
            obj.hitung_ulang_total()

