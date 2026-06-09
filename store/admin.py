from django.contrib import admin

from .models import *

admin.site.register(Product)

admin.site.register(ProductImage)

admin.site.register(ProductColor)

admin.site.register(ProductSize)

admin.site.register(Order)

admin.site.register(Wishlist)

admin.site.register(Review)