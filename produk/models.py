import uuid
from django.db import models


class Merek(models.Model):
    nama = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nama


class Kategori(models.Model):
    nama = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.nama


class Produk(models.Model):
    STATUS_CHOICES = [('aktif','Aktif'), ('nonaktif','Nonaktif'), ('habis','Habis')]
    nama = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    merek = models.ForeignKey(Merek, on_delete=models.CASCADE)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    harga_diskon = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    deskripsi = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    gambar_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='URL Gambar')

    def __str__(self):
        return self.nama

    def rating_rata(self):
        ulasan = self.ulasan_set.all()
        if ulasan:
            return round(sum(u.rating for u in ulasan) / len(ulasan), 1)
        return 0

    def jumlah_ulasan(self):
        return self.ulasan_set.count()


class Pelanggan(models.Model):
    nama = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telpon = models.CharField(max_length=20, blank=True)
    alamat = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Pesanan(models.Model):
    STATUS_CHOICES = [
        ('pending','Pending'), ('dikonfirmasi','Dikonfirmasi'),
        ('diproses','Diproses'), ('dikirim','Dikirim'),
        ('selesai','Selesai'), ('dibatalkan','Dibatalkan'),
    ]
    no_pesanan = models.CharField(max_length=50, unique=True, blank=True)
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    ongkir = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    catatan = models.TextField(blank=True, verbose_name='Catatan')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.no_pesanan

    def save(self, *args, **kwargs):
        if not self.no_pesanan:
            from django.utils import timezone
            tanggal = self.created_at or timezone.now()
            self.no_pesanan = f"INV-{tanggal.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def hitung_ulang_total(self):
        """Hitung ulang total pesanan dari seluruh item + ongkir, lalu simpan."""
        subtotal = sum((item.subtotal for item in self.item_set.all()), start=0)
        self.total = subtotal + (self.ongkir or 0)
        Pesanan.objects.filter(pk=self.pk).update(total=self.total)

    @property
    def subtotal(self):
        return self.total - (self.ongkir or 0)


class ItemPesanan(models.Model):
    pesanan = models.ForeignKey(Pesanan, on_delete=models.CASCADE, related_name='item_set')
    produk = models.ForeignKey(Produk, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    harga_satuan = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True,
        help_text='Kosongkan untuk memakai harga produk saat ini otomatis.'
    )

    class Meta:
        verbose_name = 'Item Pesanan'
        verbose_name_plural = 'Item Pesanan'

    def __str__(self):
        return f"{self.produk.nama} x{self.qty}"

    def save(self, *args, **kwargs):
        if self.harga_satuan is None:
            self.harga_satuan = self.produk.harga_diskon or self.produk.harga
        super().save(*args, **kwargs)

    @property
    def merek(self):
        return self.produk.merek

    @property
    def subtotal(self):
        return (self.harga_satuan or 0) * self.qty


class Ulasan(models.Model):
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    nama_pengulas = models.CharField(max_length=100, verbose_name='Nama')
    email_pengulas = models.EmailField(verbose_name='Email')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    komentar = models.TextField(verbose_name='Komentar')
    foto = models.ImageField(upload_to='ulasan/', blank=True, null=True, verbose_name='Foto (opsional)')
    created_at = models.DateTimeField(auto_now_add=True)
    disetujui = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nama_pengulas} - {self.produk.nama} ({self.rating}★)"

    def bintang_penuh(self):
        return range(self.rating)

    def bintang_kosong(self):
        return range(5 - self.rating)