from django.db import models
from django.contrib.auth.models import User


CATEGORY_CHOICES = (

    ('Saree', 'Saree'),

    ('Kurthi', 'Kurthi'),

    ('Jeans Top', 'Jeans Top'),

)


class Product(models.Model):

    product_code = models.CharField(max_length=20)

    name = models.CharField(max_length=200)

    price = models.IntegerField()

    available_colors = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    stock = models.IntegerField(default=1)

    image = models.ImageField(
        upload_to='products/'
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    original_price = models.IntegerField(default=0)

    discount_percent = models.IntegerField(default=0)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    )

    def __str__(self):

        return self.name


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to='products/'
    )

    def __str__(self):

        return self.product.name


# NEW MODEL FOR COLOR VARIANTS

class ProductColor(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    color_name = models.CharField(
        max_length=100
    )

    color_image = models.ImageField(
        upload_to='product_colors/'
    )

    def __str__(self):

        return f"{self.product.name} - {self.color_name}"


SIZE_CHOICES = (

    ('S', 'S'),

    ('M', 'M'),

    ('L', 'L'),

    ('XL', 'XL'),

)


class ProductSize(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES
    )

    stock = models.IntegerField(default=0)

    def __str__(self):

        return self.product.name + " - " + self.size


class Order(models.Model):

    STATUS_CHOICES = (

        ('Pending', 'Pending'),

        ('Packed', 'Packed'),

        ('Shipped', 'Shipped'),

        ('Delivered', 'Delivered'),

    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    customer_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    address = models.TextField()

    city = models.CharField(max_length=100)

    payment_method = models.CharField(max_length=100)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField()

    total_price = models.IntegerField()

    selected_color = models.CharField(
    max_length=50,
    blank=True,
    null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):

        return self.customer_name


class Wishlist(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    def __str__(self):

        return self.product.name


class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    rating = models.IntegerField()

    comment = models.TextField()

    def __str__(self):

        return self.name
