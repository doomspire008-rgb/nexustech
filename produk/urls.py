from django.urls import path
from . import views

urlpatterns = [
    path('', views.beranda, name='beranda'),
    path('produk/', views.produk_list, name='produk_list'),
    path('produk/<int:pk>/', views.produk_detail, name='produk_detail'),
    path('produk/<int:pk>/ulasan/', views.tambah_ulasan, name='tambah_ulasan'),
    path('keranjang/', views.keranjang, name='keranjang'),
    path('admin-invoice/<int:pk>/', views.admin_invoice_pdf, name='admin_invoice_pdf'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]