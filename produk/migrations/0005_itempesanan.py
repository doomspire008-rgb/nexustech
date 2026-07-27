# Generated manually for invoice PDF feature

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produk', '0004_ulasan'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesanan',
            name='catatan',
            field=models.TextField(blank=True, verbose_name='Catatan'),
        ),
        migrations.AlterField(
            model_name='pesanan',
            name='no_pesanan',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='pesanan',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=14),
        ),
        migrations.CreateModel(
            name='ItemPesanan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.PositiveIntegerField(default=1)),
                ('harga_satuan', models.DecimalField(blank=True, decimal_places=2, help_text='Kosongkan untuk memakai harga produk saat ini otomatis.', max_digits=12)),
                ('pesanan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_set', to='produk.pesanan')),
                ('produk', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='produk.produk')),
            ],
            options={
                'verbose_name': 'Item Pesanan',
                'verbose_name_plural': 'Item Pesanan',
            },
        ),
    ]
