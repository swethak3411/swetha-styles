from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('product/<int:id>/', views.product_detail),
    path('cart/', views.cart),
    path('add-to-cart/<int:id>/', views.add_to_cart),
    path('register/', views.register),
    path('order/', views.order),
    path('wishlist/', views.wishlist),
    path('add-to-wishlist/<int:id>/', views.add_to_wishlist),
    path('logout/', views.logout_user),
    path('my-orders/', views.my_orders),
    path('profile/', views.profile),
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('admin-dashboard/', views.admin_dashboard),
    path(
    'update-order/<int:order_id>/<str:status>/',
    views.update_order_status,
    name='update_order_status'
),
]